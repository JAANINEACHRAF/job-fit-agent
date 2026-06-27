"""Tests for the prompt loader and the externalized prompt files."""
from job_fit_agent.prompts import load_prompt


def test_load_prompt_returns_clean_text() -> None:
    text = load_prompt("fit_assess_system")
    assert text  # non-empty
    assert text == text.strip()  # no surrounding whitespace
    assert "technical recruiter" in text


def test_all_system_prompts_load() -> None:
    for name in ("fit_assess_system", "agent_assess_system", "agent_critic_system"):
        assert load_prompt(name)
