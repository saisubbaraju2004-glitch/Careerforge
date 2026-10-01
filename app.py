import logging
import os
import secrets

from flask import Flask, g, jsonify, redirect, render_template, request, session, url_for
from config.config import Config
from services.user_store import consume_rate_limit, connect, get_user, initialize_database
from routes.auth import auth_bp
from routes.career import career_bp
from routes.resume import resume_bp
from routes.roadmap import roadmap_bp
from routes.jobs import jobs_bp
from routes.interview import interview_bp
from routes.applications import applications_bp
from routes.progress import progress_bp
from routes.intelligence import intelligence_bp
from routes.career_agent import career_agent_bp
from routes.placements import placements_bp
from routes.placement_practice import placement_practice_bp
from routes.placement_strategy import placement_strategy_bp
from routes.job_match import job_match_bp
from routes.interview_intelligence import interview_intel_bp
from routes.learning import learning_bp
from routes.placement_analytics import placement_analytics_bp
from routes.career_os import career_os_bp

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    Config.init_app(app)
    initialize_database(app.config["DATABASE_URL"])
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(career_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(intelligence_bp)
    app.register_blueprint(career_agent_bp)
    app.register_blueprint(placements_bp)
    app.register_blueprint(placement_practice_bp)
    app.register_blueprint(placement_strategy_bp)
    app.register_blueprint(job_match_bp)
    app.register_blueprint(interview_intel_bp)
    app.register_blueprint(learning_bp)
    app.register_blueprint(placement_analytics_bp)
    app.register_blueprint(career_os_bp)


    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/health")
    def health():
        try:
            with connect(app.config["DATABASE_URL"]) as connection:
                connection.execute("SELECT 1").fetchone()
        except Exception:
            app.logger.exception("Health check database connection failed")
            return jsonify({"status": "unavailable", "success": False}), 503
        return jsonify({"status": "healthy", "database": "connected", "success": True}), 200

    @app.before_request
    def authenticate_and_limit():
        endpoint = request.endpoint or ""
        public_endpoints = {"static", "auth.login", "auth.register", "auth.logout", "health"}
        if endpoint in public_endpoints:
            if endpoint.startswith("auth."):
                return apply_rate_limit(app, "auth", app.config["RATE_LIMIT_AUTH"])
            return None

        user_id = session.get("user_id")
        user = get_user(app.config["DATABASE_URL"], user_id) if isinstance(user_id, int) else None
        if user is None:
            session.clear()
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "error": "Authentication required."}), 401
            return redirect(url_for("auth.login", next=request.full_path))

        g.user = user
        g.user_id = user["id"]
        category = "ai" if any(token in request.path for token in ("chat", "analyze", "coach", "generate")) else "default"
        limit = app.config["RATE_LIMIT_AI"] if category == "ai" else app.config["RATE_LIMIT_DEFAULT"]
        return apply_rate_limit(app, category, limit)

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Requested resource not found"}), 404

    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({"success": False, "error": "Uploaded file exceeds maximum limit (10MB)"}), 413

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error("Unhandled server error (%s)", type(e).__name__)
        return jsonify({"success": False, "error": "Internal server error occurred"}), 500

    @app.context_processor
    def inject_auth_context():
        return {
            "auth_user": getattr(g, "user", None),
            "csrf_token": session.setdefault("csrf_token", secrets.token_urlsafe(32)),
        }

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        return response

    return app


def apply_rate_limit(app, category, limit):
    if not request.endpoint:
        return None
    key = f"{request.remote_addr or 'unknown'}:{request.endpoint}:{category}"
    allowed, retry_after = consume_rate_limit(
        app.config["DATABASE_URL"], key, limit
    )
    if not allowed:
        response = jsonify({"success": False, "error": "Rate limit exceeded. Try again shortly."})
        response.status_code = 429
        response.headers["Retry-After"] = str(max(1, retry_after))
        return response
    return None

app = create_app()

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ["true", "1"]
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    app.run(host=host, port=port, debug=debug_mode)
