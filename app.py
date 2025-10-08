from flask import Flask, request, jsonify, abort
from flask_cors import CORS, cross_origin

from dataclasses import asdict
from errors import init_error_handlers, error_response

from models.trade import Trade
from parsing.order_loader import load_orders
from analytics.trade_counter import count_trades
from analytics.mistake_analyzer import analyze_all_mistakes, get_summary_insight
from analytics.stop_loss_analyzer import summarize_stop_loss_behavior
from analytics.winrate_payoff_analyzer import generate_winrate_payoff_insight
from analytics.insights import build_insights
from analytics.outsized_loss_analyzer import get_outsized_loss_insight
from analytics.risk_sizing_analyzer import get_risk_sizing_insight
from analytics.stop_loss_analyzer import get_stop_loss_insight
from analytics.excessive_risk_analyzer import get_excessive_risk_insight
from analytics.goal_tracker import generate_goal_report, get_clean_streak_stats, evaluate_goal
from mentor.mentor_blueprint import mentor_bp, init_mentor_service

import io
import statistics
import pandas as pd
import os

app = Flask(__name__)
app.register_blueprint(mentor_bp)

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",        # Vite / React dev server, etc.
    "http://localhost:5173",
    "https://tradehabit-frontend.replit.app",
    "https://app.tradehab.it",
]

CORS(
    app,
    resources={r"/*": {"origins": ALLOWED_ORIGINS}},
    supports_credentials=False
)

init_error_handlers(app)

trade_objs = []
order_df = None  # Add global order_df variable

# Initialize mentor data service with getters that access our globals
# This must happen AFTER trade_objs and order_df are defined
# The lambdas will look up the current module's globals at runtime
def get_trade_objs():
    return globals()['trade_objs']

def get_order_df():
    return globals()['order_df']

init_mentor_service(
    trade_objs_getter=get_trade_objs,
    order_df_getter=get_order_df
)

# ---------------------------------------------------------------------------
# Global, in-memory settings for user-tunable analysis thresholds. Front-end can
# adjust them once per session via POST /api/settings; every endpoint then
# reads the current value unless a query-param explicitly overrides it.
# ---------------------------------------------------------------------------

THRESHOLDS = {
    # Revenge-trade window multiplier on median hold time
    "k": 1.0,
    # Sigma used for outsized-loss detection (loss consistency)
    "sigma_loss": 1.0,
    # Sigma used for excessive-risk (stop distance)
    "sigma_risk": 1.5,
    # Coefficient-of-variation cutoff for risk-sizing consistency
    "vr": 0.35,
}

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

# ---- Main route ----
@app.route("/api/analyze", methods=["POST"])
@cross_origin()
def analyze():
    global trade_objs, order_df  # Add order_df to global declaration

    if "file" not in request.files:
        return error_response(400, "No file part")

    f = request.files["file"]

    # Validate file extension
    if not _is_allowed(f.filename):
        return error_response(400, "TradeHabit only works with the CSV file format.")

    # Validate file size (≤2 MB)
    if not _size_ok(f):
        return error_response(400, "This file exceeds the 2 MB size limit.")

    try:
        order_df = load_orders(f)  # Store the DataFrame globally
    except pd.errors.ParserError:
        return error_response(400, "This CSV format is not recognized.")
    except KeyError as exc:
        # exc.args[0] will be like "Missing columns: fill_ts"
        msg = exc.args[0]
        # Map internal names to original CSV headers for friendlier output
        col_map = {
            "fill_ts": "Fill Time",
            "ts": "Timestamp",
            "qty": "filledQty",
            "side": "B/S",
            "symbol": "Contract",
            "price": "Avg Fill Price",
        }
        for internal, original in col_map.items():
            msg = msg.replace(internal, original)
        return error_response(400, f"This file is missing required columns:\n{msg}")
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

    # Read thresholds, allowing per-request override via query-params
    sigma      = float(request.args.get("sigma", THRESHOLDS["sigma_loss"]))
    sigma_risk = float(request.args.get("sigma_risk", THRESHOLDS["sigma_risk"]))
    k          = float(request.args.get("k", THRESHOLDS["k"]))

    # 3) Tag all mistake types (stop‐loss + outsized loss + revenge + excessive risk)
    analyze_all_mistakes(trade_objs, order_df, sigma, k, sigma_risk)

    # 4) Compute mistake counts by type
    mistake_counts     = {}
    for t in trade_objs:
        for m in t.mistakes:
            mistake_counts[m] = mistake_counts.get(m, 0) + 1
    total_mistakes     = sum(mistake_counts.values())

    # 5) Count trades with >=1 mistake
    trades_with_mistakes = sum(1 for t in trade_objs if t.mistakes)

    # 6) Compute clean trade rate (trades without mistakes / total)
    clean_trade_rate   = round((len(trade_objs) - trades_with_mistakes) / len(trade_objs), 2)

    # 7) Build and return payload
    payload = {
        "meta": {
            "csvRows":            len(order_df),
            "tradesDetected":     len(trade_objs),
            "flaggedTrades":      trades_with_mistakes,
            "totalMistakes":      total_mistakes,
            "mistakeCounts":      mistake_counts,
            "cleanTradeRate":     clean_trade_rate,
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

    # Number of trades that have at least one mistake
    flagged_trades = sum(1 for t in trade_objs if t.mistakes)

    # ---------- 2) headline success metrics ----------
    clean_trade_rate = round((total_trades - flagged_trades) / total_trades, 2)

    # streaks
    current_streak, best_streak = get_clean_streak_stats(trade_objs)

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
    no_stop_pct        = mistake_counts.get("no stop-loss order", 0)
    excess_risk_pct    = mistake_counts.get("excessive risk", 0)
    outsized_loss_pct  = mistake_counts.get("outsized loss", 0)
    revenge_count      = mistake_counts.get("revenge trade", 0)
    no_stop_pct        = pct(mistake_counts.get("no stop-loss order", 0))
    excess_risk_pct    = pct(mistake_counts.get("excessive risk", 0))
    outsized_loss_pct  = pct(mistake_counts.get("outsized loss", 0))
    revenge_count_pct  = pct(mistake_counts.get("revenge trade", 0))

    # ---------- 5) risk-sizing variation ----------
    risk_vals = [t.risk_points for t in trade_objs if t.risk_points is not None]
    risk_var_flag = False
    if risk_vals:
        mean_risk = statistics.mean(risk_vals)
        std_risk  = statistics.pstdev(risk_vals) if len(risk_vals) > 1 else 0.0
        risk_var_flag = (std_risk / mean_risk) >= THRESHOLDS["vr"]

    # ---------- 6) headline diagnostic (shared with insights) ----------
    summary_text = get_summary_insight(trade_objs, clean_trade_rate)

    # ---------- 7) response
    return jsonify({
        "total_trades":       total_trades,
        "win_count":          win_count,
        "loss_count":         loss_count,
        "total_mistakes":     total_mistakes,
        "flagged_trades":     flagged_trades,
        "clean_trade_rate":   clean_trade_rate,
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

    sigma = float(request.args.get("sigma", THRESHOLDS["sigma_loss"]))
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
            "hasMistake": t.points_lost > threshold,
            # extra contextual fields
            "side": t.side,
            "exitQty": t.exit_qty,
            "symbol": t.symbol,
            "entryTime": t.entry_time.isoformat() if t.entry_time else None,
            "exitOrderId": t.exit_order_id,
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
    k = float(request.args.get("k", THRESHOLDS["k"]))

    # 2) Clone and tag
    from copy import deepcopy
    trades = deepcopy(trade_objs)
    from analytics.revenge_analyzer import analyze_trades_for_revenge, _analyze_revenge_trading
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

    # Query parameter (?vr=0.35) – coefficient of variation threshold
    vr = float(request.args.get("vr", THRESHOLDS["vr"]))

    # Get insight from analyzer with custom threshold
    insight = get_risk_sizing_insight(trade_objs, vr)
    
    # Return with all available stats
    return jsonify({
        "count": insight["stats"]["tradesWithRiskData"],
        "minRiskPoints": insight["stats"]["minRisk"],
        "maxRiskPoints": insight["stats"]["maxRisk"],
        "meanRiskPoints": insight["stats"]["meanRisk"],
        "stdDevRiskPoints": insight["stats"]["standardDeviation"],
        "variationRatio": insight["stats"]["variationRatio"],
        "variationThreshold": vr,
        "diagnostic": insight["diagnostic"]
    })

@app.get("/api/excessive-risk")
def get_excessive_risk_summary():
    global trade_objs
    if not trade_objs:
        abort(400, "No trades have been analyzed yet")

    # Get sigma multiplier from query (?sigma=...)
    sigma = float(request.args.get("sigma", THRESHOLDS["sigma_risk"]))

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

@app.get("/api/goals")
def get_goals():
    global trade_objs
    if not trade_objs:
        abort(400, "No trades have been analyzed yet")

    return jsonify(generate_goal_report(trade_objs))

@app.post("/api/goals/calculate")
@cross_origin()
def calculate_goals():
    """Calculate streak/progress stats for a user–defined list of goals.

    Expects a JSON body that is **an array** of goal objects with at least:
        id (str) – opaque identifier returned unchanged
        title (str)
        metric ("trades" | "days") – optional, defaults to "trades"
        mistake_types (list[str]) – optional, defaults to []
        target (int) – goal threshold (aka streak goal)
        start_date (YYYY-MM-DD) – optional, ISO-8601 calendar date

    Example
    -------
    [
        {
            "id": "123",
            "title": "Clean 20 Trades",
            "metric": "trades",
            "mistake_types": [],
            "target": 20,
            "start_date": "2023-01-01"
        }
    ]
    """
    global trade_objs

    # Ensure trades are available
    if not trade_objs:
        return error_response(400, "No trades have been analyzed yet.")

    payload = request.get_json(silent=True)
    if payload is None:
        return error_response(400, "Request body must be valid JSON.")

    # Accept either a dict with key "goals" or a bare list
    if isinstance(payload, dict):
        goals_in = payload.get("goals")
    else:
        goals_in = payload

    if not isinstance(goals_in, list):
        return error_response(400, "Payload must be a list of goal objects or {\"goals\": [...]}.")

    from datetime import datetime

    results = []
    for goal in goals_in:
        if not isinstance(goal, dict):
            continue  # skip invalid entries silently

        gid = goal.get("id")
        title = goal.get("title", "")
        mistake_types = goal.get("mistake_types", []) or []
        target = goal.get("target") or goal.get("goal") or 1
        metric = goal.get("metric", "trades")
        start_date_str = goal.get("start_date") or goal.get("startDate")
        try:
            start_dt = datetime.fromisoformat(start_date_str).date() if start_date_str else None
        except ValueError:
            # Invalid date format – ignore the filter
            start_dt = None

        try:
            current, best, progress = evaluate_goal(
                trades=trade_objs,
                mistake_types=mistake_types,
                goal_target=target,
                metric=metric,
                start_date=start_dt,
            )
        except ValueError as exc:
            # Unsupported metric – propagate as error field in result
            results.append({
                "id": gid,
                "title": title,
                "error": str(exc),
            })
            continue

        results.append({
            "id": gid,
            "title": title,
            "goal": target,
            "metric": metric,
            "start_date": start_date_str,
            "current_streak": current,
            "best_streak": best,
            "progress": progress,
        })

    return jsonify({"goals": results})

# ---------------------------------------------------------------------------
# Settings endpoint: read / update analysis thresholds
# ---------------------------------------------------------------------------

@app.route("/api/settings", methods=["GET", "POST"])
@cross_origin()
def settings():
    """Get or update the global analysis thresholds.

    GET  ➜ returns the current ``THRESHOLDS`` dict.
    POST ➜ body should be JSON of key-value pairs. Only keys present in
    ``THRESHOLDS`` are applied; others are ignored. All values must be
    numeric (int or float). Returns the updated settings.
    """

    global THRESHOLDS

    if request.method == "GET":
        return jsonify(THRESHOLDS)

    payload = request.get_json(silent=True)
    if payload is None:
        return error_response(400, "Request body must be valid JSON.")

    updated = {}
    for key, val in payload.items():
        if key not in THRESHOLDS:
            # Ignore unknown keys silently to keep the contract simple
            continue
        try:
            THRESHOLDS[key] = float(val)
            updated[key] = THRESHOLDS[key]
        except (TypeError, ValueError):
            return error_response(400, f"Value for '{key}' must be numeric.")

    # ------------------------------------------------------------------
    # Optional: re-run mistake tagging on existing in-memory trades so that
    # dashboard summary and insights reflect the new thresholds without
    # requiring the user to re-upload the CSV.
    # ------------------------------------------------------------------

    global trade_objs, order_df
    if trade_objs and order_df is not None:
        # Clear old mistake lists to avoid duplicates
        for t in trade_objs:
            t.mistakes.clear()

        analyze_all_mistakes(
            trade_objs,
            order_df,
            sigma_multiplier=THRESHOLDS["sigma_loss"],
            revenge_multiplier=THRESHOLDS["k"],
            sigma_risk=THRESHOLDS["sigma_risk"],
        )

    return jsonify({
        "status": "OK",
        "updated": updated,
        "thresholds": THRESHOLDS,
    })

@app.get("/api/health")
@cross_origin()
def health():
    """Lightweight liveness probe so the front-end can wake the server from an autosleep state."""
    return {"Status": "Nuh worry yuhself, mi bredda. Everyting crisp."}

if __name__ == "__main__":
    # Resolve host and port dynamically so the same code works locally and in
    # platforms like Replit/Heroku where the runtime assigns a public port.
    #
    #   • Locally   → defaults to 127.0.0.1:5000 with debug on.
    #   • Replit    → set FLASK_RUN_HOST=0.0.0.0 (and FLASK_RUN_PORT or rely on $PORT).
    #   • Heroku/Pa → $PORT is provided automatically; host 0.0.0.0 is typical.
    host  = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
    port  = int(os.environ.get("FLASK_RUN_PORT", os.environ.get("PORT", 5000)))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"

    app.run(host=host, port=port, debug=debug)
