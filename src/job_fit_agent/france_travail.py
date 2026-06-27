"""France Travail API client: cached OAuth token + resilient job search."""
import time

import httpx

from job_fit_agent.config import settings
from job_fit_agent.models import JobOffer
from job_fit_agent.sources import JobSourceAuthError, JobSourceUnavailable

_token_cache: tuple[str, float] | None = None
# Refresh when less than this fraction of the token's lifetime remains.
_REFRESH_THRESHOLD = 0.1


def _fetch_token() -> tuple[str, float]:
    """Request a fresh token. Returns (token, absolute_expiry_ts)."""
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
    payload = resp.json()
    lifetime = payload.get("expires_in", 1499)
    # Refresh after (1 - threshold) of the lifetime has elapsed.
    expiry = time.time() + lifetime * (1 - _REFRESH_THRESHOLD)
    return payload["access_token"], expiry


def get_access_token(force_refresh: bool = False) -> str:
    """Return a cached token, refreshing if expired or forced."""
    global _token_cache
    if not force_refresh and _token_cache is not None:
        token, expiry = _token_cache
        if time.time() < expiry:
            return token
    _token_cache = _fetch_token()
    return _token_cache[0]


class FranceTravailSource:
    """France Travail implementation of the ``JobSource`` protocol.

    Wraps the cached-token client above and translates library-specific failures
    (httpx errors, auth rejections) into job-source domain errors, so the core
    handles any source uniformly without knowing httpx exists.
    """

    def search(self, keywords: str, limit: int = 5) -> list[JobOffer]:
        """Search offers. Refreshes the token on a 401 and retries once."""
        try:
            resp = self._search_request(keywords, limit)
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status in (401, 403):
                raise JobSourceAuthError(
                    f"France Travail rejected credentials (HTTP {status})"
                ) from e
            raise JobSourceUnavailable(f"France Travail returned HTTP {status}") from e
        except httpx.RequestError as e:  # network error or timeout
            raise JobSourceUnavailable("France Travail is unreachable") from e

        if resp.status_code == 204:
            return []
        return [JobOffer.from_api(o) for o in resp.json().get("resultats", [])]

    def _search_request(self, keywords: str, limit: int) -> httpx.Response:
        def _request(token: str) -> httpx.Response:
            return httpx.get(
                f"{settings.ft_api_base}/offresdemploi/v2/offres/search",
                params={"motsCles": keywords, "range": f"0-{limit - 1}"},
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0,
            )

        resp = _request(get_access_token())
        if resp.status_code == 401:  # token rejected: force-refresh and retry once
            resp = _request(get_access_token(force_refresh=True))
        resp.raise_for_status()
        return resp


if __name__ == "__main__":
    print("Token OK")
    for job in FranceTravailSource().search("data scientist", limit=3):
        print(f"- {job.title} | {job.location} | {job.contract_type}")
