from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Scene:
    index: int
    narration: str
    visual_prompt: str
    duration_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Storyboard:
    title: str
    hook: str
    scenes: list[Scene]

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "hook": self.hook, "scenes": [scene.to_dict() for scene in self.scenes]}
