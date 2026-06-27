"""Job source abstraction: the single contract every offer provider must satisfy."""
from typing import Protocol

from job_fit_agent.models import JobOffer


class JobSource(Protocol):
    """A source of job offers (France Travail today, others such as Apify later).

    The core depends on this contract, never on a concrete provider, so a new
    source can be plugged in without touching the assessment logic. On failure,
    implementations raise ``JobSourceError`` (or a subclass) so callers can
    handle any provider uniformly.
    """

    def search(self, keywords: str, limit: int = 5) -> list[JobOffer]:
        """Return up to ``limit`` offers matching ``keywords``."""
        ...


class JobSourceError(Exception):
    """Base error for any job source failure, independent of the provider."""


class JobSourceUnavailable(JobSourceError):
    """The source could not be reached or returned an unexpected error."""


class JobSourceAuthError(JobSourceError):
    """The source rejected our credentials."""
