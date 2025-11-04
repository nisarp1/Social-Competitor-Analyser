# Channel IDs for Direct Use

Since Search API is blocked/quota exceeded, you can use these channel ID URLs directly:

## Your Channels

1. **@mrzthoppi**
   - Channel ID: `UC0XCrZT2-n_Yyj4gAePKekg`
   - Direct URL: `https://www.youtube.com/channel/UC0XCrZT2-n_Yyj4gAePKekg`
   - Instead of: `https://www.youtube.com/@mrzthoppi`

2. **@CallMeShazzamTECH**
   - Channel ID: `UC9MQp8a5uhaIosZPHaoqEXQ`
   - Direct URL: `https://www.youtube.com/channel/UC9MQp8a5uhaIosZPHaoqEXQ`
   - Instead of: `https://www.youtube.com/@CallMeShazzamTECH`

3. **@hanaaaneyy**
   - Channel ID: `UCBoLezq04tdd45n5gG4dOng`
   - Direct URL: `https://www.youtube.com/channel/UCBoLezq04tdd45n5gG4dOng`
   - Instead of: `https://www.youtube.com/@hanaaaneyy`

## How to Use

Instead of:
```
https://www.youtube.com/@mrzthoppi
```

Use:
```
https://www.youtube.com/channel/UC0XCrZT2-n_Yyj4gAePKekg
```

## Finding Channel IDs

If you need to find channel IDs for other channels:

1. Visit the channel page on YouTube
2. View page source (Ctrl+U / Cmd+U)
3. Search for `"channelId":"`
4. Copy the ID (starts with `UC`)

Or use online tools like:
- https://commentpicker.com/youtube-channel-id.php

## Why This Works

Channel ID URLs (`/channel/UCxxxxx`) don't require the Search API - they work directly with the channels API, which is still available even when Search API is blocked/quota exceeded.

