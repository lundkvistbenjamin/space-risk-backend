from datetime import datetime, timedelta, timezone
import logging
import time

import requests

from app.config import DONKI_BASE_URL, NASA_API_KEY


logger = logging.getLogger(__name__)

# Number of attempts allowed for transient NASA API failures
MAX_ATTEMPTS = 3

# Delay between retry attempts, in seconds
RETRY_DELAY = 1


# Fetch Solar Flare (FLR) events from NASA DONKI
def fetch_solar_flares(start_date: str, end_date: str) -> list:

    endpoint = f"{DONKI_BASE_URL}/FLR"

    params = {
        "startDate": start_date,
        "endDate": end_date,
        "api_key": NASA_API_KEY,
    }

    for attempt in range(1, MAX_ATTEMPTS + 1):

        try:

            response = requests.get(
                endpoint,
                params=params,
                timeout=10,
            )

            # Retry rate-limit and temporary server errors
            if response.status_code == 429 or response.status_code >= 500:

                if attempt < MAX_ATTEMPTS:

                    logger.warning(
                        "NASA Solar Flare API returned HTTP %s. "
                        "Retrying (%s/%s)...",
                        response.status_code,
                        attempt,
                        MAX_ATTEMPTS,
                    )

                    time.sleep(RETRY_DELAY * attempt)
                    continue

            response.raise_for_status()

            return response.json()

        except requests.RequestException as error:

            if attempt < MAX_ATTEMPTS:

                logger.warning(
                    "Error fetching Solar Flares: %s. "
                    "Retrying (%s/%s)...",
                    error,
                    attempt,
                    MAX_ATTEMPTS,
                )

                time.sleep(RETRY_DELAY * attempt)
                continue

            logger.error(
                "Failed to fetch Solar Flares after %s attempts: %s",
                MAX_ATTEMPTS,
                error,
            )

            return []

    return []


# Fetch Coronal Mass Ejection (CME) events from NASA DONKI
def fetch_cmes(start_date: str, end_date: str) -> list:

    endpoint = f"{DONKI_BASE_URL}/CME"

    params = {
        "startDate": start_date,
        "endDate": end_date,
        "api_key": NASA_API_KEY,
    }

    for attempt in range(1, MAX_ATTEMPTS + 1):

        try:

            response = requests.get(
                endpoint,
                params=params,
                timeout=10,
            )

            # Retry rate-limit and temporary server errors
            if response.status_code == 429 or response.status_code >= 500:

                if attempt < MAX_ATTEMPTS:

                    logger.warning(
                        "NASA CME API returned HTTP %s. "
                        "Retrying (%s/%s)...",
                        response.status_code,
                        attempt,
                        MAX_ATTEMPTS,
                    )

                    time.sleep(RETRY_DELAY * attempt)
                    continue

            response.raise_for_status()

            return response.json()

        except requests.RequestException as error:

            if attempt < MAX_ATTEMPTS:

                logger.warning(
                    "Error fetching CMEs: %s. "
                    "Retrying (%s/%s)...",
                    error,
                    attempt,
                    MAX_ATTEMPTS,
                )

                time.sleep(RETRY_DELAY * attempt)
                continue

            logger.error(
                "Failed to fetch CMEs after %s attempts: %s",
                MAX_ATTEMPTS,
                error,
            )

            return []

    return []


# Generate the completed calendar day to assess
def get_assessment_date(days_back: int = 1) -> str:

    assessment_date = (
        datetime.now(timezone.utc).date()
        - timedelta(days=days_back)
    )

    return assessment_date.strftime("%Y-%m-%d")