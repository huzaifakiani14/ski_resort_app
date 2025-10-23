from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import traceback
import sys
sys.path.append('ski_resort_finder')
from ski_resort import SkiResortFinder

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Configure Cross-Origin Resource Sharing (CORS)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:5000",
            "https://*.vercel.app",
            "https://ski-resort-app.vercel.app"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize SkiResortFinder with Google Maps API key
api_key = os.getenv('GOOGLE_MAPS_API_KEY') or os.getenv('GOOGLE_PLACES_API_KEY')
if not api_key:
    print("Warning: No Google Maps API key found in environment variables")
    ski_finder = None
else:
    try:
        ski_finder = SkiResortFinder(api_key)
        print("SkiResortFinder initialized successfully")
    except Exception as e:
        print(f"Error initializing SkiResortFinder: {str(e)}")
        print(traceback.format_exc())
        ski_finder = None

@app.route('/api/test', methods=['GET'])
def test_connection():
    try:
        return jsonify({
            "status": "success",
            "message": "Backend server is running",
            "api_key_configured": bool(api_key)
        })
    except Exception as e:
        print(f"Error in test_connection: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/search', methods=['POST'])
def search_resorts():
    try:
        if not ski_finder:
            return jsonify({"error": "Ski resort finder not initialized. Please check API key configuration."}), 500

        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400

        query = data['query']
        if not query.strip():
            return jsonify({"error": "Query cannot be empty"}), 400

        results = ski_finder.find_best_ski_resorts(query)
        if not results:
            return jsonify({"error": "No ski resorts found for the given query"}), 404

        return jsonify(results)
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": "An error occurred while processing your request"}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# For Vercel deployment
handler = app
