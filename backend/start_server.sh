#!/bin/bash
# Script to start the Django server for social_trends_backend

echo "Starting Social Trends Backend Server..."
echo "Make sure you're in the backend directory and have activated your virtual environment!"
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: Virtual environment not detected!"
    echo "Please activate it first: source venv/bin/activate"
    echo ""
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create it with: echo 'YOUTUBE_API_KEY=your_key' > .env"
    echo ""
fi

# Run the server
python manage.py runserver

