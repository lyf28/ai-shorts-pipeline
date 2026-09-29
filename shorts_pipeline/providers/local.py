from __future__ import annotations

import math
import wave
from pathlib import Path

from shorts_pipeline.models import Scene
from shorts_pipeline.providers.base import ImageProvider, LLMProvider, TTSProvider


class LocalLLMProvider(LLMProvider):
    """Deterministic offline provider useful for development and CI."""

    def generate_idea(self, topic: str | None = None) -> str:
        subject = topic or "everyday curiosity"
        return f"A fast, surprising micro-story about {subject}: why tiny habits compound."

    def generate_script(self, idea: str) -> str:
        return (
            "What if one tiny choice changed the shape of your whole week? "
            "Start with a single two-minute action. "
            "Done once, it feels invisible. "
            "Repeated tomorrow, it becomes a vote for the person you want to be. "
            "Small wins reduce friction, and momentum makes the next choice easier. "
            "Choose one tiny action today, then let consistency do the dramatic work."
        )


class LocalImageProvider(ImageProvider):
    """Creates original colourful PPM illustrations without external APIs."""

    PALETTES = ((20, 29, 74), (76, 29, 149), (8, 145, 178), (238, 108, 77), (255, 183, 3), (52, 211, 153))

    @property
    def file_extension(self) -> str:
        return ".ppm"

    def generate_image(self, scene: Scene, destination: Path) -> Path:
        width, height = 360, 640  # FFmpeg scales this to 1080x1920.
        base = self.PALETTES[(scene.index - 1) % len(self.PALETTES)]
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as image:
            image.write(f"P6\n{width} {height}\n255\n".encode("ascii"))
            for y in range(height):
                for x in range(width):
                    glow = int(60 * max(0, 1 - math.hypot(x - width / 2, y - height * .42) / (height * .65)))
                    stripe = 24 if ((x // 24 + y // 36 + scene.index) % 5 == 0) else 0
                    image.write(bytes(min(255, channel + glow + stripe) for channel in base))
        return destination


class LocalTTSProvider(TTSProvider):
    """Creates a quiet tonal narration placeholder; swap for a cloud TTS provider later."""

    def synthesize(self, text: str, duration_seconds: float, destination: Path) -> Path:
        sample_rate = 22050
        frames = int(duration_seconds * sample_rate)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(destination), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(sample_rate)
            for i in range(frames):
                value = int(420 * math.sin(2 * math.pi * (180 + (i // sample_rate % 2) * 35) * i / sample_rate))
                audio.writeframesraw(value.to_bytes(2, "little", signed=True))
        return destination
