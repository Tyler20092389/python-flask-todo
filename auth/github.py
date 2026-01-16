import os
from flask import Blueprint, session, redirect, render_template,\
    url_for, request
from flask_dance.contrib.github import make_github_blueprint, github

github_bp = make_github_blueprint(
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET")
)
github_auth_bp = Blueprint('github_auth', __name__)


def get_github_user():
    if github.authorized:
        if "github" in session:
            data = session["github"]
        else:
            response = github.get("/user")
            session["github"] = response.json()
            data = session["github"]
        # Prefix user id for compatibility
        user = {
            "id": f"github|{data['id']}",
            "name": data["login"],
            "email": data.get("email", "")
        }
        session["user"] = user
        return user
    return None


@github_auth_bp.route('/login/github')
def login_github():
    # Flask-Dance's default callback is /login/github/authorized
    return redirect(url_for("github.login"))


@github_auth_bp.route('/logout/github')
def logout_github():
    session.clear()
    return redirect('/')
