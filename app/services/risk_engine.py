import math


# DISCLAIMER: These functions use simplified heuristic scoring models (0-100 scale)
# for demonstration and benchmarking. They approximate complex space physics and
# DO NOT replace official space weather forecasts from NOAA SWPC or NASA CCMC.


# Calculate radio blackout risk from peak X-ray flux
def calculate_radio_risk(peak_flux: float) -> float:

    if peak_flux <= 0:
        return 0.0

    # C1 flare = 0 risk baseline
    min_log = -6.0

    # X10 flare = 100 risk ceiling
    max_log = -3.0

    current_log = math.log10(peak_flux)

    normalized = (
        (current_log - min_log)
        / (max_log - min_log)
    )

    risk = normalized * 100.0

    return round(
        max(0.0, min(100.0, risk)),
        2,
    )


# Calculate GPS disruption risk
def calculate_gps_risk(
    peak_flux: float,
    cme_features: dict,
) -> float:

    # Solar flare contribution
    flare_component = (
        calculate_radio_risk(peak_flux) * 0.4
    )

    # CME contribution only applies when the CME is
    # considered Earth-directed.
    cme_component = 0.0

    if cme_features.get("is_earth_directed", False):

        speed = cme_features.get("speed", 0.0)

        cme_component = min(
            60.0,
            (speed / 2000.0) * 60.0,
        )

    return round(
        max(
            0.0,
            min(
                100.0,
                flare_component + cme_component,
            ),
        ),
        2,
    )


# Calculate geomagnetic power grid risk
def calculate_power_grid_risk(
    cme_features: dict,
) -> float:

    # Non-Earth-directed CMEs do not contribute
    # to the geomagnetic grid risk score.
    if not cme_features.get("is_earth_directed", False):
        return 0.0

    speed = cme_features.get("speed", 0.0)
    half_angle = cme_features.get("half_angle", 0.0)

    speed_factor = min(
        70.0,
        (speed / 2500.0) * 70.0,
    )

    angle_factor = min(
        30.0,
        (half_angle / 90.0) * 30.0,
    )

    return round(
        max(
            0.0,
            min(
                100.0,
                speed_factor + angle_factor,
            ),
        ),
        2,
    )


# Generate the final assessment
def generate_space_weather_assessment(
    peak_flux: float,
    cme_features: dict,
) -> dict:

    radio_score = calculate_radio_risk(
        peak_flux
    )

    gps_score = calculate_gps_risk(
        peak_flux,
        cme_features,
    )

    grid_score = calculate_power_grid_risk(
        cme_features,
    )

    overall_score = max(
        radio_score,
        gps_score,
        grid_score,
    )

    return {
        "scores": {
            "radio_blackout": radio_score,
            "gps_disruption": gps_score,
            "power_grid": grid_score,
            "overall_max": overall_score,
        },
        "threat_level": (
            "CRITICAL"
            if overall_score >= 75
            else "HIGH"
            if overall_score >= 50
            else "MODERATE"
            if overall_score >= 25
            else "LOW"
        ),
    }