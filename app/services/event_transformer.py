import re


# Convert a flare class (e.g. X1.2) into peak X-ray flux (W/m²)
def parse_flare_class(class_type: str | None) -> float:

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
        "A": 1e-8,
        "B": 1e-7,
        "C": 1e-6,
        "M": 1e-5,
        "X": 1e-4,
    }

    return number * multipliers.get(letter, 0.0)


# Extract the CME properties used by the risk engine
def extract_cme_features(cme_event: dict) -> dict:

    analyses = cme_event.get("cmeAnalyses", [])

    if not analyses:
        return {
            "speed": 0.0,
            "half_angle": 0.0,
            "is_earth_directed": False,
        }

    # Prefer the analysis marked as most accurate.
    primary = next(
        (
            analysis
            for analysis in analyses
            if analysis.get("isMostAccurate", False)
        ),
        analyses[0],
    )

    speed = float(primary.get("speed") or 0.0)
    half_angle = float(primary.get("halfAngle") or 0.0)

    latitude = primary.get("latitude")
    longitude = primary.get("longitude")

    # Full Halo CMEs are treated as potentially Earth-directed.
    is_full_halo = primary.get("type") == "Full Halo"

    # If latitude/longitude are available, estimate the angular
    # separation between the CME propagation direction and the
    # Sun-Earth line.
    is_within_cone = False

    if latitude is not None and longitude is not None:

        try:
            latitude = float(latitude)
            longitude = float(longitude)

            angular_distance = (
                latitude ** 2
                + longitude ** 2
            ) ** 0.5

            is_within_cone = (
                angular_distance <= half_angle
            )

        except (TypeError, ValueError):
            is_within_cone = False

    is_earth_directed = (
        is_full_halo
        or is_within_cone
    )

    return {
        "speed": speed,
        "half_angle": half_angle,
        "is_earth_directed": is_earth_directed,
    }