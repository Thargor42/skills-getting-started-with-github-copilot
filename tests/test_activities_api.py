import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


ACTIVITY_NAME = "Chess Club"
EXISTING_EMAIL = "existing@mergington.edu"
NEW_EMAIL = "new@mergington.edu"
TEST_ACTIVITIES = {
    ACTIVITY_NAME: {
        "description": "Learn chess",
        "schedule": "Fridays",
        "max_participants": 3,
        "participants": [EXISTING_EMAIL],
    }
}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "activities", copy.deepcopy(TEST_ACTIVITIES))
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_activity = copy.deepcopy(TEST_ACTIVITIES[ACTIVITY_NAME])

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {ACTIVITY_NAME: expected_activity}


def test_signup_adds_participant_to_activity_list(client):
    # Arrange
    params = {"email": NEW_EMAIL}

    # Act
    signup_response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params=params,
    )
    activities_response = client.get("/activities")

    # Assert
    assert signup_response.status_code == 200
    assert signup_response.json()["message"] == (
        f"Signed up {NEW_EMAIL} for {ACTIVITY_NAME}"
    )
    assert activities_response.status_code == 200
    assert NEW_EMAIL in activities_response.json()[ACTIVITY_NAME]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    params = {"email": EXISTING_EMAIL}

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params=params,
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Student is already signed up for this activity"
    )


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    params = {"email": NEW_EMAIL}

    # Act
    response = client.post("/activities/Unknown/signup", params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant_from_activity_list(client):
    # Arrange
    params = {"email": EXISTING_EMAIL}

    # Act
    unregister_response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params=params,
    )
    activities_response = client.get("/activities")

    # Assert
    assert unregister_response.status_code == 200
    assert unregister_response.json()["message"] == (
        f"Unregistered {EXISTING_EMAIL} from {ACTIVITY_NAME}"
    )
    assert activities_response.status_code == 200
    participants = activities_response.json()[ACTIVITY_NAME]["participants"]
    assert EXISTING_EMAIL not in participants


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    params = {"email": EXISTING_EMAIL}

    # Act
    response = client.delete("/activities/Unknown/signup", params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_not_found_for_unregistered_participant(client):
    # Arrange
    params = {"email": NEW_EMAIL}

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params=params,
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Student is not signed up for this activity"
    )
