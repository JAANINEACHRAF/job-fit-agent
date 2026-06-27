"""FastAPI application exposing the job-fit agent over HTTP."""
from fastapi import Depends, FastAPI, HTTPException

from job_fit_agent.agent.graph import run_agent
from job_fit_agent.api.schemas import (
    AssessRequest,
    OfferOut,
    SearchRequest,
    SearchResponse,
    ValidatedAssessResponse,
)
from job_fit_agent.france_travail import FranceTravailSource
from job_fit_agent.matcher import FitAssessment, assess_fit
from job_fit_agent.models import JobOffer
from job_fit_agent.profile import load_profile
from job_fit_agent.sources import JobSource

app = FastAPI(
    title="Job-Fit Agent",
    description="Search French job offers and assess candidate fit with an AI agent.",
    version="0.1.0",
)


_job_source: JobSource = FranceTravailSource()


def get_job_source() -> JobSource:
    """Provide the job source; override via app.dependency_overrides in tests."""
    return _job_source


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check for deployment platforms."""
    return {"status": "ok"}


@app.post("/search", response_model=SearchResponse)
def search(
    req: SearchRequest, source: JobSource = Depends(get_job_source)
) -> SearchResponse:
    """Search job offers from France Travail."""
    offers = source.search(req.keywords, limit=req.limit)
    return SearchResponse(
        count=len(offers),
        offers=[OfferOut(**o.model_dump(exclude={"description"})) for o in offers],
    )


def _find_offer(offer_id: str, keywords: str, source: JobSource) -> JobOffer:
    """Re-fetch an offer by id; raise 404 if not found."""
    offers = source.search(keywords, limit=20)
    offer = next((o for o in offers if o.id == offer_id), None)
    if offer is None:
        raise HTTPException(
            status_code=404,
            detail=f"Offer {offer_id} not found for keywords '{keywords}'.",
        )
    return offer


@app.post("/assess", response_model=FitAssessment)
def assess(
    req: AssessRequest, source: JobSource = Depends(get_job_source)
) -> FitAssessment:
    """Assess fit for one offer (single LLM pass)."""
    offer = _find_offer(req.offer_id, req.keywords, source)
    return assess_fit(offer, load_profile())


@app.post("/assess/validated", response_model=ValidatedAssessResponse)
def assess_validated(
    req: AssessRequest, source: JobSource = Depends(get_job_source)
) -> ValidatedAssessResponse:
    """Assess fit using the self-critique agent (assess + critic + revise)."""
    offer = _find_offer(req.offer_id, req.keywords, source)
    state = run_agent(offer, load_profile())
    critique = state["critique"]
    return ValidatedAssessResponse(
        assessment=state["assessment"],
        critic_approved=critique.approved if critique else None,
        critic_issues=critique.issues if critique else [],
        revisions=state["revisions"],
    )
