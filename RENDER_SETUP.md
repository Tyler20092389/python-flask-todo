# Deployment on Render

## Prerequisites

1. **GitHub Repository**: Your code must be pushed to a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com) (free tier available)
3. **Auth0 Application**: Configured with your production callback URL

## Auth0 Setup (Production)

Before deploying to Render, set up Auth0 for production:

1. **Create an Auth0 Account**
   - Go to [auth0.com](https://auth0.com) and sign up

2. **Create an Application**
   - Dashboard → Applications → Create Application
   - Choose "Regular Web Applications"
   - Name: Flask Todo App

3. **Configure Application Settings**
   - "Allowed Callback URLs": `https://<your-app-name>.onrender.com/callback`
   - "Allowed Logout URLs": `https://<your-app-name>.onrender.com/`
   - "Allowed Web Origins": `https://<your-app-name>.onrender.com`
   - Example: `https://flask-todo-app.onrender.com/callback`

4. **Save Credentials**
   - Copy your Auth0 Domain, Client ID, and Client Secret
   - You'll need these for Render environment variables in Step 3

## Step 1: Prepare Your Repository

Ensure your repository contains:
- `render.yaml` (blueprint configuration file)
- `requirements.txt` (Python dependencies)
- All application code pushed to GitHub
- Use `python -m gunicorn app:app --bind 0.0.0.0:5000` to confirm that everything works ok under gunicorn before trying Render

## Step 2: Create a Blueprint on Render

1. **Log in to Render Dashboard**
   - Go to [dashboard.render.com](https://dashboard.render.com)

2. **Create New Blueprint**
   - Click the "New +" button in the top right
   - Select "Blueprint" from the dropdown menu
   - [Direct Link to Create Blueprint](https://dashboard.render.com/select-repo?type=blueprint)

3. **Connect Your GitHub Repository**
   - Click "Connect account" if this is your first time
   - Authorize Render to access your GitHub repositories
   - Search for select your version of `python-flask-todo`
   - Click "Connect"

4. **Review Blueprint Configuration**
   - Render will detect your `render.yaml` file
   - Review the services that will be created (web service, database, etc.)
   - Give your blueprint instance a name (e.g., "flask-todo-app")
   - Click "Apply"

## Step 3: Configure Environment Variables
   
   Add these in Render Dashboard → Environment:
   
   ```
   AUTH0_CLIENT_ID=your_client_id
   AUTH0_CLIENT_SECRET=your_client_secret
   AUTH0_DOMAIN=your_auth0_domain
   APP_SECRET_KEY=your_secret_key
   AUTH0_CALLBACK_URL=https://your-app-name.onrender.com/callback
   ```
   
   **Important:** Replace `your-app-name.onrender.com` with your actual Render app URL (found in your Render dashboard).
   
   **Important:** Do NOT set `RENDER_EXTERNAL_HOSTNAME` manually. Render sets this automatically, but it's only available at runtime, not during build.
   
   **For Auth0 Configuration:** Use your actual Render app URL (e.g., `https://python-flask-todo.onrender.com`) in Auth0 settings, not the variable name.

3. **Automatic Deployment**
   - Render will automatically build and deploy your application
   - Wait for the build to complete (check the "Logs" tab)
   - Your app will be available at `https://<your-app-name>.onrender.com`
   - **Note**: The SQLite database file will persist on Render's filesystem

## Step 4: Update Auth0 Settings

1. **Add Production Callback URL**
   - Go to [Auth0 Dashboard](https://manage.auth0.com)
   - Navigate to your application settings
   - Add to "Allowed Callback URLs": `https://<your-app-name>.onrender.com/callback`
   - Add to "Allowed Logout URLs": `https://<your-app-name>.onrender.com/`
   - Add to "Allowed Web Origins": `https://<your-app-name>.onrender.com`
   - Click "Save Changes"

## Step 5: Test Your Deployment

1. Visit your Render URL: `https://<your-app-name>.onrender.com`
2. Click "Login" - should redirect to Auth0
3. Complete authentication
4. Verify you can create and manage todos

## Continuous Deployment

Once set up, Render automatically deploys when you push to your main branch:

1. Make changes to your code locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```
3. Render detects the push and automatically rebuilds/redeploys
4. Monitor deployment progress in the Render dashboard

## Troubleshooting

- **Build Fails**: Check the "Logs" tab in Render dashboard for errors
- **Auth0 Redirect Error**: Verify callback URLs match exactly (including https://)
- **Environment Variables**: Ensure all required variables are set in Render
- **Database Issues**: Render free tier databases sleep after inactivity; first request may be slow

## Upgrading to PostgreSQL

Once your app grows and you need a more robust database, see [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md) for a complete migration guide.

## Useful Links

- [Render Blueprint Documentation](https://render.com/docs/infrastructure-as-code)
- [Render Python Deployment Guide](https://render.com/docs/deploy-flask)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Auth0 Production Checklist](https://auth0.com/docs/deploy-monitor/deploy/production-checklist)
