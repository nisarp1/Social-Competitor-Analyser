import React, { useState } from 'react';

const VideoResults = ({ results }) => {
  const [expandedChannels, setExpandedChannels] = useState({});

  const toggleChannel = (index) => {
    setExpandedChannels(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const renderVideoTable = (videoList, title, isShort = false, isTrending = false, isLive = false) => {
    if (!videoList || videoList.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          No {title.toLowerCase()} found
        </div>
      );
    }

    return (
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rank
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Thumbnail
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Views
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Likes
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Published
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Link
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {videoList.map((video, videoIndex) => (
              <tr key={video.video_id} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-semibold ${
                    videoIndex === 0 ? 'bg-yellow-100 text-yellow-800' :
                    videoIndex === 1 ? 'bg-gray-200 text-gray-700' :
                    videoIndex === 2 ? 'bg-orange-100 text-orange-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {videoIndex + 1}
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <a 
                    href={video.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="block"
                  >
                    <img 
                      src={video.thumbnail} 
                      alt={video.title}
                      className="w-24 h-16 object-cover rounded"
                    />
                  </a>
                </td>
                <td className="px-4 py-3">
                  <a 
                    href={video.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
                    title={video.title}
                  >
                    <div className="flex items-center gap-2">
                      {isLive && video.is_live && (
                        <span className="inline-block w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                      )}
                      <span>{video.title.length > 60 ? video.title.substring(0, 60) + '...' : video.title}</span>
                    </div>
                  </a>
                  {isTrending && video.hours_since_publish && (
                    <div className="text-xs text-gray-500 mt-1">
                      Published {Math.round(video.hours_since_publish * 60)} min ago
                    </div>
                  )}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-gray-900 font-semibold">
                  <div className="flex items-center gap-2">
                    {formatNumber(video.view_count)}
                    {isLive && video.is_live && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 animate-pulse">
                        🔴 LIVE
                        {video.live_viewers && (
                          <span className="ml-1">({formatNumber(parseInt(video.live_viewers))} watching)</span>
                        )}
                      </span>
                    )}
                  </div>
                  <span className="text-gray-500 text-xs font-normal ml-1 block">
                    ({video.view_count.toLocaleString()})
                    {isTrending && video.trending_score && (
                      <span className="text-red-600 font-semibold ml-2">
                        • {formatNumber(video.trending_score)} views/hr
                      </span>
                    )}
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-gray-700">
                  {formatNumber(video.like_count)}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {formatDate(video.published_at)}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <a 
                    href={video.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-indigo-600 hover:text-indigo-800"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  if (!results || results.results.length === 0) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Analysis Summary</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Channels Analyzed</p>
            <p className="text-3xl font-bold text-blue-600">{results.total_channels_processed}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Total Videos</p>
            <p className="text-3xl font-bold text-green-600">
              {results.results.reduce((sum, channel) => sum + (channel.total_videos || 0), 0)}
            </p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Total Shorts</p>
            <p className="text-3xl font-bold text-purple-600">
              {results.results.reduce((sum, channel) => sum + (channel.total_shorts || 0), 0)}
            </p>
          </div>
        </div>
        {results.errors && results.errors.length > 0 && (
          <div className={`mt-4 p-4 rounded-lg ${
            results.errors.some(e => e.quota_exceeded || e.error?.toLowerCase().includes('quota'))
              ? 'bg-red-50 border border-red-300'
              : 'bg-yellow-50 border border-yellow-200'
          }`}>
            <p className={`text-sm font-semibold mb-2 ${
              results.errors.some(e => e.quota_exceeded || e.error?.toLowerCase().includes('quota'))
                ? 'text-red-800'
                : 'text-yellow-800'
            }`}>
              {results.errors.some(e => e.quota_exceeded || e.error?.toLowerCase().includes('quota'))
                ? '🚨 API Quota Exceeded'
                : `⚠️ Some channels had errors (${results.errors.length}):`}
            </p>
            {results.errors.map((error, idx) => {
              const isQuotaError = error.quota_exceeded || error.error?.toLowerCase().includes('quota');
              return (
                <div key={idx} className={`text-sm mb-2 ${isQuotaError ? 'text-red-700' : 'text-yellow-700'}`}>
                  {!isQuotaError && <strong>{error.channel_url}:</strong>}
                  <span className={isQuotaError ? '' : 'ml-1'}>{error.error}</span>
                  {isQuotaError && (
                    <div className="mt-2 text-xs text-red-600 bg-red-100 p-2 rounded">
                      <strong>Solution:</strong> Wait until midnight Pacific Time for quota reset, 
                      or request a quota increase in Google Cloud Console. 
                      See QUOTA_INFO.md for details.
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Channel Results */}
      {results.results.map((channel, channelIndex) => (
        <div key={channelIndex} className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div 
            className="p-6 bg-gradient-to-r from-indigo-500 to-purple-600 text-white cursor-pointer"
            onClick={() => toggleChannel(channelIndex)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-start gap-3">
                {channel.channel_thumbnail && (
                  <img 
                    src={channel.channel_thumbnail} 
                    alt={channel.channel_name || 'Channel'}
                    className="w-12 h-12 rounded-full object-cover border-2 border-white"
                  />
                )}
                <div>
                  <h3 className="text-xl font-semibold mb-1">
                    {channel.channel_name || `Channel ${channelIndex + 1}`}
                  </h3>
                  <p className="text-sm text-indigo-100 break-all">{channel.channel_url}</p>
                  <div className="mt-2 flex gap-4 text-sm flex-wrap">
                  <span>{channel.total_videos || 0} videos</span>
                  <span>{channel.total_shorts || 0} Shorts</span>
                  {(channel.total_trending_videos > 0 || channel.total_trending_shorts > 0) && (
                    <span className="text-red-600 font-semibold">
                      🔥 {channel.total_trending_videos || 0} trending videos, {channel.total_trending_shorts || 0} trending shorts
                    </span>
                  )}
                  {channel.total_live > 0 && (
                    <span className="text-red-600 font-semibold animate-pulse">🔴 {channel.total_live} live</span>
                  )}
                  </div>
                </div>
              </div>
              <div className="text-2xl">
                {expandedChannels[channelIndex] ? '−' : '+'}
              </div>
            </div>
          </div>

          {expandedChannels[channelIndex] && (
            <div className="p-6">
              {(channel.videos && channel.videos.length > 0) || (channel.shorts && channel.shorts.length > 0) || (channel.trending_videos && channel.trending_videos.length > 0) || (channel.trending_shorts && channel.trending_shorts.length > 0) || (channel.live_videos && channel.live_videos.length > 0) ? (
                <div className="space-y-6">
                  {/* Trending Section - Split into Videos and Shorts */}
                  {((channel.trending_videos && channel.trending_videos.length > 0) || (channel.trending_shorts && channel.trending_shorts.length > 0)) && (
                    <div className="mb-6">
                      <h3 className="text-xl font-semibold text-gray-800 mb-4">
                        🔥 Trending (Last 3 Hours)
                      </h3>
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Trending Videos */}
                        <div>
                          <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800 mr-2">
                              Top 3 Videos ({channel.total_trending_videos || channel.trending_videos?.length || 0}) [REAL-TIME]
                            </span>
                          </h4>
                          {channel.trending_videos && channel.trending_videos.length > 0 ? (
                            renderVideoTable(channel.trending_videos, 'Trending Videos', false, true)
                          ) : (
                            <div className="text-center py-8 text-gray-500">
                              No trending videos found
                            </div>
                          )}
                        </div>
                        
                        {/* Trending Shorts */}
                        <div>
                          <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800 mr-2">
                              Top 3 Shorts ({channel.total_trending_shorts || channel.trending_shorts?.length || 0}) [REAL-TIME]
                            </span>
                          </h4>
                          {channel.trending_shorts && channel.trending_shorts.length > 0 ? (
                            renderVideoTable(channel.trending_shorts, 'Trending Shorts', true, true)
                          ) : (
                            <div className="text-center py-8 text-gray-500">
                              No trending shorts found
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Live Videos Section */}
                  {channel.live_videos && channel.live_videos.length > 0 && (
                    <div className="mb-6">
                      <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-pink-100 text-pink-800 mr-2 animate-pulse">
                          🔴 LIVE ({channel.live_videos.length} {channel.live_videos.length === 1 ? 'video' : 'videos'}) [REAL-TIME]
                        </span>
                      </h4>
                      {renderVideoTable(channel.live_videos, 'Live Videos', false, false, true)}
                    </div>
                  )}

                  {/* Regular Videos and Shorts in Grid */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Regular Videos Column */}
                    <div>
                    <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 mr-2">
                        Top 5 Videos ({channel.total_videos || 0})
                      </span>
                    </h4>
                      {renderVideoTable(channel.videos, 'Videos', false)}
                    </div>

                    {/* Shorts Column */}
                    <div>
                    <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800 mr-2">
                        Top 5 Shorts ({channel.total_shorts || 0})
                      </span>
                    </h4>
                      {renderVideoTable(channel.shorts, 'Shorts', true)}
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">
                  {channel.error || 'No videos found for this channel.'}
                </p>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default VideoResults;
