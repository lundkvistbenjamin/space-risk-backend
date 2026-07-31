import re

def parse_flare_class(class_type): 

    if not class_type or not isinstance(class_type, str): 
        return 0.0

    # Match leading letter (A, B, C, M, X) and floating number following it
    match = re.match(r"([A-Z])([\d.]+)", class_type.strip())
    if not match:
        return 0.0

    letter, number_str = match.groups()
    try:
        number = float(number_str)
    except ValueError:
        return 0.0

    # Multipliers matching solar X-ray flux orders of magnitude
    multipliers = {
        'A': 1e-8,
        'B': 1e-7,
        'C': 1e-6,
        'M': 1e-5,
        'X': 1e-4
    }

    return number * multipliers.get(letter, 0.0)

def extract_cme_features(cme_event): 

    analyses = cme_event.get("cmeAnalyses", [])
    if not analyses:
        return {"speed": 0.0, "half_angle": 0.0, "is_earth_directed": False}

    # Grab the primary (usually first/most accurate) analysis entry
    primary = analyses[0]

    speed = float(primary.get("speed") or 0.0)
    half_angle = float(primary.get("halfAngle") or 0.0)

    # Half-angle > 45 deg or halo classification ofthen indicates Earth path direction
    is_earth_directed = primary.get("isMostAccurate", False) and (half_angle >= 45.0 or primary.get("type") == "Full Halo")

    return {
        "speed": speed, 
        "half_angle": half_angle, 
        "is_earth_directed": is_earth_directed
    }

# Block to test the above code
if __name__ == "__main__":
    from nasa_client import fetch_solar_flares, fetch_cmes, get_date_range

    # 1. Fetch raw data using your existing client
    start_date, end_date = get_date_range(days_back=30)
    raw_flares = fetch_solar_flares(start_date, end_date)
    raw_cmes = fetch_cmes(start_date, end_date)

    # 2. Test Flare Class Parsing
    if raw_flares:
        sample_flare = raw_flares[0]
        raw_class = sample_flare.get("classType")
        parsed_flux = parse_flare_class(raw_class)

        print("--- Flare Transformation Test ---")
        print(f"Raw Class: {raw_class}")
        print(f"Parsed Peak X-Ray Flux: {parsed_flux} W/m^2\n")

    # 3. Test CME Feature Extraction
    if raw_cmes:
        sample_cme = raw_cmes[0]
        cme_features = extract_cme_features(sample_cme)

        print("--- CME Transformation Test ---")
        print(f"CME Activity ID: {sample_cme.get('activityID')}")
        print(f"Extracted Features: {cme_features}")