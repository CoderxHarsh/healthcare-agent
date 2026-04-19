# 🔧 OAuth Login Debugging Guide

## Quick Health Check

First, test if your API is working:

**Visit:** `http://localhost:8000/health`

This should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "users_in_db": <number>,
  "google_configured": true,
  "environment": { ... }
}
```

If you see `google_configured: false`, your Google credentials aren't loaded properly.

---

## Step-by-Step Login Testing

### 1. **Start the login flow**
   - Go to: `http://localhost:8000/`
   - Click: "Login with Google"

### 2. **Check API logs**
   During login, watch the **FastAPI terminal** for these messages:

   ✅ **Should see:**
   ```
   📝 Authorization code received: 4/0Aci9...
   🔄 Exchanging code for token...
   ✅ Token received
   🔄 Fetching user info...
   ✅ User info from Google: {'id': '12345...', 'email': 'user@gmail.com', ...}
   💾 Saving user to database...
   ✅ User saved: user@gmail.com (ID: 1)
   🔗 Redirecting to: http://localhost:8501/?user=...
   ```

   ❌ **If you see errors like:**
   - `Token exchange failed` → Google credentials might be wrong
   - `Database error` → Database connection issue
   - `Failed to get user info` → Google API issue

---

## Common Issues & Fixes

### **Issue 1: "Failed to retrieve access token"**
**Cause:** Wrong Google OAuth credentials
**Fix:**
1. Check `.env` file has:
   ```
   GOOGLE_CLIENT_ID=<your_id>
   GOOGLE_CLIENT_SECRET=<your_secret>
   GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
   ```
2. Verify credentials in [Google Cloud Console](https://console.cloud.google.com)
3. Make sure redirect URI is registered in Google OAuth app settings

### **Issue 2: "Internal server error" after Google redirect**
**Cause:** Database connection problem
**Fix:**
1. Run: `python test_db.py` to verify database
2. Check `.env` has valid `DATABASE_URL`
3. Run: `python init_db.py` to recreate tables

### **Issue 3: "No authorization code found"**
**Cause:** Google didn't send the code
**Fix:**
1. Check redirect URI matches exactly in:
   - `.env` file: `GOOGLE_REDIRECT_URI`
   - Google Cloud Console settings
2. Try logging in again

---

## Manual Testing Commands

### Test Database
```bash
.\.venv\Scripts\Activate.ps1 ; python test_db.py
```

### Test API Health
```bash
.\.venv\Scripts\Activate.ps1 ; curl http://localhost:8000/health
```

### Reinitialize Database
```bash
.\.venv\Scripts\Activate.ps1 ; python init_db.py
```

### Test Direct Imports
```bash
.\.venv\Scripts\Activate.ps1 ; python -c "from api import app; print('API imports OK')"
```

---

## Getting Detailed Error Info

### Option 1: Check the API Terminal
The API terminal (uvicorn) shows all detailed logs. Look for error messages starting with ❌

### Option 2: Check Streamlit Terminal
The Streamlit terminal where you ran `streamlit run app.py` might show connection errors

### Option 3: Browser Console
After error, press `F12` → Console tab to see browser errors

---

## Next Steps

After fixing, **try login again**:

1. Go to: `http://localhost:8000/login`
2. Sign in with Google
3. You should be redirected to onboarding form at: `http://localhost:8501`

If you still get an error, **share the error message from the API terminal logs** and I can provide more specific help!

---

## 📋 Environment Checklist

- [ ] `.env` file exists and is readable
- [ ] `GOOGLE_CLIENT_ID` is set
- [ ] `GOOGLE_CLIENT_SECRET` is set
- [ ] `GOOGLE_REDIRECT_URI` = `http://localhost:8000/auth/callback`
- [ ] `DATABASE_URL` is valid and accessible
- [ ] FastAPI running on `http://localhost:8000`
- [ ] Streamlit running on `http://localhost:8501`
- [ ] Database tables created (run `python init_db.py`)
