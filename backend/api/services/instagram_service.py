"""
Instagram Service Layer
Handles Instagram page data retrieval and analysis.
Uses web scraping since Instagram Graph API requires authentication.
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime, timezone
import time
import json
import logging

logger = logging.getLogger(__name__)

class InstagramService:
    """Service class for interacting with Instagram pages via web scraping"""
    
    # Rotate between multiple realistic user agents to appear more human-like
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self._update_headers()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
    
    def _update_headers(self):
        """Update headers with a random user agent"""
        import random
        user_agent = random.choice(self.USER_AGENTS)
        self.session.headers.update({
            'User-Agent': user_agent,
        })
    
    def _delay(self, seconds: float = 1.0):
        """Add delay between requests to avoid rate limiting"""
        time.sleep(seconds)
    
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
    
    def extract_username_from_url(self, url: str) -> Optional[str]:
        """Extract Instagram username from URL"""
        patterns = [
            r'instagram\.com/([a-zA-Z0-9_.]+)',
            r'instagram\.com/([a-zA-Z0-9_.]+)/',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                username = match.group(1)
                # Remove query parameters if any
                username = username.split('?')[0]
                # Skip Instagram's special pages
                if username not in ['p', 'reel', 'stories', 'explore', 'accounts', 'direct']:
                    return username
        
        # If URL is just a username (without instagram.com)
        if re.match(r'^[a-zA-Z0-9_.]+$', url.strip()):
            return url.strip()
        
        return None
    
    def get_page_info(self, username: str) -> Optional[Dict]:
        """
        Get Instagram page information including:
        - Page name
        - Follower count
        - Following count
        - Post count
        - Profile picture
        """
        try:
            url = f"https://www.instagram.com/{username}/"
            
            # Rotate user agent for each request
            self._update_headers()
            
            # Make request with better headers
            response = self.session.get(
                url, 
                timeout=15,
                allow_redirects=True,
                cookies={'ig_did': '', 'ig_nrcb': '1'}  # Add some basic cookies
            )
            
            # Check for redirects to login page (profile doesn't exist or is private)
            if response.status_code != 200:
                logger.warning(f"Got status {response.status_code} for {username}")
                return None
            
            # Check if redirected to login page
            if 'accounts/login' in response.url.lower() or 'login' in response.url.lower():
                logger.warning(f"Redirected to login page for {username} - profile may be private or not exist")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Instagram stores data in JSON-LD and script tags
            page_info = {
                'username': username,
                'full_name': '',
                'biography': '',
                'profile_picture': '',
                'follower_count': 0,
                'following_count': 0,
                'post_count': 0,
                'is_verified': False,
            }
            
            # Method 1: Look for JSON-LD structured data
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        # Extract from alternateName (username) and name (full name)
                        if 'alternateName' in data:
                            page_info['username'] = data['alternateName'].replace('@', '')
                        if 'name' in data:
                            page_info['full_name'] = data['name']
                        # Get image if available
                        if 'image' in data and not page_info['profile_picture']:
                            image_url = data['image']
                            if isinstance(image_url, str):
                                page_info['profile_picture'] = image_url
                            elif isinstance(image_url, dict):
                                page_info['profile_picture'] = image_url.get('url', '')
                except:
                    pass
            
            # Method 2: Extract from window._sharedData or similar
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'window._sharedData' in script.string:
                    try:
                        match = re.search(r'window\._sharedData = ({.+?});', script.string, re.DOTALL)
                        if match:
                            data = json.loads(match.group(1))
                            user_data = data.get('entry_data', {}).get('ProfilePage', [{}])[0].get('graphql', {}).get('user', {})
                            
                            if user_data:
                                page_info['full_name'] = user_data.get('full_name', '')
                                page_info['username'] = user_data.get('username', username)
                                page_info['biography'] = user_data.get('biography', '')
                                page_info['profile_picture'] = user_data.get('profile_pic_url_hd', '')
                                page_info['follower_count'] = user_data.get('edge_followed_by', {}).get('count', 0)
                                page_info['following_count'] = user_data.get('edge_follow', {}).get('count', 0)
                                page_info['post_count'] = user_data.get('edge_owner_to_timeline_media', {}).get('count', 0)
                                page_info['is_verified'] = user_data.get('is_verified', False)
                                break
                    except Exception as e:
                        logger.debug(f"Error parsing _sharedData: {e}")
            
            # Method 3: Try to extract from JSON embedded in page (Instagram embeds data in script tags)
            # Look for various JSON patterns Instagram might use
            page_text = response.text
            
            # Pattern 1: Look for JSON-LD structured data (most reliable when available)
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        # Extract from alternateName (username) and name (full name)
                        if 'alternateName' in data:
                            page_info['username'] = data['alternateName'].replace('@', '')
                        if 'name' in data and not page_info['full_name']:
                            page_info['full_name'] = data['name']
                        # Get image if available
                        if 'image' in data and not page_info['profile_picture']:
                            image_url = data['image']
                            if isinstance(image_url, str):
                                page_info['profile_picture'] = image_url
                            elif isinstance(image_url, dict):
                                page_info['profile_picture'] = image_url.get('url', '')
                except:
                    pass
            
            # Pattern 2: Look for window._sharedData (most comprehensive data when available)
            shared_data_patterns = [
                r'window\._sharedData\s*=\s*({.+?});',
                r'_sharedData\s*=\s*({.+?});',
                r'<script[^>]*>window\._sharedData\s*=\s*({.+?});</script>',
            ]
            
            for pattern in shared_data_patterns:
                match = re.search(pattern, page_text, re.DOTALL)
                if match:
                    try:
                        json_str = match.group(1)
                        data = json.loads(json_str)
                        user_data = data.get('entry_data', {}).get('ProfilePage', [{}])[0].get('graphql', {}).get('user', {})
                        
                        if user_data:
                            page_info['full_name'] = user_data.get('full_name', '') or page_info['full_name']
                            page_info['username'] = user_data.get('username', username)
                            page_info['biography'] = user_data.get('biography', '') or page_info['biography']
                            
                            # Profile picture - try multiple fields
                            profile_pic = (
                                user_data.get('profile_pic_url_hd') or 
                                user_data.get('profile_pic_url') or
                                page_info['profile_picture']
                            )
                            if profile_pic:
                                page_info['profile_picture'] = profile_pic
                            
                            page_info['follower_count'] = user_data.get('edge_followed_by', {}).get('count', 0) or page_info['follower_count']
                            page_info['following_count'] = user_data.get('edge_follow', {}).get('count', 0) or page_info['following_count']
                            page_info['post_count'] = user_data.get('edge_owner_to_timeline_media', {}).get('count', 0) or page_info['post_count']
                            page_info['is_verified'] = user_data.get('is_verified', False) or page_info['is_verified']
                            break  # Found data, stop searching
                    except Exception as e:
                        logger.debug(f"Error parsing _sharedData pattern {pattern}: {e}")
                        continue
            
            # Method 4: Parse from meta tags (FALLBACK - Instagram serves these when available)
            meta_title = soup.find('meta', {'property': 'og:title'}) or soup.find('meta', {'name': 'og:title'})
            meta_image = soup.find('meta', {'property': 'og:image'}) or soup.find('meta', {'name': 'og:image'})
            meta_description = soup.find('meta', {'property': 'og:description'}) or soup.find('meta', {'name': 'og:description'})
            
            # Only use meta tags if we don't have better data from JSON
            if not page_info['full_name'] and meta_title:
                title = meta_title.get('content', '')
                logger.debug(f"Using meta title for {username}: {title}")
                
                # Parse format: "Name (@username) • Instagram photos and videos"
                if '@' in title:
                    # Extract full name (everything before @, but remove trailing parentheses)
                    name_part = title.split('@')[0].strip()
                    # Remove trailing parenthesis if present (format: "Name (@username)")
                    if name_part.endswith('('):
                        name_part = name_part[:-1].strip()
                    clean_name = name_part.replace(' • Instagram photos and videos', '').replace(' • Instagram', '').strip()
                    if clean_name:
                        page_info['full_name'] = clean_name
                        logger.debug(f"Extracted full name from meta: {clean_name}")
                    
                    # Extract username from title (always update if found)
                    if ')' in title:
                        username_part = title.split('@')[1].split(')')[0].strip()
                        if username_part:
                            page_info['username'] = username_part
            
            # Get profile picture from og:image (ALWAYS use if available, better quality)
            if meta_image:
                img_url = meta_image.get('content', '')
                if img_url and (not page_info['profile_picture'] or 'scontent' not in page_info['profile_picture']):
                    page_info['profile_picture'] = img_url
                    logger.debug(f"Found profile picture from og:image")
            
            # Get biography from og:description
            if meta_description and not page_info['biography']:
                desc = meta_description.get('content', '')
                if desc and len(desc) > 10:  # Basic validation
                    page_info['biography'] = desc[:200]  # Truncate
            
            # Method 5: Parse follower counts from page text (fallback - try multiple patterns)
            if page_info['follower_count'] == 0:
                # Look for follower count patterns in various formats
                follower_patterns = [
                    r'"edge_followed_by":\s*\{\s*"count":\s*(\d+)',
                    r'"follower_count":\s*(\d+)',
                    r'"followed_by":\s*\{\s*"count":\s*(\d+)',
                    r'"followerCount":\s*(\d+)',
                    r'(\d+\.?\d*[KMB]?)\s*followers',
                    r'(\d{1,3}(?:,\d{3})*)\s*followers',
                    r'"edge_followed_by":\{"count":(\d+)',
                ]
                for pattern in follower_patterns:
                    matches = re.finditer(pattern, page_text, re.IGNORECASE)
                    for match in matches:
                        follower_text = match.group(1)
                        if follower_text.replace(',', '').replace('.', '').isdigit():
                            page_info['follower_count'] = int(float(follower_text.replace(',', '')))
                            logger.debug(f"Extracted follower count: {page_info['follower_count']}")
                            break
                        elif any(c in follower_text.upper() for c in ['K', 'M', 'B']):
                            page_info['follower_count'] = self._parse_count(follower_text)
                            logger.debug(f"Extracted follower count (formatted): {page_info['follower_count']}")
                            break
                    if page_info['follower_count'] > 0:
                        break
            
            self._delay()
            return page_info
            
        except Exception as e:
            logger.error(f"Error fetching Instagram page info: {e}")
            return None
    
    def fetch_page_media(self, username: str, max_posts: int = 5, max_reels: int = 5, max_videos: int = 5) -> Dict:
        """
        Fetch media from Instagram page.
        Returns dictionary with posts, reels, and videos separately.
        """
        try:
            url = f"https://www.instagram.com/{username}/"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return {
                    'username': username,
                    'posts': [],
                    'reels': [],
                    'videos': [],
                    'trending_posts': [],
                    'trending_reels': [],
                    'error': f'Could not fetch page (status: {response.status_code})'
                }
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            posts = []
            reels = []
            videos = []
            
            # Extract media from window._sharedData
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'window._sharedData' in script.string:
                    try:
                        match = re.search(r'window\._sharedData = ({.+?});', script.string, re.DOTALL)
                        if match:
                            data = json.loads(match.group(1))
                            user_data = data.get('entry_data', {}).get('ProfilePage', [{}])[0].get('graphql', {}).get('user', {})
                            
                            if user_data:
                                media_edges = user_data.get('edge_owner_to_timeline_media', {}).get('edges', [])
                                
                                for edge in media_edges:
                                    node = edge.get('node', {})
                                    media_type = node.get('__typename', '')
                                    shortcode = node.get('shortcode', '')
                                    caption = node.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', '')
                                    thumbnail = node.get('thumbnail_src', '') or node.get('display_url', '')
                                    timestamp = node.get('taken_at_timestamp', 0)
                                    
                                    # Get engagement metrics
                                    likes = node.get('edge_liked_by', {}).get('count', 0)
                                    comments = node.get('edge_media_to_comment', {}).get('count', 0)
                                    video_view_count = node.get('video_view_count', 0)
                                    
                                    # Determine if it's a video, reel, or post
                                    is_video = node.get('is_video', False)
                                    is_reel = 'REELS' in media_type or 'Reels' in media_type
                                    
                                    media_item = {
                                        'shortcode': shortcode,
                                        'url': f"https://www.instagram.com/p/{shortcode}/",
                                        'caption': caption[:200],  # Truncate
                                        'thumbnail': thumbnail,
                                        'likes': likes,
                                        'comments': comments,
                                        'views': video_view_count if is_video else 0,
                                        'timestamp': timestamp,
                                        'published_at': datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat() if timestamp else '',
                                        'is_video': is_video,
                                        'is_reel': is_reel,
                                    }
                                    
                                    # Calculate if trending (last 3 hours)
                                    if timestamp:
                                        hours_since = (datetime.now(timezone.utc).timestamp() - timestamp) / 3600
                                        media_item['hours_since_publish'] = hours_since
                                        media_item['is_trending'] = hours_since <= 3 and hours_since >= 0
                                    else:
                                        media_item['is_trending'] = False
                                    
                                    # Categorize media
                                    if is_reel:
                                        reels.append(media_item)
                                    elif is_video:
                                        videos.append(media_item)
                                    else:
                                        posts.append(media_item)
                                
                                break
                    except Exception as e:
                        logger.error(f"Error parsing media data: {e}")
            
            # Sort by engagement (likes + comments)
            posts.sort(key=lambda x: x['likes'] + x['comments'], reverse=True)
            reels.sort(key=lambda x: x['likes'] + x['views'], reverse=True)
            videos.sort(key=lambda x: x['likes'] + x['views'], reverse=True)
            
            # Get trending media
            trending_posts = [p for p in posts if p.get('is_trending', False)][:3]
            trending_reels = [r for r in reels if r.get('is_trending', False)][:3]
            
            self._delay()
            
            return {
                'username': username,
                'posts': posts[:max_posts],
                'reels': reels[:max_reels],
                'videos': videos[:max_videos],
                'trending_posts': trending_posts,
                'trending_reels': trending_reels,
                'total_posts': len(posts),
                'total_reels': len(reels),
                'total_videos': len(videos),
                'total_trending_posts': len(trending_posts),
                'total_trending_reels': len(trending_reels),
            }
            
        except Exception as e:
            logger.error(f"Error fetching Instagram media: {e}")
            return {
                'username': username,
                'posts': [],
                'reels': [],
                'videos': [],
                'trending_posts': [],
                'trending_reels': [],
                'error': str(e)
            }
    
    def fetch_page_full_data(self, username_or_url: str, max_posts: int = 5, max_reels: int = 5, max_videos: int = 5) -> Dict:
        """
        Main method: Fetch complete page data including info and media.
        """
        username = self.extract_username_from_url(username_or_url)
        if not username:
            raise ValueError(f"Could not extract username from: {username_or_url}")
        
        # Get page info
        page_info = self.get_page_info(username)
        if not page_info:
            raise ValueError(f"Could not fetch Instagram page: {username}")
        
        # Get media
        media_data = self.fetch_page_media(username, max_posts, max_reels, max_videos)
        
        # Combine results
        result = {
            'username': username,
            'page_url': f"https://www.instagram.com/{username}/",
            'full_name': page_info.get('full_name', username),
            'biography': page_info.get('biography', ''),
            'profile_picture': page_info.get('profile_picture', ''),
            'follower_count': page_info.get('follower_count', 0),
            'following_count': page_info.get('following_count', 0),
            'post_count': page_info.get('post_count', 0),
            'is_verified': page_info.get('is_verified', False),
            **media_data
        }
        
        return result

