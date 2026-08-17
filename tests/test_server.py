from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.server import app


client = TestClient(app)


# Test the health check endpoint
def test_health_check():

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "space-risk-backend",
    }


# Test that the latest assessment is returned successfully
def test_get_latest_assessment_returns_latest_record():

    latest_assessment = {
        "generated_at": "2026-08-12T12:00:00+00:00",
        "threat_level": "HIGH",
        "flare_count": 10,
        "cme_count": 5,
    }

    # Mock the Supabase response and query chain
    mock_response = MagicMock()
    mock_response.data = [latest_assessment]

    mock_query = MagicMock()
    mock_query.select.return_value = mock_query
    mock_query.order.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.execute.return_value = mock_response

    mock_supabase = MagicMock()
    mock_supabase.table.return_value = mock_query

    # Replace the real Supabase client with the mock
    with patch(
        "app.server.get_supabase_client",
        return_value=mock_supabase,
    ):
        response = client.get("/api/v1/latest-assessment")

    assert response.status_code == 200
    assert response.json() == latest_assessment

    mock_supabase.table.assert_called_once_with(
        "space_weather_assessments"
    )


# Test that the latest assessment returns 404 when the database is empty
def test_get_latest_assessment_returns_404_when_empty():

    # Simulate an empty Supabase response
    mock_response = MagicMock()
    mock_response.data = []

    mock_query = MagicMock()
    mock_query.select.return_value = mock_query
    mock_query.order.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.execute.return_value = mock_response

    mock_supabase = MagicMock()
    mock_supabase.table.return_value = mock_query

    # Replace the real Supabase client with the mock
    with patch(
        "app.server.get_supabase_client",
        return_value=mock_supabase,
    ):
        response = client.get("/api/v1/latest-assessment")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "No assessments found in database."
    }


# Test that the trends endpoint returns assessment history
def test_get_assessment_trends_returns_records():

    trends = [
        {
            "generated_at": "2026-08-12T12:00:00+00:00",
            "scores": {"overall_max": 70.0},
            "threat_level": "HIGH",
            "flare_count": 10,
            "cme_count": 5,
        },
        {
            "generated_at": "2026-08-11T12:00:00+00:00",
            "scores": {"overall_max": 30.0},
            "threat_level": "MODERATE",
            "flare_count": 6,
            "cme_count": 3,
        },
    ]

    # Mock the Supabase response and query chain
    mock_response = MagicMock()
    mock_response.data = trends

    mock_query = MagicMock()
    mock_query.select.return_value = mock_query
    mock_query.order.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.execute.return_value = mock_response

    mock_supabase = MagicMock()
    mock_supabase.table.return_value = mock_query

    # Replace the real Supabase client with the mock
    with patch(
        "app.server.get_supabase_client",
        return_value=mock_supabase,
    ):
        response = client.get("/api/v1/trends")

    assert response.status_code == 200
    assert response.json() == {
        "count": 2,
        "data": trends,
    }

    # Verify that the default limit of 7 was passed to Supabase
    mock_query.limit.assert_called_once_with(7)


# Test that the trends endpoint accepts a custom limit
def test_get_assessment_trends_accepts_custom_limit():

    # Simulate a valid empty response from Supabase
    mock_response = MagicMock()
    mock_response.data = []

    mock_query = MagicMock()
    mock_query.select.return_value = mock_query
    mock_query.order.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.execute.return_value = mock_response

    mock_supabase = MagicMock()
    mock_supabase.table.return_value = mock_query

    # Replace the real Supabase client with the mock
    with patch(
        "app.server.get_supabase_client",
        return_value=mock_supabase,
    ):
        response = client.get("/api/v1/trends?limit=10")

    assert response.status_code == 200
    assert response.json() == {
        "count": 0,
        "data": [],
    }

    mock_query.limit.assert_called_once_with(10)


# Test that the trends endpoint rejects limits above 30
def test_get_assessment_trends_rejects_limit_above_30():

    response = client.get("/api/v1/trends?limit=1000")

    assert response.status_code == 422


# Test that the trends endpoint rejects a zero limit
def test_get_assessment_trends_rejects_zero_limit():

    response = client.get("/api/v1/trends?limit=0")

    assert response.status_code == 422


# Test that the trends endpoint rejects a negative limit
def test_get_assessment_trends_rejects_negative_limit():

    response = client.get("/api/v1/trends?limit=-1")

    assert response.status_code == 422