# Quick Fix for Current Issue

## Problem
- `http://localhost:8000/` shows `pavilion_gemini` (wrong project)
- `http://localhost:3000/` shows another app (port conflict)

## Step-by-Step Solution

### Step 1: Stop Current Servers

**Stop Django (port 8000):**
```bash
# In terminal where Django is running, press Ctrl+C
# OR find and kill the process:
lsof -ti:8000 | xargs kill -9
```

**Stop React (port 3000) - if needed:**
```bash
lsof -ti:3000 | xargs kill -9
```

### Step 2: Navigate to Correct Backend

```bash
cd /Applications/MAMP/htdocs/social_trends/backend
```

### Step 3: Activate Virtual Environment

```bash
# If virtual environment doesn't exist, create it first:
python3 -m venv venv

# Then activate:
source venv/bin/activate
```

### Step 4: Install Dependencies (if not done)

```bash
pip install -r requirements.txt
```

### Step 5: Create .env File (if not exists)

```bash
echo "YOUTUBE_API_KEY=your_key_here" > .env
```

**Important:** Replace `your_key_here` with your actual YouTube API key!

### Step 6: Run Migrations

```bash
python manage.py runserver
```

Actually wait, run migrations first:
```bash
python manage.py migrate
```

### Step 7: Start Django Server

```bash
python manage.py runserver
```

**You should see:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

**NOT:**
```
Using URLconf defined in pavilion_gemini.urls  ❌ (wrong!)
```

**BUT:**
```
Using URLconf defined in social_trends_backend.urls  ✅ (correct!)
```

### Step 8: Test Backend API

Open a new terminal and test:
```bash
curl http://localhost:8000/api/analyze-channels/
```

You should get a response (probably a 400 or 405 error is fine - means endpoint exists)

### Step 9: Start Frontend (in new terminal)

```bash
cd /Applications/MAMP/htdocs/social_trends/frontend

# Install dependencies (first time only):
npm install

# Start React app:
npm start
```

If port 3000 is still in use, React will ask to use 3001 - say yes.

### Step 10: Access the App

- Frontend: `http://localhost:3000` (or 3001 if prompted)
- Backend API: `http://localhost:8000/api/analyze-channels/`

## Verify It's Working

1. Visit `http://localhost:8000/admin/` - should show Django admin (not pavilion_gemini)
2. Visit `http://localhost:3000/` - should show "Social Trends" app
3. Try pasting a YouTube channel URL and clicking "Analyze Channels"

## Still Having Issues?

Check `TROUBLESHOOTING.md` for more detailed solutions.

