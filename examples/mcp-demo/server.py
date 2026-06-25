"""MCP server exposing job-fit tools to any MCP-compatible client."""
from mcp.server.fastmcp import FastMCP

from job_fit_agent.agent.graph import run_agent
from job_fit_agent.france_travail import search_jobs
from job_fit_agent.matcher import FitAssessment, assess_fit
from job_fit_agent.profile import load_profile

mcp = FastMCP("job-fit-agent")


@mcp.tool()
def search_job_offers(keywords: str, limit: int = 5) -> list[dict]:
    """Search French job offers from France Travail by keywords.

    Args:
        keywords: search terms, e.g. "data scientist" or "ingénieur IA".
        limit: maximum number of offers to return (default 5).

    Returns a list of offers with id, title, company, location, contract_type.
    """
    offers = search_jobs(keywords, limit=limit)
    return [o.model_dump(exclude={"description"}) for o in offers]


@mcp.tool()
def assess_offer_fit(offer_id: str, keywords: str) -> dict:
    """Assess how well the candidate fits a specific job offer (single pass).

    Args:
        offer_id: the offer id returned by search_job_offers.
        keywords: the search terms used to find the offer (to re-fetch it).

    Returns a fit assessment with score, matched_skills, gaps, reasoning.
    """
    profile = load_profile()
    offers = search_jobs(keywords, limit=20)
    offer = next((o for o in offers if o.id == offer_id), None)
    if offer is None:
        return {"error": f"Offer {offer_id} not found for keywords '{keywords}'."}
    result: FitAssessment = assess_fit(offer, profile)
    return result.model_dump()


@mcp.tool()
def assess_offer_fit_validated(offer_id: str, keywords: str) -> dict:
    """Assess fit using the self-critique agent (assess + critic + revise).

    Slower but more reliable than assess_offer_fit: a critic validates the
    assessment and forces revisions if it finds hallucinated skills or gaps.

    Args:
        offer_id: the offer id returned by search_job_offers.
        keywords: the search terms used to find the offer.

    Returns the validated assessment plus the critic's verdict.
    """
    profile = load_profile()
    offers = search_jobs(keywords, limit=20)
    offer = next((o for o in offers if o.id == offer_id), None)
    if offer is None:
        return {"error": f"Offer {offer_id} not found for keywords '{keywords}'."}
    state = run_agent(offer, profile)
    assessment = state["assessment"]
    critique = state["critique"]
    return {
        "assessment": assessment.model_dump() if assessment else None,
        "critic_approved": critique.approved if critique else None,
        "critic_issues": critique.issues if critique else [],
        "revisions": state["revisions"],
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
