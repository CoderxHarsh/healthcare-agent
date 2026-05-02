"""
Streamlit Frontend for HealthCare AI Assistant
===============================================
Interactive web interface for health chatbot with user authentication,
onboarding, health tracking, medication management, and wellness metrics.
"""

import sys
import os

# Add backend folder to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Streamlit - Web app framework for building data dashboards and UIs
import streamlit as st
# requests - HTTP client for communicating with FastAPI backend
import requests
# datetime - Date/time operations for health tracking
from datetime import datetime, timedelta, date
# urllib.parse - URL encoding for OAuth parameters
import urllib.parse
# dotenv - Load environment variables
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import re

# ============================================
# PAGE CONFIG & SETUP
# ============================================
st.set_page_config(
    page_title="HealthCare AI",
    page_icon="\U0001f3e5",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_custom_css():
    st.markdown("""
    <style>
        /* Import Modern Font */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        /* Apply font, but exclude Material Icons */
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }
        
        * {
            font-family: 'Outfit', sans-serif;
        }

        .material-symbols-rounded, [class*="Icon"], [data-testid="stIconMaterial"] {
            font-family: 'Material Symbols Rounded' !important;
        }
        
        /* Hide Default Streamlit Sidebar Navigation */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        /* Modern Gradient Buttons - Primary */
        .stButton button[kind="primary"] {
            background: linear-gradient(135deg, #20A4F3 0%, #3B82F6 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 6px 16px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(32, 164, 243, 0.3) !important;
        }
        .stButton button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(32, 164, 243, 0.5) !important;
        }
        
        /* Modern Buttons - Secondary */
        .stButton button[kind="secondary"] {
            background: rgba(40, 40, 40, 0.6) !important;
            color: #CBD5E1 !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 8px !important;
            padding: 6px 16px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }
        .stButton button[kind="secondary"]:hover {
            background: rgba(60, 60, 60, 0.8) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        /* Input Fields */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox > div[data-baseweb="select"] {
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            background: rgba(15, 15, 15, 0.8) !important;
            color: #F8FAFC !important;
        }
        
        .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
            border-color: #20A4F3 !important;
            box-shadow: 0 0 0 2px rgba(32, 164, 243, 0.2) !important;
        }
        
        /* Chat Messages */
        [data-testid="chat-message-user"] {
            background: linear-gradient(135deg, #20A4F3 0%, #3B82F6 100%) !important;
            border-radius: 20px 20px 0 20px !important;
            padding: 15px !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(32, 164, 243, 0.2) !important;
            margin-bottom: 1rem !important;
        }
        
        [data-testid="chat-message-assistant"] {
            background: rgba(25, 25, 25, 0.8) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 20px 20px 20px 0 !important;
            padding: 15px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
            margin-bottom: 1rem !important;
        }
        
        /* Fix Randomly Colored Streamlit Avatars */
        [data-testid="chat-message-user"] [data-testid="stChatMessageAvatar"] {
            background: rgba(32, 164, 243, 0.2) !important;
            color: #20A4F3 !important;
            border: 1px solid rgba(32, 164, 243, 0.5) !important;
        }
        
        [data-testid="chat-message-assistant"] [data-testid="stChatMessageAvatar"] {
            background: rgba(40, 40, 40, 0.8) !important;
            color: #F8FAFC !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        /* Headers Gradient */
        h1, h2, h3 {
            background: linear-gradient(to right, #20A4F3, #A5B4FC);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700 !important;
        }
        
        /* Glassmorphism for expanders and containers */
        .streamlit-expanderHeader {
            background: rgba(25, 25, 25, 0.8) !important;
            border-radius: 10px !important;
        }
        
        div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
            background: rgba(20, 20, 20, 0.5);
            border-radius: 16px;
            padding: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        /* Dashboard Custom Cards */
        .dashboard-card {
            background: rgba(25, 25, 25, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .metric-title {
            color: #94A3B8;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #F8FAFC;
            line-height: 1.2;
        }
        
        .metric-trend-up {
            color: #10B981;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .metric-trend-down {
            color: #EF4444;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .metric-trend-warn {
            color: #F59E0B;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .metric-empty {
            color: #64748B;
            font-size: 1.5rem;
            font-weight: 500;
        }
        
        .badge-success {
            background: rgba(16, 185, 129, 0.2);
            color: #10B981;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid rgba(16, 185, 129, 0.5);
        }
        
        .badge-warning {
            background: rgba(245, 158, 11, 0.2);
            color: #F59E0B;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid rgba(245, 158, 11, 0.5);
        }
        
        .vitals-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            color: #CBD5E1;
        }
        
        .vitals-row:last-child {
            border-bottom: none;
        }
        
        .vitals-val {
            font-weight: 700;
            color: #F8FAFC;
        }
        
        .dot {
            height: 8px;
            width: 8px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        
        .dot-green { background-color: #10B981; }
        .dot-yellow { background-color: #F59E0B; }
        .dot-red { background-color: #EF4444; }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# Load environment variables
env_path = find_dotenv() or os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

def get_secret(key, default=None):
    """Read from Streamlit Cloud secrets first, then fall back to os.getenv for local dev."""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key, default)

API_BASE_URL = get_secret("API_BASE_URL", "http://localhost:8000")

# Google OAuth config
GOOGLE_CLIENT_ID = get_secret("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = get_secret("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = get_secret("GOOGLE_REDIRECT_URI", "http://localhost:8501")
GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v2/userinfo"


def get_google_login_url():
    """Build the Google OAuth2 authorization URL"""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/calendar",
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{GOOGLE_AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"

# -------------------------
# SESSION SETUP
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user" not in st.session_state:
    st.session_state.user = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "onboarded" not in st.session_state:
    st.session_state.onboarded = None

if "page" not in st.session_state:
    st.session_state.page = "chat"

if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

if "health_logs" not in st.session_state:
    st.session_state.health_logs = None


# -------------------------
# CHECK LOGIN (FROM OAUTH CALLBACK)
# -------------------------
params = st.query_params

# Handle Google OAuth callback — exchange code for token
if "code" in params and not st.session_state.user:
    code = params["code"]
    with st.spinner("🔄 Logging you in..."):
        try:
            # Exchange authorization code for access token
            token_data = {
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            token_response = requests.post(GOOGLE_TOKEN_ENDPOINT, data=token_data, timeout=30)

            if token_response.status_code != 200:
                st.error(f"❌ Google token exchange failed. Please try logging in again.")
            else:
                tokens = token_response.json()
                access_token = tokens.get("access_token")
                refresh_token = tokens.get("refresh_token")

                # Get user info from Google
                headers = {"Authorization": f"Bearer {access_token}"}
                userinfo_response = requests.get(GOOGLE_USERINFO_ENDPOINT, headers=headers, timeout=30)

                if userinfo_response.status_code != 200:
                    st.error("❌ Failed to get user info from Google.")
                else:
                    userinfo = userinfo_response.json()

                    # Save/update user in backend database
                    user_payload = {
                        "google_sub": userinfo.get("id"),
                        "email": userinfo.get("email"),
                        "name": userinfo.get("name"),
                        "picture": userinfo.get("picture"),
                        "refresh_token": refresh_token,
                    }
                    try:
                        save_response = requests.post(
                            f"{API_BASE_URL}/auth/google-login",
                            json=user_payload,
                            timeout=15,
                        )
                        
                        if save_response.status_code == 200:
                            user_data = save_response.json()
                            st.session_state.user = user_data["name"]
                            st.session_state.user_id = user_data["user_id"]
                            st.session_state.onboarded = str(user_data["is_onboarded"]).lower()
                            st.query_params.clear()
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to save user (status {save_response.status_code}). Please try again.")
                    except requests.exceptions.Timeout:
                        st.error("❌ Backend request timed out. The server may be waking up — please try again in a minute.")
                    except requests.exceptions.ConnectionError:
                        st.error(f"❌ Cannot connect to backend at {API_BASE_URL}. Please try again later.")
                    except Exception as e:
                        st.error(f"❌ Backend API error: {str(e)}")
        except Exception as e:
            st.error(f"❌ OAuth error: {str(e)}")

# Legacy support: FastAPI redirect with user params
elif "user" in params:
    st.session_state.user = params["user"]
    st.session_state.onboarded = params.get("onboarded", "false")
    try:
        st.session_state.user_id = int(params.get("user_id", 0))
    except (ValueError, TypeError):
        st.session_state.user_id = None

# Check if page parameter is set
if "page" in params:
    st.session_state.page = params["page"]


# ============================================
# ONBOARDING FUNCTION
# ============================================

def show_onboarding_page():
    """
    Display and handle the user health profile onboarding form.
    Collects age, weight, height, health conditions, medications, allergies,
    fitness level, and health goals. Saves data to backend API.
    """
    st.title("🎯 Complete Your Health Profile")
    st.markdown("---")
    st.markdown("### Help us know you better!")
    st.write("This information helps us provide personalized health advice and recommendations.")
    
    with st.form("onboarding_form"):
        # Basic Health Info
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", value=None, min_value=1, max_value=120)
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
        
        # Physical Measurements
        col1, col2 = st.columns(2)
        with col1:
            height_cm = st.number_input("Height (cm)", value=None, min_value=50, max_value=250)
        with col2:
            weight_kg = st.number_input("Weight (kg)", value=None, min_value=20, max_value=300)
        
        # Health Information
        health_conditions = st.multiselect(
            "Health Conditions (select all that apply)",
            [
                "Diabetes",
                "Hypertension (High Blood Pressure)",
                "Heart Disease",
                "Asthma",
                "Thyroid",
                "Arthritis",
                "Depression/Anxiety",
                "None",
                "Other"
            ]
        )
        
        medications = st.text_area(
            "Current Medications (if any)",
            placeholder="List your medications, e.g., Aspirin, Metformin, etc."
        )
        
        allergies = st.text_area(
            "Allergies (if any)",
            placeholder="List any known allergies, medications or food"
        )
        
        # Fitness & Goals
        col1, col2 = st.columns(2)
        with col1:
            fitness_level = st.selectbox(
                "Current Fitness Level",
                ["Sedentary", "Light", "Moderate", "Active", "Very Active"]
            )
        with col2:
            health_goals = st.multiselect(
                "Health Goals",
                [
                    "Weight Loss",
                    "Weight Gain",
                    "Build Muscle",
                    "Improve Endurance",
                    "Reduce Stress",
                    "Better Sleep",
                    "General Wellness",
                    "Manage Disease"
                ]
            )
        
        submitted = st.form_submit_button("✅ Complete Onboarding", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not age or not gender or not height_cm or not weight_kg or not fitness_level:
                st.error("❌ Please fill in all required fields (Age, Gender, Height, Weight, Fitness Level)")
            elif not st.session_state.user_id:
                st.error("❌ User ID not found. Please log in again.")
            else:
                try:
                    # Format data
                    health_conditions_str = ", ".join(health_conditions) if health_conditions else None
                    health_goals_str = ", ".join(health_goals) if health_goals else None
                    
                    # Save onboarding data
                    payload = {
                        "age": age,
                        "gender": gender,
                        "height_cm": height_cm,
                        "weight_kg": weight_kg,
                        "health_conditions": health_conditions_str,
                        "medications": medications if medications else None,
                        "allergies": allergies if allergies else None,
                        "fitness_level": fitness_level,
                        "health_goals": health_goals_str
                    }
                    
                    # First save the profile
                    response1 = requests.post(
                        f"{API_BASE_URL}/user/{st.session_state.user_id}/onboarding",
                        json=payload,
                        timeout=10
                    )
                    
                    if response1.status_code == 200:
                        # Then mark as onboarded
                        response2 = requests.post(
                            f"{API_BASE_URL}/user/{st.session_state.user_id}/complete-onboarding",
                            timeout=10
                        )
                        
                        if response2.status_code == 200:
                            st.session_state.onboarded = "true"
                            st.session_state.page = "chat"
                            st.query_params.clear()
                            st.success("✅ Onboarding completed successfully!")
                            st.balloons()
                            import time
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"❌ Error completing onboarding: {response2.json()}")
                    else:
                        st.error(f"❌ Error saving profile: {response1.json()}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# -------------------------
# ROUTING BASED ON LOGIN STATE & PAGE
# -------------------------
if st.session_state.user:
    # Check if onboarding page is requested or if user is not onboarded
    if st.session_state.page == "onboarding" or st.session_state.onboarded == "false":
        show_onboarding_page()
    else:
        # ✅ USER IS LOGGED IN AND ONBOARDED - Show main app
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title("🏥 HealthCare AI Assistant")
        with col2:
            st.write("")
            st.write("")
            st.link_button(
                "📥 PDF Report",
                f"{API_BASE_URL}/export/health-report/{st.session_state.user_id}",
                use_container_width=True
            )

        # ✅ SIDEBAR NAVIGATION
        with st.sidebar:
            st.markdown("### 🏥 HealthAgent\n<span style='color:#94A3B8;'>AI Health Monitor</span>", unsafe_allow_html=True)
            st.divider()
            
            if "nav_page" not in st.session_state:
                st.session_state.nav_page = "Chat"
                
            if st.button("Chat", type="primary" if st.session_state.nav_page == "Chat" else "secondary", use_container_width=True):
                st.session_state.nav_page = "Chat"
                st.rerun()
                
            if st.button("Dashboard", type="primary" if st.session_state.nav_page == "Dashboard" else "secondary", use_container_width=True):
                st.session_state.nav_page = "Dashboard"
                st.session_state.health_logs = None
                st.session_state.user_profile = None
                st.rerun()
                
            if st.button("Goals", type="primary" if st.session_state.nav_page == "Goals" else "secondary", use_container_width=True):
                st.session_state.nav_page = "Goals"
                st.session_state.health_logs = None
                st.session_state.user_profile = None
                st.rerun()

            if st.button("Wellness", type="primary" if st.session_state.nav_page == "Wellness" else "secondary", use_container_width=True):
                st.session_state.nav_page = "Wellness"
                st.session_state.health_logs = None
                st.session_state.user_profile = None
                st.rerun()

            if st.button("Medications", type="primary" if st.session_state.nav_page == "Medications" else "secondary", use_container_width=True):
                st.session_state.nav_page = "Medications"
                st.rerun()
                
            page = st.session_state.nav_page
            
            st.write("")
            st.write("")
            st.caption(f"Signed in as\n\n**{st.session_state.user}**")
            
            if st.button("Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.user_id = None
                st.session_state.user_profile = None
                st.session_state.health_logs = None
                st.session_state.messages = []
                st.query_params.clear()
                import time
                time.sleep(0.5)
                st.rerun()
            
            # Pushing footer links to the bottom
            st.write("\n" * 5)
            st.divider()
            st.page_link("pages/1_Terms_of_Service.py", label="Terms of Service", icon="📜")
            st.page_link("pages/2_Privacy_Policy.py", label="Privacy Policy", icon="🔒")
            
        if page == "Dashboard":
            col_title, col_badge = st.columns([3, 1])
            with col_title:
                st.markdown("<h2 style='margin-bottom:0;'>Dashboard</h2>", unsafe_allow_html=True)
                st.markdown("<p style='color:#94A3B8; margin-top:0;'>Overview of your vitals</p>", unsafe_allow_html=True)
            with col_badge:
                st.markdown("<div style='text-align:right; margin-top:15px;'><span class='badge-success'>ALL SYSTEMS NORMAL</span></div>", unsafe_allow_html=True)
            
            st.write("")
            
            # Fetch logs if not loaded
            if "health_logs" not in st.session_state or st.session_state.health_logs is None:
                try:
                    logs_response = requests.get(f"{API_BASE_URL}/health-logs/{st.session_state.user_id}", params={"days": 30}, timeout=5)
                    st.session_state.health_logs = logs_response.json().get("logs", []) if logs_response.status_code == 200 else []
                except:
                    st.session_state.health_logs = []
            
            def get_latest(metric_type):
                if not st.session_state.health_logs: return None
                logs = [l for l in st.session_state.health_logs if l.get('metric_type') == metric_type]
                return logs[0] if logs else None
                
            hr_log = get_latest('heart_rate')
            bp_log = get_latest('blood_pressure')
            sleep_log = get_latest('sleep')
            weight_log = get_latest('weight')
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'''
                <div class="dashboard-card">
                    <div class="metric-title">HEART RATE</div>
                    {f'<div class="metric-value">{hr_log["value"]}</div><div class="metric-trend-up">↑ +2 bpm</div>' if hr_log else '<div class="metric-empty">--</div>'}
                </div>
                ''', unsafe_allow_html=True)
            with c2:
                st.markdown(f'''
                <div class="dashboard-card">
                    <div class="metric-title">BLOOD PRESSURE</div>
                    {f'<div class="metric-value">{bp_log["value"]}</div><div class="metric-trend-warn">⚠ elevated</div>' if bp_log else '<div class="metric-empty">--</div>'}
                </div>
                ''', unsafe_allow_html=True)
            with c3:
                st.markdown(f'''
                <div class="dashboard-card">
                    <div class="metric-title">SLEEP</div>
                    {f'<div class="metric-value">{sleep_log["value"]}h</div><div class="metric-trend-up">↑ +0.5h</div>' if sleep_log else '<div class="metric-empty">--</div>'}
                </div>
                ''', unsafe_allow_html=True)
            with c4:
                st.markdown(f'''
                <div class="dashboard-card">
                    <div class="metric-title">WEIGHT</div>
                    {f'<div class="metric-value">{weight_log["value"]}</div><div class="metric-trend-down">↓ -0.2kg</div>' if weight_log else '<div class="metric-empty">--</div>'}
                </div>
                ''', unsafe_allow_html=True)
                
            c_summary, c_ai = st.columns(2)
            with c_summary:
                st.markdown(f'''
                <div class="dashboard-card" style="height: 100%;">
                    <div class="metric-title" style="margin-bottom:15px;">VITALS SUMMARY</div>
                    <div class="vitals-row">
                        <span>Heart Rate</span>
                        <span class="vitals-val"><span class="dot dot-green"></span>{hr_log["value"] if hr_log else "--"} bpm</span>
                    </div>
                    <div class="vitals-row">
                        <span>Blood Pressure</span>
                        <span class="vitals-val"><span class="dot {"dot-yellow" if bp_log else "dot-green"}"></span>{bp_log["value"] if bp_log else "--"}</span>
                    </div>
                    <div class="vitals-row">
                        <span>Sleep</span>
                        <span class="vitals-val"><span class="dot dot-green"></span>{sleep_log["value"] if sleep_log else "--"} h</span>
                    </div>
                    <div class="vitals-row">
                        <span>Weight</span>
                        <span class="vitals-val"><span class="dot dot-green"></span>{weight_log["value"] if weight_log else "--"} kg</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
            with c_ai:
                ai_text = "Gathering health insights..."
                error_occurred = False
                
                try:
                    with st.spinner("🔍 Analyzing your health data..."):
                        res = requests.get(f"{API_BASE_URL}/user/{st.session_state.user_id}/vitals-summary", timeout=15)
                        if res.status_code == 200:
                            response_data = res.json()
                            ai_text = response_data.get("summary", "Analysis unavailable.")
                        else:
                            ai_text = "Could not retrieve analysis. Please check your health data."
                            error_occurred = True
                except requests.exceptions.Timeout:
                    ai_text = "Analysis is loading... (timeout). Try refreshing the page."
                    error_occurred = True
                except Exception as e:
                    ai_text = "Unable to generate analysis. Please make sure you've logged some health data."
                    error_occurred = False
                        
                # Display the AI analysis with styling
                badge_color = "rgba(239, 68, 68, 0.2)" if error_occurred else "rgba(34, 197, 94, 0.2)"
                badge_text = "⚠️ CHECK NEEDED" if error_occurred else "✅ GENERATED"
                badge_border = "rgba(239, 68, 68, 0.5)" if error_occurred else "rgba(34, 197, 94, 0.5)"
                
                st.markdown(f'''
                <div class="dashboard-card" style="height: 100%;">
                    <div class="metric-title" style="margin-bottom:15px;">🤖 AI ANALYSIS</div>
                    <p style="color:#CBD5E1; font-size:0.95rem; line-height:1.6;">
                        {ai_text}
                    </p>
                    <div style="margin-top:20px;">
                        <span class="badge-warning" style="margin-right:10px; background:{badge_color}; border-color:{badge_border};">{badge_text}</span>
                        <span class="badge-success" style="background:rgba(59,130,246,0.2); color:#3B82F6; border-color:rgba(59,130,246,0.5);">ML POWERED</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

        elif page == "Goals":
            # ── HEALTH GOALS SECTION ─────────────────────────────────
            st.title("🎯 Health Goals")
            st.markdown("<p style='color:#94A3B8; margin-top:0; margin-bottom:16px;'>Track and update your personal health objectives</p>", unsafe_allow_html=True)
            st.divider()

            # Load profile if not already loaded
            if "user_profile" not in st.session_state or st.session_state.user_profile is None:
                try:
                    pr = requests.get(f"{API_BASE_URL}/user/{st.session_state.user_id}/profile", timeout=5)
                    st.session_state.user_profile = pr.json().get("profile", {}) if pr.status_code == 200 else {}
                except Exception:
                    st.session_state.user_profile = {}

            profile = st.session_state.user_profile or {}

            # ── Current goals display ──
            current_goals_text = profile.get("health_goals", "") or ""
            current_weight = profile.get("weight_kg")
            current_fitness = profile.get("fitness_level", "moderate")

            # Parse goals into a list (comma or newline separated)
            goals_list = [g.strip() for g in current_goals_text.replace("\n", ",").split(",") if g.strip()]

            goal_col, edit_col = st.columns([2, 1])

            with goal_col:
                if goals_list:
                    st.markdown("""
                    <div class="dashboard-card" style="padding:16px 20px;">
                        <div class="metric-title" style="margin-bottom:12px;">ACTIVE GOALS</div>
                    """, unsafe_allow_html=True)
                    for i, goal in enumerate(goals_list):
                        # Determine icon based on keywords
                        icon = "🎯"
                        gl = goal.lower()
                        if any(w in gl for w in ["weight", "kg", "lose", "gain"]): icon = "⚖️"
                        elif any(w in gl for w in ["run", "walk", "exercise", "gym", "fitness", "cardio"]): icon = "🏃"
                        elif any(w in gl for w in ["sleep", "rest"]): icon = "😴"
                        elif any(w in gl for w in ["diet", "eat", "nutrition", "calorie"]): icon = "🥗"
                        elif any(w in gl for w in ["stress", "meditat", "mental", "anxiety"]): icon = "🧘"
                        elif any(w in gl for w in ["water", "hydrat"]): icon = "💧"
                        st.markdown(f"""
                        <div style="display:flex; align-items:center; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                            <span style="font-size:1.2rem; margin-right:10px;">{icon}</span>
                            <span style="color:#CBD5E1; font-size:0.95rem;">{goal}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="dashboard-card" style="padding:20px; text-align:center;">
                        <div style="font-size:2rem; margin-bottom:8px;">🎯</div>
                        <div style="color:#64748B;">No health goals set yet. Add your first goal →</div>
                    </div>
                    """, unsafe_allow_html=True)

            with edit_col:
                with st.expander("✏️ Edit Goals", expanded=not bool(goals_list)):
                    with st.form("goals_form"):
                        new_goals = st.text_area(
                            "Your Goals",
                            value=current_goals_text,
                            placeholder="e.g. Lose 5kg, Run 5km, Sleep 8 hours daily",
                            help="Separate multiple goals with commas",
                            height=100
                        )
                        new_weight = st.number_input(
                            "Target Weight (kg)",
                            min_value=30.0, max_value=300.0,
                            value=float(current_weight) if current_weight else 70.0,
                            step=0.5
                        )
                        new_fitness = st.selectbox(
                            "Fitness Level",
                            ["sedentary", "light", "moderate", "active", "very active"],
                            index=["sedentary", "light", "moderate", "active", "very active"].index(
                                current_fitness.lower() if current_fitness and current_fitness.lower() in ["sedentary", "light", "moderate", "active", "very active"] else "moderate"
                            )
                        )
                        save_goals = st.form_submit_button("💾 Save Goals", use_container_width=True)

                        if save_goals:
                            try:
                                res = requests.patch(
                                    f"{API_BASE_URL}/user/{st.session_state.user_id}/goals",
                                    json={
                                        "health_goals": new_goals,
                                        "weight_kg": new_weight,
                                        "fitness_level": new_fitness
                                    },
                                    timeout=10
                                )
                                if res.status_code == 200:
                                    st.success("✅ Goals saved!")
                                    st.session_state.user_profile = None  # refresh cache
                                    st.rerun()
                                else:
                                    st.error(f"❌ {res.json().get('detail', 'Error saving goals')}")
                            except Exception as e:
                                st.error(f"❌ Connection error: {e}")

            st.divider()
            st.markdown("<h3 style='margin-bottom:4px;'>📈 Progress Trends</h3>", unsafe_allow_html=True)
            
            # Fetch health logs for the charts
            if "health_logs" not in st.session_state or st.session_state.health_logs is None:
                with st.spinner("📊 Loading health logs..."):
                    try:
                        logs_response = requests.get(
                            f"{API_BASE_URL}/health-logs/{st.session_state.user_id}",
                            params={"days": 90},
                            timeout=5
                        )
                        if logs_response.status_code == 200:
                            st.session_state.health_logs = logs_response.json().get("logs", [])
                        else:
                            st.error(f"❌ Failed to load health logs: {logs_response.status_code}")
                            st.session_state.health_logs = []
                    except Exception as e:
                        st.error(f"❌ Error loading health logs: {str(e)}")
                        st.session_state.health_logs = []
            
            logs = st.session_state.health_logs
            if not logs:
                st.info("📝 No health logs available yet. Chat with the assistant to start tracking your vitals!\n\nExamples:\n- 'I weigh 75kg today'\n- 'I slept 7 hours'\n- 'My blood pressure is 120/80'")
            else:
                # Helper function to extract numeric values
                def extract_number(val_str):
                    match = re.search(r'[-+]?\d*\.\d+|\d+', str(val_str))
                    return float(match.group()) if match else None

                # Process data for Weight
                weight_data = []
                for log in logs:
                    if log["metric_type"] == "weight":
                        num = extract_number(log["value"])
                        if num is not None:
                            # Use just the date part for grouping
                            weight_data.append({"Date": log["created_at"].split("T")[0], "Weight (kg)": num})
                
                # Process data for Sleep
                sleep_data = []
                for log in logs:
                    if log["metric_type"] == "sleep":
                        num = extract_number(log["value"])
                        if num is not None:
                            sleep_data.append({"Date": log["created_at"].split("T")[0], "Sleep (hours)": num})

                # Process data for Blood Pressure
                bp_data = []
                for log in logs:
                    if log["metric_type"] == "blood_pressure":
                        try:
                            # Usually formatted like "120/80"
                            parts = log["value"].split("/")
                            if len(parts) == 2:
                                sys_num = extract_number(parts[0])
                                dia_num = extract_number(parts[1])
                                if sys_num and dia_num:
                                    bp_data.append({
                                        "Date": log["created_at"].split("T")[0],
                                        "Systolic (High)": sys_num,
                                        "Diastolic (Low)": dia_num
                                    })
                        except Exception:
                            pass

                w_col, s_col = st.columns(2)
                
                with w_col:
                    st.markdown("<div class='metric-title' style='margin-bottom:10px;'>Weight Trend</div>", unsafe_allow_html=True)
                    if weight_data:
                        df_weight = pd.DataFrame(weight_data)
                        df_weight = df_weight.groupby("Date").mean().reset_index()
                        df_weight.set_index("Date", inplace=True)
                        st.line_chart(df_weight, height=250)
                    else:
                        st.caption("No weight data logged recently. Tell the chatbot 'I weigh 70kg today' to see your chart!")

                with s_col:
                    st.markdown("<div class='metric-title' style='margin-bottom:10px;'>Sleep Consistency</div>", unsafe_allow_html=True)
                    if sleep_data:
                        df_sleep = pd.DataFrame(sleep_data)
                        df_sleep = df_sleep.groupby("Date").mean().reset_index()
                        df_sleep.set_index("Date", inplace=True)
                        st.bar_chart(df_sleep, height=250)
                    else:
                        st.caption("No sleep data logged recently. Tell the chatbot 'I slept 7 hours' to track your rest!")

                # Blood pressure full width chart
                st.write("")
                st.markdown("<div class='metric-title' style='margin-bottom:10px;'>Blood Pressure Trend (mmHg)</div>", unsafe_allow_html=True)
                if bp_data:
                    df_bp = pd.DataFrame(bp_data)
                    df_bp = df_bp.groupby("Date").mean().reset_index()
                    df_bp.set_index("Date", inplace=True)
                    # Streamlit line chart automatically plots multiple columns.
                    # Setting specific colors: Red for Systolic, Blue for Diastolic
                    st.line_chart(df_bp, height=250, color=["#EF4444", "#3B82F6"])
                else:
                    st.caption("No blood pressure data logged recently. Tell the chatbot 'My BP is 120/80' to track it!")

        elif page == "Medications":
            st.title("💊 Medication Manager")
            st.markdown("<p style='color:#94A3B8; margin-top:0; margin-bottom:16px;'>Track your prescriptions, log doses, and set Google Calendar reminders</p>", unsafe_allow_html=True)
            st.divider()

            med_tab1, med_tab2, med_tab3 = st.tabs(["📊 My Medications", "➕ Add Medication", "📊 Adherence Report"])

            # ── TAB 1: MY MEDICATIONS ──────────────────────────────────────────
            with med_tab1:
                st.subheader("📊 Active Medications")
                try:
                    meds_resp = requests.get(
                        f"{API_BASE_URL}/medications/{st.session_state.user_id}",
                        params={"active_only": True},
                        timeout=5
                    )
                    meds = meds_resp.json().get("medications", []) if meds_resp.status_code == 200 else []
                except Exception:
                    meds = []
                    st.error("❌ Could not connect to the backend.")

                if not meds:
                    st.info("💤 No medications added yet. Add your first medication in the \"Add Medication\" tab.")
                else:
                    # Deduplicate medications by ID just in case the backend returns duplicates
                    unique_meds = []
                    seen_ids = set()
                    for m in meds:
                        if m['id'] not in seen_ids:
                            unique_meds.append(m)
                            seen_ids.add(m['id'])
                    
                    for med in unique_meds:
                        with st.container():
                            gcal_badge = "📅 Calendar Reminder Set" if med["has_calendar_event"] else "⚠️ No Calendar Reminder"
                            freq_display = med["frequency"].replace("_", " ").title()
                            st.markdown(f"""
                            <div class="dashboard-card" style="padding:14px 18px; margin-bottom:10px;">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <div>
                                        <span style="font-size:1.1rem; font-weight:600; color:#F1F5F9;">💊 {med['name']}</span>
                                        <span style="margin-left:10px; color:#94A3B8; font-size:0.85rem;">{med.get('dosage','')}</span>
                                    </div>
                                    <span style="color:#64748B; font-size:0.8rem;">{gcal_badge}</span>
                                </div>
                                <div style="color:#94A3B8; font-size:0.85rem; margin-top:6px;">
                                    🔁 {freq_display} &nbsp;&nbsp; ⏰ {med.get('time_of_day','N/A')} &nbsp;&nbsp; 📆 From {med.get('start_date','')}
                                </div>
                                {f"<div style='color:#64748B; font-size:0.8rem; margin-top:4px;'>📝 {med['notes']}</div>" if med.get('notes') else ""}
                            </div>
                            """, unsafe_allow_html=True)

                            log_col1, log_col2, del_col = st.columns([1, 1, 1])
                            today_str = date.today().isoformat()
                            with log_col1:
                                if st.button(f"✅ Taken", key=f"btn_taken_{med['id']}", use_container_width=True):
                                    try:
                                        r = requests.post(
                                            f"{API_BASE_URL}/medications/{med['id']}/log",
                                            json={"scheduled_date": today_str, "status": "taken"},
                                            timeout=5
                                        )
                                        if r.status_code == 200:
                                            st.success(f"✅ {med['name']} marked as taken!")
                                            st.rerun()
                                        else:
                                            st.error("❌ Could not log. Try again.")
                                    except Exception as e:
                                        st.error(f"❌ {e}")
                            with log_col2:
                                if st.button(f"❌ Skipped", key=f"btn_skip_{med['id']}", use_container_width=True):
                                    try:
                                        r = requests.post(
                                            f"{API_BASE_URL}/medications/{med['id']}/log",
                                            json={"scheduled_date": today_str, "status": "skipped"},
                                            timeout=5
                                        )
                                        if r.status_code == 200:
                                            st.warning(f"⚠️ {med['name']} marked as skipped.")
                                            st.rerun()
                                        else:
                                            st.error("❌ Could not log. Try again.")
                                    except Exception as e:
                                        st.error(f"❌ {e}")
                            with del_col:
                                if st.button(f"🗑️ Remove", key=f"btn_del_{med['id']}", use_container_width=True):
                                    try:
                                        r = requests.delete(
                                            f"{API_BASE_URL}/medications/{med['id']}",
                                            timeout=5
                                        )
                                        if r.status_code == 200:
                                            st.success(f"✅ {med['name']} removed.")
                                            st.rerun()
                                        else:
                                            st.error("❌ Could not remove medication.")
                                    except Exception as e:
                                        st.error(f"❌ {e}")

            # ── TAB 2: ADD MEDICATION ──────────────────────────────────────────
            with med_tab2:
                st.subheader("➕ Add New Medication")
                st.caption("📅 A recurring Google Calendar reminder will automatically be created for this medication.")
                st.write("")
                with st.form("add_med_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        med_name = st.text_input("Medication Name *", placeholder="e.g. Metformin")
                        med_dosage = st.text_input("Dosage", placeholder="e.g. 500mg")
                        med_frequency = st.selectbox(
                            "Frequency *",
                            ["daily", "twice_daily", "weekly", "as_needed"],
                            format_func=lambda x: x.replace("_", " ").title()
                        )
                    with col2:
                        med_time = st.text_input("Time of Day", value="08:00", help="Format: HH:MM (24hr). For twice daily, use e.g. 08:00,20:00")
                        med_start = st.date_input("Start Date", value=date.today())
                        med_end = st.date_input("End Date (optional)", value=None)
                    med_notes = st.text_area("Notes", placeholder="e.g. Take with food", height=80)
                    submitted = st.form_submit_button("💾 Add Medication & Create Reminder", use_container_width=True)

                    if submitted:
                        if not med_name.strip():
                            st.error("❌ Medication name is required.")
                        else:
                            try:
                                payload = {
                                    "name": med_name.strip(),
                                    "dosage": med_dosage.strip() or None,
                                    "frequency": med_frequency,
                                    "time_of_day": med_time.strip(),
                                    "start_date": med_start.isoformat(),
                                    "end_date": med_end.isoformat() if med_end else None,
                                    "notes": med_notes.strip() or None,
                                }
                                r = requests.post(
                                    f"{API_BASE_URL}/medications/{st.session_state.user_id}",
                                    json=payload,
                                    timeout=15
                                )
                                if r.status_code == 200:
                                    data = r.json()
                                    st.success(f"✅ {med_name} added successfully!")
                                    if data.get("calendar_event") == "created":
                                        st.info("📅 Google Calendar reminder created! Check your calendar.")
                                    else:
                                        st.warning("⚠️ Calendar reminder could not be created (login may need refresh).")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {r.json().get('detail', 'Error adding medication')}")
                            except Exception as e:
                                st.error(f"❌ Connection error: {e}")

            # ── TAB 3: ADHERENCE REPORT ────────────────────────────────────────
            with med_tab3:
                st.subheader("📊 Medication Adherence Report")
                days_filter = st.slider("Report Period (days)", 7, 90, 30)
                try:
                    adh_resp = requests.get(
                        f"{API_BASE_URL}/medications/{st.session_state.user_id}/adherence",
                        params={"days": days_filter},
                        timeout=5
                    )
                    if adh_resp.status_code == 200:
                        adh = adh_resp.json()
                        overall = adh.get("overall_adherence_rate", 0)
                        per_med = adh.get("per_medication", [])

                        # Overall metric
                        st.metric(
                            label=f"Overall Adherence (Last {days_filter} days)",
                            value=f"{overall:.0f}%",
                            delta="👍 Great!" if overall >= 80 else "⚠️ Needs Improvement"
                        )
                        st.progress(overall / 100)
                        st.write("")

                        if per_med:
                            st.markdown("<div class='metric-title' style='margin-bottom:12px;'>PER MEDICATION BREAKDOWN</div>", unsafe_allow_html=True)
                            for med_stat in per_med:
                                rate = med_stat.get("adherence_rate", 0)
                                color = "#22C55E" if rate >= 80 else ("#F59E0B" if rate >= 50 else "#EF4444")
                                st.markdown(f"""
                                <div class="dashboard-card" style="padding:12px 16px; margin-bottom:8px;">
                                    <div style="display:flex; justify-content:space-between; align-items:center;">
                                        <span style="color:#F1F5F9; font-weight:600;">💊 {med_stat.get('medication_name', 'Unknown')}</span>
                                        <span style="color:{color}; font-weight:700; font-size:1.1rem;">{rate:.0f}%</span>
                                    </div>
                                    <div style="color:#64748B; font-size:0.8rem; margin-top:4px;">
                                        ✅ Taken: {med_stat.get('taken', 0)} &nbsp; ❌ Skipped: {med_stat.get('skipped', 0)} &nbsp; 🟡 Missed: {med_stat.get('missed', 0)}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No adherence data yet. Use the \"My Medications\" tab to log doses.")
                    else:
                        st.error("❌ Could not load adherence report.")
                except Exception as e:
                    st.error(f"❌ Connection error: {e}")

        elif page == "Chat":
            st.divider()

            # Load profile from API if not already loaded
            if "user_profile" not in st.session_state or st.session_state.user_profile is None:
                try:
                    pr = requests.get(f"{API_BASE_URL}/user/{st.session_state.user_id}/profile", timeout=5)
                    st.session_state.user_profile = pr.json().get("profile", {}) if pr.status_code == 200 else {}
                except Exception:
                    st.session_state.user_profile = {}

            # Load health logs from API if not already loaded
            if "health_logs" not in st.session_state or st.session_state.health_logs is None:
                try:
                    logs_response = requests.get(
                        f"{API_BASE_URL}/health-logs/{st.session_state.user_id}",
                        params={"days": 90},
                        timeout=5
                    )
                    st.session_state.health_logs = logs_response.json().get("logs", []) if logs_response.status_code == 200 else []
                except Exception:
                    st.session_state.health_logs = []

            # Display chat messages
            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])

            # --- File Upload (Login only, above chat input) ---
            uploaded_file = st.file_uploader(
                "📄 Upload Health Document (PDF/TXT) to personalize AI answers",
                type=["pdf", "txt"],
                key="login_doc_upload",
                label_visibility="visible"
            )

            # Handle File Upload
            if uploaded_file is not None:
                current_name = uploaded_file.name
                if st.session_state.get("last_uploaded") != current_name:
                    with st.spinner("📚 Processing document..."):
                        files = {"file": (current_name, uploaded_file.getvalue(), uploaded_file.type)}
                        try:
                            upload_res = requests.post(f"{API_BASE_URL}/rag/upload/{st.session_state.user_id}", files=files, timeout=30)
                            if upload_res.status_code == 200:
                                st.success(f"✅ '{current_name}' added to your knowledge base!")
                                st.session_state.last_uploaded = current_name
                            else:
                                st.error("❌ Upload failed.")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

            # --- Native Chat Input (identical to guest mode) ---
            user_input = st.chat_input("Ask me about your health...")

            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.rerun()

            # Generate AI response
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                last_msg = st.session_state.messages[-1]["content"]

                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown("Thinking...")

                    try:
                        response_data = requests.post(
                            f"{API_BASE_URL}/chat",
                            json={
                                "message": last_msg,
                                "user_profile": st.session_state.user_profile,
                                "health_logs": st.session_state.health_logs,
                                "chat_history": st.session_state.messages[:-1]
                            },
                            timeout=30
                        )
                        response = response_data.json().get("response", "Sorry, I couldn't generate a response.")
                    except Exception as e:
                        response = f"Error communicating with chatbot: {str(e)}"

                    try:
                        metrics_res = requests.post(f"{API_BASE_URL}/parse-metrics", json={"text": last_msg}, timeout=10)
                        metrics = metrics_res.json().get("metrics", [])
                    except Exception:
                        metrics = []

                    if metrics and st.session_state.user_id:
                        try:
                            for metric in metrics:
                                requests.post(
                                    f"{API_BASE_URL}/health-logs/{st.session_state.user_id}",
                                    json={"metric_type": metric["metric_type"], "value": metric["value"], "unit": metric["unit"], "source": "chatbot"},
                                    timeout=5
                                )
                            response += f"\n\n📊 **Metrics saved:** {', '.join([m['metric_type'] for m in metrics])}"
                            st.session_state.health_logs = None
                        except Exception:
                            pass

                    message_placeholder.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()


        elif page == "Wellness":
            st.header("📊 Your Wellness Tracker")

            # Tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📈 View Logs", "➕ Add Metric", "📋 Summary", "📥 Bulk Import"])
            
            with tab1:
                st.subheader("Health Metrics History")
                
                # Filter options
                col1, col2 = st.columns(2)
                with col1:
                    metric_types = [
                        "All Metrics",
                        "Blood Pressure",
                        "Weight",
                        "Heart Rate",
                        "Blood Sugar",
                        "Sleep",
                        "Exercise"
                    ]
                    selected_metric = st.selectbox("Filter by Metric", metric_types)
                
                with col2:
                    days = st.slider("Show last N days", 1, 90, 30)
                
                # Fetch logs
                metric_param = None
                if selected_metric != "All Metrics":
                    metric_param = selected_metric.lower().replace(" ", "_")
                
                try:
                    response = requests.get(
                        f"{API_BASE_URL}/health-logs/{st.session_state.user_id}",
                        params={"metric_type": metric_param, "days": days},
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        logs = data.get("logs", [])
                        
                        if logs:
                            logs_df = []
                            for log in logs:
                                logs_df.append({
                                    "Date": datetime.fromisoformat(log["created_at"]).strftime("%Y-%m-%d %H:%M"),
                                    "Metric": log["metric_type"].replace("_", " ").title(),
                                    "Value": f"{log['value']} {log['unit']}",
                                    "Notes": log.get("notes", "—")
                                })
                            st.dataframe(logs_df, use_container_width=True)
                        else:
                            st.info("📭 No metrics logged yet. Add one below!")
                    else:
                        st.error(f"Error fetching logs: {response.text}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            
            with tab2:
                st.subheader("Add Health Metric")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    metric_type = st.selectbox(
                        "Metric Type",
                        [
                            "blood_pressure",
                            "weight",
                            "heart_rate",
                            "blood_sugar",
                            "sleep",
                            "exercise",
                            "temperature"
                        ]
                    )
                
                with col2:
                    value = st.text_input("Value (e.g., 120/80, 75.5, 8)")
                
                unit_map = {
                    "blood_pressure": "mmHg",
                    "weight": "kg",
                    "heart_rate": "bpm",
                    "blood_sugar": "mg/dL",
                    "sleep": "hours",
                    "exercise": "minutes",
                    "temperature": "°C"
                }
                
                unit = unit_map.get(metric_type, "")
                
                notes = st.text_area("Notes (optional)", height=70)
                
                if st.button("💾 Save Metric", use_container_width=True):
                    if not value:
                        st.error("❌ Please enter a value")
                    else:
                        try:
                            response = requests.post(
                                f"{API_BASE_URL}/health-logs/{st.session_state.user_id}",
                                json={
                                    "metric_type": metric_type,
                                    "value": value,
                                    "unit": unit,
                                    "notes": notes if notes else None,
                                    "source": "manual"
                                },
                                timeout=5
                            )
                            
                            if response.status_code == 200:
                                st.success("✅ Metric saved successfully!")
                                st.balloons()
                            else:
                                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            
            with tab3:
                st.subheader("Health Summary")
                
                days = st.slider("Summary period (days)", 1, 90, 30)
                
                try:
                    response = requests.get(
                        f"{API_BASE_URL}/health-logs/{st.session_state.user_id}/summary",
                        params={"days": days},
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        summary = data.get("summary", {})
                        
                        if summary:
                            for metric_type, entries in summary.items():
                                with st.expander(f"📊 {metric_type.replace('_', ' ').title()} ({len(entries)} entries)"):
                                    for entry in entries[:5]:  # Show last 5
                                        col1, col2, col3 = st.columns([2, 1, 2])
                                        with col1:
                                            st.caption(datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M"))
                                        with col2:
                                            st.caption(f"**{entry['value']}** {entry['unit']}")
                                        with col3:
                                            if entry.get("notes"):
                                                st.caption(f"_{entry['notes']}_")
                        else:
                            st.info("📭 No metrics logged yet in this period.")
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

            with tab4:
                st.subheader("📥 Bulk Import Health Logs")
                st.markdown("Upload a CSV, JSON, or XML file containing your historical health logs.")
                st.info("Expected columns/keys: `metric_type`, `value`, `unit` (optional), `date` (optional).")
                
                uploaded_bulk = st.file_uploader(
                    "Upload file",
                    type=["csv", "json", "xml"],
                    key="bulk_import_upload"
                )
                
                if uploaded_bulk is not None:
                    if st.button("🚀 Process Import", use_container_width=True):
                        with st.spinner("Processing file..."):
                            files = {"file": (uploaded_bulk.name, uploaded_bulk.getvalue(), uploaded_bulk.type)}
                            try:
                                res = requests.post(
                                    f"{API_BASE_URL}/health-logs/{st.session_state.user_id}/upload",
                                    files=files,
                                    timeout=30
                                )
                                if res.status_code == 200:
                                    data = res.json()
                                    if data.get("skipped", 0) > 0:
                                        st.warning(data.get("message"))
                                    else:
                                        st.success(data.get("message"))
                                        st.balloons()
                                    # Clear cached logs to force refresh on dashboard
                                    st.session_state.health_logs = None
                                else:
                                    st.error(f"❌ Error: {res.json().get('detail', 'Unknown error')}")
                            except Exception as e:
                                st.error(f"❌ Connection Error: {e}")


else:
    # ❌ USER NOT LOGGED IN
    
    # ✅ GUEST SIDEBAR
    with st.sidebar:
        st.markdown("### 🏥 HealthAgent\n<span style='color:#94A3B8;'>AI Health Monitor</span>", unsafe_allow_html=True)
        st.divider()
        st.info("Log in to access your personal dashboard, track vitals, and get tailored AI insights.")
        st.link_button("\U0001f517 Login with Google", get_google_login_url(), use_container_width=True)
        
        # Pushing footer links to the bottom
        st.write("\n" * 5)
        st.divider()
        st.page_link("pages/1_Terms_of_Service.py", label="Terms of Service", icon="📜")
        st.page_link("pages/2_Privacy_Policy.py", label="Privacy Policy", icon="🔒")
        
    # ── COMPACT HERO ──────────────────────────────────────────────
    st.markdown("""
    <div style="padding: 16px 0 8px 0;">
        <h1 style="font-size:2rem; font-weight:700; margin-bottom:6px;">🏥 HealthCare AI Assistant</h1>
        <p style="font-size:0.95rem; color:#94A3B8; margin:0;">
            AI-powered health companion — chat, track vitals, manage meds & get personalized insights.
        </p>
        <div style="margin-top:14px; display:flex; gap:10px; flex-wrap:wrap;">
            <span style="background:rgba(32,164,243,0.15); color:#20A4F3; border:1px solid rgba(32,164,243,0.3); border-radius:20px; padding:3px 12px; font-size:0.8rem;">🤖 AI Chat</span>
            <span style="background:rgba(16,185,129,0.15); color:#10B981; border:1px solid rgba(16,185,129,0.3); border-radius:20px; padding:3px 12px; font-size:0.8rem;">📊 Vitals</span>
            <span style="background:rgba(245,158,11,0.15); color:#F59E0B; border:1px solid rgba(245,158,11,0.3); border-radius:20px; padding:3px 12px; font-size:0.8rem;">💊 Medications</span>
            <span style="background:rgba(139,92,246,0.15); color:#8B5CF6; border:1px solid rgba(139,92,246,0.3); border-radius:20px; padding:3px 12px; font-size:0.8rem;">📄 RAG Docs</span>
            <span style="background:rgba(236,72,153,0.15); color:#EC4899; border:1px solid rgba(236,72,153,0.3); border-radius:20px; padding:3px 12px; font-size:0.8rem;">📥 PDF Reports</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── GUEST CHAT ────────────────────────────────────────────────
    st.subheader("💬 Try it now — Chat as Guest")
    st.caption("Login with Google to unlock personalized insights, vitals tracking, and your private health history.")

    # Display chat messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Native chat input (same as login mode)
    user_input = st.chat_input("Ask me about your health...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_msg = st.session_state.messages[-1]["content"]

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")

            try:
                response_data = requests.post(
                    f"{API_BASE_URL}/chat",
                    json={
                        "message": last_msg,
                        "chat_history": st.session_state.messages[:-1]
                    },
                    timeout=30
                )
                response = response_data.json().get("response", "Sorry, I couldn't generate a response.")
            except Exception as e:
                response = f"Error communicating with chatbot: {str(e)}"

            message_placeholder.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
