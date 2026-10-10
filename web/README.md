# HealthCare AI — React frontend

React + Vite + TypeScript replacement for the Streamlit app in `../frontend`. It talks to the same FastAPI backend and needs no backend code changes for local development.

## Run locally

```bash
# 1. Backend, from the repo root
python -m uvicorn backend.api:app --reload --port 8000

# 2. Frontend, from this folder
npm install
npm run dev        # http://localhost:8501
```

Open `http://localhost:8501` (not `127.0.0.1`). The port is fixed at 8501 because the backend's CORS allow-list and its OAuth callback redirect are hardcoded to that origin.

`npm run build` type-checks and writes a production bundle to `dist/`.

## Google login setup

A browser app cannot hold the Google client secret, so sign-in goes through the backend's `/login` → `/auth/callback` routes instead of the code exchange Streamlit did itself. For that to work:

1. In the root `.env`, set `GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback`.
2. In Google Cloud Console → Credentials → your OAuth client, add `http://localhost:8000/auth/callback` to **Authorized redirect URIs**.

With this setting the Streamlit app's own login stops working, since both read the same variable.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend base URL. Copy `.env.example` to `.env` to change it. |

## Not yet possible without backend changes

- **Production deploy:** `backend/api.py` redirects to `http://localhost:8501` after login and only allows that origin plus the Streamlit URL in CORS. Both need to become configurable before this app can be hosted.
- **Per-medication adherence:** `/medications/{id}/adherence` returns overall totals only, so the report shows overall figures.

## Layout

- `src/api/` — typed client, response types, and query definitions for every backend route used.
- `src/auth/` — session (user id in `localStorage`, profile fetched from the backend).
- `src/chat/` — conversation state, kept above the router so it survives navigation.
- `src/pages/` — one file per screen.
- `src/components/` — layout shell, route guards, chat panel, tabs, toasts.
