"""Candidate profile: typed model + loader."""
import json
from pathlib import Path

from pydantic import BaseModel

_PROFILE_PATH = Path(__file__).parent / "data" / "profile.json"


class Experience(BaseModel):
    role: str
    company: str
    period: str
    highlights: list[str]


class Project(BaseModel):
    name: str
    description: str


class CandidateProfile(BaseModel):
    name: str
    title: str
    location: str
    summary: str
    seniority: str
    languages: list[str]
    skills: dict[str, list[str]]
    experience: list[Experience]
    projects: list[Project]
    education: list[str]
    certifications: list[str]

    def to_prompt_context(self) -> str:
        """Flatten the profile into a compact text block for an LLM prompt."""
        skills = "; ".join(f"{k}: {', '.join(v)}" for k, v in self.skills.items())
        exp = "\n".join(
            f"- {e.role} @ {e.company} ({e.period}): {' '.join(e.highlights)}"
            for e in self.experience
        )
        projects = "\n".join(f"- {p.name}: {p.description}" for p in self.projects)
        return (
            f"Name: {self.name} | {self.title} | {self.location} "
            f"| seniority: {self.seniority}\n"
            f"Summary: {self.summary}\n"
            f"Languages: {', '.join(self.languages)}\n"
            f"Skills: {skills}\n"
            f"Experience:\n{exp}\n"
            f"Projects:\n{projects}\n"
            f"Education: {'; '.join(self.education)}\n"
            f"Certifications: {'; '.join(self.certifications)}"
        )


def load_profile() -> CandidateProfile:
    """Load and validate the candidate profile from disk."""
    with _PROFILE_PATH.open(encoding="utf-8") as f:
        return CandidateProfile.model_validate(json.load(f))
