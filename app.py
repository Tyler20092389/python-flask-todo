# Load environment variables from .env file (needed for gunicorn)
from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask
from auth import auth_bp, auth0_bp, github_bp, github_auth_bp
from auth import is_codespaces, is_render
from todo import todo_bp, init_app as init_todo 
from todo import db, Todo
from admin import init_admin


SITE = {
    "WebsiteName": "TodoApp",
    "ControllerName": "UTC Sheffield Olympic Legacy Park",
    "ControllerAddress": "UTC Sheffield Olympic Legacy Park, 2 Old Hall Road"
    + ", Sheffield, S9 3TU",
    "ControllerURL": "https://www.utcsheffield.org.uk/olp/",
}

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL',
                                                  'sqlite:///todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(auth0_bp)
app.register_blueprint(github_bp, url_prefix="/login")
app.register_blueprint(github_auth_bp)
app.register_blueprint(todo_bp)


@app.context_processor
def inject_dict_for_all_templates():
    auth_provider = "Auth0" if is_codespaces() or is_render() else "GitHub"
    return {"site": SITE, "auth_provider": auth_provider}


# Initialize todo module (db and tables)
init_todo(app)

# Set AUTH0_CALLBACK_URL dynamically based on Render's hostname
if 'RENDER_EXTERNAL_HOSTNAME' in os.environ:
    auth0_callback_url = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/callback"
else:
    auth0_callback_url = os.environ.get('AUTH0_CALLBACK_URL', 'http://localhost:5000/callback')

app.config['AUTH0_CALLBACK_URL'] = auth0_callback_url

# Set redirect_uri based on environment
if os.getenv('CODESPACE_NAME'):
    # Running in GitHub Codespaces
    redirect_uri = f"https://{os.getenv('CODESPACE_NAME')}-5000.{os.getenv('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN')}/callback"
else:
    # Use AUTH0_CALLBACK_URL from environment (for both local and production)
    redirect_uri = os.getenv('AUTH0_CALLBACK_URL', 'http://localhost:5000/callback')

# Initialize admin interface (secured)
init_admin(app, db, Todo)

if __name__ == '__main__':
    app.run(debug=True)
