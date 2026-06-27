"""Prompt artifacts loaded from text files. Git is the versioning system."""
from importlib import resources


def load_prompt(name: str) -> str:
    """Return the system prompt stored in ``<name>.md`` within this package."""
    path = resources.files(__name__) / f"{name}.md"
    return path.read_text(encoding="utf-8").strip()
