import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Number of predefined activities
    # Check that each activity has the expected structure
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_success(client):
    response = client.post("/activities/Chess Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@example.com" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert "test@example.com" in activities["Chess Club"]["participants"]


def test_signup_duplicate(client):
    # First signup
    client.post("/activities/Chess Club/signup?email=test@example.com")
    # Second signup with same email
    response = client.post("/activities/Chess Club/signup?email=test@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_nonexistent_activity(client):
    response = client.post("/activities/Nonexistent Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_delete_participant_success(client):
    # First signup
    client.post("/activities/Chess Club/signup?email=test@example.com")
    # Then delete
    response = client.delete("/activities/Chess Club/participants/test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "unregistered" in data["message"].lower()

    # Verify the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert "test@example.com" not in activities["Chess Club"]["participants"]


def test_delete_nonexistent_participant(client):
    response = client.delete("/activities/Chess Club/participants/nonexistent@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_delete_nonexistent_activity(client):
    response = client.delete("/activities/Nonexistent Activity/participants/test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()