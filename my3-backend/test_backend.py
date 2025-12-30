#!/usr/bin/env python3
"""
Simple script to test My3 backend API endpoints.
Run this after starting the server: uvicorn app.main:app --reload
"""

import requests
import json
import sys
import os
from typing import Optional

# Fix Windows encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health_check():
    """Test the health check endpoint."""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server. Is it running?")
        print("   Start with: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def register_user(email: str = "test@example.com", password: str = "testpassword123", name: str = "Test User"):
    """Register a new user."""
    print_section("2. Register User")
    try:
        data = {
            "email": email,
            "password": password,
            "name": name
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("[OK] User registered successfully")
            return True
        elif response.status_code == 409:
            print("[INFO] User already exists (this is OK)")
            return True
        else:
            print("[FAIL] Registration failed")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def login(email: str = "test@example.com", password: str = "testpassword123") -> Optional[tuple]:
    """Login and get access token."""
    print_section("3. Login")
    try:
        data = {
            "email": email,
            "password": password
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            token = result.get("access_token")
            # API returns "user" object, extract id from it
            user_obj = result.get("user", {})
            user_id = user_obj.get("id") if user_obj else None
            if not user_id:
                # Fallback: try user_id directly (for backward compatibility)
                user_id = result.get("user_id")
            print(f"[OK] Login successful")
            print(f"Token: {token[:50]}...")
            print(f"User ID: {user_id}")
            return (token, str(user_id))
        else:
            print(f"[FAIL] Login failed: {response.json()}")
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def get_recipients(token: str):
    """Get all recipients for the user."""
    print_section("4. Get Recipients")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/recipients", headers=headers, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            recipients = response.json()
            print(f"[OK] Found {len(recipients)} recipients")
            if recipients:
                print(f"Recipients: {json.dumps(recipients, indent=2)}")
            else:
                print("No recipients yet (empty list)")
            return True
        else:
            print(f"[FAIL] Failed: {response.json()}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def send_chat_message(token: str, user_id: str, message: str):
    """Send a chat message to the My3 agent."""
    print_section("5. Send Chat Message")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "message": message,
            "user_id": user_id
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=data, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] Chat message sent successfully")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"[FAIL] Failed: {response.json()}")
            return False
    except requests.exceptions.Timeout:
        print("[TIMEOUT] Request timed out (this might be normal for LLM calls)")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_root_endpoint():
    """Test the root endpoint."""
    print_section("0. Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "My3 Backend API Test Suite" + "\n")
    print(f"Testing server at: {BASE_URL}")
    print("Make sure the server is running: uvicorn app.main:app --reload\n")
    
    results = []
    
    # Test root endpoint
    results.append(("Root Endpoint", test_root_endpoint()))
    
    # Test health check
    results.append(("Health Check", test_health_check()))
    
    if not results[-1][1]:
        print("\n[ERROR] Server is not responding. Please start the server first.")
        sys.exit(1)
    
    # Register user
    results.append(("Register User", register_user()))
    
    # Login
    login_result = login()
    if not login_result:
        print("\n[ERROR] Cannot proceed without authentication token.")
        sys.exit(1)
    
    token, user_id = login_result
    results.append(("Login", True))
    
    # Get recipients
    results.append(("Get Recipients", get_recipients(token)))
    
    # Send chat message (optional - requires OpenAI API key)
    print("\n[INFO] Chat test requires OpenAI API key. Skipping if not configured.")
    chat_result = send_chat_message(
        token, 
        user_id, 
        "My mom loves gardening, her birthday is April 16"
    )
    results.append(("Send Chat Message", chat_result))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

