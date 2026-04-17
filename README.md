# 🏥 HealthCare AI Assistant

An AI-powered health assistant that provides **personalized** health advice based on user profiles, tracks health metrics over time, and uses specialized domain tools for fitness, nutrition, medication, symptoms, and medical research.

---

## 🚀 Project Overview

This project is a smart health chatbot that allows users to:

- 🔐 Log in securely with Google OAuth
- 📋 Complete a health profile during onboarding (age, conditions, medications, goals, etc.)
- 💬 Chat naturally and receive **personalized** advice based on their health profile
- 📊 Track health metrics (BP, weight, sleep, heart rate, etc.) over time
- 🏋️ Get domain-specific guidance via 5 specialized AI tools
- 📈 View health trends and summaries in a wellness tracker dashboard

---

## ✅ Features Implemented

### 🔐 1. Google OAuth Authentication
- Login with Google account via FastAPI OAuth2 flow
- Unique user identification using Google `sub` ID
- Secure callback handling and session management

---

### 📋 2. User Onboarding
- New users complete a health profile form after first login
- Collects: age, gender, height, weight, health conditions, medications, allergies, fitness level, health goals
- Data saved to PostgreSQL and used to personalize all chatbot responses

---

### 💬 3. AI Chatbot (Personalized)
- Built using **LangChain + Groq** (openai/gpt-oss-20b model)
- **Profile-aware**: Injects the user's onboarding data (conditions, medications, allergies, goals) into every prompt
- **Logs-aware**: Feeds recent health logs (last 30 days) into the prompt so the bot can reference actual tracked data and spot trends
- Uses prompt engineering for safe, concise, and supportive replies
- Auto-extracts health metrics from chat (e.g. "my BP is 120/80") and saves them to the database

---

### 🧰 4. Specialized Healthcare Tools
Five domain-specific tools that automatically activate based on the user's query:

| Tool | Activates On | What It Does |
|------|-------------|--------------|
| 🏋️ **Fitness Advisor** | workout, exercise, gym, yoga… | Calculates BMI, recommends intensity based on fitness level, warns about condition conflicts |
| 💊 **Medication Advisor** | medicine, drug, dose, side effect… | Flags interactions with current meds, checks allergies, enforces safe prescribing rules |
| 🥗 **Nutrition Advisor** | diet, food, calorie, meal… | Computes TDEE/BMR, suggests caloric targets for goals, respects allergies & conditions |
| 🔬 **Medical Research** | research, study, guidelines… | Evidence-based framing, cites WHO/CDC/NIH, distinguishes established vs. emerging science |
| 🩺 **Symptom Checker** | pain, headache, fever, cough… | Structured triage (🟢🟡🔴 urgency), asks clarifying questions, flags emergencies |

Tools are routed automatically via keyword detection — no user action needed.

---

### 📊 5. Health Data Tracking
- **Auto-parsing**: Extracts structured metrics from natural language chat
  - Example: `"My BP is 120/80"` → saved as Blood Pressure = 120/80 mmHg
- **Manual logging**: Users can add metrics via the Wellness Tracker tab
- **Supported metrics**: Blood Pressure, Weight, Heart Rate, Blood Sugar, Sleep, Exercise, Temperature
- **Data fed into chatbot**: Recent logs are included in the AI prompt for trend-aware responses

---

### 📈 6. Wellness Tracker Dashboard
- **View Logs**: Filterable table of health metrics by type and date range
- **Add Metric**: Manual entry form with auto-detected units
- **Health Summary**: Grouped overview of all metrics with expandable details

---

### 🗄️ 7. PostgreSQL Database (Neon)
- **Users table**: Profile info + onboarding health data (age, conditions, medications, etc.)
- **Health Logs table**: Time-series health measurements with metric type, value, unit, source
- Async database access via SQLAlchemy + asyncpg
- CRUD operations for users, onboarding, and health logs

---

### 💻 8. Interactive UI
- Built using **Streamlit**
- Chat interface with message history
- Navigation pills: 💬 Chat | 📊 Wellness Tracker
- Guest mode (basic chat) and authenticated mode (personalized)
- Onboarding flow with auto-redirect after completion

---

## 🧱 Architecture

```
User → Streamlit UI → FastAPI Backend → PostgreSQL (Neon)
                ↓                ↓
         Chat Interface    Google OAuth
                ↓
       Chatbot Engine (LangChain + Groq)
         ├── User Profile (from DB)
         ├── Health Logs (from DB)
         └── Tool Router → Fitness | Medication | Nutrition | Research | Symptoms
```

---

## 📁 Project Structure

```
HealthCareAGENT/
├── app.py                  # Streamlit frontend (chat, tracker, onboarding)
├── api.py                  # FastAPI backend (OAuth, REST endpoints)
├── chatbot.py              # LLM integration (prompt builder, profile/logs injection)
├── tools.py                # 5 specialized healthcare tools + topic router
├── models.py               # SQLAlchemy models (User, HealthLog)
├── crud.py                 # Database CRUD operations
├── database.py             # Async DB engine & session setup
├── data_parser.py          # Regex-based health metric extractor
├── migrate_users_table.py  # DB migration script for onboarding columns
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (API keys, DB URL, OAuth)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit |
| **Backend API** | FastAPI + Uvicorn |
| **AI Model** | Groq (openai/gpt-oss-20b) via LangChain |
| **Database** | PostgreSQL (Neon) — async via SQLAlchemy + asyncpg |
| **Authentication** | Google OAuth 2.0 |
| **Language** | Python 3.11+ |

---

## 🚧 Upcoming Features

- 💊 **Medication Management** — Add/track medications via chatbot, store dosage & frequency
- ⏰ **Google Calendar Integration** — Auto-create reminders for medications & health activities
- 🧠 **RAG (Retrieval-Augmented Generation)** — Vector search over health history using pgvector
- 📉 **Advanced Analytics** — Weekly/monthly health reports with trend charts
- 🔔 **Push Notifications** — Alerts for abnormal readings or missed medications

---

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/CoderxHarsh/healthcare-agent.git
cd healthcare-agent

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up .env file with:
#    GROK_API_KEY, DATABASE_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

# 5. Start FastAPI backend
uvicorn api:app --reload

# 6. Start Streamlit frontend (in another terminal)
streamlit run app.py
```

---