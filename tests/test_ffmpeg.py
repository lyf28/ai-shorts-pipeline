import tempfile
import unittest
import wave
from pathlib import Path

from shorts_pipeline.ffmpeg import audio_duration, build_video_command
from shorts_pipeline.storyboard import build_storyboard


class FFmpegCommandTests(unittest.TestCase):
    def test_command_targets_vertical_h264_mp4_with_subtitles(self) -> None:
        board = build_storyboard("Idea", "One. Two. Three. Four. Five. Six.")
        command = build_video_command("ffmpeg", board, [Path(f"scene_{i}.ppm") for i in range(6)], Path("audio.wav"), Path("subtitles.srt"), Path("out.mp4"))
        joined = " ".join(command)
        self.assertIn("scale=1080:1920", joined)
        self.assertIn("zoompan=", joined)
        self.assertIn("-framerate 30", joined)
        self.assertIn("subtitles=subtitles.srt", joined)
        self.assertIn("libx264", command)
        self.assertEqual(command[-1], "out.mp4")

    def test_reads_wav_narration_duration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "narration.wav"
            with wave.open(str(path), "wb") as audio:
                audio.setnchannels(1)
                audio.setsampwidth(2)
                audio.setframerate(100)
                audio.writeframes(b"\0\0" * 250)
            self.assertEqual(audio_duration(path), 2.5)
