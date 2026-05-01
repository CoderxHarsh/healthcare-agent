"""
FastAPI Backend for HealthCare AI Assistant
============================================
Handles Google OAuth authentication, user profile management, 
health metrics logging, medication tracking, and API endpoints.
"""

# FastAPI core - Web framework for building APIs
from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File
# Response types - HTML and redirect responses for web UI
from fastapi.responses import HTMLResponse, RedirectResponse
# Pydantic - Data validation and serialization
from pydantic import BaseModel
from typing import Optional
# tempfile - Temporary file handling for uploads
import tempfile
# os - Environment variable and path handling
import os
# urllib.parse - URL encoding for OAuth parameters
import urllib.parse
# httpx - Async HTTP client for Google API calls
import httpx
# requests - HTTP client for making external API calls
import requests  # pip install requests
# python-dotenv - Load .env configuration files
from dotenv import load_dotenv, find_dotenv
# pathlib - Cross-platform file path handling
from pathlib import Path
# datetime - Date and time operations
from datetime import date, datetime
import pandas as pd
import json
import xml.etree.ElementTree as ET
from io import BytesIO

# Database connection, session management, and table initialization
from .database import engine, Base, get_db, disconnect_db
# SQLAlchemy async - Async database operations
from sqlalchemy.ext.asyncio import AsyncSession
# SQLAlchemy select - Building SQL queries
from sqlalchemy.future import select
# SQLAlchemy text - Executing raw SQL statements
from sqlalchemy import text

# CRUD operations - User, health logs, medications, and onboarding functions
from .crud import (
    upsert_user, create_health_log, get_user_health_logs, 
    get_health_metrics_summary, get_latest_health_log,
    update_user_onboarding, complete_onboarding, get_user_profile,
    create_medication, get_user_medications, get_medication_by_id,
    deactivate_medication, log_medication_status, get_medication_logs,
    get_adherence_stats
)

# SQLAlchemy models - User database model
from .models import User
# Health metric parser - Extract health metrics from natural language
from .data_parser import HealthMetricParser
# Google Calendar integration - Create/delete medication reminders
from .google_calendar import create_medication_reminder, delete_medication_reminder
# PDF Generation - Create health report PDFs
from .pdf_generator import generate_health_report_pdf, format_report_data
# Chatbot - Get LLM responses
from .chatbot import get_response
# Health Analyzer - ML-based health analysis and predictions
from .health_analyzer import get_health_analysis

app = FastAPI()

# CORS middleware — allow Streamlit Cloud (and localhost) to call this API
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "https://healthcare-agent-nuurhq4dt28vzlr5jeypa2.streamlit.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# PYDANTIC REQUEST MODELS
# ============================================

class ChatRequest(BaseModel):
    message: str
    user_profile: Optional[dict] = None
    health_logs: Optional[list] = None
    chat_history: Optional[list] = None

class MetricsParseRequest(BaseModel):
    text: str

# ============================================
# STARTUP & SHUTDOWN OPERATIONS
# ============================================

@app.get("/startup")
async def startup():
    """Initialize database tables on application startup"""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(Base.metadata.create_all)
    print("Database connected")

@app.get("/shutdown")
async def shutdown():
    """Gracefully close all database connections on application shutdown"""
    await disconnect_db()


# Load .env from root directory (works from any location)
env_path = find_dotenv() or Path(__file__).parent.parent / ".env"
load_dotenv(env_path)
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
    """Display home page with Google OAuth login link"""
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
    """Initiate Google OAuth2 flow by redirecting to Google's authorization endpoint"""
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
        encoded_name = urllib.parse.quote(user.name or "User")
        if not user.is_onboarded:
            redirect_url = f"http://localhost:8501/?user={encoded_name}&user_id={user.id}&onboarded=false"
        else:
            redirect_url = f"http://localhost:8501/?user={encoded_name}&user_id={user.id}&onboarded=true"
        
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
    """Display user's profile information from Google OAuth"""
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
# STREAMLIT OAUTH — user upsert endpoint
# ============================================

class GoogleLoginData(BaseModel):
    google_sub: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    refresh_token: Optional[str] = None


@app.post("/auth/google-login")
async def google_login(data: GoogleLoginData, db: AsyncSession = Depends(get_db)):
    """Accept user info from Streamlit OAuth flow and upsert into the database"""
    try:
        user = await upsert_user(
            db,
            google_sub=data.google_sub,
            email=data.email,
            name=data.name,
            picture=data.picture,
            refresh_token=data.refresh_token,
        )
        return {
            "user_id": user.id,
            "name": user.name or "User",
            "email": user.email,
            "is_onboarded": user.is_onboarded,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save user: {str(e)}")


# ============================================
# PYDANTIC MODELS - Data validation for health logs
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
# HEALTH LOG ENDPOINTS - Create and retrieve health metrics
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


@app.post("/health-logs/{user_id}/upload")
async def upload_health_logs(
    user_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload health logs via CSV, JSON, or XML"""
    contents = await file.read()
    filename = file.filename.lower()
    
    valid_records = []
    skipped_count = 0
    
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(contents))
            records = df.to_dict(orient="records")
        elif filename.endswith(".json"):
            records = json.loads(contents)
            if not isinstance(records, list):
                raise ValueError("JSON must be a list of records")
        elif filename.endswith(".xml"):
            root = ET.fromstring(contents)
            records = []
            for child in root:
                record = {}
                for subchild in child:
                    record[subchild.tag] = subchild.text
                records.append(record)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV, JSON, or XML.")
            
        for rec in records:
            # Flexible keys matching
            metric_type = rec.get("metric_type") or rec.get("metric") or rec.get("type")
            value = rec.get("value") or rec.get("val")
            unit = rec.get("unit") or rec.get("u")
            
            if not metric_type or value is None:
                skipped_count += 1
                continue
                
            date_str = rec.get("date") or rec.get("timestamp") or rec.get("created_at")
            created_at = None
            if date_str:
                try:
                    # Parse basic ISO or standard dates
                    created_at = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
                except Exception:
                    pass
            
            # Default unit if missing
            if not unit:
                unit = ""
                
            await create_health_log(
                db,
                user_id=user_id,
                metric_type=str(metric_type).lower().replace(" ", "_"),
                value=str(value),
                unit=str(unit),
                notes=rec.get("notes"),
                source="bulk_import",
                created_at=created_at
            )
            valid_records.append(rec)
            
        return {
            "status": "success",
            "message": f"✅ Imported {len(valid_records)} records. ⚠️ Skipped {skipped_count} invalid rows." if skipped_count else f"✅ Imported {len(valid_records)} records.",
            "imported": len(valid_records),
            "skipped": skipped_count
        }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")


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
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    health_conditions: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    fitness_level: Optional[str] = None
    health_goals: Optional[str] = None


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
# HEALTH GOALS ENDPOINTS
# ============================================

class GoalsUpdate(BaseModel):
    health_goals: Optional[str] = None
    weight_kg: Optional[float] = None
    fitness_level: Optional[str] = None

@app.patch("/user/{user_id}/goals")
async def update_user_goals(
    user_id: int,
    data: GoalsUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user's health goals, target weight, and fitness level"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if data.health_goals is not None:
            user.health_goals = data.health_goals
        if data.weight_kg is not None:
            user.weight_kg = data.weight_kg
        if data.fitness_level is not None:
            user.fitness_level = data.fitness_level

        await db.commit()
        await db.refresh(user)
        return {"status": "success", "message": "✅ Goals updated successfully"}
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


# ============================================
# EXPORT ENDPOINTS - Generate PDF reports
# ============================================

from fastapi.responses import FileResponse
import tempfile

@app.get("/export/health-report/{user_id}")
async def export_health_report(
    user_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Generate and download a PDF health report"""
    try:
        # Get user profile
        user = await get_user_profile(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get health logs
        health_logs_data = await get_user_health_logs(db, user_id, days=days)
        health_logs = [
            {
                "id": log.id,
                "metric_type": log.metric_type,
                "value": log.value,
                "unit": log.unit,
                "notes": log.notes,
                "created_at": log.created_at.isoformat(),
                "source": log.source
            }
            for log in health_logs_data
        ]
        
        # Get medications — split into active and past (soft-deleted)
        meds_data = await get_user_medications(db, user_id, active_only=False)
        
        def _fmt_med(med):
            return {
                "id": med.id,
                "name": med.name,
                "dosage": med.dosage,
                "frequency": med.frequency,
                "time_of_day": med.time_of_day,
                "start_date": med.start_date.isoformat() if med.start_date else None,
                "end_date": med.end_date.isoformat() if med.end_date else None,
                "notes": med.notes,
                "is_active": med.is_active,
            }
        
        active_medications = [_fmt_med(m) for m in meds_data if m.is_active]
        past_medications = [_fmt_med(m) for m in meds_data if not m.is_active]
        
        # Get adherence stats
        adherence_stats = await get_adherence_stats(db, user_id, days=days)
        adherence_dict = {
            med_id: {
                'adherence_rate': stats.get('adherence_rate', 0)
            }
            for med_id, stats in adherence_stats.get('medications', {}).items()
        }
        
        # Format user profile for report
        user_profile = {
            'name': user.name or 'User',
            'age': user.age,
            'gender': user.gender,
            'height_cm': user.height_cm,
            'weight_kg': user.weight_kg,
            'health_conditions': user.health_conditions or '',
            'medications': user.medications or '',
            'allergies': user.allergies or '',
            'fitness_level': user.fitness_level or 'Not specified',
            'health_goals': user.health_goals or '',
        }
        
        # Format data for PDF generation
        report_data = format_report_data(
            user_profile=user_profile,
            health_logs=health_logs,
            medications=active_medications,
            adherence_stats=adherence_dict,
            past_medications=past_medications
        )
        
        # Generate PDF
        pdf_data = generate_health_report_pdf(report_data)
        
        # Save to temporary file for download
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_data.getvalue())
            tmp_path = tmp.name
        
        return FileResponse(
            tmp_path,
            media_type="application/pdf",
            filename=f"health_report_{user.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating health report: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Failed to generate report: {str(e)}")


# ============================================
# CHATBOT & AI ENDPOINTS
# ============================================

@app.get("/user/{user_id}/vitals-summary")
async def get_vitals_summary(user_id: int, db: AsyncSession = Depends(get_db)):
    """Generate a personalized AI analysis of the user's health using ML model."""
    try:
        # Get user profile
        profile = await get_user_profile(db, user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get recent health logs
        logs_data = await get_user_health_logs(db, user_id, days=30)
        health_logs = [
            {
                "metric_type": log.metric_type,
                "value": log.value,
                "unit": log.unit,
                "created_at": log.created_at.isoformat(),
                "notes": log.notes or ""
            }
            for log in logs_data
        ]
        
        # Convert profile to dictionary
        profile_dict = {
            "id": profile.id,
            "name": profile.name,
            "email": profile.email,
            "age": profile.age,
            "gender": profile.gender,
            "height_cm": profile.height_cm,
            "weight_kg": profile.weight_kg,
            "health_conditions": profile.health_conditions,
            "medications": profile.medications,
            "allergies": profile.allergies,
            "fitness_level": profile.fitness_level,
            "health_goals": profile.health_goals,
        }
        
        # Generate AI analysis
        analysis = get_health_analysis(profile_dict, health_logs)
        
        return {
            "status": "success",
            "summary": analysis,
            "generated_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating vitals summary: {str(e)}")
        return {
            "status": "error",
            "summary": "Unable to generate analysis at this moment. Please try again later.",
            "error": str(e)
        }

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Get chatbot response with optional user profile and health logs context"""
    try:
        response = get_response(
            request.message,
            user_profile=request.user_profile,
            health_logs=request.health_logs,
            chat_history=request.chat_history
        )
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/parse-metrics")
async def parse_metrics_endpoint(request: MetricsParseRequest):
    """Parse health metrics from natural language text"""
    try:
        metrics = HealthMetricParser.parse(request.text)
        return {
            "status": "success",
            "metrics": metrics or []
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# RAG KNOWLEDGE BASE ENDPOINTS
# ============================================

from .rag.ingestion import ingest_all_documents, ingest_file
from .rag.vector_store import get_collection_stats, delete_chunks_by_source
from .rag.config import DOCUMENTS_DIR
from fastapi import UploadFile, File as FastAPIFile
import shutil


@app.post("/rag/ingest")
async def rag_ingest(force: bool = False):
    """
    Ingest all documents in data/documents/ into the vector store.
    Set force=true to re-index files that are already indexed.
    """
    try:
        results = ingest_all_documents(force=force)
        stats = get_collection_stats()
        return {
            "status": "success",
            "files_processed": results,
            "total_chunks": stats["total_chunks"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/rag/upload/{user_id}")
async def rag_upload(user_id: int, file: UploadFile = FastAPIFile(...), force: bool = False):
    """
    Upload a document (PDF/TXT/MD) and immediately ingest it into the vector store.
    """
    allowed = {".pdf", ".txt", ".md"}
    suffix = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if suffix not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{suffix}'. Allowed: {allowed}")

    dest = DOCUMENTS_DIR / file.filename
    try:
        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        count = ingest_file(dest, force=force, user_id=user_id)
        
        # Delete file after ingestion to save space (it is permanently in PostgreSQL)
        if dest.exists():
            dest.unlink()
            
        stats = get_collection_stats()
        return {
            "status": "success",
            "file": file.filename,
            "chunks_indexed": count,
            "total_chunks": stats["total_chunks"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload/ingest failed: {str(e)}")


@app.get("/rag/stats")
async def rag_stats():
    """Return current vector store statistics."""
    try:
        stats = get_collection_stats()
        # List files in documents directory
        docs = [f.name for f in DOCUMENTS_DIR.iterdir() if f.is_file()]
        return {
            "status": "success",
            **stats,
            "document_files": docs,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/rag/delete/{filename}")
async def rag_delete(filename: str):
    """Remove all chunks belonging to a specific document from the vector store."""
    try:
        removed = delete_chunks_by_source(filename)
        return {
            "status": "success",
            "file": filename,
            "chunks_removed": removed,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# RAG DOCUMENT UPLOAD ENDPOINT
# ============================================

@app.post("/rag/upload/{user_id}")
async def upload_user_document(user_id: int, file: UploadFile = File(...)):
    """
    Accept a PDF or TXT file upload from a logged-in user,
    ingest it into the vector store tagged with their user_id,
    so the RAG retriever can return personalised results.
    """
    from .rag.ingestion import ingest_file

    allowed = {".pdf", ".txt"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed:
        raise HTTPException(status_code=400, detail=f"File type '{suffix}' not supported. Use PDF or TXT.")

    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(contents)
            tmp_path = Path(tmp.name)

        chunks_indexed = ingest_file(tmp_path, force=True, user_id=user_id)
        tmp_path.unlink(missing_ok=True)  # clean up temp file

        return {
            "status": "success",
            "file": file.filename,
            "chunks_indexed": chunks_indexed,
            "message": f"✅ '{file.filename}' ingested with {chunks_indexed} chunks for user {user_id}."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
