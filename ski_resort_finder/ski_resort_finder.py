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
        self.API_KEY = api_key or os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.API_KEY:
            raise ValueError("No Google Places API key provided")
            
        self.model = SentenceTransformer(model_name)
        self.nlp = spacy.load("en_core_web_trf")
        self.max_distance_km = max_distance_km
        self.popular_keywords = [
            "ski resort", "ski area", "ski mountain", "ski hill", "ski center",
            "snow resort", "winter resort", "alpine resort", "mountain resort"
        ]

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
        locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
        return locations[0] if locations else None

    def fetch_ski_resorts_for_point(self, lat, lng):
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        results = []
        seen_resorts = set()
        next_page_token = None

        while True:
            try:
                params = {
                    "location": f"{lat},{lng}",
                    "radius": 50000,
                    "keyword": "|".join(self.popular_keywords),
                    "type": "establishment",
                    "key": self.API_KEY
                }
                if next_page_token:
                    params["pagetoken"] = next_page_token

                response = requests.get(url, params=params)
                if response.status_code != 200:
                    print(f"Error: Places API returned status code {response.status_code}")
                    break

                data = response.json()
                if data.get("status") != "OK":
                    print(f"Error: Places API returned status {data.get('status')}")
                    break

                for place in data.get("results", []):
                    try:
                        place_id = place.get("place_id")
                        name = place.get("name", "").lower()

                        if place_id in seen_resorts or any(term in name for term in [
                            "shop", "club", "sledding", "touring", "tubing", "hill", 
                            "lodge", "center", "parking", "cross country", "cabin",
                            "rental", "store", "equipment", "repair", "school", "lesson"
                        ]):
                            continue

                        details_url = f"https://maps.googleapis.com/maps/api/place/details/json"
                        details_params = {
                            'place_id': place_id,
                            'fields': 'name,formatted_address,rating,reviews,website,geometry',
                            'key': self.API_KEY
                        }
                        
                        details_response = requests.get(details_url, params=details_params)
                        if details_response.status_code != 200:
                            print(f"Error: Places Details API returned status code {details_response.status_code}")
                            continue
                            
                        details_data = details_response.json()
                        if details_data['status'] != 'OK':
                            print(f"Error: Places Details API returned status {details_data.get('status')}")
                            continue
                            
                        resort = details_data['result']
                        
                        if 'geometry' not in resort or 'location' not in resort['geometry']:
                            print(f"Warning: Missing geometry data for resort {resort.get('name')}")
                            continue
                            
                        resort_location = (resort['geometry']['location']['lat'],
                                         resort['geometry']['location']['lng'])
                        distance = geodesic((lat, lng), resort_location).kilometers
                        
                        resort_data = {
                            "name": resort['name'],
                            "address": resort['formatted_address'],
                            "rating": resort.get('rating', 0),
                            "lat": resort['geometry']['location']['lat'],
                            "lng": resort['geometry']['location']['lng'],
                            "distance": distance,
                            "website": resort.get('website', ''),
                            "reviews": resort.get('reviews', [])
                        }
                        results.append(resort_data)
                        seen_resorts.add(place_id)
                        
                    except Exception as e:
                        print(f"Error processing resort {place.get('name', 'unknown')}: {str(e)}")
                        continue

                next_page_token = data.get("next_page_token")
                if not next_page_token:
                    break
                time.sleep(1)
                
            except Exception as e:
                print(f"Error in fetch_ski_resorts_for_point: {str(e)}")
                break
                
        return results

    def get_ski_resorts_grid_search(self, center_lat, center_lng):
        step_distance = 50  # Step in km
        lat_step = step_distance / 110.574
        lng_step = step_distance / (111.320 * abs(np.cos(np.radians(center_lat))))

        ski_resorts = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            lat_lng_points = [(center_lat + d_lat * lat_step, center_lng + d_lng * lng_step) 
                            for d_lat in [-1, 0, 1] for d_lng in [-1, 0, 1]]
            ski_resorts = list(executor.map(lambda point: self.fetch_ski_resorts_for_point(*point), lat_lng_points))
        return [resort for sublist in ski_resorts for resort in sublist]

    def filter_by_distance(self, resorts, lat, lng):
        return [
            {**resort, "distance": geodesic((lat, lng), (resort["lat"], resort["lng"])).km}
            for resort in resorts if geodesic((lat, lng), (resort["lat"], resort["lng"])).km <= self.max_distance_km
        ]

    def create_resort_embeddings(self, resorts):
        return np.array([self.model.encode(resort["name"] + " " + resort["address"]) for resort in resorts])

    def get_top_matches(self, query, resort_embeddings, resorts, top_n=30):
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
        top_resorts = self.get_top_matches(user_query, resort_embeddings, ski_resorts, top_n=30)
        return self.sort_resorts(top_resorts)

    def find_resorts(self, query):
        results = self.find_best_ski_resorts(query)
        if not results:
            return []
            
        # Format results to match the frontend's expected structure
        formatted_results = []
        for resort in results:
            formatted_resort = {
                'name': resort['name'],
                'address': resort['address'],
                'rating': resort['rating'],
                'distance': round(resort['distance'], 2),
                'website': resort.get('website', ''),
                'reviews': resort.get('reviews', [])
            }
            formatted_results.append(formatted_resort)
            
        return formatted_results