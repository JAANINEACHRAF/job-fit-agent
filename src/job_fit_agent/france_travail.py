"""Minimal France Travail API client: OAuth token + job search."""
import httpx

from job_fit_agent.config import settings
from job_fit_agent.models import JobOffer


def get_access_token() -> str:
    """Fetch an OAuth2 access token via client credentials flow."""
    resp = httpx.post(
        settings.ft_token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": settings.ft_client_id,
            "client_secret": settings.ft_client_secret,
            "scope": settings.ft_scope,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10.0,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def search_jobs(keywords: str, token: str, limit: int = 5) -> list[JobOffer]:
    """Search job offers by keywords. Returns a list of JobOffer."""
    resp = httpx.get(
        f"{settings.ft_api_base}/offresdemploi/v2/offres/search",
        params={"motsCles": keywords, "range": f"0-{limit - 1}"},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    resp.raise_for_status()
    if resp.status_code == 204:  # No Content = zero results
        return []
    raw_offers = resp.json().get("resultats", [])
    return [JobOffer.from_api(o) for o in raw_offers]


if __name__ == "__main__":
    tok = get_access_token()
    print("Token OK")
    for job in search_jobs("data scientist", tok, limit=3):
        print(f"- {job.title} | {job.location} | {job.contract_type}")
