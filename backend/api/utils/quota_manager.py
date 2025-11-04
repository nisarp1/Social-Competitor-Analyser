"""
Quota Manager for YouTube API
Tracks API quota usage and prevents exceeding limits
"""
from django.core.cache import cache
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class QuotaManager:
    """Manages YouTube API quota usage and tracking"""
    
    CACHE_KEY_PREFIX = 'youtube_quota'
    DAILY_QUOTA_KEY = f'{CACHE_KEY_PREFIX}:daily'
    HOURLY_QUOTA_KEY = f'{CACHE_KEY_PREFIX}:hourly'
    
    def __init__(self, daily_limit=10000, warning_threshold=8000):
        self.daily_limit = daily_limit
        self.warning_threshold = warning_threshold
        
    def _get_today_key(self):
        """Get cache key for today's date"""
        today = datetime.now(timezone.utc).date().isoformat()
        return f'{self.DAILY_QUOTA_KEY}:{today}'
    
    def _get_current_hour_key(self):
        """Get cache key for current hour"""
        now = datetime.now(timezone.utc)
        hour_key = f'{now.year}-{now.month:02d}-{now.day:02d}-{now.hour:02d}'
        return f'{self.HOURLY_QUOTA_KEY}:{hour_key}'
    
    def get_daily_quota_used(self):
        """Get quota used today"""
        key = self._get_today_key()
        used = cache.get(key, 0)
        return int(used)
    
    def get_remaining_quota(self):
        """Get remaining quota for today"""
        used = self.get_daily_quota_used()
        remaining = self.daily_limit - used
        return max(0, remaining)
    
    def get_quota_percentage(self):
        """Get quota usage percentage"""
        used = self.get_daily_quota_used()
        return (used / self.daily_limit) * 100
    
    def consume_quota(self, units):
        """
        Consume quota units.
        Returns True if quota was consumed successfully, False if quota exceeded.
        """
        key = self._get_today_key()
        current_used = cache.get(key, 0)
        new_used = current_used + units
        
        if new_used > self.daily_limit:
            logger.warning(f"Quota would exceed limit: {new_used} > {self.daily_limit}")
            return False
        
        # Set with expiration at end of day (Pacific Time)
        # Calculate seconds until midnight PST (UTC-8 or UTC-7 for DST)
        now = datetime.now(timezone.utc)
        # Approximate: assume UTC-8 for simplicity (can be improved)
        # Pacific midnight = 08:00 UTC next day
        tomorrow_utc = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if tomorrow_utc <= now:
            tomorrow_utc = tomorrow_utc.replace(day=tomorrow_utc.day + 1)
        seconds_until_reset = (tomorrow_utc - now).total_seconds()
        
        cache.set(key, new_used, timeout=int(seconds_until_reset) + 3600)  # +1 hour buffer
        
        # Track hourly usage
        hour_key = self._get_current_hour_key()
        hourly_used = cache.get(hour_key, 0)
        cache.set(hour_key, hourly_used + units, timeout=3600)
        
        # Log warning if approaching limit
        if new_used >= self.warning_threshold:
            logger.warning(f"Quota usage at {self.get_quota_percentage():.1f}%: {new_used}/{self.daily_limit}")
        
        return True
    
    def can_make_request(self, estimated_units):
        """Check if we can make a request without exceeding quota"""
        current_used = self.get_daily_quota_used()
        if current_used + estimated_units > self.daily_limit:
            return False
        return True
    
    def get_quota_status(self):
        """Get detailed quota status"""
        used = self.get_daily_quota_used()
        remaining = self.get_remaining_quota()
        percentage = self.get_quota_percentage()
        
        return {
            'used': used,
            'limit': self.daily_limit,
            'remaining': remaining,
            'percentage': round(percentage, 2),
            'can_make_requests': remaining > 0,
            'status': 'critical' if percentage >= 90 else 'warning' if percentage >= 80 else 'ok'
        }
    
    def reset_quota(self):
        """Reset quota (for testing/admin purposes)"""
        key = self._get_today_key()
        cache.delete(key)
        logger.info("Quota reset manually")

