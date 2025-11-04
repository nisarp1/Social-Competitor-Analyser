"""
Rate Limiter for YouTube API Calls
Prevents API call bursts that could trigger rate limits
"""
from django.core.cache import cache
from datetime import datetime, timezone
import time
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting for API calls"""
    
    def __init__(self, max_per_second=5, max_per_minute=100):
        self.max_per_second = max_per_second
        self.max_per_minute = max_per_minute
    
    def _get_window_key(self, window_type):
        """Get cache key for rate limit window"""
        now = datetime.now(timezone.utc)
        if window_type == 'second':
            return f'ratelimit:second:{now.timestamp():.0f}'
        elif window_type == 'minute':
            return f'ratelimit:minute:{now.year}-{now.month:02d}-{now.day:02d}-{now.hour:02d}-{now.minute:02d}'
    
    def can_make_request(self):
        """Check if we can make a request without violating rate limits"""
        # Check per-second limit
        second_key = self._get_window_key('second')
        second_count = cache.get(second_key, 0)
        
        if second_count >= self.max_per_second:
            logger.warning(f"Rate limit: {second_count} requests in current second")
            return False
        
        # Check per-minute limit
        minute_key = self._get_window_key('minute')
        minute_count = cache.get(minute_key, 0)
        
        if minute_count >= self.max_per_minute:
            logger.warning(f"Rate limit: {minute_count} requests in current minute")
            return False
        
        return True
    
    def record_request(self):
        """Record that a request was made"""
        # Increment second counter (expires in 2 seconds)
        second_key = self._get_window_key('second')
        cache.set(second_key, cache.get(second_key, 0) + 1, timeout=2)
        
        # Increment minute counter (expires in 61 seconds)
        minute_key = self._get_window_key('minute')
        cache.set(minute_key, cache.get(minute_key, 0) + 1, timeout=61)
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        if not self.can_make_request():
            # Wait until next second
            time.sleep(1)
            # Retry once
            if not self.can_make_request():
                time.sleep(1)

