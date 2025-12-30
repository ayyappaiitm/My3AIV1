"""
Manual script to add occasions to recipients.
Usage: python add_occasion_manual.py <user_email> <recipient_name> <occasion_name> <date>
Example: python add_occasion_manual.py user@example.com "Manasa" "Birthday" "November 30"
"""
import asyncio
import sys
from datetime import date
from sqlalchemy import select
from app.database.connection import get_db
from app.database.models import User, Recipient, Occasion, OccasionStatus
import re

async def add_occasion_manual(user_email: str, recipient_name: str, occasion_name: str, date_str: str):
    """Manually add an occasion to a recipient."""
    async for db in get_db():
        # Get user
        result = await db.execute(
            select(User).where(User.email == user_email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ User with email '{user_email}' not found.")
            return
        
        # Find recipient (fuzzy match)
        recipients_result = await db.execute(
            select(Recipient).where(Recipient.user_id == user.id)
        )
        recipients = recipients_result.scalars().all()
        
        # Try exact match first
        recipient = None
        for r in recipients:
            if r.name.lower().strip() == recipient_name.lower().strip():
                recipient = r
                break
        
        # Try fuzzy match
        if not recipient:
            from difflib import SequenceMatcher
            best_match = None
            best_score = 0.7  # threshold
            for r in recipients:
                similarity = SequenceMatcher(None, recipient_name.lower(), r.name.lower()).ratio()
                if similarity > best_score:
                    best_score = similarity
                    best_match = r
            recipient = best_match
        
        if not recipient:
            print(f"❌ Recipient '{recipient_name}' not found.")
            print(f"Available recipients: {[r.name for r in recipients]}")
            return
        
        print(f"✅ Found recipient: {recipient.name} (ID: {recipient.id})")
        
        # Parse date
        occasion_date = None
        try:
            # Try ISO format first
            try:
                from datetime import datetime as dt
                occasion_date = dt.fromisoformat(date_str.replace("Z", "+00:00")).date()
            except:
                # Try parsing natural language dates
                month_map = {
                    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
                    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
                }
                date_str_lower = date_str.lower()
                today = date.today()
                current_year = today.year
                
                for month_name, month_num in month_map.items():
                    if month_name in date_str_lower:
                        day_match = re.search(r'(\d+)', date_str)
                        if day_match:
                            day = int(day_match.group(1))
                            try:
                                test_date = date(current_year, month_num, day)
                                if test_date < today:
                                    occasion_date = date(current_year + 1, month_num, day)
                                else:
                                    occasion_date = test_date
                            except ValueError:
                                try:
                                    occasion_date = date(current_year + 1, month_num, day)
                                except ValueError:
                                    print(f"⚠️  Invalid date: {month_num}/{day}")
                                pass
                            break
        except Exception as e:
            print(f"⚠️  Could not parse date '{date_str}': {e}")
        
        # Create occasion
        new_occasion = Occasion(
            user_id=user.id,
            recipient_id=recipient.id,
            name=occasion_name,
            occasion_type=occasion_name.lower(),
            date=occasion_date,
            status=OccasionStatus.IDEA_NEEDED
        )
        db.add(new_occasion)
        await db.commit()
        await db.refresh(new_occasion)
        
        print(f"✅ Created occasion: {occasion_name} for {recipient.name}")
        if occasion_date:
            print(f"   Date: {occasion_date}")
        else:
            print(f"   Date: {date_str} (could not parse, stored as text)")
        print(f"   Occasion ID: {new_occasion.id}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python add_occasion_manual.py <user_email> <recipient_name> <occasion_name> <date>")
        print('Example: python add_occasion_manual.py user@example.com "Manasa" "Birthday" "November 30"')
        print('Example: python add_occasion_manual.py user@example.com "Ritika" "Birthday" "April 16"')
        sys.exit(1)
    
    user_email = sys.argv[1]
    recipient_name = sys.argv[2]
    occasion_name = sys.argv[3]
    date_str = sys.argv[4]
    
    asyncio.run(add_occasion_manual(user_email, recipient_name, occasion_name, date_str))

