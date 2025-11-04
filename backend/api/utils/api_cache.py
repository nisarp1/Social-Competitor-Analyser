"""
API Response Caching Layer
Caches YouTube API responses to minimize API calls and quota usage
"""
from django.core.cache import cache
from django.conf import settings
import hashlib
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class APICache:
    """Caching layer for YouTube API responses"""
    
    CACHE_PREFIX = 'youtube_api'
    
    @staticmethod
    def _generate_cache_key(endpoint, params):
        """Generate a cache key from endpoint and parameters"""
        # Sort params for consistent key generation
        sorted_params = json.dumps(params, sort_keys=True)
        key_string = f"{endpoint}:{sorted_params}"
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{APICache.CACHE_PREFIX}:{endpoint}:{key_hash}"
    
    @staticmethod
    def get(endpoint, params, ttl=None):
        """
        Get cached API response.
        Returns (data, is_cached) tuple
        """
        cache_key = APICache._generate_cache_key(endpoint, params)
        
        # Get TTL from settings if not provided
        if ttl is None:
            ttl_map = {
                'channel_videos': settings.CACHE_TTL.get('channel_videos', 3600),
                'video_statistics': settings.CACHE_TTL.get('video_statistics', 1800),
                'channel_info': settings.CACHE_TTL.get('channel_info', 86400),
                'trending_videos': settings.CACHE_TTL.get('trending_videos', 300),
                'live_videos': settings.CACHE_TTL.get('live_videos', 60),
                'playlist_items': settings.CACHE_TTL.get('playlist_items', 1800),
            }
            ttl = ttl_map.get(endpoint, 1800)  # Default 30 minutes
        
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.debug(f"Cache HIT for {endpoint}")
            return cached_data, True
        
        logger.debug(f"Cache MISS for {endpoint}")
        return None, False
    
    @staticmethod
    def set(endpoint, params, data, ttl=None):
        """Cache API response"""
        cache_key = APICache._generate_cache_key(endpoint, params)
        
        # Get TTL from settings if not provided
        if ttl is None:
            ttl_map = {
                'channel_videos': settings.CACHE_TTL.get('channel_videos', 3600),
                'video_statistics': settings.CACHE_TTL.get('video_statistics', 1800),
                'channel_info': settings.CACHE_TTL.get('channel_info', 86400),
                'trending_videos': settings.CACHE_TTL.get('trending_videos', 300),
                'live_videos': settings.CACHE_TTL.get('live_videos', 60),
                'playlist_items': settings.CACHE_TTL.get('playlist_items', 1800),
            }
            ttl = ttl_map.get(endpoint, 1800)
        
        # Add metadata
        cached_data = {
            'data': data,
            'cached_at': datetime.now(timezone.utc).isoformat(),
            'endpoint': endpoint,
        }
        
        try:
            cache.set(cache_key, cached_data, timeout=ttl)
            logger.debug(f"Cached {endpoint} for {ttl}s")
            return True
        except Exception as e:
            logger.error(f"Failed to cache {endpoint}: {e}")
            return False
    
    @staticmethod
    def invalidate_channel(channel_id):
        """Invalidate all cache entries for a specific channel"""
        # This is a simplified version - in production, you might want to track
        # all keys for a channel and invalidate them specifically
        logger.info(f"Cache invalidation requested for channel {channel_id}")
        # For now, we rely on TTL-based expiration
    
    @staticmethod
    def clear_all():
        """Clear all API cache (admin function)"""
        # In production with Redis, you'd use: cache.delete_pattern('youtube_api:*')
        logger.warning("Cache clear requested - this requires manual Redis cache flush or pattern deletion")

