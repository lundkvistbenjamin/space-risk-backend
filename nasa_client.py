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

def fetch_cmes(start_date, end_date):
    endpoint = f"{BASE_URL}/CME"
    params = {
        "startDate": start_date, 
        "endDate": end_date, 
        "api_key": NASA_API_KEY
    }

    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching CMEs: HTTP {response.status_code}")
        return []

if __name__ == "__main__":
    start_date = "2026-07-01"
    end_date = "2026-07-29"

    # Fetch both event types
    flares = fetch_solar_flares(start_date, end_date)
    cmes = fetch_cmes(start_date, end_date)

    print(f"Found {len(flares)} flare event(s).")
    print(f"Found {len(cmes)} CME event(s).")

    if cmes:
        sample_cme = cmes[0]

        # Safely extract the nested cmeAnalyses list
        analyses = sample_cme.get("cmeAnalyses", [])

        # If analyses exist, grab speed from the first item; otherwise default to "N/A"
        speed = analyses[0].get("speed") if analyses else "N/A"

        print("\nSample CME Data:")
        print("Activity ID:", sample_cme.get("activityID"))
        print("Start Time:", sample_cme.get("startTime"))
        print("Speed (km/s):", speed)