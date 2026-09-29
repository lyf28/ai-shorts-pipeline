import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from shorts_pipeline.config import Settings
from shorts_pipeline.models import Scene
from shorts_pipeline.pipeline import Pipeline, select_video_provider
from shorts_pipeline.providers import RunwayVideoProvider, RunwayVideoProviderError


MP4 = b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00"


class FakeImageToVideo:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> SimpleNamespace:
        self.calls.append(kwargs)
        return SimpleNamespace(id="task-123")


class FakeTasks:
    def __init__(self, statuses: list[SimpleNamespace]) -> None:
        self.statuses = iter(statuses)
        self.calls: list[str] = []

    def retrieve(self, task_id: str) -> SimpleNamespace:
        self.calls.append(task_id)
        return next(self.statuses)


class RunwayVideoProviderTests(unittest.TestCase):
    scene = Scene(1, "A reveal.", "visual", 4)

    def settings(self, **overrides: object) -> Settings:
        values: dict[str, object] = {
            "root": Path("."), "llm_provider": "local", "image_provider": "local", "tts_provider": "local", "video_provider": "local",
            "openai_api_key": None, "openai_model": "test-llm-model", "openai_image_model": "test-image-model", "openai_tts_model": "test-tts-model", "openai_tts_voice": "test-voice",
            "runway_api_key": None, "runway_video_model": "test-video-model", "runway_video_duration_seconds": 4, "runway_video_cost_per_second_usd": 0.05,
            "max_video_seconds_per_run": 12, "max_video_cost_per_run_usd": 0.75, "ffmpeg_bin": None, "ffprobe_bin": None, "timeout_seconds": 30, "retries": 0,
        }
        values.update(overrides)
        return Settings(**values)  # type: ignore[arg-type]

    def test_selects_runway_video_provider(self) -> None:
        settings = self.settings(video_provider="runway", runway_api_key="test-key")
        with patch("shorts_pipeline.pipeline.RunwayVideoProvider") as provider_class:
            provider = select_video_provider(settings)

        provider_class.assert_called_once_with("test-key", "test-video-model", 30)
        self.assertIs(provider, provider_class.return_value)
        self.assertIsNone(select_video_provider(self.settings()))

    def test_runway_selection_requires_api_key(self) -> None:
        with self.assertRaisesRegex(ValueError, "VIDEO_PROVIDER=runway requires RUNWAY_API_KEY"):
            select_video_provider(self.settings(video_provider="runway"))
        with self.assertRaisesRegex(ValueError, "VIDEO_PROVIDER=runway requires RUNWAY_API_KEY"):
            Pipeline(self.settings(video_provider="runway"))

    def test_generates_mp4_after_polling_successful_task(self) -> None:
        image_to_video = FakeImageToVideo()
        tasks = FakeTasks([
            SimpleNamespace(status="PENDING"),
            SimpleNamespace(status="RUNNING"),
            SimpleNamespace(status="SUCCEEDED", output=["https://example.invalid/video.mp4"]),
        ])
        sleeps: list[float] = []
        client = SimpleNamespace(image_to_video=image_to_video, tasks=tasks)

        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "scene.png"
            image.write_bytes(b"png")
            destination = Path(directory) / "scene.mp4"
            provider = RunwayVideoProvider("test-key", "test-model", client=client, downloader=lambda url, path, timeout: path.write_bytes(MP4), sleeper=sleeps.append)
            result = provider.generate_from_image(self.scene, image, "The camera pushes toward the reveal.", 4, destination)

        self.assertEqual(result, destination)
        self.assertEqual(tasks.calls, ["task-123", "task-123", "task-123"])
        self.assertEqual(sleeps, [5.0, 5.0])
        self.assertEqual(image_to_video.calls[0]["model"], "test-model")
        self.assertEqual(image_to_video.calls[0]["ratio"], "720:1280")
        self.assertEqual(image_to_video.calls[0]["duration"], 4)

    def test_rejects_failed_or_timed_out_task(self) -> None:
        for task, message, clock in (
            (SimpleNamespace(status="FAILED"), "ended with status FAILED", None),
            (SimpleNamespace(status="PENDING"), "timed out", iter([0.0, 4.0]).__next__),
        ):
            client = SimpleNamespace(image_to_video=FakeImageToVideo(), tasks=FakeTasks([task]))
            with self.subTest(message=message), tempfile.TemporaryDirectory() as directory:
                image = Path(directory) / "scene.png"
                image.write_bytes(b"png")
                provider = RunwayVideoProvider("test-key", "test-model", timeout_seconds=3, client=client, clock=clock or (lambda: 0.0), sleeper=lambda seconds: None)
                with self.assertRaisesRegex(RunwayVideoProviderError, message):
                    provider.generate_from_image(self.scene, image, "The camera pushes toward the reveal.", 4, Path(directory) / "scene.mp4")
