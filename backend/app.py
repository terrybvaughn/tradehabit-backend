from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import io
from dataclasses import asdict

from backend.models.trade import Trade
from backend.parsing.order_loader import load_orders
from backend.analytics.trade_counter import count_trades
from backend.analytics.stop_loss_analyzer import analyze_trades_for_no_stop_mistake

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

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
    if "file" not in request.files:
        abort(400, "No file part")

    f = request.files["file"]
    if not _is_allowed(f.filename) or not _size_ok(f):
        abort(400, "Only CSV files ≤2 MB accepted")

    df = load_orders(f)
    print("Loaded columns:", list(df.columns))

    trades, _ = count_trades(df)          # list[Trade]
    trade_objs = [t for t in trades if isinstance(t, Trade)]
    if len(trade_objs) != len(trades):
        print(f"Warning: {len(trades) - len(trade_objs)} non-Trade items skipped")

    # Mutate trades in-place to flag mistakes
    analyze_trades_for_no_stop_mistake(trade_objs, df)

    # How many trades ended up with the “no stop-loss order” flag?
    trades_missing_stop = sum(
        "no stop-loss order" in t.mistakes for t in trade_objs
    )

    payload = {
        "meta": {
            "csvRows":          len(df),
            "tradesDetected":   len(trade_objs),
            "tradesMissingStop": trades_missing_stop,  # ← renamed & clearer
        },
        "trades": [
            t.to_dict() if hasattr(t, "to_dict") else asdict(t) for t in trade_objs
        ],
    }
    return jsonify(payload)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
