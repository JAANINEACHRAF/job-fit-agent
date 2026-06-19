"""Domain models for job offers."""
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
    def from_api(cls, raw: dict) -> "JobOffer":
        """Build a JobOffer from a raw France Travail offer dict."""
        return cls(
            id=raw["id"],
            intitule=raw.get("intitule", ""),
            description=raw.get("description"),
            company=raw.get("entreprise", {}).get("nom"),
            location=raw.get("lieuTravail", {}).get("libelle"),
            contract_type=raw.get("typeContratLibelle"),
            url=raw.get("origineOffre", {}).get("urlOrigine"),
        )
