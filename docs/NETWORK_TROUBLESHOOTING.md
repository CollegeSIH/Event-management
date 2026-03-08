# EventHub Network Error Troubleshooting

## Why You're Getting "Network Error"

The "Network error. Please try again." message appears when your frontend (HTML file) cannot connect to the backend server running on `http://localhost:5000`.

## Common Causes & Solutions

### 1. Backend Server Not Running
**Symptoms:** Network error on all API calls
**Solution:**
```bash
cd backend
python app.py
```
Keep this terminal window open while using the app.

### 2. Wrong Way to Open HTML File
**❌ Don't do this:** Double-click `index.html` in File Explorer
**✅ Do this instead:**
- Open VS Code
- Right-click `index.html` → "Open with Live Server" (if you have the extension)
- Or use a local web server:
  ```bash
  # Install http-server globally (optional)
  npm install -g http-server

  # Serve the current directory
  http-server -p 8080
  ```
  Then open: `http://localhost:8080`

### 3. Browser Security Blocking Requests
**Symptoms:** CORS errors in browser console
**Solution:** Use a proper web server (see #2) instead of opening file directly

### 4. Port Already in Use
**Symptoms:** Backend fails to start with "Address already in use"
**Solution:**
```bash
# Kill process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change port in app.py
```

## How to Test if Everything Works

### Step 1: Start Backend
```bash
cd backend
python app.py
```
You should see: `* Running on http://127.0.0.1:5000/`

### Step 2: Test Backend Directly
```bash
# Test login
curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d '{"email":"admin@eventhub.com","password":"admin123"}'

# Test events (should return 401 - unauthorized)
curl http://localhost:5000/events
```

### Step 3: Open Frontend Properly
- Use Live Server extension in VS Code, OR
- Use `http-server` as described above, OR
- Open browser and go to: `http://localhost:8080` (if using http-server)

### Step 4: Check Browser Console
- Press F12 → Console tab
- Look for debug messages starting with 🔄, 📡, ✅, ❌, 🚨
- These will show exactly what's happening with API calls

## Debug Messages You'll See

- `🔄 Attempting login to backend...` - Frontend trying to connect
- `📡 Login response status: 200` - Success
- `🚨 Network error during login:` - Connection failed
- Similar messages for signup/verification

## Quick Fix Checklist

1. ✅ Backend server running (`cd backend && python app.py`)
2. ✅ HTML opened via web server (not file://)
3. ✅ Browser console shows successful connections
4. ✅ No firewall blocking localhost:5000

## Still Having Issues?

Run this test script:
```bash
python -c "
import requests
try:
    r = requests.get('http://localhost:5000/events')
    print('Backend: RUNNING' if r.status_code in [200,401] else 'NOT RUNNING')
except:
    print('Backend: NOT RUNNING - Start with: cd backend && python app.py')
"
```

If backend is running but you still get network errors, the issue is with how you're opening the HTML file.