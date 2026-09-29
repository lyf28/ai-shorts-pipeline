from __future__ import annotations

import base64
import mimetypes
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.request import urlopen

from shorts_pipeline.models import Scene
from shorts_pipeline.providers.base import VideoProvider


class RunwayVideoProviderError(RuntimeError):
    """Raised when a Runway image-to-video task cannot return a usable MP4."""


def download_file(url: str, destination: Path, timeout_seconds: int) -> None:
    with urlopen(url, timeout=timeout_seconds) as response:
        destination.write_bytes(response.read())


class RunwayVideoProvider(VideoProvider):
    """Generate one MP4 through Runway's asynchronous image-to-video API."""

    POLL_INTERVAL_SECONDS = 5.0

    @property
    def file_extension(self) -> str:
        return ".mp4"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: int = 180,
        client: Any | None = None,
        downloader: Callable[[str, Path, int], None] = download_file,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        if not api_key:
            raise ValueError("Runway video provider requires RUNWAY_API_KEY.")
        if not model.strip():
            raise ValueError("Runway video provider requires a non-empty RUNWAY_VIDEO_MODEL.")
        self.model = model.strip()
        self.timeout_seconds = timeout_seconds
        self._downloader = downloader
        self._clock = clock
        self._sleeper = sleeper
        if client is None:
            try:
                from runwayml import RunwayML
            except ImportError as error:
                raise RunwayVideoProviderError("Runway SDK is not installed. Run `pip install -r requirements.txt`.") from error
            client = RunwayML(api_key=api_key, timeout=timeout_seconds)
        self._client = client

    def generate_from_image(
        self,
        scene: Scene,
        image: Path,
        motion_prompt: str,
        duration_seconds: float,
        destination: Path,
    ) -> Path:
        if destination.suffix.lower() != self.file_extension:
            raise ValueError(f"Runway video destination must end in {self.file_extension}: {destination}")
        if duration_seconds <= 0:
            raise ValueError("Runway video duration must be greater than zero")
        if not motion_prompt.strip():
            raise ValueError("Runway video generation requires a non-empty motion prompt")
        try:
            task = self._client.image_to_video.create(
                model=self.model,
                prompt_image=self._image_data_uri(image),
                prompt_text=motion_prompt,
                ratio="720:1280",
                duration=duration_seconds,
            )
            task_id = getattr(task, "id", None)
            if not isinstance(task_id, str) or not task_id:
                raise RunwayVideoProviderError("Runway did not return an image-to-video task ID.")
            completed = self._poll_task(task_id)
            output = getattr(completed, "output", None)
            url = output[0] if isinstance(output, list) and output else None
            if not isinstance(url, str) or not url:
                raise RunwayVideoProviderError(f"Runway task {task_id} completed without a video URL.")
            destination.parent.mkdir(parents=True, exist_ok=True)
            self._downloader(url, destination, self.timeout_seconds)
        except RunwayVideoProviderError:
            raise
        except Exception as error:
            raise RunwayVideoProviderError(f"Runway video generation failed for scene {scene.index}: {error}") from error
        self._validate_mp4(destination)
        return destination

    def _poll_task(self, task_id: str) -> Any:
        deadline = self._clock() + self.timeout_seconds
        while True:
            task = self._client.tasks.retrieve(task_id)
            status = str(getattr(task, "status", "")).upper()
            if status == "SUCCEEDED":
                return task
            if status in {"FAILED", "CANCELED"}:
                raise RunwayVideoProviderError(f"Runway task {task_id} ended with status {status}.")
            remaining = deadline - self._clock()
            if remaining <= 0:
                raise RunwayVideoProviderError(f"Runway task {task_id} timed out after {self.timeout_seconds} seconds.")
            self._sleeper(min(self.POLL_INTERVAL_SECONDS, remaining))

    @staticmethod
    def _image_data_uri(image: Path) -> str:
        if not image.is_file():
            raise RunwayVideoProviderError(f"Runway start-frame image does not exist: {image}")
        mime_type, _ = mimetypes.guess_type(str(image))
        if mime_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise RunwayVideoProviderError(f"Runway start-frame image must be PNG, JPEG, or WebP: {image}")
        encoded = base64.b64encode(image.read_bytes()).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"

    @staticmethod
    def _validate_mp4(destination: Path) -> None:
        if not destination.is_file() or destination.stat().st_size < 12:
            raise RunwayVideoProviderError("Runway video download contained no MP4 data.")
        if destination.read_bytes()[:8][4:8] != b"ftyp":
            raise RunwayVideoProviderError("Runway video download was not an MP4 file.")
