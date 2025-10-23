"""
Ski Resort Finder API
Flask backend for serving ski resort search requests.
This API interacts with the SkiResortFinder class to provide resort search functionality.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import traceback
from ski_resort import SkiResortFinder

# Load environment variables from .env file
# This includes the GOOGLE_MAPS_API_KEY or GOOGLE_PLACES_API
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Configure Cross-Origin Resource Sharing (CORS)
# This allows the frontend to make requests to this API from different origins
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",  # Development React server
            "http://localhost:5000",  # Alternative local development server
            "https://*.vercel.app",   # Vercel preview deployments
            "https://ski-resort-app.vercel.app"  # Production deployment
        ],
        "methods": ["GET", "POST", "OPTIONS"],  # Allowed HTTP methods
        "allow_headers": ["Content-Type"]       # Allowed request headers
    }
})

# Initialize SkiResortFinder with Google Maps API key
# First try GOOGLE_MAPS_API_KEY, then fallback to GOOGLE_PLACES_API_KEY if needed
api_key = os.getenv('GOOGLE_MAPS_API_KEY') or os.getenv('GOOGLE_PLACES_API_KEY')
if not api_key:
    print("Warning: No Google Maps API key found in environment variables")
    ski_finder = None
else:
    try:
        # Create an instance of SkiResortFinder with the API key
        ski_finder = SkiResortFinder(api_key)
        print("SkiResortFinder initialized successfully")
    except Exception as e:
        # Handle initialization errors gracefully
        print(f"Error initializing SkiResortFinder: {str(e)}")
        print(traceback.format_exc())
        ski_finder = None

@app.route('/test', methods=['GET'])
def test_connection_legacy():
    """
    Legacy endpoint for testing API connectivity
    Maintained for backward compatibility with older frontend versions
    Simply forwards to the new /api/test endpoint
    """
    return test_connection()

@app.route('/api/test', methods=['GET'])
def test_connection():
    """
    Endpoint to test if the API is running and configured properly
    Returns:
        JSON with status, message, and whether API key is configured
    """
    try:
        return jsonify({
            "status": "success",
            "message": "Backend server is running",
            "api_key_configured": bool(api_key)
        })
    except Exception as e:
        # Log the error for debugging
        print(f"Error in test_connection: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@app.route('/search', methods=['POST'])
def search_resorts_legacy():
    """
    Legacy endpoint for searching ski resorts
    Maintained for backward compatibility with older frontend versions
    Simply forwards to the new /api/search endpoint
    """
    return search_resorts()

@app.route('/api/search', methods=['POST'])
def search_resorts():
    """
    Main endpoint for searching ski resorts based on user query
    Expects: JSON with a 'query' field containing the search text
    Returns: JSON array of ski resort objects or error message
    """
    try:
        # Check if SkiResortFinder was properly initialized
        if not ski_finder:
            return jsonify({"error": "Ski resort finder not initialized. Please check API key configuration."}), 500

        # Extract and validate request data
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400

        query = data['query']
        if not query.strip():
            return jsonify({"error": "Query cannot be empty"}), 400

        # Perform the search using SkiResortFinder
        results = ski_finder.find_best_ski_resorts(query)
        if not results:
            return jsonify({"error": "No ski resorts found for the given query"}), 404

        # Return the search results
        return jsonify(results)
    except Exception as e:
        # Log the error for debugging
        print(f"Error processing request: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": "An error occurred while processing your request"}), 500

@app.errorhandler(404)
def not_found_error(error):
    """
    Handler for 404 Not Found errors
    Returns a JSON error response instead of HTML
    """
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Handler for 500 Internal Server errors
    Returns a JSON error response instead of HTML
    """
    return jsonify({"error": "Internal server error"}), 500

# Start the Flask server when this file is run directly
if __name__ == '__main__':
    # Get the port from environment variable or use 5001 as default
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting server on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)
else:
    # For Vercel deployment
    handler = app