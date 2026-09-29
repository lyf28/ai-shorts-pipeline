import unittest

from shorts_pipeline.media_strategy import build_motion_prompt, select_video_candidates
from shorts_pipeline.storyboard import build_storyboard


class SceneMediaStrategyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.storyboard = build_storyboard("Idea", "One. Two. Three. Four. Five. Six.")

    def test_assigns_simple_roles_and_motion_metadata(self) -> None:
        scenes = self.storyboard.scenes

        self.assertEqual(scenes[0].scene_role, "hook")
        self.assertEqual(scenes[-1].scene_role, "payoff")
        self.assertTrue(scenes[0].motion_required)
        self.assertTrue(scenes[3].motion_required)
        self.assertTrue(scenes[-1].motion_required)
        self.assertGreater(scenes[0].importance, scenes[1].importance)

    def test_prioritizes_hook_escalation_and_payoff_for_video(self) -> None:
        candidates = select_video_candidates(self.storyboard)

        self.assertEqual([candidate.scene.index for candidate in candidates], [1, 6, 4])

    def test_motion_prompt_uses_existing_start_frame_and_motion_brief(self) -> None:
        prompt = build_motion_prompt(self.storyboard.scenes[0])

        for label in ("existing start frame", "Subject movement:", "Camera movement:", "Environmental motion:", "Emotional beat:"):
            self.assertIn(label, prompt)
        self.assertNotIn(self.storyboard.scenes[0].narration, prompt)
