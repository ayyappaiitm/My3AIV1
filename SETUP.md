# My3AI Setup Instructions

## Backend Setup

1. **Navigate to backend directory:**
   ```powershell
   cd my3-backend
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Upgrade pip:**
   ```powershell
   python -m pip install --upgrade pip
   ```

5. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

6. **Create .env file:**
   ```powershell
   copy .env.example .env
   ```
   Then edit `.env` and add your:
   - OpenAI API key
   - Secret key (generate a random string)
   - Database URL (default should work)

7. **Start PostgreSQL with Docker:**
   ```powershell
   docker-compose up -d
   ```

8. **Run database migrations:**
   ```powershell
   alembic upgrade head
   ```

9. **Start the backend server:**
   ```powershell
   uvicorn app.main:app --reload
   ```
   Backend will be available at: http://localhost:8000
   API docs: http://localhost:8000/docs

## Frontend Setup

1. **Navigate to frontend directory:**
   ```powershell
   cd ..\my3-frontend
   ```

2. **Install dependencies:**
   ```powershell
   npm install
   ```

3. **Create .env.local file:**
   ```powershell
   copy .env.local.example .env.local
   ```
   Edit `.env.local` and set:
   - `NEXT_PUBLIC_API_URL=http://localhost:8000`
   - `NEXTAUTH_SECRET` (generate a random string)

4. **Start the development server:**
   ```powershell
   npm run dev
   ```
   Frontend will be available at: http://localhost:3000

## Quick Start (After Setup)

**Terminal 1 - Backend:**
```powershell
cd my3-backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd my3-frontend
npm run dev
```

**Terminal 3 - Database (if needed):**
```powershell
cd my3-backend
docker-compose up -d
```

## Troubleshooting

- **If virtual environment activation fails:** Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell
- **If Docker fails:** Make sure Docker Desktop is running
- **If port 8000 or 3000 is in use:** Change ports in config files

