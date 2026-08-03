import math

def calculate_radio_risk(peak_flux): 
    if peak_flux <= 0: 
        return 0.0

    min_log = -6.0 # C-class baseline
    max_log = -3.0 # X10 extreme flare ceiling

    current_log = math.log10(peak_flux)

    # Min-max normalization mapped to 0-100
    normalized = (current_log - min_log) / (max_log - min_log)
    risk = normalized * 100.0

    # Clamp bounds strictly between 0 and 100
    return round(max(0.0, min(100.0, risk)), 2)

def calculate_gps_risk(peak_flux, cme_features): 
    # Flare component contributes up to 40 points
    flare_component = calculate_radio_risk(peak_flux) * 0.4

    speed = cme_features.get("speed", 0.0)
    is_earth = cme_features.get("is_earth_directed", False)

    # CME component contributes up to 60 points
    cme_component = 0.0
    if is_earth:
        cme_component = min(60.0, (speed / 2000.0) * 60.0)

    total_risk = flare_component + cme_component
    return round(max(0.0, min(100.0, total_risk)), 2)

def calculate_power_grid_risk(cme_features): 
    if not cme_features.get("is_earth_directed", False):
        return 0.0

    speed = cme_features.get("speed", 0.0)
    half_angle = cme_features.get("half_angle", 0.0)

    speed_factor = min(70.0, (speed / 2500.0) * 70.0)
    angle_factor = min(30.0, (half_angle / 90.0) * 30.0)

    total_risk = speed_factor + angle_factor
    return round(max(0.0, min(100.0, total_risk)), 2)

def generate_space_weather_assessment(peak_flux, cme_features): 
    radio_score = calculate_radio_risk(peak_flux)
    gps_score = calculate_gps_risk(peak_flux, cme_features)
    grid_score = calculate_power_grid_risk(cme_features)

    overall_score = max(radio_score, gps_score, grid_score)

    return {
            "scores": {
                "radio_blackout": radio_score,
                "gps_disruption": gps_score,
                "power_grid": grid_score,
                "overall_max": overall_score
            },
            "threat_level": "CRITICAL" if overall_score >= 75 else
                            "HIGH" if overall_score >= 50 else
                            "MODERATE" if overall_score >= 25 else "LOW"
        }

if __name__ == "__main__":
    from transformer import parse_flare_class, extract_cme_features

    # Synthetic test: X1.5 flare + 1200 km/s Earth-directed CME
    test_flux = parse_flare_class("X1.5")
    test_cme = {
        "cmeAnalyses": [{
            "speed": 1200,
            "halfAngle": 50,
            "isMostAccurate": True,
            "type": "Full Halo"
        }]
    }
    extracted_cme = extract_cme_features(test_cme)

    assessment = generate_space_weather_assessment(test_flux, extracted_cme)
    
    print("--- Risk Assessment Test Output ---")
    print("Input Flare: X1.5 | Input CME Speed: 1200 km/s (Earth-directed)")
    print("Scores:", assessment["scores"])
    print("Threat Level:", assessment["threat_level"])