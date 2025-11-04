# Backend Setup Guide

## Quick Start

1. **Create and activate virtual environment:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create `.env` file:**
```bash
cp .env.example .env
# Edit .env and add your YouTube API key:
# YOUTUBE_API_KEY=your_key_here
```

4. **Run migrations:**
```bash
python manage.py migrate
```

5. **Start the server:**
```bash
python manage.py runserver
```

Server will run on `http://localhost:8000`

## Getting a YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable "YouTube Data API v3"
4. Go to "Credentials" and create an API key
5. Copy the key to your `.env` file

## API Endpoint

**POST** `http://localhost:8000/api/analyze-channels/`

**Request:**
```json
{
  "channel_urls": [
    "https://www.youtube.com/@channel1",
    "https://www.youtube.com/@channel2"
  ]
}
```

**Response:**
```json
{
  "results": [...],
  "errors": [...],
  "total_channels_processed": 2,
  "total_channels_failed": 0
}
```

