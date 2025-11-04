# Critical: YouTube API Permissions Issue

## Current Problem

Your API key is **blocking all search operations**. All methods that use the `search` API are returning:
```
403 Forbidden: "Requests to this API youtube method youtube.api.v3.V3DataSearchService.List are blocked."
```

## Why This Happens

The YouTube Data API v3 has multiple services:
- ✅ `channels().list()` - May work (for direct channel IDs)
- ❌ `search().list()` - **BLOCKED** (needed for @handle URLs)
- ❌ `videos().list()` - May be blocked
- ❌ Other methods may also be blocked

## Solution: Enable All Required APIs

### Step 1: Go to Google Cloud Console
Visit: https://console.cloud.google.com/

### Step 2: Enable Required APIs
Go to **APIs & Services** → **Library** and enable:

1. **YouTube Data API v3** ⚠️ **CRITICAL**
   - Search for "YouTube Data API v3"
   - Click **Enable**

2. **Check All YouTube APIs** (optional but recommended):
   - YouTube Analytics API
   - YouTube Reporting API

### Step 3: Remove API Key Restrictions (Temporary)

1. Go to **APIs & Services** → **Credentials**
2. Click your API key: `AIzaSyChjTtomXqAmiUxU0pWXRELF2wm4AEi5j4`
3. Under **API restrictions**:
   - Select **"Don't restrict key"** (for testing)
   - OR if you want restrictions, make sure **"YouTube Data API v3"** is in the allowed list
4. Click **Save**

### Step 4: Check Quotas
1. Go to **APIs & Services** → **Dashboard**
2. Find "YouTube Data API v3"
3. Check **Quotas** tab
4. Make sure your daily quota is not exhausted (default: 10,000 units/day)

### Step 5: Wait and Test
- Wait 1-2 minutes for changes to propagate
- Restart your Django server
- Try analyzing channels again

## Alternative: Use Channel ID URLs

While you fix the API permissions, you can use channel IDs directly:

Instead of:
- ❌ `https://www.youtube.com/@CallMeShazzamTECH`

Use:
- ✅ `https://www.youtube.com/channel/UCxxxxxxxxxxxxx`

### How to Get Channel IDs:

1. Go to the channel page (e.g., `youtube.com/@CallMeShazzamTECH`)
2. View page source (Ctrl+U / Cmd+U)
3. Search for `"channelId":"`
4. Copy the channel ID (starts with `UC`)

Or use online tools like:
- https://commentpicker.com/youtube-channel-id.php

## Testing After Fix

Test with:
```bash
curl -X POST http://localhost:8000/api/analyze-channels/ \
  -H "Content-Type: application/json" \
  -d '{"channel_urls": ["https://www.youtube.com/@mkbhd"]}'
```

Should return video data, not 403 errors.

## Summary

The issue is **NOT with the code** - it's that your API key doesn't have permission to use the YouTube Search API. You must:
1. ✅ Enable YouTube Data API v3
2. ✅ Remove or properly configure API restrictions
3. ✅ Wait for changes to propagate
4. ✅ Test again

Once permissions are correct, @handle URLs will work!

