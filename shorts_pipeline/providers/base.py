from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from shorts_pipeline.models import Scene


class LLMProvider(ABC):
    """Provider contract for creative text generation."""

    @abstractmethod
    def generate_idea(self, topic: str | None = None) -> str: ...

    @abstractmethod
    def generate_script(self, idea: str) -> str: ...


class VideoProvider(ABC):
    """Provider contract for a visual asset per scene."""

    @abstractmethod
    def generate_visual(self, scene: Scene, destination: Path) -> Path: ...


class TTSProvider(ABC):
    """Provider contract for narration audio."""

    @abstractmethod
    def synthesize(self, text: str, duration_seconds: float, destination: Path) -> Path: ...
