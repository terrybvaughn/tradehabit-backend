from flask import jsonify
from werkzeug.exceptions import HTTPException


def init_error_handlers(app):
    """Register JSON error handlers for all HTTP and uncaught exceptions."""

    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException):  # type: ignore[arg-type]
        """Convert any Werkzeug-raised HTTPException to JSON."""
        response = jsonify(error=exc.description)
        response.status_code = exc.code
        return response

    @app.errorhandler(Exception)
    def handle_generic_exception(exc: Exception):  # noqa: BLE001
        """Return uncaught exceptions as JSON 500 responses."""
        response = jsonify(error=str(exc))
        response.status_code = 500
        return response 