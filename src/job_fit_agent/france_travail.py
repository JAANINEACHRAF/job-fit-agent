"""Minimal France Travail API client: OAuth token + job search."""
import httpx

from job_fit_agent.config import settings


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


def search_jobs(keywords: str, token: str, limit: int = 5) -> list[dict]:
    """Search job offers by keywords. Returns a list of offer dicts."""
    resp = httpx.get(
        f"{settings.ft_api_base}/offresdemploi/v2/offres/search",
        params={"motsCles": keywords, "range": f"0-{limit - 1}"},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    resp.raise_for_status()
    return resp.json().get("resultats", [])


if __name__ == "__main__":
    tok = get_access_token()
    print("Token OK")
    offers = search_jobs("data scientist", tok, limit=3)
    for o in offers:
        print(f"- {o.get('intitule')} | {o.get('lieuTravail', {}).get('libelle')}")
