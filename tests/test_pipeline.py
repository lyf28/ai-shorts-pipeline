import tempfile
import unittest
from pathlib import Path

from shorts_pipeline.config import Settings
from shorts_pipeline.pipeline import Pipeline
from shorts_pipeline.storage import RunStore


class PipelineTests(unittest.TestCase):
    def test_dry_run_persists_storyboard_without_media_tools(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = Settings(
                root=root,
                llm_provider="local",
                image_provider="local",
                tts_provider="local",
                video_provider="local",
                openai_api_key=None,
                openai_model="gpt-4o-mini",
                openai_image_model="gpt-image-2.5-flare",
                openai_tts_model="gpt-4o-mini-tts",
                openai_tts_voice="alloy",
                runway_api_key=None,
                runway_video_model="gen4_turbo",
                runway_video_duration_seconds=4,
                runway_video_cost_per_second_usd=0.05,
                max_video_seconds_per_run=12,
                max_video_cost_per_run_usd=0.75,
                ffmpeg_bin=None,
                ffprobe_bin=None,
                timeout_seconds=30,
                retries=0,
            )
            result = Pipeline(settings).run(topic="focus", dry_run=True)
            self.assertIsNone(result)
            store = RunStore(root / "data" / "pipeline.sqlite3")
            record = store.get(1)
            store.close()
        self.assertEqual(record["generation_status"], "dry_run_complete")
        self.assertEqual(record["idea"].find("focus") >= 0, True)
