import os
import requests
from dotenv import load_dotenv

# Load key-value pairs from .env file into environment
load_dotenv()

NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
BASE_URL = "https://api.nasa.gov/DONKI"

def fetch_solar_flares(start_date, end_date):
    endpoint = f"{BASE_URL}/FLR"
    params = {
        "startDate": start_date, 
        "endDate": end_date, 
        "api_key": NASA_API_KEY
    }

    response = requests.get(endpoint, params=params)

    if response.status_code == 200: 
        return response.json()
    else: 
        print(f"Error fetching flares: HTTP {response.status_code}")
        return []

if __name__ == "__main__":
    # Test call: Fetch flares for the last 30 days
    flares = fetch_solar_flares("2026-07-01", "2026-07-29")
    print(f"Found {len(flares)} flare event(s).")
    
    if flares:
        # Inspect the first returned event
        print("\nSample Flare Data:")
        print("Class:", flares[0].get("classType"))
        print("Peak Time:", flares[0].get("peakTime"))