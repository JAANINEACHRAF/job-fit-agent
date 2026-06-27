"""API endpoint tests backed by a fake JobSource (no network)."""
from fastapi.testclient import TestClient

from job_fit_agent.api.app import app, get_job_source
from job_fit_agent.models import JobOffer
from job_fit_agent.sources import JobSource


class FakeJobSource:
    """In-memory JobSource for tests: returns canned offers, no network."""

    def __init__(self, offers: list[JobOffer]) -> None:
        self._offers = offers

    def search(self, keywords: str, limit: int = 5) -> list[JobOffer]:
        return self._offers[:limit]


def test_search_returns_offers_from_injected_source() -> None:
    fake: JobSource = FakeJobSource(
        [JobOffer(id="A1", title="Data Scientist", company="ACME", location="Paris")]
    )
    app.dependency_overrides[get_job_source] = lambda: fake
    try:
        resp = TestClient(app).post("/search", json={"keywords": "data", "limit": 5})
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    assert body["offers"][0]["id"] == "A1"
    assert body["offers"][0]["title"] == "Data Scientist"
