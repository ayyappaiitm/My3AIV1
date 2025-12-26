"""Simple script to check database tables and their contents."""
import asyncio
from sqlalchemy import text
from app.database.connection import engine


async def show_tables():
    """Display all tables and their row counts."""
    print("=" * 60)
    print("DATABASE TABLES OVERVIEW")
    print("=" * 60)
    
    async with engine.begin() as conn:
        # Get all tables
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """))
        tables = [row[0] for row in result.fetchall()]
        
        print(f"\nFound {len(tables)} tables:\n")
        
        for table in tables:
            # Get row count
            count_result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = count_result.scalar()
            
            # Get column names
            cols_result = await conn.execute(text(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table}'
                ORDER BY ordinal_position;
            """))
            columns = [(row[0], row[1]) for row in cols_result.fetchall()]
            
            print(f"Table: {table}")
            print(f"  Rows: {count}")
            print(f"  Columns ({len(columns)}):")
            for col_name, col_type in columns:
                print(f"    - {col_name} ({col_type})")
            print()


async def show_table_data(table_name: str, limit: int = 10):
    """Show data from a specific table."""
    async with engine.begin() as conn:
        # Get column names first
        cols_result = await conn.execute(text(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
        """))
        columns = [row[0] for row in cols_result.fetchall()]
        
        if not columns:
            print(f"Table '{table_name}' not found!")
            return
        
        # Get data
        result = await conn.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
        rows = result.fetchall()
        
        print(f"\n{'=' * 60}")
        print(f"TABLE: {table_name} (showing {len(rows)} rows)")
        print(f"{'=' * 60}\n")
        
        if rows:
            # Print header
            print(" | ".join(columns))
            print("-" * 60)
            
            # Print rows
            for row in rows:
                values = [str(val)[:30] if val is not None else "NULL" for val in row]
                print(" | ".join(values))
        else:
            print("(No data)")
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Show specific table data
        table_name = sys.argv[1]
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        asyncio.run(show_table_data(table_name, limit))
    else:
        # Show all tables overview
        asyncio.run(show_tables())
        print("\nTo view data from a specific table, run:")
        print("  python check_db_tables.py <table_name> [limit]")
        print("\nExample:")
        print("  python check_db_tables.py users")
        print("  python check_db_tables.py recipients 5")



