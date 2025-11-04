# Troubleshooting Guide

## Issue: Wrong Django Project Running (pavilion_gemini instead of social_trends_backend)

### Solution 1: Stop the Current Server

1. **Find and stop the running Django server:**
   - Press `Ctrl+C` in the terminal where the server is running, OR
   - Find the process and kill it:
   ```bash
   # Find the process
   lsof -ti:8000
   # Kill it (replace PID with the number from above)
   kill -9 <PID>
   ```

2. **Navigate to the correct directory:**
   ```bash
   cd /Applications/MAMP/htdocs/social_trends/backend
   ```

3. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Start the correct server:**
   ```bash
   python manage.py runserver
   ```

### Solution 2: Use a Different Port

If you want to keep the other project running, use port 8001:

```bash
python manage.py runserver 8001
```

Then update `frontend/src/App.jsx` to point to port 8001:
```javascript
const response = await fetch('http://localhost:8001/api/analyze-channels/', {
  ...
});
```

## Issue: Port 3000 Already in Use (Another React App)

### Solution 1: Stop the Other App

```bash
# Find process on port 3000
lsof -ti:3000
# Kill it
kill -9 <PID>
```

### Solution 2: Use a Different Port

The React app will prompt you to use a different port, or you can specify it:

```bash
PORT=3001 npm start
```

Then access at `http://localhost:3001`

## Verify You're Running the Correct Server

1. **Check the Django server:**
   - Visit `http://localhost:8000/api/analyze-channels/`
   - You should see an error about POST method (that's expected - it means the endpoint exists)
   - If you see "pavilion_gemini" errors, you're running the wrong server

2. **Check Django settings:**
   - The terminal should show: `Starting development server at http://127.0.0.1:8000/`
   - It should NOT mention "pavilion_gemini"

3. **Verify the correct project structure:**
   ```bash
   # In backend directory, check:
   ls social_trends_backend/
   # Should show: __init__.py, settings.py, urls.py, wsgi.py, asgi.py
   
   # Check if api app exists:
   ls api/
   # Should show: __init__.py, apps.py, urls.py, views.py, services/
   ```

## Common Issues

### "ModuleNotFoundError: No module named 'api'"
- Make sure you're running from the `backend/` directory
- Check that `api/` folder exists in `backend/`
- Verify `INSTALLED_APPS` in `settings.py` includes `'api'`

### "YOUTUBE_API_KEY not found"
- Create `.env` file in `backend/` directory
- Add: `YOUTUBE_API_KEY=your_actual_key_here`
- Make sure `python-dotenv` is installed: `pip install python-dotenv`

### CORS Errors in Browser
- Make sure `django-cors-headers` is installed
- Verify `CORS_ALLOWED_ORIGINS` in `settings.py` includes your frontend URL
- Check that `corsheaders` is in `INSTALLED_APPS` and `MIDDLEWARE`

### API Returns 404
- Verify URL pattern: should be `/api/analyze-channels/`
- Check that you're sending POST request (not GET)
- Ensure Django server is actually running

