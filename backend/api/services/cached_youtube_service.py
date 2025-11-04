"""
Cached YouTube Service Wrapper
Adds caching, quota management, and rate limiting to YouTube API calls
"""
from typing import List, Dict, Optional
from api.services.youtube_service import YouTubeService
from api.utils.api_cache import APICache
from api.utils.quota_manager import QuotaManager
from api.utils.rate_limiter import RateLimiter
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CachedYouTubeService:
    """
    Wrapper around YouTubeService that adds:
    - Response caching to reduce API calls
    - Quota tracking and management
    - Rate limiting to prevent bursts
    """
    
    # API call costs in quota units
    QUOTA_COSTS = {
        'channels.list': 1,
        'playlistItems.list': 1,
        'videos.list': 1,
        'search.list': 100,  # Very expensive!
    }
    
    def __init__(self):
        self.youtube_service = YouTubeService()
        self.quota_manager = QuotaManager(
            daily_limit=settings.YOUTUBE_QUOTA_LIMIT,
            warning_threshold=settings.YOUTUBE_QUOTA_WARNING_THRESHOLD
        )
        self.rate_limiter = RateLimiter(
            max_per_second=settings.YOUTUBE_API_RATE_LIMIT['max_requests_per_second'],
            max_per_minute=settings.YOUTUBE_API_RATE_LIMIT['max_requests_per_minute']
        )
    
    def _make_api_call(self, endpoint, params, func, quota_cost, bypass_cache=True):
        """
        Make an API call with caching, quota checking, and rate limiting.
        
        Args:
            endpoint: Cache endpoint identifier
            params: Parameters for cache key generation
            func: Function to call if cache miss
            quota_cost: Quota units this call will consume
            bypass_cache: If True, skip cache check and always make API call (DEFAULT: True - CACHE DISABLED FOR DEBUGGING)
        """
        # TEMPORARILY DISABLE CACHE FOR DEBUGGING
        # Check cache first (unless bypassed)
        if False and not bypass_cache:  # Force bypass - cache disabled
            cached_data, is_cached = APICache.get(endpoint, params)
            if is_cached:
                logger.info(f"Cache HIT for {endpoint}, saving {quota_cost} quota units")
                return cached_data['data']
            logger.info(f"Cache miss for {endpoint} - making API call")
        else:
            logger.warning(f"⚠️ CACHE DISABLED - Fetching fresh data for {endpoint}")
        
        # Check quota before making request
        if not self.quota_manager.can_make_request(quota_cost):
            quota_status = self.quota_manager.get_quota_status()
            raise ValueError(
                f"API quota exceeded. Used: {quota_status['used']}/{quota_status['limit']} "
                f"({quota_status['percentage']:.1f}%). Please try again later or request quota increase."
            )
        
        # Rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Make the API call
        try:
            logger.info(f"Making API call to {endpoint} (cost: {quota_cost} units)")
            result = func()
            
            # Consume quota
            if not self.quota_manager.consume_quota(quota_cost):
                logger.warning(f"Quota exceeded after API call - this shouldn't happen!")
            
            # TEMPORARILY DISABLE CACHING FOR DEBUGGING
            # Cache the result
            # APICache.set(endpoint, params, result)  # DISABLED
            logger.warning(f"⚠️ CACHE SET DISABLED - result not cached for {endpoint}")
            
            # Record rate limit
            self.rate_limiter.record_request()
            
            return result
            
        except Exception as e:
            # Don't consume quota on errors (unless it's a quota error)
            error_str = str(e)
            if 'quota' in error_str.lower() or 'quotaExceeded' in error_str:
                # Mark quota as exceeded
                logger.error(f"Quota error from API: {e}")
            raise
    
    def extract_channel_id(self, channel_url: str) -> Optional[str]:
        """Extract channel ID - no caching needed (fast operation)"""
        return self.youtube_service.extract_channel_id(channel_url)
    
    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """Get channel information with caching"""
        endpoint = 'channel_info'
        params = {'channel_id': channel_id, 'type': 'full_info'}
        
        def _fetch():
            return self.youtube_service.get_channel_info(channel_id)
        
        # TEMPORARILY DISABLE CACHE FOR DEBUGGING
        return self._make_api_call(endpoint, params, _fetch, self.QUOTA_COSTS['channels.list'], bypass_cache=True)
    
    def get_uploads_playlist_id(self, channel_id: str) -> Optional[str]:
        """Get uploads playlist ID with caching (legacy method for compatibility)"""
        channel_info = self.get_channel_info(channel_id)
        if channel_info:
            return channel_info.get('uploads_playlist_id')
        return None
    
    def get_last_n_videos(self, playlist_id: str, max_results: int = 20) -> List[str]:
        """Get video IDs from playlist with caching"""
        endpoint = 'playlist_items'
        params = {'playlist_id': playlist_id, 'max_results': max_results}
        
        def _fetch():
            return self.youtube_service.get_last_n_videos(playlist_id, max_results)
        
        # Estimate quota cost (1 unit per 50 items fetched)
        estimated_cost = max(1, (max_results // 50) + 1)
        # TEMPORARILY DISABLE CACHE FOR DEBUGGING
        return self._make_api_call(endpoint, params, _fetch, estimated_cost * self.QUOTA_COSTS['playlistItems.list'], bypass_cache=True)
    
    def get_video_statistics(self, video_ids: List[str], bypass_cache=True) -> List[Dict]:
        """Get video statistics with caching"""
        # Sort video IDs for consistent cache key
        sorted_ids = sorted(video_ids)
        endpoint = 'video_statistics'
        params = {'video_ids': sorted_ids}
        
        def _fetch():
            return self.youtube_service.get_video_statistics(video_ids)
        
        # Calculate quota cost (1 unit per batch of 50)
        batch_count = (len(video_ids) + 49) // 50
        quota_cost = batch_count * self.QUOTA_COSTS['videos.list']
        
        return self._make_api_call(endpoint, params, _fetch, quota_cost, bypass_cache=bypass_cache)
    
    def fetch_channel_videos_by_popularity(self, channel_id: str, max_results: int = 50) -> List[Dict]:
        """Fetch videos by popularity with caching"""
        endpoint = 'channel_videos_by_popularity'
        params = {'channel_id': channel_id, 'max_results': max_results}
        
        def _fetch():
            return self.youtube_service.fetch_channel_videos_by_popularity(channel_id, max_results)
        
        # Search API is expensive - estimate cost
        estimated_cost = max(self.QUOTA_COSTS['search.list'], (max_results // 50) * self.QUOTA_COSTS['search.list'])
        
        return self._make_api_call(endpoint, params, _fetch, estimated_cost)
    
    def fetch_channel_videos(self, channel_url: str, max_videos: int = 5, max_shorts: int = 5, real_time_trending=False, real_time_live=False) -> Dict:
        """
        Main method: Fetch channel videos with caching.
        This method is cached as a whole to avoid redundant calls.
        """
        # Extract channel ID first (cached internally if needed)
        channel_id = self.extract_channel_id(channel_url)
        if not channel_id:
            raise ValueError(f"Could not extract channel ID from URL: {channel_url}")
        
        # Cache the entire result
        endpoint = 'channel_videos'
        params = {
            'channel_id': channel_id,
            'max_videos': max_videos,
            'max_shorts': max_shorts,
            'version': '2.1'  # Version bump to invalidate old cache that might have no videos
        }
        
        def _fetch():
            # Use the underlying service methods but through our cached wrapper
            # This ensures individual calls are cached too
            return self.youtube_service.fetch_channel_videos(channel_url, max_videos, max_shorts)
        
        # Estimate total quota cost (conservative)
        estimated_cost = (
            self.QUOTA_COSTS['channels.list'] +  # Get playlist ID + stats
            5 * self.QUOTA_COSTS['playlistItems.list'] +  # Fetch playlist items
            5 * self.QUOTA_COSTS['videos.list']  # Get video stats
        )
        
        # TEMPORARILY DISABLE CACHE FOR DEBUGGING - fetch fresh every time
        logger.warning(f"⚠️ CACHE DISABLED - Fetching fresh data for channel {channel_id}")
        result = _fetch()  # Always fetch fresh, no cache
        
        # Ensure live videos are sorted by view count (highest first)
        # IMPORTANT: Sort by MOST VIEWS, not publish date
        # Prioritize concurrent viewers, then total view count
        if result and result.get('live_videos') and len(result.get('live_videos', [])) > 0:
            logger.info(f"Sorting {len(result['live_videos'])} live videos by view count (NOT by publish date)")
            # Log before sorting
            for idx, live in enumerate(result['live_videos']):
                logger.info(f"  Live {idx} BEFORE SORT: '{live.get('title', 'Unknown')[:40]}' - viewers: {live.get('live_viewers')} (type: {type(live.get('live_viewers'))}), views: {live.get('view_count')} (type: {type(live.get('view_count'))})")
            
            def get_sort_key(video):
                live_viewers = video.get('live_viewers')
                view_count = video.get('view_count', 0)
                
                # Convert live_viewers to int
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
                
                return (viewers_int, views_int)
            
            result['live_videos'] = sorted(result['live_videos'], key=get_sort_key, reverse=True)
            
            # Log after sorting
            for idx, live in enumerate(result['live_videos']):
                logger.info(f"  Live {idx} AFTER SORT: '{live.get('title', 'Unknown')[:40]}' - viewers: {live.get('live_viewers')}, views: {live.get('view_count')}")
            
            # Only keep the top live video (one with most viewers)
            if len(result['live_videos']) > 1:
                logger.info(f"⚠️ Found {len(result['live_videos'])} live videos - keeping only the one with most viewers")
                result['live_videos'] = [result['live_videos'][0]]  # Keep only the first (highest viewers)
                result['total_live'] = 1  # Update count
                logger.info(f"✓ Selected top live video: '{result['live_videos'][0].get('title', 'Unknown')[:40]}' with {result['live_videos'][0].get('live_viewers')} concurrent viewers, {result['live_videos'][0].get('view_count')} total views")
            else:
                logger.info(f"✓ Live video: '{result['live_videos'][0].get('title', 'Unknown')[:40]}' with {result['live_videos'][0].get('live_viewers')} concurrent viewers, {result['live_videos'][0].get('view_count')} total views")
        
        # Ensure statistics are always included (in case cache didn't have them)
        if result and 'subscriber_count' not in result:
            # If stats are missing, fetch channel info fresh
            try:
                channel_info = self.get_channel_info(channel_id)
                if channel_info:
                    result['subscriber_count'] = channel_info.get('subscriber_count', 0)
                    result['view_count'] = channel_info.get('view_count', 0)
                    result['video_count'] = channel_info.get('video_count', 0)
            except:
                # If we can't fetch, set defaults
                result['subscriber_count'] = 0
                result['view_count'] = 0
                result['video_count'] = 0
        
        # If real-time trending or live requested, fetch fresh data for those
        if real_time_trending or real_time_live:
            logger.info("Fetching real-time trending/live data (bypassing cache)")
            # Collect all video IDs from result (including trending videos and shorts)
            all_video_ids = []
            for video in result.get('videos', []):
                all_video_ids.append(video.get('video_id'))
            for video in result.get('shorts', []):
                all_video_ids.append(video.get('video_id'))
            # Also include trending videos and shorts for real-time updates
            for video in result.get('trending_videos', []):
                vid_id = video.get('video_id')
                if vid_id and vid_id not in all_video_ids:
                    all_video_ids.append(vid_id)
            for video in result.get('trending_shorts', []):
                vid_id = video.get('video_id')
                if vid_id and vid_id not in all_video_ids:
                    all_video_ids.append(vid_id)
            
            if all_video_ids:
                # Fetch fresh stats (bypass cache for real-time)
                fresh_stats = self.get_video_statistics(all_video_ids, bypass_cache=True)
                # Create lookup dict
                fresh_stats_dict = {v['video_id']: v for v in fresh_stats}
                
                # Update trending videos with fresh data
                if real_time_trending:
                    # Update trending videos
                    if result.get('trending_videos'):
                        for trending in result['trending_videos']:
                            vid_id = trending.get('video_id')
                            if vid_id in fresh_stats_dict:
                                fresh_data = fresh_stats_dict[vid_id]
                                # Update with real-time stats
                                trending.update({
                                    'view_count': fresh_data['view_count'],
                                    'like_count': fresh_data['like_count'],
                                    'comment_count': fresh_data['comment_count'],
                                    'trending_score': fresh_data.get('trending_score', 0),
                                    'hours_since_publish': fresh_data.get('hours_since_publish', 0),
                                })
                    
                    # Update trending shorts
                    if result.get('trending_shorts'):
                        for trending in result['trending_shorts']:
                            vid_id = trending.get('video_id')
                            if vid_id in fresh_stats_dict:
                                fresh_data = fresh_stats_dict[vid_id]
                                # Update with real-time stats
                                trending.update({
                                    'view_count': fresh_data['view_count'],
                                    'like_count': fresh_data['like_count'],
                                    'comment_count': fresh_data['comment_count'],
                                    'trending_score': fresh_data.get('trending_score', 0),
                                    'hours_since_publish': fresh_data.get('hours_since_publish', 0),
                                })
                
                # Update live videos with fresh data
                if real_time_live and result.get('live_videos'):
                    for live in result['live_videos']:
                        vid_id = live.get('video_id')
                        if vid_id in fresh_stats_dict:
                            fresh_data = fresh_stats_dict[vid_id]
                            # Update with real-time stats
                            live.update({
                                'view_count': fresh_data['view_count'],
                                'live_viewers': fresh_data.get('live_viewers'),
                                'is_live': fresh_data.get('is_live', False),
                                'like_count': fresh_data['like_count'],
                                'comment_count': fresh_data['comment_count'],
                            })
                            # Also check if video is still live
                            if not fresh_data.get('is_live', False):
                                # Remove from live list if no longer live
                                result['live_videos'] = [v for v in result['live_videos'] if v.get('video_id') != vid_id]
                                result['total_live'] = len(result['live_videos'])
                    
                    # Re-sort live videos by view count after updating stats
                    # IMPORTANT: Live videos sorted by MOST VIEWS, not publish date
                    # Prioritize concurrent viewers, then total view count (highest first)
                    if result.get('live_videos'):
                        def get_live_sort_key(video):
                            live_viewers = video.get('live_viewers')
                            view_count = video.get('view_count', 0)
                            
                            # Convert to int for proper comparison
                            if live_viewers is None:
                                viewers_int = 0
                            elif isinstance(live_viewers, str):
                                viewers_int = int(live_viewers) if live_viewers.isdigit() else 0
                            else:
                                viewers_int = int(live_viewers)
                            
                            if view_count is None:
                                views_int = 0
                            elif isinstance(view_count, str):
                                views_int = int(view_count) if view_count.isdigit() else 0
                            else:
                                views_int = int(view_count)
                            
                            return (viewers_int, views_int)
                        
                        result['live_videos'] = sorted(result['live_videos'], key=get_live_sort_key, reverse=True)
                        # Only keep the top live video (one with most viewers)
                        if len(result['live_videos']) > 1:
                            logger.info(f"⚠️ Found {len(result['live_videos'])} live videos after update - keeping only the one with most viewers")
                            result['live_videos'] = [result['live_videos'][0]]  # Keep only the first (highest viewers)
                            result['total_live'] = 1  # Update count
                        if result.get('live_videos'):
                            logger.info(f"Top live video: {result['live_videos'][0].get('title', 'Unknown')[:40]} ({result['live_videos'][0].get('live_viewers')} viewers, {result['live_videos'][0].get('view_count')} views)")
        
        # Add quota status to result
        quota_status = self.quota_manager.get_quota_status()
        result['quota_status'] = quota_status
        
        # Final debug logging
        logger.info(f"📤 Returning result for channel {channel_id}:")
        logger.info(f"   Videos: {len(result.get('videos', []))}")
        logger.info(f"   Shorts: {len(result.get('shorts', []))}")
        logger.info(f"   Trending videos: {len(result.get('trending_videos', []))}")
        logger.info(f"   Trending shorts: {len(result.get('trending_shorts', []))}")
        logger.info(f"   🔴 LIVE VIDEOS: {len(result.get('live_videos', []))}")
        if result.get('live_videos'):
            for idx, live in enumerate(result.get('live_videos', [])):
                logger.info(f"      Live {idx+1}: '{live.get('title', 'Unknown')[:50]}' - viewers: {live.get('live_viewers')}, views: {live.get('view_count')}")
        else:
            logger.warning(f"   ⚠️ NO LIVE VIDEOS IN RESULT (channel: {channel_id})")
        
        return result
    
    def get_quota_status(self):
        """Get current quota status"""
        return self.quota_manager.get_quota_status()

