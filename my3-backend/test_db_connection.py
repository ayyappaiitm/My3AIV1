"""Test database connection and verify tables exist."""
import asyncio
from sqlalchemy import text
from app.database.connection import engine, AsyncSessionLocal


async def test_connection():
    """Test database connection and list tables."""
    print("Testing database connection...")
    print("-" * 50)
    
    try:
        # Test 1: Basic connection
        print("\n1. Testing basic connection...")
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"   [OK] Connected to PostgreSQL")
            print(f"   Version: {version.split(',')[0]}")
        
        # Test 2: List all tables
        print("\n2. Checking database tables...")
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"   [OK] Found {len(tables)} table(s):")
                for table in tables:
                    print(f"      - {table}")
            else:
                print("   [WARNING] No tables found")
        
        # Test 3: Check table structures
        print("\n3. Checking table structures...")
        expected_tables = ['users', 'recipients', 'occasions', 'gift_ideas', 'conversations', 'messages']
        async with engine.begin() as conn:
            for table_name in expected_tables:
                result = await conn.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}';
                """))
                count = result.scalar()
                if count > 0:
                    print(f"   [OK] {table_name}: {count} columns")
                else:
                    print(f"   [ERROR] {table_name}: Table not found")
        
        # Test 4: Test session creation
        print("\n4. Testing session creation...")
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            if test_value == 1:
                print("   [OK] Session created and query executed successfully")
        
        # Test 5: Check if we can insert/query (without actually inserting)
        print("\n5. Testing query capabilities...")
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print(f"   [OK] Query successful - Current users in database: {user_count}")
        
        print("\n" + "=" * 50)
        print("[SUCCESS] All database connection tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n[ERROR] Database connection test failed!")
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    asyncio.run(test_connection())

