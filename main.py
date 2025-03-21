from ski_resort_finder import SkiResortFinder
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("GOOGLE_PLACES_API")

    ski_finder = SkiResortFinder(api_key)

    user_query = "ski resorts near Amherst"

    sorted_resorts = ski_finder.find_best_ski_resorts(user_query)

    if sorted_resorts:
        for resort in sorted_resorts:
            print(f"🏔️ {resort['name']} - {resort['address']} (⭐ {resort['rating']}, 📍 {round(resort['distance'], 2)} km)")
    else:
        print("No resorts found.")
