import os
import argparse
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def search_businesses(zone, business_type="commerce"):
    """
    Search for businesses in a specific geographic zone using Google Places API (New).
    """
    if not GOOGLE_MAPS_API_KEY:
        print("Error: GOOGLE_MAPS_API_KEY is not set in the .env file.")
        return []

    url = "https://places.googleapis.com/v1/places:searchText"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.websiteUri,places.internationalPhoneNumber,places.googleMapsUri,places.rating,places.userRatingCount"
    }

    query = f"{business_type} in {zone}"
    
    payload = {
        "textQuery": query,
        "languageCode": "fr",
        # "pageSize": 20 # Optional: can be configured
    }

    print(f"Searching for '{query}'...")
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Error calling Google API: {response.status_code} - {response.text}")
        return []

    data = response.json()
    places = data.get("places", [])
    
    print(f"Found {len(places)} total results.")
    
    # Filter businesses without a website
    potential_clients = []
    for place in places:
        # If 'websiteUri' is not present, the business does not have a website listed on Google Maps
        if "websiteUri" not in place:
            name = place.get("displayName", {}).get("text", "Unknown")
            address = place.get("formattedAddress", "Unknown")
            phone = place.get("internationalPhoneNumber", "N/A")
            maps_url = place.get("googleMapsUri", "N/A")
            rating = place.get("rating", "N/A")
            ratings_count = place.get("userRatingCount", 0)

            potential_clients.append({
                "Name": name,
                "Address": address,
                "Phone": phone,
                "Rating": rating,
                "Ratings Count": ratings_count,
                "Google Maps URL": maps_url
            })

    print(f"Filtered to {len(potential_clients)} potential clients (no website).")
    return potential_clients

def export_to_csv(clients, zone):
    if not clients:
        print("No clients to export.")
        return

    filename = f"leads_{zone.replace(' ', '_').lower()}.csv"
    df = pd.DataFrame(clients)
    df.to_csv(filename, index=False)
    print(f"Results exported to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find potential clients on Google Maps (businesses without a website).")
    parser.add_argument("zone", help="Geographic zone to search in (e.g., 'Paris', 'Lyon 3ème')")
    parser.add_argument("--type", default="commerces", help="Type of business to search for (default: 'commerces')")
    
    args = parser.parse_args()
    
    clients = search_businesses(args.zone, args.type)
    export_to_csv(clients, args.zone)
    
    # Note: To export to Google Sheets directly, additional setup with gspread and a service account is required.
    # For now, we generate a CSV file that can be easily imported into Google Sheets.
