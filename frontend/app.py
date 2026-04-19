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
# Chatbot AI responses - Get personalized health advice using LLM
from chatbot import get_response
# Health metric parser - Extract metrics from natural language input
from data_parser import HealthMetricParser
# requests - HTTP client for communicating with FastAPI backend
import requests
# datetime - Date/time operations for health tracking
from datetime import datetime, timedelta, date

# ============================================
# PAGE CONFIG & SETUP
# ============================================
st.set_page_config(
    page_title="HealthCare AI",
    page_icon="🏥",
    layout="wide"
)

API_BASE_URL = "http://localhost:8000"

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
# CHECK LOGIN (FROM FASTAPI REDIRECT)
# -------------------------
params = st.query_params

# FastAPI sends: ?user=name&onboarded=true/false&user_id=123
if "user" in params:
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
                            st.success("✅ Onboarding completed successfully!")
                            st.balloons()
                            st.markdown("---")
                            st.write("Redirecting to dashboard...")
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
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            st.title("🏥 HealthCare AI Assistant")
        with col2:
            st.write("")
            st.write("")
            st.caption(f"👤 {st.session_state.user}")
        with col3:
            st.write("")
            st.write("")
            st.link_button(
                "📥 PDF Report",
                f"{API_BASE_URL}/export/health-report/{st.session_state.user_id}",
                use_container_width=True
            )
        with col4:
            st.write("")
            st.write("")
            if st.button("Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.user_id = None
                st.session_state.user_profile = None
                st.session_state.health_logs = None
                st.session_state.messages = []
                st.query_params.clear()
                st.rerun()

        # ✅ NAVIGATION FOR LOGGED-IN USERS
        page = st.pills(
            "Navigation",
            ["💬 Chat", "💊 Medications", "📊 Wellness Tracker"],
            default="💬 Chat"
        )

        if page == "💬 Chat":
            st.divider()

            # Fetch and cache the user's health profile for personalized responses
            if "user_profile" not in st.session_state or st.session_state.user_profile is None:
                try:
                    profile_response = requests.get(
                        f"{API_BASE_URL}/user/{st.session_state.user_id}/profile",
                        timeout=5
                    )
                    if profile_response.status_code == 200:
                        st.session_state.user_profile = profile_response.json().get("profile", {})
                    else:
                        st.session_state.user_profile = {}
                except Exception:
                    st.session_state.user_profile = {}

            # Fetch and cache recent health logs for context-aware responses
            if "health_logs" not in st.session_state or st.session_state.health_logs is None:
                try:
                    logs_response = requests.get(
                        f"{API_BASE_URL}/health-logs/{st.session_state.user_id}",
                        params={"days": 30},
                        timeout=5
                    )
                    if logs_response.status_code == 200:
                        st.session_state.health_logs = logs_response.json().get("logs", [])
                    else:
                        st.session_state.health_logs = []
                except Exception:
                    st.session_state.health_logs = []

            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])

            user_input = st.chat_input("Ask me about your health...")

            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.chat_message("user").write(user_input)

                # Get response from chatbot WITH profile, health logs, AND chat history
                response = get_response(
                    user_input,
                    user_profile=st.session_state.user_profile,
                    health_logs=st.session_state.health_logs,
                    chat_history=st.session_state.messages
                )
                
                # Extract and save any health metrics from the input
                metrics = HealthMetricParser.parse(user_input)
                if metrics and st.session_state.user_id:
                    try:
                        for metric in metrics:
                            requests.post(
                                f"{API_BASE_URL}/health-logs/{st.session_state.user_id}",
                                json={
                                    "metric_type": metric["metric_type"],
                                    "value": metric["value"],
                                    "unit": metric["unit"],
                                    "source": "chatbot"
                                },
                                timeout=5
                            )
                        response += f"\n\n📊 **Metrics saved:** {', '.join([m['metric_type'] for m in metrics])}"
                        # Refresh the cached health logs so next response has latest data
                        st.session_state.health_logs = None
                    except Exception as e:
                        st.warning(f"⚠️ Could not save metrics: {str(e)}")

                st.session_state.messages.append({"role": "assistant", "content": response})
                st.chat_message("assistant").write(response)

        elif page == "📊 Wellness Tracker":
            st.header("📊 Your Wellness Tracker")

            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["📈 View Logs", "➕ Add Metric", "📋 Summary"])
            
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

        elif page == "💊 Medications":
            st.header("💊 Medication Manager")

            med_tab1, med_tab2, med_tab3 = st.tabs(["📋 My Medications", "➕ Add Medication", "📈 Adherence Report"])

            # ========================
            # TAB 1: My Medications
            # ========================
            with med_tab1:
                st.subheader("Your Active Medications")

                try:
                    response = requests.get(
                        f"{API_BASE_URL}/medications/{st.session_state.user_id}",
                        timeout=5
                    )

                    if response.status_code == 200:
                        data = response.json()
                        meds = data.get("medications", [])

                        if meds:
                            today_str = date.today().isoformat()

                            for med in meds:
                                with st.container(border=True):
                                    col1, col2, col3 = st.columns([3, 2, 2])

                                    with col1:
                                        st.markdown(f"### 💊 {med['name']}")
                                        if med.get('dosage'):
                                            st.caption(f"Dosage: {med['dosage']}")
                                        freq_display = med.get('frequency', 'daily').replace('_', ' ').title()
                                        st.caption(f"⏰ {freq_display} at {med.get('time_of_day', 'N/A')}")
                                        if med.get('notes'):
                                            st.caption(f"📝 {med['notes']}")

                                    with col2:
                                        st.write("")
                                        st.write("**Today's status:**")
                                        bcol1, bcol2 = st.columns(2)
                                        with bcol1:
                                            if st.button("✅ Taken", key=f"taken_{med['id']}", use_container_width=True):
                                                try:
                                                    requests.post(
                                                        f"{API_BASE_URL}/medications/{med['id']}/log",
                                                        json={"scheduled_date": today_str, "status": "taken"},
                                                        timeout=5
                                                    )
                                                    st.success("Marked as taken!")
                                                    st.rerun()
                                                except Exception as e:
                                                    st.error(f"Error: {e}")
                                        with bcol2:
                                            if st.button("⏭️ Skip", key=f"skip_{med['id']}", use_container_width=True):
                                                try:
                                                    requests.post(
                                                        f"{API_BASE_URL}/medications/{med['id']}/log",
                                                        json={"scheduled_date": today_str, "status": "skipped"},
                                                        timeout=5
                                                    )
                                                    st.warning("Marked as skipped")
                                                    st.rerun()
                                                except Exception as e:
                                                    st.error(f"Error: {e}")

                                    with col3:
                                        st.write("")
                                        cal_status = "📅 Calendar ✅" if med.get('has_calendar_event') else "📅 No reminder"
                                        st.caption(cal_status)
                                        if st.button("🗑️ Remove", key=f"remove_{med['id']}", use_container_width=True):
                                            try:
                                                requests.delete(
                                                    f"{API_BASE_URL}/medications/{med['id']}",
                                                    timeout=5
                                                )
                                                st.success(f"Removed {med['name']}")
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Error: {e}")
                        else:
                            st.info("📭 No medications added yet. Use the 'Add Medication' tab to get started!")
                    else:
                        st.error(f"Error fetching medications: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

            # ========================
            # TAB 2: Add Medication
            # ========================
            with med_tab2:
                st.subheader("Add a New Medication")

                with st.form("add_medication_form"):
                    med_name = st.text_input("Medication Name *", placeholder="e.g., Metformin")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        med_dosage = st.text_input("Dosage", placeholder="e.g., 500mg")
                    with col2:
                        med_frequency = st.selectbox(
                            "Frequency",
                            ["daily", "twice_daily", "weekly", "as_needed"],
                            format_func=lambda x: x.replace("_", " ").title()
                        )

                    col1, col2 = st.columns(2)
                    with col1:
                        med_time = st.time_input("Reminder Time", value=None)
                    with col2:
                        med_start = st.date_input("Start Date", value=date.today())

                    med_end = st.date_input("End Date (optional)", value=None)
                    med_notes = st.text_area("Notes (optional)", placeholder="e.g., Take with food")

                    submitted = st.form_submit_button("💊 Add Medication & Set Reminder", use_container_width=True)

                    if submitted:
                        if not med_name:
                            st.error("❌ Please enter a medication name")
                        else:
                            try:
                                time_str = med_time.strftime("%H:%M") if med_time else "08:00"
                                payload = {
                                    "name": med_name,
                                    "dosage": med_dosage if med_dosage else None,
                                    "frequency": med_frequency,
                                    "time_of_day": time_str,
                                    "start_date": med_start.isoformat(),
                                    "end_date": med_end.isoformat() if med_end else None,
                                    "notes": med_notes if med_notes else None,
                                }

                                response = requests.post(
                                    f"{API_BASE_URL}/medications/{st.session_state.user_id}",
                                    json=payload,
                                    timeout=15
                                )

                                if response.status_code == 200:
                                    result = response.json()
                                    st.success(f"✅ {med_name} added successfully!")
                                    if result.get("calendar_event") == "created":
                                        st.info("📅 Google Calendar reminder created!")
                                    else:
                                        st.warning("⚠️ Calendar reminder not created. Please re-login to grant calendar access.")
                                    st.balloons()
                                else:
                                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")

            # ========================
            # TAB 3: Adherence Report
            # ========================
            with med_tab3:
                st.subheader("📈 Medication Adherence")

                period = st.selectbox("Report Period", [7, 14, 30], format_func=lambda x: f"Last {x} days")

                try:
                    response = requests.get(
                        f"{API_BASE_URL}/medications/{st.session_state.user_id}/adherence",
                        params={"days": period},
                        timeout=5
                    )

                    if response.status_code == 200:
                        stats = response.json()

                        if stats.get("total_medications", 0) > 0:
                            # Summary metrics
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("💊 Active Meds", stats.get("total_medications", 0))
                            with col2:
                                st.metric("✅ Taken", stats.get("taken", 0))
                            with col3:
                                st.metric("⏭️ Skipped", stats.get("skipped", 0))
                            with col4:
                                rate = stats.get("adherence_rate", 0)
                                st.metric("📊 Adherence", f"{rate}%")

                            # Visual indicator
                            st.divider()
                            rate = stats.get("adherence_rate", 0)
                            if rate >= 80:
                                st.success(f"🌟 Excellent! Your adherence rate is {rate}%. Keep it up!")
                            elif rate >= 50:
                                st.warning(f"⚠️ Your adherence rate is {rate}%. Try to be more consistent with your medications.")
                            else:
                                st.error(f"🔴 Your adherence rate is {rate}%. Please talk to your doctor if you're having trouble with your medications.")
                        else:
                            st.info("📭 No medications to track. Add medications first!")
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

else:
    # ❌ USER NOT LOGGED IN
    st.title("🏥 HealthCare AI Assistant")
    
    mode = st.radio(
        "Choose Mode",
        ["Continue as Guest", "Login for Personalized Advice"]
    )

    if mode == "Login for Personalized Advice":
        st.warning("🔐 Please log in with your Google account to:")
        st.markdown("""
        - **Get personalized health advice** based on your profile
        - **Track your wellness metrics** over time
        - **Access your health history** anytime
        - **Receive insights** based on your data
        """)
        st.link_button("🔗 Login with Google", "http://127.0.0.1:8000/login", use_container_width=True)
        st.stop()
    
    # GUEST MODE
    st.divider()
    st.subheader("💬 Chat with Health Assistant")
    
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    user_input = st.chat_input("Ask me about your health...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        response = get_response(user_input, chat_history=st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)