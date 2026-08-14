from unittest.mock import MagicMock, patch

from app.pipeline.ingestion import (
    get_peak_flare,
    get_primary_cme,
    save_to_supabase,
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


# Test saving assessments to Supabase
def test_save_to_supabase_uses_assessment_date():

    payload = {
        "metadata": {
            "generated_at": "2026-08-12T12:00:00+00:00",
            "assessment_date": "2026-08-12",
            "events_analyzed": {
                "flare_count": 13,
                "cme_count": 115,
            },
        },
        "observed_extremes": {
            "peak_solar_flare_class": "M3.6",
            "peak_xray_flux_wm2": 3.6e-5,
            "primary_cme_features": {
                "speed": 1549.0,
                "half_angle": 45.0,
                "is_earth_directed": True,
            },
        },
        "risk_assessment": {
            "scores": {
                "power_grid": 58.37,
                "overall_max": 67.22,
                "gps_disruption": 67.22,
                "radio_blackout": 51.88,
            },
            "threat_level": "HIGH",
        },
    }

    mock_response = MagicMock()

    mock_query = MagicMock()
    mock_query.upsert.return_value = mock_query
    mock_query.execute.return_value = mock_response

    mock_supabase = MagicMock()
    mock_supabase.table.return_value = mock_query

    with patch(
        "app.pipeline.ingestion.create_client",
        return_value=mock_supabase,
    ):
        save_to_supabase(payload)

    mock_query.upsert.assert_called_once()

    row = mock_query.upsert.call_args.args[0]

    assert row["assessment_date"] == "2026-08-12"
    assert "window_start" not in row
    assert "window_end" not in row


def test_save_to_supabase_upserts_on_assessment_date():

    payload = {
        "metadata": {
            "generated_at": "2026-08-12T12:00:00+00:00",
            "assessment_date": "2026-08-12",
            "events_analyzed": {
                "flare_count": 13,
                "cme_count": 115,
            },
        },
        "observed_extremes": {
            "peak_solar_flare_class": "M3.6",
            "peak_xray_flux_wm2": 3.6e-5,
            "primary_cme_features": {
                "speed": 1549.0,
                "half_angle": 45.0,
                "is_earth_directed": True,
            },
        },
        "risk_assessment": {
            "scores": {
                "power_grid": 58.37,
                "overall_max": 67.22,
                "gps_disruption": 67.22,
                "radio_blackout": 51.88,
            },
            "threat_level": "HIGH",
        },
    }

    mock_response = MagicMock()

    mock_query = MagicMock()
    mock_query.upsert.return_value = mock_query
    mock_query.execute.return_value = mock_response

    mock_supabase = MagicMock()
    mock_supabase.table.return_value = mock_query

    with patch(
        "app.pipeline.ingestion.create_client",
        return_value=mock_supabase,
    ):
        save_to_supabase(payload)

    mock_query.upsert.assert_called_once()

    call_kwargs = mock_query.upsert.call_args.kwargs

    assert call_kwargs["on_conflict"] == "assessment_date"