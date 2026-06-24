"""LLM-based fit matcher: scores one job offer against the candidate profile."""
import json

from openai import OpenAI
from pydantic import BaseModel, Field

from job_fit_agent.config import llm_settings
from job_fit_agent.models import JobOffer
from job_fit_agent.profile import CandidateProfile


class FitAssessment(BaseModel):
    """Structured fit assessment returned by the LLM."""

    score: int = Field(ge=0, le=100, description="Overall fit score 0-100")
    matched_skills: list[str] = Field(description="Profile skills the job requires")
    gaps: list[str] = Field(description="Job requirements the profile lacks")
    reasoning: str = Field(description="Concise justification for the score")


_SYSTEM = (
    "You are a precise technical recruiter. Assess how well a candidate fits a job "
    "offer. Base every judgment only on the provided profile and offer. Be honest "
    "about gaps. Respond ONLY with a JSON object matching this schema: "
    '{"score": int 0-100, "matched_skills": [str], "gaps": [str], "reasoning": str}. '
    "No markdown, no prose outside the JSON."
)


def _client() -> OpenAI:
    return OpenAI(
        api_key=llm_settings.openrouter_api_key,
        base_url=llm_settings.openrouter_base_url,
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
    resp = _client().chat.completions.create(
        model=llm_settings.llm_model,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": user},
        ],
        temperature=0,
    )
    raw = resp.choices[0].message.content or "{}"
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    return FitAssessment.model_validate(json.loads(raw))


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
