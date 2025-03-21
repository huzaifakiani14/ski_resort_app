import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [resorts, setResorts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedResort, setSelectedResort] = useState(null);
  const [snowflakes, setSnowflakes] = useState([]);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [filters, setFilters] = useState({
    minRating: 0,
    maxDistance: 100,
    sortBy: 'rating'
  });
  const [recentSearches, setRecentSearches] = useState([]);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    // Check backend connection
    const checkBackendConnection = async () => {
      try {
        const response = await fetch('http://localhost:5001/test');
        if (response.ok) {
          setBackendStatus('connected');
        } else {
          setBackendStatus('error');
          setError('Backend server is not responding correctly');
        }
      } catch (err) {
        setBackendStatus('error');
        setError('Cannot connect to backend server. Please make sure the server is running.');
      }
    };

    checkBackendConnection();
  }, []);

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

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResorts([]);
    setSelectedResort(null);

    try {
      const response = await fetch('http://localhost:5001/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch ski resorts');
      }

      // Add to recent searches
      setRecentSearches(prev => {
        const newSearches = [query, ...prev.filter(s => s !== query)].slice(0, 5);
        localStorage.setItem('recentSearches', JSON.stringify(newSearches));
        return newSearches;
      });

      setResorts(data);
    } catch (err) {
      setError(err.message);
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleResortClick = (resort) => {
    setSelectedResort(resort);
  };

  const handleCloseModal = () => {
    setSelectedResort(null);
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const filteredResorts = resorts
    .filter(resort => resort.rating >= filters.minRating)
    .filter(resort => resort.distance <= filters.maxDistance)
    .sort((a, b) => {
      if (filters.sortBy === 'rating') return b.rating - a.rating;
      if (filters.sortBy === 'distance') return a.distance - b.distance;
      return 0;
    });

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
      {createSnowflakes()}
      <header className="hero">
        <div className="hero-content">
          <h1>Find Your Perfect Ski Resort</h1>
          <p>Search for ski resorts by location or description</p>
          {backendStatus === 'checking' && (
            <div className="backend-status checking">
              Checking backend connection...
            </div>
          )}
          {backendStatus === 'error' && (
            <div className="backend-status error">
              Backend connection error. Please check if the server is running.
            </div>
          )}
          <form onSubmit={handleSearch} className="search-form">
            <div className="search-input-container">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., ski resorts near Denver or best resorts in Colorado"
                className="search-input"
                disabled={backendStatus !== 'connected'}
                list="recent-searches"
              />
              <datalist id="recent-searches">
                {recentSearches.map((search, index) => (
                  <option key={index} value={search} />
                ))}
              </datalist>
            </div>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={backendStatus !== 'connected'}
            >
              Search
            </button>
          </form>
        </div>
      </header>

      <main className="container">
        {loading && (
          <div className="loading">
            <div className="snowflake">❄</div>
            <p>Finding the best ski resorts...</p>
          </div>
        )}

        {error && (
          <div className="error">
            <p>{error}</p>
          </div>
        )}

        {resorts.length > 0 && (
          <>
            <div className="filters-section">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowFilters(!showFilters)}
              >
                {showFilters ? 'Hide Filters' : 'Show Filters'}
              </button>
              
              {showFilters && (
                <div className="filters">
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
                  <h2>{resort.name}</h2>
                  <p className="address">{resort.address}</p>
                  <div className="resort-details">
                    <span className="rating">⭐ {resort.rating.toFixed(1)}</span>
                    <span className="distance">📍 {resort.distance.toFixed(1)} km</span>
                  </div>
                  {resort.photo_ref && (
                    <img
                      src={`https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=${resort.photo_ref}&key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}`}
                      alt={resort.name}
                      className="resort-image"
                    />
                  )}
                  {resort.website && (
                    <a
                      href={resort.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="website-link"
                      onClick={(e) => e.stopPropagation()}
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

      {selectedResort && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={handleCloseModal}>×</button>
            <h2>{selectedResort.name}</h2>
            <p className="address">{selectedResort.address}</p>
            <div className="resort-details">
              <span className="rating">⭐ {selectedResort.rating.toFixed(1)}</span>
              <span className="distance">📍 {selectedResort.distance.toFixed(1)} km</span>
            </div>
            {selectedResort.photo_ref && (
              <img
                src={`https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference=${selectedResort.photo_ref}&key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}`}
                alt={selectedResort.name}
                className="modal-image"
              />
            )}
            {selectedResort.reviews && selectedResort.reviews.length > 0 && (
              <div className="reviews-section">
                <h3>Recent Reviews</h3>
                <div className="reviews-list">
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

export default App;