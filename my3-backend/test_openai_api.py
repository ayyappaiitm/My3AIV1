"""
Test script to check if OpenAI API key is valid and has credits.
"""
import asyncio
import sys
from langchain_openai import ChatOpenAI
from app.config import settings

async def test_openai_api():
    """Test OpenAI API connection and credits."""
    print("=" * 80)
    print("Testing OpenAI API Connection")
    print("=" * 80)
    
    # Check if API key is set
    if not settings.openai_api_key:
        print("ERROR: OpenAI API key is not set in environment variables")
        print("Please set OPENAI_API_KEY in your .env file")
        return False
    
    print(f"[OK] API Key found: {settings.openai_api_key[:10]}...{settings.openai_api_key[-4:]}")
    
    try:
        # Create LLM instance
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=settings.openai_api_key
        )
        
        print("[OK] LLM instance created")
        print("Testing API call...")
        
        # Make a simple test call
        response = await llm.ainvoke("Say 'Hello, API test successful!' and nothing else.")
        
        print("[OK] API call successful!")
        print(f"Response: {response.content}")
        print("=" * 80)
        print("[SUCCESS] OpenAI API is working correctly!")
        print("=" * 80)
        return True
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        
        print("=" * 80)
        print("[FAILED] API CALL FAILED")
        print("=" * 80)
        print(f"Error Type: {error_type}")
        print(f"Error Message: {error_msg}")
        print()
        
        # Check for specific error types
        if "authentication" in error_msg.lower() or "invalid" in error_msg.lower() or "401" in error_msg:
            print("[CRITICAL] ISSUE: Authentication Error")
            print("   - Your API key may be invalid or expired")
            print("   - Please check your OPENAI_API_KEY in .env file")
            print("   - Verify the key at https://platform.openai.com/api-keys")
        elif "rate limit" in error_msg.lower() or "429" in error_msg:
            print("[WARNING] ISSUE: Rate Limit Error")
            print("   - You've exceeded the rate limit")
            print("   - Please wait a few minutes and try again")
        elif "insufficient" in error_msg.lower() or "quota" in error_msg.lower() or "credit" in error_msg.lower():
            print("[CRITICAL] ISSUE: Credit/Quota Exhausted")
            print("   - Your OpenAI account has run out of credits")
            print("   - Please add credits at https://platform.openai.com/account/billing")
        elif "timeout" in error_msg.lower():
            print("[WARNING] ISSUE: Request Timeout")
            print("   - The API request took too long")
            print("   - This might be a temporary network issue")
        else:
            print("[ERROR] ISSUE: Unknown Error")
            print("   - Please check the error message above")
            print("   - Verify your OpenAI account status at https://platform.openai.com/account")
        
        print("=" * 80)
        return False

if __name__ == "__main__":
    success = asyncio.run(test_openai_api())
    sys.exit(0 if success else 1)

