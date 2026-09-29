import tempfile
import unittest
from pathlib import Path

from shorts_pipeline.storage import RunStore


class StorageTests(unittest.TestCase):
    def test_persists_required_run_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = RunStore(Path(directory) / "runs.sqlite3")
            run_id = store.create()
            store.update(run_id, idea="Idea", script="Script", storyboard_json={"scenes": []}, prompts_json=["prompt"], generation_status="completed", output_path="output/x.mp4", error_logs="")
            record = store.get(run_id)
            store.close()
        self.assertEqual(record["idea"], "Idea")
        self.assertEqual(record["generation_status"], "completed")
        self.assertIn("scenes", record["storyboard_json"])
