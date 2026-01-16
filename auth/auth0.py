import os
from flask import Blueprint, session, redirect, \
    render_template, url_for, request
from urllib.parse import urlencode
import requests

auth0_bp = Blueprint('auth0', __name__)

auth0_domain = os.getenv("AUTH0_DOMAIN")
auth0_client_id = os.getenv("AUTH0_CLIENT_ID")
auth0_client_secret = os.getenv("AUTH0_CLIENT_SECRET")

auth0_callback_url = os.getenv("AUTH0_CALLBACK_URL",
                               "http://localhost:5000/callback")

auth0_base_url = f"https://{auth0_domain}"
auth0_authorize_url = f"{auth0_base_url}/authorize"
auth0_token_url = f"{auth0_base_url}/oauth/token"
auth0_userinfo_url = f"{auth0_base_url}/userinfo"


def _external_base_url():
    """Resolve the externally reachable base URL for redirects."""
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        return render_url.rstrip('/')

    codespace_name = os.getenv("CODESPACE_NAME")
    if codespace_name:
        port = os.getenv("PORT", "5000")
        domain = os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN",
                           "app.github.dev")
        return f"https://{codespace_name}-{port}.{domain}".rstrip('/')

    return request.host_url.rstrip('/')


def get_callback_url():
    if auth0_callback_url:
        return auth0_callback_url
    return f"{_external_base_url()}/callback"


def get_auth0_user():
    return session.get("user")


@auth0_bp.route('/login/auth0')
def login_auth0():
    callback_url = get_callback_url()
    params = {
        "audience": f"{auth0_base_url}/userinfo",
        "response_type": "code",
        "client_id": auth0_client_id,
        "redirect_uri": callback_url,
        "scope": "openid profile email"
    }
    return redirect(f"{auth0_authorize_url}?" + urlencode(params))


@auth0_bp.route('/callback')
def callback_auth0():
    code = request.args.get('code')
    callback_url = get_callback_url()
    token_payload = {
        'grant_type': 'authorization_code',
        'client_id': auth0_client_id,
        'client_secret': auth0_client_secret,
        'code': code,
        'redirect_uri': callback_url
    }
    token_info = requests.post(auth0_token_url, json=token_payload).json()
    userinfo_response = requests.get(
        auth0_userinfo_url,
        headers={'Authorization': f"Bearer {token_info['access_token']}"}
    )
    userinfo = userinfo_response.json()
    session['user'] = {
        'id': userinfo['sub'],
        'name': userinfo.get('nickname', userinfo.get('name', '')),
        'email': userinfo.get('email', '')
    }
    return redirect('/')


@auth0_bp.route('/logout/auth0')
def logout_auth0():
    session.clear()
    base_url = _external_base_url()
    params = {
        'returnTo': f"{base_url}/",
        'client_id': auth0_client_id
    }
    return redirect(f"{auth0_base_url}/v2/logout?" + urlencode(params))
