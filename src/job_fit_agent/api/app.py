"""FastAPI application exposing the job-fit agent over HTTP."""
from fastapi import FastAPI, HTTPException

from job_fit_agent.agent.graph import run_agent
from job_fit_agent.api.schemas import (
    AssessRequest,
    OfferOut,
    SearchRequest,
    SearchResponse,
    ValidatedAssessResponse,
)
from job_fit_agent.france_travail import search_jobs
from job_fit_agent.matcher import FitAssessment, assess_fit
from job_fit_agent.models import JobOffer
from job_fit_agent.profile import load_profile

app = FastAPI(
    title="Job-Fit Agent",
    description="Search French job offers and assess candidate fit with an AI agent.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check for deployment platforms."""
    return {"status": "ok"}


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest) -> SearchResponse:
    """Search job offers from France Travail."""
    offers = search_jobs(req.keywords, limit=req.limit)
    return SearchResponse(
        count=len(offers),
        offers=[OfferOut(**o.model_dump(exclude={"description"})) for o in offers],
    )


def _find_offer(offer_id: str, keywords: str) -> JobOffer:
    """Re-fetch an offer by id; raise 404 if not found."""
    offers = search_jobs(keywords, limit=20)
    offer = next((o for o in offers if o.id == offer_id), None)
    if offer is None:
        raise HTTPException(
            status_code=404,
            detail=f"Offer {offer_id} not found for keywords '{keywords}'.",
        )
    return offer


@app.post("/assess", response_model=FitAssessment)
def assess(req: AssessRequest) -> FitAssessment:
    """Assess fit for one offer (single LLM pass)."""
    offer = _find_offer(req.offer_id, req.keywords)
    return assess_fit(offer, load_profile())


@app.post("/assess/validated", response_model=ValidatedAssessResponse)
def assess_validated(req: AssessRequest) -> ValidatedAssessResponse:
    """Assess fit using the self-critique agent (assess + critic + revise)."""
    offer = _find_offer(req.offer_id, req.keywords)
    state = run_agent(offer, load_profile())
    critique = state["critique"]
    return ValidatedAssessResponse(
        assessment=state["assessment"],
        critic_approved=critique.approved if critique else None,
        critic_issues=critique.issues if critique else [],
        revisions=state["revisions"],
    )
