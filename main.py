import json
from datetime import datetime, timezone

from nasa_client import fetch_solar_flares, fetch_cmes, get_date_range
from transformer import parse_flare_class, extract_cme_features
from risk_engine import generate_space_weather_assessment

def run_pipeline(days_back=30):
    start_date, end_date = get_date_range(days_back=days_back)
    print(f"[*] Fetching space weather data ({start_date} to {end_date})...")

    raw_flares = fetch_solar_flares(start_date, end_date)
    raw_cmes = fetch_cmes(start_date, end_date)

    # 1. Process Solar Flares: find the flare with the highest X-ray flux
    max_flux = 0.0
    top_flare_raw = None

    for flare in raw_flares:
        raw_class = flare.get("classType")
        parsed_flux = parse_flare_class(raw_class)
        if parsed_flux > max_flux:
            max_flux = parsed_flux
            top_flare_raw = raw_class

    # 2. Process CMEs: prioritize Earth-directed CMEs, then evaluate by speed
    top_cme_features = {"speed": 0.0, "half_angle": 0.0, "is_earth_directed": False}
    
    for cme in raw_cmes:
        features = extract_cme_features(cme)
        
        # Found first Earth-directed CME: replace non-Earth-directed candidate immediately
        if features["is_earth_directed"] and not top_cme_features["is_earth_directed"]:
            top_cme_features = features
            
        # Both are Earth-directed (or both are NOT): keep the faster one
        elif features["is_earth_directed"] == top_cme_features["is_earth_directed"]:
            if features["speed"] > top_cme_features["speed"]:
                top_cme_features = features

    # 3. Generate Risk Assessment
    assessment = generate_space_weather_assessment(max_flux, top_cme_features)

    # 4. Construct Final Pipeline Payload
    payload = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "window_start": start_date,
            "window_end": end_date,
            "events_analyzed": {
                "flare_count": len(raw_flares),
                "cme_count": len(raw_cmes)
            }
        },
        "observed_extremes": {
            "peak_solar_flare_class": top_flare_raw or "None",
            "peak_xray_flux_wm2": max_flux,
            "primary_cme_features": top_cme_features
        },
        "risk_assessment": assessment
    }

    return payload

if __name__ == "__main__":
    results = run_pipeline(days_back=30)
    print("\n--- Helios Pipeline Risk Assessment Payload ---")
    print(json.dumps(results, indent=2))