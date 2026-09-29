from __future__ import annotations

import importlib
import logging
import re
import shutil
import subprocess
import wave
from pathlib import Path

from shorts_pipeline.models import Storyboard

LOG = logging.getLogger(__name__)


class FFmpegError(RuntimeError):
    pass


def resolve_ffmpeg(configured: str | None = None) -> str:
    if configured:
        return configured
    if binary := shutil.which("ffmpeg"):
        return binary
    try:
        return importlib.import_module("imageio_ffmpeg").get_ffmpeg_exe()
    except (ImportError, RuntimeError) as error:
        raise FFmpegError("FFmpeg was not found. Install imageio-ffmpeg or set FFMPEG_BIN in .env.") from error


def resolve_ffprobe(configured: str | None = None) -> str | None:
    if configured:
        return configured
    return shutil.which("ffprobe")


def audio_duration(path: Path) -> float:
    """Return the duration of the pipeline's normalized WAV narration."""
    try:
        with wave.open(str(path), "rb") as audio:
            frames = audio.getnframes()
            sample_rate = audio.getframerate()
    except (wave.Error, EOFError) as error:
        raise FFmpegError(f"Narration audio is not a readable WAV file: {path}") from error
    if frames <= 0 or sample_rate <= 0:
        raise FFmpegError(f"Narration audio has no duration: {path}")
    return frames / sample_rate


def image_motion_filter(index: int) -> str:
    """Return a subtle deterministic Ken Burns movement for one scene."""
    zoom = "min(max(zoom,pzoom)+0.0005,1.08)"
    if index % 2:
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    else:
        x, y = "min(iw-iw/zoom,on*1.25)", "ih/2-(ih/zoom/2)"
    return f"zoompan=z='{zoom}':x='{x}':y='{y}':d=1:s=1080x1920:fps=30"


def build_video_command(ffmpeg: str, storyboard: Storyboard, images: list[Path], audio: Path, subtitles: Path, output: Path) -> list[str]:
    if len(images) != len(storyboard.scenes):
        raise ValueError("Every storyboard scene needs exactly one visual asset")
    command = [ffmpeg, "-y"]
    for scene, image in zip(storyboard.scenes, images, strict=True):
        # Use relative names: some Windows FFmpeg builds cannot open Unicode absolute paths.
        command.extend(["-loop", "1", "-framerate", "30", "-t", str(scene.duration_seconds), "-i", image.name])
    command.extend(["-i", audio.name])
    filters = [
        (
            f"[{index}:v]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop=1080:1920,{image_motion_filter(index)},setsar=1[v{index}]"
        )
        for index in range(len(images))
    ]
    filters.append("".join(f"[v{i}]" for i in range(len(images))) + f"concat=n={len(images)}:v=1:a=0[concat_video]")
    # Subtitle filtering must be part of the complex graph because concat already is.
    # The command executes in the subtitles directory, avoiding Windows drive-letter escaping.
    filters.append(f"[concat_video]subtitles={subtitles.name}[video]")
    command.extend([
        "-filter_complex", ";".join(filters), "-map", "[video]", "-map", f"{len(images)}:a",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-r", "30", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", output.name,
    ])
    return command


def render_video(command: list[str], cwd: Path, timeout_seconds: int, retries: int) -> None:
    failure: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            LOG.info("Running FFmpeg (attempt %s/%s)", attempt, retries + 1)
            result = subprocess.run(command, cwd=cwd, check=True, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=timeout_seconds)
            LOG.debug("FFmpeg output: %s", result.stderr[-2000:])
            return
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            failure = error
            LOG.warning("FFmpeg attempt %s failed: %s", attempt, error)
    details = getattr(failure, "stderr", "") or str(failure)
    raise FFmpegError(f"FFmpeg failed after {retries + 1} attempts: {details[-2000:]}")


def validate_video(path: Path, ffprobe: str | None, ffmpeg: str, timeout_seconds: int) -> None:
    if not path.exists() or path.stat().st_size < 1024:
        raise FFmpegError(f"Video was not created or is too small: {path}")
    if ffprobe:
        result = subprocess.run(
            [ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_type,width,height", "-of", "csv=p=0", path.name],
            cwd=path.parent, check=True, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=timeout_seconds,
        )
        actual = result.stdout.strip().split(",")
        if len(actual) < 3 or actual[-2:] != ["1080", "1920"]:
            raise FFmpegError(f"Unexpected output stream: {result.stdout.strip()}")
        return
    # imageio-ffmpeg distributes ffmpeg but not ffprobe. Decode one frame and inspect its stream line.
    result = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", path.name, "-frames:v", "1", "-f", "null", "-"], cwd=path.parent,
        check=True, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=timeout_seconds,
    )
    if not re.search(r"Video:.*?1080x1920", result.stderr):
        raise FFmpegError(f"Fallback validation could not confirm 1080x1920 stream: {result.stderr[-1000:]}")
    LOG.info("Validated MP4 decodability and 1080x1920 dimensions with FFmpeg fallback")
