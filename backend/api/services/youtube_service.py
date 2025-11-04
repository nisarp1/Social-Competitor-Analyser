"""
YouTube Service Layer
Handles all YouTube Data API interactions and data processing.
"""
import re
from typing import List, Dict, Optional
from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build
from django.conf import settings


class YouTubeService:
    """Service class for interacting with YouTube Data API v3"""
    
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        if not self.api_key or self.api_key == 'your_youtube_api_key_here':
            raise ValueError("YOUTUBE_API_KEY not found or not configured. Please add your YouTube API key to the .env file.")
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def extract_channel_id(self, channel_url: str) -> Optional[str]:
        """
        Extract channel ID from various YouTube channel URL formats.
        Supports:
        - https://www.youtube.com/channel/UCxxxxx
        - https://www.youtube.com/c/ChannelName
        - https://www.youtube.com/@ChannelHandle
        - https://youtube.com/@ChannelHandle
        """
        # Pattern 1: /channel/UCxxxxx
        match = re.search(r'/channel/([a-zA-Z0-9_-]+)', channel_url)
        if match:
            return match.group(1)
        
        # Pattern 2: /c/ChannelName or /user/ChannelName
        match = re.search(r'/(?:c|user)/([a-zA-Z0-9_-]+)', channel_url)
        if match:
            return self._get_channel_id_from_username(match.group(1))
        
        # Pattern 3: /@ChannelHandle
        match = re.search(r'/@([a-zA-Z0-9_-]+)', channel_url)
        if match:
            channel_id = self._get_channel_id_from_handle(match.group(1))
            if channel_id:
                return channel_id
            # If search API fails, return None (will be handled by caller)
        
        # If it's already just a channel ID
        if re.match(r'^UC[a-zA-Z0-9_-]{22}$', channel_url):
            return channel_url
        
        return None
    
    def _get_channel_id_from_username(self, username: str) -> Optional[str]:
        """Get channel ID from username"""
        try:
            request = self.youtube.channels().list(
                part='id',
                forUsername=username
            )
            response = request.execute()
            if response.get('items'):
                return response['items'][0]['id']
        except Exception:
            pass
        return None
    
    def _get_channel_id_from_handle(self, handle: str) -> Optional[str]:
        """Get channel ID from channel handle (e.g., @ChannelName)"""
        # First, try web scraping (no quota cost)
        try:
            from api.services.youtube_scraper import YouTubeScraper
            scraper = YouTubeScraper()
            url = f"https://www.youtube.com/@{handle}"
            channel_id = scraper.extract_channel_id_from_url(url)
            if channel_id:
                print(f"✅ Extracted channel ID {channel_id} from @{handle} using web scraping")
                return channel_id
        except Exception as e:
            print(f"Web scraping failed for @{handle}: {e}")
        
        # Fallback to Search API (if enabled and available)
        from django.conf import settings
        use_search_api = getattr(settings, 'USE_SEARCH_API', False)
        if not use_search_api:
            print(f"⚠️ Search API disabled. Web scraping failed for @{handle}. Please use channel ID URL format.")
            return None
        
        # Method 2: Try search API with exact handle URL format
        try:
            # Search for the exact URL pattern
            search_query = f"youtube.com/@{handle}"
            request = self.youtube.search().list(
                part='snippet',
                q=search_query,
                type='channel',
                maxResults=20
            )
            response = request.execute()
            if response.get('items'):
                # Look for exact match - check customUrl field
                for item in response['items']:
                    snippet = item.get('snippet', {})
                    custom_url = snippet.get('customUrl', '').lower()
                    channel_id = snippet.get('channelId')
                    
                    # Check if customUrl exactly matches the handle
                    if custom_url:
                        # Remove @ and compare
                        clean_custom_url = custom_url.replace('@', '').replace('youtube.com/', '').replace('c/', '')
                        if handle.lower() == clean_custom_url or f"@{handle.lower()}" == custom_url:
                            return channel_id
                
                # If no exact match, check title similarity and return first result
                # Sometimes the first result is correct even if customUrl doesn't match exactly
                best_match = None
                for item in response['items']:
                    snippet = item.get('snippet', {})
                    title = snippet.get('title', '').lower()
                    channel_id = snippet.get('channelId')
                    
                    # If title contains handle, it's likely the right channel
                    if handle.lower() in title:
                        return channel_id
                    if not best_match:
                        best_match = channel_id
                
                # Return first result as fallback
                if best_match:
                    return best_match
        except Exception as e:
            error_msg = str(e)
            if '403' in error_msg or 'blocked' in error_msg.lower() or 'quota' in error_msg.lower():
                print(f"Search API unavailable for handle extraction: {error_msg[:100]}")
                # Don't raise, continue to next method
            else:
                print(f"Error in handle search with URL pattern: {e}")
        
        # Method 3: Try search with @ prefix only
        try:
            search_query = f"@{handle}"
            request = self.youtube.search().list(
                part='snippet',
                q=search_query,
                type='channel',
                maxResults=10
            )
            response = request.execute()
            if response.get('items'):
                for item in response['items']:
                    snippet = item.get('snippet', {})
                    custom_url = snippet.get('customUrl', '').lower()
                    channel_id = snippet.get('channelId')
                    
                    if custom_url and (handle.lower() in custom_url or f"@{handle.lower()}" == custom_url):
                        return channel_id
                
                # Return first result
                if response['items']:
                    return response['items'][0]['snippet']['channelId']
        except Exception as e:
            error_msg = str(e)
            if '403' in error_msg or 'blocked' in error_msg.lower() or 'quota' in error_msg.lower():
                print(f"Search API unavailable (blocked/quota): {error_msg[:100]}")
                # Don't raise, continue to next method
            else:
                print(f"Error in handle search with @ prefix: {e}")
        
        # Method 4: Try search without @ prefix
        try:
            request = self.youtube.search().list(
                part='snippet',
                q=handle,
                type='channel',
                maxResults=10
            )
            response = request.execute()
            if response.get('items'):
                for item in response['items']:
                    snippet = item.get('snippet', {})
                    custom_url = snippet.get('customUrl', '').lower()
                    channel_id = snippet.get('channelId')
                    title = snippet.get('title', '').lower()
                    
                    # Prefer exact matches
                    if custom_url and handle.lower() in custom_url:
                        return channel_id
                    # Check title
                    if handle.lower() in title:
                        return channel_id
                
                # Fallback to first result
                if response['items']:
                    return response['items'][0]['snippet']['channelId']
        except Exception as e:
            error_msg = str(e)
            if '403' in error_msg or 'blocked' in error_msg.lower() or 'quota' in error_msg.lower():
                print(f"Search API unavailable (blocked/quota): {error_msg[:100]}")
                # Don't raise, just return None
            else:
                print(f"Error in handle search without @ prefix: {e}")
        
        return None
    
    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """
        Get channel information including name, description, statistics, and uploads playlist ID.
        
        Available parts in YouTube Data API v3 channels.list:
        - snippet: title (channel name), description, thumbnails, customUrl, publishedAt, country
        - contentDetails: relatedPlaylists (uploads, likes, favorites, watchHistory, watchLater)
        - statistics: viewCount, subscriberCount, videoCount, hiddenSubscriberCount
        - brandingSettings: channel, watch, image
        - topicDetails: topicIds, relevantTopicIds
        - status: privacyStatus, isLinked, longUploadsStatus, madeForKids
        - snippet.localized: localized title and description
        """
        try:
            request = self.youtube.channels().list(
                part='snippet,contentDetails,statistics',
                id=channel_id
            )
            response = request.execute()
            
            if not response.get('items'):
                raise ValueError(f"Channel {channel_id} not found or inaccessible")
            
            channel_data = response['items'][0]
            snippet = channel_data.get('snippet', {})
            content_details = channel_data.get('contentDetails', {})
            statistics = channel_data.get('statistics', {})
            related_playlists = content_details.get('relatedPlaylists', {})
            
            # Get thumbnails - try different sizes
            thumbnails = snippet.get('thumbnails', {})
            
            return {
                'channel_id': channel_id,
                'channel_name': snippet.get('title', 'Unknown Channel'),
                'channel_description': snippet.get('description', ''),
                'channel_thumbnail': (
                    thumbnails.get('high', {}).get('url') or
                    thumbnails.get('medium', {}).get('url') or
                    thumbnails.get('default', {}).get('url') or
                    ''
                ),
                'uploads_playlist_id': related_playlists.get('uploads'),
                'custom_url': snippet.get('customUrl', ''),
                # Additional statistics
                'subscriber_count': int(statistics.get('subscriberCount', 0)),
                'video_count': int(statistics.get('videoCount', 0)),
                'view_count': int(statistics.get('viewCount', 0)),
                'published_at': snippet.get('publishedAt', ''),
                'country': snippet.get('country', ''),
                # Full snippet for debugging
                'snippet_title': snippet.get('title'),  # Explicit title for debugging
            }
        except Exception as e:
            error_msg = str(e)
            if 'quota' in error_msg.lower() or 'quotaExceeded' in error_msg:
                raise ValueError(
                    "API quota exceeded. Daily limit (10,000 units) reached. "
                    "Please try again tomorrow (resets at midnight Pacific Time) "
                    "or request a quota increase in Google Cloud Console."
                )
            elif 'expired' in error_msg.lower() or '403' in error_msg or '400' in error_msg:
                raise ValueError(
                    f"API key issue: {error_msg}. Please check your API key is valid and has proper permissions."
                )
            raise ValueError(f"Could not get uploads playlist for channel {channel_id}: {error_msg}")
    
    def get_last_n_videos(self, playlist_id: str, max_results: int = 20) -> List[str]:
        """
        Step 1: Get the last N video IDs from a playlist.
        Returns list of video IDs (newest first).
        Note: playlistItems are returned in reverse chronological order by default.
        Fetches ALL pages if needed to reach max_results.
        """
        video_ids = []
        try:
            # Always request 50 items per page (API max) for efficiency
            items_per_page = 50
            
            # First page
            request = self.youtube.playlistItems().list(
                part='contentDetails,snippet',
                playlistId=playlist_id,
                maxResults=items_per_page
            )
            response = request.execute()
            
            for item in response.get('items', []):
                if len(video_ids) >= max_results:
                    break
                video_ids.append(item['contentDetails']['videoId'])
            
            print(f"Playlist page 1: Got {len(response.get('items', []))} items (total: {len(video_ids)})")
            
            # Handle pagination - continue until we reach max_results or run out of pages
            page_num = 1
            while len(video_ids) < max_results:
                if 'nextPageToken' not in response:
                    print(f"No more pages available. Total fetched: {len(video_ids)}")
                    break
                    
                page_num += 1
                remaining = max_results - len(video_ids)
                items_to_fetch = min(50, remaining)
                
                try:
                    request = self.youtube.playlistItems().list(
                        part='contentDetails,snippet',
                        playlistId=playlist_id,
                        maxResults=items_to_fetch,
                        pageToken=response['nextPageToken']
                    )
                    response = request.execute()
                    
                    page_items = response.get('items', [])
                    page_count = len(page_items)
                    
                    for item in page_items:
                        if len(video_ids) >= max_results:
                            break
                        video_ids.append(item['contentDetails']['videoId'])
                    
                    print(f"Playlist page {page_num}: Got {page_count} items (total: {len(video_ids)})")
                    
                    # If this page returned fewer than requested, we've reached the end
                    if page_count < items_to_fetch:
                        print(f"Reached end of playlist (last page had {page_count} items)")
                        break
                        
                    # Safety check to avoid infinite loops
                    if page_num > 20:  # Max 20 pages = 1000 videos
                        print(f"⚠️ Reached maximum page limit (20 pages = ~1000 videos)")
                        break
                        
                except Exception as e:
                    error_msg = str(e)
                    if 'quota' in error_msg.lower():
                        print(f"⚠️ Quota exceeded during pagination, using {len(video_ids)} videos collected")
                        break
                    else:
                        print(f"Error on page {page_num}: {e}")
                        break
                
        except Exception as e:
            error_msg = str(e)
            print(f"Error fetching playlist items: {e}")
            
            # Check for quota exceeded first
            if 'quota' in error_msg.lower() or 'quotaExceeded' in error_msg:
                if video_ids:
                    print("⚠️ API quota exceeded, but continuing with available videos")
                    return video_ids
                else:
                    raise ValueError(
                        "API quota exceeded. Daily limit (10,000 units) reached. "
                        "Please try again tomorrow (resets at midnight Pacific Time) "
                        "or request a quota increase in Google Cloud Console."
                    )
            
            # Don't fail completely if we got some videos
            if video_ids:
                print(f"Warning: Got {len(video_ids)} videos before error occurred")
                return video_ids
            else:
                # Only raise if we got zero videos
                if 'expired' in error_msg.lower():
                    raise ValueError(f"API key expired. Please renew your API key.")
                elif '403' in error_msg or 'blocked' in error_msg.lower():
                    raise ValueError(f"API access blocked: {error_msg}")
                else:
                    raise ValueError(f"Error fetching videos: {error_msg[:200]}")
        
        return video_ids[:max_results]  # Ensure we don't exceed max_results
    
    def get_video_statistics(self, video_ids: List[str]) -> List[Dict]:
        """
        Step 2: Get statistics and details for multiple videos.
        Returns list of video dictionaries with all relevant data.
        """
        if not video_ids:
            return []
        
        videos_data = []
        try:
            # YouTube API allows up to 50 video IDs per request
            # Process in batches to ensure we get all videos
            for i in range(0, len(video_ids), 50):
                batch = video_ids[i:i+50]
                if not batch:
                    continue
                    
                request = self.youtube.videos().list(
                    part='statistics,snippet,contentDetails,liveStreamingDetails',
                    id=','.join(batch)
                )
                response = request.execute()
                
                items_returned = response.get('items', [])
                print(f"Requested {len(batch)} video IDs, got {len(items_returned)} back")
                
                for item in items_returned:
                    # Handle videos with hidden statistics
                    statistics = item.get('statistics', {})
                    
                    # Check if video is live - check both liveBroadcastContent and liveStreamingDetails
                    live_status = item['snippet'].get('liveBroadcastContent', 'none')
                    live_streaming_details = item.get('liveStreamingDetails', {})
                    
                    # Video is live if:
                    # 1. liveBroadcastContent is 'live', OR
                    # 2. liveStreamingDetails exists (indicates it's a live broadcast - even if concurrentViewers is null)
                    #    For 24/7 streams, liveStreamingDetails exists even when temporarily offline
                    concurrent_viewers = live_streaming_details.get('concurrentViewers')
                    has_live_streaming_details = bool(live_streaming_details)
                    # IMPORTANT: For 24/7 live streams, liveStreamingDetails exists even without concurrentViewers
                    # So we check for liveStreamingDetails OR liveBroadcastContent='live'
                    is_live = (live_status == 'live') or has_live_streaming_details
                    is_upcoming = live_status == 'upcoming'
                    
                    # Debug: Log all videos with live-related data for troubleshooting
                    if live_status != 'none' or has_live_streaming_details:
                        print(f"🔍 Live check for '{item['snippet']['title'][:50]}': liveBroadcastContent={live_status}, has_liveStreamingDetails={has_live_streaming_details}, concurrentViewers={concurrent_viewers}, is_live={is_live}")
                    
                    published_at = item['snippet']['publishedAt']
                    published_datetime = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    now = datetime.now(timezone.utc)
                    hours_since_publish = (now - published_datetime).total_seconds() / 3600
                    
                    view_count = int(statistics.get('viewCount', 0)) if statistics.get('viewCount') else 0
                    
                    # Calculate trending score: views per hour (for videos published in last 3 hours)
                    # Include videos published up to 3 hours ago (including 0 hours = just published)
                    trending_score = 0
                    is_trending = False
                    if hours_since_publish <= 3 and hours_since_publish >= 0:
                        # For videos just published (hours < 0.1), use view count as score
                        if hours_since_publish < 0.1:
                            trending_score = view_count * 10  # Boost for very recent videos
                        else:
                            trending_score = view_count / hours_since_publish if hours_since_publish > 0 else view_count
                        is_trending = True
                    
                    video_data = {
                        'video_id': item['id'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'][:200] if item['snippet'].get('description') else '',
                        'thumbnail': item['snippet']['thumbnails'].get('medium', {}).get('url', ''),
                        'published_at': published_at,
                        'published_datetime': published_datetime.isoformat(),
                        'hours_since_publish': round(hours_since_publish, 2),
                        'view_count': view_count,
                        'like_count': int(statistics.get('likeCount', 0)) if statistics.get('likeCount') else 0,
                        'comment_count': int(statistics.get('commentCount', 0)) if statistics.get('commentCount') else 0,
                        'duration': item['contentDetails'].get('duration', ''),
                        'url': f"https://www.youtube.com/watch?v={item['id']}",
                        'is_short': self._is_short_video(item['contentDetails'].get('duration', '')),
                        'is_live': is_live,
                        'is_upcoming': is_upcoming,
                        'live_viewers': int(concurrent_viewers) if concurrent_viewers is not None else None,
                        'live_broadcast_content': live_status,  # Store the original value for debugging
                        'trending_score': round(trending_score, 2),
                        'is_trending': is_trending
                    }
                    
                    # Debug logging for live videos - log more details
                    if is_live:
                        print(f"🔴 LIVE VIDEO DETECTED in get_video_statistics: '{item['snippet']['title'][:50]}' - liveBroadcastContent={live_status}, concurrentViewers={concurrent_viewers}, is_live={is_live}, has_liveStreamingDetails={has_live_streaming_details}")
                    elif live_status != 'none' or has_live_streaming_details:
                        # Log videos that have live-related data but weren't marked as live
                        print(f"⚠️ Video with live data but not marked live: '{item['snippet']['title'][:50]}' - liveBroadcastContent={live_status}, has_liveStreamingDetails={has_live_streaming_details}, concurrentViewers={concurrent_viewers}")
                    
                    videos_data.append(video_data)
                
                # If we got fewer items than requested, log it but continue
                if len(items_returned) < len(batch):
                    print(f"Warning: Only got {len(items_returned)}/{len(batch)} videos from API (some may be private/deleted)")
        except Exception as e:
            error_msg = str(e)
            print(f"Error fetching video statistics: {e}")
            # Check for API key or permission issues
            if 'expired' in error_msg.lower() or '403' in error_msg or '400' in error_msg or 'blocked' in error_msg.lower():
                raise ValueError(
                    f"API error when fetching video statistics: {error_msg}. "
                    f"Please check your API key permissions and quota."
                )
            # Re-raise other errors
            raise
        
        return videos_data
    
    def _is_short_video(self, duration: str) -> bool:
        """
        Determine if a video is a Short based on duration.
        YouTube Shorts are 60 seconds or less.
        Duration format: PT#M#S (e.g., PT1M30S = 1 minute 30 seconds)
        """
        if not duration:
            return False
        
        # Parse ISO 8601 duration format
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return False
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds <= 60
    
    def rank_videos_by_views(self, videos: List[Dict], reverse: bool = True) -> List[Dict]:
        """Rank videos by view count (highest to lowest by default)"""
        return sorted(videos, key=lambda x: x['view_count'], reverse=reverse)
    
    def fetch_channel_videos_by_popularity(self, channel_id: str, max_results: int = 50) -> List[Dict]:
        """
        Fetch videos from a channel sorted by view count (popularity) using search API.
        This method uses search.list with order=viewCount to get videos sorted by popularity.
        Fetches multiple pages if needed to get enough results.
        """
        all_videos = []
        video_ids = []
        try:
            # Fetch first page
            request = self.youtube.search().list(
                part='snippet',
                channelId=channel_id,
                type='video',
                order='viewCount',  # Sort by view count (highest first)
                maxResults=50  # API max is 50 per request
            )
            response = request.execute()
            
            # Collect video IDs from first page
            for item in response.get('items', []):
                video_ids.append(item['id']['videoId'])
            
            print(f"Search API - Page 1: Got {len(video_ids)} videos")
            
            # Handle pagination - fetch more pages if we need more results
            page_count = 1
            while len(video_ids) < max_results and 'nextPageToken' in response:
                page_count += 1
                request = self.youtube.search().list(
                    part='snippet',
                    channelId=channel_id,
                    type='video',
                    order='viewCount',
                    maxResults=50,
                    pageToken=response['nextPageToken']
                )
                response = request.execute()
                
                page_items = len(response.get('items', []))
                for item in response.get('items', []):
                    if len(video_ids) >= max_results:
                        break
                    video_ids.append(item['id']['videoId'])
                
                print(f"Search API - Page {page_count}: Got {page_items} videos (total: {len(video_ids)})")
                
                # If this page returned fewer than 50, we've reached the end
                if page_items < 50:
                    break
            
            print(f"Total videos fetched from search API: {len(video_ids)}")
            
            # Get detailed statistics for all videos
            if video_ids:
                all_videos = self.get_video_statistics(video_ids)
                
        except Exception as e:
            error_msg = str(e)
            print(f"Error fetching videos by popularity: {e}")
            # Don't raise - let the calling function handle fallback
            # Just return empty list so we can fall back to playlist method
            if '403' in error_msg or 'blocked' in error_msg.lower() or 'quota' in error_msg.lower():
                print("Search API unavailable (blocked/quota), will use playlist method")
                return []
            # For other errors, still return empty to trigger fallback
            print("Search API error, will use playlist method")
            return []
        
        return all_videos
    
    def fetch_channel_videos(self, channel_url: str, max_videos: int = 5, max_shorts: int = 5) -> Dict:
        """
        Main method: Fetch and rank videos from a channel.
        Uses search API with order=viewCount to get videos sorted by popularity directly.
        Fetches videos and shorts separately.
        Returns dictionary with channel info and ranked videos/shorts separately.
        """
        # Extract channel ID
        channel_id = self.extract_channel_id(channel_url)
        if not channel_id:
            # Check if it's an @handle URL - provide helpful error message
            if '/@' in channel_url:
                handle = channel_url.split('/@')[-1].split('/')[0].split('?')[0]
                error_msg = (
                    f"Could not extract channel ID from @handle URL: {channel_url}. "
                    f"This happens when Search API is blocked or quota exceeded. "
                    f"Please use channel ID URL format instead: "
                    f"https://www.youtube.com/channel/UCxxxxx"
                )
                # If we know the channel ID, suggest it
                known_channels = {
                    'hanaaaneyy': 'UCBoLezq04tdd45n5gG4dOng',
                    'mrzthoppi': 'UC0XCrZT2-n_Yyj4gAePKekg',
                    'CallMeShazzamTECH': 'UC9MQp8a5uhaIosZPHaoqEXQ',
                    'techwiser': None,  # Don't have this one
                }
                if handle.lower() in [k.lower() for k in known_channels.keys()]:
                    known_id = next((v for k, v in known_channels.items() if k.lower() == handle.lower()), None)
                    if known_id:
                        error_msg += f" Try: https://www.youtube.com/channel/{known_id}"
            else:
                error_msg = (
                    f"Could not extract channel ID from URL: {channel_url}. "
                    f"Please ensure the URL is in a valid format."
                )
            raise ValueError(error_msg)
        
        # Get channel information (name, thumbnail, etc.)
        channel_info = self.get_channel_info(channel_id)
        if not channel_info:
            print(f"⚠️ Warning: Could not get channel info for {channel_id}")
            channel_name = 'Unknown Channel'
            channel_thumbnail = ''
        else:
            # Try multiple field names to ensure we get the name
            channel_name = (
                channel_info.get('channel_name') or
                channel_info.get('snippet_title') or
                'Unknown Channel'
            )
            channel_thumbnail = channel_info.get('channel_thumbnail', '')
            print(f"✅ Channel info fetched: name='{channel_name}', has_thumbnail={bool(channel_thumbnail)}")
        
        # Check for active live broadcasts - 24/7 streams might not be in regular uploads
        print(f"\n🔴 Checking for active live broadcasts on channel {channel_id}...")
        live_broadcast_details = []  # Initialize to ensure it's always defined
        try:
            # Search for live broadcasts on this channel
            live_search = self.youtube.search().list(
                part='snippet',
                channelId=channel_id,
                type='video',
                eventType='live',  # Get only live broadcasts
                maxResults=5
            ).execute()
            
            live_broadcast_ids = []
            for item in live_search.get('items', []):
                video_id = item['id'].get('videoId')
                if video_id:
                    live_broadcast_ids.append(video_id)
                    print(f"  ✓ Found live broadcast: {item['snippet']['title'][:50]} (ID: {video_id})")
            
            # If we found live broadcasts, get their full details
            if live_broadcast_ids:
                print(f"  📺 Fetching details for {len(live_broadcast_ids)} live broadcast(s)...")
                live_broadcast_details = self.get_video_statistics(live_broadcast_ids)
                print(f"  ✅ Got {len(live_broadcast_details)} live broadcast details")
            else:
                live_broadcast_details = []
                print(f"  ℹ️ No active live broadcasts found via search API")
        except Exception as e:
            error_msg = str(e)
            if '403' in error_msg or 'blocked' in error_msg.lower():
                print(f"  ⚠️ Search API blocked for live broadcasts (likely quota/restrictions): {error_msg[:100]}")
            else:
                print(f"  ⚠️ Error checking for live broadcasts: {error_msg[:100]}")
            live_broadcast_details = []
        
        # Fetch enough videos to ensure we get top 5 videos and top 5 shorts
        # We need to fetch significantly more because:
        # 1. Search API might return limited results per channel
        # 2. We need to filter into videos vs shorts
        # 3. Some channels have more videos than shorts (or vice versa)
        # 4. We also need recent videos for trending detection (last 1 hour)
        # Fetch at least 200 items to ensure we get enough of each type + recent videos
        total_needed = max_videos + max_shorts
        fetch_count = max(total_needed * 20, 200)  # Fetch 20x to ensure we get enough of each type + recent videos for trending
        
        # Use hybrid approach: Search API for popularity + Playlist for more content
        all_videos_dict = {}  # Use dict to avoid duplicates (video_id as key)
        
        # Add live broadcasts found earlier (24/7 streams)
        if live_broadcast_details:
            print(f"Adding {len(live_broadcast_details)} live broadcast(s) to video collection...")
            for video in live_broadcast_details:
                # Ensure they're marked as live
                video['is_live'] = True
                all_videos_dict[video['video_id']] = video
                print(f"  ✓ Added live broadcast: {video.get('title', 'Unknown')[:50]}")
        
        # Step 1: Try search API to get popular videos (ONLY if enabled - it's expensive: 100 units!)
        # Check settings to see if Search API should be used
        from django.conf import settings
        use_search_api = getattr(settings, 'USE_SEARCH_API', False)
        
        if use_search_api:
            search_videos = self.fetch_channel_videos_by_popularity(channel_id, fetch_count)
            
            if search_videos:
                print(f"Search API returned: {len(search_videos)} videos")
                # Add to dict (already sorted by popularity)
                for video in search_videos:
                    all_videos_dict[video['video_id']] = video
            else:
                print("Search API returned no results, will rely on playlist method")
        else:
            print("⚠️ Search API disabled (saves 100 quota units per channel). Using playlist method + sorting.")
        
        # Step 2: If we don't have enough videos/shorts (or search API failed), fetch from playlist
        regular_videos = [v for v in all_videos_dict.values() if not v['is_short']]
        shorts = [v for v in all_videos_dict.values() if v['is_short']]
        
        print(f"After search API: {len(regular_videos)} videos, {len(shorts)} shorts")
        
        # If search API failed or we don't have enough of either type, fetch from playlist
        search_api_failed = len(all_videos_dict) == 0
        need_more = (len(regular_videos) < max_videos) or (len(shorts) < max_shorts)
        
        if search_api_failed or need_more:
            print("Fetching additional videos from playlist to get enough content...")
            try:
                # Get channel info which includes playlist ID
                if not channel_info:
                    channel_info = self.get_channel_info(channel_id)
                playlist_id = channel_info.get('uploads_playlist_id') if channel_info else None
                if playlist_id:
                    # Fetch more from playlist (recent uploads)
                    # Fetch significantly more to ensure we get enough of each type
                    # Also need recent videos for trending detection
                    playlist_fetch_count = max(max_videos * 30, max_shorts * 30, 300)
                    print(f"Fetching up to {playlist_fetch_count} videos from playlist (will paginate to get all)...")
                    video_ids = self.get_last_n_videos(playlist_id, playlist_fetch_count)
                    print(f"Actually fetched {len(video_ids)} video IDs from playlist (requested {playlist_fetch_count})")
                    
                    # If we got fewer than expected but still have a nextPageToken, 
                    # it might mean the playlist has more items but we hit quota or other limits
                    
                    if video_ids:
                        playlist_videos = self.get_video_statistics(video_ids)
                        print(f"Playlist returned: {len(playlist_videos)} videos")
                        
                        # Add new videos (don't overwrite search API results - those are already sorted)
                        for video in playlist_videos:
                            if video['video_id'] not in all_videos_dict:
                                all_videos_dict[video['video_id']] = video
                        
                        # Re-categorize
                        regular_videos = [v for v in all_videos_dict.values() if not v['is_short']]
                        shorts = [v for v in all_videos_dict.values() if v['is_short']]
                        
                        print(f"After adding playlist: {len(regular_videos)} videos, {len(shorts)} shorts")
                        
                        # Sort by view count (search API videos are already sorted, but playlist ones need sorting)
                        # Combine and re-sort all to ensure proper ranking
                        all_videos_list = list(all_videos_dict.values())
                        regular_videos = sorted([v for v in all_videos_list if not v['is_short']], 
                                               key=lambda x: int(x.get('view_count', 0)), reverse=True)
                        shorts = sorted([v for v in all_videos_list if v['is_short']], 
                                        key=lambda x: int(x.get('view_count', 0)), reverse=True)
            except Exception as e:
                print(f"Error fetching from playlist: {e}")
        
        # Extract trending videos (published in last 3 hours) and live videos from all videos
        all_videos_list = list(all_videos_dict.values())
        
        # Recalculate trending status for all videos (in case hours changed during processing)
        # This ensures we catch all videos published in the last 3 hours
        now = datetime.now(timezone.utc)
        trending_count = 0
        live_count = 0
        
        for video in all_videos_list:
            # Recalculate live status (in case it changed)
            if video.get('is_live', False):
                live_count += 1
                video['is_live'] = True  # Ensure it's set
            
            if video.get('published_at'):
                try:
                    pub_dt = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
                    hours_since = (now - pub_dt).total_seconds() / 3600
                    video['hours_since_publish'] = round(hours_since, 2)
                    
                    # Update trending status if within 3 hours (including 0 = just published)
                    if hours_since <= 3 and hours_since >= 0:
                        video['is_trending'] = True
                        trending_count += 1
                        view_count = video.get('view_count', 0)
                        
                        # Calculate trending score
                        if hours_since < 0.1:  # Very recent (< 6 minutes)
                            video['trending_score'] = view_count * 10
                        else:
                            video['trending_score'] = view_count / hours_since if hours_since > 0 else view_count
                    else:
                        video['is_trending'] = False
                        video['trending_score'] = 0
                except Exception as e:
                    print(f"Error calculating trending for video {video.get('video_id')}: {e}")
                    video['is_trending'] = False
        
        # Separate trending into videos and shorts
        # Double-check trending status with explicit validation
        trending_all = []
        for v in all_videos_list:
            if v.get('is_trending', False):
                # Verify hours_since_publish is still valid
                hours = v.get('hours_since_publish', 999)
                if hours <= 3 and hours >= 0:
                    trending_all.append(v)
                else:
                    # Clear the flag if hours don't match
                    v['is_trending'] = False
        
        print(f"Found {trending_count} trending videos and {live_count} live videos out of {len(all_videos_list)} total")
        
        # Split into trending videos and trending shorts
        trending_videos_all = [v for v in trending_all if not v.get('is_short', False)]
        trending_shorts_all = [v for v in trending_all if v.get('is_short', False)]
        
        # Sort each by trending score and take top 3
        trending_videos_sorted = sorted(trending_videos_all, 
                                       key=lambda x: x.get('trending_score', 0), 
                                       reverse=True)
        trending_shorts_sorted = sorted(trending_shorts_all,
                                       key=lambda x: x.get('trending_score', 0),
                                       reverse=True)
        
        trending_videos = trending_videos_sorted[:3]  # Top 3 trending videos
        trending_shorts = trending_shorts_sorted[:3]  # Top 3 trending shorts
        
        print(f"Found {len(trending_videos_all)} trending videos and {len(trending_shorts_all)} trending shorts out of {len(all_videos_list)} total")
        print(f"Showing top {len(trending_videos)} trending videos and top {len(trending_shorts)} trending shorts")
        
        # Extract live videos
        # Filter live videos - double-check
        live_videos = []
        print(f"\n🔍 DEBUG: Checking {len(all_videos_list)} videos for live status...")
        for v in all_videos_list:
            video_id = v.get('video_id', 'Unknown')
            is_live_flag = v.get('is_live', False)
            live_viewers = v.get('live_viewers')
            title = v.get('title', 'Unknown')[:50]
            
            print(f"  Video '{title}': is_live={is_live_flag}, live_viewers={live_viewers}, video_id={video_id}")
            
            if is_live_flag:
                print(f"    ✓ Added to live_videos (is_live=True)")
                live_videos.append(v)
            # Also check if it has live streaming details (might be live but flag not set)
            elif live_viewers:
                print(f"    ✓ Added to live_videos (has live_viewers={live_viewers})")
                v['is_live'] = True
                live_videos.append(v)
            # Also check liveBroadcastContent directly if available
            elif v.get('live_broadcast_content') == 'live':
                print(f"    ✓ Added to live_videos (liveBroadcastContent='live')")
                v['is_live'] = True
                live_videos.append(v)
            # Also check if liveStreamingDetails exists (even without concurrentViewers, it indicates a live stream)
            elif v.get('live_broadcast_content') == 'upcoming':
                print(f"    ⏰ Skipping upcoming live stream: '{title}'")
            # Check if video has live_streaming_details but wasn't marked as live
            elif v.get('live_broadcast_content') and v.get('live_broadcast_content') != 'none':
                print(f"    🔍 Found live_broadcast_content='{v.get('live_broadcast_content')}' for '{title}' - checking if should be included")
        
        print(f"🔴 Total live videos found: {len(live_videos)}")
        if live_videos:
            live_videos_list = [f"'{v.get('title', 'Unknown')[:30]}' (viewers: {v.get('live_viewers')})" for v in live_videos]
            print(f"   Live videos: {live_videos_list}")
        
        # Sort live videos by view count (or concurrent viewers if available) - highest first
        # IMPORTANT: Live videos should be sorted by MOST VIEWS, not by publish date
        # Prioritize concurrent viewers for live streams, then fall back to total view count
        if live_videos:
            print(f"Before sorting - Live videos: {[(v.get('title', 'Unknown')[:30], 'viewers:', v.get('live_viewers'), 'views:', v.get('view_count'), 'type:', type(v.get('live_viewers')), type(v.get('view_count'))) for v in live_videos]}")
            
            # Sort by concurrent viewers first (if available), then total view count
            # Convert to int to ensure proper numeric comparison
            def get_sort_key(video):
                live_viewers = video.get('live_viewers')
                view_count = video.get('view_count', 0)
                
                # Convert live_viewers to int (might be string or None)
                if live_viewers is None:
                    viewers_int = 0
                elif isinstance(live_viewers, str):
                    viewers_int = int(live_viewers) if live_viewers.isdigit() else 0
                else:
                    viewers_int = int(live_viewers)
                
                # Convert view_count to int
                if view_count is None:
                    views_int = 0
                elif isinstance(view_count, str):
                    views_int = int(view_count) if view_count.isdigit() else 0
                else:
                    views_int = int(view_count)
                
                # Return tuple: (concurrent_viewers, total_views) - higher is better
                return (viewers_int, views_int)
            
            live_videos = sorted(live_videos, key=get_sort_key, reverse=True)
            
            print(f"After sorting - Live videos: {[(v.get('title', 'Unknown')[:30], 'viewers:', v.get('live_viewers'), 'views:', v.get('view_count')) for v in live_videos]}")
            
            # Only keep the top live video (one with most viewers)
            if len(live_videos) > 1:
                print(f"⚠️ Found {len(live_videos)} live videos - keeping only the one with most viewers")
                live_videos = [live_videos[0]]  # Keep only the first (highest viewers)
                print(f"✓ Selected top live video: '{live_videos[0].get('title', 'Unknown')[:50]}' - {live_videos[0].get('live_viewers')} concurrent viewers, {live_videos[0].get('view_count')} total views")
            elif live_videos:
                first = live_videos[0]
                print(f"✓ Single live video: '{first.get('title', 'Unknown')[:50]}' - {first.get('live_viewers')} concurrent viewers, {first.get('view_count')} total views")
        
        if not all_videos_dict:
            # Make sure we have channel info even if no videos
            if not channel_info:
                try:
                    channel_info = self.get_channel_info(channel_id)
                    if channel_info:
                        channel_name = channel_info.get('channel_name', 'Unknown Channel')
                        channel_thumbnail = channel_info.get('channel_thumbnail', '')
                except:
                    pass  # Keep defaults
            
            result = {
                'channel_id': channel_id,
                'channel_url': channel_url,
                'channel_name': channel_name,
                'channel_thumbnail': channel_thumbnail,
                'videos': [],
                'shorts': [],
                'trending_videos': [],
                'trending_shorts': [],
                'live_videos': [],
                'total_trending_videos': 0,
                'total_trending_shorts': 0,
                'total_trending': 0,
                'total_live': 0,
                'error': 'No videos found or could not retrieve video data'
            }
            
            # Add channel statistics if channel_info is available
            if channel_info:
                result['subscriber_count'] = channel_info.get('subscriber_count', 0)
                result['view_count'] = channel_info.get('view_count', 0)
                result['video_count'] = channel_info.get('video_count', 0)
                result['published_at'] = channel_info.get('published_at', '')
                result['country'] = channel_info.get('country', '')
            
            return result
        
        # Take top N of each type (already sorted by popularity)
        # Note: If channel has fewer videos than requested, return what's available
        ranked_videos = regular_videos[:max_videos]
        ranked_shorts = shorts[:max_shorts]
        
        # Log if we couldn't get the requested amount
        if len(ranked_videos) < max_videos:
            print(f"⚠️ Channel only has {len(ranked_videos)} regular videos (requested {max_videos})")
        if len(ranked_shorts) < max_shorts:
            print(f"⚠️ Channel only has {len(ranked_shorts)} shorts (requested {max_shorts})")
        
        print(f"\n📊 FINAL RESULT SUMMARY:")
        print(f"   Videos: {len(ranked_videos)}")
        print(f"   Shorts: {len(ranked_shorts)}")
        print(f"   Trending videos (last 3hr): {len(trending_videos)}")
        print(f"   Trending shorts (last 3hr): {len(trending_shorts)}")
        print(f"   🔴 LIVE VIDEOS: {len(live_videos)} (showing only top one with most viewers)")
        if live_videos:
            live = live_videos[0]
            print(f"      Top Live: '{live.get('title', 'Unknown')[:50]}' - {live.get('live_viewers')} concurrent viewers, {live.get('view_count')} total views")
        else:
            print(f"      ⚠️ No live videos found in {len(all_videos_list)} total videos")
        
        # Include additional channel statistics if available
        result = {
            'channel_id': channel_id,
            'channel_url': channel_url,
            'channel_name': channel_name,
            'channel_thumbnail': channel_thumbnail,
            'videos': ranked_videos,
            'shorts': ranked_shorts,
            'trending_videos': trending_videos,
            'trending_shorts': trending_shorts,
            'live_videos': live_videos,
            'total_videos': len(ranked_videos),
            'total_shorts': len(ranked_shorts),
            'total_trending_videos': len(trending_videos),
            'total_trending_shorts': len(trending_shorts),
            'total_trending': len(trending_videos) + len(trending_shorts),
            'total_live': len(live_videos),
            'total_fetched': len(all_videos_dict)
        }
        
        # Add channel statistics if channel_info is available
        if channel_info:
            result['subscriber_count'] = channel_info.get('subscriber_count', 0)
            result['view_count'] = channel_info.get('view_count', 0)
            result['video_count'] = channel_info.get('video_count', 0)
            result['published_at'] = channel_info.get('published_at', '')
            result['country'] = channel_info.get('country', '')
        
        return result
    
    def _fetch_via_playlist(self, channel_id: str, channel_url: str, max_videos: int, max_shorts: int) -> Dict:
        """
        Fallback method: Fetch videos via playlist (original method).
        Used when search API is not available.
        """
        # Get uploads playlist ID
        playlist_id = self.get_uploads_playlist_id(channel_id)
        if not playlist_id:
            raise ValueError(f"Could not get uploads playlist for channel: {channel_id}")
        
        # Fetch enough items
        total_needed = max_videos + max_shorts
        fetch_count = max(total_needed * 5, 100)
        
        # Get video IDs
        video_ids = self.get_last_n_videos(playlist_id, fetch_count)
        if not video_ids:
            return {
                'channel_id': channel_id,
                'channel_url': channel_url,
                'videos': [],
                'shorts': [],
                'error': 'No videos found'
            }
        
        # Get video statistics
        all_videos = self.get_video_statistics(video_ids)
        
        if not all_videos:
            return {
                'channel_id': channel_id,
                'channel_url': channel_url,
                'videos': [],
                'shorts': [],
                'error': f'Found {len(video_ids)} video IDs but could not retrieve video data.'
            }
        
        # Separate and sort
        regular_videos = [v for v in all_videos if not v['is_short']]
        shorts = [v for v in all_videos if v['is_short']]
        
        # Sort by view count (highest first)
        ranked_videos = sorted(regular_videos, key=lambda x: int(x.get('view_count', 0)), reverse=True)[:max_videos]
        ranked_shorts = sorted(shorts, key=lambda x: int(x.get('view_count', 0)), reverse=True)[:max_shorts]
        
        return {
            'channel_id': channel_id,
            'channel_url': channel_url,
            'videos': ranked_videos,
            'shorts': ranked_shorts,
            'total_videos': len(ranked_videos),
            'total_shorts': len(ranked_shorts),
            'total_fetched': len(all_videos)
        }

