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
    scenes = [
        Scene(
            index=i + 1,
            narration=chunk,
            visual_prompt=f"Vertical cinematic abstract illustration for: {chunk}",
            duration_seconds=duration,
            scene_role="hook" if i == 0 else "payoff" if i == len(chunks) - 1 else "development",
            importance=3 if i in {0, len(chunks) - 1} else 2 if i == len(chunks) // 2 else 1,
            motion_required=i in {0, len(chunks) // 2, len(chunks) - 1},
        )
        for i, chunk in enumerate(chunks)
    ]
    return Storyboard(title=idea[:80], hook=chunks[0], scenes=scenes)


def retime_storyboard(storyboard: Storyboard, total_seconds: float) -> Storyboard:
    """Allocate actual narration time proportionally to the spoken words in each scene."""
    if total_seconds <= 0:
        raise ValueError("Narration duration must be greater than zero")
    weights = [max(1, len(scene.narration.split())) for scene in storyboard.scenes]
    total_weight = sum(weights)
    durations = [round(total_seconds * weight / total_weight, 3) for weight in weights]
    durations[-1] = round(total_seconds - sum(durations[:-1]), 3)
    if any(duration <= 0 for duration in durations):
        raise ValueError("Narration duration is too short to allocate to every scene")
    scenes = [
        Scene(scene.index, scene.narration, scene.visual_prompt, duration, scene.scene_role, scene.importance, scene.motion_required)
        for scene, duration in zip(storyboard.scenes, durations, strict=True)
    ]
    return Storyboard(title=storyboard.title, hook=storyboard.hook, scenes=scenes)


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
