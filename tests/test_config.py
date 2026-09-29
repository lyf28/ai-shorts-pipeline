import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from shorts_pipeline.config import Settings


class SettingsTests(unittest.TestCase):
    def test_reads_provider_settings_from_environment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(
                os.environ,
                {
                    "LLM_PROVIDER": "openai",
                    "IMAGE_PROVIDER": "openai",
                    "TTS_PROVIDER": "openai",
                    "VIDEO_PROVIDER": "runway",
                    "OPENAI_API_KEY": "test-key",
                    "OPENAI_MODEL": "test-model",
                    "OPENAI_IMAGE_MODEL": "test-image-model",
                    "OPENAI_TTS_MODEL": "test-tts-model",
                    "OPENAI_TTS_VOICE": "test-voice",
                    "RUNWAY_API_KEY": "runway-test-key",
                    "RUNWAY_VIDEO_MODEL": "test-video-model",
                    "RUNWAY_VIDEO_DURATION_SECONDS": "3",
                    "RUNWAY_VIDEO_COST_PER_SECOND_USD": "0.04",
                    "MAX_VIDEO_SECONDS_PER_RUN": "9",
                    "MAX_VIDEO_COST_PER_RUN_USD": "0.36",
                },
                clear=False,
            ):
                settings = Settings.from_root(Path(directory))

        self.assertEqual(settings.llm_provider, "openai")
        self.assertEqual(settings.image_provider, "openai")
        self.assertEqual(settings.tts_provider, "openai")
        self.assertEqual(settings.video_provider, "runway")
        self.assertEqual(settings.openai_api_key, "test-key")
        self.assertEqual(settings.openai_model, "test-model")
        self.assertEqual(settings.openai_image_model, "test-image-model")
        self.assertEqual(settings.openai_tts_model, "test-tts-model")
        self.assertEqual(settings.openai_tts_voice, "test-voice")
        self.assertEqual(settings.runway_api_key, "runway-test-key")
        self.assertEqual(settings.runway_video_model, "test-video-model")
        self.assertEqual(settings.runway_video_duration_seconds, 3)
        self.assertEqual(settings.runway_video_cost_per_second_usd, 0.04)
        self.assertEqual(settings.max_video_seconds_per_run, 9)
        self.assertEqual(settings.max_video_cost_per_run_usd, 0.36)
