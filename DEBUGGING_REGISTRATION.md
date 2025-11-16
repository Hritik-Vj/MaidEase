# 🔍 Debugging Registration Issue

## Current Status
Registration form loads but appears to hang indefinitely on "Creating account..." message. Need to identify where the request is failing.

## Step 1: Frontend Diagnostics ✅

### 1.1 Check Browser Console
1. Go to https://maidease-two.vercel.app/register
2. Press **F12** to open Developer Tools
3. Click **Console** tab
4. Fill out the registration form
5. Click **"Create Account"**
6. **Look for these logs:**
   - Should see: `📤 API Request: { method: 'POST', url: '/auth/register', ... }`
   - Should see: Either `✅ API Response Success: { status: 201, ... }` OR `❌ API Response Error: { status: XXX, ... }`

### 1.2 Check Network Tab
1. Keep Developer Tools open (F12)
2. Click **Network** tab
3. Click the **XHR** filter to show only API calls
4. **Refresh the page**
5. Fill out the registration form again
6. Click **"Create Account"**
7. **Look for:**
   - A **POST** request to `/auth/register`
   - If found:
     - Click on it
     - Check **Status** column (should be 201 for success, or 4xx/5xx for error)
     - Click **Response** tab to see the answer from backend
     - Click **Request** tab to see what data was sent
   - If NOT found:
     - This means the request never left your browser!
     - Check Console for JavaScript errors

### 1.3 What the Logs Should Show (Success Case)
```
🔗 API URL: https://maidease-api.onrender.com/api/v1
📦 Environment: { VITE_API_URL: 'https://maidease-api.onrender.com/api/v1', MODE: 'production', DEV: false, HOSTNAME: 'maidease-two.vercel.app' }
📤 API Request: { method: 'POST', url: '/auth/register', headers: {...}, data: {...} }
✅ API Response Success: { url: '/auth/register', status: 201, data: { id: 'xxx', email: 'test@example.com', ... } }
```

---

## Step 2: Backend Diagnostics ✅

### 2.1 Check Backend Logs on Render
1. Go to https://dashboard.render.com
2. Click on **maidease-api** service
3. Click **Logs** tab
4. The logs automatically scroll to latest
5. Try registration again from frontend
6. **Look for these messages:**
   ```
   🔐 Registration attempt: email=user@example.com, role=customer
   🔐 Checking if user exists: user@example.com
   🔐 Creating new user: user@example.com, role=customer
   💾 Saving user to database: user@example.com
   ✅ Registration successful: user_id=xxx (user@example.com)
   📨 POST /api/v1/auth/register - Client: xxx.xxx.xxx.xxx
   📤 POST /api/v1/auth/register - Status: 201 - Time: 0.23s
   ```

### 2.2 If Logs Show Errors
Look for messages like:
- `❌ Registration error: Email already registered`
- `❌ Unexpected error during registration: ...`
- `💔 Database connection failed`

---

## Step 3: Troubleshooting Decision Tree

### Scenario A: Console shows `📤 API Request` but no `✅ API Response`
**Problem:** Request sent but no response received
- **Check Network tab:** What's the status code?
  - **504, 503, timeout:** Backend crashed or taking too long
    - Action: Check Render logs for errors
  - **CORS error:** Not appearing in console, but Network shows error
    - Action: Verify CORS_ORIGINS in Render environment variables
  - **Other error (4xx/5xx):** 
    - Action: Check Response tab for error message

### Scenario B: Console shows NO `📤 API Request` log
**Problem:** Request never sent from browser
- **Check Console for errors:** Look for red error messages
  - **JavaScript error?** Fix the error, then try again
  - **Form validation error?** Check if form values are valid
- **Might be:** Register button not actually being clicked, or form validation is failing silently

### Scenario C: Backend logs show request arriving
**Problem:** Backend received request, but something went wrong
- **Check Render logs for error messages** (look for 🔴 or ❌ symbols)
- **Common issues:**
  - `Email already registered` - Use different email
  - `Database connection failed` - Check DATABASE_URL env var
  - `Invalid role` - Make sure role is 'customer' or 'maid'

### Scenario D: Backend logs show NO request arriving
**Problem:** Network issue between Vercel and Render
- **Check:**
  - Is CORS_ORIGINS correct? Should be: `https://maidease-two.vercel.app`
  - Is Render backend actually running? Try: https://maidease-api.onrender.com/health
  - Is the API URL correct? Should be: `https://maidease-api.onrender.com/api/v1`

---

## Step 4: Test Endpoints Directly

### 4.1 Test Backend Health
Open in browser: https://maidease-api.onrender.com/health

Should see: `{"status":"healthy"}`

### 4.2 Test Registration via Postman/curl

```bash
curl -X POST "https://maidease-api.onrender.com/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Password123!",
    "full_name": "Test User",
    "phone_number": "9876543210",
    "role": "customer"
  }'
```

**Success response (201):**
```json
{
  "id": "uuid-here",
  "email": "test@example.com",
  "full_name": "Test User",
  "phone_number": "9876543210",
  "role": "customer",
  "is_active": true,
  "created_at": "2024-01-20T10:30:00"
}
```

---

## Recent Logging Enhancements ✨

The following files have been updated with detailed logging:

### Frontend: `src/api/client.js`
- ✅ Logs all API requests with method, URL, headers, and data
- ✅ Logs all API responses with status and data
- ✅ Logs API errors with status and error details
- ✅ 30-second timeout configured to catch hanging requests

### Backend: `app/api/v1/auth.py`
- ✅ Logs registration attempts with email and role
- ✅ Logs successful registrations with user ID
- ✅ Logs registration errors with details

### Backend: `app/services/auth_service.py`
- ✅ Logs checking if user exists
- ✅ Logs user creation with email and role
- ✅ Logs database saving operation
- ✅ Logs successful user registration

### Backend: `app/main.py`
- ✅ Logs startup with DEBUG mode, DATABASE_URL, and CORS origins
- ✅ Logs API routes registration
- ✅ Logs root and health endpoints calls

---

## What to Report Back

Once you've run through these diagnostics, please provide:

1. **Console logs** (copy-paste from browser console):
   - Does `📤 API Request` appear?
   - Does `✅ API Response Success` or `❌ API Response Error` appear?
   - Are there any red error messages?

2. **Network tab info:**
   - Is POST `/auth/register` visible?
   - If yes, what's the Status code?
   - If no, what error appears in console?

3. **Backend logs** (from Render dashboard):
   - Do you see the registration attempt logged?
   - Any error messages?

4. **Form data you're using:**
   - Email, name, role, etc.

This will help identify exactly where the registration flow is breaking! 🔧
