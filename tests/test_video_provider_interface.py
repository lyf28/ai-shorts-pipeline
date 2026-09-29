import tempfile
import unittest
from pathlib import Path

from shorts_pipeline.models import Scene
from shorts_pipeline.providers import VideoProvider


class StubVideoProvider(VideoProvider):
    @property
    def file_extension(self) -> str:
        return ".mp4"

    def generate_from_image(
        self,
        scene: Scene,
        image: Path,
        motion_prompt: str,
        duration_seconds: float,
        destination: Path,
    ) -> Path:
        del scene, image, motion_prompt, duration_seconds
        destination.write_bytes(b"stub video")
        return destination


class VideoProviderInterfaceTests(unittest.TestCase):
    def test_supports_image_to_video_generation_contract(self) -> None:
        scene = Scene(1, "A hook.", "visual", 4)
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "scene.mp4"
            result = StubVideoProvider().generate_from_image(scene, Path(directory) / "scene.png", "Camera gently pushes in.", 4, destination)

        self.assertEqual(result, destination)
        self.assertEqual(StubVideoProvider().file_extension, ".mp4")
