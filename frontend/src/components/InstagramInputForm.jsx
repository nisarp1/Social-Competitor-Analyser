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

const InstagramInputForm = ({ onAnalyze, loading }) => {
  const [selectedPages, setSelectedPages] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [error, setError] = useState('');
  const searchTimeoutRef = useRef(null);

  // Format number helper
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
      return;
    }

    setSearchLoading(true);
    searchTimeoutRef.current = setTimeout(async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/api/search-instagram/?q=${encodeURIComponent(searchQuery)}&max_results=10`
        );
        
        if (response.ok) {
          const data = await response.json();
          console.log('Instagram search response:', data);
          setSearchResults(data.results || []);
          
          if (!data.results || data.results.length === 0) {
            console.log('No results returned for query:', searchQuery);
          }
        } else {
          const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
          console.error('Instagram search API error:', response.status, errorData);
          setSearchResults([]);
        }
      } catch (err) {
        console.error('Instagram search error:', err);
        setSearchResults([]);
      } finally {
        setSearchLoading(false);
      }
    }, 500); // 500ms delay

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchQuery]);

  const handlePageSelect = (event, value) => {
    if (value && typeof value === 'object') {
      // Check if already added
      const isDuplicate = selectedPages.some(
        p => p.username === value.username
      );
      
      if (!isDuplicate && selectedPages.length < 10) {
        setSelectedPages([...selectedPages, value]);
        setSearchQuery('');
        setSearchResults([]);
      }
    } else if (value && typeof value === 'string') {
      // Handle manual string input
      const username = value.replace('@', '').replace('https://www.instagram.com/', '').replace('https://instagram.com/', '').split('/')[0];
      const isDuplicate = selectedPages.some(p => p.username === username);
      
      if (!isDuplicate && selectedPages.length < 10) {
        const pageObj = {
          username: username,
          url: value.includes('http') ? value : `https://www.instagram.com/${username}/`,
          full_name: username,
          profile_picture: '',
          follower_count: 0,
        };
        setSelectedPages([...selectedPages, pageObj]);
        setSearchQuery('');
        setSearchResults([]);
      }
    }
  };


  const handleRemovePage = (username) => {
    setSelectedPages(selectedPages.filter(p => p.username !== username));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (selectedPages.length === 0) {
      setError('Please select at least one Instagram page');
      return;
    }

    // Use URLs for API call
    const urls = selectedPages.map(page => page.url);

    onAnalyze(urls);
  };

  const handleManualInput = () => {
    const manualInput = prompt('Enter Instagram page username or URL:');
    if (manualInput && manualInput.trim()) {
      const username = manualInput.trim().replace('@', '').replace('https://www.instagram.com/', '').replace('https://instagram.com/', '').split('/')[0];
      const pageObj = {
        username: username,
        url: manualInput.includes('http') ? manualInput : `https://www.instagram.com/${username}/`,
      };
      
      const isDuplicate = selectedPages.some(p => p.username === pageObj.username);
      if (!isDuplicate && selectedPages.length < 10) {
        setSelectedPages([...selectedPages, pageObj]);
      }
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
          Social Trends - Instagram Analyzer
        </Typography>
        
        <form onSubmit={handleSubmit}>
          {/* Instagram Page Search Autocomplete */}
          <Autocomplete
            freeSolo
            options={searchResults}
            loading={searchLoading}
            getOptionLabel={(option) => {
              if (typeof option === 'string') return option;
              return option.full_name || option.username || 'Unknown Page';
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
                {option.profile_picture && (
                  <Avatar
                    src={option.profile_picture}
                    alt={option.full_name || option.username}
                    sx={{ width: 40, height: 40 }}
                  />
                )}
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <Typography variant="body1" sx={{ color: '#1a1a1a', fontWeight: 'medium' }}>
                      {option.full_name || option.username}
                    </Typography>
                    {option.is_verified && (
                      <Typography sx={{ color: '#1976d2', fontSize: '0.875rem' }}>✓</Typography>
                    )}
                  </Box>
                  {option.follower_count > 0 && (
                    <Typography variant="caption" sx={{ color: '#666', display: 'block', fontWeight: 'medium' }}>
                      {formatNumber(option.follower_count)} followers
                    </Typography>
                  )}
                  <Typography variant="caption" sx={{ color: '#999', display: 'block' }}>
                    @{option.username}
                  </Typography>
                </Box>
              </Box>
            )}
            inputValue={searchQuery}
            onInputChange={(event, newInputValue) => {
              setSearchQuery(newInputValue);
            }}
            onChange={handlePageSelect}
            disabled={loading || selectedPages.length >= 10}
            renderInput={(params) => (
              <TextField
                {...params}
                placeholder={selectedPages.length >= 10 
                  ? "Maximum 10 pages reached" 
                  : "Search for Instagram pages..."}
                variant="outlined"
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
                      borderColor: '#E4405F',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#E4405F',
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
              },
            }}
          />

          {/* Selected Pages */}
          {selectedPages.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ color: '#999', mb: 1 }}>
                Selected Pages ({selectedPages.length}/10):
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {selectedPages.map((page) => (
                  <Chip
                    key={page.username}
                    label={page.full_name ? `${page.full_name} (@${page.username})` : `@${page.username}`}
                    avatar={page.profile_picture ? <Avatar src={page.profile_picture} /> : undefined}
                    onDelete={() => handleRemovePage(page.username)}
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
              disabled={loading || selectedPages.length >= 10}
              sx={{
                color: '#999',
                '&:hover': {
                  color: 'white',
                  bgcolor: '#2a2a2a',
                },
              }}
            >
              Or paste Instagram page URL/username manually
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
            disabled={loading || selectedPages.length === 0}
            startIcon={loading ? <CircularProgress size={20} /> : <Send />}
            sx={{
              bgcolor: '#E4405F', // Instagram brand color
              py: 1.5,
              '&:hover': {
                bgcolor: '#C13584',
              },
              '&:disabled': {
                bgcolor: '#424242',
                color: '#666',
              },
            }}
          >
            {loading ? 'Analyzing...' : `Analyze ${selectedPages.length} Page${selectedPages.length !== 1 ? 's' : ''}`}
          </Button>
        </form>
      </Paper>
    </Box>
  );
};

export default InstagramInputForm;

