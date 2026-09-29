import json
import tempfile
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from shorts_pipeline.config import Settings
from shorts_pipeline.ffmpeg import audio_duration
from shorts_pipeline.models import Scene
from shorts_pipeline.pipeline import Pipeline, select_providers
from shorts_pipeline.providers import LocalLLMProvider, LocalTTSProvider, OpenAITTSProvider, OpenAITTSProviderError
from shorts_pipeline.storage import RunStore


class FakeStreamingResponse:
    def __init__(self, payload: str) -> None:
        self.payload = payload

    def __enter__(self) -> "FakeStreamingResponse":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> bool:
        return False

    def stream_to_file(self, destination: Path) -> None:
        if self.payload == "empty":
            destination.write_bytes(b"")
            return
        if self.payload == "invalid":
            destination.write_bytes(b"not-a-wav" * 10)
            return
        with wave.open(str(destination), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(100)
            audio.writeframes(b"\0\0" * 250)


class FakeStreamingResponses:
    def __init__(self, payload: str | Exception) -> None:
        self.payload = payload
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> FakeStreamingResponse:
        self.calls.append(kwargs)
        if isinstance(self.payload, Exception):
            raise self.payload
        return FakeStreamingResponse(self.payload)


class FixedDurationTTS:
    def synthesize(self, text: str, duration_seconds: float, destination: Path) -> Path:
        del text, duration_seconds
        with wave.open(str(destination), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(100)
            audio.writeframes(b"\0\0" * 275)
        return destination


class FakeImageProvider:
    file_extension = ".ppm"

    def generate_image(self, scene: Scene, destination: Path) -> Path:
        del scene
        destination.write_bytes(b"placeholder")
        return destination


class OpenAITTSProviderTests(unittest.TestCase):
    def settings(self, **overrides: object) -> Settings:
        values: dict[str, object] = {
            "root": Path("."),
            "llm_provider": "local",
            "image_provider": "local",
            "tts_provider": "local",
            "video_provider": "local",
            "openai_api_key": None,
            "openai_model": "test-llm-model",
            "openai_image_model": "test-image-model",
            "openai_tts_model": "test-tts-model",
            "openai_tts_voice": "test-voice",
            "runway_api_key": None,
            "runway_video_model": "test-video-model",
            "runway_video_duration_seconds": 4,
            "runway_video_cost_per_second_usd": 0.05,
            "max_video_seconds_per_run": 12,
            "max_video_cost_per_run_usd": 0.75,
            "ffmpeg_bin": None,
            "ffprobe_bin": None,
            "timeout_seconds": 30,
            "retries": 0,
        }
        values.update(overrides)
        return Settings(**values)  # type: ignore[arg-type]

    def client(self, payload: str | Exception) -> tuple[SimpleNamespace, FakeStreamingResponses]:
        responses = FakeStreamingResponses(payload)
        return SimpleNamespace(audio=SimpleNamespace(speech=SimpleNamespace(with_streaming_response=responses))), responses

    def test_selects_local_tts_provider(self) -> None:
        _, _, tts = select_providers(self.settings())
        self.assertIsInstance(tts, LocalTTSProvider)

    def test_selects_openai_tts_provider(self) -> None:
        settings = self.settings(tts_provider="openai", openai_api_key="test-key")
        with patch("shorts_pipeline.pipeline.OpenAITTSProvider") as provider_class:
            _, _, tts = select_providers(settings)

        provider_class.assert_called_once_with("test-key", "test-tts-model", "test-voice", 30)
        self.assertIs(tts, provider_class.return_value)

    def test_openai_tts_selection_requires_api_key(self) -> None:
        with self.assertRaisesRegex(ValueError, "TTS_PROVIDER=openai requires OPENAI_API_KEY"):
            select_providers(self.settings(tts_provider="openai"))

    def test_writes_valid_wav_from_successful_response(self) -> None:
        client, responses = self.client("valid")
        provider = OpenAITTSProvider("test-key", "test-model", "test-voice", client=client)
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "narration.wav"
            result = provider.synthesize("A concise narration.", 24, destination)
            duration = audio_duration(destination)

        self.assertEqual(result, destination)
        self.assertEqual(duration, 2.5)
        self.assertEqual(responses.calls[0]["model"], "test-model")
        self.assertEqual(responses.calls[0]["voice"], "test-voice")
        self.assertEqual(responses.calls[0]["response_format"], "wav")

    def test_rejects_empty_or_malformed_audio_response(self) -> None:
        for payload, message in (("empty", "no audio data"), ("invalid", "not a valid WAV")):
            client, _ = self.client(payload)
            provider = OpenAITTSProvider("test-key", "test-model", "test-voice", client=client)
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as directory:
                with self.assertRaisesRegex(OpenAITTSProviderError, message):
                    provider.synthesize("A concise narration.", 24, Path(directory) / "narration.wav")

    def test_wraps_tts_api_failure(self) -> None:
        client, _ = self.client(RuntimeError("unavailable"))
        provider = OpenAITTSProvider("test-key", "test-model", "test-voice", client=client)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(OpenAITTSProviderError, "generation failed"):
                provider.synthesize("A concise narration.", 24, Path(directory) / "narration.wav")

    def test_pipeline_persists_scene_timing_from_actual_audio(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            settings = self.settings(root=Path(directory))

            def render(command: list[str], cwd: Path, timeout_seconds: int, retries: int) -> None:
                del command, timeout_seconds, retries
                (cwd / "render.mp4").write_bytes(b"mock mp4")

            with (
                patch("shorts_pipeline.pipeline.select_providers", return_value=(LocalLLMProvider(), FakeImageProvider(), FixedDurationTTS())),
                patch("shorts_pipeline.pipeline.render_video", side_effect=render),
                patch("shorts_pipeline.pipeline.validate_video"),
            ):
                output = Pipeline(settings).run(topic="timing")

            store = RunStore(Path(directory) / "data" / "pipeline.sqlite3")
            saved = json.loads(store.get(1)["storyboard_json"])
            store.close()

        self.assertIsNotNone(output)
        self.assertEqual(round(sum(scene["duration_seconds"] for scene in saved["scenes"]), 3), 2.75)
        self.assertNotEqual(saved["scenes"][0]["duration_seconds"], saved["scenes"][1]["duration_seconds"])
