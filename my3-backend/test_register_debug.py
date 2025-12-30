"""Debug script to test registration and see the actual error."""
import asyncio
import sys
from app.database.connection import get_db, AsyncSessionLocal
from app.database.models import User
from app.database.schemas import UserCreate, UserResponse
from app.utils.auth import get_password_hash, create_access_token
from sqlalchemy import select
from datetime import timedelta

async def test_register():
    """Test registration logic step by step."""
    try:
        # Create test data
        user_data = UserCreate(
            email="debug@example.com",
            password="testpass123",
            name="Debug User"
        )
        print(f"1. Created UserCreate: {user_data}")
        
        # Get database session
        async with AsyncSessionLocal() as db:
            # Check if user exists
            result = await db.execute(select(User).where(User.email == user_data.email))
            existing_user = result.scalar_one_or_none()
            print(f"2. Checked existing user: {existing_user}")
            
            if existing_user:
                print("User already exists, deleting...")
                await db.delete(existing_user)
                await db.commit()
            
            # Hash password
            hashed_password = get_password_hash(user_data.password)
            print(f"3. Hashed password: {hashed_password[:20]}...")
            
            # Create user
            new_user = User(
                email=user_data.email,
                name=user_data.name,
                hashed_password=hashed_password
            )
            print(f"4. Created User object: {new_user}")
            
            db.add(new_user)
            await db.commit()
            print(f"5. Committed to database")
            
            await db.refresh(new_user)
            print(f"6. Refreshed user: id={new_user.id}, created_at={new_user.created_at}")
            
            # Create token
            access_token_expires = timedelta(days=7)
            access_token = create_access_token(
                data={"sub": str(new_user.id)},
                expires_delta=access_token_expires
            )
            print(f"7. Created access token: {access_token[:50]}...")
            
            # Try to create UserResponse
            try:
                user_response = UserResponse.model_validate(new_user)
                print(f"8. Created UserResponse: {user_response}")
            except Exception as e:
                print(f"8. ERROR creating UserResponse: {e}")
                print(f"   User object: id={new_user.id}, email={new_user.email}, name={new_user.name}")
                print(f"   User object type: {type(new_user)}")
                print(f"   User object attributes: {dir(new_user)}")
                raise
            
            # Return dict
            result_dict = {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user_response
            }
            print(f"9. Created result dict")
            print(f"SUCCESS! Registration would work.")
            
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_register())
    sys.exit(0 if success else 1)


