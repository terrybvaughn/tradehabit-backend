from flask import jsonify
from werkzeug.exceptions import HTTPException
from typing import List

# Reusable helper to build consistent JSON error envelopes
def error_response(status_code: int, message: str, details: List[str] | None = None):
    payload = {
        "status": "ERROR",
        "message": message,
        "details": details or [],
    }
    resp = jsonify(payload)
    resp.status_code = status_code
    return resp

def init_error_handlers(app):
    """Register JSON error handlers for all HTTP and uncaught exceptions."""

    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException):  # type: ignore[arg-type]
        """Convert any Werkzeug-raised HTTPException to JSON."""
        return error_response(exc.code or 500, exc.description)

    @app.errorhandler(Exception)
    def handle_generic_exception(exc: Exception):  # noqa: BLE001
        """Return uncaught exceptions as JSON 500 responses."""
        return error_response(500, str(exc)) 