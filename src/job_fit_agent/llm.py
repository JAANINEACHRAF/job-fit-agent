"""Shared LLM client (OpenRouter) and response helpers."""
import json
import re
from typing import Any

from openai import OpenAI

from job_fit_agent.config import llm_settings


def get_client() -> OpenAI:
    """Return an OpenAI-compatible client pointed at OpenRouter."""
    return OpenAI(
        api_key=llm_settings.openrouter_api_key,
        base_url=llm_settings.openrouter_base_url,
    )


def parse_json_response(raw: str | None) -> dict[str, Any]:
    """Extract and parse the first JSON object from an LLM response.

    Handles markdown code fences and trailing/leading prose by isolating the
    outermost {...} block before parsing.
    """
    text = (raw or "{}").strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    # Isolate the outermost JSON object: first '{' to last '}'.
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match is None:
        raise ValueError(f"No JSON object found in LLM response: {text[:200]!r}")
    return json.loads(match.group(0))
