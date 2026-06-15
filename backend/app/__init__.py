import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from app.config import config_map
from app.logging_config import configure_logging
from app.middleware import register_request_logging
from app.extensions import db, jwt, migrate, limiter


def create_app() -> Flask:
    app = Flask(__name__)
    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_map[env])

    # Extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # CORS — allow the frontend origin (set FRONTEND_URL in production)
    frontend_url = os.getenv("FRONTEND_URL", "*")
    CORS(app, resources={r"/api/*": {"origins": frontend_url}}, supports_credentials=True)

    configure_logging(app)
    register_request_logging(app)

    # Auto-create tables on startup in production (Render free tier workaround)
    if env == "production":
        with app.app_context():
            try:
                db.create_all()
                app.logger.info("Database tables created successfully")
            except Exception as e:
                app.logger.error(f"Table creation failed: {e}")
                # Don't crash — let the app start so we can debug via logs

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.teams import teams_bp
    from app.blueprints.projects import projects_bp
    from app.blueprints.tasks import tasks_bp
    from app.blueprints.worklogs import worklogs_bp
    from app.blueprints.weekly import weekly_bp
    from app.blueprints.learning import learning_bp
    from app.blueprints.analytics import analytics_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.feedback import feedback_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(teams_bp, url_prefix="/api/teams")
    app.register_blueprint(projects_bp, url_prefix="/api/projects")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(worklogs_bp, url_prefix="/api/worklogs")
    app.register_blueprint(weekly_bp, url_prefix="/api/weekly")
    app.register_blueprint(learning_bp, url_prefix="/api/learning")
    app.register_blueprint(analytics_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(feedback_bp, url_prefix="/api/feedback")

    _register_error_handlers(app)

    # Serve the OpenAPI spec + Swagger UI in development only
    if app.debug:
        @app.get("/api/openapi.yaml")
        def _openapi_yaml():
            import os
            from flask import send_file
            spec_path = os.path.join(os.path.dirname(app.root_path), "openapi.yaml")
            return send_file(spec_path, mimetype="text/yaml")

        @app.get("/api/docs")
        def _swagger_ui():
            return """<!DOCTYPE html>
<html><head><title>Tracker API Docs</title>
<meta charset="utf-8"/>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head><body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>
SwaggerUIBundle({url:"/api/openapi.yaml",dom_id:"#swagger-ui",
presets:[SwaggerUIBundle.presets.apis,SwaggerUIBundle.SwaggerUIStandalonePreset],
layout:"StandaloneLayout"})
</script></body></html>""", 200, {"Content-Type": "text/html"}

    # TEMPORARY: Manual migration trigger endpoint (remove after first use)
    @app.get("/api/run-migrations")
    def _run_migrations():
        from flask import jsonify
        import subprocess
        import os
        try:
            # Run flask db upgrade via subprocess (CLI approach)
            result = subprocess.run(
                ["flask", "db", "upgrade"],
                cwd=os.path.dirname(app.root_path),
                env={**os.environ, "FLASK_APP": "run.py"},
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return jsonify({
                    "status": "success",
                    "message": "Migrations applied",
                    "output": result.stdout
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "Migration failed",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }), 500
        except Exception as e:
            import traceback
            return jsonify({"status": "error", "message": str(e), "trace": traceback.format_exc()}), 500



    return app


def _register_error_handlers(app: Flask) -> None:
    from flask import jsonify
    from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError
    from jwt.exceptions import ExpiredSignatureError, DecodeError

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "detail": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        # Avoid leaking stack traces in production
        app.logger.exception("Unhandled exception")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(NoAuthorizationError)
    @app.errorhandler(InvalidHeaderError)
    def missing_token(e):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    @app.errorhandler(ExpiredSignatureError)
    def expired_token(e):
        return jsonify({"error": "Token has expired"}), 401

    @app.errorhandler(DecodeError)
    def bad_token(e):
        return jsonify({"error": "Token is invalid"}), 401
