from fastapi.testclient import TestClient

import app as app_module
from src.config.session import MissingCredentialsError


client = TestClient(app_module.app)


def test_gemini_quota_error_returns_429(monkeypatch):
    def fake_run_travel_agent(**kwargs):
        raise RuntimeError("429 RESOURCE_EXHAUSTED: quota exceeded")

    monkeypatch.setattr(
        app_module, "run_travel_agent", fake_run_travel_agent
    )

    response = client.post(
        "/api/travel",
        json={"message": "Plan a trip to Jaipur"},
    )

    assert response.status_code == 429
    assert response.json()["success"] is False
    assert response.json()["kind"] == "quota"
    assert "try again later" in response.json()["error"].lower()


def test_unrelated_error_returns_500(monkeypatch):
    def fake_run_travel_agent(**kwargs):
        raise RuntimeError("Unexpected internal failure")

    monkeypatch.setattr(
        app_module, "run_travel_agent", fake_run_travel_agent
    )

    response = client.post(
        "/api/travel",
        json={"message": "Plan a trip to Jaipur"},
    )

    assert response.status_code == 500
    assert response.json()["success"] is False
    assert "unexpected error" in response.json()["error"].lower()
    assert "internal failure" not in response.json()["error"].lower()


def test_missing_credentials_returns_428(monkeypatch):
    def fake_run_travel_agent(**kwargs):
        raise MissingCredentialsError(["GEMINI_API_KEY"])

    monkeypatch.setattr(
        app_module, "run_travel_agent", fake_run_travel_agent
    )

    response = client.post(
        "/api/travel",
        json={"message": "Plan a trip to Jaipur"},
    )

    assert response.status_code == 428
    assert response.json()["success"] is False
    assert "GEMINI_API_KEY" in response.json()["missing"]
