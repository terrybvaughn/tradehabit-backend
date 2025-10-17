import os
import json
import time
import logging
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI

# Import data service directly to avoid circular imports
from mentor.data_service import MentorDataService


# Load environment from .env if present (safe no-op if not)
load_dotenv()

logger = logging.getLogger(__name__)


# --- Environment ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY")
if not ASSISTANT_ID:
    raise RuntimeError("Missing ASSISTANT_ID")


# --- OpenAI client ---
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Data service instance ---
# Note: We'll get the data service from the blueprint module to ensure
# we use the same instance that has access to global state
data_service = None  # Will be set by init_mentor_service


# --- Helper functions (ported from blueprint to avoid circular imports) ---
def canonicalize(name: str) -> str:
    """Normalize an endpoint key: lowercase and unify separators to hyphens."""
    n = (name or "").strip().lower()
    n = n.replace("_", "-").replace(" ", "-")
    return n


def _parse_iso_dt(s: str):
    """Parse ISO datetime with or without 'Z'."""
    from datetime import datetime, timezone
    if not isinstance(s, str):
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
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
    if limit > 50:  # MAX_PAGE_SIZE
        limit = 50
    
    fields = payload.get("fields")
    if fields is not None and not isinstance(fields, list):
        fields = None
    
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


def build_whitelist() -> Dict[str, str]:
    """Auto-discover all .json snapshots under data/static and create flexible keys."""
    mapping: Dict[str, str] = {}
    data_dir = data_service.fixtures_path
    
    if not os.path.isdir(data_dir):
        return mapping
    
    for fname in os.listdir(data_dir):
        if not fname.lower().endswith(".json"):
            continue
        stem = os.path.splitext(fname)[0]
        lower_stem = stem.lower()
        canon = canonicalize(lower_stem)
        
        mapping[canon] = fname
        mapping[lower_stem] = fname
        mapping[lower_stem.replace("-", "_")] = fname
        mapping[lower_stem.replace("-", " ")] = fname
        mapping[lower_stem.replace("_", " ")] = fname
    
    return mapping


def _with_retry(fn, tries: int = 3, base_delay_ms: int = 800):
    delay = base_delay_ms
    last_err = None
    for _ in range(tries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            status = getattr(e, "status", None)
            msg = str(e)
            rate_limited = (status == 429) or ("rate limit" in msg.lower()) or ("too many requests" in msg.lower())
            if not rate_limited:
                break
            time.sleep(delay / 1000.0)
            delay *= 2
    if last_err:
        raise last_err
    raise RuntimeError("Retry limit reached")



def _call_tool_runner(name: str, args: Dict[str, Any], user_text: Optional[str] = None) -> Dict[str, Any]:
    """Execute tool calls in-process using the mentor data service and helpers."""
    if data_service is None:
        raise RuntimeError("Data service not initialized. Make sure init_mentor_service() was called.")
    
    payload = dict(args or {})

    # get_summary_data
    if name == "get_summary_data":
        data, code = data_service.get_summary()
        if code != 200:
            raise RuntimeError(data.get("message", "Failed to load summary"))
        return data

    # get_endpoint_data with normalization and safe defaults
    if name == "get_endpoint_data":
        safe = dict(payload)
        if safe.get("topic") and not safe.get("name"):
            safe["name"] = safe.pop("topic")
        if "keys_only" not in safe and not safe.get("top"):
            safe["keys_only"] = True
        if safe.get("top") == "trades" and not isinstance(safe.get("fields"), list):
            safe["fields"] = ["id", "entryTime", "symbol", "pnl", "mistakes"]
        req = safe.get("max_results")
        try:
            req = int(req)
            safe["max_results"] = max(1, min(req, 50))
        except Exception:
            safe["max_results"] = 10

        raw = safe.get("name", "")
        name_canon = canonicalize(raw)

        if data_service.mode == "live":
            data, code = data_service.get_endpoint(name_canon)
            if code != 200:
                raise RuntimeError(data.get("message", f"Failed to compute {name_canon}"))
        else:
            wl = build_whitelist()
            filename = wl.get(name_canon) or wl.get(str(raw).lower())
            if not filename:
                raise RuntimeError(f"Unknown or disallowed endpoint name: {raw!r} (canonical: {name_canon!r})")
            data, code = data_service.load_json(filename)
            if code != 200:
                raise RuntimeError(data.get("message", f"Failed to load {filename}"))

        # Enrich losses with stats as blueprint does
        try:
            if name_canon == "losses" and isinstance(data, dict) and isinstance(data.get("losses"), list):
                pts = [float(r.get("pointsLost")) for r in data.get("losses", [])
                       if isinstance(r, dict) and isinstance(r.get("pointsLost"), (int, float))]
                if pts:
                    n = len(pts)
                    mu = sum(pts) / n
                    var = sum((x - mu) ** 2 for x in pts) / n
                    sigma = var ** 0.5
                    stats = {
                        "mean_loss": round(mu, 2),
                        "std_loss": round(sigma, 2),
                        "unit": "points",
                    }
                    params = data.get("params", {})
                    if not isinstance(params, dict):
                        params = {}
                    params.setdefault("outsized_loss_multiplier", 2)
                    data["stats"] = stats
                    data["params"] = params
        except Exception:
            pass

        # flat endpoint short-circuit
        if isinstance(data, dict) and not any(isinstance(v, list) for v in data.values()):
            return {
                "name": raw,
                "canonical": name_canon,
                "flat": True,
                "keys": list(data.keys()),
                "results": data,
            }

        # keys_only
        if safe.get("keys_only"):
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
            return {
                "name": raw,
                "canonical": name_canon,
                "keys": keys,
                "array_lengths": array_lengths,
            }

        # optional paging of a specific top-level array
        top_key = safe.get("top")
        if top_key:
            if isinstance(data, list) and top_key == name_canon:
                page = _paginate_list(data, safe, default_limit=10)
                return {"name": raw, "canonical": name_canon, "top": top_key, **page}

            if isinstance(data, dict):
                if top_key == "losses":
                    return _tool_filter_losses(safe)
                if top_key == "trades":
                    return _tool_filter_trades(safe)
                arr = data.get(top_key, None)
                if isinstance(arr, list):
                    page = _paginate_list(arr, safe, default_limit=10)
                    return {"name": raw, "canonical": name_canon, "top": top_key, **page}
                # fallback – invalid top
                keys = list(data.keys())
                array_lengths = {}
                available_arrays = []
                for k, v in data.items():
                    if isinstance(v, list):
                        array_lengths[k] = len(v)
                        available_arrays.append(k)
                    elif isinstance(v, dict):
                        array_lengths[k] = len(v)
                return {
                    "name": raw,
                    "canonical": name_canon,
                    "error": "invalid_top",
                    "top_requested": top_key,
                    "keys": keys,
                    "array_lengths": array_lengths,
                    "available_arrays": available_arrays,
                }

            if isinstance(data, list):
                return {
                    "name": raw,
                    "canonical": name_canon,
                    "error": "invalid_top",
                    "top_requested": top_key,
                    "keys": ["<root:list>"],
                    "array_lengths": {"<root>": len(data)},
                    "available_arrays": [name_canon],
                }

        # default: full snapshot
        return data

    # filter_trades
    if name == "filter_trades":
        return _tool_filter_trades(payload, user_text)

    # filter_losses
    if name == "filter_losses":
        return _tool_filter_losses(payload, user_text)

    return {"error": f"Unknown tool: {name}"}


def _tool_filter_trades(payload: Dict[str, Any], user_text: Optional[str] = None) -> Dict[str, Any]:
    safe = {"include_total": True, **(payload or {})}
    data, code = data_service.get_trades()
    if code != 200:
        raise RuntimeError(data.get("message", "Failed to load trades.json"))
    trades = data.get("trades", [])

    def match(trade: Dict[str, Any]) -> bool:
        if "hasMistake" in safe:
            want = bool(safe["hasMistake"])
            mistakes = trade.get("mistakes", [])
            flag = bool(trade.get("hasMistake", False)) or (isinstance(mistakes, list) and len(mistakes) > 0)
            if want and not flag: return False
            if not want and flag: return False

        if "mistakes" in safe and safe["mistakes"]:
            wanted = set(safe["mistakes"]) if isinstance(safe["mistakes"], list) else {safe["mistakes"]}
            wanted = {str(m).strip() for m in wanted if str(m).strip().lower() != "any"}
            if wanted and not any(m in trade.get("mistakes", []) for m in wanted): return False

        if "time_of_day" in safe and safe["time_of_day"]:
            dt = _parse_iso_dt(trade.get("entryTime", ""))
            if not dt: return False
            hour = dt.hour
            tod = safe["time_of_day"]
            if tod == "morning" and not (5 <= hour < 12): return False
            if tod == "afternoon" and not (12 <= hour < 17): return False
            if tod == "evening" and not (17 <= hour <= 22): return False

        if safe.get("time_range"):
            dt = _parse_iso_dt(trade.get("entryTime", ""))
            if not dt: return False
            entry_t = dt.time()
            from datetime import datetime as _dt
            start_t = _dt.strptime(safe["time_range"]["start"], "%H:%M").time()
            end_t = _dt.strptime(safe["time_range"]["end"], "%H:%M").time()
            if not (start_t <= entry_t <= end_t): return False

        if safe.get("datetime_range"):
            dt = _parse_iso_dt(trade.get("entryTime", ""))
            if not dt: return False
            start_dt = _parse_iso_dt(safe["datetime_range"]["start"])
            end_dt = _parse_iso_dt(safe["datetime_range"]["end"])
            if not (start_dt and end_dt): return False
            if not (start_dt <= dt <= end_dt): return False

        if safe.get("side"):
            if trade.get("side", "").lower() != str(safe["side"]).lower(): return False

        if safe.get("symbol"):
            if trade.get("symbol", "").lower() != str(safe["symbol"]).lower(): return False

        for field in ("riskPoints", "pointsLost", "pnl"):
            min_key = f"{field}_min"
            max_key = f"{field}_max"
            val = trade.get(field)
            if min_key in safe:
                threshold = safe[min_key]
                if val is None or val < threshold: return False
            if max_key in safe:
                threshold = safe[max_key]
                if val is None or val > threshold: return False

        if safe.get("result") in {"win", "loss"}:
            pnl = trade.get("pnl", 0) or 0
            if safe["result"] == "win" and pnl <= 0: return False
            if safe["result"] == "loss" and pnl > 0: return False
        return True

    filtered = [t for t in trades if match(t)]

    sort_by = safe.get("sort_by")
    sort_dir = safe.get("sort_dir", "desc")
    if sort_by in {"entryTime", "pointsLost", "pnl"}:
        with_key = [r for r in filtered if r.get(sort_by) is not None]
        without = [r for r in filtered if r.get(sort_by) is None]
        reverse = (sort_dir == "desc")
        if sort_by == "entryTime":
            with_key.sort(key=lambda r: _parse_iso_dt(r.get("entryTime", "")) or 0, reverse=reverse)
        else:
            with_key.sort(key=lambda r: r[sort_by], reverse=reverse)
        filtered = with_key + without

    page = _paginate_list(filtered, safe, default_limit=10)
    return page


def _tool_filter_losses(payload: Dict[str, Any], user_text: Optional[str] = None) -> Dict[str, Any]:
    safe = {"include_total": True, **(payload or {})}
    data, code = data_service.get_losses()
    if code != 200:
        raise RuntimeError(data.get("message", "Failed to load losses.json"))
    records = data.get("losses", [])
    if not isinstance(records, list):
        raise RuntimeError("losses.json must contain top-level array 'losses'")

    def match(rec: Dict[str, Any]) -> bool:
        if "hasMistake" in safe:
            want = bool(safe["hasMistake"])
            mistakes = rec.get("mistakes", [])
            flag = bool(rec.get("hasMistake", False)) or (isinstance(mistakes, list) and len(mistakes) > 0)
            if want and not flag: return False
            if not want and flag: return False

        if "time_of_day" in safe and safe["time_of_day"]:
            dt = _parse_iso_dt(rec.get("entryTime", ""))
            if not dt: return False
            hour = dt.hour
            tod = safe["time_of_day"]
            if tod == "morning" and not (5 <= hour < 12): return False
            if tod == "afternoon" and not (12 <= hour < 17): return False
            if tod == "evening" and not (17 <= hour <= 22): return False

        if safe.get("time_range"):
            dt = _parse_iso_dt(rec.get("entryTime", ""))
            if not dt: return False
            entry_t = dt.time()
            from datetime import datetime as _dt
            start_t = _dt.strptime(safe["time_range"]["start"], "%H:%M").time()
            end_t = _dt.strptime(safe["time_range"]["end"], "%H:%M").time()
            if not (start_t <= entry_t <= end_t): return False

        if safe.get("datetime_range"):
            dt = _parse_iso_dt(rec.get("entryTime", ""))
            if not dt: return False
            start_dt = _parse_iso_dt(safe["datetime_range"]["start"])
            end_dt = _parse_iso_dt(safe["datetime_range"]["end"])
            if not (start_dt and end_dt): return False
            if not (start_dt <= dt <= end_dt): return False

        if safe.get("side"):
            if rec.get("side", "").lower() != str(safe["side"]).lower(): return False

        if safe.get("symbol"):
            if rec.get("symbol", "").lower() != str(safe["symbol"]).lower(): return False

        for field in ("pointsLost",):
            min_key = f"{field}_min"
            max_key = f"{field}_max"
            val = rec.get(field)
            if min_key in safe:
                threshold = safe[min_key]
                if val is None or val < threshold: return False
            if max_key in safe:
                threshold = safe[max_key]
                if val is None or val > threshold: return False
        return True

    filtered = [r for r in records if match(r)]

    # extrema
    ext = safe.get("extrema")
    include_total, offset, limit, fields = _parse_pagination(safe, default_limit=10)
    if ext and isinstance(ext, dict):
        field = ext.get("field", "pointsLost")
        mode = ext.get("mode", "max")
        candidates = [r for r in filtered if r.get(field) is not None]
        if not candidates:
            return {"total": len(filtered) if include_total else None, "offset": 0, "returned": 0, "results": []}
        pick = max(candidates, key=lambda r: r[field]) if mode == "max" else min(candidates, key=lambda r: r[field])
        return {
            "total": len(filtered) if include_total else None,
            "offset": 0,
            "returned": 1,
            "results": [_project_fields(pick, fields) if isinstance(pick, dict) else pick],
        }

    # optional sorting
    sort_by = safe.get("sort_by")
    sort_dir = safe.get("sort_dir", "desc")
    if sort_by in {"pointsLost", "entryTime"}:
        with_key = [r for r in filtered if r.get(sort_by) is not None]
        without = [r for r in filtered if r.get(sort_by) is None]
        reverse = (sort_dir == "desc")
        if sort_by == "entryTime":
            with_key.sort(key=lambda r: _parse_iso_dt(r.get("entryTime", "")) or 0, reverse=reverse)
        else:
            with_key.sort(key=lambda r: r[sort_by], reverse=reverse)
        filtered = with_key + without

    page = _paginate_list(filtered, safe, default_limit=10)

    # Add loss statistics
    try:
        all_points = [float(r.get("pointsLost", 0)) for r in records if isinstance(r.get("pointsLost"), (int, float))]
        if all_points:
            n = len(all_points)
            mean_loss = sum(all_points) / n
            var = sum((x - mean_loss) ** 2 for x in all_points) / n
            std_loss = var ** 0.5
            outsized_loss_multiplier = 1.0
            outsized_loss_threshold = mean_loss + (outsized_loss_multiplier * std_loss)
            outsized_losses_count = sum(1 for x in all_points if x > outsized_loss_threshold)
            page["loss_statistics"] = {
                "mean_loss": round(mean_loss, 2),
                "std_loss": round(std_loss, 2),
                "outsized_loss_multiplier": outsized_loss_multiplier,
                "outsized_loss_threshold": round(outsized_loss_threshold, 2),
                "total_losses": n,
                "outsized_losses_count": outsized_losses_count,
                "unit": "points",
            }
    except Exception:
        pass

    return page


def run_assistant_turn(*, thread_id: Optional[str], user_text: str) -> Dict[str, Any]:
    # Create or reuse thread; always operate with a string thread_id
    if thread_id:
        current_thread_id = thread_id
    else:
        thread_obj = _with_retry(lambda: client.beta.threads.create())
        current_thread_id = getattr(thread_obj, "id")

    # Add user message
    _with_retry(lambda: client.beta.threads.messages.create(thread_id=current_thread_id, role="user", content=user_text))

    # Create run and keep run_id string
    run_obj = _with_retry(lambda: client.beta.threads.runs.create(thread_id=current_thread_id, assistant_id=ASSISTANT_ID))
    run_id = getattr(run_obj, "id")

    # Adaptive polling
    poll_delay_ms = 750
    max_delay_ms = 3000
    backoff = 1.5

    while True:
        run_obj = _with_retry(lambda: client.beta.threads.runs.retrieve(thread_id=current_thread_id, run_id=run_id))
        status = getattr(run_obj, "status", None)
        required_action = getattr(run_obj, "required_action", None)

        if status == "requires_action" and required_action and getattr(required_action, "submit_tool_outputs", None):
            tool_calls = required_action.submit_tool_outputs.tool_calls or []
            outputs = []
            for tc in tool_calls:
                fn = tc.function
                name = getattr(fn, "name", "")
                args_str = getattr(fn, "arguments", "") or "{}"
                try:
                    args = json.loads(args_str)
                except Exception:
                    args = {}
                result = _call_tool_runner(name, args, user_text)
                outputs.append({"tool_call_id": tc.id, "output": json.dumps(result)})
            _with_retry(lambda: client.beta.threads.runs.submit_tool_outputs(
                thread_id=current_thread_id, run_id=run_id, tool_outputs=outputs
            ))
            # After submitting, continue polling (run_id stays the same)
            poll_delay_ms = 750
            continue

        if status == "completed":
            msgs = _with_retry(lambda: client.beta.threads.messages.list(thread_id=current_thread_id, limit=1, order="desc"))
            latest = msgs.data[0] if getattr(msgs, "data", []) else None
            text = ""
            if latest and latest.content and latest.content[0].type == "text":
                text = latest.content[0].text.value or ""
            return {"threadId": current_thread_id, "text": text}

        if status in {"failed", "cancelled", "expired"}:
            err = getattr(run_obj, "last_error", None)
            code = getattr(err, "code", "no_code") if err else "no_code"
            msg = getattr(err, "message", "Unknown error") if err else "Unknown error"
            return {"threadId": current_thread_id, "text": f"⚠️ Assistant run ended with status: {status}\nError code: {code}\nDetails: {msg}"}

        time.sleep(poll_delay_ms / 1000.0)
        poll_delay_ms = min(int(poll_delay_ms * backoff), max_delay_ms)


