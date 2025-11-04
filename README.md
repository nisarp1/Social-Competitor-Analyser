# Social Competitor Analyser

A comprehensive social media analytics platform for analyzing YouTube and Instagram channels. Features intelligent video ranking, trending detection, live stream monitoring, and competitor analysis.

## 🏷️ Tags

- **YouTube API with Auto Suggestion Search** - Intelligent channel search with real-time suggestions
- Social Media Analytics
- Competitor Analysis
- YouTube Analytics
- Instagram Analytics
- Live Stream Detection
- Trending Content Analysis

## ✨ Features

### YouTube Analysis
- **Auto-suggestion Search** - Search for YouTube channels with intelligent autocomplete suggestions
- **Video Ranking** - Rank videos by popularity, views, and engagement
- **Live Stream Detection** - Automatically detect and monitor 24/7 live streams
- **Trending Detection** - Identify trending videos from the last 3 hours
- **Shorts Analysis** - Separate analysis for YouTube Shorts
- **Multi-channel Comparison** - Analyze up to 10 channels simultaneously

### Instagram Analysis
- **Page Analytics** - Analyze Instagram pages and posts
- **Reels & Videos** - Separate tracking for Reels and Videos
- **Content Ranking** - Rank posts by engagement and popularity

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- YouTube Data API v3 Key
- Django 4.2+
- React 18+

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your YouTube API key
echo "YOUTUBE_API_KEY=your_api_key_here" > .env

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The app will be available at `http://localhost:3000`

## 📁 Project Structure

```
social_trends/
├── backend/              # Django REST API
│   ├── api/             # API app
│   │   ├── services/    # YouTube & Instagram services
│   │   ├── views.py     # API endpoints
│   │   └── urls.py      # URL routing
│   └── social_trends_backend/  # Django project settings
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   └── App.jsx      # Main app component
│   └── public/
└── README.md
```

## 🔑 API Configuration

### YouTube API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project or select existing
3. Enable "YouTube Data API v3"
4. Create API credentials
5. Add your API key to `backend/.env`:
   ```
   YOUTUBE_API_KEY=your_api_key_here
   ```

### Required YouTube API Permissions

- YouTube Data API v3 (Search, Channels, Videos, Playlists)
- Ensure Search API is enabled in your API key restrictions

## 🎯 Key Features Explained

### Auto-Suggestion Search
- Real-time channel search with debounced API calls
- Material-UI Autocomplete component
- Shows channel thumbnails, subscriber counts, and descriptions
- Supports multiple channel selection (up to 10)

### Live Stream Detection
- Automatically detects 24/7 live streams
- Searches for active broadcasts using `eventType='live'`
- Shows only the live stream with most concurrent viewers when multiple exist
- Handles live streams even when temporarily offline

### Trending Detection
- Identifies videos published in the last 3 hours
- Calculates trending score based on views per hour
- Ranks trending content separately from regular videos

## 📊 API Endpoints

### YouTube
- `POST /api/analyze-channels/` - Analyze YouTube channels
- `GET /api/search-channels/?q=query` - Search channels with autocomplete
- `GET /api/quota-status/` - Check YouTube API quota status

### Instagram
- `POST /api/analyze-instagram/` - Analyze Instagram pages
- `GET /api/search-instagram/?q=query` - Search Instagram pages

## 🔧 Configuration

### Enable Search API (Optional)
Edit `backend/social_trends_backend/settings.py`:
```python
USE_SEARCH_API = True  # Enables search API (costs 100 quota units per channel)
```

### CORS Settings
CORS is configured to allow requests from:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:5173` (Vite)

## 📝 Usage Examples

### Analyze YouTube Channels
```javascript
POST http://localhost:8000/api/analyze-channels/
{
  "channel_urls": [
    "https://www.youtube.com/@channel1",
    "https://www.youtube.com/@channel2"
  ],
  "real_time_trending": false,
  "real_time_live": false
}
```

### Search Channels
```javascript
GET http://localhost:8000/api/search-channels/?q=tech&max_results=10
```

## 🛠️ Technologies Used

### Backend
- Django 4.2
- Django REST Framework
- Google API Python Client (YouTube Data API v3)
- BeautifulSoup4 (Web scraping fallback)
- django-cors-headers

### Frontend
- React 18
- Material-UI (MUI)
- Axios/Fetch API

## 📄 License

This project is open source and available for use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Made with ❤️ for social media analytics**
