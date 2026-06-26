"""Job source abstraction: the single contract every offer provider must satisfy."""
from typing import Protocol

from job_fit_agent.models import JobOffer


class JobSource(Protocol):
    """A source of job offers (France Travail today, others such as Apify later).

    The core depends on this contract, never on a concrete provider, so a new
    source can be plugged in without touching the assessment logic. On failure,
    implementations raise a job-source-level error (defined alongside the first
    implementation) so callers can handle any provider uniformly.
    """

    def search(self, keywords: str, limit: int = 5) -> list[JobOffer]:
        """Return up to ``limit`` offers matching ``keywords``."""
        ...
