# How to Increase YouTube API Quota

This guide walks you through requesting a quota increase for the YouTube Data API v3.

## Current Default Quota

- **Default Daily Quota**: 10,000 units per day
- **Resets**: At midnight Pacific Time (PST/PDT)
- **Your Current Status**: Exceeded (all API calls failing)

## Step-by-Step Instructions

### Step 1: Go to Google Cloud Console

1. Open your browser and go to: https://console.cloud.google.com/
2. Make sure you're signed in with the Google account that owns the API key you're using

### Step 2: Select Your Project

1. Click on the project dropdown at the top of the page
2. Select the project that contains your YouTube Data API key
   - If you don't know which project, check your `.env` file for the API key, then search for it in the console

### Step 3: Navigate to APIs & Services → Quotas

1. In the left sidebar, click **"APIs & Services"**
2. Click **"Quotas"** (you may need to click "Dashboard" first, then "Quotas")

### Step 4: Find YouTube Data API v3

1. In the search/filter box at the top, type: **"YouTube Data API v3"**
2. Or scroll down to find it in the list
3. Look for quota metrics like:
   - "Queries per day"
   - "Queries per 100 seconds per user"
   - "Queries per 100 seconds"

### Step 5: Request Quota Increase

1. **Select the quota metric** you want to increase (usually "Queries per day")
2. Click the checkbox next to it
3. Click the **"EDIT QUOTAS"** button at the top (or "Request increase" link)
4. A form will appear

### Step 6: Fill Out the Request Form

You'll need to provide:

1. **Requested Quota Amount**
   - Recommended: **50,000** or **100,000** units per day
   - For heavy usage: **200,000** units per day
   - For very heavy usage: **1,000,000** units per day
   - **Note**: They may approve less than requested

2. **Justification** (This is important! Use something like):
   ```
   I'm building a YouTube channel analysis tool that needs to fetch video 
   statistics and metadata from multiple channels. The default 10,000 
   units per day is insufficient for analyzing 10+ channels with their 
   videos and shorts. I need approximately 50,000 units per day to:
   - Fetch channel information
   - Retrieve video lists from channels
   - Get video statistics (views, likes, comments)
   - Support multiple users analyzing channels
   
   This is for personal/development use and I understand the quota 
   limits and costs.
   ```

3. **Your Contact Information**
   - Name, email, phone (usually pre-filled)

### Step 7: Submit and Wait

1. Click **"Submit Request"** or **"Submit"**
2. You'll receive a confirmation email
3. **Processing Time**: Usually 24-48 hours, but can take up to 5 business days
4. Google will email you when:
   - Your request is approved
   - Your request needs more information
   - Your request is denied (rare, usually asks for clarification instead)

## Alternative: Multiple API Keys (Not Recommended)

If quota increase is denied or taking too long:

1. Create additional Google Cloud projects
2. Create new API keys in each project
3. Rotate between them in your application
4. **Limitations**:
   - Each project has its own 10,000 unit limit
   - More complex to manage
   - Not a sustainable solution

## Understanding Quota Costs

Different API calls cost different amounts:

| API Method | Cost (Units) |
|------------|--------------|
| `channels.list` | 1 unit |
| `playlistItems.list` | 1 unit |
| `videos.list` | 1 unit |
| `search.list` | 100 units ⚠️ **Very expensive!** |

**For your app:**
- Each channel analysis uses approximately:
  - 1-2 units: Get channel info
  - 1 unit per page: Get playlist items (up to 50 videos per page)
  - 1 unit per batch: Get video statistics (up to 50 videos per batch)
  - **100 units per call**: If using Search API (currently blocked for you)

**Example calculation for 10 channels:**
- 10 channels × (2 + 5 playlist calls + 3 video stat calls) = ~100 units
- If Search API works: 10 channels × 100 units = 1,000 units
- **Total for 10 channels**: ~1,100 units

With 10,000 units, you can analyze about **9 batches of 10 channels** per day.

## Tips for Approval

1. **Be Specific**: Explain exactly what you're building and why you need more quota
2. **Be Honest**: Don't exaggerate your needs
3. **Professional Tone**: Write clearly and professionally
4. **Show Usage**: If you can, mention your current usage patterns
5. **Educational/Personal Projects**: Often approved faster than commercial use

## What Happens After Approval?

1. You'll receive an email notification
2. Your quota limit increases immediately
3. The new limit appears in the Quotas page
4. You can start using the additional quota right away
5. **Note**: Quota still resets daily at midnight Pacific Time

## Checking Your Quota Usage

1. Go to **APIs & Services → Dashboard**
2. Find "YouTube Data API v3"
3. Click on it to see:
   - Current quota usage
   - Quota limit
   - Usage graph

## If Request is Denied

1. **Resubmit with more detail**: Provide more specific information
2. **Lower your request**: Try requesting 25,000 instead of 100,000
3. **Contact Support**: Use the "Help" button in Google Cloud Console
4. **Optimize your code**: Reduce API calls (which we've already done)

## Quick Links

- **Google Cloud Console**: https://console.cloud.google.com/
- **YouTube API Quota Documentation**: https://developers.google.com/youtube/v3/getting-started#quota
- **API Quota Calculator**: https://developers.google.com/youtube/v3/determine_quota_cost

## Questions?

If you run into issues:
1. Check Google Cloud Console → Support
2. Review YouTube API documentation
3. Check the error messages in your application logs

---

**Remember**: While waiting for quota approval, you can still use the app with channel ID URLs (they use fewer API units than @handle URLs).

