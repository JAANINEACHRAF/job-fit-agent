"""Domain models for job offers."""
from typing import Any

from pydantic import BaseModel, Field


class JobOffer(BaseModel):
    """A normalized job offer parsed from the France Travail API."""

    id: str
    title: str = Field(alias="intitule")
    description: str | None = None
    company: str | None = None
    location: str | None = None
    contract_type: str | None = None
    url: str | None = None

    model_config = {"populate_by_name": True}

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> "JobOffer":
        """Build a JobOffer from a raw France Travail offer dict.

        Nested objects (entreprise, lieuTravail, origineOffre) can be missing
        OR explicitly null in the API response, so we coerce both to {} before
        reading sub-fields.
        """
        entreprise = raw.get("entreprise") or {}
        lieu = raw.get("lieuTravail") or {}
        origine = raw.get("origineOffre") or {}
        return cls(
            id=raw["id"],
            intitule=raw.get("intitule", ""),
            description=raw.get("description"),
            company=entreprise.get("nom"),
            location=lieu.get("libelle"),
            contract_type=raw.get("typeContratLibelle"),
            url=origine.get("urlOrigine"),
        )
