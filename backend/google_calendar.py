"""
Google Calendar Integration Module
-----------------------------------
Creates and manages medication reminder events in Google Calendar.
Uses the user's stored refresh_token to make API calls on their behalf.
No extra dependencies needed — uses httpx (already installed with FastAPI).
"""

import httpx
import os
import json
from datetime import datetime, timedelta, date
from typing import Optional, Dict
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Load .env from root directory (works from any location)
env_path = find_dotenv() or Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_CALENDAR_API = "https://www.googleapis.com/calendar/v3"


async def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Use the stored refresh_token to get a fresh access_token.
    Returns the access_token or None if refresh fails.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_ENDPOINT,
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=15,
        )

        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print(f"❌ Token refresh failed: {response.status_code} - {response.text}")
            return None


def _build_recurrence_rule(frequency: str) -> list:
    """Build iCalendar RRULE based on medication frequency"""
    rules = {
        "daily": ["RRULE:FREQ=DAILY"],
        "twice_daily": ["RRULE:FREQ=DAILY"],  # We'll create 2 events for twice_daily
        "weekly": ["RRULE:FREQ=WEEKLY"],
        "monthly": ["RRULE:FREQ=MONTHLY"],
        "as_needed": [],  # No recurrence for as-needed
    }
    return rules.get(frequency, ["RRULE:FREQ=DAILY"])


async def create_medication_reminder(
    refresh_token: str,
    medication_name: str,
    dosage: str,
    time_of_day: str,
    frequency: str,
    start_date: date,
    end_date: Optional[date] = None,
    notes: Optional[str] = None,
) -> Optional[str]:
    """
    Create a recurring medication reminder event in Google Calendar.
    
    Returns the Google Calendar event ID, or None on failure.
    """
    access_token = await refresh_access_token(refresh_token)
    if not access_token:
        print("❌ Cannot create calendar event: token refresh failed")
        return None

    # Parse time (e.g., "08:00")
    try:
        hour, minute = map(int, time_of_day.split(":"))
    except (ValueError, AttributeError):
        hour, minute = 8, 0  # Default to 8:00 AM

    # Build event start/end datetime
    start_dt = datetime(start_date.year, start_date.month, start_date.day, hour, minute)
    end_dt = start_dt + timedelta(minutes=15)  # 15-min event window

    # Build description
    description = f"💊 Time to take: {medication_name}"
    if dosage:
        description += f" ({dosage})"
    if notes:
        description += f"\n📝 Notes: {notes}"
    description += "\n\nCreated by HealthCare AI Assistant"

    # Build event body
    event = {
        "summary": f"💊 {medication_name} - {dosage}" if dosage else f"💊 {medication_name}",
        "description": description,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "Asia/Kolkata",  # Indian timezone
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 5},     # Browser popup 5 min before
                {"method": "email", "minutes": 15},     # Email 15 min before
            ],
        },
        "colorId": "11",  # Red color for medication events
    }

    # Add recurrence rule
    recurrence = _build_recurrence_rule(frequency)
    if recurrence:
        if end_date:
            # Add UNTIL to the recurrence rule
            until_str = end_date.strftime("%Y%m%dT235959Z")
            recurrence = [rule + f";UNTIL={until_str}" for rule in recurrence]
        event["recurrence"] = recurrence

    # Create the event via Google Calendar API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GOOGLE_CALENDAR_API}/calendars/primary/events",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json=event,
            timeout=15,
        )

        if response.status_code in (200, 201):
            event_data = response.json()
            event_id = event_data.get("id")
            print(f"✅ Calendar event created: {event_id}")
            return event_id
        else:
            print(f"❌ Calendar event creation failed: {response.status_code} - {response.text}")
            return None


async def delete_medication_reminder(
    refresh_token: str,
    gcal_event_id: str,
) -> bool:
    """
    Delete a medication reminder event from Google Calendar.
    Returns True on success.
    """
    if not gcal_event_id:
        return True  # Nothing to delete

    access_token = await refresh_access_token(refresh_token)
    if not access_token:
        print("❌ Cannot delete calendar event: token refresh failed")
        return False

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{GOOGLE_CALENDAR_API}/calendars/primary/events/{gcal_event_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
        )

        if response.status_code in (200, 204):
            print(f"✅ Calendar event deleted: {gcal_event_id}")
            return True
        elif response.status_code == 404:
            print(f"⚠️ Calendar event not found (already deleted): {gcal_event_id}")
            return True
        else:
            print(f"❌ Calendar event deletion failed: {response.status_code} - {response.text}")
            return False
