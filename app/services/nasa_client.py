from datetime import datetime, timedelta, timezone
import logging
import requests
from app.config import DONKI_BASE_URL, NASA_API_KEY


logger = logging.getLogger(__name__)

# Fetch Solar Flare (FLR) events from NASA DONKI
def fetch_solar_flares(start_date: str, end_date: str) -> list:

    endpoint = f"{DONKI_BASE_URL}/FLR"

    params = {
        "startDate": start_date,
        "endDate": end_date,
        "api_key": NASA_API_KEY,
    }

    try:

        response = requests.get(
            endpoint,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:

        logger.error(
            "Error fetching Solar Flares: %s",
            error,
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

    try:

        response = requests.get(
            endpoint,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:

        logger.error(
            "Error fetching CMEs: %s",
            error,
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

    logger.info(
        "Fetching data from %s to %s",
        start_date,
        end_date,
    )

    flares = fetch_solar_flares(start_date, end_date)
    cmes = fetch_cmes(start_date, end_date)

    logger.info(
        "Found %s flare event(s).",
        len(flares),
    )

    logger.info(
        "Found %s CME event(s).",
        len(cmes),
    )

    if cmes:

        sample_cme = cmes[0]

        # Safely extract the nested cmeAnalyses list
        analyses = sample_cme.get("cmeAnalyses", [])

        # Grab the first speed if analyses exist
        speed = analyses[0].get("speed") if analyses else "N/A"

        logger.info("Sample CME Data:")
        logger.info(
            "Activity ID: %s",
            sample_cme.get("activityID"),
        )
        logger.info(
            "Start Time: %s",
            sample_cme.get("startTime"),
        )
        logger.info(
            "Speed (km/s): %s",
            speed,
        )