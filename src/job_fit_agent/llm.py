"""Shared LLM client (OpenRouter) and structured-output helper."""
from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

from job_fit_agent.config import llm_settings

T = TypeVar("T", bound=BaseModel)

# Force OpenRouter to route only to providers that honour the response schema.
_PROVIDER_REQUIRE = {"require_parameters": True}


def get_client() -> OpenAI:
    """Return an OpenAI-compatible client pointed at OpenRouter."""
    return OpenAI(
        api_key=llm_settings.openrouter_api_key,
        base_url=llm_settings.openrouter_base_url,
        timeout=30.0,
        max_retries=2,
    )


def structured_completion(system: str, user: str, schema: type[T]) -> T:
    """Call the LLM and return a validated instance of `schema`.

    Uses OpenRouter structured outputs (JSON schema, strict) so the response is
    guaranteed to match the Pydantic model — no manual text parsing.
    """
    completion = get_client().beta.chat.completions.parse(
        model=llm_settings.llm_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format=schema,
        temperature=0,
        extra_body={"provider": _PROVIDER_REQUIRE},
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise ValueError("LLM returned no parseable structured output.")
    return parsed
