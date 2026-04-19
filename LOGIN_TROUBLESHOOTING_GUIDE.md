# Login Stuck on Loading - Troubleshooting Guide

## Issues Fixed ✅

### 1. **API_BASE_URL Configuration** 
- **Problem**: API_BASE_URL was commented out in `.env`, causing frontend to fail backend calls
- **Fix**: Enabled `API_BASE_URL=http://localhost:8000` for local development
- **Location**: `.env` line 8

### 2. **Google OAuth Redirect URI**
- **Problem**: GOOGLE_REDIRECT_URI was set to production URL (Streamlit Cloud) instead of local dev
- **Fix**: Changed to `GOOGLE_REDIRECT_URI=http://localhost:8501` for local development
- **Location**: `.env` line 5

### 3. **Debug Logging Added**
- **Problem**: No visibility into which step was failing in the OAuth flow
- **Fix**: Added debug messages in frontend/app.py:
  - `🔄 Processing OAuth callback...` - Shows OAuth flow started
  - `📝 Exchanging authorization code for tokens...` - Token exchange in progress
  - `👤 Retrieving Google user info...` - Getting user profile from Google
  - `💾 Saving user to backend database...` - Saving to DB
  - `✅ Login successful! Redirecting...` - Confirmation before rerun
  - Added spinners for profile/health log loading

## How to Test

### Prerequisites
1. **FastAPI Backend Running**:
   ```bash
   cd d:\Projects\HealthCareAGENT\backend
   python -m uvicorn api:app --reload --host localhost --port 8000
   ```

2. **Database Connected**:
   - Ensure `DATABASE_URL` in `.env` points to valid PostgreSQL database
   - Check Neon database credentials are correct

3. **Google OAuth Credentials Valid**:
   - `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` must be correct
   - OAuth app must have `http://localhost:8501` registered as a redirect URI

### Test Steps

1. **Start Backend**:
   ```bash
   cd backend
   python -m uvicorn api:app --reload
   ```

2. **Start Streamlit Frontend**:
   ```bash
   cd frontend
   streamlit run app.py
   ```

3. **Test Login Flow**:
   - Navigate to http://localhost:8501
   - Click "Login for Personalized Advice"
   - Click "Login with Google"
   - Complete OAuth flow
   - **Check for debug messages** showing each step
   - Should redirect to onboarding or main app

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Failed to save user" error | Backend not running or API_BASE_URL incorrect | Check backend is running on http://localhost:8000 |
| OAuth callback fails | GOOGLE_REDIRECT_URI doesn't match registered URI | Ensure .env has `GOOGLE_REDIRECT_URI=http://localhost:8501` |
| Page loads forever | Database connection timeout | Check DATABASE_URL and Neon credentials |
| "Failed to get user info from Google" | OAuth token invalid or Google API issue | Check OAuth credentials in .env |
| Still stuck on loading after fixes | Backend API endpoints not responding | Check backend logs for errors |

## Verification Checklist

- [ ] API_BASE_URL is uncommented and set to `http://localhost:8000`
- [ ] GOOGLE_REDIRECT_URI is set to `http://localhost:8501` (not production URL)
- [ ] FastAPI backend is running on port 8000
- [ ] Database connection is working
- [ ] Debug messages appear in Streamlit when attempting login
- [ ] Backend receives POST request to `/auth/google-login` endpoint
- [ ] User is successfully created in database

## Debug Commands

### Check Backend Connectivity
```bash
curl -X GET http://localhost:8000/health
```

### View Streamlit Logs
Check the terminal where `streamlit run` was executed

### Check Backend Database
```bash
# In PostgreSQL:
SELECT * FROM users WHERE email = 'your.email@gmail.com';
```

## Files Modified
- `.env` - Fixed API_BASE_URL and GOOGLE_REDIRECT_URI
- `frontend/app.py` - Added debug logging and spinners for loading states
