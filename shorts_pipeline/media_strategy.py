from __future__ import annotations

from dataclasses import dataclass

from shorts_pipeline.models import Scene, Storyboard


ROLE_BEATS = {
    "hook": ("an immediate, attention-grabbing subject movement", "a quick controlled push-in", "a small visible motion that starts the story", "curiosity and momentum"),
    "development": ("a clear action that advances the scene", "a subtle lateral camera move", "gentle environmental movement", "steady progression"),
    "payoff": ("a decisive reveal or satisfying final action", "a controlled pull-back to reveal the result", "a visible reaction or settling motion", "a clear closing beat"),
}


@dataclass(frozen=True)
class VideoCandidate:
    scene: Scene
    motion_prompt: str


def build_motion_prompt(scene: Scene) -> str:
    """Describe motion against the existing image instead of recreating its static appearance."""
    subject, camera, environment, beat = ROLE_BEATS.get(scene.scene_role, ROLE_BEATS["development"])
    return (
        "Animate the existing start frame without changing its characters, wardrobe, style, or composition. "
        f"Subject movement: {subject}. Camera movement: {camera}. "
        f"Environmental motion: {environment}. Emotional beat: {beat}. "
        "Keep the portrait framing stable and leave space for subtitles."
    )


def select_video_candidates(storyboard: Storyboard) -> list[VideoCandidate]:
    """Return high-value motion scenes in deterministic priority order."""
    candidates = [VideoCandidate(scene, build_motion_prompt(scene)) for scene in storyboard.scenes if scene.motion_required]
    return sorted(candidates, key=lambda candidate: (-candidate.scene.importance, candidate.scene.index))
