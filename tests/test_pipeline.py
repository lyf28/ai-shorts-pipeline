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
            settings = Settings(root, "local", "local", "local", None, "gpt-4o-mini", None, None, 30, 0)
            result = Pipeline(settings).run(topic="focus", dry_run=True)
            self.assertIsNone(result)
            store = RunStore(root / "data" / "pipeline.sqlite3")
            record = store.get(1)
            store.close()
        self.assertEqual(record["generation_status"], "dry_run_complete")
        self.assertEqual(record["idea"].find("focus") >= 0, True)
