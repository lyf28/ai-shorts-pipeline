from __future__ import annotations

import re

from shorts_pipeline.models import Scene


_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "if", "in", "is", "it",
    "of", "on", "or", "the", "this", "that", "to", "with", "your", "you", "what", "when", "why",
}
_FRAMING = ("medium close-up", "wide establishing shot", "overhead detail shot", "dynamic medium shot", "close-up")


def scene_concept(narration: str) -> str:
    """Distill narration into visual keywords instead of sending it verbatim to an image model."""
    words = re.findall(r"[A-Za-z0-9']+", narration.lower())
    keywords = [word for word in words if len(word) > 2 and word not in _STOP_WORDS]
    return ", ".join(keywords[:8]) or "a clear moment of personal progress"


def build_image_prompt(scene: Scene) -> str:
    """Create a consistent visual brief; future callers may add character or style bibles here."""
    return (
        "Create a polished cinematic illustration for a vertical short-form video. "
        "Subject: the same focused young adult creator in a cobalt jacket and round glasses, "
        "kept visually consistent across every scene in this video. "
        f"Action: visually interpret this scene concept: {scene_concept(scene.narration)}. "
        "Environment: a clean, modern setting with a few meaningful visual props. "
        "Mood: curious, energetic, and satisfying. "
        f"Camera framing: {_FRAMING[(scene.index - 1) % len(_FRAMING)]}. "
        "Lighting: soft cinematic key light with vivid cobalt and amber accents. "
        "Visual consistency: editorial illustration, crisp shapes, subtle texture, no text or logos. "
        "Vertical short-form composition: portrait 9:16, subject clearly readable, "
        "with an uncluttered lower third reserved for subtitles."
    )
