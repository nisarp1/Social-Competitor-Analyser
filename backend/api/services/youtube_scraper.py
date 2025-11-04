"""
YouTube Web Scraper Service
Alternative to YouTube API that uses web scraping to avoid quota limits.
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

class YouTubeScraper:
    """Scrapes YouTube data without using the API"""
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def _delay(self, seconds: float = 1.0):
        """Add delay between requests to avoid rate limiting"""
        time.sleep(seconds)
    
    def extract_channel_id_from_url(self, url: str) -> Optional[str]:
        """Extract channel ID from various URL formats"""
        patterns = [
            r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
            r'youtube\.com/@([a-zA-Z0-9_-]+)',
            r'youtube\.com/c/([a-zA-Z0-9_-]+)',
            r'youtube\.com/user/([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                channel_id_or_handle = match.group(1)
                # If it's a handle (@username), we need to resolve it to channel ID
                if '/@' in url or url.startswith('@'):
                    # Try to get channel ID from handle
                    return self._get_channel_id_from_handle(channel_id_or_handle)
                return channel_id_or_handle
        
        return None
    
    def _get_channel_id_from_handle(self, handle: str) -> Optional[str]:
        """Get channel ID from @handle by scraping the channel page"""
        try:
            url = f"https://www.youtube.com/@{handle}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                # Method 1: Extract from canonical URL
                soup = BeautifulSoup(response.text, 'html.parser')
                canonical = soup.find('link', {'rel': 'canonical'})
                if canonical and canonical.get('href'):
                    match = re.search(r'/channel/([a-zA-Z0-9_-]+)', canonical.get('href'))
                    if match:
                        channel_id = match.group(1)
                        logger.info(f"Found channel ID {channel_id} from canonical URL")
                        return channel_id
                
                # Method 2: Look for channel ID in page source (ytInitialData)
                # YouTube stores channel data in ytInitialData JSON
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'var ytInitialData' in script.string:
                        # Extract JSON data
                        match = re.search(r'var ytInitialData = ({.+?});', script.string, re.DOTALL)
                        if match:
                            try:
                                import json
                                data = json.loads(match.group(1))
                                # Navigate through JSON to find channel ID
                                # Structure: metadata.channelMetadataRenderer.externalId
                                metadata = data.get('metadata', {})
                                channel_metadata = metadata.get('channelMetadataRenderer', {})
                                channel_id = channel_metadata.get('externalId')
                                if channel_id:
                                    logger.info(f"Found channel ID {channel_id} from ytInitialData")
                                    return channel_id
                                
                                # Alternative path: header.c4TabbedHeaderRenderer.channelId
                                header = data.get('header', {})
                                c4_header = header.get('c4TabbedHeaderRenderer', {})
                                channel_id = c4_header.get('channelId')
                                if channel_id:
                                    logger.info(f"Found channel ID {channel_id} from header")
                                    return channel_id
                            except Exception as e:
                                logger.debug(f"Error parsing ytInitialData: {e}")
                
                # Method 3: Look for channel ID in JSON-LD structured data
                scripts = soup.find_all('script', type='application/ld+json')
                for script in scripts:
                    try:
                        import json
                        data = json.loads(script.string)
                        if isinstance(data, dict):
                            # Try different possible fields
                            channel_id = data.get('channelId') or data.get('@id')
                            if channel_id:
                                # Extract from URL format if needed
                                match = re.search(r'/channel/([a-zA-Z0-9_-]+)', str(channel_id))
                                if match:
                                    return match.group(1)
                                if re.match(r'^UC[a-zA-Z0-9_-]{22}$', str(channel_id)):
                                    return str(channel_id)
                    except:
                        pass
                
                # Method 4: Look in page source text for channel ID pattern
                # Channel IDs typically start with UC and are 24 characters
                channel_id_pattern = r'"channelId":"(UC[a-zA-Z0-9_-]{22})"'
                matches = re.findall(channel_id_pattern, response.text)
                if matches:
                    # Use first unique match
                    unique_ids = list(set(matches))
                    if unique_ids:
                        logger.info(f"Found channel ID {unique_ids[0]} from page source")
                        return unique_ids[0]
                
                self._delay()
        except Exception as e:
            logger.error(f"Error getting channel ID from handle {handle}: {e}")
        
        return None
    
    def get_channel_info(self, channel_url: str) -> Optional[Dict]:
        """
        Scrape channel information including:
        - Channel name
        - Subscriber count
        - Total views
        - Channel thumbnail
        """
        try:
            channel_id = self.extract_channel_id_from_url(channel_url)
            if not channel_id:
                return None
            
            # Try to access channel page
            if '/channel/' in channel_url:
                url = f"https://www.youtube.com/channel/{channel_id}/about"
            elif '/@' in channel_url:
                handle = re.search(r'/@([^/]+)', channel_url)
                if handle:
                    url = f"https://www.youtube.com/@{handle.group(1)}/about"
                else:
                    url = f"https://www.youtube.com/channel/{channel_id}/about"
            else:
                url = f"https://www.youtube.com/channel/{channel_id}/about"
            
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract channel name
            channel_name = None
            title_tag = soup.find('title')
            if title_tag:
                channel_name = title_tag.string.replace(' - YouTube', '').strip()
            
            # Try to find channel name in meta tags or structured data
            if not channel_name:
                meta_title = soup.find('meta', {'property': 'og:title'})
                if meta_title:
                    channel_name = meta_title.get('content', '').replace(' - YouTube', '').strip()
            
            # Extract subscriber count
            subscriber_count = 0
            subscriber_text = None
            
            # Look for subscriber count in various formats
            # Pattern: "X subscribers" or "X.XM subscribers"
            subscriber_patterns = [
                r'(\d+\.?\d*[KMB]?)\s*subscribers',
                r'(\d+\.?\d*[KMB]?)\s*abonnenten',  # German
                r'"subscriberCountText":\s*"([^"]+)"',
                r'"subscriberCount":\s*"([^"]+)"',
            ]
            
            page_text = response.text
            
            for pattern in subscriber_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    subscriber_text = match.group(1)
                    break
            
            # Convert subscriber text to number
            if subscriber_text:
                subscriber_count = self._parse_count(subscriber_text)
            
            # Extract total views (channel views)
            view_count = 0
            # Look for "X views" in channel stats
            view_patterns = [
                r'(\d+\.?\d*[KMB]?)\s*views',
                r'"viewCount":\s*"(\d+)"',
                r'"viewCountText":\s*"([^"]+)"',
            ]
            
            for pattern in view_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    view_text = match.group(1)
                    view_count = self._parse_count(view_text)
                    break
            
            # Extract thumbnail
            channel_thumbnail = None
            meta_image = soup.find('meta', {'property': 'og:image'})
            if meta_image:
                channel_thumbnail = meta_image.get('content')
            
            # Try to get from channel avatar
            if not channel_thumbnail:
                img_tag = soup.find('img', {'id': 'img', 'class': 'style-scope yt-img-shadow'})
                if img_tag:
                    channel_thumbnail = img_tag.get('src') or img_tag.get('data-src')
            
            self._delay()
            
            return {
                'channel_id': channel_id,
                'channel_name': channel_name or 'Unknown Channel',
                'subscriber_count': subscriber_count,
                'view_count': view_count,
                'channel_thumbnail': channel_thumbnail or '',
                'video_count': 0,  # Hard to get accurately via scraping
                'published_at': '',
                'country': '',
            }
            
        except Exception as e:
            logger.error(f"Error scraping channel info: {e}")
            return None
    
    def _parse_count(self, text: str) -> int:
        """Parse counts like '1.2M', '500K', '1234' into integers"""
        if not text:
            return 0
        
        text = text.replace(',', '').strip().upper()
        
        # Handle millions
        if 'M' in text:
            number = float(text.replace('M', ''))
            return int(number * 1_000_000)
        
        # Handle thousands
        if 'K' in text:
            number = float(text.replace('K', ''))
            return int(number * 1_000)
        
        # Handle billions
        if 'B' in text:
            number = float(text.replace('B', ''))
            return int(number * 1_000_000_000)
        
        # Regular number
        try:
            return int(float(text))
        except:
            return 0
    
    def get_video_list(self, channel_id: str, max_results: int = 50) -> List[Dict]:
        """
        Scrape list of videos from channel page.
        Returns basic video info (no view counts - need to scrape individual pages).
        """
        try:
            url = f"https://www.youtube.com/channel/{channel_id}/videos"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            videos = []
            
            # YouTube uses JSON-LD or script tags with video data
            # Look for ytInitialData
            scripts = soup.find_all('script')
            video_data = None
            
            for script in scripts:
                if script.string and 'var ytInitialData' in script.string:
                    # Extract JSON data
                    match = re.search(r'var ytInitialData = ({.+?});', script.string, re.DOTALL)
                    if match:
                        try:
                            import json
                            video_data = json.loads(match.group(1))
                            break
                        except:
                            pass
            
            if not video_data:
                logger.warning("Could not extract video data from page")
                return []
            
            # Navigate through JSON structure to find videos
            # This structure can change, so this is a simplified version
            try:
                contents = video_data.get('contents', {})
                two_column = contents.get('twoColumnBrowseResultsRenderer', {})
                tabs = two_column.get('tabs', [])
                
                for tab in tabs:
                    tab_renderer = tab.get('tabRenderer', {})
                    if tab_renderer.get('title', '').lower() == 'videos':
                        content = tab_renderer.get('content', {})
                        section_list = content.get('sectionListRenderer', {})
                        items = section_list.get('contents', [])
                        
                        for item in items:
                            item_section = item.get('itemSectionRenderer', {})
                            contents_list = item_section.get('contents', [])
                            
                            for content_item in contents_list:
                                grid = content_item.get('gridRenderer', {})
                                items_list = grid.get('items', [])
                                
                                for video_item in items_list[:max_results]:
                                    video_renderer = video_item.get('gridVideoRenderer', {})
                                    if video_renderer:
                                        video_id = video_renderer.get('videoId')
                                        title = video_renderer.get('title', {}).get('runs', [{}])[0].get('text', '')
                                        
                                        if video_id:
                                            videos.append({
                                                'video_id': video_id,
                                                'title': title,
                                                'thumbnail': f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                                            })
                                            
                                            if len(videos) >= max_results:
                                                break
            except Exception as e:
                logger.error(f"Error parsing video list: {e}")
            
            self._delay()
            return videos
            
        except Exception as e:
            logger.error(f"Error scraping video list: {e}")
            return []
    
    def get_video_stats(self, video_id: str) -> Optional[Dict]:
        """Scrape individual video page for view count and other stats"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for view count in various locations
            view_count = 0
            
            # Pattern 1: In meta tags
            meta_views = soup.find('meta', {'itemprop': 'interactionCount'})
            if meta_views:
                view_count = int(meta_views.get('content', 0))
            
            # Pattern 2: In page text
            if view_count == 0:
                view_pattern = r'"viewCount":\s*"(\d+)"'
                match = re.search(view_pattern, response.text)
                if match:
                    view_count = int(match.group(1))
            
            # Pattern 3: In text (e.g., "1,234,567 views")
            if view_count == 0:
                view_pattern = r'(\d{1,3}(?:,\d{3})*)\s*views'
                match = re.search(view_pattern, response.text)
                if match:
                    view_text = match.group(1).replace(',', '')
                    try:
                        view_count = int(view_text)
                    except:
                        pass
            
            # Get like count (if available)
            like_count = 0
            like_pattern = r'"likeCount":\s*"(\d+)"'
            match = re.search(like_pattern, response.text)
            if match:
                like_count = int(match.group(1))
            
            # Get published date
            published_at = ''
            pub_pattern = r'"uploadDate":\s*"([^"]+)"'
            match = re.search(pub_pattern, response.text)
            if match:
                published_at = match.group(1)
            
            self._delay(0.5)  # Shorter delay for individual pages
            
            return {
                'video_id': video_id,
                'view_count': view_count,
                'like_count': like_count,
                'comment_count': 0,  # Hard to get without API
                'published_at': published_at,
            }
            
        except Exception as e:
            logger.error(f"Error scraping video stats for {video_id}: {e}")
            return None

