from app.pipeline.ingestion import (
    get_peak_flare,
    get_primary_cme,
)


# Test peak flare selection

def test_get_peak_flare_empty_list():

    result = get_peak_flare([])

    assert result == (0.0, None)


def test_get_peak_flare_selects_strongest():

    flares = [
        {"classType": "C2.0"},
        {"classType": "M5.0"},
        {"classType": "X1.0"},
    ]

    result = get_peak_flare(flares)

    assert result == (1e-4, "X1.0")


def test_get_peak_flare_ignores_weaker_flares():

    flares = [
        {"classType": "X1.0"},
        {"classType": "M9.0"},
        {"classType": "C5.0"},
    ]

    result = get_peak_flare(flares)

    assert result == (1e-4, "X1.0")


# Test primary CME selection

def test_get_primary_cme_empty_list():

    result = get_primary_cme([])

    assert result == {
        "speed": 0.0,
        "half_angle": 0.0,
        "is_earth_directed": False,
    }


def test_get_primary_cme_prefers_earth_directed():

    cmes = [
        {
            "cmeAnalyses": [
                {
                    "speed": 2000,
                    "halfAngle": 30,
                    "isMostAccurate": True,
                    "type": "CME",
                }
            ]
        },
        {
            "cmeAnalyses": [
                {
                    "speed": 1000,
                    "halfAngle": 60,
                    "isMostAccurate": True,
                    "type": "CME",
                }
            ]
        },
    ]

    result = get_primary_cme(cmes)

    assert result["speed"] == 1000.0
    assert result["half_angle"] == 60.0
    assert result["is_earth_directed"] is True


def test_get_primary_cme_selects_fastest_same_priority():

    cmes = [
        {
            "cmeAnalyses": [
                {
                    "speed": 1000,
                    "halfAngle": 30,
                    "isMostAccurate": True,
                    "type": "CME",
                }
            ]
        },
        {
            "cmeAnalyses": [
                {
                    "speed": 1800,
                    "halfAngle": 30,
                    "isMostAccurate": True,
                    "type": "CME",
                }
            ]
        },
    ]

    result = get_primary_cme(cmes)

    assert result["speed"] == 1800.0