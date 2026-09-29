from __future__ import annotations

import base64
import binascii
from pathlib import Path
from typing import Any

from shorts_pipeline.image_prompts import build_image_prompt
from shorts_pipeline.models import Scene
from shorts_pipeline.providers.base import ImageProvider


class OpenAIImageProviderError(RuntimeError):
    """Raised when the OpenAI Images API cannot supply a usable scene image."""


class OpenAIImageProvider(ImageProvider):
    """Generate one portrait PNG per scene through the OpenAI Images API."""

    @property
    def file_extension(self) -> str:
        return ".png"

    def __init__(self, api_key: str, model: str, timeout_seconds: int = 180, client: Any | None = None) -> None:
        if not api_key:
            raise ValueError("OpenAI image provider requires OPENAI_API_KEY.")
        if not model.strip():
            raise ValueError("OpenAI image provider requires a non-empty OPENAI_IMAGE_MODEL.")
        self.model = model
        if client is None:
            try:
                from openai import OpenAI
            except ImportError as error:
                raise OpenAIImageProviderError("OpenAI SDK is not installed. Run `pip install -r requirements.txt`.") from error
            client = OpenAI(api_key=api_key, timeout=timeout_seconds)
        self._client = client

    def generate_image(self, scene: Scene, destination: Path) -> Path:
        if destination.suffix.lower() != self.file_extension:
            raise ValueError(f"OpenAI image destination must end in {self.file_extension}: {destination}")
        try:
            response = self._client.images.generate(
                model=self.model,
                prompt=build_image_prompt(scene),
                size="1024x1536",
                quality="low",
                output_format="png",
                n=1,
            )
        except Exception as error:
            raise OpenAIImageProviderError(f"OpenAI image generation failed for scene {scene.index}: {error}") from error
        data = getattr(response, "data", None)
        image = data[0] if isinstance(data, list) and data else None
        encoded = getattr(image, "b64_json", None)
        if not isinstance(encoded, str):
            raise OpenAIImageProviderError("OpenAI image response contained no base64 image data.")
        try:
            content = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as error:
            raise OpenAIImageProviderError("OpenAI image response contained invalid base64 data.") from error
        if not content.startswith(b"\x89PNG\r\n\x1a\n"):
            raise OpenAIImageProviderError("OpenAI image response was not a PNG image.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        return destination
