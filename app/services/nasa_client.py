from datetime import datetime, timedelta, timezone
import requests
from app.config import DONKI_BASE_URL, NASA_API_KEY

# Fetch Solar Flare (FLR) events from NASA DONKI
def fetch_solar_flares(start_date: str, end_date: str) -> list:

    endpoint = f"{DONKI_BASE_URL}/FLR"

    params = {
        "startDate": start_date,
        "endDate": end_date,
        "api_key": NASA_API_KEY,
    }

    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        return response.json()

    print(
    f"Error fetching Solar Flares "
    f"(HTTP {response.status_code})"
    )
    return []


# Fetch Coronal Mass Ejection (CME) events from NASA DONKI
def fetch_cmes(start_date: str, end_date: str) -> list:

    endpoint = f"{DONKI_BASE_URL}/CME"

    params = {
        "startDate": start_date,
        "endDate": end_date,
        "api_key": NASA_API_KEY,
    }

    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        return response.json()

    print(
    f"Error fetching CMEs "
    f"(HTTP {response.status_code})"
    )
    return []


# Generate a rolling UTC date range ending today
def get_date_range(days_back: int = 30) -> tuple[str, str]:

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_back)

    # Format dates as YYYY-MM-DD
    return (
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
    )


# Test the NASA client independently
if __name__ == "__main__":

    start_date, end_date = get_date_range(days_back=30)

    print(f"Fetching data from {start_date} to {end_date}...\n")

    flares = fetch_solar_flares(start_date, end_date)
    cmes = fetch_cmes(start_date, end_date)

    print(f"Found {len(flares)} flare event(s).")
    print(f"Found {len(cmes)} CME event(s).")

    if cmes:

        sample_cme = cmes[0]

        # Safely extract the nested cmeAnalyses list
        analyses = sample_cme.get("cmeAnalyses", [])

        # Grab the first speed if analyses exist
        speed = analyses[0].get("speed") if analyses else "N/A"

        print("\nSample CME Data:")
        print("Activity ID:", sample_cme.get("activityID"))
        print("Start Time:", sample_cme.get("startTime"))
        print("Speed (km/s):", speed)