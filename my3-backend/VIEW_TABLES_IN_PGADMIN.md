# How to View Tables in pgAdmin

## Steps to See Tables in my3_db:

1. **Expand "my3_db" database** (click the arrow next to it)
2. **Expand "Schemas (1)"**
3. **Expand "public"** (this is where your tables are)
4. **Expand "Tables"** - You should see all 7 tables:
   - alembic_version
   - conversations
   - gift_ideas
   - messages
   - occasions
   - recipients
   - users

## Quick Navigation Path:
```
My3 Port 5433
  └── Databases
      └── my3_db
          └── Schemas (1)
              └── public
                  └── Tables (7) ← Your tables are here!
```

## If Tables Don't Appear:

1. Right-click on "my3_db" → "Refresh"
2. Make sure you're looking under "Schemas" → "public" → "Tables"
3. Check that the database connection is active (green icon)



