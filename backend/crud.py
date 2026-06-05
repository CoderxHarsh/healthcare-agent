"""
CRUD Operations for HealthCare AI
==================================
Database operations for users, health logs, medications, and adherence tracking.
Provides async functions for creating, reading, and updating health data.
"""

# SQLAlchemy async - Async database session management
from sqlalchemy.ext.asyncio import AsyncSession
# SQLAlchemy select - Building SQL SELECT queries
from sqlalchemy.future import select
# SQLAlchemy PostgreSQL - PostgreSQL-specific insert with conflict handling
from sqlalchemy.dialects.postgresql import insert
# ORM models - Database models for users, health logs, medications
from .models import User, HealthLog, Medication, MedicationLog
# SQLAlchemy functions - SQL functions like NOW()
from sqlalchemy.sql import func
# datetime - Date and time operations
from datetime import datetime, timedelta, date, timezone
# typing - Type hints for function parameters and returns
from typing import List, Dict, Optional

async def upsert_user(db: AsyncSession, google_sub: str, email: str, name: str, picture: str, refresh_token: str = None) -> User:
    """
    Upsert user record - Insert new user or update if already exists.
    Stores Google OAuth identity and updates last login timestamp.
    Returns the User object after insert/update.
    """
    values = dict(
        google_sub=google_sub,
        email=email,
        name=name,
        profile_picture_url=picture,
    )
    update_set = {"last_login_at": func.now(), "email": email, "name": name, "profile_picture_url": picture}

    # Only include refresh_token if provided (it's only sent on first consent)
    if refresh_token:
        values["google_refresh_token"] = refresh_token
        update_set["google_refresh_token"] = refresh_token

    stmt = insert(User).values(**values).on_conflict_do_update(
        index_elements=["google_sub"],
        set_=update_set
    )
    #Execute the statement asynchronously
    await db.execute(stmt)
    #Commit the transaction to save it to the database
    await db.commit()

    # Fetch and return the user
    print(f"📝 Looking up user with google_sub: {google_sub}")
    result = await db.execute(select(User).where(User.google_sub == google_sub))
    user = result.scalar_one()
    print(f"✅ Found user: email={user.email}, id={user.id}")
    return user


# ============================================
# HEALTH LOG CRUD OPERATIONS - Track health metrics over time
# ============================================

async def create_health_log(
    db: AsyncSession,
    user_id: int,
    metric_type: str,
    value: str,
    unit: str,
    notes: Optional[str] = None,
    source: str = "manual",
    created_at: Optional[datetime] = None
) -> HealthLog:
    """Create a new health log entry"""
    health_log = HealthLog(
        user_id=user_id,
        metric_type=metric_type,
        value=value,
        unit=unit,
        notes=notes,
        source=source
    )
    if created_at:
        health_log.created_at = created_at
        
    db.add(health_log)
    await db.commit()
    await db.refresh(health_log)
    return health_log


async def get_user_health_logs(
    db: AsyncSession,
    user_id: int,
    metric_type: Optional[str] = None,
    days: int = 30
) -> List[HealthLog]:
    """Get user's health logs, optionally filtered by metric type and date range"""
    query = select(HealthLog).where(
        (HealthLog.user_id == user_id) &
        (HealthLog.created_at >= datetime.now(timezone.utc) - timedelta(days=days))
    )
    
    if metric_type:
        query = query.where(HealthLog.metric_type == metric_type)
    
    query = query.order_by(HealthLog.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def get_latest_health_log(
    db: AsyncSession,
    user_id: int,
    metric_type: str
) -> Optional[HealthLog]:
    """Get the most recent health log for a specific metric type"""
    query = select(HealthLog).where(
        (HealthLog.user_id == user_id) &
        (HealthLog.metric_type == metric_type)
    ).order_by(HealthLog.created_at.desc()).limit(1)
    
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_health_metrics_summary(
    db: AsyncSession,
    user_id: int,
    days: int = 30
) -> Dict:
    """Get a summary of all health metrics for the user"""
    logs = await get_user_health_logs(db, user_id, days=days)
    
    summary = {}
    for log in logs:
        if log.metric_type not in summary:
            summary[log.metric_type] = []
        summary[log.metric_type].append({
            "value": log.value,
            "unit": log.unit,
            "timestamp": log.created_at.isoformat(),
            "notes": log.notes
        })
    
    return summary


async def delete_health_log(db: AsyncSession, log_id: int) -> bool:
    """Delete a health log entry"""
    result = await db.execute(select(HealthLog).where(HealthLog.id == log_id))
    health_log = result.scalar_one_or_none()
    
    if health_log:
        await db.delete(health_log)
        await db.commit()
        return True
    return False


# ============================================
# ONBOARDING CRUD OPERATIONS - Manage user health profiles
# ============================================

async def update_user_onboarding(
    db: AsyncSession,
    user_id: int,
    age: int = None,
    gender: str = None,
    height_cm: float = None,
    weight_kg: float = None,
    health_conditions: str = None,
    medications: str = None,
    allergies: str = None,
    fitness_level: str = None,
    health_goals: str = None
) -> User:
    """Update user's health profile during onboarding"""
    print(f"🔍 Looking for user with ID: {user_id} (type: {type(user_id)})")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        # Debug: try to get all users
        all_users = await db.execute(select(User))
        user_count = len(all_users.scalars().all())
        print(f"❌ User with id {user_id} not found. Total users in DB: {user_count}")
        raise ValueError(f"User with id {user_id} not found")
    
    print(f"✅ Found user: {user.email}")
    
    # Update only provided fields
    if age is not None:
        user.age = age
    if gender is not None:
        user.gender = gender
    if height_cm is not None:
        user.height_cm = height_cm
    if weight_kg is not None:
        user.weight_kg = weight_kg
    if health_conditions is not None:
        user.health_conditions = health_conditions
    if medications is not None:
        user.medications = medications
    if allergies is not None:
        user.allergies = allergies
    if fitness_level is not None:
        user.fitness_level = fitness_level
    if health_goals is not None:
        user.health_goals = health_goals
    
    await db.commit()
    await db.refresh(user)
    print(f"✅ User profile updated for {user.email}")
    return user


async def complete_onboarding(db: AsyncSession, user_id: int) -> User:
    """Mark user as onboarded"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise ValueError(f"User with id {user_id} not found")
    
    user.is_onboarded = True
    user.onboarded_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_profile(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user's complete profile including onboarding info"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


# ============================================
# MEDICATION CRUD OPERATIONS - Manage user medications and adherence
# ============================================

async def create_medication(
    db: AsyncSession,
    user_id: int,
    name: str,
    dosage: str,
    frequency: str,
    time_of_day: str,
    start_date: date = None,
    end_date: date = None,
    notes: str = None,
    gcal_event_id: str = None,
) -> Medication:
    """Create a new medication entry"""
    medication = Medication(
        user_id=user_id,
        name=name,
        dosage=dosage,
        frequency=frequency,
        time_of_day=time_of_day,
        start_date=start_date or date.today(),
        end_date=end_date,
        notes=notes,
        gcal_event_id=gcal_event_id,
    )
    db.add(medication)
    await db.commit()
    await db.refresh(medication)
    return medication


async def get_user_medications(
    db: AsyncSession,
    user_id: int,
    active_only: bool = True,
) -> List[Medication]:
    """Get all medications for a user"""
    query = select(Medication).where(Medication.user_id == user_id)
    if active_only:
        query = query.where(Medication.is_active == True)
    query = query.order_by(Medication.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def get_medication_by_id(
    db: AsyncSession,
    medication_id: int,
) -> Optional[Medication]:
    """Get a single medication by ID"""
    result = await db.execute(select(Medication).where(Medication.id == medication_id))
    return result.scalar_one_or_none()


async def deactivate_medication(
    db: AsyncSession,
    medication_id: int,
) -> Optional[Medication]:
    """Soft-delete a medication (mark as inactive)"""
    result = await db.execute(select(Medication).where(Medication.id == medication_id))
    med = result.scalar_one_or_none()
    if med:
        med.is_active = False
        await db.commit()
        await db.refresh(med)
    return med


async def log_medication_status(
    db: AsyncSession,
    medication_id: int,
    user_id: int,
    scheduled_date: date,
    status: str,  # "taken", "skipped"
) -> MedicationLog:
    """Log whether a medication was taken or skipped"""
    # Check if already logged for this date
    existing = await db.execute(
        select(MedicationLog).where(
            (MedicationLog.medication_id == medication_id) &
            (MedicationLog.scheduled_date == scheduled_date)
        )
    )
    existing_log = existing.scalar_one_or_none()

    if existing_log:
        # Update existing log
        existing_log.status = status
        existing_log.logged_at = datetime.utcnow()
        await db.commit()
        await db.refresh(existing_log)
        return existing_log
    else:
        # Create new log
        med_log = MedicationLog(
            medication_id=medication_id,
            user_id=user_id,
            scheduled_date=scheduled_date,
            status=status,
        )
        db.add(med_log)
        await db.commit()
        await db.refresh(med_log)
        return med_log


async def get_medication_logs(
    db: AsyncSession,
    user_id: int,
    days: int = 30,
    medication_id: int = None,
) -> List[MedicationLog]:
    """Get medication logs for a user"""
    query = select(MedicationLog).where(
        (MedicationLog.user_id == user_id) &
        (MedicationLog.scheduled_date >= date.today() - timedelta(days=days))
    )
    if medication_id:
        query = query.where(MedicationLog.medication_id == medication_id)
    query = query.order_by(MedicationLog.scheduled_date.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def get_adherence_stats(
    db: AsyncSession,
    user_id: int,
    days: int = 30,
) -> Dict:
    """Calculate medication adherence statistics"""
    logs = await get_medication_logs(db, user_id, days=days)
    medications = await get_user_medications(db, user_id)

    total_expected = len(medications) * days  # Simplified: 1 dose per med per day
    taken_count = sum(1 for log in logs if log.status == "taken")
    skipped_count = sum(1 for log in logs if log.status == "skipped")
    logged_count = taken_count + skipped_count

    adherence_rate = round((taken_count / total_expected * 100), 1) if total_expected > 0 else 0

    return {
        "total_medications": len(medications),
        "period_days": days,
        "total_expected_doses": total_expected,
        "taken": taken_count,
        "skipped": skipped_count,
        "not_logged": total_expected - logged_count,
        "adherence_rate": adherence_rate,
    }