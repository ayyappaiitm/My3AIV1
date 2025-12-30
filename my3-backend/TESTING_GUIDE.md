# Backend Testing Guide

This guide shows you how to test the My3 backend API.

## Prerequisites

1. **Start PostgreSQL database:**
   ```bash
   cd my3-backend
   docker-compose up -d
   ```

2. **Set up environment variables:**
   Create a `.env` file in `my3-backend/` with:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/my3_db
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your_secret_key_here_min_32_chars
   CORS_ORIGINS=http://localhost:3000
   ENVIRONMENT=development
   ```

3. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Server will run at: `http://localhost:8000`

---

## Method 1: Swagger UI (Easiest) ⭐

The easiest way to test the API is using the auto-generated Swagger UI:

1. **Open in browser:**
   ```
   http://localhost:8000/docs
   ```

2. **Test endpoints:**
   - Click on any endpoint (e.g., `GET /api/health`)
   - Click "Try it out"
   - Click "Execute"
   - See the response below

3. **For authenticated endpoints:**
   - Click the "Authorize" button (top right)
   - Enter: `Bearer <your_jwt_token>`
   - Token format: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**Example Flow:**
1. Test `/api/health` (no auth needed)
2. Register user: `POST /api/auth/register`
3. Login: `POST /api/auth/login` → Copy the `access_token`
4. Authorize with token
5. Test `/api/recipients` (requires auth)

---

## Method 2: Using curl (Command Line)

### 1. Health Check (No Auth)
```bash
curl http://localhost:8000/api/health
```

### 2. Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "name": "Test User"
  }'
```

### 3. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

**Save the token:**
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

### 4. Get Recipients (With Auth)
```bash
curl http://localhost:8000/api/recipients \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Send Chat Message
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "My mom loves gardening, her birthday is April 16",
    "user_id": "your-user-id-here"
  }'
```

---

## Method 3: Using Python Requests

Create a test script `test_backend.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Health Check
print("1. Testing Health Check...")
response = requests.get(f"{BASE_URL}/api/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# 2. Register User
print("2. Registering user...")
register_data = {
    "email": "test@example.com",
    "password": "testpassword123",
    "name": "Test User"
}
response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    print(f"User registered: {response.json()}\n")
else:
    print(f"Error: {response.json()}\n")

# 3. Login
print("3. Logging in...")
login_data = {
    "email": "test@example.com",
    "password": "testpassword123"
}
response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    token = response.json()["access_token"]
    user_id = response.json()["user_id"]
    print(f"Token received: {token[:50]}...\n")
else:
    print(f"Error: {response.json()}\n")
    exit(1)

# 4. Get Recipients (with auth)
print("4. Getting recipients...")
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/api/recipients", headers=headers)
print(f"Status: {response.status_code}")
print(f"Recipients: {response.json()}\n")

# 5. Send Chat Message
print("5. Sending chat message...")
chat_data = {
    "message": "My mom loves gardening, her birthday is April 16",
    "user_id": user_id
}
response = requests.post(f"{BASE_URL}/api/chat", json=chat_data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")
```

Run it:
```bash
python test_backend.py
```

---

## Method 4: Running pytest Tests

Run the existing test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=app tests/
```

---

## Method 5: Using Postman or Insomnia

1. **Import OpenAPI spec:**
   - Go to `http://localhost:8000/openapi.json`
   - Copy the JSON
   - Import into Postman/Insomnia

2. **Set up environment:**
   - Create environment variable: `base_url = http://localhost:8000`
   - Create variable: `token` (will be set after login)

3. **Test flow:**
   - Register → Login → Save token → Use token in other requests

---

## Quick Test Checklist

- [ ] Health check works: `GET /api/health`
- [ ] Can register user: `POST /api/auth/register`
- [ ] Can login: `POST /api/auth/login`
- [ ] Can get recipients (empty list): `GET /api/recipients`
- [ ] Can send chat message: `POST /api/chat`
- [ ] Can create recipient via chat
- [ ] Can get recipient details: `GET /api/recipients/{id}`
- [ ] Can update recipient: `PUT /api/recipients/{id}`
- [ ] Can delete recipient: `DELETE /api/recipients/{id}`
- [ ] Max 10 recipients limit enforced

---

## Troubleshooting

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker ps

# Check database logs
docker logs my3_postgres

# Restart database
docker-compose restart postgres
```

### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Mac/Linux

# Or change port
uvicorn app.main:app --reload --port 8001
```

### Missing Environment Variables
```bash
# Check if .env file exists
ls -la .env

# Verify variables are loaded
python -c "from app.config import settings; print(settings.database_url)"
```

### OpenAI API Errors
- Verify `OPENAI_API_KEY` is set correctly
- Check API key has credits
- Verify network connection

---

## Next Steps

Once backend is tested and working:
1. Proceed to frontend development (Sprint 1, Day 9-11)
2. Test end-to-end flow with frontend
3. Deploy to production (Sprint 3)


