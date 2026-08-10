import logging
from datetime import datetime, timezone
from supabase import Client, create_client
from app.config import SUPABASE_KEY, SUPABASE_URL
from app.services.risk_engine import generate_space_weather_assessment

from app.services.nasa_client import (
    fetch_cmes,
    fetch_solar_flares,
    get_date_range,
)
from app.services.event_transformer import (
    extract_cme_features,
    parse_flare_class,
)


logger = logging.getLogger(__name__)

# Find the strongest solar flare within the selected date range
def get_peak_flare(raw_flares: list) -> tuple[float, str | None]:

    max_flux = 0.0
    peak_flare_class = None

    for flare in raw_flares:

        raw_class = flare.get("classType")

        parsed_flux = parse_flare_class(raw_class)

        if parsed_flux > max_flux:
            max_flux = parsed_flux
            peak_flare_class = raw_class

    return max_flux, peak_flare_class


# Find the most significant CME
# Earth-directed CMEs are always prioritized over non-Earth-directed ones.
# If two CMEs have the same priority, the faster one is selected.
def get_primary_cme(raw_cmes: list) -> dict:

    top_cme = {
        "speed": 0.0,
        "half_angle": 0.0,
        "is_earth_directed": False,
    }

    for cme in raw_cmes:

        features = extract_cme_features(cme)

        # Prefer Earth-directed CMEs
        if (
            features["is_earth_directed"]
            and not top_cme["is_earth_directed"]
        ):
            top_cme = features
            continue

        # Otherwise compare speeds if both have the same priority
        if (
            features["is_earth_directed"]
            == top_cme["is_earth_directed"]
            and features["speed"] > top_cme["speed"]
        ):
            top_cme = features

    return top_cme


# Run the complete ingestion pipeline
def run_pipeline(days_back: int = 30) -> dict:

    start_date, end_date = get_date_range(days_back)

    logger.info(
        "Fetching space weather data (%s to %s)...",
        start_date,
        end_date,
    )

    # Download raw NASA DONKI data
    raw_flares = fetch_solar_flares(start_date, end_date)
    raw_cmes = fetch_cmes(start_date, end_date)

    # Determine the strongest flare
    peak_flux, peak_flare_class = get_peak_flare(raw_flares)

    # Determine the primary CME
    primary_cme = get_primary_cme(raw_cmes)

    # Generate the risk assessment
    assessment = generate_space_weather_assessment(
        peak_flux,
        primary_cme,
    )

    # Construct the payload returned by the pipeline
    payload = {

        "metadata": {

            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "window_start": start_date,
            "window_end": end_date,

            "events_analyzed": {

                "flare_count": len(raw_flares),
                "cme_count": len(raw_cmes),

            },
        },

        "observed_extremes": {

            "peak_solar_flare_class": (
                peak_flare_class or "None"
            ),

            "peak_xray_flux_wm2": peak_flux,

            "primary_cme_features": primary_cme,

        },

        "risk_assessment": assessment,
    }

    return payload


# Save the generated assessment to Supabase
def save_to_supabase(payload: dict):

    if not SUPABASE_URL or not SUPABASE_KEY:

        logger.warning(
            "Supabase credentials missing. "
            "Skipping database upload."
        )

        return

    supabase: Client = create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )

    # Flatten the nested payload into the database schema
    row = {

        "generated_at":
            payload["metadata"]["generated_at"],

        "window_start":
            payload["metadata"]["window_start"],

        "window_end":
            payload["metadata"]["window_end"],

        "flare_count":
            payload["metadata"]["events_analyzed"]["flare_count"],

        "cme_count":
            payload["metadata"]["events_analyzed"]["cme_count"],

        "peak_solar_flare_class":
            payload["observed_extremes"]["peak_solar_flare_class"],

        "peak_xray_flux_wm2":
            payload["observed_extremes"]["peak_xray_flux_wm2"],

        "primary_cme_features":
            payload["observed_extremes"]["primary_cme_features"],

        "scores":
            payload["risk_assessment"]["scores"],

        "threat_level":
            payload["risk_assessment"]["threat_level"],
    }

    response = (
        supabase
        .table("space_weather_assessments")
        .insert(row)
        .execute()
    )

    logger.info(
        "Successfully pushed record to Supabase!"
    )

    return response


# Allow the pipeline to be executed directly
if __name__ == "__main__":

    results = run_pipeline(days_back=30)

    save_to_supabase(results)