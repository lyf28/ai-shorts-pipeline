import tempfile
import unittest
from pathlib import Path

from shorts_pipeline.config import Settings
from shorts_pipeline.pipeline import Pipeline
from shorts_pipeline.providers.base import VideoProvider
from shorts_pipeline.storyboard import build_storyboard


MP4 = b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00"


class FakeVideoProvider(VideoProvider):
    @property
    def file_extension(self) -> str:
        return ".mp4"

    def generate_from_image(self, scene, image, motion_prompt, duration_seconds, destination):
        del image, motion_prompt, duration_seconds
        if scene.index == 6:
            raise RuntimeError("generation failed")
        destination.write_bytes(MP4)
        return destination


class HybridPipelineTests(unittest.TestCase):
    def settings(self, root: Path) -> Settings:
        return Settings(
            root=root, llm_provider="local", image_provider="local", tts_provider="local", video_provider="runway",
            openai_api_key=None, openai_model="test-llm", openai_image_model="test-image", openai_tts_model="test-tts", openai_tts_voice="test-voice",
            runway_api_key="test-key", runway_video_model="gen4_turbo", runway_video_duration_seconds=4, runway_video_cost_per_second_usd=0.05,
            max_video_seconds_per_run=8, max_video_cost_per_run_usd=0.75, ffmpeg_bin=None, ffprobe_bin=None, timeout_seconds=30, retries=0,
        )

    def test_uses_budgeted_video_clips_and_falls_back_per_failed_scene(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            images = []
            for index in range(1, 7):
                image = root / f"scene_{index}.png"
                image.write_bytes(b"png")
                images.append(image)
            pipeline = object.__new__(Pipeline)
            pipeline.settings = self.settings(root)
            pipeline.video = FakeVideoProvider()
            media, metadata = pipeline._generate_hybrid_media(build_storyboard("Idea", "One. Two. Three. Four. Five. Six."), images, root)

        self.assertEqual(media[0].suffix, ".mp4")
        self.assertEqual(media[5].suffix, ".png")
        self.assertEqual(media[3].suffix, ".png")
        self.assertEqual(metadata["requested_video_seconds"], 8)
        self.assertEqual(metadata["generated_video_scenes"], 1)
        self.assertEqual(metadata["generated_estimated_cost_usd"], 0.2)
        self.assertEqual(metadata["fallbacks"], [
            {"scene_index": 4, "reason": "budget_limit"},
            {"scene_index": 6, "reason": "generation_failed", "detail": "generation failed"},
        ])
