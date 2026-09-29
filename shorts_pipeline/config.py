from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


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
    video_provider: str
    tts_provider: str
    ffmpeg_bin: str | None
    ffprobe_bin: str | None
    timeout_seconds: int
    retries: int

    @classmethod
    def from_root(cls, root: Path) -> "Settings":
        load_dotenv(root / ".env")
        return cls(
            root=root,
            llm_provider=os.getenv("LLM_PROVIDER", "local"),
            video_provider=os.getenv("VIDEO_PROVIDER", "local"),
            tts_provider=os.getenv("TTS_PROVIDER", "local"),
            ffmpeg_bin=os.getenv("FFMPEG_BIN") or None,
            ffprobe_bin=os.getenv("FFPROBE_BIN") or None,
            timeout_seconds=int(os.getenv("PIPELINE_TIMEOUT_SECONDS", "180")),
            retries=int(os.getenv("PIPELINE_RETRIES", "2")),
        )
