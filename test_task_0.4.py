"""
Task 0.4 Verification Script
Tests:
1. Backend /docs shows API endpoints
2. Frontend landing page loads
3. Database connection works
4. Commit initial code (manual step)
"""

import sys
import io
import requests
import subprocess
import time
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except AttributeError:
        pass  # Already wrapped or not available

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}[PASS] {text}{RESET}")

def print_error(text):
    print(f"{RED}[FAIL] {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}[WARN] {text}{RESET}")

def print_info(text):
    print(f"{BLUE}[INFO] {text}{RESET}")

def test_backend_docs():
    """Test 1: Backend /docs shows API endpoints"""
    print_header("TEST 1: Backend API Documentation")
    
    try:
        # Check if backend is running
        print_info("Checking if backend is running on http://localhost:8000...")
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        
        if response.status_code == 200:
            print_success("Backend is running!")
            print(f"   Health check response: {response.json()}")
        else:
            print_error(f"Backend health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Backend is not running. Please start it with:")
        print("   cd my3-backend")
        print("   uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print_error(f"Error checking backend: {e}")
        return False
    
    try:
        # Check /docs endpoint
        print_info("Checking /docs endpoint...")
        response = requests.get("http://localhost:8000/docs", timeout=5)
        
        if response.status_code == 200:
            print_success("API documentation is accessible at http://localhost:8000/docs")
            
            # Check for OpenAPI JSON
            openapi_response = requests.get("http://localhost:8000/openapi.json", timeout=5)
            if openapi_response.status_code == 200:
                openapi_data = openapi_response.json()
                paths = openapi_data.get("paths", {})
                print_success(f"Found {len(paths)} API endpoints:")
                for path in sorted(paths.keys()):
                    methods = list(paths[path].keys())
                    print(f"   - {path} [{', '.join(methods).upper()}]")
                return True
            else:
                print_warning("Could not fetch OpenAPI JSON")
                return True  # Still pass if /docs loads
        else:
            print_error(f"/docs endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error checking /docs: {e}")
        return False

def test_frontend_landing():
    """Test 2: Frontend landing page loads"""
    print_header("TEST 2: Frontend Landing Page")
    
    try:
        print_info("Checking if frontend is running on http://localhost:3000...")
        response = requests.get("http://localhost:3000", timeout=5)
        
        if response.status_code == 200:
            print_success("Frontend is running!")
            
            # Check if it's a Next.js page (should contain React/Next.js indicators)
            content = response.text.lower()
            if "my3" in content or "hero" in content or "next" in content:
                print_success("Landing page content detected")
            else:
                print_warning("Landing page loaded but content verification unclear")
            
            # Check for common Next.js indicators
            if "_next" in content or "react" in content:
                print_success("Next.js framework detected")
            
            print_info("Landing page is accessible at http://localhost:3000")
            return True
        else:
            print_error(f"Frontend returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Frontend is not running. Please start it with:")
        print("   cd my3-frontend")
        print("   npm run dev")
        return False
    except Exception as e:
        print_error(f"Error checking frontend: {e}")
        return False

def test_database_connection():
    """Test 3: Database connection works"""
    print_header("TEST 3: Database Connection")
    
    backend_dir = Path("my3-backend")
    if not backend_dir.exists():
        print_error("my3-backend directory not found")
        return False
    
    # Check if PostgreSQL container is running
    print_info("Checking if PostgreSQL container is running...")
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=my3_postgres", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "my3_postgres" in result.stdout:
            print_success("PostgreSQL container is running")
        else:
            print_warning("PostgreSQL container not running. Starting it...")
            print_info("Run: cd my3-backend && docker-compose up -d")
            # Try to start it
            try:
                subprocess.run(
                    ["docker-compose", "up", "-d"],
                    cwd=backend_dir,
                    timeout=30,
                    check=False
                )
                print_info("Waiting for PostgreSQL to be ready...")
                time.sleep(5)
            except Exception as e:
                print_warning(f"Could not auto-start container: {e}")
                return False
    except FileNotFoundError:
        print_error("Docker not found. Please install Docker or start PostgreSQL manually")
        return False
    except Exception as e:
        print_error(f"Error checking Docker: {e}")
        return False
    
    # Test database connection using Python
    print_info("Testing database connection...")
    test_script = backend_dir / "test_db_connection.py"
    
    if test_script.exists():
        try:
            # Change to backend directory and run the test
            result = subprocess.run(
                [sys.executable, "test_db_connection.py"],
                cwd=str(backend_dir.absolute()),
                capture_output=True,
                text=True,
                timeout=30,
                env=os.environ.copy()
            )
            
            if result.returncode == 0:
                print_success("Database connection successful!")
                if result.stdout:
                    print(f"   {result.stdout.strip()}")
                return True
            else:
                print_error("Database connection test failed")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
                return False
        except Exception as e:
            print_error(f"Error running database test: {e}")
            return False
    else:
        # Create a simple test script
        print_warning("test_db_connection.py not found. Creating one...")
        test_script_content = '''import asyncio
from app.database.connection import engine, AsyncSessionLocal
from app.config import settings

async def test_connection():
    try:
        async with AsyncSessionLocal() as session:
            # Simple query to test connection
            result = await session.execute("SELECT 1")
            print("Database connection successful!")
            print(f"Database URL: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'configured'}")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
'''
        with open(test_script, "w") as f:
            f.write(test_script_content)
        
        print_info("Created test_db_connection.py. Please run it manually:")
        print(f"   cd my3-backend && python test_db_connection.py")
        return None  # Indeterminate

def check_git_status():
    """Test 4: Check git status for commit"""
    print_header("TEST 4: Git Status Check")
    
    try:
        # Check if git is initialized
        result = subprocess.run(
            ["git", "status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print_success("Git repository initialized")
            
            # Check for uncommitted changes
            if "nothing to commit" in result.stdout.lower():
                print_info("No uncommitted changes")
            else:
                print_warning("You have uncommitted changes")
                print_info("To commit initial code:")
                print("   git add .")
                print("   git commit -m 'Initial commit: Sprint 0 setup complete'")
            
            # Check if there are any commits
            commit_result = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if commit_result.returncode == 0 and commit_result.stdout.strip():
                print_success("Repository has commits")
                print(f"   Latest: {commit_result.stdout.strip()}")
            else:
                print_warning("No commits yet. Ready to commit initial code.")
            
            return True
        else:
            print_warning("Git not initialized or not a git repository")
            print_info("To initialize git:")
            print("   git init")
            print("   git add .")
            print("   git commit -m 'Initial commit: Sprint 0 setup complete'")
            return False
            
    except FileNotFoundError:
        print_warning("Git not found. Please install Git or commit manually")
        return False
    except Exception as e:
        print_error(f"Error checking git status: {e}")
        return False

def main():
    print_header("TASK 0.4 VERIFICATION - Sprint 0 Setup")
    print("Testing all requirements from Task 0.4...\n")
    
    results = {
        "Backend /docs": test_backend_docs(),
        "Frontend landing": test_frontend_landing(),
        "Database connection": test_database_connection(),
        "Git status": check_git_status()
    }
    
    print_header("TEST SUMMARY")
    
    passed = 0
    failed = 0
    warnings = 0
    
    for test_name, result in results.items():
        if result is True:
            print_success(f"{test_name}: PASSED")
            passed += 1
        elif result is False:
            print_error(f"{test_name}: FAILED")
            failed += 1
        else:
            print_warning(f"{test_name}: NEEDS MANUAL CHECK")
            warnings += 1
    
    print(f"\n{GREEN}Passed: {passed}{RESET}")
    if warnings > 0:
        print(f"{YELLOW}Warnings: {warnings}{RESET}")
    if failed > 0:
        print(f"{RED}Failed: {failed}{RESET}")
    
    print("\n" + "="*60)
    if failed == 0 and warnings == 0:
        print(f"{GREEN}[SUCCESS] All tests passed! Sprint 0 setup is complete.{RESET}")
    elif failed == 0:
        print(f"{YELLOW}[WARNING] Most tests passed. Please check warnings above.{RESET}")
    else:
        print(f"{RED}[ERROR] Some tests failed. Please fix the issues above.{RESET}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

