from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from shorts_pipeline.video_budget import default_cost_per_second


def load_dotenv(path: Path) -> None:
    """Tiny .env reader so an offline run has no bootstrap dependency."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class Settings:
    root: Path
    llm_provider: str
    image_provider: str
    tts_provider: str
    video_provider: str
    openai_api_key: str | None
    openai_model: str
    openai_image_model: str
    openai_tts_model: str
    openai_tts_voice: str
    runway_api_key: str | None
    runway_video_model: str
    runway_video_duration_seconds: float
    runway_video_cost_per_second_usd: float
    max_video_seconds_per_run: float
    max_video_cost_per_run_usd: float
    ffmpeg_bin: str | None
    ffprobe_bin: str | None
    timeout_seconds: int
    retries: int

    @classmethod
    def from_root(cls, root: Path) -> "Settings":
        load_dotenv(root / ".env")
        runway_video_model = os.getenv("RUNWAY_VIDEO_MODEL", "gen4_turbo")
        return cls(
            root=root,
            llm_provider=os.getenv("LLM_PROVIDER", "local"),
            image_provider=os.getenv("IMAGE_PROVIDER", "local"),
            tts_provider=os.getenv("TTS_PROVIDER", "local"),
            video_provider=os.getenv("VIDEO_PROVIDER", "local"),
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_image_model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2.5-flare"),
            openai_tts_model=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
            openai_tts_voice=os.getenv("OPENAI_TTS_VOICE", "alloy"),
            runway_api_key=os.getenv("RUNWAY_API_KEY") or None,
            runway_video_model=runway_video_model,
            runway_video_duration_seconds=float(os.getenv("RUNWAY_VIDEO_DURATION_SECONDS", "4")),
            runway_video_cost_per_second_usd=float(os.getenv("RUNWAY_VIDEO_COST_PER_SECOND_USD", str(default_cost_per_second(runway_video_model)))),
            max_video_seconds_per_run=float(os.getenv("MAX_VIDEO_SECONDS_PER_RUN", "12")),
            max_video_cost_per_run_usd=float(os.getenv("MAX_VIDEO_COST_PER_RUN_USD", "0.75")),
            ffmpeg_bin=os.getenv("FFMPEG_BIN") or None,
            ffprobe_bin=os.getenv("FFPROBE_BIN") or None,
            timeout_seconds=int(os.getenv("PIPELINE_TIMEOUT_SECONDS", "180")),
            retries=int(os.getenv("PIPELINE_RETRIES", "2")),
        )
