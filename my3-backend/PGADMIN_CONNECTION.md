# Connecting pgAdmin to My3 Docker Database

## Connection Details

- **Host:** localhost (or 127.0.0.1)
- **Port:** 5433 (NOT 5432 - that's your local PostgreSQL)
- **Database:** my3_db
- **Username:** postgres
- **Password:** postgres

## Steps to Add Connection in pgAdmin

1. **Right-click on "Servers"** in the left panel
2. Select **"Register" → "Server..."**
3. In the **"General" tab:**
   - Name: `My3 Docker Database` (or any name you prefer)
4. In the **"Connection" tab:**
   - Host name/address: `localhost`
   - Port: `5433` ⚠️ **IMPORTANT: Use 5433, not 5432**
   - Maintenance database: `my3_db`
   - Username: `postgres`
   - Password: `postgres`
   - Check "Save password" if you want
5. Click **"Save"**

## Verify Docker Container is Running

```powershell
docker ps --filter "name=my3_postgres"
```

If not running, start it:
```powershell
cd my3-backend
docker-compose up -d
```

## Troubleshooting

- **Can't connect?** Make sure Docker container is running
- **Wrong database?** Check you're using port 5433, not 5432
- **Connection refused?** Verify container is healthy: `docker ps`




