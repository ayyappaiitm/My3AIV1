# Railway Deployment - Quick Start Checklist

Use this checklist for a quick deployment to Railway.

## Pre-Deployment

- [ ] Railway account created
- [ ] GitHub repository is ready
- [ ] OpenAI API key available
- [ ] Frontend URL ready (for CORS configuration)

## Deployment Steps

### 1. Create Project
- [ ] Go to [railway.app](https://railway.app)
- [ ] Click "New Project" → "Deploy from GitHub repo"
- [ ] Select `my3-backend` repository

### 2. Add Database
- [ ] Click "+ New" → "Database" → "Add PostgreSQL"
- [ ] Wait for database to provision (DATABASE_URL auto-set)

### 3. Set Environment Variables
Go to **Variables** tab and add:

- [ ] `OPENAI_API_KEY` = `sk-...` (your OpenAI key)
- [ ] `SECRET_KEY` = (run `python generate_secret_key.py` to generate)
- [ ] `CORS_ORIGINS` = `https://your-frontend-url.vercel.app` (or your frontend URL)
- [ ] `ENVIRONMENT` = `production`
- [ ] `GOOGLE_MAPS_API_KEY` = (optional, for address validation)
- [ ] `ENABLE_ADDRESS_VALIDATION` = `true` (optional, defaults to true)

**Note:** `DATABASE_URL` is automatically set by Railway - don't set it manually!

### 4. Deploy
- [ ] Railway will auto-deploy (or click "Deploy")
- [ ] Wait for build to complete
- [ ] Check deployment logs for errors

### 5. Run Migrations
- [ ] Open Railway CLI or use dashboard shell
- [ ] Run: `railway run alembic upgrade head`
- [ ] Verify migrations completed successfully

### 6. Verify Deployment
- [ ] Test health endpoint: `https://your-service.railway.app/api/health`
- [ ] Test API docs: `https://your-service.railway.app/docs`
- [ ] Verify database connection in health check response

### 7. Get Service URL
- [ ] Go to Settings → Networking
- [ ] Copy service URL
- [ ] Update frontend `NEXT_PUBLIC_API_URL` with this URL

## Post-Deployment

- [ ] Update frontend environment variables
- [ ] Test end-to-end flow (signup → login → chat)
- [ ] Monitor logs for errors
- [ ] Set up alerts (optional)

## Troubleshooting

**Build fails?**
- Check build logs
- Verify `requirements.txt` is correct
- Ensure Dockerfile is valid

**Database errors?**
- Verify migrations ran: `railway run alembic current`
- Check DATABASE_URL is set (should be auto-set)
- Run migrations: `railway run alembic upgrade head`

**CORS errors?**
- Verify `CORS_ORIGINS` includes your frontend URL
- Check no trailing slashes in URLs

## Generate SECRET_KEY

```bash
python generate_secret_key.py
```

Or use:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Full Documentation

See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for detailed instructions.

