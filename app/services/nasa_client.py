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