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
import { Add, Visibility } from '@mui/icons-material';

const InstagramLayout = ({ results }) => {
  const [selectedTab, setSelectedTab] = useState({});
  const [selectedSourceTab, setSelectedSourceTab] = useState({});
  const [trendingTimeRange, setTrendingTimeRange] = useState({});
  const [popularTimeRange, setPopularTimeRange] = useState({});

  const handleTabChange = (pageIndex, value) => {
    setSelectedTab({ ...selectedTab, [pageIndex]: value });
  };

  const handleSourceTabChange = (sourceIndex, value) => {
    setSelectedSourceTab({ ...selectedSourceTab, [sourceIndex]: value });
  };

  const handleTrendingTimeRangeChange = (sourceIndex, pageIndex, value) => {
    setTrendingTimeRange({ ...trendingTimeRange, [`${sourceIndex}-${pageIndex}`]: value });
  };

  const handlePopularTimeRangeChange = (sourceIndex, pageIndex, value) => {
    setPopularTimeRange({ ...popularTimeRange, [`${sourceIndex}-${pageIndex}`]: value });
  };

  const formatNumber = (num) => {
    if (!num) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    } catch {
      return dateString;
    }
  };

  const getTimeSincePublish = (timestamp) => {
    if (!timestamp) return '';
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      
      if (diffHours < 1) return 'Just now';
      if (diffHours < 24) return `${diffHours}h ago`;
      const diffDays = Math.floor(diffHours / 24);
      if (diffDays < 7) return `${diffDays}d ago`;
      const diffWeeks = Math.floor(diffDays / 7);
      return `${diffWeeks}w ago`;
    } catch {
      return '';
    }
  };

  const calculateViewsPerTimeUnit = (views, publishedAt, timeRange) => {
    if (!views || !publishedAt) return 0;
    try {
      const published = new Date(publishedAt);
      const now = new Date();
      const diffHours = (now - published) / (1000 * 60 * 60);
      
      if (timeRange === 'Last 30 Minutes') {
        return diffHours >= 0.5 ? views / diffHours * 0.5 : views;
      } else if (timeRange === '1 Hour') {
        return diffHours >= 1 ? views / diffHours : views;
      } else if (timeRange === '1 Day') {
        const diffDays = diffHours / 24;
        return diffDays >= 1 ? views / diffDays : views;
      }
      return views;
    } catch {
      return views;
    }
  };

  const pages = results.results || [];
  const uniquePages = pages.filter((page, index, self) => 
    index === self.findIndex(p => p.username === page.username)
  );

  const sources = uniquePages.slice(0, 3).map(page => [page]);
  while (sources.length < 3) {
    sources.push([]);
  }

  return (
    <Box sx={{ p: 2, bgcolor: '#000', minHeight: '100vh' }}>
      <Box
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', sm: 'row', md: 'row' },
          gap: 2,
          justifyContent: 'space-between',
        }}
      >
        {sources.map((sourcePages, sourceIndex) => {
          const page = sourcePages.length > 0 ? sourcePages[0] : null;
          const currentTab = selectedTab[sourceIndex] || 0;
          const currentSourceTab = selectedSourceTab[sourceIndex] || 0;

          return (
            <Box
              key={sourceIndex}
              sx={{
                width: { xs: '100%', sm: 'calc(33.333% - 16px)', md: 'calc(33.333% - 16px)' },
                flexShrink: 0,
              }}
            >
              {/* Page Header */}
              <Paper
                elevation={2}
                sx={{
                  p: 2,
                  mb: 2,
                  bgcolor: '#E4405F', // Instagram brand color
                  color: 'white',
                  borderRadius: 2,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flex: 1 }}>
                    {page?.profile_picture && (
                      <Avatar
                        src={page.profile_picture}
                        alt={page.full_name || page.username || `Source ${sourceIndex + 1}`}
                        sx={{ width: 32, height: 32 }}
                      />
                    )}
                    <Typography variant="h6" fontWeight="bold">
                      {page?.full_name || page?.username || `Source ${sourceIndex + 1}`}
                    </Typography>
                  </Box>
                  
                  {/* Follower Count */}
                  {page && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                      {page.follower_count > 0 && (
                        <Chip
                          label={`${formatNumber(page.follower_count)} followers`}
                          size="small"
                          sx={{
                            bgcolor: 'rgba(255, 255, 255, 0.2)',
                            color: 'primary.contrastText',
                            fontWeight: 'medium',
                          }}
                        />
                      )}
                      {page.post_count > 0 && (
                        <Chip
                          label={`${formatNumber(page.post_count)} posts`}
                          size="small"
                          sx={{
                            bgcolor: 'rgba(255, 255, 255, 0.2)',
                            color: 'primary.contrastText',
                            fontWeight: 'medium',
                          }}
                        />
                      )}
                    </Box>
                  )}
                </Box>
              </Paper>

              {/* Add Button for empty sources */}
              {sourcePages.length === 0 && (
                <Paper
                  elevation={1}
                  sx={{
                    p: 3,
                    textAlign: 'center',
                    bgcolor: '#1a1a1a',
                    borderRadius: 2,
                  }}
                >
                  <Button
                    startIcon={<Add />}
                    variant="outlined"
                    sx={{
                      color: '#999',
                      borderColor: '#424242',
                      '&:hover': {
                        borderColor: '#1976d2',
                        color: 'white',
                      },
                    }}
                  >
                    Add Instagram Page
                  </Button>
                </Paper>
              )}

              {page && (
                <>
                  {/* Trending Section */}
                  <Paper elevation={1} sx={{ p: 2, mb: 2, bgcolor: '#1a1a1a', borderRadius: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
                        🔥 Trending
                      </Typography>
                      <FormControl size="small" sx={{ minWidth: 120 }}>
                        <Select
                          value={trendingTimeRange[`${sourceIndex}-0`] || '1 Hour'}
                          onChange={(e) => handleTrendingTimeRangeChange(sourceIndex, 0, e.target.value)}
                          sx={{
                            color: 'white',
                            bgcolor: '#2a2a2a',
                            '& .MuiOutlinedInput-notchedOutline': {
                              borderColor: '#424242',
                            },
                            '&:hover .MuiOutlinedInput-notchedOutline': {
                              borderColor: '#1976d2',
                            },
                          }}
                        >
                          <MenuItem value="Last 30 Minutes">Last 30 Minutes</MenuItem>
                          <MenuItem value="1 Hour">1 Hour</MenuItem>
                          <MenuItem value="1 Day">1 Day</MenuItem>
                        </Select>
                      </FormControl>
                    </Box>

                    <Tabs
                      value={currentSourceTab}
                      onChange={(e, newValue) => handleSourceTabChange(sourceIndex, newValue)}
                      sx={{
                        mb: 2,
                        '& .MuiTab-root': {
                          color: '#999',
                          '&.Mui-selected': {
                            color: '#1976d2',
                          },
                        },
                        '& .MuiTabs-indicator': {
                          bgcolor: '#1976d2',
                        },
                      }}
                    >
                      <Tab label="Posts" />
                      <Tab label="Reels" />
                    </Tabs>

                    {currentSourceTab === 0 && (
                      <Box>
                        {page.trending_posts && page.trending_posts.length > 0 ? (
                          page.trending_posts.slice(0, 3).map((item, idx) => (
                            <Card key={idx} sx={{ mb: 2, bgcolor: '#2a2a2a' }}>
                              <CardMedia
                                component="img"
                                height="180"
                                image={item.thumbnail || '/placeholder.jpg'}
                                alt={item.caption || 'Post'}
                              />
                              <Box sx={{ p: 1.5 }}>
                                <Typography variant="body2" sx={{ color: 'white', mb: 1, fontWeight: 'medium' }}>
                                  {item.caption?.substring(0, 60) || 'No caption'}...
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                                  <Chip
                                    label={`${formatNumber(item.likes)} likes`}
                                    size="small"
                                    sx={{ bgcolor: '#E4405F', color: 'white' }}
                                  />
                                  <Chip
                                    label={`${formatNumber(item.comments)} comments`}
                                    size="small"
                                    sx={{ bgcolor: '#2a2a2a', color: '#999' }}
                                  />
                                  {item.hours_since_publish !== undefined && (
                                    <Chip
                                      label={getTimeSincePublish(item.published_at)}
                                      size="small"
                                      sx={{ bgcolor: '#2a2a2a', color: '#999' }}
                                    />
                                  )}
                                </Box>
                                <Button
                                  size="small"
                                  startIcon={<Visibility />}
                                  href={item.url}
                                  target="_blank"
                                  sx={{ color: '#1976d2' }}
                                >
                                  View
                                </Button>
                              </Box>
                            </Card>
                          ))
                        ) : (
                          <Typography variant="body2" sx={{ color: '#999', textAlign: 'center', py: 2 }}>
                            No trending posts
                          </Typography>
                        )}
                      </Box>
                    )}

                    {currentSourceTab === 1 && (
                      <Box>
                        {page.trending_reels && page.trending_reels.length > 0 ? (
                          page.trending_reels.slice(0, 3).map((item, idx) => (
                            <Card key={idx} sx={{ mb: 2, bgcolor: '#2a2a2a' }}>
                              <CardMedia
                                component="img"
                                height="180"
                                image={item.thumbnail || '/placeholder.jpg'}
                                alt={item.caption || 'Reel'}
                              />
                              <Box sx={{ p: 1.5 }}>
                                <Typography variant="body2" sx={{ color: 'white', mb: 1, fontWeight: 'medium' }}>
                                  {item.caption?.substring(0, 60) || 'No caption'}...
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                                  <Chip
                                    label={`${formatNumber(item.views || item.likes)} views`}
                                    size="small"
                                    sx={{ bgcolor: '#E4405F', color: 'white' }}
                                  />
                                  <Chip
                                    label={`${formatNumber(item.likes)} likes`}
                                    size="small"
                                    sx={{ bgcolor: '#2a2a2a', color: '#999' }}
                                  />
                                  {item.hours_since_publish !== undefined && (
                                    <Chip
                                      label={getTimeSincePublish(item.published_at)}
                                      size="small"
                                      sx={{ bgcolor: '#2a2a2a', color: '#999' }}
                                    />
                                  )}
                                </Box>
                                <Button
                                  size="small"
                                  startIcon={<Visibility />}
                                  href={item.url}
                                  target="_blank"
                                  sx={{ color: '#1976d2' }}
                                >
                                  View
                                </Button>
                              </Box>
                            </Card>
                          ))
                        ) : (
                          <Typography variant="body2" sx={{ color: '#999', textAlign: 'center', py: 2 }}>
                            No trending reels
                          </Typography>
                        )}
                      </Box>
                    )}
                  </Paper>

                  {/* Popular Section */}
                  <Paper elevation={1} sx={{ p: 2, bgcolor: '#1a1a1a', borderRadius: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
                        📊 Popular
                      </Typography>
                      <FormControl size="small" sx={{ minWidth: 120 }}>
                        <Select
                          value={popularTimeRange[`${sourceIndex}-0`] || 'All Time'}
                          onChange={(e) => handlePopularTimeRangeChange(sourceIndex, 0, e.target.value)}
                          sx={{
                            color: 'white',
                            bgcolor: '#2a2a2a',
                            '& .MuiOutlinedInput-notchedOutline': {
                              borderColor: '#424242',
                            },
                            '&:hover .MuiOutlinedInput-notchedOutline': {
                              borderColor: '#1976d2',
                            },
                          }}
                        >
                          <MenuItem value="This Month">This Month</MenuItem>
                          <MenuItem value="This Year">This Year</MenuItem>
                          <MenuItem value="All Time">All Time</MenuItem>
                        </Select>
                      </FormControl>
                    </Box>

                    <Tabs
                      value={currentTab}
                      onChange={(e, newValue) => handleTabChange(sourceIndex, newValue)}
                      sx={{
                        mb: 2,
                        '& .MuiTab-root': {
                          color: '#999',
                          '&.Mui-selected': {
                            color: '#1976d2',
                          },
                        },
                        '& .MuiTabs-indicator': {
                          bgcolor: '#1976d2',
                        },
                      }}
                    >
                      <Tab label="Posts" />
                      <Tab label="Reels" />
                      <Tab label="Videos" />
                    </Tabs>

                    {/* Posts Tab */}
                    {currentTab === 0 && (
                      <Box>
                        {page.posts && page.posts.length > 0 ? (
                          page.posts.slice(0, 5).map((item, idx) => (
                            <Card key={idx} sx={{ mb: 2, bgcolor: '#2a2a2a' }}>
                              <CardMedia
                                component="img"
                                height="180"
                                image={item.thumbnail || '/placeholder.jpg'}
                                alt={item.caption || 'Post'}
                              />
                              <Box sx={{ p: 1.5 }}>
                                <Typography variant="body2" sx={{ color: 'white', mb: 1, fontWeight: 'medium' }}>
                                  {item.caption?.substring(0, 60) || 'No caption'}...
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                                  <Chip
                                    label={`${formatNumber(item.likes)} likes`}
                                    size="small"
                                    sx={{ bgcolor: '#E4405F', color: 'white' }}
                                  />
                                  <Chip
                                    label={`${formatNumber(item.comments)} comments`}
                                    size="small"
                                    sx={{ bgcolor: '#2a2a2a', color: '#999' }}
                                  />
                                  {item.published_at && (
                                    <Chip
                                      label={formatDate(item.published_at)}
                                      size="small"
                                      sx={{ bgcolor: '#2a2a2a', color: '#999' }}
                                    />
                                  )}
                                </Box>
                                <Button
                                  size="small"
                                  startIcon={<Visibility />}
                                  href={item.url}
                                  target="_blank"
                                  sx={{ color: '#1976d2' }}
                                >
                                  View
                                </Button>
                              </Box>
                            </Card>
                          ))
                        ) : (
                          <Typography variant="body2" sx={{ color: '#999', textAlign: 'center', py: 2 }}>
                            No posts found
                          </Typography>
                        )}
                      </Box>
                    )}

                    {/* Reels Tab */}
                    {currentTab === 1 && (
                      <Box>
                        {page.reels && page.reels.length > 0 ? (
                          page.reels.slice(0, 5).map((item, idx) => (
                            <Card key={idx} sx={{ mb: 2, bgcolor: '#2a2a2a' }}>
                              <CardMedia
                                component="img"
                                height="180"
                                image={item.thumbnail || '/placeholder.jpg'}
                                alt={item.caption || 'Reel'}
                              />
                              <Box sx={{ p: 1.5 }}>
                                <Typography variant="body2" sx={{ color: 'white', mb: 1, fontWeight: 'medium' }}>
                                  {item.caption?.substring(0, 60) || 'No caption'}...
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                                  <Chip
                                    label={`${formatNumber(item.views || item.likes)} views`}
                                    size="small"
                                    sx={{ bgcolor: '#E4405F', color: 'white' }}
                                  />
                                  <Chip
                                    label={`${formatNumber(item.likes)} likes`}
                                    size="small"
                                    sx={{ bgcolor: '#2a2a2a', color: '#999' }}
                                  />
                                  {item.published_at && (
                                    <Chip
                                      label={formatDate(item.published_at)}
                                      size="small"
                                      sx={{ bgcolor: '#2a2a2a', color: '#999' }}
                                    />
                                  )}
                                </Box>
                                <Button
                                  size="small"
                                  startIcon={<Visibility />}
                                  href={item.url}
                                  target="_blank"
                                  sx={{ color: '#1976d2' }}
                                >
                                  View
                                </Button>
                              </Box>
                            </Card>
                          ))
                        ) : (
                          <Typography variant="body2" sx={{ color: '#999', textAlign: 'center', py: 2 }}>
                            No reels found
                          </Typography>
                        )}
                      </Box>
                    )}

                    {/* Videos Tab */}
                    {currentTab === 2 && (
                      <Box>
                        {page.videos && page.videos.length > 0 ? (
                          page.videos.slice(0, 5).map((item, idx) => (
                            <Card key={idx} sx={{ mb: 2, bgcolor: '#2a2a2a' }}>
                              <CardMedia
                                component="img"
                                height="180"
                                image={item.thumbnail || '/placeholder.jpg'}
                                alt={item.caption || 'Video'}
                              />
                              <Box sx={{ p: 1.5 }}>
                                <Typography variant="body2" sx={{ color: 'white', mb: 1, fontWeight: 'medium' }}>
                                  {item.caption?.substring(0, 60) || 'No caption'}...
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                                  <Chip
                                    label={`${formatNumber(item.views || item.likes)} views`}
                                    size="small"
                                    sx={{ bgcolor: '#E4405F', color: 'white' }}
                                  />
                                  <Chip
                                    label={`${formatNumber(item.likes)} likes`}
                                    size="small"
                                    sx={{ bgcolor: '#2a2a2a', color: '#999' }}
                                  />
                                  {item.published_at && (
                                    <Chip
                                      label={formatDate(item.published_at)}
                                      size="small"
                                      sx={{ bgcolor: '#2a2a2a', color: '#999' }}
                                    />
                                  )}
                                </Box>
                                <Button
                                  size="small"
                                  startIcon={<Visibility />}
                                  href={item.url}
                                  target="_blank"
                                  sx={{ color: '#1976d2' }}
                                >
                                  View
                                </Button>
                              </Box>
                            </Card>
                          ))
                        ) : (
                          <Typography variant="body2" sx={{ color: '#999', textAlign: 'center', py: 2 }}>
                            No videos found
                          </Typography>
                        )}
                      </Box>
                    )}
                  </Paper>
                </>
              )}
            </Box>
          );
        })}
      </Box>
    </Box>
  );
};

export default InstagramLayout;

