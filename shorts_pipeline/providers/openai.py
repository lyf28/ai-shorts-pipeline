from __future__ import annotations

import json
from typing import Any

from shorts_pipeline.providers.base import LLMProvider


class OpenAIProviderError(RuntimeError):
    """Raised when OpenAI cannot return the structured text the pipeline needs."""


IDEA_SCHEMA = {
    "type": "object",
    "properties": {"idea": {"type": "string"}},
    "required": ["idea"],
    "additionalProperties": False,
}

SCRIPT_SCHEMA = {
    "type": "object",
    "properties": {"script": {"type": "string"}},
    "required": ["script"],
    "additionalProperties": False,
}

IDEA_INSTRUCTIONS = """You create compelling short-form video ideas for Shorts, TikTok, and Reels.
Return one simple, instantly understandable, highly visual premise. The first one or two seconds
must have a clear hook. Build in visible progression, then finish with a concrete payoff, reveal,
twist, or satisfying ending. Avoid generic motivational filler, vague advice, and introductions."""

SCRIPT_INSTRUCTIONS = """You write voiceover scripts for 20 to 30 second vertical short videos.
Open with the hook immediately; never use an introduction such as 'Today I am going to introduce'.
Every sentence must advance the story. Write roughly 55 to 75 spoken words that can be cut into
five or six visual scenes, with a clear closing beat, payoff, reveal, or satisfying ending.
Avoid generic motivational filler."""


class OpenAILLMProvider(LLMProvider):
    """OpenAI-backed creative text provider using strict structured output."""

    def __init__(self, api_key: str, model: str, timeout_seconds: int = 180, client: Any | None = None) -> None:
        if not api_key:
            raise ValueError("OpenAI LLM provider requires OPENAI_API_KEY.")
        if not model.strip():
            raise ValueError("OpenAI LLM provider requires a non-empty OPENAI_MODEL.")
        self.model = model
        if client is None:
            try:
                from openai import OpenAI
            except ImportError as error:
                raise OpenAIProviderError("OpenAI SDK is not installed. Run `pip install -r requirements.txt`.") from error
            client = OpenAI(api_key=api_key, timeout=timeout_seconds)
        self._client = client

    def generate_idea(self, topic: str | None = None) -> str:
        request = f"Create an idea about this topic: {topic}." if topic else "Create an original idea."
        return self._request(IDEA_INSTRUCTIONS, request, "short_video_idea", IDEA_SCHEMA, "idea")

    def generate_script(self, idea: str) -> str:
        request = f"Write the script for this idea: {idea}"
        return self._request(SCRIPT_INSTRUCTIONS, request, "short_video_script", SCRIPT_SCHEMA, "script")

    def _request(self, instructions: str, request: str, schema_name: str, schema: dict[str, object], field: str) -> str:
        response = self._client.responses.create(
            model=self.model,
            instructions=instructions,
            input=request,
            max_output_tokens=400,
            text={"format": {"type": "json_schema", "name": schema_name, "strict": True, "schema": schema}},
        )
        output_text = getattr(response, "output_text", None)
        if not isinstance(output_text, str):
            raise OpenAIProviderError(f"OpenAI returned no structured {field} output.")
        try:
            payload = json.loads(output_text)
        except json.JSONDecodeError as error:
            raise OpenAIProviderError(f"OpenAI returned malformed {field} JSON.") from error
        value = payload.get(field) if isinstance(payload, dict) else None
        if not isinstance(value, str) or not value.strip():
            raise OpenAIProviderError(f"OpenAI returned malformed {field} output: expected a non-empty '{field}' field.")
        return value.strip()
