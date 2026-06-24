"""Request/response schemas for the HTTP API."""
from pydantic import BaseModel, Field

from job_fit_agent.matcher import FitAssessment


class SearchRequest(BaseModel):
    keywords: str = Field(description="Search terms, e.g. 'data scientist'")
    limit: int = Field(default=5, ge=1, le=20)


class OfferOut(BaseModel):
    id: str
    title: str
    company: str | None = None
    location: str | None = None
    contract_type: str | None = None
    url: str | None = None


class SearchResponse(BaseModel):
    count: int
    offers: list[OfferOut]


class AssessRequest(BaseModel):
    offer_id: str = Field(description="Offer id from a prior search")
    keywords: str = Field(description="Keywords used to find the offer")


class ValidatedAssessResponse(BaseModel):
    assessment: FitAssessment | None
    critic_approved: bool | None
    critic_issues: list[str]
    revisions: int
