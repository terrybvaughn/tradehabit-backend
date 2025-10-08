"""
Mentor Blueprint - Endpoints for OpenAI Assistant integration.

Supports two modes (controlled by MENTOR_MODE environment variable):
- fixtures: Reads from data/static/*.json (default)
- live: Computes from app.trade_objs and app.order_df
"""
from flask import Blueprint, request, jsonify
from mentor.data_service import MentorDataService
from datetime import datetime, timezone
from typing import Any, Dict
import os
import statistics

# Create blueprint with /api/mentor prefix
mentor_bp = Blueprint("mentor", __name__, url_prefix="/api/mentor")

# Read mode from environment variable (default: fixtures)
MENTOR_MODE = os.environ.get("MENTOR_MODE", "fixtures")

# Data service will be initialized after app registration (see init_mentor_service)
data_service = None


def init_mentor_service(trade_objs_getter, order_df_getter):
    """
    Initialize the data service with references to app's global state.
    Must be called from app.py after the blueprint is registered.
    
    Args:
        trade_objs_getter: Callable that returns the trade_objs list
        order_df_getter: Callable that returns the order_df DataFrame
    """
    global data_service
    data_service = MentorDataService(
        mode=MENTOR_MODE,
        trade_objs_ref=trade_objs_getter,
        order_df_ref=order_df_getter
    )

# Constants
MAX_PAGE_SIZE = 50

# -----------------------------
# Helper Functions
# -----------------------------

def err(status_code: int, message: str, details: list | None = None):
    """Return standardized error response."""
    return jsonify({
        "status": "ERROR",
        "message": message,
        "details": details or []
    }), status_code


def canonicalize(name: str) -> str:
    """Normalize an endpoint key: lowercase and unify separators to hyphens."""
    n = (name or "").strip().lower()
    n = n.replace("_", "-").replace(" ", "-")
    return n


def build_whitelist() -> Dict[str, str]:
    """
    Auto-discover all .json snapshots under data/static and create flexible keys.
    
    For each file stem (e.g., "excessive-risk"), we register multiple aliases:
      - canonical hyphen form: "excessive-risk"
      - underscore form:       "excessive_risk"
      - space forms:           "excessive risk", "stop loss"
      - raw lower stem:        original stem lowercased
    """
    mapping: Dict[str, str] = {}
    data_dir = data_service.fixtures_path
    
    if not os.path.isdir(data_dir):
        return mapping
    
    for fname in os.listdir(data_dir):
        if not fname.lower().endswith(".json"):
            continue
        stem = os.path.splitext(fname)[0]     # original stem
        lower_stem = stem.lower()
        canon = canonicalize(lower_stem)      # hyphen form
        
        mapping[canon] = fname
        mapping[lower_stem] = fname
        mapping[lower_stem.replace("-", "_")] = fname
        mapping[lower_stem.replace("-", " ")] = fname
        mapping[lower_stem.replace("_", " ")] = fname
    
    return mapping


def _parse_iso_dt(s: str) -> datetime | None:
    """Parse ISO datetime with or without 'Z'."""
    if not isinstance(s, str):
        return None
    try:
        if s.endswith("Z"):
            # Python's fromisoformat needs offset like +00:00
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        # Normalize to UTC-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt
    except Exception:
        return None


def _parse_pagination(payload: Dict[str, Any], default_limit: int = 10):
    """Parse pagination parameters from request payload."""
    include_total = bool(payload.get("include_total", True))
    
    try:
        offset = int(payload.get("offset", 0) or 0)
    except Exception:
        offset = 0
    if offset < 0:
        offset = 0
    
    try:
        limit = int(payload.get("max_results", default_limit))
    except Exception:
        limit = default_limit
    if limit < 0:
        limit = 0
    if limit > MAX_PAGE_SIZE:
        limit = MAX_PAGE_SIZE
    
    fields = payload.get("fields")
    if fields is not None and not isinstance(fields, list):
        fields = None  # ignore bad shape
    
    return include_total, offset, limit, fields


def _project_fields(item: Dict[str, Any], fields: list | None):
    """Project only specified fields from an item."""
    if not fields:
        return item
    return {k: item.get(k) for k in fields if k in item}


def _paginate_list(items: list, payload: Dict[str, Any], default_limit: int = 10):
    """Paginate a list of items with field projection."""
    include_total, offset, limit, fields = _parse_pagination(payload, default_limit)
    total = len(items)
    page_full = items[offset: offset + limit] if limit > 0 else []
    page = [_project_fields(x, fields) if isinstance(x, dict) else x for x in page_full]
    next_offset = offset + len(page)
    has_more = total > next_offset
    return {
        "total": total if include_total else None,
        "offset": offset,
        "returned": len(page),
        "results": page,
        "has_more": has_more,
        "next_offset": next_offset if has_more else None
    }


# -----------------------------
# Routes
# -----------------------------

@mentor_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "OK"}), 200


@mentor_bp.route("/list_endpoints", methods=["GET"])
def list_endpoints():
    """List available analytics endpoints."""
    wl = build_whitelist()
    return jsonify({
        "status": "OK",
        "available": sorted(set(wl.keys())),
        "directory": data_service.fixtures_path
    }), 200


@mentor_bp.route("/refresh_cache", methods=["POST"])
def refresh_cache():
    """Clear the in-memory cache."""
    data_service.cache.clear()
    return jsonify({"status": "OK", "message": "Cache cleared"}), 200


@mentor_bp.route("/get_summary_data", methods=["POST", "OPTIONS"])
def get_summary_data():
    """Get portfolio summary data."""
    if request.method == "OPTIONS":
        return ("", 204)
    
    data, code = data_service.get_summary()
    if code != 200:
        return err(code, data.get("message", "Failed to load summary.json"))
    return jsonify(data), 200


@mentor_bp.route("/get_endpoint_data", methods=["POST", "OPTIONS"])
def get_endpoint_data():
    """Get data for a specific analytics endpoint with flexible querying."""
    if request.method == "OPTIONS":
        return ("", 204)
    
    payload = request.get_json(silent=True) or {}
    raw = payload.get("name", "")
    name = canonicalize(raw)
    
    # Alias mapping for documentation topics
    # Map outsized-loss related requests to the canonical 'losses' snapshot
    if name == "outsized-loss":
        name = "losses"
    
    # In live mode, use the data service's get_endpoint method
    # In fixture mode, validate against whitelist first
    if data_service.mode == "live":
        # For flat endpoints like revenge, excessive-risk, etc.
        data, code = data_service.get_endpoint(name)
        if code != 200:
            return err(code, data.get("message", f"Failed to compute {name}"))
    else:
        # Fixture mode: validate against whitelist
        wl = build_whitelist()  # dynamic discovery
        
        filename = wl.get(name) or wl.get(raw.lower())
        if not filename:
            return err(
                400,
                f"Unknown or disallowed endpoint name: {raw!r} (canonical: {name!r})",
                details=[{"allowed": sorted(set(wl.keys()))}]
            )
        
        data, code = data_service.load_json(filename)
        if code != 200:
            return err(code, data.get("message", f"Failed to load {filename}"))
    
    # Enrich losses snapshot with computed stats (μ and σ) when available
    try:
        if name == "losses" and isinstance(data, dict) and isinstance(data.get("losses"), list):
            pts = [float(r.get("pointsLost")) for r in data.get("losses", []) 
                   if isinstance(r, dict) and isinstance(r.get("pointsLost"), (int, float))]
            if pts:
                n = len(pts)
                mu = sum(pts) / n
                var = sum((x - mu) ** 2 for x in pts) / n  # population σ
                sigma = var ** 0.5
                stats = {
                    "mean_loss": round(mu, 2),
                    "std_loss": round(sigma, 2),
                    "unit": "points"
                }
                params = data.get("params", {})
                if not isinstance(params, dict):
                    params = {}
                params.setdefault("outsized_loss_multiplier", 2)
                data["stats"] = stats
                data["params"] = params
    except Exception:
        # Do not fail the endpoint if stats computation has an issue
        pass
    
    # ---- flat endpoint short-circuit: dict with no list values ----
    if isinstance(data, dict) and not any(isinstance(v, list) for v in data.values()):
        return jsonify({
            "name": raw,
            "canonical": name,
            "flat": True,
            "keys": list(data.keys()),
            "results": data
        }), 200
    
    # ---- keys-only metadata (tiny, safe) ----
    if payload.get("keys_only"):
        keys = []
        array_lengths = {}
        if isinstance(data, dict):
            keys = list(data.keys())
            for k, v in data.items():
                if isinstance(v, list):
                    array_lengths[k] = len(v)
                elif isinstance(v, dict):
                    array_lengths[k] = len(v)
        else:
            keys = [f"<root:{type(data).__name__}>"]
        
        return jsonify({
            "name": raw,
            "canonical": name,
            "keys": keys,
            "array_lengths": array_lengths
        }), 200
    
    # ---- optional paging of a specific top-level array (e.g., "losses", "trades") ----
    top_key = payload.get("top")
    if top_key:
        # Handle root-level arrays (e.g., insights.json)
        if isinstance(data, list) and top_key == name:
            page = _paginate_list(data, payload, default_limit=10)
            return jsonify({
                "name": raw,
                "canonical": name,
                "top": top_key,
                **page
            }), 200
        
        # Handle dict with nested arrays
        if isinstance(data, dict):
            # Redirect to dedicated filter endpoints which already handle
            # pagination, filtering, sorting, and field projection.
            if top_key == "losses":
                return filter_losses()
            if top_key == "trades":
                return filter_trades()
            
            arr = data.get(top_key, None)
            if isinstance(arr, list):
                page = _paginate_list(arr, payload, default_limit=10)
                return jsonify({
                    "name": raw,
                    "canonical": name,
                    "top": top_key,
                    **page
                }), 200
            
            # Graceful fallback: wrong/missing top array → return keys-only + arrays available
            keys = list(data.keys())
            array_lengths = {}
            available_arrays = []
            for k, v in data.items():
                if isinstance(v, list):
                    array_lengths[k] = len(v)
                    available_arrays.append(k)
                elif isinstance(v, dict):
                    array_lengths[k] = len(v)
            
            return jsonify({
                "name": raw,
                "canonical": name,
                "error": "invalid_top",
                "top_requested": top_key,
                "keys": keys,
                "array_lengths": array_lengths,
                "available_arrays": available_arrays
            }), 200
        
        # Root-level array but top_key doesn't match name - invalid
        if isinstance(data, list):
            return jsonify({
                "name": raw,
                "canonical": name,
                "error": "invalid_top",
                "top_requested": top_key,
                "keys": [f"<root:list>"],
                "array_lengths": {"<root>": len(data)},
                "available_arrays": [name]
            }), 200
    
    # ---- default: return the full snapshot (be careful with big files) ----
    return jsonify(data), 200


@mentor_bp.route("/filter_trades", methods=["POST", "OPTIONS"])
def filter_trades():
    """Filter and paginate trades with flexible criteria."""
    if request.method == "OPTIONS":
        return ("", 204)
    
    payload = request.get_json(silent=True) or {}
    data, code = data_service.get_trades()
    if code != 200:
        return err(code, data.get("message", "Failed to load trades.json"))
    
    trades = data.get("trades", [])
    
    def match(trade: Dict[str, Any]) -> bool:
        # hasMistake filter (accept either explicit boolean or inferred from a 'mistakes' array)
        if "hasMistake" in payload:
            want = bool(payload["hasMistake"])
            mistakes = trade.get("mistakes", [])
            flag = bool(trade.get("hasMistake", False)) or (isinstance(mistakes, list) and len(mistakes) > 0)
            if want and not flag:
                return False
            if not want and flag:
                return False
        
        # Mistakes (any-of)
        if "mistakes" in payload and payload["mistakes"]:
            wanted = set(payload["mistakes"]) if isinstance(payload["mistakes"], list) else {payload["mistakes"]}
            # ignore placeholders like "any"
            wanted = {str(m).strip() for m in wanted if str(m).strip().lower() != "any"}
            if wanted and not any(m in trade.get("mistakes", []) for m in wanted):
                return False
        
        # Time of day
        if "time_of_day" in payload and payload["time_of_day"]:
            dt = _parse_iso_dt(trade.get("entryTime", ""))
            if not dt:
                return False
            hour = dt.hour
            tod = payload["time_of_day"]
            if tod == "morning" and not (5 <= hour < 12): return False
            if tod == "afternoon" and not (12 <= hour < 17): return False
            if tod == "evening" and not (17 <= hour <= 22): return False
        
        # Time range (HH:MM)
        if payload.get("time_range"):
            dt = _parse_iso_dt(trade.get("entryTime", ""))
            if not dt:
                return False
            entry_t = dt.time()
            start_t = datetime.strptime(payload["time_range"]["start"], "%H:%M").time()
            end_t = datetime.strptime(payload["time_range"]["end"], "%H:%M").time()
            if not (start_t <= entry_t <= end_t):
                return False
        
        # Datetime range (ISO), normalized to UTC-aware for safe comparisons
        if payload.get("datetime_range"):
            dt = _parse_iso_dt(trade.get("entryTime", ""))
            if not dt:
                return False
            start_dt = _parse_iso_dt(payload["datetime_range"]["start"])
            end_dt = _parse_iso_dt(payload["datetime_range"]["end"])
            if not (start_dt and end_dt):
                return False
            if not (start_dt <= dt <= end_dt):
                return False
        
        # Side
        if payload.get("side"):
            if trade.get("side", "").lower() != str(payload["side"]).lower():
                return False
        
        # Symbol
        if payload.get("symbol"):
            if trade.get("symbol", "").lower() != str(payload["symbol"]).lower():
                return False
        
        # Numeric ranges
        for field in ("riskPoints", "pointsLost", "pnl"):
            min_key = f"{field}_min"
            max_key = f"{field}_max"
            val = trade.get(field)
            
            if min_key in payload:
                threshold = payload[min_key]
                if val is None:
                    return False
                if val < threshold:
                    return False
            
            if max_key in payload:
                threshold = payload[max_key]
                if val is None:
                    return False
                if val > threshold:
                    return False
        
        # Result (win/loss)
        if payload.get("result") in {"win", "loss"}:
            pnl = trade.get("pnl", 0) or 0
            if payload["result"] == "win" and pnl <= 0:
                return False
            if payload["result"] == "loss" and pnl > 0:
                return False
        
        return True
    
    filtered = [t for t in trades if match(t)]
    
    # --- optional sorting before pagination ---
    sort_by = payload.get("sort_by")
    sort_dir = payload.get("sort_dir", "desc")
    if sort_by in {"entryTime", "pointsLost", "pnl"}:
        with_key = [r for r in filtered if r.get(sort_by) is not None]
        without = [r for r in filtered if r.get(sort_by) is None]
        reverse = (sort_dir == "desc")
        
        if sort_by == "entryTime":
            # sort by datetime
            def _dt_key(r):
                dt = _parse_iso_dt(r.get("entryTime", ""))
                return dt or datetime.min.replace(tzinfo=timezone.utc)
            with_key.sort(key=_dt_key, reverse=reverse)
        else:
            with_key.sort(key=lambda r: r[sort_by], reverse=reverse)
        
        filtered = with_key + without
    
    page = _paginate_list(filtered, payload, default_limit=10)
    return jsonify(page), 200


@mentor_bp.route("/filter_losses", methods=["POST", "OPTIONS"])
def filter_losses():
    """
    Filter/paginate 'losses' snapshot and optionally return extremes
    (e.g., worst loss) deterministically.
    Expects losses.json with top-level "losses": [ ...records... ]
    """
    if request.method == "OPTIONS":
        return ("", 204)
    
    payload = request.get_json(silent=True) or {}
    data, code = data_service.get_losses()
    if code != 200:
        return err(code, data.get("message", "Failed to load losses.json"))
    
    records = data.get("losses", [])
    if not isinstance(records, list):
        return err(400, "losses.json must contain top-level array 'losses'")
    
    def match(rec: Dict[str, Any]) -> bool:
        # hasMistake filter (accepts either explicit boolean or inferred from a 'mistakes' array)
        if "hasMistake" in payload:
            want = bool(payload["hasMistake"])
            mistakes = rec.get("mistakes", [])
            flag = bool(rec.get("hasMistake", False)) or (isinstance(mistakes, list) and len(mistakes) > 0)
            if want and not flag:
                return False
            if not want and flag:
                return False
        
        # Time of day
        if "time_of_day" in payload and payload["time_of_day"]:
            dt = _parse_iso_dt(rec.get("entryTime", ""))
            if not dt:
                return False
            hour = dt.hour
            tod = payload["time_of_day"]
            if tod == "morning" and not (5 <= hour < 12): return False
            if tod == "afternoon" and not (12 <= hour < 17): return False
            if tod == "evening" and not (17 <= hour <= 22): return False
        
        # Time range (HH:MM)
        if payload.get("time_range"):
            dt = _parse_iso_dt(rec.get("entryTime", ""))
            if not dt:
                return False
            entry_t = dt.time()
            start_t = datetime.strptime(payload["time_range"]["start"], "%H:%M").time()
            end_t = datetime.strptime(payload["time_range"]["end"], "%H:%M").time()
            if not (start_t <= entry_t <= end_t):
                return False
        
        # Datetime range (ISO), normalized to UTC-aware for safe comparisons
        if payload.get("datetime_range"):
            dt = _parse_iso_dt(rec.get("entryTime", ""))
            if not dt:
                return False
            start_dt = _parse_iso_dt(payload["datetime_range"]["start"])
            end_dt = _parse_iso_dt(payload["datetime_range"]["end"])
            if not (start_dt and end_dt):
                return False
            if not (start_dt <= dt <= end_dt):
                return False
        
        # Side
        if payload.get("side"):
            if rec.get("side", "").lower() != str(payload["side"]).lower():
                return False
        
        # Symbol
        if payload.get("symbol"):
            if rec.get("symbol", "").lower() != str(payload["symbol"]).lower():
                return False
        
        # Points lost range
        for field in ("pointsLost",):
            min_key = f"{field}_min"
            max_key = f"{field}_max"
            val = rec.get(field)
            
            if min_key in payload:
                threshold = payload[min_key]
                if val is None or val < threshold:
                    return False
            
            if max_key in payload:
                threshold = payload[max_key]
                if val is None or val > threshold:
                    return False
        
        return True
    
    filtered = [r for r in records if match(r)]
    
    # --- extrema (e.g., worst loss) ---
    ext = payload.get("extrema")
    include_total, offset, limit, fields = _parse_pagination(payload, default_limit=10)
    
    if ext and isinstance(ext, dict):
        field = ext.get("field", "pointsLost")
        mode = ext.get("mode", "max")
        candidates = [r for r in filtered if r.get(field) is not None]
        if not candidates:
            return jsonify({
                "total": len(filtered) if include_total else None,
                "offset": 0, "returned": 0, "results": []
            }), 200
        pick = max(candidates, key=lambda r: r[field]) if mode == "max" else min(candidates, key=lambda r: r[field])
        return jsonify({
            "total": len(filtered) if include_total else None,
            "offset": 0,
            "returned": 1,
            "results": [_project_fields(pick, fields) if isinstance(pick, dict) else pick]
        }), 200
    
    # --- optional sorting before pagination ---
    sort_by = payload.get("sort_by")
    sort_dir = payload.get("sort_dir", "desc")
    if sort_by in {"pointsLost", "entryTime"}:
        with_key = [r for r in filtered if r.get(sort_by) is not None]
        without = [r for r in filtered if r.get(sort_by) is None]
        reverse = (sort_dir == "desc")
        
        if sort_by == "entryTime":
            # sort by datetime
            def _dt_key(r):
                dt = _parse_iso_dt(r.get("entryTime", ""))
                return dt or datetime.min.replace(tzinfo=timezone.utc)
            with_key.sort(key=_dt_key, reverse=reverse)
        else:
            with_key.sort(key=lambda r: r[sort_by], reverse=reverse)
        
        filtered = with_key + without
    
    # paginate + project
    page = _paginate_list(filtered, payload, default_limit=10)
    
    # Add loss statistics for Loss Consistency Chart analysis
    try:
        # Calculate base statistics using ALL losing trades, not filtered subset
        all_points_lost_values = [float(r.get("pointsLost", 0)) for r in records 
                                   if isinstance(r.get("pointsLost"), (int, float))]
        if all_points_lost_values and len(all_points_lost_values) > 0:
            n = len(all_points_lost_values)
            mean_loss = sum(all_points_lost_values) / n
            var = sum((x - mean_loss) ** 2 for x in all_points_lost_values) / n  # population variance
            std_loss = var ** 0.5
            
            # Default outsized loss multiplier (from analytics_explanations.md)
            outsized_loss_multiplier = 1.0
            outsized_loss_threshold = mean_loss + (outsized_loss_multiplier * std_loss)
            
            # Count losses exceeding threshold (from ALL losses, not just filtered)
            outsized_losses_count = sum(1 for x in all_points_lost_values if x > outsized_loss_threshold)
            
            page["loss_statistics"] = {
                "mean_loss": round(mean_loss, 2),
                "std_loss": round(std_loss, 2),
                "outsized_loss_multiplier": outsized_loss_multiplier,
                "outsized_loss_threshold": round(outsized_loss_threshold, 2),
                "total_losses": n,
                "outsized_losses_count": outsized_losses_count,
                "unit": "points"
            }
    except Exception:
        # Don't fail the endpoint if stats computation has an issue
        pass
    
    return jsonify(page), 200
