# Migrating to PostgreSQL

This guide explains how to upgrade your Flask Todo App from SQLite to PostgreSQL for production use on Render.

## Why Migrate to PostgreSQL?

- **Reliability**: SQLite is file-based and not ideal for production web apps
- **Concurrency**: PostgreSQL handles multiple concurrent users better
- **Scalability**: Better performance as your app grows
- **Data Persistence**: Render's free PostgreSQL databases are more stable than file-based SQLite

## When to Migrate

- Your app is getting real users
- You need guaranteed data persistence
- You're moving beyond testing/development

## Prerequisites

- Existing Flask Todo App deployed on Render
- Access to your Render dashboard
- Your app source code updated locally

## Step 1: Create PostgreSQL Database on Render

1. **Log in to Render Dashboard**
   - Go to [dashboard.render.com](https://dashboard.render.com)

2. **Create New PostgreSQL Database**
   - Click "New +" button
   - Select "PostgreSQL"
   - Choose your preferred region (same as your web service recommended)
   - Name your database (e.g., "flask-todo-db")
   - Plan: Free tier available
   - Click "Create Database"

3. **Wait for Database to Initialize**
   - This takes a few minutes
   - Once ready, you'll see the connection details

## Step 2: Update Your Application Code

### Install PostgreSQL Driver

Add psycopg2 to your `requirements.txt`:

```
Flask==2.3.0
SQLAlchemy==2.0.0
psycopg2-binary==2.9.6
# ...other dependencies...
```

### Update Database Configuration

In your `app.py`, update the database URI to use PostgreSQL when the `DATABASE_URL` environment variable is present:

```python
import os
from flask import Flask
from sqlalchemy import create_engine

app = Flask(__name__)

# Use DATABASE_URL if available (Render), otherwise use SQLite
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Fix the PostgreSQL URI format for SQLAlchemy
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
```

## Step 3: Update render.yaml

Update your `render.yaml` to include the PostgreSQL database and link it to your web service:

```yaml
services:
  - type: web
    name: flask-todo-app
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.10
      - key: OAUTHLIB_INSECURE_TRANSPORT
        value: "0"
      - key: APP_SECRET_KEY
        generateValue: true
      - key: AUTH0_DOMAIN
        sync: false
      - key: AUTH0_CLIENT_ID
        sync: false
      - key: AUTH0_CLIENT_SECRET
        sync: false
      - key: AUTH0_CALLBACK_URL
        value: https://${RENDER_EXTERNAL_HOSTNAME}/callback
      - key: DATABASE_URL
        fromDatabase:
          name: flask-todo-db
          property: connectionString

databases:
  - name: flask-todo-db
    databaseName: flask_todo
    plan: free
```

## Step 4: Create Database Tables

When your app first connects to PostgreSQL, it needs to create the tables:

### Option A: Automatic (Recommended)

Update your app initialization to create tables on startup:

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

# In your init_todo() function or app creation:
with app.app_context():
    db.create_all()
```

### Option B: Manual via Shell

1. SSH into your Render web service
2. Run:
   ```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

## Step 5: Deploy Updated Code

1. **Commit and push your changes**
   ```bash
   git add requirements.txt app.py render.yaml
   git commit -m "Add PostgreSQL support"
   git push origin main
   ```

2. **Render automatically redeploys**
   - Check the "Logs" tab in Render dashboard
   - Wait for build to complete

## Step 6: Verify Migration

1. Visit your app: `https://<your-app-name>.onrender.com`
2. Create a test todo
3. Refresh the page - data should persist
4. Check Render PostgreSQL dashboard to confirm queries are running

## Rollback to SQLite (If Needed)

If you need to go back to SQLite:

1. Remove the `DATABASE_URL` environment variable from Render
2. Revert your `app.py` to use SQLite only
3. Push to GitHub
4. Render will redeploy with SQLite

## Troubleshooting

### "Ident authentication failed"

- Your `DATABASE_URL` may be malformed
- Ensure you're using `postgresql://` not `postgres://`
- Check that the connection string includes username and password

### "relation 'todo' does not exist"

- Tables haven't been created yet
- Ensure `db.create_all()` runs on app startup
- Check application logs for errors

### Connection Timeout

- PostgreSQL service may still be starting
- Wait a few minutes and try again
- Check that your web service can reach the database (same region recommended)

### Data Lost After Redeploy

- Free tier databases may have limitations
- Consider upgrading to a paid plan for production
- Alternatively, implement regular backups

## Useful Links

- [Render PostgreSQL Documentation](https://render.com/docs/databases)
- [SQLAlchemy PostgreSQL Dialect](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-envars.html)
- [Database Migrations with Flask-Migrate](https://flask-migrate.readthedocs.io/)

## Next Steps

Once PostgreSQL is running reliably:

- Implement database migrations using [Flask-Migrate](https://flask-migrate.readthedocs.io/)
- Set up automated backups in Render
- Consider upgrading to a paid database plan for production use
