/**
 * Ski Resort Finder Application
 * Main React component that handles the ski resort search functionality, 
 * UI rendering, and API interactions.
 */
import React, { useState, useEffect } from 'react';
import './App.css';

// Mock data for demonstration when backend is unavailable
const MOCK_DATA = {
  "vermont": [
    {
      "name": "Killington Resort",
      "address": "3861 Killington Road, Killington, VT 05751",
      "rating": 4.6,
      "lat": 43.6548,
      "lng": -72.7933,
      "place_id": "mock-id-1",
      "distance": 5.2
    },
    {
      "name": "Stowe Mountain Resort",
      "address": "7412 Mountain Road, Stowe, VT 05672",
      "rating": 4.8,
      "lat": 44.5303,
      "lng": -72.7814,
      "place_id": "mock-id-2",
      "distance": 8.1
    },
    {
      "name": "Mount Snow",
      "address": "39 Mount Snow Road, West Dover, VT 05356",
      "rating": 4.5,
      "lat": 42.9602,
      "lng": -72.9204,
      "place_id": "mock-id-3",
      "distance": 12.7
    }
  ],
  "new hampshire": [
    {
      "name": "Loon Mountain",
      "address": "60 Loon Mountain Road, Lincoln, NH 03251",
      "rating": 4.7,
      "lat": 44.0360,
      "lng": -71.6214,
      "place_id": "mock-id-4",
      "distance": 4.3
    },
    {
      "name": "Bretton Woods",
      "address": "99 Ski Area Road, Bretton Woods, NH 03575",
      "rating": 4.6,
      "lat": 44.2544,
      "lng": -71.4415,
      "place_id": "mock-id-5",
      "distance": 7.8
    }
  ],
  "maine": [
    {
      "name": "Sunday River",
      "address": "15 South Ridge Road, Newry, ME 04261",
      "rating": 4.7,
      "lat": 44.4734,
      "lng": -70.8570,
      "place_id": "mock-id-6",
      "distance": 6.2
    },
    {
      "name": "Sugarloaf",
      "address": "5092 Access Road, Carrabassett Valley, ME 04947",
      "rating": 4.8,
      "lat": 45.0334,
      "lng": -70.3133,
      "place_id": "mock-id-7",
      "distance": 9.1
    }
  ]
};

// Set API base URL based on environment
// In production, use relative paths; in development, use localhost with port
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '' // Empty string for relative paths in production
  : 'http://localhost:5001';

// Flag to use mock data in case backend is unavailable
const USE_MOCK_DATA = true;

function App() {
  // State variables
  const [query, setQuery] = useState(''); // Search query input by user
  const [resorts, setResorts] = useState([]); // Array of ski resorts returned from API
  const [loading, setLoading] = useState(false); // Loading state during API calls
  const [error, setError] = useState(null); // Error message if API call fails
  const [selectedResort, setSelectedResort] = useState(null); // Currently selected resort for modal view
  const [snowflakes, setSnowflakes] = useState([]); // Decorative snowflakes for UI
  const [backendStatus, setBackendStatus] = useState('checking'); // Status of backend connection
  const [filters, setFilters] = useState({
    minRating: 0, // Minimum rating filter (0-5)
    maxDistance: 100, // Maximum distance filter in km
    sortBy: 'rating' // Sort criteria ('rating' or 'distance')
  });
  const [recentSearches, setRecentSearches] = useState([]); // User's recent search queries
  const [showFilters, setShowFilters] = useState(false); // Toggle for filter section visibility

  /**
   * Effect hook to check backend connection on component mount
   * Tries multiple endpoints to handle both new and legacy API formats
   */
  useEffect(() => {
    // Check backend connection
    const checkBackendConnection = async () => {
      setBackendStatus('checking');
      // Try multiple endpoint patterns
      const endpoints = [
        `${API_BASE_URL}/api/test`,  // New API format
        `${API_BASE_URL}/test`       // Legacy format
      ];
      
      for (const endpoint of endpoints) {
        try {
          console.log(`Trying to connect to backend at: ${endpoint}`);
          const response = await fetch(endpoint);
          if (response.ok) {
            console.log(`Successfully connected to backend at: ${endpoint}`);
            setBackendStatus('connected');
            return; // Exit on success
          }
        } catch (err) {
          console.error(`Failed to connect to ${endpoint}:`, err);
          // Continue to next endpoint
        }
      }
      
      // If we get here, all endpoints failed
      setBackendStatus('error');
      setError('Cannot connect to backend server. Using demo data for demonstration.');
    };

    checkBackendConnection();
  }, []);

  /**
   * Effect hook to create decorative snowflakes for winter theme
   * Initializes 20 snowflakes with random positions and animation delays
   */
  useEffect(() => {
    // Create initial snowflakes
    const initialSnowflakes = Array.from({ length: 20 }).map((_, index) => ({
      id: index,
      left: `${Math.random() * 100}%`,
      animationDelay: `${Math.random() * 5}s`,
      size: Math.random() * 1.5 + 0.8,
    }));
    setSnowflakes(initialSnowflakes);
  }, []);

  /**
   * Handles the search form submission
   * Sends search query to backend API and processes results
   * Tries multiple endpoints to handle both new and legacy API formats
   * @param {Event} e - The form submission event
   */
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResorts([]);
    setSelectedResort(null);

    // Try multiple endpoint patterns
    const endpoints = [
      `${API_BASE_URL}/api/search`,  // New API format
      `${API_BASE_URL}/search`       // Legacy format
    ];

    let success = false;
    
    for (const endpoint of endpoints) {
      try {
        console.log(`Trying to search using endpoint: ${endpoint}`);
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query }),
        });

        const data = await response.json();

        if (!response.ok) {
          console.error(`Error from ${endpoint}:`, data.error);
          continue; // Try next endpoint
        }

        // Add to recent searches
        setRecentSearches(prev => {
          const newSearches = [query, ...prev.filter(s => s !== query)].slice(0, 5);
          localStorage.setItem('recentSearches', JSON.stringify(newSearches));
          return newSearches;
        });

        setResorts(data);
        success = true;
        break; // Exit on success
      } catch (err) {
        console.error(`Search error with ${endpoint}:`, err);
        // Continue to next endpoint
      }
    }

    if (!success) {
      setError('Failed to fetch ski resorts. Please try again later.');
    }
    
    setLoading(false);
  };

  /**
   * Opens the modal with detailed information about a selected resort
   * @param {Object} resort - The resort object to display in the modal
   */
  const handleResortClick = (resort) => {
    setSelectedResort(resort);
  };

  /**
   * Closes the resort details modal
   */
  const handleCloseModal = () => {
    setSelectedResort(null);
  };

  /**
   * Updates filter state when user changes filter values
   * @param {Event} e - Input change event from filter controls
   */
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  /**
   * Filtered and sorted list of resorts based on user's filter preferences
   * Filters by minimum rating and maximum distance, then sorts by rating or distance
   */
  const filteredResorts = resorts
    .filter(resort => resort.rating >= filters.minRating)
    .filter(resort => resort.distance <= filters.maxDistance)
    .sort((a, b) => {
      if (filters.sortBy === 'rating') return b.rating - a.rating; // Sort by rating (highest first)
      if (filters.sortBy === 'distance') return a.distance - b.distance; // Sort by distance (closest first)
      return 0;
    });

  /**
   * Creates decorative snowflake elements for the winter-themed UI
   * @returns {Array} Array of snowflake div elements with random positions
   */
  const createSnowflakes = () => {
    return snowflakes.map((snowflake) => (
      <div
        key={snowflake.id}
        className="snowflake"
        style={{
          left: snowflake.left,
          animationDelay: snowflake.animationDelay,
          fontSize: `${snowflake.size}em`,
        }}
      >
        ❄
      </div>
    ));
  };

  return (
    <div className="app">
      {/* Decorative snowflakes for winter theme */}
      {createSnowflakes()}
      
      {/* Hero section with title and search form */}
      <header className="hero">
        <div className="hero-content">
          <h1>Ski Resort Finder</h1>
          <p>Discover the perfect powder near you!</p>
          
          {/* Backend connection status indicators */}
          {backendStatus === 'checking' && (
            <div className="backend-status checking">
              Checking connection to our backend service...
            </div>
          )}
          {backendStatus === 'error' && (
            <div className="backend-status error">
              Backend unavailable. Using demo data for demonstration.
            </div>
          )}
          
          {backendStatus === 'demo' && (
            <div className="backend-status demo">
              Demo mode: Using sample data for demonstration purposes.
            </div>
          )}
          
          {/* Search form */}
          <form onSubmit={handleSearch} className="search-form">
            <div className="search-input-container">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter location (e.g., 'Vermont ski resorts')"
                className="search-input"
                disabled={backendStatus === 'checking'}
                list="recent-searches"
              />
              {/* Datalist for recent searches autocomplete */}
              <datalist id="recent-searches">
                {recentSearches.map((search, index) => (
                  <option key={index} value={search} />
                ))}
              </datalist>
            </div>
            {/* Search button */}
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={backendStatus === 'checking' || !query.trim()}
            >
              Search
            </button>
          </form>
        </div>
      </header>

      <main className="container">
        {/* Loading indicator shown during API requests */}
        {loading && (
          <div className="loading">
            <div className="snowflake">❄</div>
            <p>Finding the best ski resorts...</p>
          </div>
        )}

        {/* Error message display */}
        {error && (
          <div className="error">
            <p>{error}</p>
          </div>
        )}

        {/* Results section - only displayed when resorts are found */}
        {resorts.length > 0 && (
          <>
            {/* Filters section for refining search results */}
            <div className="filters-section">
              {/* Toggle button to show/hide filters */}
              <button 
                className="btn btn-secondary"
                onClick={() => setShowFilters(!showFilters)}
              >
                {showFilters ? 'Hide Filters' : 'Show Filters'}
              </button>
              
              {/* Filter controls - only displayed when showFilters is true */}
              {showFilters && (
                <div className="filters">
                  {/* Minimum rating filter - slider from 0 to 5 stars */}
                  <div className="filter-group">
                    <label>Minimum Rating:</label>
                    <input
                      type="range"
                      name="minRating"
                      min="0"
                      max="5"
                      step="0.5"
                      value={filters.minRating}
                      onChange={handleFilterChange}
                    />
                    <span>{filters.minRating} ⭐</span>
                  </div>
                  
                  {/* Maximum distance filter - slider from 0 to 200 km */}
                  <div className="filter-group">
                    <label>Max Distance:</label>
                    <input
                      type="range"
                      name="maxDistance"
                      min="0"
                      max="200"
                      step="10"
                      value={filters.maxDistance}
                      onChange={handleFilterChange}
                    />
                    <span>{filters.maxDistance} km</span>
                  </div>
                  
                  {/* Sort criteria selector - rating or distance */}
                  <div className="filter-group">
                    <label>Sort By:</label>
                    <select
                      name="sortBy"
                      value={filters.sortBy}
                      onChange={handleFilterChange}
                    >
                      <option value="rating">Rating</option>
                      <option value="distance">Distance</option>
                    </select>
                  </div>
                </div>
              )}
            </div>

            {/* Grid display of filtered resort results */}
            <div className="resorts-grid">
              {filteredResorts.map((resort, index) => (
                <div
                  key={index}
                  className="resort-card card"
                  onClick={() => handleResortClick(resort)}
                  style={{
                    animationDelay: `${index * 0.1}s`,
                  }}
                >
                  {/* Resort name */}
                  <h2>{resort.name}</h2>
                  
                  {/* Resort address */}
                  <p className="address">{resort.address}</p>
                  
                  {/* Rating and distance information */}
                  <div className="resort-details">
                    <span className="rating">⭐ {resort.rating.toFixed(1)}</span>
                    <span className="distance">📍 {resort.distance.toFixed(1)} km</span>
                  </div>
                  
                  {/* Resort image - only shown if photo reference exists */}
                  {resort.photo_ref && (
                    <img
                      src={`https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=${resort.photo_ref}&key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}`}
                      alt={resort.name}
                      className="resort-image"
                    />
                  )}
                  
                  {/* Resort website link - only shown if website exists */}
                  {resort.website && (
                    <a
                      href={resort.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="website-link"
                      onClick={(e) => e.stopPropagation()} // Prevent card click event
                    >
                      Visit Website
                    </a>
                  )}
                </div>
              ))}
            </div>
          </>
        )}
      </main>

      {/* Resort details modal - only shown when a resort is selected */}
      {selectedResort && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            {/* Close button */}
            <button className="modal-close" onClick={handleCloseModal}>×</button>
            
            {/* Resort name */}
            <h2>{selectedResort.name}</h2>
            
            {/* Resort address */}
            <p className="address">{selectedResort.address}</p>
            
            {/* Rating and distance information */}
            <div className="resort-details">
              <span className="rating">⭐ {selectedResort.rating.toFixed(1)}</span>
              <span className="distance">📍 {selectedResort.distance.toFixed(1)} km</span>
            </div>
            
            {/* Resort image - larger version for modal */}
            {selectedResort.photo_ref && (
              <img
                src={`https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference=${selectedResort.photo_ref}&key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}`}
                alt={selectedResort.name}
                className="modal-image"
              />
            )}
            
            {/* Reviews section - only shown if reviews exist */}
            {selectedResort.reviews && selectedResort.reviews.length > 0 && (
              <div className="reviews-section">
                <h3>Recent Reviews</h3>
                <div className="reviews-list">
                  {/* Display up to 3 reviews */}
                  {selectedResort.reviews.slice(0, 3).map((review, index) => (
                    <div key={index} className="review">
                      <div className="review-rating">⭐ {review.rating}</div>
                      <p className="review-text">{review.text}</p>
                      <div className="review-author">- {review.author_name}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Resort website link - only shown if website exists */}
            {selectedResort.website && (
              <a
                href={selectedResort.website}
                target="_blank"
                rel="noopener noreferrer"
                className="website-link"
              >
                Visit Website
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Export the App component as the default export
export default App;