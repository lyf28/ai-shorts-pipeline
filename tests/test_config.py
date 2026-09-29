import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from shorts_pipeline.config import Settings


class SettingsTests(unittest.TestCase):
    def test_reads_openai_llm_settings_from_environment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(
                os.environ,
                {
                    "LLM_PROVIDER": "openai",
                    "IMAGE_PROVIDER": "openai",
                    "OPENAI_API_KEY": "test-key",
                    "OPENAI_MODEL": "test-model",
                    "OPENAI_IMAGE_MODEL": "test-image-model",
                },
                clear=False,
            ):
                settings = Settings.from_root(Path(directory))

        self.assertEqual(settings.llm_provider, "openai")
        self.assertEqual(settings.image_provider, "openai")
        self.assertEqual(settings.openai_api_key, "test-key")
        self.assertEqual(settings.openai_model, "test-model")
        self.assertEqual(settings.openai_image_model, "test-image-model")
