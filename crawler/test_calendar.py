"""Test Google Calendar event creation"""
import asyncio, asyncpg, os
from dotenv import load_dotenv
load_dotenv()

from google_calendar import refresh_access_token, create_medication_reminder
from datetime import date

url = os.getenv("DATABASE_URL").replace("postgresql+asyncpg://", "postgresql://")

async def test():
    # Get the refresh token from DB
    conn = await asyncpg.connect(url)
    row = await conn.fetchrow("SELECT google_refresh_token FROM users WHERE id = 8")
    await conn.close()
    
    refresh_token = row["google_refresh_token"]
    print(f"Refresh token: {refresh_token[:20]}...")

    # Step 1: Test token refresh
    print("\n--- Step 1: Refreshing access token ---")
    access_token = await refresh_access_token(refresh_token)
    if access_token:
        print(f"Access token OK: {access_token[:20]}...")
    else:
        print("FAILED to refresh token. Calendar API may not be enabled.")
        return

    # Step 2: Test creating a calendar event
    print("\n--- Step 2: Creating test calendar event ---")
    event_id = await create_medication_reminder(
        refresh_token=refresh_token,
        medication_name="Test Medication",
        dosage="100mg",
        time_of_day="09:00",
        frequency="daily",
        start_date=date.today(),
        notes="This is a test reminder - can be deleted",
    )
    
    if event_id:
        print(f"SUCCESS! Event created: {event_id}")
    else:
        print("FAILED to create event")

asyncio.run(test())
