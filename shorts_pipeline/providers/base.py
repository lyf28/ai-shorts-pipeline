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


class ImageProvider(ABC):
    """Provider contract for one still image asset per scene."""

    @property
    @abstractmethod
    def file_extension(self) -> str: ...

    @abstractmethod
    def generate_image(self, scene: Scene, destination: Path) -> Path: ...


class TTSProvider(ABC):
    """Provider contract for narration audio."""

    @abstractmethod
    def synthesize(self, text: str, duration_seconds: float, destination: Path) -> Path: ...
