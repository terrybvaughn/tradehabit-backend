from flask import Flask, request, jsonify, abort
from flask_cors import CORS

from dataclasses import asdict

from backend.models.trade import Trade
from backend.parsing.order_loader import load_orders
from backend.analytics.trade_counter import count_trades
from backend.analytics.mistake_analyzer import analyze_all_mistakes

import io
import statistics

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

trade_objs = []

# ---- Helper functions (CSV gate) ----
ALLOWED_EXT = {".csv"}
MAX_MB = 2  # MB

def _is_allowed(filename: str) -> bool:
    return filename.lower().endswith(tuple(ALLOWED_EXT))

def _size_ok(file_storage) -> bool:
    file_storage.seek(0, io.SEEK_END)
    ok = file_storage.tell() <= MAX_MB * 1024 * 1024
    file_storage.seek(0)
    return ok

# ---- Error handlers ----
@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e.description)), 400

@app.errorhandler(413)
def too_large(e):
    return jsonify(error="File too large"), 413

# ---- Main route ----
@app.post("/api/analyze")
def analyze():
    global trade_objs

    if "file" not in request.files:
        abort(400, "No file part")

    f = request.files["file"]
    if not _is_allowed(f.filename) or not _size_ok(f):
        abort(400, "Only CSV files ≤2 MB accepted")

    df = load_orders(f)
    print("Loaded columns:", list(df.columns))

    trades, _ = count_trades(df)  # list[Trade]
    trade_objs.clear()
    trade_objs.extend(t for t in trades if isinstance(t, Trade))
    if len(trade_objs) != len(trades):
        print(f"Warning: {len(trades) - len(trade_objs)} non-Trade items skipped")

    # 1) Compute PnL and points_lost for each trade
    for t in trade_objs:
        direction    = 1 if t.side.lower() == "buy" else -1
        raw_points   = t.exit_price - t.entry_price

        # total dollar PnL (price difference × qty)
        t.pnl         = round(raw_points * direction * t.exit_qty, 2)

        # points lost (for loss‐consistency chart)
        t.points_lost = abs(round(raw_points * direction, 2))

    # 2) Read sigma multiplier from ?sigma= query (default 1.0)
    sigma = float(request.args.get("sigma", 1.0))

    # 3) Tag all mistake types (stop‐loss + outsized loss at μ + sigma·σ)
    analyze_all_mistakes(trade_objs, df, sigma)

    # 4) Compute mistake counts by type
    mistake_counts     = {}
    for t in trade_objs:
        for m in t.mistakes:
            mistake_counts[m] = mistake_counts.get(m, 0) + 1
    total_mistakes     = sum(mistake_counts.values())

    # 5) Count trades with >=1 mistake
    trades_with_mistakes = sum(1 for t in trade_objs if t.mistakes)

    # 6) Compute success rate
    success_rate       = round((len(trade_objs) - total_mistakes) / len(trade_objs), 2)

    # 7) Build and return payload
    payload = {
        "meta": {
            "csvRows":            len(df),
            "tradesDetected":     len(trade_objs),
            "tradesWithMistakes": trades_with_mistakes,
            "totalMistakes":      total_mistakes,
            "mistakeCounts":      mistake_counts,
            "successRate":        success_rate,
            "sigmaUsed":          sigma
        },
        "trades": [t.to_dict() for t in trade_objs],
    }
    return jsonify(payload)

@app.get("/api/summary")
def get_summary():
    global trade_objs  # in-memory list from /api/analyze

    if not trade_objs:
        abort(400, "No trades have been analyzed yet")

    total_trades = len(trade_objs)

    # 1) Count all mistake types
    mistake_counts = {}
    for t in trade_objs:
        for m in t.mistakes:
            mistake_counts[m] = mistake_counts.get(m, 0) + 1
    total_mistakes = sum(mistake_counts.values())

    # 2) Compute success rate
    success_rate = (
        round((total_trades - total_mistakes) / total_trades, 2)
        if total_trades > 0 else 0.0
    )

    # 3) Compute streaks
    current = 0
    streak_record = 0
    for t in trade_objs:
        if not t.mistakes:
            current += 1
            streak_record = max(streak_record, current)
        else:
            current = 0
    streak_current = current

    # 4) Rule-based diagnostic text
    diagnostic_text = (
        f"Over this time period, {int(success_rate * 100)}% "
        "of your trades were executed without a mistake."
    )

    # 5) Payoff-ratio block (all-time)
    wins    = [t.pnl for t in trade_objs if t.pnl > 0]
    losses  = [abs(t.pnl) for t in trade_objs if t.pnl < 0]

    win_rate = len(wins) / total_trades if total_trades > 0 else 0.0
    average_win  = round(sum(wins) / len(wins), 2)    if wins   else 0.0
    average_loss = round(sum(losses) / len(losses), 2) if losses else 0.0

    payoff_ratio          = round(average_win / average_loss, 2)             if average_loss > 0 else None
    required_payoff_ratio = round((1 - win_rate) / win_rate, 2)              if win_rate > 0     else None

    # 6) Return everything
    return jsonify({
        "total_trades":            total_trades,
        "total_mistakes":          total_mistakes,
        "success_rate":            success_rate,
        "streak_current":          streak_current,
        "streak_record":           streak_record,
        "mistake_counts":          mistake_counts,
        "diagnostic_text":         diagnostic_text,
        "win_rate":                round(win_rate, 2),
        "average_win":             average_win,
        "average_loss":            average_loss,
        "payoff_ratio":            payoff_ratio,
        "required_payoff_ratio":   required_payoff_ratio,
    })

@app.get("/api/trades")
def get_trades():
    global trade_objs

    if not trade_objs:
        abort(400, "No trades have been analyzed yet")

    return jsonify([t.to_dict() for t in trade_objs])

@app.get("/api/losses")
def get_losses():
    global trade_objs

    if not trade_objs:
        abort(400, "No trades have been analyzed yet")

    sigma  = float(request.args.get("sigma", 1.0))
    symbol = request.args.get("symbol", None)

    # 1) Filter to actual losing trades
    filtered = [
        t for t in trade_objs
        if t.pnl < 0
        and (symbol is None or t.symbol == symbol)
    ]

    # 2) Compute stats
    losses = [t.points_lost for t in filtered]
    mean_pts = statistics.mean(losses) if losses else 0.0
    std_pts  = statistics.pstdev(losses) if losses else 0.0
    threshold = mean_pts + sigma * std_pts

    # 3) Build the series, now including tradeId
    loss_list = []
    for idx, t in enumerate(filtered, start=1):
        loss_list.append({
            "lossIndex":  idx,
            "tradeId":    t.id,
            "pointsLost": t.points_lost,
            "hasMistake": t.points_lost > threshold
        })

    return jsonify({
        "losses":               loss_list,
        "meanPointsLost":       round(mean_pts, 2),
        "stdDevPointsLost":     round(std_pts, 2),
        "thresholdPointsLost":  round(threshold, 2),
        "sigmaUsed":            sigma,
        "symbolFiltered":       symbol
    })

@app.get("/api/revenge")
def get_revenge_stats():
    global trade_objs
    if not trade_objs:
        abort(400, "No trades have been analyzed yet")

    # 1) Read multiplier (default 1.0× median hold)
    k = float(request.args.get("k", 1.0))

    # 2) Clone and tag
    from copy import deepcopy
    trades = deepcopy(trade_objs)
    from backend.analytics.revenge_analyzer import analyze_trades_for_revenge
    analyze_trades_for_revenge(trades, k)

    # 3) Aggregate stats
    revenge_trades = [t for t in trades if "revenge trade" in t.mistakes]
    total_rev   = len(revenge_trades)
    win_rev     = sum(1 for t in revenge_trades if t.pnl > 0)
    loss_rev    = sum(1 for t in revenge_trades if t.pnl < 0)

    avg_win_rev  = round(
        sum(t.pnl for t in revenge_trades if t.pnl > 0) / win_rev, 2
    ) if win_rev else 0.0

    avg_loss_rev = round(
        sum(abs(t.pnl) for t in revenge_trades if t.pnl < 0) / loss_rev, 2
    ) if loss_rev else 0.0

    win_rate_rev = round(win_rev / total_rev, 2) if total_rev else None

    # — NEW: Revenge Payoff Ratio
    payoff_ratio_rev = (
        round(avg_win_rev / avg_loss_rev, 2)
        if avg_loss_rev > 0 else None
    )

    # 4) Return
    return jsonify({
        "revenge_multiplier":       k,
        "total_revenge_trades":     total_rev,
        "revenge_win_rate":         win_rate_rev,
        "average_win_revenge":      avg_win_rev,
        "average_loss_revenge":     avg_loss_rev,
        "payoff_ratio_revenge":     payoff_ratio_rev,
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
