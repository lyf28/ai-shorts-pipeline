import subprocess
import tempfile
import unittest
import wave
from pathlib import Path

from shorts_pipeline.ffmpeg import build_hybrid_video_command, render_video, resolve_ffmpeg, resolve_ffprobe, validate_video
from shorts_pipeline.storyboard import build_storyboard, write_subtitles


class HybridFFmpegIntegrationTests(unittest.TestCase):
    def test_composes_a_real_mixed_media_vertical_mp4(self) -> None:
        ffmpeg = resolve_ffmpeg()
        storyboard = build_storyboard("Idea", "One. Two. Three. Four. Five. Six.", total_seconds=1.2)
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory)
            video = work_dir / "scene_1.mp4"
            subprocess.run(
                [ffmpeg, "-y", "-f", "lavfi", "-i", "color=c=blue:s=360x640:r=30:d=0.3", "-c:v", "libx264", "-pix_fmt", "yuv420p", video.name],
                cwd=work_dir,
                check=True,
                capture_output=True,
            )
            images = []
            for index in range(2, 7):
                image = work_dir / f"scene_{index}.ppm"
                image.write_bytes(b"P6\n2 4\n255\n" + bytes([index * 20, 40, 180]) * 8)
                images.append(image)
            audio = work_dir / "narration.wav"
            with wave.open(str(audio), "wb") as narration:
                narration.setnchannels(1)
                narration.setsampwidth(2)
                narration.setframerate(8000)
                narration.writeframes(b"\0\0" * int(8000 * 1.2))
            subtitles = work_dir / "subtitles.srt"
            write_subtitles(storyboard, subtitles)
            output = work_dir / "render.mp4"
            command = build_hybrid_video_command(ffmpeg, storyboard, [video, *images], audio, subtitles, output)
            render_video(command, work_dir, timeout_seconds=30, retries=0)
            validate_video(output, resolve_ffprobe(), ffmpeg, timeout_seconds=30)

            self.assertGreater(output.stat().st_size, 1024)
