# Railway Deployment Guide

This guide walks you through deploying the My3 backend to Railway.

## Prerequisites

- Railway account (sign up at [railway.app](https://railway.app))
- GitHub account with the `my3-backend` repository
- OpenAI API key
- Google Maps API key (optional, for address validation)

## Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `my3-backend` repository
5. Railway will automatically detect the Dockerfile and start building

## Step 2: Add PostgreSQL Database

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically create a PostgreSQL database
4. The `DATABASE_URL` environment variable will be automatically set

**Note:** Railway provides the `DATABASE_URL` in the format `postgresql://...`. The application automatically converts this to `postgresql+asyncpg://` for async SQLAlchemy operations. This conversion is handled automatically in `app/database/connection.py` - no manual configuration needed.

## Step 3: Set Environment Variables

In your Railway project, go to **Variables** tab and add the following:

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | ✅ **Auto-set by Railway** - Don't manually set this | `postgresql://...` |
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-...` |
| `SECRET_KEY` | JWT secret key (see below for generation) | `your-secret-key-here` |
| `CORS_ORIGINS` | Frontend URL(s), comma-separated | `https://yourdomain.com,https://www.yourdomain.com` |
| `ENVIRONMENT` | Set to `production` | `production` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_MAPS_API_KEY` | For address validation | (none) |
| `ENABLE_ADDRESS_VALIDATION` | Enable/disable address validation | `true` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FORMAT` | Log format (`json` or `text`) | `json` |

### Generate SECRET_KEY

Generate a secure random secret key using one of these methods:

**Option 1: Python**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Option 2: OpenSSL**
```bash
openssl rand -hex 32
```

**Option 3: Online Generator**
- Use a secure random string generator (at least 32 characters)

Copy the generated key and paste it as the `SECRET_KEY` value in Railway.

## Step 4: Configure Build Settings

Railway should auto-detect the Dockerfile. Verify these settings:

1. Go to your service → **Settings** → **Build**
2. **Root Directory**: Leave empty (or set to `my3-backend` if repo is monorepo)
3. **Dockerfile Path**: `Dockerfile` (should be auto-detected)
4. **Build Command**: (not needed, Dockerfile handles this)
5. **Start Command**: (not needed, Dockerfile CMD handles this)

## Step 5: Deploy

1. Railway will automatically deploy when you push to your main branch
2. Or click **"Deploy"** in the Railway dashboard
3. Wait for the build to complete (check the **Deployments** tab)

## Step 6: Run Database Migrations

After the first deployment, run migrations:

1. In Railway dashboard, go to your service
2. Click **"Deployments"** → Select the latest deployment
3. Click **"View Logs"** to open the terminal
4. Or use Railway CLI:

```bash
# Install Railway CLI (if not installed)
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run migrations
railway run alembic upgrade head
```

**Alternative: Using Railway Dashboard**
1. Go to your service → **Settings** → **Deploy**
2. Add a one-time command: `alembic upgrade head`
3. Or use the **Shell** feature in Railway dashboard

## Step 7: Verify Deployment

### Test Health Endpoint

```bash
# Get your Railway service URL (e.g., https://my3-backend-production.up.railway.app)
curl https://your-service-url.railway.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Test API Documentation

Visit: `https://your-service-url.railway.app/docs`

You should see the Swagger UI with all API endpoints.

### Test Database Connection

The health endpoint will verify database connectivity. If it shows `"database": "connected"`, you're good!

## Step 8: Get Your Service URL

1. In Railway dashboard, go to your service
2. Click **"Settings"** → **"Networking"**
3. Your service URL will be shown (e.g., `https://my3-backend-production.up.railway.app`)
4. Copy this URL - you'll need it for:
   - Frontend `NEXT_PUBLIC_API_URL` environment variable
   - Testing API endpoints
   - Updating CORS origins if needed

## Step 9: Update CORS Origins (If Needed)

If your frontend URL changes, update the `CORS_ORIGINS` variable:

1. Go to **Variables** tab
2. Update `CORS_ORIGINS` with your frontend URL(s)
3. Railway will automatically redeploy

Example:
```
CORS_ORIGINS=https://my3-app.vercel.app,https://www.my3-app.com
```

## Monitoring & Logs

### View Logs

1. Go to your service → **Deployments**
2. Click on a deployment → **"View Logs"**
3. Or use Railway CLI: `railway logs`

### Monitor Metrics

Railway provides:
- CPU usage
- Memory usage
- Network traffic
- Request count

View these in the **Metrics** tab of your service.

## Troubleshooting

### Build Fails

- Check build logs for errors
- Verify `requirements.txt` is correct
- Ensure Dockerfile syntax is valid
- Check that all dependencies are listed

### Database Connection Errors

- Verify `DATABASE_URL` is set (should be auto-set by Railway)
- Check PostgreSQL service is running
- Ensure migrations have been run: `railway run alembic upgrade head`
- **Note:** The application automatically converts Railway's `postgresql://` URL to `postgresql+asyncpg://` for async SQLAlchemy. This is handled in `app/database/connection.py`.

### Application Crashes

- Check logs for error messages
- Verify all required environment variables are set
- Check that `SECRET_KEY` is set and valid
- Verify `OPENAI_API_KEY` is correct

### CORS Errors

- Verify `CORS_ORIGINS` includes your frontend URL
- Check that frontend is using the correct backend URL
- Ensure no trailing slashes in URLs

### Migration Issues

- Check that `alembic` is in `requirements.txt`
- Verify `alembic.ini` is present
- Ensure migration files are in `alembic/versions/`
- Run: `railway run alembic current` to check migration status

## Environment Variables Checklist

Before going live, verify all variables are set:

- [ ] `DATABASE_URL` (auto-set by Railway)
- [ ] `OPENAI_API_KEY`
- [ ] `SECRET_KEY`
- [ ] `CORS_ORIGINS`
- [ ] `ENVIRONMENT=production`
- [ ] `GOOGLE_MAPS_API_KEY` (optional)
- [ ] `ENABLE_ADDRESS_VALIDATION` (optional, defaults to `true`)

## Next Steps

After successful deployment:

1. ✅ Test all API endpoints
2. ✅ Update frontend with Railway backend URL
3. ✅ Set up monitoring and alerts
4. ✅ Configure custom domain (if needed)
5. ✅ Set up automated backups for PostgreSQL

## Railway CLI Commands Reference

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs

# Run command in Railway environment
railway run <command>

# Example: Run migrations
railway run alembic upgrade head

# Example: Open shell
railway shell

# View variables
railway variables

# Set variable
railway variables set KEY=value
```

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app

