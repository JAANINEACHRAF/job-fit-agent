"""LangGraph self-critique agent: assess fit, then validate and revise."""
from typing import TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field

from job_fit_agent.llm import structured_completion
from job_fit_agent.matcher import FitAssessment
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
    "provided profile and offer. Be honest about gaps. The score must be 0 to 100."
)

_CRITIC_SYS = (
    "You are a strict reviewer of a recruiter's fit assessment. Check that every "
    "matched_skill is actually in the candidate profile, every gap is genuinely "
    "absent, and the score matches the evidence. Flag any hallucinated skill or "
    "unsupported claim."
)


def _offer_block(offer: JobOffer) -> str:
    return (
        f"Title: {offer.title}\nCompany: {offer.company}\n"
        f"Location: {offer.location}\nContract: {offer.contract_type}\n"
        f"Description:\n{offer.description}"
    )


def assess_node(state: AgentState) -> dict:
    user = (
        f"CANDIDATE PROFILE:\n{state['profile'].to_prompt_context()}\n\n"
        f"JOB OFFER:\n{_offer_block(state['offer'])}"
    )
    critique = state.get("critique")
    if critique is not None and not critique.approved:
        user += (
            "\n\nA reviewer flagged your previous assessment. Fix these issues:\n"
            + "\n".join(f"- {i}" for i in critique.issues)
        )
    assessment = structured_completion(_ASSESS_SYS, user, FitAssessment)
    return {"assessment": assessment}


def critique_node(state: AgentState) -> dict:
    assessment = state["assessment"]
    assert assessment is not None  # assess_node always runs first
    user = (
        f"CANDIDATE PROFILE:\n{state['profile'].to_prompt_context()}\n\n"
        f"JOB OFFER:\n{_offer_block(state['offer'])}\n\n"
        f"ASSESSMENT TO REVIEW:\n{assessment.model_dump_json(indent=2)}"
    )
    critique = structured_completion(_CRITIC_SYS, user, Critique)
    return {"critique": critique, "revisions": state.get("revisions", 0) + 1}


def should_revise(state: AgentState) -> str:
    """Conditional edge: revise if critic rejected and we have budget left."""
    critique = state["critique"]
    assert critique is not None  # critique_node always runs before this
    if critique.approved or state["revisions"] >= _MAX_REVISIONS:
        return END
    return "assess"


def build_agent() -> CompiledStateGraph:
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
    return agent.invoke(initial)  # type: ignore[return-value]


if __name__ == "__main__":
    from job_fit_agent.france_travail import FranceTravailSource
    from job_fit_agent.profile import load_profile

    prof = load_profile()
    offer = FranceTravailSource().search("data scientist", limit=1)[0]
    result = run_agent(offer, prof)
    a = result["assessment"]
    c = result["critique"]
    assert a is not None and c is not None
    print(f"{offer.title}")
    print(f"Score: {a.score}/100 | revisions: {result['revisions']}")
    print(f"Critic approved: {c.approved}")
    if c.issues:
        print(f"Issues raised: {c.issues}")
    print(f"Gaps: {a.gaps}")
