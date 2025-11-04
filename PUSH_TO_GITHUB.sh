#!/bin/bash

# Script to push Social Competitor Analyser to GitHub
# Usage: ./PUSH_TO_GITHUB.sh YOUR_GITHUB_USERNAME

if [ -z "$1" ]; then
    echo "❌ Error: Please provide your GitHub username"
    echo "Usage: ./PUSH_TO_GITHUB.sh YOUR_GITHUB_USERNAME"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME="Social-Competitor-Analyser"

echo "🚀 Preparing to push to GitHub..."
echo "Repository: $REPO_NAME"
echo "Username: $GITHUB_USERNAME"
echo ""

# Check if remote already exists
if git remote | grep -q "^origin$"; then
    echo "⚠️  Remote 'origin' already exists. Updating..."
    git remote set-url origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
else
    echo "➕ Adding remote repository..."
    git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
fi

echo ""
echo "📋 Current status:"
git remote -v
echo ""

echo "⚠️  IMPORTANT: Make sure you've created the repository on GitHub first!"
echo "   Go to: https://github.com/new"
echo "   Repository name: $REPO_NAME"
echo "   DO NOT initialize with README, .gitignore, or license"
echo ""
read -p "Have you created the repository on GitHub? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Please create the repository on GitHub first, then run this script again."
    exit 1
fi

echo "📤 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "   Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Go to your repository on GitHub"
    echo "   2. Add topics/tags: youtube-api, auto-suggestion-search, social-media-analytics"
    echo "   3. Update repository description"
else
    echo ""
    echo "❌ Push failed. Please check:"
    echo "   1. Repository exists on GitHub"
    echo "   2. You have push access"
    echo "   3. Your GitHub credentials are correct"
fi

