# YouTube API Key Setup Instructions

## Current Issue

The API key is configured but getting a **403 Forbidden** error:
```
"Requests to this API youtube method youtube.api.v3.V3DataChannelService.List are blocked."
```

## Solution: Enable YouTube Data API v3

Your API key needs to have the YouTube Data API v3 enabled. Follow these steps:

### Step 1: Go to Google Cloud Console
Visit: https://console.cloud.google.com/

### Step 2: Select Your Project
- Make sure you're in the correct project where your API key was created
- If you don't have a project, create one

### Step 3: Enable YouTube Data API v3
1. Go to **APIs & Services** → **Library**
2. Search for "YouTube Data API v3"
3. Click on it
4. Click **Enable** button
5. Wait for it to enable (may take a minute)

### Step 4: Check API Key Restrictions (Optional but Recommended)
1. Go to **APIs & Services** → **Credentials**
2. Find your API key: `AIzaSyChjTtomXqAmiUxU0pWXRELF2wm4AEi5j4`
3. Click on it to edit
4. Under **API restrictions**:
   - Either select **Don't restrict key** (for testing)
   - OR select **Restrict key** and add "YouTube Data API v3" to allowed APIs
5. Click **Save**

### Step 5: Verify
After enabling, wait 1-2 minutes for changes to propagate, then try your app again.

## Alternative: Create a New API Key

If you prefer to create a fresh API key:

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **API Key**
3. Enable **YouTube Data API v3** first (Step 3 above)
4. Copy the new key
5. Update `backend/.env` file with the new key

## Testing

After enabling the API, test with:
```bash
curl -X POST http://localhost:8000/api/analyze-channels/ \
  -H "Content-Type: application/json" \
  -d '{"channel_urls": ["https://www.youtube.com/channel/UCBJycsmduvYEL83R_U4JriQ"]}'
```

You should get video data instead of a 403 error.

