import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from shorts_pipeline.config import Settings
from shorts_pipeline.pipeline import select_providers
from shorts_pipeline.providers import LocalImageProvider, LocalLLMProvider, LocalTTSProvider
from shorts_pipeline.providers.openai import OpenAILLMProvider, OpenAIProviderError


class FakeResponses:
    def __init__(self, payloads: dict[str, object]) -> None:
        self.payloads = payloads
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> SimpleNamespace:
        self.calls.append(kwargs)
        name = kwargs["text"]["format"]["name"]  # type: ignore[index]
        payload = self.payloads[name]  # type: ignore[index]
        return SimpleNamespace(output_text=payload if isinstance(payload, str) else json.dumps(payload))


class OpenAILLMProviderTests(unittest.TestCase):
    def settings(self, **overrides: object) -> Settings:
        values: dict[str, object] = {
            "root": Path("."),
            "llm_provider": "local",
            "image_provider": "local",
            "tts_provider": "local",
            "openai_api_key": None,
            "openai_model": "test-model",
            "openai_image_model": "test-image-model",
            "openai_tts_model": "test-tts-model",
            "openai_tts_voice": "test-voice",
            "ffmpeg_bin": None,
            "ffprobe_bin": None,
            "timeout_seconds": 30,
            "retries": 0,
        }
        values.update(overrides)
        return Settings(**values)  # type: ignore[arg-type]

    def test_selects_local_providers_by_default(self) -> None:
        llm, video, tts = select_providers(self.settings())

        self.assertIsInstance(llm, LocalLLMProvider)
        self.assertIsInstance(video, LocalImageProvider)
        self.assertIsInstance(tts, LocalTTSProvider)

    def test_selects_openai_llm_provider(self) -> None:
        settings = self.settings(llm_provider="openai", openai_api_key="test-key")
        with patch("shorts_pipeline.pipeline.OpenAILLMProvider") as provider_class:
            llm, _, _ = select_providers(settings)

        provider_class.assert_called_once_with("test-key", "test-model", 30)
        self.assertIs(llm, provider_class.return_value)

    def test_openai_selection_requires_an_api_key(self) -> None:
        with self.assertRaisesRegex(ValueError, "LLM_PROVIDER=openai requires OPENAI_API_KEY"):
            select_providers(self.settings(llm_provider="openai"))

    def test_generates_structured_idea(self) -> None:
        responses = FakeResponses({"short_video_idea": {"idea": "A hidden domino path reveals the payoff."}})
        provider = OpenAILLMProvider("test-key", "test-model", client=SimpleNamespace(responses=responses))

        idea = provider.generate_idea("habits")

        self.assertEqual(idea, "A hidden domino path reveals the payoff.")
        call = responses.calls[0]
        self.assertEqual(call["model"], "test-model")
        self.assertIn("hook", call["instructions"])
        self.assertEqual(call["text"]["format"]["strict"], True)  # type: ignore[index]

    def test_generates_structured_script(self) -> None:
        script = "The first domino falls. The chain races forward. The final block reveals why tiny choices matter."
        responses = FakeResponses({"short_video_script": {"script": script}})
        provider = OpenAILLMProvider("test-key", "test-model", client=SimpleNamespace(responses=responses))

        result = provider.generate_script("A domino-chain habit reveal")

        self.assertEqual(result, script)
        self.assertIn("five or six visual scenes", responses.calls[0]["instructions"])

    def test_rejects_malformed_structured_response(self) -> None:
        responses = FakeResponses({"short_video_idea": "not-json"})
        provider = OpenAILLMProvider("test-key", "test-model", client=SimpleNamespace(responses=responses))

        with self.assertRaisesRegex(OpenAIProviderError, "malformed idea JSON"):
            provider.generate_idea()
