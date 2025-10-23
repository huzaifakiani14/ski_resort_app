import requests
from dotenv import load_dotenv
import os
import time
import spacy
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from geopy.distance import geodesic
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

class SkiResortFinder:
    def __init__(self, api_key, model_name='paraphrase-distilroberta-base-v1', max_distance_km=100):
        load_dotenv()
        self.API_KEY = api_key
        self.model = SentenceTransformer(model_name)
        
        # Use a smaller spaCy model that's easier to deploy
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except:
            # If the model isn't available, download a small one
            spacy.cli.download('en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')
            
        self.max_distance_km = max_distance_km
        
        # Known major ski resorts by state
        self.known_resorts = {
            'massachusetts': [
                'Wachusett Mountain',
                'Berkshire East',
                'Jiminy Peak',
                'Nashoba Valley',
                'Blandford Ski Area'
            ],
            'vermont': [
                'Killington Resort',
                'Stowe Mountain Resort',
                'Mount Snow',
                'Sugarbush Resort',
                'Okemo Mountain Resort'
            ],
            'new hampshire': [
                'Loon Mountain',
                'Waterville Valley',
                'Bretton Woods',
                'Cannon Mountain',
                'Mount Sunapee'
            ],
            'maine': [
                'Sunday River',
                'Sugarloaf',
                'Saddleback Mountain',
                'Shawnee Peak',
                'Mount Abram'
            ]
        }

    @lru_cache(maxsize=100)
    def get_lat_lng_from_location(self, location):
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": location, "key": self.API_KEY}
        response = requests.get(url, params=params).json()

        if response.get("results"):
            lat = response["results"][0]["geometry"]["location"]["lat"]
            lng = response["results"][0]["geometry"]["location"]["lng"]
            return lat, lng
        return None, None

    def extract_location(self, query):
        doc = self.nlp(query)
        locations = []
        
        # Extract locations and states
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                locations.append(ent.text.lower())
        
        # Check for state names in the query
        state_keywords = {
            'massachusetts': ['massachusetts', 'ma', 'berkshire', 'wachusett'],
            'vermont': ['vermont', 'vt', 'killington', 'stowe'],
            'new hampshire': ['new hampshire', 'nh', 'loon', 'waterville'],
            'maine': ['maine', 'me', 'sunday river', 'sugarloaf']
        }
        
        for state, keywords in state_keywords.items():
            if any(keyword in query.lower() for keyword in keywords):
                locations.append(state)
        
        return locations[0] if locations else None

    def fetch_ski_resorts_for_point(self, lat, lng):
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        results = []
        seen_resorts = set()
        next_page_token = None

        while True:
            params = {
                "location": f"{lat},{lng}",
                "radius": 50000,  # Increased radius to 50km
                "keyword": "ski resort|mountain|ski area|ski hill",
                "type": "establishment",
                "key": self.API_KEY
            }
            if next_page_token:
                params["pagetoken"] = next_page_token

            response = requests.get(url, params=params)
            if response.status_code != 200:
                break

            data = response.json()
            if data.get("status") != "OK":
                break

            for place in data.get("results", []):
                place_id = place.get("place_id")
                name = place.get("name", "").lower()
                vicinity = place.get("vicinity", "").lower()

                # Skip if already seen or not a ski resort
                if place_id in seen_resorts:
                    continue

                # Check if it's a ski resort
                ski_keywords = ['ski', 'snowboard', 'mountain', 'resort', 'slope', 'lift']
                if not any(keyword in name or keyword in vicinity for keyword in ski_keywords):
                    continue

                # Skip non-resort places
                exclude_keywords = ['shop', 'club', 'sledding', 'touring', 'tubing', 'hill', 'lodge', 'center', 'parking', 'cross country', 'cabin']
                if any(term in name for term in exclude_keywords):
                    continue

                resort = {
                    "name": place.get("name"),
                    "address": place.get("vicinity"),
                    "rating": place.get("rating", 0),
                    "lat": place["geometry"]["location"]["lat"],
                    "lng": place["geometry"]["location"]["lng"],
                    "place_id": place_id
                }
                results.append(resort)
                seen_resorts.add(place_id)

            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break
            time.sleep(1)
        return results

    def get_ski_resorts_grid_search(self, center_lat, center_lng):
        step_distance = 30  # Reduced step distance for better coverage
        lat_step = step_distance / 110.574
        lng_step = step_distance / (111.320 * abs(np.cos(np.radians(center_lat))))

        ski_resorts = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            lat_lng_points = [(center_lat + d_lat * lat_step, center_lng + d_lng * lng_step) 
                            for d_lat in [-2, -1, 0, 1, 2] 
                            for d_lng in [-2, -1, 0, 1, 2]]
            ski_resorts = list(executor.map(lambda point: self.fetch_ski_resorts_for_point(*point), lat_lng_points))
        return [resort for sublist in ski_resorts for resort in sublist]

    def filter_by_distance(self, resorts, lat, lng):
        return [
            {**resort, "distance": geodesic((lat, lng), (resort["lat"], resort["lng"])).km}
            for resort in resorts if geodesic((lat, lng), (resort["lat"], resort["lng"])).km <= self.max_distance_km
        ]

    def create_resort_embeddings(self, resorts):
        return np.array([self.model.encode(resort["name"] + " " + resort["address"]) for resort in resorts])

    def get_top_matches(self, query, resort_embeddings, resorts, top_n=10):
        user_query_embedding = self.model.encode(query).reshape(1, -1)
        similarities = cosine_similarity(user_query_embedding, resort_embeddings)[0]
        sorted_resorts = sorted(zip(resorts, similarities), key=lambda x: -x[1])[:top_n]
        return [resort for resort, _ in sorted_resorts]

    def remove_duplicates(self, resorts):
        unique_resorts = {}
        for resort in resorts:
            key = (resort["name"].lower(), resort["address"].lower())
            if key not in unique_resorts:
                unique_resorts[key] = resort
        return list(unique_resorts.values())

    def remove_invalid_resorts(self, resorts):
        return [resort for resort in resorts if resort['rating'] > 0]

    def sort_resorts(self, resorts):
        return sorted(resorts, key=lambda x: (-x["rating"], x["distance"]))

    def find_best_ski_resorts(self, user_query):
        location = self.extract_location(user_query)
        if not location:
            return None

        # Check if we have known resorts for this location
        location_lower = location.lower()
        for state, resorts in self.known_resorts.items():
            if state in location_lower:
                # Get coordinates for the state
                lat, lng = self.get_lat_lng_from_location(state)
                if lat and lng:
                    # Combine known resorts with found resorts
                    known_resorts_data = []
                    for resort_name in resorts:
                        resort_data = {
                            "name": resort_name,
                            "address": f"{resort_name}, {state.title()}",
                            "rating": 4.5,  # Default rating for known resorts
                            "lat": lat,
                            "lng": lng,
                            "place_id": None
                        }
                        known_resorts_data.append(resort_data)
                    
                    # Get additional resorts from Google Places
                    found_resorts = self.get_ski_resorts_grid_search(lat, lng)
                    all_resorts = known_resorts_data + found_resorts
                    
                    # Process and return results
                    all_resorts = self.filter_by_distance(all_resorts, lat, lng)
                    all_resorts = self.remove_duplicates(all_resorts)
                    all_resorts = self.remove_invalid_resorts(all_resorts)
                    
                    if not all_resorts:
                        return None
                    
                    resort_embeddings = self.create_resort_embeddings(all_resorts)
                    top_resorts = self.get_top_matches(user_query, resort_embeddings, all_resorts, top_n=10)
                    return self.sort_resorts(top_resorts)

        # If no known resorts found, proceed with regular search
        latitude, longitude = self.get_lat_lng_from_location(location)
        if not latitude or not longitude:
            return None

        ski_resorts = self.get_ski_resorts_grid_search(latitude, longitude)
        ski_resorts = self.filter_by_distance(ski_resorts, latitude, longitude)
        ski_resorts = self.remove_duplicates(ski_resorts)
        ski_resorts = self.remove_invalid_resorts(ski_resorts)

        if not ski_resorts:
            return None

        resort_embeddings = self.create_resort_embeddings(ski_resorts)
        top_resorts = self.get_top_matches(user_query, resort_embeddings, ski_resorts, top_n=10)
        return self.sort_resorts(top_resorts)
