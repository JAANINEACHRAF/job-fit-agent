"""LangGraph self-critique agent: assess fit, then validate and revise."""
import json
from typing import TypedDict

from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from job_fit_agent.config import llm_settings
from job_fit_agent.matcher import FitAssessment, _client
from job_fit_agent.models import JobOffer
from job_fit_agent.profile import CandidateProfile


class Critique(BaseModel):
    """The critic's verdict on an assessment."""

    approved: bool = Field(description="True if the assessment is sound")
    issues: list[str] = Field(description="Specific problems found, empty if approved")


class AgentState(TypedDict):
    offer: JobOffer
    profile: CandidateProfile
    assessment: FitAssessment | None
    critique: Critique | None
    revisions: int


_MAX_REVISIONS = 2

_ASSESS_SYS = (
    "You are a precise technical recruiter. Assess candidate-job fit using ONLY the "
    "provided profile and offer. Respond ONLY with JSON: "
    '{"score": int 0-100, "matched_skills": [str], "gaps": [str], "reasoning": str}.'
)

_CRITIC_SYS = (
    "You are a strict reviewer of a recruiter's fit assessment. Check that every "
    "matched_skill is actually in the candidate profile, every gap is genuinely "
    "absent, and the score matches the evidence. Flag any hallucinated skill or "
    "unsupported claim. Respond ONLY with JSON: "
    '{"approved": bool, "issues": [str]}.'
)


def _parse(raw: str | None) -> dict:
    text = (raw or "{}").strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```")
    return json.loads(text)


def _offer_block(offer: JobOffer) -> str:
    return (
        f"Title: {offer.title}\nCompany: {offer.company}\n"
        f"Location: {offer.location}\nContract: {offer.contract_type}\n"
        f"Description:\n{offer.description}"
    )


def assess_node(state: AgentState) -> AgentState:
    user = (
        f"CANDIDATE PROFILE:\n{state['profile'].to_prompt_context()}\n\n"
        f"JOB OFFER:\n{_offer_block(state['offer'])}"
    )
    if state.get("critique") and not state["critique"].approved:
        user += (
            "\n\nA reviewer flagged your previous assessment. Fix these issues:\n"
            + "\n".join(f"- {i}" for i in state["critique"].issues)
        )
    resp = _client().chat.completions.create(
        model=llm_settings.llm_model,
        messages=[
            {"role": "system", "content": _ASSESS_SYS},
            {"role": "user", "content": user},
        ],
        temperature=0,
    )
    state["assessment"] = FitAssessment.model_validate(
        _parse(resp.choices[0].message.content)
    )
    return state


def critique_node(state: AgentState) -> AgentState:
    user = (
        f"CANDIDATE PROFILE:\n{state['profile'].to_prompt_context()}\n\n"
        f"JOB OFFER:\n{_offer_block(state['offer'])}\n\n"
        f"ASSESSMENT TO REVIEW:\n{state['assessment'].model_dump_json(indent=2)}"
    )
    resp = _client().chat.completions.create(
        model=llm_settings.llm_model,
        messages=[
            {"role": "system", "content": _CRITIC_SYS},
            {"role": "user", "content": user},
        ],
        temperature=0,
    )
    state["critique"] = Critique.model_validate(_parse(resp.choices[0].message.content))
    state["revisions"] = state.get("revisions", 0) + 1
    return state


def should_revise(state: AgentState) -> str:
    """Conditional edge: revise if critic rejected and we have budget left."""
    if state["critique"].approved or state["revisions"] >= _MAX_REVISIONS:
        return END
    return "assess"


def build_agent() -> object:
    g = StateGraph(AgentState)
    g.add_node("assess", assess_node)
    g.add_node("critique", critique_node)
    g.set_entry_point("assess")
    g.add_edge("assess", "critique")
    g.add_conditional_edges("critique", should_revise, {"assess": "assess", END: END})
    return g.compile()


def run_agent(offer: JobOffer, profile: CandidateProfile) -> AgentState:
    agent = build_agent()
    initial: AgentState = {
        "offer": offer,
        "profile": profile,
        "assessment": None,
        "critique": None,
        "revisions": 0,
    }
    return agent.invoke(initial)


if __name__ == "__main__":
    from job_fit_agent.france_travail import get_access_token, search_jobs
    from job_fit_agent.profile import load_profile

    prof = load_profile()
    tok = get_access_token()
    offer = search_jobs("data scientist", tok, limit=1)[0]
    result = run_agent(offer, prof)
    a = result["assessment"]
    print(f"{offer.title}")
    print(f"Score: {a.score}/100 | revisions: {result['revisions']}")
    print(f"Critic approved: {result['critique'].approved}")
    if result["critique"].issues:
        print(f"Issues raised: {result['critique'].issues}")
    print(f"Gaps: {a.gaps}")
