"""
Logging setup for the application.

In development: human-readable coloured output to stderr.
In production:  JSON lines to stdout (ready for Datadog / CloudWatch / Loki).

Call configure_logging(app) from the app factory before the first request.
"""
import logging
import json
import sys
from datetime import datetime, timezone


class _JsonFormatter(logging.Formatter):
    """Emits one JSON object per log record — easy to parse in log aggregators."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        # Any extra kwargs passed via logger.info("x", extra={"req_id": "..."})
        for key in ("req_id", "user_id", "team_id", "path", "method", "status"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(app) -> None:
    """Attach appropriate handlers to the root logger and Flask's app logger."""
    is_prod = app.config.get("ENV") == "production" or not app.debug

    handler = logging.StreamHandler(sys.stdout)

    if is_prod:
        handler.setFormatter(_JsonFormatter())
        level = logging.INFO
    else:
        # Simple readable format for local dev
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        level = logging.DEBUG

    # Configure root — this covers SQLAlchemy, alembic, etc.
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    # Flask's own logger inherits from root, but make it explicit
    app.logger.setLevel(level)

    # Quieten noisy libraries in production
    if is_prod:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("werkzeug").setLevel(logging.WARNING)

    app.logger.info("Logging configured", extra={"env": "production" if is_prod else "development"})
