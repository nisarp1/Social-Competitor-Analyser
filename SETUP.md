# Quick Setup Guide

Follow these steps to get the application running:

## 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your YouTube API key
echo "YOUTUBE_API_KEY=your_key_here" > .env

# Run migrations
python manage.py migrate

# Start server (runs on http://localhost:8000)
python manage.py runserver
```

## 2. Frontend Setup (in a new terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start development server (runs on http://localhost:3000)
npm start
```

## 3. Get YouTube API Key

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select existing)
3. Navigate to "APIs & Services" > "Library"
4. Search for "YouTube Data API v3" and enable it
5. Go to "Credentials" > "Create Credentials" > "API Key"
6. Copy the key and paste it in `backend/.env` file

## 4. Usage

1. Open `http://localhost:3000` in your browser
2. Paste YouTube channel URLs (one per line)
3. Click "Analyze Channels"
4. View ranked results!

## Troubleshooting

### Backend errors
- Make sure `.env` file exists in `backend/` directory
- Verify `YOUTUBE_API_KEY` is set correctly
- Check that Django server is running on port 8000

### Frontend errors
- Make sure backend is running first
- Check browser console for CORS errors
- Verify `http://localhost:8000` is accessible

### API Quota Issues
- YouTube API has daily quota limits (default: 10,000 units)
- Each channel analysis uses ~3-5 units
- Monitor usage in Google Cloud Console

