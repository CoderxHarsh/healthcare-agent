# 🏥 Health Monitoring Chatbot

An AI-powered health assistant that helps users track health metrics, manage medications, and receive personalized insights using modern AI and cloud technologies.

---

## 🚀 Project Overview

This project is a smart health chatbot that allows users to:

- Chat naturally about their health  
- Log health data (BP, sugar, weight, etc.)  
- Get basic health insights  
- (Upcoming) Receive medication reminders  
- (Upcoming) Store and analyze personal health history  

---

## ✅ Features Implemented

### 💬 1. AI Chatbot 
- Built using **Grok AI**
- Provides health-related responses
- Uses prompt engineering for safe and helpful replies

---

### 🧠 2. Intent Detection (upcoming)
- Detects user intent:
  - Health data logging  
  - General health questions  
  - Medication-related inputs  

---

### 📊 3. Health Data Parsing (upcoming)
- Extracts structured data from natural language  

**Example:**
"My BP is 120/80" → Parsed as BP = 120/80"


---

### 🗂️ 4. Temporary Data Storage
- Uses session-based storage (Streamlit)
- Simulates database behavior before backend integration  

---

### 💻 5. Interactive UI
- Built using **Streamlit**
- Chat interface with history tracking  
- Clean and responsive layout  

---

## 🧱 Current Architecture
User → Chat UI (Streamlit) → Python Backend → Grok API → Response


---

## 🚧 Upcoming Features

### 🔐 1. Google OAuth Authentication
- Login with Google account  
- Unique user identification using Google `sub` ID  

---

### 🗄️ 2. PostgreSQL Database Integration
- Store:
  - User profiles  
  - Health logs  
  - Medications  
- Structured relational schema  

---

### 🧠 3. RAG (Retrieval-Augmented Generation)
- Personalized responses using user's own health history  
- Vector search using pgvector  

---

### 💊 4. Medication Management System
- Add medications via chatbot  
- Store dosage and frequency  

---

### ⏰ 5. Google Calendar Integration
- Automatic reminder creation  
- Notifications for:
  - Medications  
  - Health activities (e.g., yoga)  

---

### 📈 6. Health Insights & Analytics
- Weekly/monthly summaries  
- Trend analysis (e.g., BP over time)  

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit  
- **Backend**: Python  
- **AI Model**: Grok AI (openai/gpt-oss-20b)  
- **Database (Upcoming)**: PostgreSQL  
- **Auth (Upcoming)**: Google OAuth  
- **APIs (Upcoming)**: Google Calendar API  

---