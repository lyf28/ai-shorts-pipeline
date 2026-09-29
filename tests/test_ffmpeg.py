import unittest
from pathlib import Path

from shorts_pipeline.ffmpeg import build_video_command
from shorts_pipeline.storyboard import build_storyboard


class FFmpegCommandTests(unittest.TestCase):
    def test_command_targets_vertical_h264_mp4_with_subtitles(self) -> None:
        board = build_storyboard("Idea", "One. Two. Three. Four. Five. Six.")
        command = build_video_command("ffmpeg", board, [Path(f"scene_{i}.ppm") for i in range(6)], Path("audio.wav"), Path("subtitles.srt"), Path("out.mp4"))
        joined = " ".join(command)
        self.assertIn("scale=1080:1920", joined)
        self.assertIn("subtitles=subtitles.srt", joined)
        self.assertIn("libx264", command)
        self.assertEqual(command[-1], "out.mp4")
