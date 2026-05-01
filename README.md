# 🏥 HealthCare AI Agent

> An AI-powered personal health assistant that automates medication tracking, monitors fitness data, provides medical insights, and delivers personalized healthcare guidance — all through a conversational interface.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://healthcare-agent-nuurhq4dt28vzlr5jeypa2.streamlit.app)
[![FastAPI Backend](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi)](https://healthcare-agent-xiuw.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Local Setup](#-local-setup)
- [Environment Variables](#-environment-variables)
- [Running Locally](#-running-locally)
- [Deployment](#-deployment)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)

---

## 🌟 Project Overview

HealthCare AI Agent is a **full-stack AI health monitoring platform** built for the Digital Health & Wellness Technology track. It combines a conversational AI chatbot with a structured health database and an interactive dashboard to give patients a complete view of their health journey.

The agent automatically extracts health metrics from natural language (e.g. *"My BP is 120/80 and I slept 7 hours"*), stores them in a database, and visualizes trends over time — no manual data entry required.

**Live Demo:** [https://healthcare-agent-nuurhq4dt28vzlr5jeypa2.streamlit.app](https://healthcare-agent-nuurhq4dt28vzlr5jeypa2.streamlit.app)

---

## ✨ Features

### 🤖 AI Health Agent (5 Specialized Tools)
| Tool | Capability |
|---|---|
| 🏃 **Fitness Tool** | Tracks exercise, steps, calories, and activity patterns |
| 💊 **Medication Tool** | Manages prescriptions, schedules doses, checks for interactions |
| 🥗 **Nutrition Tool** | Provides dietary advice and meal recommendations |
| 🔬 **Medical Research Tool** | Searches MedlinePlus for reliable medical information |
| 🩺 **Symptoms Tool** | Analyzes symptoms and suggests when to seek professional care |

### 📊 Dashboard
- Real-time health vitals cards (Blood Pressure, Weight, Heart Rate, Sleep, Exercise)
- AI-generated personalized health summary based on your recent logs
- Automatic metric extraction from chat messages

### 🎯 Goals & Progress Tracking
- Set personal health goals (weight loss, fitness, sleep, diet, etc.)
- Interactive trend charts powered by live database data:
  - **Weight Trend** — line chart over 90 days
  - **Sleep Consistency** — bar chart over 90 days
  - **Blood Pressure Trend** — dual-line chart (Systolic/Diastolic)

### 💊 Medication Management
- Add and schedule medications with dosage and frequency
- One-click Google Calendar integration — medications are added as recurring calendar events with reminders
- Track medication adherence (Taken / Skipped / Missed)
- View adherence rate percentage

### 📄 PDF Health Report
- Download a full PDF health report with all your vitals, medications, and AI insights

### 🔐 Authentication
- Secure Google OAuth 2.0 sign-in
- User onboarding for health profile (age, weight, conditions, medications, goals)

### 📚 RAG Knowledge Base
- Upload personal PDFs (lab reports, medical documents) that the chatbot can reference
- Admin-managed global medical knowledge base using pgvector similarity search

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Streamlit)                      │
│   ┌──────────┐  ┌───────────┐  ┌─────────┐  ┌──────────┐  │
│   │  Chat UI │  │ Dashboard │  │  Goals  │  │  Meds    │  │
│   └────┬─────┘  └─────┬─────┘  └────┬────┘  └────┬─────┘  │
└────────┼──────────────┼─────────────┼─────────────┼────────┘
         │              │             │             │
         │        HTTP (requests)     │             │
         ▼              ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│                                                             │
│  ┌─────────────┐  ┌────────────┐  ┌─────────────────────┐  │
│  │ Google OAuth│  │ Health Log │  │  Medication CRUD    │  │
│  │  Endpoints  │  │  Endpoints │  │  + Calendar API     │  │
│  └─────────────┘  └────────────┘  └─────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              AI AGENT (LangChain)                   │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │  │ Tool     │ │ Tool     │ │ Tool     │  + 2 more │   │
│  │  │ Fitness  │ │ Meds     │ │ Research │           │   │
│  │  └──────────┘ └──────────┘ └──────────┘           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          HealthMetricParser (data_parser.py)        │   │
│  │  Extracts vitals from natural language chat         │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │ SQLAlchemy (async)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              DATABASE (PostgreSQL + pgvector)                │
│                                                             │
│  users │ health_logs │ medications │ medication_logs        │
│  knowledge_chunks (vector embeddings for RAG)               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow — Chat Message
1. User types *"My BP is 130/85 today"* in the chat.
2. Streamlit sends the message to the FastAPI `/chat/{user_id}` endpoint.
3. The `HealthMetricParser` automatically detects and logs `blood_pressure: 130/85` to the database.
4. The LangChain agent selects the appropriate tool (Symptoms / Medical Research) and generates a health response.
5. The Dashboard and Goals charts are updated the next time the user visits those pages.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit (custom dark-mode CSS) |
| **Backend** | FastAPI + Uvicorn |
| **AI Agent** | LangChain + Google Gemini (LLM) + Groq (fast inference) |
| **Embeddings** | Google Gemini `text-embedding-004` (768-dimensional) |
| **Database** | PostgreSQL (Neon) + pgvector |
| **ORM** | SQLAlchemy (async) |
| **Authentication** | Google OAuth 2.0 |
| **Calendar** | Google Calendar API |
| **Medical Info** | MedlinePlus API |
| **PDF Export** | fpdf2 |
| **RAG Pipeline** | pgvector + custom chunking |
| **Deployment** | Streamlit Cloud + Render |

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+
- PostgreSQL database (local or cloud — we recommend [Neon](https://neon.tech) for free cloud PostgreSQL with pgvector)
- A Google Cloud project with OAuth 2.0 and Calendar API enabled
- A Google AI Studio API key (for Gemini)
- A Groq API key (for LLM inference)

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/HealthCareAGENT.git
cd HealthCareAGENT
```

### 2. Create a Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root (see the [Environment Variables](#-environment-variables) section below for all required keys):
```bash
cp .env.example .env   # if example file exists, otherwise create manually
```

### 5. Initialize the Database
```bash
python -c "from backend.init_db import init; import asyncio; asyncio.run(init())"
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# =============================================
# 🤖 AI / LLM API KEYS
# =============================================

# Google AI Studio API Key — used for Gemini LLM + embeddings
# Get it at: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your_google_ai_studio_api_key

# Groq API Key — used for fast LLM inference
# Get it at: https://console.groq.com
GROK_API_KEY=your_groq_api_key


# =============================================
# 🔐 GOOGLE OAUTH (Sign In with Google)
# =============================================
# How to get these:
# 1. Go to: https://console.cloud.google.com/apis/credentials
# 2. Create an OAuth 2.0 Client ID (Web Application type)
# 3. Copy the Client ID and Client Secret below
# 4. Add authorized redirect URIs (see below)

GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret

# Redirect URI — must match EXACTLY what you register in Google Cloud Console
# For local development:
GOOGLE_REDIRECT_URI=http://localhost:8501
# For production (replace with your Streamlit Cloud URL):
# GOOGLE_REDIRECT_URI=https://your-app.streamlit.app


# =============================================
# 🌐 API URL
# =============================================
# For local development:
API_BASE_URL=http://localhost:8000
# For production (replace with your Render URL):
# API_BASE_URL=https://your-app.onrender.com


# =============================================
# 🗄️ DATABASE (PostgreSQL + pgvector)
# =============================================
# Get a free PostgreSQL database with pgvector at: https://neon.tech
# Connection string format:
# postgresql+asyncpg://USER:PASSWORD@HOST/DBNAME?ssl=require

DATABASE_URL=postgresql+asyncpg://user:password@host/dbname?ssl=require
```

### How to Get Your Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable these APIs:
   - **Google Calendar API**
   - **Google People API** (for profile info)
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Select **Web Application**
6. Add the following **Authorized Redirect URIs**:
   - `http://localhost:8501` (for local dev)
   - `https://your-app.streamlit.app` (for production)
7. Add yourself as a **Test User** under **OAuth Consent Screen → Test Users** (required while the app is in Testing mode)
8. Copy the **Client ID** and **Client Secret** into your `.env` file

---

## ▶️ Running Locally

You need to run **two terminal windows** simultaneously — one for the backend API and one for the frontend.

### Terminal 1 — Start the FastAPI Backend
```bash
# From the project root
python -m uvicorn backend.api:app --reload --port 8000
```
The backend will be live at `http://localhost:8000`.  
You can view the interactive API docs at `http://localhost:8000/docs`.

### Terminal 2 — Start the Streamlit Frontend
```bash
# From the project root
python -m streamlit run frontend/app.py
```
The app will open at `http://localhost:8501`.

### Verify Everything is Working
1. Open `http://localhost:8501` in your browser
2. Click **Sign in with Google**
3. Complete the onboarding profile
4. Try chatting: *"My blood pressure is 120/80 and I slept 7 hours last night"*
5. Open the **Dashboard** tab — your logged metrics should appear
6. Open the **Goals** tab — your Progress Trends charts will populate over time

---

## ☁️ Deployment

### Frontend — Streamlit Cloud
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Set the main file path to `frontend/app.py`
4. Add all `.env` variables as **Secrets** in the Streamlit Cloud dashboard
5. Update `GOOGLE_REDIRECT_URI` to your Streamlit Cloud URL

### Backend — Render
1. Go to [render.com](https://render.com) and create a new **Web Service**
2. Connect your GitHub repo
3. Set the build command to: `pip install -r requirements.txt`
4. Set the start command to: `uvicorn backend.api:app --host 0.0.0.0 --port 8000`
5. Add all `.env` variables as **Environment Variables** in the Render dashboard
6. Update `API_BASE_URL` in your Streamlit Cloud secrets to your Render URL

---

## 📡 API Reference

The full interactive API documentation is available at `http://localhost:8000/docs` when running locally.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check — verify backend is running |
| `GET` | `/login` | Initiate Google OAuth flow |
| `GET` | `/auth/callback` | Handle Google OAuth callback |
| `POST` | `/auth/google-login` | Upsert user from Streamlit OAuth |
| `GET` | `/user/{id}/profile` | Get user's full health profile |
| `POST` | `/user/{id}/onboarding` | Save onboarding health data |
| `PATCH` | `/user/{id}/goals` | Update health goals & fitness level |
| `POST` | `/health-logs/{id}` | Log a health metric |
| `GET` | `/health-logs/{id}` | Get all health logs (filterable by type/days) |
| `GET` | `/health-logs/{id}/latest/{type}` | Get latest log for a specific metric |
| `GET` | `/health-logs/{id}/summary` | Get aggregated health summary |
| `POST` | `/health-logs/{id}/from-text` | Parse and log metrics from natural language |
| `GET` | `/medications/{id}` | Get all active medications |
| `POST` | `/medications/{id}` | Add a new medication + Calendar event |
| `DELETE` | `/medications/{med_id}` | Delete a medication |
| `POST` | `/medications/{med_id}/log` | Log medication as taken/skipped |
| `POST` | `/chat/{id}` | Send a message to the AI agent |
| `GET` | `/export/health-report/{id}` | Download PDF health report |
| `POST` | `/rag/ingest/{id}` | Upload a document to the RAG knowledge base |
| `POST` | `/rag/query` | Query the RAG knowledge base |

---

## 📁 Project Structure

```
HealthCareAGENT/
├── backend/
│   ├── api.py              # FastAPI app — all endpoints, OAuth, CRUD
│   ├── chatbot.py          # LangChain agent setup and routing
│   ├── tools.py            # 5 health tools (Fitness, Medication, Nutrition, Research, Symptoms)
│   ├── models.py           # SQLAlchemy ORM models (User, HealthLog, Medication, etc.)
│   ├── crud.py             # Database helper functions
│   ├── data_parser.py      # Natural language health metric extractor
│   ├── database.py         # Async database connection and session management
│   ├── pdf_generator.py    # PDF health report generator
│   ├── medlineplus.py      # MedlinePlus API integration
│   ├── google_calendar.py  # Google Calendar API integration
│   └── rag/                # RAG pipeline (embedding, chunking, retrieval)
│
├── frontend/
│   ├── app.py              # Main Streamlit app (chat, dashboard, goals, meds)
│   └── pages/
│       ├── 1_Terms_of_Service.py
│       └── 2_Privacy_Policy.py
│
├── crawler/                # Medical web scraper (Trafilatura + BeautifulSoup)
├── data/                   # Local medical knowledge documents
├── admin_ingest.py         # Script to bulk-ingest admin documents into RAG
├── requirements.txt        # Full dependency list
└── .env                    # Environment variables (do NOT commit this)
```

---

## 🔒 Data Privacy

- All health data is stored in a private PostgreSQL database and is never shared with third parties.
- Google OAuth tokens are stored securely and used only for Calendar event creation.
- The AI agent includes safety guardrails — it always recommends consulting a doctor for serious medical concerns.
- No personal health data is sent to external LLM providers beyond what is necessary to generate a response.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ as part of the Digital Health & Wellness Technology Hackathon*