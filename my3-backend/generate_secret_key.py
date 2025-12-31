#!/usr/bin/env python3
"""
Generate a secure random secret key for JWT authentication.

Usage:
    python generate_secret_key.py

This will output a secure random string suitable for use as SECRET_KEY.
"""

import secrets

if __name__ == "__main__":
    # Generate a URL-safe random string (32 bytes = 256 bits)
    secret_key = secrets.token_urlsafe(32)
    print(f"\nGenerated SECRET_KEY:")
    print(f"{secret_key}\n")
    print("Copy this value and set it as SECRET_KEY in your Railway environment variables.")
    print("⚠️  Keep this secret key secure and never commit it to version control!\n")

