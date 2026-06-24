"""Shared LLM client (OpenRouter) and response helpers."""
import json

from openai import OpenAI

from job_fit_agent.config import llm_settings


def get_client() -> OpenAI:
    """Return an OpenAI-compatible client pointed at OpenRouter."""
    return OpenAI(
        api_key=llm_settings.openrouter_api_key,
        base_url=llm_settings.openrouter_base_url,
    )


def parse_json_response(raw: str | None) -> dict:
    """Parse an LLM response into a dict, stripping markdown code fences."""
    text = (raw or "{}").strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```")
    return json.loads(text)
