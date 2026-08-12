from app.services.event_transformer import (
    extract_cme_features,
    parse_flare_class,
)


# Test valid solar flare classes
def test_parse_flare_class_x1():

    assert parse_flare_class("X1.0") == 1e-4


def test_parse_flare_class_m5():

    assert parse_flare_class("M5.0") == 5e-5


def test_parse_flare_class_c2():

    assert parse_flare_class("C2.0") == 2e-6


# Test invalid or missing solar flare classes
def test_parse_flare_class_none():

    assert parse_flare_class(None) == 0.0


def test_parse_flare_class_empty_string():

    assert parse_flare_class("") == 0.0


def test_parse_flare_class_invalid_string():

    assert parse_flare_class("invalid") == 0.0


# Test CME feature extraction
def test_extract_cme_features_empty_event():

    result = extract_cme_features({})

    assert result == {
        "speed": 0.0,
        "half_angle": 0.0,
        "is_earth_directed": False,
    }


def test_extract_cme_features_earth_directed():

    cme = {
        "cmeAnalyses": [
            {
                "speed": 1500,
                "halfAngle": 60,
                "isMostAccurate": True,
                "type": "CME",
            }
        ]
    }

    result = extract_cme_features(cme)

    assert result["speed"] == 1500.0
    assert result["half_angle"] == 60.0
    assert result["is_earth_directed"] is True


def test_extract_cme_features_not_earth_directed():

    cme = {
        "cmeAnalyses": [
            {
                "speed": 1000,
                "halfAngle": 30,
                "isMostAccurate": True,
                "type": "CME",
            }
        ]
    }

    result = extract_cme_features(cme)

    assert result["speed"] == 1000.0
    assert result["half_angle"] == 30.0
    assert result["is_earth_directed"] is False


def test_extract_cme_features_full_halo():

    cme = {
        "cmeAnalyses": [
            {
                "speed": 2000,
                "halfAngle": 20,
                "isMostAccurate": True,
                "type": "Full Halo",
            }
        ]
    }

    result = extract_cme_features(cme)

    assert result["is_earth_directed"] is True