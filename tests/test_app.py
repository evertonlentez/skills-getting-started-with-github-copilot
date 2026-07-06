from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original = deepcopy(app_module.activities)
    app_module.activities.clear()
    app_module.activities.update(deepcopy(original))
    yield
    app_module.activities.clear()
    app_module.activities.update(deepcopy(original))


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_get_activities_returns_the_activity_catalog(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["max_participants"] == 12
    assert "michael@mergington.edu" in payload["Chess Club"]["participants"]


def test_signup_for_activity_adds_a_participant(client):
    email = "newstudent@mergington.edu"
    response = client.post(
        f"/activities/{quote('Chess Club')}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_for_activity_rejects_duplicate_participant(client):
    response = client.post(
        f"/activities/{quote('Chess Club')}/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_successfully(client):
    email = "michael@mergington.edu"
    response = client.delete(
        f"/activities/{quote('Chess Club')}/participants/{quote(email)}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_remove_participant_returns_404_for_missing_participant(client):
    response = client.delete(
        f"/activities/{quote('Chess Club')}/participants/{quote('missing@mergington.edu')}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
