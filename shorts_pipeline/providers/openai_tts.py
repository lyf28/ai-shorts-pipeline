from __future__ import annotations

import wave
from pathlib import Path
from typing import Any

from shorts_pipeline.providers.base import TTSProvider


class OpenAITTSProviderError(RuntimeError):
    """Raised when the OpenAI Speech API cannot supply usable narration audio."""


TTS_INSTRUCTIONS = """Speak as a clear, natural short-form narrator. Keep a concise, steady pace,
avoid long pauses, and do not sound overly dramatic."""


class OpenAITTSProvider(TTSProvider):
    """Generate WAV narration through the OpenAI Speech API."""

    def __init__(self, api_key: str, model: str, voice: str, timeout_seconds: int = 180, client: Any | None = None) -> None:
        if not api_key:
            raise ValueError("OpenAI TTS provider requires OPENAI_API_KEY.")
        if not model.strip():
            raise ValueError("OpenAI TTS provider requires a non-empty OPENAI_TTS_MODEL.")
        if not voice.strip():
            raise ValueError("OpenAI TTS provider requires a non-empty OPENAI_TTS_VOICE.")
        self.model = model.strip()
        self.voice = voice.strip()
        if client is None:
            try:
                from openai import OpenAI
            except ImportError as error:
                raise OpenAITTSProviderError("OpenAI SDK is not installed. Run `pip install -r requirements.txt`.") from error
            client = OpenAI(api_key=api_key, timeout=timeout_seconds)
        self._client = client

    def synthesize(self, text: str, duration_seconds: float, destination: Path) -> Path:
        del duration_seconds  # The provider reports an actual duration after it renders speech.
        if not text.strip():
            raise ValueError("OpenAI TTS requires non-empty narration text.")
        if destination.suffix.lower() != ".wav":
            raise ValueError(f"OpenAI TTS destination must end in .wav: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self._client.audio.speech.with_streaming_response.create(
                model=self.model,
                voice=self.voice,
                input=text,
                instructions=TTS_INSTRUCTIONS,
                response_format="wav",
            ) as response:
                response.stream_to_file(destination)
        except Exception as error:
            raise OpenAITTSProviderError(f"OpenAI TTS generation failed: {error}") from error
        self._validate_wav(destination)
        return destination

    @staticmethod
    def _validate_wav(destination: Path) -> None:
        if not destination.is_file() or destination.stat().st_size <= 44:
            raise OpenAITTSProviderError("OpenAI TTS response contained no audio data.")
        try:
            with wave.open(str(destination), "rb") as audio:
                if audio.getnframes() <= 0:
                    raise OpenAITTSProviderError("OpenAI TTS response contained no audio frames.")
        except (wave.Error, EOFError) as error:
            raise OpenAITTSProviderError("OpenAI TTS response was not a valid WAV file.") from error
