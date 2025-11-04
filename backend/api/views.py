"""
Django REST Framework API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.services.cached_youtube_service import CachedYouTubeService
import requests


class YouTubeAnalyzerAPIView(APIView):
    """
    API endpoint to analyze YouTube channels.
    Accepts POST request with channel URLs and returns ranked videos.
    """
    
    def post(self, request):
        """
        Process channel URLs and return ranked videos.
        Expected request body:
        {
            "channel_urls": ["https://youtube.com/@channel1", "https://youtube.com/@channel2"]
        }
        """
        channel_urls = request.data.get('channel_urls', [])
        
        if not channel_urls:
            return Response(
                {'error': 'No channel URLs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(channel_urls, list):
            return Response(
                {'error': 'channel_urls must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Limit to 10 channels
        if len(channel_urls) > 10:
            return Response(
                {'error': 'Maximum 10 channels allowed per request'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = []
        errors = []
        
        try:
            # Use cached service wrapper for quota management and caching
            youtube_service = CachedYouTubeService()
            
            for channel_url in channel_urls:
                try:
                    # Check if real-time data requested (default to False to use cache)
                    real_time_trending = request.data.get('real_time_trending', False)  # Default to False to use cache
                    real_time_live = request.data.get('real_time_live', False)  # Default to False to use cache
                    
                    channel_data = youtube_service.fetch_channel_videos(
                        channel_url.strip(),
                        max_videos=5,  # Limited to 5
                        max_shorts=5,  # Limited to 5
                        real_time_trending=real_time_trending,
                        real_time_live=real_time_live
                    )
                    # If quota error, make sure it's clear in the response
                    if channel_data.get('error') and 'quota' in channel_data.get('error', '').lower():
                        errors.append({
                            'channel_url': channel_url,
                            'error': channel_data.get('error'),
                            'quota_exceeded': True
                        })
                    else:
                        results.append(channel_data)
                except Exception as e:
                    error_str = str(e)
                    error_info = {
                        'channel_url': channel_url,
                        'error': error_str
                    }
                    # Mark quota errors specially
                    if 'quota' in error_str.lower():
                        error_info['quota_exceeded'] = True
                    errors.append(error_info)
        
        except Exception as e:
            return Response(
                {'error': f'Service error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Get quota status from service
        quota_status = None
        try:
            quota_status = youtube_service.get_quota_status()
        except:
            pass
        
        response_data = {
            'results': results,
            'errors': errors,
            'total_channels_processed': len(results),
            'total_channels_failed': len(errors)
        }
        
        # Add quota status if available
        if quota_status:
            response_data['quota_status'] = quota_status
        
        return Response(response_data, status=status.HTTP_200_OK)


class QuotaStatusAPIView(APIView):
    """API endpoint to check YouTube API quota status"""
    
    def get(self, request):
        try:
            service = CachedYouTubeService()
            quota_status = service.get_quota_status()
            return Response(quota_status, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Could not retrieve quota status: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChannelSearchAPIView(APIView):
    """API endpoint to search for YouTube channels with autocomplete"""
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        max_results = min(int(request.GET.get('max_results', 10)), 20)
        
        if not query or len(query) < 2:
            return Response({'results': []}, status=status.HTTP_200_OK)
        
        channels = []
        
        try:
            from api.services.youtube_service import YouTubeService
            service = YouTubeService()
            
            # Search for channels
            search_response = service.youtube.search().list(
                part='snippet',
                q=query,
                type='channel',
                maxResults=max_results
            ).execute()
            
            # Process results
            for item in search_response.get('items', []):
                snippet = item.get('snippet', {})
                # When type='channel', the id structure is: item['id']['channelId']
                channel_id = item.get('id', {}).get('channelId')
                
                if channel_id:
                    # Get subscriber count
                    subscriber_count = 0
                    try:
                        stats_response = service.youtube.channels().list(
                            part='statistics',
                            id=channel_id
                        ).execute()
                        if stats_response.get('items'):
                            subscriber_count = int(stats_response['items'][0].get('statistics', {}).get('subscriberCount', 0))
                    except Exception as stats_err:
                        # Log but don't fail - subscriber count is optional
                        print(f"Warning: Could not get subscriber count for {channel_id}: {stats_err}")
                    
                    custom_url = snippet.get('customUrl', '')
                    handle_url = None
                    if custom_url:
                        # Clean up custom URL (remove @ and youtube.com/ if present)
                        clean_handle = custom_url.replace('@', '').replace('youtube.com/', '').replace('c/', '')
                        if clean_handle:
                            handle_url = f"https://www.youtube.com/@{clean_handle}"
                    
                    channels.append({
                        'channel_id': channel_id,
                        'channel_name': snippet.get('title', ''),
                        'description': snippet.get('description', '')[:100] if snippet.get('description') else '',
                        'thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
                        'custom_url': custom_url,
                        'subscriber_count': subscriber_count,
                        'url': f"https://www.youtube.com/channel/{channel_id}",
                        'handle_url': handle_url,
                    })
        except Exception as e:
            # Log the error for debugging
            import traceback
            error_msg = str(e)
            print(f"Error in ChannelSearchAPIView: {error_msg}")
            print(traceback.format_exc())
            # Return error info in response for debugging
            return Response({
                'results': [],
                'error': error_msg,
                'debug': 'Check backend logs for details'
            }, status=status.HTTP_200_OK)  # Still return 200 so frontend can handle it
        
        return Response({'results': channels}, status=status.HTTP_200_OK)


class InstagramAnalyzerAPIView(APIView):
    """
    API endpoint to analyze Instagram pages.
    Accepts POST request with page URLs/usernames and returns ranked posts, reels, and videos.
    """
    
    def post(self, request):
        """
        Process Instagram page URLs/usernames and return ranked media.
        Expected request body:
        {
            "page_urls": ["https://instagram.com/username", "username2"]
        }
        """
        page_urls = request.data.get('page_urls', [])
        
        if not page_urls:
            return Response(
                {'error': 'No Instagram page URLs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(page_urls, list):
            return Response(
                {'error': 'page_urls must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Limit to 10 pages
        if len(page_urls) > 10:
            return Response(
                {'error': 'Maximum 10 pages allowed per request'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = []
        errors = []
        
        try:
            from api.services.instagram_service import InstagramService
            instagram_service = InstagramService()
            
            for page_url in page_urls:
                try:
                    page_data = instagram_service.fetch_page_full_data(
                        page_url.strip(),
                        max_posts=5,
                        max_reels=5,
                        max_videos=5
                    )
                    results.append(page_data)
                except Exception as e:
                    error_str = str(e)
                    errors.append({
                        'page_url': page_url,
                        'error': error_str
                    })
        
        except Exception as e:
            return Response(
                {'error': f'Service error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response_data = {
            'results': results,
            'errors': errors,
            'total_pages_processed': len(results),
            'total_pages_failed': len(errors)
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class InstagramPageSearchAPIView(APIView):
    """API endpoint to search for Instagram pages with autocomplete"""
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if not query or len(query) < 2:
            return Response(
                {'error': 'Query must be at least 2 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(query) > 100:
            return Response(
                {'error': 'Query too long (max 100 characters)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        max_results = min(int(request.GET.get('max_results', 10)), 20)  # Max 20 results
        
        try:
            from api.services.instagram_service import InstagramService
            from bs4 import BeautifulSoup
            import json
            import re
            
            instagram_service = InstagramService()
            pages = []
            
            # Method 1: Try Instagram's internal search API (may require auth)
            try:
                # Instagram search endpoint - requires authentication now
                search_url = f"https://www.instagram.com/web/search/topsearch/?query={query}"
                # Use the session from the service which has proper headers
                response = instagram_service.session.get(search_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse users from search results
                    users = data.get('users', [])
                    for user_item in users[:max_results]:
                        user = user_item.get('user', {})
                        username = user.get('username', '')
                        full_name = user.get('full_name', '')
                        profile_pic_url = user.get('profile_pic_url', '')
                        follower_count = user.get('follower_count', 0)
                        is_verified = user.get('is_verified', False)
                        
                        if username:
                            pages.append({
                                'username': username,
                                'full_name': full_name or username,
                                'profile_picture': profile_pic_url,
                                'follower_count': follower_count,
                                'is_verified': is_verified,
                                'url': f"https://www.instagram.com/{username}/",
                                'handle_url': f"https://www.instagram.com/{username}/",
                            })
            
            except Exception as e:
                print(f"Instagram search API error (likely requires auth): {e}")
            
            # Method 2: Use InstagramService's get_page_info method (better extraction)
            # If query looks like a username, use the service method which has better parsing
            if not pages and re.match(r'^[a-zA-Z0-9_.]+$', query) and len(query) > 2:
                try:
                    page_info = instagram_service.get_page_info(query)
                    if page_info:
                        pages.append({
                            'username': page_info.get('username', query),
                            'full_name': page_info.get('full_name', query),
                            'profile_picture': page_info.get('profile_picture', ''),
                            'follower_count': page_info.get('follower_count', 0),
                            'is_verified': page_info.get('is_verified', False),
                            'url': f"https://www.instagram.com/{query}/",
                            'handle_url': f"https://www.instagram.com/{query}/",
                        })
                except Exception as e:
                    print(f"Error fetching page info for {query}: {e}")
                    
                    # Fallback: Simple validation - just check if page exists
                    try:
                        username_url = f"https://www.instagram.com/{query}/"
                        response = instagram_service.session.get(username_url, timeout=5)
                        
                        if response.status_code == 200 and 'login' not in response.url.lower():
                            # Page exists, create basic entry
                            soup = BeautifulSoup(response.text, 'html.parser')
                            title = soup.find('title')
                            full_name = query
                            
                            if title and title.string:
                                title_text = title.string
                                if '@' in title_text:
                                    full_name = title_text.split('@')[0].strip().replace(' • Instagram', '').strip()
                                elif '•' in title_text:
                                    full_name = title_text.split('•')[0].strip()
                            
                            pages.append({
                                'username': query,
                                'full_name': full_name,
                                'profile_picture': '',
                                'follower_count': 0,
                                'is_verified': False,
                                'url': f"https://www.instagram.com/{query}/",
                                'handle_url': f"https://www.instagram.com/{query}/",
                            })
                    except:
                        pass
            
            return Response({
                'query': query,
                'results': pages[:max_results],
                'total_results': len(pages)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Search error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

