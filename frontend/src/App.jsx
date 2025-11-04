import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Alert, Tabs, Tab, AppBar, Toolbar, Typography } from '@mui/material';
import { YouTube, Instagram } from '@mui/icons-material';
import ChannelInputForm from './components/ChannelInputForm';
import WireframeLayout from './components/WireframeLayout';
import InstagramInputForm from './components/InstagramInputForm';
import InstagramLayout from './components/InstagramLayout';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
  },
});

function App() {
  const [currentPage, setCurrentPage] = useState('youtube'); // 'youtube' or 'instagram'
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async (urls) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      let endpoint, bodyKey;
      
      // Use localhost for Django backend
      const API_BASE = 'http://localhost:8000';
      
      if (currentPage === 'youtube') {
        endpoint = `${API_BASE}/api/analyze-channels/`;
        bodyKey = 'channel_urls';
      } else {
        endpoint = `${API_BASE}/api/analyze-instagram/`;
        bodyKey = 'page_urls';
      }

      // Simple endpoint without cache busting (backend handles caching)
      const endpointWithCacheBuster = endpoint;
      
      try {
        const response = await fetch(endpointWithCacheBuster, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            [bodyKey]: urls,
            real_time_trending: false,  // Use cache to save quota
            real_time_live: false  // Use cache to save quota
          }),
        });

        console.log('Response status:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('❌ API Error Response:', errorText);
          try {
            const errorData = JSON.parse(errorText);
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
          } catch {
            throw new Error(`HTTP error! status: ${response.status}, body: ${errorText.substring(0, 200)}`);
          }
        }
        
        const data = await response.json();
      
      // Comprehensive logging
      console.log('📥 API Response received:', {
        status: response.status,
        resultsCount: data.results?.length || 0,
        errorsCount: data.errors?.length || 0,
      });
      
      // Log detailed info for each channel
      if (data.results && data.results.length > 0) {
        console.log('📊 Channel Data Details:');
        data.results.forEach((channel, idx) => {
          console.log(`  Channel ${idx + 1} (${channel.channel_name || 'Unknown'}):`, {
            channel_id: channel.channel_id,
            channel_name: channel.channel_name,
            videos_count: channel.videos?.length || 0,
            shorts_count: channel.shorts?.length || 0,
            trending_videos_count: channel.trending_videos?.length || 0,
            trending_shorts_count: channel.trending_shorts?.length || 0,
            live_videos_count: channel.live_videos?.length || 0,
            has_videos_array: Array.isArray(channel.videos),
            has_shorts_array: Array.isArray(channel.shorts),
            videos_sample: channel.videos?.[0] ? {
              title: channel.videos[0].title,
              video_id: channel.videos[0].video_id,
              view_count: channel.videos[0].view_count,
              url: channel.videos[0].url
            } : null,
            all_keys: Object.keys(channel)
          });
        });
      } else {
        console.warn('⚠️ No results in API response!', data);
      }
      
      // Log full response for debugging
      console.log('📋 Full API Response:', JSON.stringify(data, null, 2));

      // Error handling moved above - response.ok already checked

      // Check for quota errors first (these are critical)
      const quotaErrors = data.errors?.filter(e => e.quota_exceeded || e.error?.toLowerCase().includes('quota'));
      if (quotaErrors && quotaErrors.length > 0) {
        const quotaMsg = "🚨 API Quota Exceeded: Daily limit (10,000 units) reached. " +
          "The quota resets at midnight Pacific Time. " +
          "Please try again tomorrow or request a quota increase in Google Cloud Console.";
        setError(quotaMsg);
        setResults(data); // Still show partial results if any
        return;
      }

      // Check for other errors in the response
      if (data.errors && data.errors.length > 0) {
        const errorMessages = data.errors.map(e => `${e.channel_url}: ${e.error}`).join('; ');
        setError(`Some channels failed: ${errorMessages}`);
      }

      // Only show error if ALL channels failed
      if (data.total_channels_processed === 0 && data.errors && data.errors.length > 0) {
        const errorMessages = data.errors.map(e => `${e.channel_url}: ${e.error}`).join('; ');
        // Check if it's a quota error
        if (errorMessages.toLowerCase().includes('quota')) {
          throw new Error(
            "🚨 API Quota Exceeded: Daily limit (10,000 units) reached. " +
            "The quota resets at midnight Pacific Time. " +
            "Please try again tomorrow or request a quota increase in Google Cloud Console."
          );
        }
        // Check if it's a channel ID extraction error - provide helpful message
        if (errorMessages.toLowerCase().includes('could not extract channel id')) {
          const helpfulMsg = 
            "⚠️ Channel ID Extraction Failed: Could not extract channel IDs from @handle URLs. " +
            "This happens when Search API is blocked or quota exceeded. " +
            "Solution: Use channel ID URLs instead (format: https://www.youtube.com/channel/UCxxxxx). " +
            "See CHANNEL_IDS.md for channel ID mappings. " +
            "Error details: " + errorMessages;
          throw new Error(helpfulMsg);
        }
        throw new Error(`All channels failed: ${errorMessages}`);
      }

        setResults(data);
      } catch (fetchError) {
        // Network error or fetch failed
        console.error('❌ Fetch Error:', fetchError);
        console.error('❌ Fetch Error Details:', {
          name: fetchError.name,
          message: fetchError.message,
          stack: fetchError.stack,
          endpoint: endpointWithCacheBuster
        });
        
        if (fetchError instanceof TypeError && (fetchError.message.includes('fetch') || fetchError.message.includes('NetworkError') || fetchError.message.includes('Failed to fetch'))) {
          throw new Error(
            `🌐 Network Error: Cannot connect to backend server at ${endpoint}. ` +
            `\n\nPossible causes:` +
            `\n1. Django server not running - Start it with: cd backend && python manage.py runserver` +
            `\n2. Wrong port - Check if Django is on port 8000` +
            `\n3. CORS blocked - Check browser console for CORS errors` +
            `\n4. Firewall blocking - Check system firewall settings` +
            `\n\nError: ${fetchError.message}`
          );
        }
        throw fetchError;
      }
    } catch (err) {
      console.error('Error analyzing channels:', err);
      setError(err.message || 'An unexpected error occurred. Please check the browser console for details.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
        {/* Navigation Bar */}
        <AppBar position="static" sx={{ bgcolor: '#1a1a1a', borderBottom: '1px solid #424242' }}>
          <Toolbar>
            <Typography variant="h6" sx={{ flexGrow: 1, color: 'white', fontWeight: 'bold' }}>
              Social Trends Analyzer
            </Typography>
            <Tabs
              value={currentPage === 'youtube' ? 0 : 1}
              onChange={(e, newValue) => {
                setCurrentPage(newValue === 0 ? 'youtube' : 'instagram');
                setResults(null);
                setError(null);
              }}
              sx={{
                '& .MuiTab-root': {
                  color: '#999',
                  '&.Mui-selected': {
                    color: 'white',
                  },
                },
                '& .MuiTabs-indicator': {
                  bgcolor: 'white',
                },
              }}
            >
              <Tab icon={<YouTube />} label="YouTube" iconPosition="start" />
              <Tab icon={<Instagram />} label="Instagram" iconPosition="start" />
            </Tabs>
          </Toolbar>
        </AppBar>

        {/* Content based on current page */}
        {currentPage === 'youtube' ? (
          <>
            <ChannelInputForm 
              onAnalyze={handleAnalyze} 
              loading={loading}
            />

            {error && (
              <Box sx={{ m: 2 }}>
                <Alert severity="error">{error}</Alert>
              </Box>
            )}

            {results && (
              <WireframeLayout results={results} />
            )}
          </>
        ) : (
          <>
            <InstagramInputForm 
              onAnalyze={handleAnalyze} 
              loading={loading}
            />

            {error && (
              <Box sx={{ m: 2 }}>
                <Alert severity="error">{error}</Alert>
              </Box>
            )}

            {results && (
              <InstagramLayout results={results} />
            )}
          </>
        )}
      </Box>
    </ThemeProvider>
  );
}

export default App;

