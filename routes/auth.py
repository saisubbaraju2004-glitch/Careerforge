import hmac
import re
import secrets
from urllib.parse import urlparse

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from services.user_store import authenticate_user, create_user


auth_bp = Blueprint("auth", __name__)


def _safe_next_url(candidate):
    if not candidate:
        return url_for("index")
    parsed = urlparse(candidate)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith("/") or parsed.path.startswith("//"):
        return url_for("index")
    return candidate


def _valid_csrf():
    token = request.form.get("csrf_token", "")
    expected = session.get("csrf_token", "")
    return bool(token and expected and hmac.compare_digest(token, expected))


def _render_auth(mode, error=None, status=200):
    session.setdefault("csrf_token", secrets.token_urlsafe(32))
    return render_template(
        "auth.html",
        mode=mode,
        error=error,
        next_url=_safe_next_url(request.values.get("next")),
    ), status


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("user_id"):
            return redirect(_safe_next_url(request.args.get("next")))
        return _render_auth("login")
    if not _valid_csrf():
        return _render_auth("login", "Your form expired. Refresh the page and try again.", 400)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    user = authenticate_user(current_app.config["DATABASE_URL"], username, password)
    if user is None:
        return _render_auth("login", "Username or password is incorrect.", 401)

    destination = _safe_next_url(request.form.get("next"))
    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["csrf_token"] = secrets.token_urlsafe(32)
    session.permanent = True
    return redirect(destination)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("index"))
        return _render_auth("register")
    if not _valid_csrf():
        return _render_auth("register", "Your form expired. Refresh the page and try again.", 400)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not re.fullmatch(r"[A-Za-z0-9_.@+-]{3,64}", username):
        return _render_auth("register", "Use 3-64 letters, numbers, or . _ @ + - for the username.", 400)
    if len(password) < 12 or len(password) > 256:
        return _render_auth("register", "Password must be between 12 and 256 characters.", 400)

    user = create_user(current_app.config["DATABASE_URL"], username, password)
    if user is None:
        return _render_auth("register", "Unable to create an account with those details.", 409)

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["csrf_token"] = secrets.token_urlsafe(32)
    session.permanent = True
    return redirect(url_for("index"))


@auth_bp.route("/logout", methods=["POST"])
def logout():
    if not _valid_csrf():
        return _render_auth("login", "Your form expired. Refresh the page and try again.", 400)
    session.clear()
    return redirect(url_for("auth.login"))
