"""
Script to check which recipients have occasions stored in the database.
Run this from the backend directory: python check_occasions.py <user_email>
"""
import asyncio
import sys
from sqlalchemy import select
from app.database.connection import get_db
from app.database.models import User, Recipient, Occasion

async def check_occasions(user_email: str):
    """Check all recipients and their occasions for a user."""
    async for db in get_db():
        # Get user
        result = await db.execute(
            select(User).where(User.email == user_email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ User with email '{user_email}' not found.")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.id})\n")
        print("=" * 80)
        
        # Get all recipients
        recipients_result = await db.execute(
            select(Recipient).where(Recipient.user_id == user.id)
            .order_by(Recipient.name)
        )
        recipients = recipients_result.scalars().all()
        
        if not recipients:
            print("❌ No recipients found for this user.")
            return
        
        print(f"📋 Found {len(recipients)} recipient(s):\n")
        
        for recipient in recipients:
            print(f"\n👤 {recipient.name}")
            print(f"   Relationship: {recipient.relationship_type or 'N/A'}")
            print(f"   ID: {recipient.id}")
            
            # Get occasions for this recipient
            occasions_result = await db.execute(
                select(Occasion).where(Occasion.recipient_id == recipient.id)
                .order_by(Occasion.date if Occasion.date else Occasion.created_at)
            )
            occasions = occasions_result.scalars().all()
            
            if occasions:
                print(f"   ✅ Has {len(occasions)} occasion(s):")
                for occ in occasions:
                    date_str = str(occ.date) if occ.date else "No date"
                    print(f"      - {occ.name} ({occ.occasion_type or 'N/A'}) on {date_str}")
            else:
                print(f"   ❌ No occasions stored")
        
        print("\n" + "=" * 80)
        print("\n💡 To add a birthday occasion, tell My3:")
        print('   Example: "Visala\'s birthday is June 30th"')
        print('   Example: "Add Manasa Veena, her birthday is November 1st"')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_occasions.py <user_email>")
        print("Example: python check_occasions.py user@example.com")
        sys.exit(1)
    
    user_email = sys.argv[1]
    asyncio.run(check_occasions(user_email))

