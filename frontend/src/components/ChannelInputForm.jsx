import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Alert,
  CircularProgress,
  Autocomplete,
  Chip,
  Avatar,
  Stack,
} from '@mui/material';
import { Send, Search } from '@mui/icons-material';

const ChannelInputForm = ({ onAnalyze, loading }) => {
  const [selectedChannels, setSelectedChannels] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [error, setError] = useState('');
  const [open, setOpen] = useState(false);
  const searchTimeoutRef = useRef(null);

  // Format number helper (same as in WireframeLayout)
  const formatNumber = (num) => {
    if (!num) return '0';
    if (num >= 1000000000) {
      return (num / 1000000000).toFixed(1) + 'B';
    } else if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  // Debounced search function
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    if (searchQuery.trim().length < 2) {
      setSearchResults([]);
      setOpen(false);
      return;
    }

    setSearchLoading(true);
    searchTimeoutRef.current = setTimeout(async () => {
      try {
        const url = `http://localhost:8000/api/search-channels/?q=${encodeURIComponent(searchQuery)}&max_results=10`;
        console.log('🔍 Searching channels:', searchQuery);
        
        const response = await fetch(url);
        
        if (response.ok) {
          const data = await response.json();
          const results = data.results || [];
          console.log('✅ Search results:', results.length, 'channels found');
          
          if (data.error) {
            console.error('⚠️ API returned error:', data.error);
            setError(`Search error: ${data.error}`);
          } else {
            setError('');
          }
          
          setSearchResults(results);
          // Open dropdown if we have results
          if (results.length > 0) {
            setOpen(true);
            console.log('📋 Opening dropdown with', results.length, 'results');
          } else {
            setOpen(false);
            console.log('📭 No results found');
          }
        } else {
          const errorText = await response.text();
          console.error('❌ Search API error:', response.status, errorText);
          setSearchResults([]);
          setOpen(false);
          setError(`Search failed: ${response.status}`);
        }
      } catch (err) {
        console.error('❌ Fetch error:', err);
        setSearchResults([]);
        setOpen(false);
        
        // Provide helpful error message
        if (err.message.includes('fetch') || err.message.includes('NetworkError') || err.message.includes('Failed to fetch')) {
          setError(
            'Backend server not running. Please start the Django server: Open terminal, run "cd backend && source venv/bin/activate && python manage.py runserver", then refresh this page.'
          );
        } else {
          setError(`Network error: ${err.message}`);
        }
      } finally {
        setSearchLoading(false);
      }
    }, 500);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchQuery]);

  const handleChannelSelect = (event, value) => {
    if (value) {
      // Check if channel already added
      const isDuplicate = selectedChannels.some(
        ch => ch.channel_id === value.channel_id
      );
      
      if (!isDuplicate && selectedChannels.length < 10) {
        setSelectedChannels([...selectedChannels, value]);
        setSearchQuery('');
        setSearchResults([]);
      }
    }
  };

  const handleRemoveChannel = (channelId) => {
    setSelectedChannels(selectedChannels.filter(ch => ch.channel_id !== channelId));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (selectedChannels.length === 0) {
      setError('Please select at least one channel');
      return;
    }

    // Use handle_url if available, otherwise use channel URL
    const urls = selectedChannels.map(ch => 
      ch.handle_url || ch.url
    );

    onAnalyze(urls);
  };

  const handleManualInput = () => {
    // Allow manual URL input as fallback
    const manualUrl = prompt('Enter YouTube channel URL manually:');
    if (manualUrl && manualUrl.trim()) {
      // Create a temporary channel object for manual URLs
      const tempChannel = {
        channel_id: `manual_${Date.now()}`,
        channel_name: 'Manual Channel',
        url: manualUrl.trim(),
        handle_url: null,
      };
      setSelectedChannels([...selectedChannels, tempChannel]);
    }
  };

  return (
    <Box sx={{ p: 2, bgcolor: '#000' }}>
      <Paper
        sx={{
          p: 3,
          bgcolor: '#1a1a1a',
          borderRadius: 2,
          maxWidth: 800,
          mx: 'auto',
        }}
      >
        <Typography variant="h5" gutterBottom sx={{ color: 'white', mb: 2 }}>
          Social Trends - YouTube Analyzer
        </Typography>
        
        <form onSubmit={handleSubmit}>
          {/* Channel Search Autocomplete */}
          <Autocomplete
            freeSolo
            open={open}
            onOpen={() => {
              // Open if we have results or are loading
              if (searchResults.length > 0 || searchLoading) {
                setOpen(true);
              }
            }}
            onClose={() => {
              setOpen(false);
            }}
            options={searchResults}
            loading={searchLoading}
            filterOptions={(options) => options} // Disable client-side filtering since we're doing server-side
            noOptionsText={searchQuery.trim().length >= 2 ? "No channels found" : "Type at least 2 characters"}
            loadingText="Searching channels..."
            getOptionLabel={(option) => {
              if (typeof option === 'string') return option;
              return option.channel_name || 'Unknown Channel';
            }}
            renderOption={(props, option) => (
              <Box
                component="li"
                {...props}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  py: 1,
                  px: 2,
                  '&:hover': {
                    bgcolor: '#f5f5f5',
                  },
                }}
              >
                {option.thumbnail && (
                  <Avatar
                    src={option.thumbnail}
                    alt={option.channel_name}
                    sx={{ width: 40, height: 40 }}
                  />
                )}
                <Box sx={{ flex: 1 }}>
                  <Typography variant="body1" sx={{ color: '#1a1a1a', fontWeight: 'medium' }}>
                    {option.channel_name}
                  </Typography>
                  {option.subscriber_count > 0 && (
                    <Typography variant="caption" sx={{ color: '#666', display: 'block', fontWeight: 'medium' }}>
                      {formatNumber(option.subscriber_count)} subscribers
                    </Typography>
                  )}
                  {option.description && (
                    <Typography variant="caption" sx={{ color: '#999', display: 'block' }}>
                      {option.description}
                    </Typography>
                  )}
                  <Typography variant="caption" sx={{ color: '#999', display: 'block' }}>
                    {option.handle_url || option.url}
                  </Typography>
                </Box>
              </Box>
            )}
            inputValue={searchQuery}
            onInputChange={(event, newInputValue, reason) => {
              setSearchQuery(newInputValue);
              // Close if user clears input
              if (newInputValue.trim().length < 2) {
                setOpen(false);
              }
              // Don't close on input - let the search results control when to open
            }}
            onChange={(event, value) => {
              handleChannelSelect(event, value);
              setOpen(false);
            }}
            disabled={loading || selectedChannels.length >= 10}
            renderInput={(params) => (
              <TextField
                {...params}
                placeholder={selectedChannels.length >= 10 
                  ? "Maximum 10 channels reached" 
                  : "Search for YouTube channels..."}
                variant="outlined"
                onFocus={(e) => {
                  // Open dropdown when input is focused if we have results
                  if (searchResults.length > 0) {
                    setOpen(true);
                  }
                  params.inputProps.onFocus?.(e);
                }}
                InputProps={{
                  ...params.InputProps,
                  startAdornment: <Search sx={{ color: '#666', mr: 1 }} />,
                  endAdornment: (
                    <>
                      {searchLoading ? <CircularProgress size={20} /> : null}
                      {params.InputProps.endAdornment}
                    </>
                  ),
                }}
                sx={{
                  mb: 2,
                  '& .MuiOutlinedInput-root': {
                    bgcolor: '#2a2a2a',
                    color: 'white',
                    '& fieldset': {
                      borderColor: '#424242',
                    },
                    '&:hover fieldset': {
                      borderColor: '#1976d2',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#1976d2',
                    },
                  },
                  '& .MuiInputBase-input': {
                    color: 'white',
                  },
                }}
              />
            )}
            sx={{
              mb: 2,
              '& .MuiAutocomplete-paper': {
                bgcolor: 'white',
                border: '1px solid #e0e0e0',
                boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)',
                zIndex: 1300,
              },
              '& .MuiAutocomplete-popper': {
                zIndex: 1300,
              },
            }}
          />

          {/* Selected Channels */}
          {selectedChannels.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ color: '#999', mb: 1 }}>
                Selected Channels ({selectedChannels.length}/10):
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {selectedChannels.map((channel) => (
                  <Chip
                    key={channel.channel_id}
                    label={channel.channel_name}
                    avatar={channel.thumbnail ? <Avatar src={channel.thumbnail} /> : undefined}
                    onDelete={() => handleRemoveChannel(channel.channel_id)}
                    sx={{
                      bgcolor: '#2a2a2a',
                      color: 'white',
                      '& .MuiChip-deleteIcon': {
                        color: '#999',
                        '&:hover': {
                          color: 'white',
                        },
                      },
                    }}
                  />
                ))}
              </Stack>
            </Box>
          )}

          {/* Manual URL Input Option */}
          <Box sx={{ mb: 2, textAlign: 'center' }}>
            <Button
              variant="text"
              size="small"
              onClick={handleManualInput}
              disabled={loading || selectedChannels.length >= 10}
              sx={{
                color: '#999',
                '&:hover': {
                  color: 'white',
                  bgcolor: '#2a2a2a',
                },
              }}
            >
              Or paste channel URL manually
            </Button>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Button
            type="submit"
            variant="contained"
            fullWidth
            disabled={loading || selectedChannels.length === 0}
            startIcon={loading ? <CircularProgress size={20} /> : <Send />}
            sx={{
              bgcolor: '#1976d2',
              py: 1.5,
              '&:hover': {
                bgcolor: '#1565c0',
              },
              '&:disabled': {
                bgcolor: '#424242',
                color: '#666',
              },
            }}
          >
            {loading ? 'Analyzing...' : `Analyze ${selectedChannels.length} Channel${selectedChannels.length !== 1 ? 's' : ''}`}
          </Button>
        </form>
      </Paper>
    </Box>
  );
};

export default ChannelInputForm;
