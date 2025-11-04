# GitHub Repository Setup Instructions

## Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `Social-Competitor-Analyser`
   - **Description**: `YouTube API with auto suggestion search - Social media analytics platform for analyzing YouTube and Instagram channels`
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**

## Step 2: Push to GitHub

After creating the repository, GitHub will show you commands. Run these in your terminal:

```bash
cd /Applications/MAMP/htdocs/social_trends

# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/Social-Competitor-Analyser.git

# Push to GitHub
git push -u origin main
```

## Step 3: Add Tags/Topics

After pushing, go to your repository on GitHub and:

1. Click on the repository
2. Click the **gear icon** (⚙️) next to "About" on the right side
3. Add these topics/tags:
   - `youtube-api`
   - `auto-suggestion-search`
   - `social-media-analytics`
   - `competitor-analysis`
   - `youtube-analytics`
   - `instagram-analytics`
   - `live-stream-detection`
   - `trending-content`
   - `django`
   - `react`
   - `python`
   - `javascript`

## Step 4: Update Repository Description

In the same "About" section:
- **Description**: `YouTube API with auto suggestion search - Social media competitor analysis platform`

## Alternative: Using SSH (if you have SSH keys set up)

```bash
git remote add origin git@github.com:YOUR_USERNAME/Social-Competitor-Analyser.git
git push -u origin main
```

## Quick Command Reference

If you need to check your remote:
```bash
git remote -v
```

If you need to update the remote URL:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/Social-Competitor-Analyser.git
```

## Your Repository is Ready!

Once pushed, your repository will be available at:
`https://github.com/YOUR_USERNAME/Social-Competitor-Analyser`

