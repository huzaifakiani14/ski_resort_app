from flask import Flask, request, jsonify
from flask_cors import CORS
from ski_resort_finder import SkiResortFinder
from dotenv import load_dotenv
import os
import traceback

app = Flask(__name__)
# Configure CORS to allow requests from the frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_PLACES_API_KEY")
if not api_key:
    print("Warning: No Google Places API key found in environment variables")
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
    return jsonify({
        'status': 'ok', 
        'message': 'Backend is running',
        'api_key_configured': bool(api_key)
    })

@app.route('/api/search', methods=['POST'])
def search_resorts():
    try:
        if not ski_finder:
            return jsonify({'error': 'Ski resort finder not initialized. Please check API key configuration.'}), 500
            
        data = request.get_json()
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
            
        results = ski_finder.find_resorts(query)
        if not results:
            return jsonify({'error': 'No ski resorts found for the given query'}), 404
            
        return jsonify(results)
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'An error occurred while processing your request'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0') 