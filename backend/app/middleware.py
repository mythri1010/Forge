"""
Attaches before/after request hooks that log:
  - Incoming: method, path, user_id (if authenticated)
  - Outgoing: status code, duration_ms

Registered in the app factory via register_request_logging(app).
"""
import time
import logging
from flask import request, g
from flask_jwt_extended import decode_token
from flask_jwt_extended.exceptions import JWTDecodeError

logger = logging.getLogger("tracker.request")


def register_request_logging(app) -> None:

    @app.before_request
    def _before():
        g.start_time = time.monotonic()
        g.user_id = _extract_user_id()

    @app.after_request
    def _after(response):
        duration_ms = round((time.monotonic() - g.get("start_time", time.monotonic())) * 1000, 1)
        logger.info(
            "%s %s → %d",
            request.method,
            request.path,
            response.status_code,
            extra={
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
                "user_id": g.get("user_id"),
            },
        )
        return response


def _extract_user_id():
    """Best-effort: decode the JWT without raising if it is missing or invalid."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        data = decode_token(auth[7:])
        return data.get("sub")
    except Exception:
        return None
