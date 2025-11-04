# Frontend Setup Guide

## Quick Start

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Start the development server:**
```bash
npm start
```

The app will open at `http://localhost:3000`

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## Configuration

The frontend expects the backend to run on `http://localhost:8000`.

To change this, edit `src/App.jsx` and update the fetch URL:

```javascript
const response = await fetch('http://your-backend-url/api/analyze-channels/', {
  ...
});
```

