"""LLM-based fit matcher: scores one job offer against the candidate profile."""
from pydantic import BaseModel, Field, field_validator

from job_fit_agent.llm import structured_completion
from job_fit_agent.models import JobOffer
from job_fit_agent.profile import CandidateProfile


class FitAssessment(BaseModel):
    """Structured fit assessment returned by the LLM."""

    score: int = Field(description="Overall fit score from 0 to 100")
    matched_skills: list[str] = Field(description="Profile skills the job requires")
    gaps: list[str] = Field(description="Job requirements the profile lacks")
    reasoning: str = Field(description="Concise justification for the score")

    @field_validator("score")
    @classmethod
    def _clamp_score(cls, v: int) -> int:
        """Keep the score within 0-100 even if the model drifts out of range."""
        return max(0, min(100, v))


_SYSTEM = (
    "You are a precise technical recruiter. Assess how well a candidate fits a job "
    "offer. Base every judgment only on the provided profile and offer. Be honest "
    "about gaps. The score must be between 0 and 100."
)


def assess_fit(offer: JobOffer, profile: CandidateProfile) -> FitAssessment:
    """Ask the LLM to score the offer against the profile, return typed result."""
    user = (
        f"CANDIDATE PROFILE:\n{profile.to_prompt_context()}\n\n"
        f"JOB OFFER:\nTitle: {offer.title}\n"
        f"Company: {offer.company}\nLocation: {offer.location}\n"
        f"Contract: {offer.contract_type}\n"
        f"Description:\n{offer.description}"
    )
    return structured_completion(_SYSTEM, user, FitAssessment)


if __name__ == "__main__":
    from job_fit_agent.france_travail import search_jobs
    from job_fit_agent.profile import load_profile

    prof = load_profile()
    offer = search_jobs("data scientist", limit=1)[0]
    result = assess_fit(offer, prof)
    print(f"{offer.title}\nScore: {result.score}/100")
    print(f"Matched: {result.matched_skills}")
    print(f"Gaps: {result.gaps}")
    print(f"Why: {result.reasoning}")
