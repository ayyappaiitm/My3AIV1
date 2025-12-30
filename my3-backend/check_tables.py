"""Quick script to check if database tables exist."""
import asyncio
from app.database.connection import engine
from sqlalchemy import text

async def check_tables():
    try:
        async with engine.begin() as conn:
            result = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
            tables = [row[0] for row in result]
            print("Database tables found:")
            for table in sorted(tables):
                print(f"  - {table}")
            
            if "users" in tables:
                # Check if users table has data
                count_result = await conn.execute(text("SELECT COUNT(*) FROM users"))
                count = count_result.scalar()
                print(f"\nUsers table has {count} records")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_tables())


