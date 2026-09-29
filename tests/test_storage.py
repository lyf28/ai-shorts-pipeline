import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from shorts_pipeline.storage import RunStore


class StorageTests(unittest.TestCase):
    def test_persists_required_run_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = RunStore(Path(directory) / "runs.sqlite3")
            run_id = store.create()
            store.update(run_id, idea="Idea", script="Script", storyboard_json={"scenes": []}, prompts_json=["prompt"], media_json={"provider": "local"}, generation_status="completed", output_path="output/x.mp4", error_logs="")
            record = store.get(run_id)
            store.close()
        self.assertEqual(record["idea"], "Idea")
        self.assertEqual(record["generation_status"], "completed")
        self.assertIn("scenes", record["storyboard_json"])
        self.assertEqual(json.loads(record["media_json"])["provider"], "local")

    def test_migrates_existing_database_with_media_metadata_column(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "runs.sqlite3"
            connection = sqlite3.connect(path)
            connection.execute("CREATE TABLE pipeline_runs (id INTEGER PRIMARY KEY, created_at TEXT, generation_status TEXT, error_logs TEXT)")
            connection.close()
            store = RunStore(path)
            columns = {row[1] for row in store.connection.execute("PRAGMA table_info(pipeline_runs)")}
            store.close()
        self.assertIn("media_json", columns)
