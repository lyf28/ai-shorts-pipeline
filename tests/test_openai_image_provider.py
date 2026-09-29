import base64
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from shorts_pipeline.config import Settings
from shorts_pipeline.image_prompts import build_image_prompt
from shorts_pipeline.models import Scene
from shorts_pipeline.pipeline import select_providers
from shorts_pipeline.providers import LocalImageProvider
from shorts_pipeline.providers.openai_image import OpenAIImageProvider, OpenAIImageProviderError


class FakeImages:
    def __init__(self, payload: str | Exception) -> None:
        self.payload = payload
        self.calls: list[dict[str, object]] = []

    def generate(self, **kwargs: object) -> SimpleNamespace:
        self.calls.append(kwargs)
        if isinstance(self.payload, Exception):
            raise self.payload
        return SimpleNamespace(data=[SimpleNamespace(b64_json=self.payload)])


class OpenAIImageProviderTests(unittest.TestCase):
    scene = Scene(2, "A small choice starts a visible chain of momentum.", "unused", 4)

    def settings(self, **overrides: object) -> Settings:
        values: dict[str, object] = {
            "root": Path("."),
            "llm_provider": "local",
            "image_provider": "local",
            "tts_provider": "local",
            "openai_api_key": None,
            "openai_model": "test-llm-model",
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

    def test_selects_local_image_provider(self) -> None:
        _, image, _ = select_providers(self.settings())

        self.assertIsInstance(image, LocalImageProvider)

    def test_selects_openai_image_provider(self) -> None:
        settings = self.settings(image_provider="openai", openai_api_key="test-key")
        with patch("shorts_pipeline.pipeline.OpenAIImageProvider") as provider_class:
            _, image, _ = select_providers(settings)

        provider_class.assert_called_once_with("test-key", "test-image-model", 30)
        self.assertIs(image, provider_class.return_value)

    def test_openai_image_selection_requires_an_api_key(self) -> None:
        with self.assertRaisesRegex(ValueError, "IMAGE_PROVIDER=openai requires OPENAI_API_KEY"):
            select_providers(self.settings(image_provider="openai"))

    def test_prompt_is_a_structured_visual_brief_not_raw_narration(self) -> None:
        prompt = build_image_prompt(self.scene)

        for label in ("Subject:", "Action:", "Environment:", "Mood:", "Camera framing:", "Lighting:", "Visual consistency:", "Vertical short-form composition:"):
            self.assertIn(label, prompt)
        self.assertNotIn(self.scene.narration, prompt)
        self.assertIn("small, choice, starts", prompt)

    def test_writes_expected_png_image_output(self) -> None:
        content = b"\x89PNG\r\n\x1a\nminimal-png-content"
        images = FakeImages(base64.b64encode(content).decode())
        provider = OpenAIImageProvider("test-key", "test-image-model", client=SimpleNamespace(images=images))
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "scene.png"
            result = provider.generate_image(self.scene, destination)
            written = destination.read_bytes()

        self.assertEqual(result, destination)
        self.assertEqual(written, content)
        self.assertEqual(images.calls[0]["model"], "test-image-model")
        self.assertEqual(images.calls[0]["size"], "1024x1536")
        self.assertEqual(images.calls[0]["output_format"], "png")

    def test_rejects_malformed_image_response(self) -> None:
        provider = OpenAIImageProvider("test-key", "test-image-model", client=SimpleNamespace(images=FakeImages("not-base64")))

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(OpenAIImageProviderError, "invalid base64"):
                provider.generate_image(self.scene, Path(directory) / "scene.png")

    def test_wraps_image_api_failure(self) -> None:
        provider = OpenAIImageProvider("test-key", "test-image-model", client=SimpleNamespace(images=FakeImages(RuntimeError("unavailable"))))

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(OpenAIImageProviderError, "generation failed"):
                provider.generate_image(self.scene, Path(directory) / "scene.png")
