import tempfile
import unittest
from pathlib import Path

from shorts_pipeline.storyboard import build_storyboard, split_script, srt_timestamp, write_subtitles


class StoryboardTests(unittest.TestCase):
    def test_builds_six_scenes_totalling_24_seconds(self) -> None:
        script = "First hook. Second point. Third point. Fourth point. Fifth point. Final action."
        board = build_storyboard("Idea", script)
        self.assertEqual(len(board.scenes), 6)
        self.assertEqual(sum(scene.duration_seconds for scene in board.scenes), 24)
        self.assertEqual(board.scenes[0].index, 1)

    def test_short_script_is_split_to_requested_scene_count(self) -> None:
        chunks = split_script("A considerably longer sentence should be divided into smaller parts for scenes.", 5)
        self.assertEqual(len(chunks), 5)
        self.assertTrue(all(chunks))

    def test_writes_standard_srt_timestamps(self) -> None:
        self.assertEqual(srt_timestamp(61.25), "00:01:01,250")
        board = build_storyboard("Idea", "One. Two. Three. Four. Five. Six.")
        with tempfile.TemporaryDirectory() as directory:
            subtitles = Path(directory) / "captions.srt"
            write_subtitles(board, subtitles)
            self.assertIn("00:00:00,000 --> 00:00:04,000", subtitles.read_text(encoding="utf-8"))
