from flask import Flask, request, jsonify, abort
from flask_cors import CORS

from dataclasses import asdict

from backend.models.trade import Trade
from backend.parsing.order_loader import load_orders
from backend.analytics.trade_counter import count_trades
from backend.analytics.mistake_analyzer import analyze_all_mistakes, get_summary_insight
from backend.analytics.stop_loss_analyzer import summarize_stop_loss_behavior
from backend.analytics.winrate_payoff_analyzer import generate_winrate_payoff_insight
from backend.analytics.insights import build_insights
from backend.analytics.outsized_loss_analyzer import get_outsized_loss_insight
from backend.analytics.risk_sizing_analyzer import get_risk_sizing_insight
from backend.analytics.stop_loss_analyzer import get_stop_loss_insight
from backend.analytics.excessive_risk_analyzer import get_excessive_risk_insight

import io
import statistics

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

trade_objs = []
order_df = None  # Add global order_df variable

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
    global trade_objs, order_df  # Add order_df to global declaration

    if "file" not in request.files:
        abort(400, "No file part")

    f = request.files["file"]
    if not _is_allowed(f.filename) or not _size_ok(f):
        abort(400, "Only CSV files ≤2 MB accepted")

    order_df = load_orders(f)  # Store the DataFrame globally
    print("Loaded columns:", list(order_df.columns))

    trades, _ = count_trades(order_df)  # list[Trade]
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

    # 2a) Read sigma_risk multiplier from ?sigma_risk= query (default 1.5)
    sigma_risk = float(request.args.get("sigma_risk", 1.5))

    # 3) Tag all mistake types (stop‐loss + outsized loss + revenge + excessive risk)
    analyze_all_mistakes(trade_objs, order_df, sigma, 1.0, sigma_risk)

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
            "csvRows":            len(order_df),
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
    """
    High-level dashboard summary.
    Includes: success rate, streaks, payoff stats, and
    a headline diagnostic chosen from a risk-weighted decision tree.
    """
    global trade_objs
    if not trade_objs:
        abort(400, "No trades have been analyzed yet")

    total_trades = len(trade_objs)

    # ---------- 1) basic mistake tallies ----------
    mistake_counts: dict[str, int] = {}
    for t in trade_objs:
        for m in t.mistakes:
            mistake_counts[m] = mistake_counts.get(m, 0) + 1
    total_mistakes = sum(mistake_counts.values())

    # ---------- 2) headline success metrics ----------
    success_rate = round((total_trades - total_mistakes) / total_trades, 2)

    # streaks
    current_streak = best_streak = 0
    for t in trade_objs:
        if not t.mistakes:
            current_streak += 1
            best_streak = max(best_streak, current_streak)
        else:
            current_streak = 0

    # ---------- 3) payoff & win-rate stats ----------
    wins   = [t.pnl for t in trade_objs if t.pnl and t.pnl > 0]
    losses = [abs(t.pnl) for t in trade_objs if t.pnl and t.pnl < 0]
    win_count = len(wins)
    loss_count = len(losses)

    win_rate        = round(len(wins) / total_trades, 2) if total_trades else 0.0
    avg_win         = round(sum(wins)   / len(wins), 2) if wins   else 0.0
    avg_loss        = round(sum(losses) / len(losses), 2) if losses else 0.0
    payoff_ratio    = round(avg_win / avg_loss, 2) if avg_loss else None
    required_wr_raw = 1 / (1 + (payoff_ratio or 0)) if payoff_ratio else None
    required_wr_adj = round(required_wr_raw * 1.01, 2) if required_wr_raw else None  # +1 % cushion

    # ---------- 4) helper counters ----------
    pct = lambda n: round(100 * n / total_trades, 1) if total_trades else 0.0
    no_stop_pct        = pct(mistake_counts.get("no stop-loss order", 0))
    excess_risk_pct    = pct(mistake_counts.get("excessive risk", 0))
    outsized_loss_pct  = pct(mistake_counts.get("outsized loss", 0))
    revenge_count      = mistake_counts.get("revenge trade", 0)

    # ---------- 5) risk-sizing variation ----------
    risk_vals = [t.risk_points for t in trade_objs if t.risk_points is not None]
    risk_var_flag = False
    if risk_vals:
        mean_risk = statistics.mean(risk_vals)
        std_risk  = statistics.pstdev(risk_vals) if len(risk_vals) > 1 else 0.0
        risk_var_flag = (std_risk / mean_risk) >= 0.35

    # ---------- 6) headline diagnostic (shared with insights) ----------
    summary_text = get_summary_insight(trade_objs, success_rate)

    # ---------- 7) response
    return jsonify({
        "total_trades":       total_trades,
        "win_count":          win_count,
        "loss_count":         loss_count,
        "total_mistakes":     total_mistakes,
        "success_rate":       success_rate,
        "streak_current":     current_streak,
        "streak_record":      best_streak,
        "mistake_counts":     mistake_counts,
        "win_rate":           win_rate,
        "average_win":        avg_win,
        "average_loss":       avg_loss,
        "payoff_ratio":       payoff_ratio,
        "required_wr_adj":    required_wr_adj,
        "diagnostic_text":    summary_text,
    })

@app.get("/api/trades")
def get_trades():
    global trade_objs

    if not trade_objs:
        abort(400, "No trades have been analyzed yet")

    trades_list = [t.to_dict() for t in trade_objs]
    if trades_list:
        # Use the correct camelCase keys
        entry_times = [t["entryTime"] for t in trades_list if t.get("entryTime")]
        exit_times = [t["exitTime"] for t in trades_list if t.get("exitTime")]
        start = min(entry_times) if entry_times else None
        end = max(exit_times) if exit_times else None
    else:
        start = end = None

    return jsonify({
        "trades": trades_list,
        "date_range": {
            "start": start,
            "end": end
        }
    })

@app.get("/api/losses")
def get_losses():
    global trade_objs

    if not trade_objs:
        abort(400, "No trades have been analyzed yet")

    sigma = float(request.args.get("sigma", 1.0))
    symbol = request.args.get("symbol", None)

    # 1) Filter to actual losing trades
    filtered = [
        t for t in trade_objs
        if t.pnl < 0 and (symbol is None or t.symbol == symbol)
    ]

    # 2) Compute stats
    losses = [t.points_lost for t in filtered]
    mean_pts = statistics.mean(losses) if losses else 0.0
    std_pts = statistics.pstdev(losses) if len(losses) > 1 else 0.0
    threshold = mean_pts + sigma * std_pts

    # 3) Identify outsized losses
    outsized = [t for t in filtered if t.points_lost > threshold]
    excess_loss = sum(t.points_lost - mean_pts for t in outsized)

    # 4) Build the series
    loss_list = []
    for idx, t in enumerate(filtered, start=1):
        loss_list.append({
            "lossIndex": idx,
            "tradeId": t.id,
            "pointsLost": t.points_lost,
            "hasMistake": t.points_lost > threshold
        })

    # 5) Plain-English diagnostic
    diagnostic = get_outsized_loss_insight(trade_objs, sigma)

    # 6) Return
    return jsonify({
    "losses": loss_list,
    "meanPointsLost": round(mean_pts, 2),
    "stdDevPointsLost": round(std_pts, 2),
    "thresholdPointsLost": round(threshold, 2),
    "sigmaUsed": sigma,
    "symbolFiltered": symbol,
    "diagnostic": diagnostic.get('diagnostic', ''),  # Extract just the diagnostic text
    "count": diagnostic.get('count', 0),            # Add count of outsized losses
    "percentage": diagnostic.get('percentage', 0),   # Add percentage
    "excessLossPoints": diagnostic.get('excessLossPoints', 0)  # Add excess loss points
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
    from backend.analytics.revenge_analyzer import analyze_trades_for_revenge, _analyze_revenge_trading
    analyze_trades_for_revenge(trades, k)

    # 3) Get analysis
    analysis = _analyze_revenge_trading(trades)

    # 4) Return
    return jsonify({
        "revenge_multiplier":         k,
        "total_revenge_trades":       analysis["count"],
        "revenge_win_rate":           analysis["win_rate_rev"],
        "average_win_revenge":        analysis["avg_win_rev"],
        "average_loss_revenge":       analysis["avg_loss_rev"],
        "payoff_ratio_revenge":       analysis["payoff_ratio_rev"],
        "net_pnl_revenge":            analysis["net_pnl_rev"],
        "net_pnl_per_trade_revenge":  analysis["net_pnl_per_trade"],
        "overall_win_rate":           analysis["global_win_rate"],
        "overall_payoff_ratio":       analysis["global_payoff_ratio"],
        "diagnostic":                 analysis["diagnostic"]
    })

@app.get("/api/risk-sizing")
def get_risk_sizing():
    global trade_objs
    if not trade_objs:
        abort(400, "No trades have been analyzed yet")

    # Get insight from analyzer
    insight = get_risk_sizing_insight(trade_objs)
    
    # Return with all available stats
    return jsonify({
        "count": insight["stats"]["tradesWithRiskData"],
        "minRiskPoints": insight["stats"]["minRisk"],
        "maxRiskPoints": insight["stats"]["maxRisk"],
        "meanRiskPoints": insight["stats"]["meanRisk"],
        "stdDevRiskPoints": insight["stats"]["standardDeviation"],
        "variationRatio": insight["stats"]["variationRatio"],
        "diagnostic": insight["diagnostic"]
    })

@app.get("/api/excessive-risk")
def get_excessive_risk_summary():
    global trade_objs
    if not trade_objs:
        abort(400, "No trades have been analyzed yet")

    # Get sigma multiplier from query (?sigma=...)
    sigma = float(request.args.get("sigma", 1.5))

    # Get insight from analyzer
    insight = get_excessive_risk_insight(trade_objs, sigma)
    
    # Return with all available stats
    return jsonify({
        "totalTradesWithStops": insight["stats"]["totalTradesWithStops"],
        "meanRiskPoints": insight["stats"]["meanRiskPoints"],
        "stdDevRiskPoints": insight["stats"]["stdDevRiskPoints"],
        "excessiveRiskThreshold": insight["stats"]["excessiveRiskThreshold"],
        "excessiveRiskCount": insight["stats"]["excessiveRiskCount"],
        "excessiveRiskPercent": insight["stats"]["excessiveRiskPercent"],
        "averageRiskAmongExcessive": insight["stats"]["averageRiskAmongExcessive"],
        "sigmaUsed": sigma,
        "diagnostic": insight["diagnostic"]
    })

@app.get("/api/stop-loss")
def get_stop_loss_summary():
    global trade_objs
    if not trade_objs:
        abort(400, "No trades have been analyzed yet")

    # Get insight from analyzer
    insight = get_stop_loss_insight(trade_objs)
    
    # Return with all available stats
    return jsonify({
        "totalTrades": insight["stats"]["totalTrades"],
        "tradesWithStops": insight["stats"]["totalTrades"] - insight["stats"]["tradesWithoutStop"],
        "tradesWithoutStops": insight["stats"]["tradesWithoutStop"],
        "averageLossWithStop": insight["stats"]["averageLossWithStop"],
        "averageLossWithoutStop": insight["stats"]["averageLossWithoutStop"],
        "maxLossWithoutStop": insight["stats"]["maxLossWithoutStop"],
        "diagnostic": insight["diagnostic"]
    })

@app.get("/api/winrate-payoff")
def get_winrate_payoff_summary():
    global trade_objs
    if not trade_objs:
        abort(400, "No trades have been analyzed yet")

    wins   = [t.pnl for t in trade_objs if t.pnl > 0]
    losses = [abs(t.pnl) for t in trade_objs if t.pnl < 0]

    if not wins or not losses:
        return jsonify({
            "message": "Not enough win/loss data to compute win rate and payoff ratio."
        })

    win_rate     = len(wins) / len(trade_objs)
    avg_win      = sum(wins) / len(wins)
    avg_loss     = sum(losses) / len(losses)
    payoff_ratio = avg_win / avg_loss

    diagnostic = generate_winrate_payoff_insight(win_rate, avg_win, avg_loss)

    return jsonify({
        "winRate": round(win_rate, 4),
        "averageWin": round(avg_win, 2),
        "averageLoss": round(avg_loss, 2),
        "payoffRatio": round(payoff_ratio, 2),
        "diagnostic": diagnostic
    })

@app.get("/api/insights")
def get_insights():
    """
    Full insights report (summary + prioritized insight sections).
    """
    global trade_objs, order_df

    # Check if trades were loaded
    if not trade_objs:
        abort(400, "No trades have been analyzed yet")

    # Check if order_df is defined and not empty
    if 'order_df' not in globals() or order_df is None:
        abort(400, "Order data is missing or has not been processed yet")

    insights = build_insights(trade_objs, order_df)
    return jsonify(insights)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

