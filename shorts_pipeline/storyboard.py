from __future__ import annotations

import re
from pathlib import Path

from shorts_pipeline.models import Scene, Storyboard


def split_script(script: str, scene_count: int = 6) -> list[str]:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", script.strip()) if part.strip()]
    if not sentences:
        raise ValueError("Script cannot be empty")
    while len(sentences) < scene_count:
        longest = max(range(len(sentences)), key=lambda i: len(sentences[i]))
        words = sentences.pop(longest).split()
        pivot = max(1, len(words) // 2)
        sentences[longest:longest] = [" ".join(words[:pivot]), " ".join(words[pivot:])]
    if len(sentences) > scene_count:
        sentences = [*sentences[: scene_count - 1], " ".join(sentences[scene_count - 1 :])]
    return sentences


def build_storyboard(idea: str, script: str, scene_count: int = 6, total_seconds: float = 24) -> Storyboard:
    chunks = split_script(script, scene_count)
    duration = round(total_seconds / len(chunks), 2)
    scenes = [Scene(i + 1, chunk, f"Vertical cinematic abstract illustration for: {chunk}", duration) for i, chunk in enumerate(chunks)]
    return Storyboard(title=idea[:80], hook=chunks[0], scenes=scenes)


def srt_timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    whole_seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{whole_seconds:02},{milliseconds:03}"


def write_subtitles(storyboard: Storyboard, path: Path) -> None:
    position = 0.0
    entries: list[str] = []
    for scene in storyboard.scenes:
        entries.append(f"{scene.index}\n{srt_timestamp(position)} --> {srt_timestamp(position + scene.duration_seconds)}\n{scene.narration}\n")
        position += scene.duration_seconds
    path.write_text("\n".join(entries), encoding="utf-8")
