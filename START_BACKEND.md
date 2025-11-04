# Quick Start: Backend Server

## The Issue
The frontend is getting a "NetworkError" because the Django backend server is not running.

## Solution: Start the Backend Server

### Option 1: Quick Start (Recommended)

Open a **new terminal window** and run:

```bash
cd /Applications/MAMP/htdocs/social_trends/backend
source venv/bin/activate
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

**Keep this terminal window open** - the server needs to keep running.

### Option 2: If You Get Errors

1. **Check Python virtual environment:**
   ```bash
   cd /Applications/MAMP/htdocs/social_trends/backend
   source venv/bin/activate
   ```

2. **Install dependencies (if needed):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check .env file exists:**
   ```bash
   ls -la .env
   ```
   If it doesn't exist, create it:
   ```bash
   echo "YOUTUBE_API_KEY=your_api_key_here" > .env
   ```

4. **Run migrations (if needed):**
   ```bash
   python manage.py migrate
   ```

5. **Start server:**
   ```bash
   python manage.py runserver
   ```

## Verify It's Working

Once the server is running, test it:

1. Open browser: `http://localhost:8000/`
   - Should show: `{"status":"ok","project":"social_trends_backend","message":"API is running correctly"}`

2. Test search endpoint: `http://localhost:8000/api/search-channels/?q=test`
   - Should return JSON with results or empty array

## Now Test the Frontend

1. Make sure backend is running (terminal shows server is active)
2. Go to `http://localhost:3000`
3. Type in the YouTube search field
4. Suggestions should now appear!

## Troubleshooting

### "Port 8000 already in use"
```bash
# Find what's using port 8000
lsof -ti:8000

# Kill it (replace PID with the number from above)
kill -9 <PID>

# Or use a different port
python manage.py runserver 8001
```
Then update `frontend/src/components/ChannelInputForm.jsx` line 54 to use port 8001.

### "YOUTUBE_API_KEY not found"
Make sure `.env` file exists in the `backend/` directory with:
```
YOUTUBE_API_KEY=your_actual_api_key_here
```

### Still getting NetworkError?
1. Check backend terminal for errors
2. Check browser console (F12) for detailed error messages
3. Verify backend is accessible: `curl http://localhost:8000/`

