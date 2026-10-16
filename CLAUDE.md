# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Run everything from the repo root — `backend` is a package using relative imports, so `python backend/api.py` does not work.

```bash
# Backend (FastAPI) — http://localhost:8000, interactive docs at /docs
python -m uvicorn backend.api:app --reload --port 8000

# Frontend (Streamlit) — http://localhost:8501
python -m streamlit run frontend/app.py

# Create tables + pgvector extension: hit this once while the backend is running
curl http://localhost:8000/startup

# Ingest every PDF/TXT/MD in data/documents/ as global (all-user) RAG knowledge
python admin_ingest.py [--force]
python train_model.py --mode ingest|test|stats   # same ingestion, plus retrieval smoke test / stats

# Health analyzer smoke script (calls the real Anthropic API; needs ANTHROPIC_API_KEY)
python test_health_analyzer.py
```

There is no pytest suite, linter, or formatter configured. `test_health_analyzer.py` is a plain script with printed output, not assertions. `GET /debug/llm-test` and `GET /debug/user/{id}/logs` are the backend's diagnostic endpoints.

### Setup gotchas

- **Dependencies:** there are four requirements files with conflicting pins and none is complete. Root `requirements.txt` lacks `langchain-anthropic` (imported by `backend/chatbot.py` and `backend/health_analyzer.py`); `requirements-backend.txt` lacks `pypdf`; `backend/requirements.txt` lacks `pgvector`. When adding a dependency, update the files that are actually deployed (README: Render builds from root `requirements.txt`).
- **Table creation:** the README's `from backend.init_db import init` command is wrong (the function is `init_tables`), and `backend/init_db.py` never imports `models`, so it creates nothing. `GET /startup` in `api.py` is the path that works. It is a plain route, not a FastAPI startup hook, so it does not run automatically. There are no migrations — schema changes to existing tables must be applied by hand.
- **Database:** `backend/database.py` strips the query string from `DATABASE_URL` and forces `ssl=True`, so it targets Neon; a local non-SSL Postgres needs that changed. `echo=True` logs all SQL.

### Environment variables (`.env` in repo root)

The backend fails at import time if any of these are missing: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, `DATABASE_URL`, `GOOGLE_API_KEY` (Gemini embeddings), `GROK_API_KEY` (misspelled on purpose in code — it holds the **Groq** key). `ANTHROPIC_API_KEY` is needed for the dashboard AI analysis. The frontend reads `API_BASE_URL` (default `http://localhost:8000`) and the Google OAuth vars via `get_secret()`, which checks `st.secrets` first, then the environment.

## Architecture

Two separately deployed processes that talk only over HTTP: a Streamlit frontend (Streamlit Cloud) and a FastAPI backend (Render), backed by Neon PostgreSQL with pgvector.

### Frontend — `frontend/app.py`

One ~1500-line script; no components or modules. Views (chat, dashboard, goals, medications, onboarding) are branches on `st.session_state.page` inside `if st.session_state.user:`; the `else:` branch is the landing page with guest chat. Styling is one CSS block in `inject_custom_css()`.

Auth lives in the frontend: Streamlit receives the Google OAuth `code`, exchanges it with Google itself, then POSTs the user to `/auth/google-login`. The session is kept across refreshes by putting `user_id` in the URL query params and re-fetching the profile. The backend's `/login` and `/auth/callback` are a legacy flow with `localhost:8501` hardcoded.

**The backend has no authentication.** Every endpoint trusts the `user_id` in the path, and the frontend trusts `user_id` from the URL.

### Backend — `backend/`

- `api.py` — every route, plus the Pydantic request models defined inline next to the routes that use them. CORS origins are hardcoded here (localhost:8501 and the production Streamlit URL).
- `crud.py` / `models.py` / `database.py` — async SQLAlchemy (asyncpg). Tables: `users`, `health_logs`, `medications`, `medication_logs`, `knowledge_chunks`. `HealthLog.value` is a free-form string (`"120/80"`, `"7"`), so consumers parse it themselves. Medications are soft-deleted via `is_active`.
- `rag/` — uses its **own synchronous engine** (psycopg2, URL rewritten in `rag/vector_store.py`), separate from the async one. `KnowledgeChunk.user_id IS NULL` means global knowledge; users see global + their own chunks, guests only global. `Vector(3072)` in `models.py` is tied to `EMBEDDING_MODEL` in `rag/config.py` (`gemini-embedding-2`) — changing one requires changing the other and re-ingesting.

### Chat pipeline

`POST /chat` is stateless: the frontend sends the message together with the user profile, recent health logs, and chat history in the body. `chatbot.get_response()` then:

1. If the message contains a generic medical keyword ("what is", "symptoms", "treatment", …) and MedlinePlus returns a result, summarizes that and **returns early**, skipping everything below.
2. Otherwise builds one prompt from profile + logs + history + RAG chunks (`rag/retriever.py`) + tool context, and calls Groq (`llama-3.1-8b-instant`).

The "5 tools" in `tools.py` are not LangChain agent tools. `get_tool_context()` picks a topic by regex keyword counts (`TOPIC_PATTERNS`), falling back to the recent conversation's topic when the current message matches weakly, and the chosen tool function returns a block of prompt instructions. The tool name is prepended to the reply as an italic badge.

Metric extraction from chat is driven by the frontend, not `/chat`: after a reply, the frontend calls `/parse-metrics` (regex-based `HealthMetricParser` in `data_parser.py`) and POSTs each hit to `/health-logs/{user_id}`.

### Two LLM providers

- Chat: Groq via `langchain_groq` (`chatbot.py`).
- Dashboard "AI analysis" (`GET /user/{id}/vitals-summary`): `health_analyzer.py` computes trends, anomalies, and risk factors statistically, then asks Anthropic Claude Haiku for a 3–4 line summary, falling back to a templated string if the LLM call fails.

### Stale documentation

`README.md` predates several changes: it describes `/chat/{id}`, `/rag/query`, `/rag/ingest/{id}`, `text-embedding-004` (768-dim), and `crawler/` and `data/` directories — none of which match the code. `ML_TRAINING_ARCHITECTURE.md` and `MODEL_TRAINING_QUICKSTART.md` describe RAG ingestion (there is no model training) and reference a `crawler/crawl_medical_docs.py` and a `train_model.py --mode crawl` that do not exist. Trust the code over these files.
