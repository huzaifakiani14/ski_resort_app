import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import spacy
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SkiResortFinder:
    def __init__(self, api_key):
        self.api_key = api_key
        self.geocoder = Nominatim(user_agent="ski_resort_finder")
        self.nlp = spacy.load("en_core_web_trf")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def find_resorts(self, query):
        # Get location coordinates from query
        try:
            location = self.geocoder.geocode(query)
            if not location:
                return []
                
            lat, lon = location.latitude, location.longitude
            
            # Search for ski resorts using Google Places API
            url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{lat},{lon}",
                'radius': 50000,  # 50km radius
                'type': 'point_of_interest',
                'keyword': 'ski resort',
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] != 'OK':
                return []
                
            resorts = []
            for place in data['results']:
                # Get detailed information for each resort
                place_id = place['place_id']
                details_url = f"https://maps.googleapis.com/maps/api/place/details/json"
                details_params = {
                    'place_id': place_id,
                    'fields': 'name,formatted_address,rating,reviews,photos,website',
                    'key': self.api_key
                }
                
                details_response = requests.get(details_url, params=details_params)
                details_data = details_response.json()
                
                if details_data['status'] == 'OK':
                    resort = details_data['result']
                    
                    # Calculate distance from search location
                    resort_location = (resort['geometry']['location']['lat'],
                                     resort['geometry']['location']['lng'])
                    distance = geodesic((lat, lon), resort_location).kilometers
                    
                    # Get photo reference if available
                    photo_ref = None
                    if 'photos' in resort:
                        photo_ref = resort['photos'][0]['photo_reference']
                    
                    resorts.append({
                        'name': resort['name'],
                        'address': resort['formatted_address'],
                        'rating': resort.get('rating', 0),
                        'distance': round(distance, 2),
                        'photo_ref': photo_ref,
                        'website': resort.get('website', ''),
                        'reviews': resort.get('reviews', [])
                    })
            
            # Sort resorts by relevance score
            resorts = self._sort_by_relevance(resorts, query)
            return resorts[:10]  # Return top 10 results
            
        except Exception as e:
            print(f"Error finding resorts: {str(e)}")
            return []
            
    def _sort_by_relevance(self, resorts, query):
        # Create query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Create resort descriptions and their embeddings
        resort_descriptions = []
        for resort in resorts:
            description = f"{resort['name']} {resort['address']}"
            resort_descriptions.append(description)
            
        resort_embeddings = self.model.encode(resort_descriptions)
        
        # Calculate cosine similarity scores
        similarities = cosine_similarity([query_embedding], resort_embeddings)[0]
        
        # Combine similarity scores with distance and rating
        for i, resort in enumerate(resorts):
            resort['relevance_score'] = (
                0.4 * similarities[i] +  # Semantic similarity
                0.3 * (1 - min(resort['distance'] / 100, 1)) +  # Distance (normalized)
                0.3 * (resort['rating'] / 5)  # Rating
            )
            
        # Sort by relevance score
        return sorted(resorts, key=lambda x: x['relevance_score'], reverse=True) 