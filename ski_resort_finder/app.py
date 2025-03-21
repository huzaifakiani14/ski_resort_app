from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from ski_resort import SkiResortFinder

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize SkiResortFinder with Google Maps API key
api_key = os.getenv('GOOGLE_MAPS_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_MAPS_API_KEY not found in environment variables")

ski_finder = SkiResortFinder(api_key)

@app.route('/test', methods=['GET'])
def test_connection():
    return jsonify({"status": "success", "message": "Backend server is running"})

@app.route('/search', methods=['POST'])
def search_resorts():
    try:
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
        return jsonify({"error": "An error occurred while processing your request"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)