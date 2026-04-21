"""
Database Models for HealthCare AI
==================================
SQLAlchemy ORM models for users, health logs, medications, and adherence tracking.
"""

# SQLAlchemy column types - Define database columns for ORM models
from .sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Text, Float, ForeignKey, Date, Time
# Database base class - Provides ORM foundation for all models
from .database import Base

class User(Base):
    """
    User model - Stores Google OAuth user data and health profile information.
    Includes authentication tokens, onboarding status, and personal health metrics.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    google_sub = Column(Text, unique=True, nullable=False)
    email = Column(Text)
    name = Column(Text)
    profile_picture_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    is_onboarded = Column(Boolean, default=False)
    
    # Google OAuth tokens (needed for Calendar API)
    google_refresh_token = Column(Text)  # Stored to create calendar events on behalf of user
    
    # Onboarding health profile fields
    age = Column(Integer)
    gender = Column(String)  # "Male", "Female", "Other"
    height_cm = Column(Float)  # Height in centimeters
    weight_kg = Column(Float)  # Weight in kilograms
    health_conditions = Column(Text)  # Comma-separated or JSON
    medications = Column(Text)  # Current medications
    allergies = Column(Text)  # Known allergies
    fitness_level = Column(String)  # "Sedentary", "Light", "Moderate", "Active", "Very Active"
    health_goals = Column(Text)  # Health goals or objectives
    onboarded_at = Column(DateTime(timezone=True))


class HealthLog(Base):
    """
    Health metrics log model - Tracks individual health measurements.
    Records blood pressure, weight, heart rate, sleep, exercise, temperature, etc.
    """
    __tablename__ = "health_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    metric_type = Column(String, nullable=False)  # e.g., "blood_pressure", "weight", "exercise", "sleep", "heart_rate"
    value = Column(String, nullable=False)  # Flexible for different formats (e.g., "120/80", "75.5 kg", "30 min running")
    unit = Column(String)  # e.g., "mmHg", "kg", "min", "bpm"
    notes = Column(Text)  # Optional notes about the log
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String, default="manual")  # "manual" or "chatbot"


class Medication(Base):
    """
    Medication model - Stores prescribed medications and treatment information.
    Tracks medication name, dosage, frequency, and creates Google Calendar reminders.
    """
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)          # e.g., "Metformin"
    dosage = Column(String)                         # e.g., "500mg"
    frequency = Column(String, nullable=False)      # "daily", "twice_daily", "weekly", "as_needed"
    time_of_day = Column(String)                    # e.g., "08:00" or "08:00,20:00" for twice daily
    start_date = Column(Date)                       # When the medication started
    end_date = Column(Date)                         # Optional end date
    notes = Column(Text)                            # e.g., "Take with food"
    gcal_event_id = Column(String)                  # Google Calendar event ID for reminders
    is_active = Column(Boolean, default=True)       # Soft delete
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MedicationLog(Base):
    """
    Medication adherence log model - Tracks whether medications were taken on schedule.
    Records daily medication compliance for adherence monitoring and health analytics.
    """
    __tablename__ = "medication_logs"

    id = Column(Integer, primary_key=True)
    medication_id = Column(Integer, ForeignKey("medications.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    scheduled_date = Column(Date, nullable=False)   # The date this dose was scheduled
    status = Column(String, nullable=False)         # "taken", "skipped", "missed"
    logged_at = Column(DateTime(timezone=True), server_default=func.now())  # When user marked it