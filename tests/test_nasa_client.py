from unittest.mock import Mock, patch

import requests

from app.services.nasa_client import (
    fetch_cmes,
    fetch_solar_flares,
    get_date_range,
)


# Test successful Solar Flare API request
@patch("app.services.nasa_client.requests.get")
def test_fetch_solar_flares_success(mock_get):

    mock_response = Mock()
    mock_response.json.return_value = [
        {"classType": "X1.0"},
        {"classType": "M5.0"},
    ]
    mock_response.raise_for_status.return_value = None

    mock_get.return_value = mock_response

    result = fetch_solar_flares(
        "2026-08-01",
        "2026-08-11",
    )

    assert result == [
        {"classType": "X1.0"},
        {"classType": "M5.0"},
    ]

    mock_get.assert_called_once()


# Test Solar Flare API request failure
@patch("app.services.nasa_client.requests.get")
def test_fetch_solar_flares_request_failure(mock_get):

    mock_get.side_effect = requests.RequestException(
        "NASA API unavailable"
    )

    result = fetch_solar_flares(
        "2026-08-01",
        "2026-08-11",
    )

    assert result == []


# Test successful CME API request
@patch("app.services.nasa_client.requests.get")
def test_fetch_cmes_success(mock_get):

    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "activityID": "2026-08-01-CME-001",
            "cmeAnalyses": [],
        }
    ]
    mock_response.raise_for_status.return_value = None

    mock_get.return_value = mock_response

    result = fetch_cmes(
        "2026-08-01",
        "2026-08-11",
    )

    assert result == [
        {
            "activityID": "2026-08-01-CME-001",
            "cmeAnalyses": [],
        }
    ]

    mock_get.assert_called_once()


# Test CME API request failure
@patch("app.services.nasa_client.requests.get")
def test_fetch_cmes_request_failure(mock_get):

    mock_get.side_effect = requests.RequestException(
        "NASA API unavailable"
    )

    result = fetch_cmes(
        "2026-08-01",
        "2026-08-11",
    )

    assert result == []


# Test date range generation
@patch("app.services.nasa_client.datetime")
def test_get_date_range(mock_datetime):

    mock_end_date = Mock()
    mock_start_date = Mock()

    mock_end_date.strftime.return_value = "2026-08-11"
    mock_start_date.strftime.return_value = "2026-07-12"

    mock_datetime.now.return_value = mock_end_date
    mock_end_date.__sub__ = Mock(return_value=mock_start_date)

    start_date, end_date = get_date_range(days_back=30)

    assert start_date == "2026-07-12"
    assert end_date == "2026-08-11"