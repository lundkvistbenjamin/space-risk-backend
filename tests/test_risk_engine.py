from app.services.risk_engine import (
    calculate_gps_risk,
    calculate_power_grid_risk,
    calculate_radio_risk,
    generate_space_weather_assessment,
)


# Test radio blackout risk
def test_calculate_radio_risk_zero_flux():

    assert calculate_radio_risk(0.0) == 0.0


def test_calculate_radio_risk_c_class_baseline():

    assert calculate_radio_risk(1e-6) == 0.0


def test_calculate_radio_risk_x10():

    assert calculate_radio_risk(1e-3) == 100.0


def test_calculate_radio_risk_midpoint():

    assert calculate_radio_risk(1e-4) == 66.67


def test_calculate_radio_risk_capped_at_100():

    assert calculate_radio_risk(1e-2) == 100.0


# Test GPS disruption risk
def test_calculate_gps_risk_without_earth_directed_cme():

    cme_features = {
        "speed": 2000.0,
        "half_angle": 90.0,
        "is_earth_directed": False,
    }

    result = calculate_gps_risk(
        1e-4,
        cme_features,
    )

    assert result == 26.67


def test_calculate_gps_risk_with_earth_directed_cme():

    cme_features = {
        "speed": 2000.0,
        "half_angle": 90.0,
        "is_earth_directed": True,
    }

    result = calculate_gps_risk(
        1e-4,
        cme_features,
    )

    assert result == 86.67


def test_calculate_gps_risk_capped_at_100():

    cme_features = {
        "speed": 5000.0,
        "half_angle": 90.0,
        "is_earth_directed": True,
    }

    result = calculate_gps_risk(
        1e-3,
        cme_features,
    )

    assert result == 100.0


# Test power grid risk
def test_calculate_power_grid_risk_without_earth_directed_cme():

    cme_features = {
        "speed": 2500.0,
        "half_angle": 90.0,
        "is_earth_directed": False,
    }

    assert calculate_power_grid_risk(cme_features) == 0.0


def test_calculate_power_grid_risk_maximum():

    cme_features = {
        "speed": 2500.0,
        "half_angle": 90.0,
        "is_earth_directed": True,
    }

    assert calculate_power_grid_risk(cme_features) == 100.0


def test_calculate_power_grid_risk_partial():

    cme_features = {
        "speed": 1250.0,
        "half_angle": 45.0,
        "is_earth_directed": True,
    }

    assert calculate_power_grid_risk(cme_features) == 50.0


# Test final assessment
def test_generate_space_weather_assessment_low_risk():

    cme_features = {
        "speed": 0.0,
        "half_angle": 0.0,
        "is_earth_directed": False,
    }

    result = generate_space_weather_assessment(
        1e-6,
        cme_features,
    )

    assert result["scores"]["overall_max"] == 0.0
    assert result["threat_level"] == "LOW"


def test_generate_space_weather_assessment_critical():

    cme_features = {
        "speed": 2500.0,
        "half_angle": 90.0,
        "is_earth_directed": True,
    }

    result = generate_space_weather_assessment(
        1e-3,
        cme_features,
    )

    assert result["scores"]["overall_max"] == 100.0
    assert result["threat_level"] == "CRITICAL"