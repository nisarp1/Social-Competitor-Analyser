import React, { useState } from 'react';
import {
  Box,
  Card,
  CardMedia,
  Typography,
  Chip,
  Tabs,
  Tab,
  Button,
  Paper,
  Avatar,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { Add, LiveTv, Visibility } from '@mui/icons-material';

const WireframeLayout = ({ results }) => {
  const [selectedTab, setSelectedTab] = useState({});
  const [selectedSourceTab, setSelectedSourceTab] = useState({});
  const [trendingTimeRange, setTrendingTimeRange] = useState({});
  const [popularTimeRange, setPopularTimeRange] = useState({});

  const handleTabChange = (channelIndex, value) => {
    setSelectedTab({ ...selectedTab, [channelIndex]: value });
  };

  const handleSourceTabChange = (sourceIndex, value) => {
    setSelectedSourceTab({ ...selectedSourceTab, [sourceIndex]: value });
  };

  const handleTrendingTimeRangeChange = (sourceIndex, channelIndex, value) => {
    setTrendingTimeRange({ ...trendingTimeRange, [`${sourceIndex}-${channelIndex}`]: value });
  };

  const handlePopularTimeRangeChange = (sourceIndex, channelIndex, value) => {
    setPopularTimeRange({ ...popularTimeRange, [`${sourceIndex}-${channelIndex}`]: value });
  };

  const formatNumber = (num) => {
    if (!num) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const getTimeSincePublish = (dateString) => {
    if (!dateString) return 0;
    const publishDate = new Date(dateString);
    const now = new Date();
    return (now - publishDate) / (1000 * 60 * 60); // hours
  };

  const calculateViewsPerTimeUnit = (viewCount, hoursSincePublish, timeRange) => {
    if (!viewCount || !hoursSincePublish || hoursSincePublish <= 0) return 0;
    
    const hoursMap = {
      '30min': 0.5,
      '1hr': 1,
      '1day': 24,
      '1month': 24 * 30,
      '1year': 24 * 365,
      'alltime': hoursSincePublish
    };
    
    const timeUnit = hoursMap[timeRange] || hoursSincePublish;
    if (hoursSincePublish < timeUnit) return viewCount; // If video is newer than time range
    return Math.round(viewCount / (hoursSincePublish / timeUnit));
  };

  if (!results || !results.results || results.results.length === 0) {
    return null;
  }

  // Group channels into sources - each channel becomes a source
  // Remove duplicates by channel_id to prevent duplication
  const channels = results.results || [];
  
  // Enhanced deduplication: handle null/undefined channel_ids properly
  const uniqueChannels = channels.filter((channel, index, self) => {
    const channelId = channel?.channel_id;
    // If channel_id is null/undefined, treat each channel as unique by index
    if (!channelId) {
      return index === self.findIndex((c, i) => i === index && !c?.channel_id);
    }
    // If channel_id exists, deduplicate by channel_id
    return index === self.findIndex(c => c?.channel_id === channelId);
  });
  
  // Debug: Check for potential issues
  console.log('🔍 Deduplication Debug:', {
    total_channels: channels.length,
    unique_channels: uniqueChannels.length,
    channels_with_null_id: channels.filter(c => !c?.channel_id).length,
    channel_ids: channels.map(c => c?.channel_id),
    unique_channel_ids: uniqueChannels.map(c => c?.channel_id)
  });
  
  // Debug: Log full channel data to see what we have
  console.log('📊 Full Channels data:', uniqueChannels);
  console.log('📋 Channels summary:', uniqueChannels.map(c => ({
    channel_name: c?.channel_name,
    snippet_title: c?.snippet_title,
    channel_id: c?.channel_id,
    subscriber_count: c?.subscriber_count,
    videos_count: c?.videos?.length || 0,
    shorts_count: c?.shorts?.length || 0,
    trending_videos_count: c?.trending_videos?.length || 0,
    trending_shorts_count: c?.trending_shorts?.length || 0,
    live_videos_count: c?.live_videos?.length || 0,
    view_count: c?.view_count,
    has_thumbnail: !!c?.channel_thumbnail,
    all_keys: c ? Object.keys(c).filter(k => k.includes('subscriber') || k.includes('view_count') || k.includes('name') || k.includes('channel') || k.includes('title')) : [],
    full_object: c  // Full object for inspection
  })));
  
  // Each channel is a separate source (up to 3 sources shown)
  const sources = uniqueChannels.slice(0, 3).map(channel => [channel]); // Each source contains one channel
  
  // Pad with empty sources if we have fewer than 3 channels
  while (sources.length < 3) {
    sources.push([]);
  }
  
  // Debug: Log sources structure
  console.log('Sources structure:', sources.map((src, idx) => ({
    sourceIndex: idx,
    hasChannel: src.length > 0,
    channelName: src[0]?.channel_name,
    channelId: src[0]?.channel_id
  })));

  return (
    <Box sx={{ width: '100%', minHeight: '100vh', p: 2 }}>
      <Box 
        sx={{ 
          width: '100%',
          display: 'flex',
          flexDirection: { xs: 'column', sm: 'row', md: 'row' },
          gap: 2,
        }}
      >
        {/* Three Source Columns - Each taking 1/3 width for single-row layout */}
        {sources.map((sourceChannels, sourceIndex) => (
          <Box
            key={sourceIndex}
            sx={{ 
              display: 'flex',
              flexDirection: 'column',
              width: { xs: '100%', sm: 'calc(33.333% - 16px)', md: 'calc(33.333% - 16px)' },
              minWidth: { xs: '100%', sm: 'calc(33.333% - 16px)', md: 'calc(33.333% - 16px)' },
              flexShrink: 0,
            }}
          >
            <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', width: '100%' }}>
              {/* Source Header - Shows channel name */}
              <Paper
                elevation={2}
                sx={{
                  bgcolor: 'primary.main',
                  color: 'primary.contrastText',
                  p: 2,
                  mb: 2,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flex: 1 }}>
                    {sourceChannels.length > 0 && sourceChannels[0]?.channel_thumbnail && (
                      <Avatar
                        src={sourceChannels[0].channel_thumbnail}
                        alt={sourceChannels[0].channel_name || `Source ${sourceIndex + 1}`}
                        sx={{ width: 32, height: 32 }}
                      />
                    )}
                    <Typography variant="h6" fontWeight="bold">
                      {(() => {
                        const channel = sourceChannels.length > 0 ? sourceChannels[0] : null;
                        const channelName = channel?.channel_name;
                        
                        // Debug log
                        if (sourceIndex < 3) {
                          console.log(`Source ${sourceIndex + 1}:`, {
                            hasChannel: !!channel,
                            channelName: channelName,
                            channelId: channel?.channel_id,
                            allKeys: channel ? Object.keys(channel) : []
                          });
                        }
                        
                        if (channelName && channelName.trim()) {
                          return channelName.trim();
                        }
                        return `Source ${sourceIndex + 1}`;
                      })()}
                    </Typography>
                  </Box>
                  
                  {/* Subscriber Count and Total Views */}
                  {sourceChannels.length > 0 && sourceChannels[0] && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                      <Chip
                        label={`${formatNumber(sourceChannels[0].subscriber_count ?? 0)} subscribers`}
                        size="small"
                        sx={{
                          bgcolor: 'rgba(255, 255, 255, 0.2)',
                          color: 'primary.contrastText',
                          fontWeight: 'medium',
                        }}
                      />
                      <Chip
                        label={`${formatNumber(sourceChannels[0].view_count ?? 0)} total views`}
                        size="small"
                        sx={{
                          bgcolor: 'rgba(255, 255, 255, 0.2)',
                          color: 'primary.contrastText',
                          fontWeight: 'medium',
                        }}
                      />
                    </Box>
                  )}
                </Box>
              </Paper>

              {/* Add Button for empty sources */}
              {sourceChannels.length === 0 && (
                <Paper
                  elevation={1}
                  sx={{
                    bgcolor: 'grey.300',
                    p: 4,
                    mb: 2,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    '&:hover': { bgcolor: 'grey.400' },
                  }}
                  onClick={() => {
                    // TODO: Add channel functionality
                    console.log('Add channel clicked');
                  }}
                >
                  <Add sx={{ fontSize: 40, color: 'grey.700' }} />
                </Paper>
              )}

              {/* Channel Content */}
              {sourceChannels.map((channel, channelIndex) => {
                // Debug logging for each channel
                console.log(`🔍 Source ${sourceIndex + 1}, Channel ${channelIndex + 1}:`, {
                  channel_name: channel?.channel_name,
                  channel_id: channel?.channel_id,
                  live_videos: channel?.live_videos,
                  live_videos_length: channel?.live_videos?.length || 0,
                  live_videos_type: Array.isArray(channel?.live_videos) ? 'array' : typeof channel?.live_videos,
                  trending_videos: channel?.trending_videos,
                  trending_videos_length: channel?.trending_videos?.length || 0,
                  trending_shorts: channel?.trending_shorts,
                  trending_shorts_length: channel?.trending_shorts?.length || 0,
                  all_keys: channel ? Object.keys(channel) : []
                });
                
                return (
                <Box key={`channel-${channel?.channel_id || channelIndex}`} sx={{ mb: 3 }}>
                  {/* Live Videos Section - Show ALL live videos */}
                  {channel.live_videos && Array.isArray(channel.live_videos) && channel.live_videos.length > 0 ? (
                    <Box sx={{ mb: 3 }}>
                      {channel.live_videos.map((liveVideo, liveIndex) => (
                        <Card
                          key={liveVideo.video_id || liveIndex}
                          elevation={2}
                          sx={{
                            mb: channel.live_videos.length > 1 && liveIndex < channel.live_videos.length - 1 ? 2 : 0,
                            display: 'flex',
                            gap: 2,
                            p: 2,
                          }}
                        >
                          <CardMedia
                            component="img"
                            sx={{
                              width: 140,
                              height: 100,
                              flexShrink: 0,
                              borderRadius: 1,
                            }}
                            image={liveVideo.thumbnail}
                            alt={liveVideo.title}
                          />
                          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                            <Box>
                              <Chip
                                icon={<LiveTv />}
                                label="LIVE"
                                color="error"
                                size="small"
                                sx={{ mb: 1 }}
                              />
                              <Typography variant="body1" fontWeight="medium" sx={{ mb: 0.5 }}>
                                {liveVideo.title || 'Live Video Title and details'}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {formatDate(liveVideo.published_at)}
                              </Typography>
                            </Box>
                          </Box>
                          <Chip
                            label={(() => {
                              const liveViewers = liveVideo.live_viewers;
                              if (liveViewers && !isNaN(liveViewers)) {
                                const viewers = typeof liveViewers === 'string' ? parseInt(liveViewers) : liveViewers;
                                if (viewers > 0) {
                                  return formatNumber(viewers);
                                }
                              }
                              return formatNumber(liveVideo.view_count || 0);
                            })()}
                            color="primary"
                            sx={{ alignSelf: 'flex-start', fontWeight: 'bold', fontSize: '1rem', px: 2 }}
                          />
                        </Card>
                      ))}
                    </Box>
                  ) : (
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="body2" color="text.secondary" fontStyle="italic">
                        No live videos
                      </Typography>
                      {channel.live_videos !== undefined && (
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                          (Debug: live_videos = {JSON.stringify(channel.live_videos).substring(0, 100)})
                        </Typography>
                      )}
                    </Box>
                  )}

                  {/* Trending Section */}
                  {((channel.trending_videos && Array.isArray(channel.trending_videos) && channel.trending_videos.length > 0) || 
                    (channel.trending_shorts && Array.isArray(channel.trending_shorts) && channel.trending_shorts.length > 0)) && (
                    <Box sx={{ mb: 3 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                        <Typography 
                          variant="h6" 
                          fontWeight="bold" 
                          sx={{ color: 'error.main' }}
                        >
                          🔥 Trending
                        </Typography>
                        <FormControl size="small" sx={{ minWidth: 150 }}>
                          <Select
                            value={trendingTimeRange[`${sourceIndex}-${channelIndex}`] || '1hr'}
                            onChange={(e) => handleTrendingTimeRangeChange(sourceIndex, channelIndex, e.target.value)}
                          >
                            <MenuItem value="30min">Last 30 Minutes</MenuItem>
                            <MenuItem value="1hr">1 Hour</MenuItem>
                            <MenuItem value="1day">1 Day</MenuItem>
                          </Select>
                        </FormControl>
                      </Box>
                      
                      {/* Tabs for Trending */}
                      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
                        <Tabs
                          value={selectedTab[`trending-${sourceIndex}-${channelIndex}`] || 0}
                          onChange={(e, val) => handleTabChange(`trending-${sourceIndex}-${channelIndex}`, val)}
                        >
                          <Tab label="Videos" />
                          <Tab label="Shorts" />
                        </Tabs>
                      </Box>

                      {/* Trending Content based on selected tab */}
                      {(() => {
                        const isShorts = selectedTab[`trending-${sourceIndex}-${channelIndex}`] === 1;
                        const timeRange = trendingTimeRange[`${sourceIndex}-${channelIndex}`] || '1hr';
                        let videoList = isShorts
                          ? (channel.trending_shorts || [])
                          : (channel.trending_videos || []);

                        // Filter videos based on time range
                        const hoursMap = {
                          '30min': 0.5,
                          '1hr': 1,
                          '1day': 24
                        };
                        const maxHours = hoursMap[timeRange] || 1;
                        videoList = videoList.filter(video => {
                          const hours = video.hours_since_publish || getTimeSincePublish(video.published_at);
                          return hours <= maxHours && hours >= 0;
                        });

                        return videoList.length > 0 ? (
                          videoList.slice(0, 3).map((video, videoIndex) => {
                            const hoursSincePublish = video.hours_since_publish || getTimeSincePublish(video.published_at);
                            const viewsPerTimeUnit = calculateViewsPerTimeUnit(video.view_count, hoursSincePublish, timeRange);
                            const timeLabel = timeRange === '30min' ? '30 min' : timeRange === '1hr' ? 'hour' : 'day';
                            
                            return (
                            <Card
                              key={videoIndex}
                              elevation={1}
                              sx={{
                                mb: 1.5,
                                display: 'flex',
                                gap: 1.5,
                                p: 1.5,
                              }}
                            >
                              <CardMedia
                                component="img"
                                sx={{
                                  width: 100,
                                  height: 75,
                                  flexShrink: 0,
                                  borderRadius: 1,
                                }}
                                image={video.thumbnail}
                                alt={video.title}
                              />
                              <Box sx={{ flex: 1, minWidth: 0 }}>
                                <Typography 
                                  variant="body2" 
                                  fontWeight="medium" 
                                  sx={{ mb: 0.5 }}
                                >
                                  {video.title || 'Video Details'}
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                  <Chip
                                    label={`${formatNumber(video.view_count || 0)} views`}
                                    size="small"
                                    variant="outlined"
                                  />
                                  <Chip
                                    label={`${formatNumber(viewsPerTimeUnit)} views/${timeLabel}`}
                                    size="small"
                                    variant="outlined"
                                    color="error"
                                  />
                                  <Chip
                                    label={formatDate(video.published_at)}
                                    size="small"
                                    variant="outlined"
                                  />
                                </Box>
                              </Box>
                            </Card>
                            );
                          })
                        ) : (
                          <Box sx={{ textAlign: 'center', py: 3 }}>
                            <Typography variant="body2" color="text.secondary">
                              No trending {isShorts ? 'shorts' : 'videos'} found
                            </Typography>
                          </Box>
                        );
                      })()}
                    </Box>
                  )}

                      {/* Popular Section */}
                      <Box sx={{ mb: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                          <Typography 
                            variant="h6" 
                            fontWeight="bold" 
                            sx={{ color: 'primary.main' }}
                          >
                            📊 Popular
                          </Typography>
                          <FormControl size="small" sx={{ minWidth: 150 }}>
                            <Select
                              value={popularTimeRange[`${sourceIndex}-${channelIndex}`] || 'alltime'}
                              onChange={(e) => handlePopularTimeRangeChange(sourceIndex, channelIndex, e.target.value)}
                            >
                              <MenuItem value="1month">This Month</MenuItem>
                              <MenuItem value="1year">This Year</MenuItem>
                              <MenuItem value="alltime">All Time</MenuItem>
                            </Select>
                          </FormControl>
                        </Box>
                        
                        {/* Video Details Listings - Repeat twice as per wireframe */}
                        {[0, 1].map((rowIndex) => (
                          <Box key={rowIndex} sx={{ mb: 3 }}>
                            {/* Tabs */}
                            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
                              <Tabs
                                value={selectedSourceTab[`${sourceIndex}-${channelIndex}-${rowIndex}`] || 0}
                                onChange={(e, val) => handleSourceTabChange(`${sourceIndex}-${channelIndex}-${rowIndex}`, val)}
                              >
                                <Tab label="Videos" />
                                <Tab label="Shorts" />
                              </Tabs>
                            </Box>

                          {/* Video Cards - Show 3 cards per row */}
                          {(() => {
                            const isShorts = selectedSourceTab[`${sourceIndex}-${channelIndex}-${rowIndex}`] === 1;
                            const timeRange = popularTimeRange[`${sourceIndex}-${channelIndex}`] || 'alltime';
                            
                            // Debug logging
                            console.log(`Source ${sourceIndex}, Channel ${channelIndex}, Row ${rowIndex}:`, {
                              isShorts,
                              videosCount: channel.videos?.length || 0,
                              shortsCount: channel.shorts?.length || 0,
                              hasVideos: !!channel.videos,
                              hasShorts: !!channel.shorts
                            });
                            
                            let videoList = isShorts
                              ? (channel.shorts || [])
                              : (channel.videos || []);
                            
                            console.log(`Video list length: ${videoList.length}`);

                            // Filter videos based on time range
                            const hoursMap = {
                              '1month': 24 * 30,
                              '1year': 24 * 365,
                              'alltime': Infinity
                            };
                            const maxHours = hoursMap[timeRange] || Infinity;
                            if (timeRange !== 'alltime') {
                              videoList = videoList.filter(video => {
                                const hours = getTimeSincePublish(video.published_at);
                                return hours <= maxHours;
                              });
                            }

                            // Sort by view count for the selected time range
                            videoList = [...videoList].sort((a, b) => {
                              const hoursA = getTimeSincePublish(a.published_at);
                              const hoursB = getTimeSincePublish(b.published_at);
                              const viewsPerUnitA = calculateViewsPerTimeUnit(a.view_count, hoursA, timeRange);
                              const viewsPerUnitB = calculateViewsPerTimeUnit(b.view_count, hoursB, timeRange);
                              return viewsPerUnitB - viewsPerUnitA;
                            });

                            // Only slice if we have videos - otherwise show empty state
                            const startIndex = rowIndex * 3;
                            const endIndex = startIndex + 3;
                            const slicedList = videoList.slice(startIndex, endIndex);
                            
                            console.log(`Sliced video list: start=${startIndex}, end=${endIndex}, length=${slicedList.length}, total=${videoList.length}`);

                            return slicedList.length > 0 ? (
                              slicedList.map((video, videoIndex) => {
                                const hoursSincePublish = getTimeSincePublish(video.published_at);
                                const viewsPerTimeUnit = calculateViewsPerTimeUnit(video.view_count, hoursSincePublish, timeRange);
                                const timeLabel = timeRange === '1month' ? 'month' : timeRange === '1year' ? 'year' : 'all time';
                                
                                // Debug each video
                                console.log(`Rendering video ${videoIndex}:`, {
                                  title: video.title,
                                  video_id: video.video_id,
                                  view_count: video.view_count
                                });
                                
                                return (
                                  <Card
                                    key={videoIndex}
                                    elevation={1}
                                    sx={{
                                      mb: 2,
                                      display: 'flex',
                                      gap: 2,
                                      p: 1.5,
                                    }}
                                  >
                                    <CardMedia
                                      component="img"
                                      sx={{
                                        width: 120,
                                        height: 90,
                                        flexShrink: 0,
                                        borderRadius: 1,
                                      }}
                                      image={video.thumbnail}
                                      alt={video.title}
                                    />
                                    <Box sx={{ flex: 1, minWidth: 0 }}>
                                      <Typography 
                                        variant="body2" 
                                        fontWeight="medium" 
                                        sx={{ mb: 1 }}
                                      >
                                        {video.title || 'Video Details'}
                                      </Typography>
                                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                        <Chip
                                          label={`${formatNumber(video.view_count || 0)} views`}
                                          size="small"
                                          variant="outlined"
                                        />
                                        <Chip
                                          label={`${formatNumber(viewsPerTimeUnit)} views/${timeLabel}`}
                                          size="small"
                                          variant="outlined"
                                          color="primary"
                                        />
                                        <Chip
                                          label={formatDate(video.published_at)}
                                          size="small"
                                          variant="outlined"
                                        />
                                        <Chip
                                          icon={<Visibility />}
                                          label="View"
                                          size="small"
                                          variant="outlined"
                                          onClick={() => window.open(video.url, '_blank')}
                                          sx={{ cursor: 'pointer' }}
                                        />
                                      </Box>
                                    </Box>
                                  </Card>
                                );
                              })
                            ) : (
                              <Box sx={{ textAlign: 'center', py: 3 }}>
                                <Typography variant="body2" color="text.secondary">
                                  No {isShorts ? 'shorts' : 'videos'} found
                                </Typography>
                              </Box>
                            );
                          })()}
                        </Box>
                        ))}
                      </Box>
                </Box>
              );
              })}

              {/* Empty state for Source 1 */}
              {sourceIndex === 0 && sourceChannels.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    Click + to add a channel
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>
        ))}
      </Box>

      {/* Load More Button */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4, mb: 4 }}>
        <Button
          variant="contained"
          size="large"
          sx={{ px: 4, py: 1.5 }}
        >
          Load More
        </Button>
      </Box>
    </Box>
  );
};

export default WireframeLayout;

