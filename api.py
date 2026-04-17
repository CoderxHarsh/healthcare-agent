from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import os
import urllib.parse
import httpx
import requests  # pip install requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import date, datetime
#for database operations
from database import engine, Base, get_db, disconnect_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
#importing the functions from crud.py
from crud import (
    upsert_user, create_health_log, get_user_health_logs, 
    get_health_metrics_summary, get_latest_health_log,
    update_user_onboarding, complete_onboarding, get_user_profile,
    create_medication, get_user_medications, get_medication_by_id,
    deactivate_medication, log_medication_status, get_medication_logs,
    get_adherence_stats
)
#for creating tables on startup and disconnecting db on shutdown
from database import engine, Base, get_db
from models import User
from data_parser import HealthMetricParser
from google_calendar import create_medication_reminder, delete_medication_reminder

app = FastAPI()

#Functions to handle database connection on startup and shutdown
@app.get("/startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database connected")

#for shutdown, we will dispose the engine to close all connections gracefully
@app.get("/shutdown")
async def shutdown():
    await disconnect_db()


load_dotenv(Path("./.env"))
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI]):
    raise RuntimeError("Missing required Google OAuth environment variables")

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v2/userinfo"


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h2>Welcome to FastAPI Google OAuth2 Login</h2>
    <a href="/login">Login with Google</a>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint to verify configuration"""
    return {
        "status": "healthy",
        "api": "running",
        "google_configured": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET),
        "database_url_set": bool(os.getenv("DATABASE_URL")),
        "environment": {
            "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID[:20] + "..." if GOOGLE_CLIENT_ID else "NOT SET",
            "GOOGLE_REDIRECT_URI": GOOGLE_REDIRECT_URI,
            "DATABASE_CONFIGURED": "YES" if "postgresql" in str(os.getenv("DATABASE_URL", "")).lower() else "NO"
        }
    }


@app.get("/login")
def login():
    query_params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/calendar",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{GOOGLE_AUTH_ENDPOINT}?{urllib.parse.urlencode(query_params)}"
    return RedirectResponse(url)


@app.get("/auth/callback")
async def auth_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        code = request.query_params.get("code")
        if not code:
            print("❌ No authorization code found")
            raise HTTPException(status_code=400, detail="Authorization code not found")

        print(f"📝 Authorization code received: {code[:20]}...")
        
        # Exchange code for access token
        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        try:
            async with httpx.AsyncClient() as client:
                print("🔄 Exchanging code for token...")
                token_response = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data, timeout=30)
                
                if token_response.status_code != 200:
                    print(f"❌ Token error: {token_response.status_code} - {token_response.text}")
                    raise HTTPException(status_code=400, detail=f"Token exchange failed: {token_response.text}")
                
                token_data = token_response.json()
                access_token = token_data.get("access_token")

                if not access_token:
                    print(f"❌ No access token in response: {token_data}")
                    raise HTTPException(status_code=400, detail="Failed to retrieve access token")

                print("✅ Token received")
                
                # Get user info from Google
                print("🔄 Fetching user info...")
                headers = {"Authorization": f"Bearer {access_token}"}
                userinfo_response = await client.get(GOOGLE_USERINFO_ENDPOINT, headers=headers, timeout=30)
                
                if userinfo_response.status_code != 200:
                    print(f"❌ Userinfo error: {userinfo_response.status_code} - {userinfo_response.text}")
                    raise HTTPException(status_code=400, detail="Failed to get user info")
                
                userinfo = userinfo_response.json()
                print(f"✅ User info from Google: {userinfo}")
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ HTTP request error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to communicate with Google: {str(e)}")

        # Save user to database (including refresh_token for Calendar API)
        try:
            refresh_token = token_data.get("refresh_token")
            if refresh_token:
                print(f"🔑 Refresh token received — will store for Calendar API")
            else:
                print(f"⚠️ No refresh token (user may have already granted access)")

            print(f"💾 Saving user to database...")
            user = await upsert_user(
                db,
                google_sub=userinfo.get("id"),
                email=userinfo.get("email"),
                name=userinfo.get("name"),
                picture=userinfo.get("picture"),
                refresh_token=refresh_token,
            )
            print(f"✅ User saved: {user.email} (ID: {user.id})")
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save user to database: {str(e)}")

        # Redirect based on onboarding status
        if not user.is_onboarded:
            redirect_url = f"http://localhost:8501/?user={user.email}&user_id={user.id}&onboarded=false"
        else:
            redirect_url = f"http://localhost:8501/?user={user.email}&user_id={user.id}&onboarded=true"
        
        print(f"🔗 Redirecting to: {redirect_url}")
        return RedirectResponse(url=redirect_url)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error in auth_callback: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    name = request.query_params.get("name")
    email = request.query_params.get("email")
    picture = request.query_params.get("picture")

    return f"""
    <html>
        <head><title>User Profile</title></head>
        <body style='text-align:center; font-family:sans-serif;'>
            <h1>Welcome, {name}!</h1>
            <img src="{picture}" alt="Profile Picture" width="120"/><br>
            <p>Email: {email}</p>
        </body>
    </html>
    """


# ============================================
# PYDANTIC MODELS FOR HEALTH LOGS
# ============================================

class HealthLogCreate(BaseModel):
    metric_type: str
    value: str
    unit: str
    notes: str = None
    source: str = "manual"


class HealthLogResponse(BaseModel):
    id: int
    user_id: int
    metric_type: str
    value: str
    unit: str
    notes: str = None
    created_at: str
    source: str


# ============================================
# HEALTH LOG ENDPOINTS
# ============================================

@app.post("/health-logs/{user_id}")
async def log_health_metric(
    user_id: int,
    log_data: HealthLogCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new health log entry"""
    try:
        health_log = await create_health_log(
            db,
            user_id=user_id,
            metric_type=log_data.metric_type,
            value=log_data.value,
            unit=log_data.unit,
            notes=log_data.notes,
            source=log_data.source
        )
        return {
            "status": "success",
            "message": f"✅ Health metric ({log_data.metric_type}) logged successfully",
            "log_id": health_log.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/health-logs/{user_id}/from-text")
async def log_from_text(
    user_id: int,
    request_body: dict,
    db: AsyncSession = Depends(get_db)
):
    """Parse and log health metrics from natural language text"""
    text = request_body.get("text", "")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text input is required")
    
    # Parse metrics from text
    metrics = HealthMetricParser.parse(text)
    
    if not metrics:
        return {
            "status": "no_metrics",
            "message": "No health metrics found in the provided text"
        }
    
    logged_metrics = []
    for metric in metrics:
        health_log = await create_health_log(
            db,
            user_id=user_id,
            metric_type=metric["metric_type"],
            value=metric["value"],
            unit=metric["unit"],
            source="chatbot"
        )
        logged_metrics.append({
            "metric_type": metric["metric_type"],
            "value": metric["value"],
            "unit": metric["unit"]
        })
    
    return {
        "status": "success",
        "message": f"✅ Logged {len(logged_metrics)} health metric(s)",
        "metrics": logged_metrics
    }


@app.get("/health-logs/{user_id}")
async def get_logs(
    user_id: int,
    metric_type: str = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get user's health logs"""
    try:
        logs = await get_user_health_logs(db, user_id, metric_type=metric_type, days=days)
        return {
            "status": "success",
            "count": len(logs),
            "logs": [
                {
                    "id": log.id,
                    "metric_type": log.metric_type,
                    "value": log.value,
                    "unit": log.unit,
                    "notes": log.notes,
                    "created_at": log.created_at.isoformat(),
                    "source": log.source
                }
                for log in logs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health-logs/{user_id}/latest/{metric_type}")
async def get_latest_log(
    user_id: int,
    metric_type: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the latest health log for a specific metric type"""
    try:
        log = await get_latest_health_log(db, user_id, metric_type)
        
        if not log:
            raise HTTPException(status_code=404, detail=f"No logs found for metric: {metric_type}")
        
        return {
            "status": "success",
            "log": {
                "id": log.id,
                "metric_type": log.metric_type,
                "value": log.value,
                "unit": log.unit,
                "notes": log.notes,
                "created_at": log.created_at.isoformat(),
                "source": log.source
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health-logs/{user_id}/summary")
async def get_summary(
    user_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get a summary of all health metrics for the user"""
    try:
        summary = await get_health_metrics_summary(db, user_id, days=days)
        
        return {
            "status": "success",
            "period_days": days,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# ONBOARDING ENDPOINTS
# ============================================

class OnboardingData(BaseModel):
    age: int = None
    gender: str = None
    height_cm: float = None
    weight_kg: float = None
    health_conditions: str = None
    medications: str = None
    allergies: str = None
    fitness_level: str = None
    health_goals: str = None


@app.get("/onboarding")
async def onboarding_page():
    """Redirect to Streamlit onboarding page"""
    return RedirectResponse(url="http://localhost:8501/?page=onboarding")


@app.post("/user/{user_id}/onboarding")
async def save_onboarding(
    user_id: int,
    data: OnboardingData,
    db: AsyncSession = Depends(get_db)
):
    """Save user's onboarding health profile"""
    print(f"💾 Saving onboarding data for user_id: {user_id} (type: {type(user_id)})")
    try:
        user = await update_user_onboarding(
            db,
            user_id=user_id,
            age=data.age,
            gender=data.gender,
            height_cm=data.height_cm,
            weight_kg=data.weight_kg,
            health_conditions=data.health_conditions,
            medications=data.medications,
            allergies=data.allergies,
            fitness_level=data.fitness_level,
            health_goals=data.health_goals
        )
        
        print(f"✅ Onboarding data saved for {user.email}")
        return {
            "status": "success",
            "message": "✅ Health profile updated successfully"
        }
    except ValueError as e:
        print(f"❌ Value error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"❌ Unexpected error in save_onboarding: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/user/{user_id}/complete-onboarding")
async def complete_user_onboarding(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Mark user as onboarded and redirect to dashboard"""
    try:
        user = await complete_onboarding(db, user_id)
        
        return {
            "status": "success",
            "message": "✅ Onboarding completed!",
            "user_id": user.id,
            "email": user.email
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/user/{user_id}/profile")
async def get_user_profile_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user's complete profile including onboarding info"""
    try:
        user = await get_user_profile(db, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "status": "success",
            "profile": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_onboarded": user.is_onboarded,
                "age": user.age,
                "gender": user.gender,
                "height_cm": user.height_cm,
                "weight_kg": user.weight_kg,
                "health_conditions": user.health_conditions,
                "medications": user.medications,
                "allergies": user.allergies,
                "fitness_level": user.fitness_level,
                "health_goals": user.health_goals,
                "onboarded_at": user.onboarded_at.isoformat() if user.onboarded_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# MEDICATION ENDPOINTS
# ============================================

class MedicationCreate(BaseModel):
    name: str
    dosage: str = None
    frequency: str = "daily"  # daily, twice_daily, weekly, as_needed
    time_of_day: str = "08:00"
    start_date: str = None  # ISO date string
    end_date: str = None
    notes: str = None


class MedicationLogCreate(BaseModel):
    scheduled_date: str  # ISO date string
    status: str  # "taken" or "skipped"


@app.post("/medications/{user_id}")
async def add_medication(
    user_id: int,
    data: MedicationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a new medication and create a Google Calendar reminder"""
    try:
        # Parse dates
        start = date.fromisoformat(data.start_date) if data.start_date else date.today()
        end = date.fromisoformat(data.end_date) if data.end_date else None

        # Try to create Google Calendar event
        gcal_event_id = None
        user = await get_user_profile(db, user_id)
        if user and user.google_refresh_token:
            gcal_event_id = await create_medication_reminder(
                refresh_token=user.google_refresh_token,
                medication_name=data.name,
                dosage=data.dosage or "",
                time_of_day=data.time_of_day,
                frequency=data.frequency,
                start_date=start,
                end_date=end,
                notes=data.notes,
            )

        # Save medication to database
        medication = await create_medication(
            db,
            user_id=user_id,
            name=data.name,
            dosage=data.dosage,
            frequency=data.frequency,
            time_of_day=data.time_of_day,
            start_date=start,
            end_date=end,
            notes=data.notes,
            gcal_event_id=gcal_event_id,
        )

        return {
            "status": "success",
            "message": f"✅ Medication '{data.name}' added",
            "medication_id": medication.id,
            "calendar_event": "created" if gcal_event_id else "not created (no token)",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/medications/{user_id}")
async def list_medications(
    user_id: int,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Get all medications for a user"""
    try:
        meds = await get_user_medications(db, user_id, active_only=active_only)
        return {
            "status": "success",
            "count": len(meds),
            "medications": [
                {
                    "id": med.id,
                    "name": med.name,
                    "dosage": med.dosage,
                    "frequency": med.frequency,
                    "time_of_day": med.time_of_day,
                    "start_date": med.start_date.isoformat() if med.start_date else None,
                    "end_date": med.end_date.isoformat() if med.end_date else None,
                    "notes": med.notes,
                    "is_active": med.is_active,
                    "has_calendar_event": bool(med.gcal_event_id),
                }
                for med in meds
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/medications/{medication_id}/log")
async def log_medication(
    medication_id: int,
    data: MedicationLogCreate,
    db: AsyncSession = Depends(get_db)
):
    """Log whether a medication was taken or skipped"""
    try:
        med = await get_medication_by_id(db, medication_id)
        if not med:
            raise HTTPException(status_code=404, detail="Medication not found")

        if data.status not in ("taken", "skipped"):
            raise HTTPException(status_code=400, detail="Status must be 'taken' or 'skipped'")

        scheduled = date.fromisoformat(data.scheduled_date)
        log = await log_medication_status(
            db,
            medication_id=medication_id,
            user_id=med.user_id,
            scheduled_date=scheduled,
            status=data.status,
        )

        return {
            "status": "success",
            "message": f"✅ Medication marked as '{data.status}'",
            "log_id": log.id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/medications/{medication_id}")
async def remove_medication(
    medication_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Deactivate a medication and remove its Google Calendar event"""
    try:
        med = await get_medication_by_id(db, medication_id)
        if not med:
            raise HTTPException(status_code=404, detail="Medication not found")

        # Delete Google Calendar event if exists
        if med.gcal_event_id:
            user = await get_user_profile(db, med.user_id)
            if user and user.google_refresh_token:
                await delete_medication_reminder(user.google_refresh_token, med.gcal_event_id)

        # Soft-delete the medication
        await deactivate_medication(db, medication_id)

        return {
            "status": "success",
            "message": f"✅ Medication '{med.name}' removed",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/medications/{user_id}/adherence")
async def medication_adherence(
    user_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get medication adherence statistics"""
    try:
        stats = await get_adherence_stats(db, user_id, days=days)
        return {
            "status": "success",
            **stats,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))