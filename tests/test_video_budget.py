import unittest

from shorts_pipeline.media_strategy import select_video_candidates
from shorts_pipeline.storyboard import build_storyboard
from shorts_pipeline.video_budget import VideoBudget, apply_video_budget, default_cost_per_second, estimate_video_cost


class VideoBudgetTests(unittest.TestCase):
    def setUp(self) -> None:
        storyboard = build_storyboard("Idea", "One. Two. Three. Four. Five. Six.")
        self.candidates = select_video_candidates(storyboard)

    def test_estimates_configurable_model_cost(self) -> None:
        self.assertEqual(default_cost_per_second("gen4_turbo"), 0.05)
        self.assertEqual(estimate_video_cost(12, 0.05), 0.6)

    def test_selects_three_high_value_clips_with_default_budget(self) -> None:
        plan = apply_video_budget(self.candidates, VideoBudget("gen4_turbo", 4, 12, 0.75, 0.05))

        self.assertEqual([candidate.scene.index for candidate in plan.video_candidates], [1, 6, 4])
        self.assertEqual(plan.total_video_seconds, 12)
        self.assertEqual(plan.estimated_cost_usd, 0.6)
        self.assertEqual(plan.image_candidates, [])

    def test_downgrades_lowest_priority_scenes_when_seconds_or_cost_are_limited(self) -> None:
        seconds_limited = apply_video_budget(self.candidates, VideoBudget("gen4_turbo", 4, 8, 0.75, 0.05))
        cost_limited = apply_video_budget(self.candidates, VideoBudget("gen4_turbo", 4, 12, 0.21, 0.05))

        self.assertEqual([candidate.scene.index for candidate in seconds_limited.video_candidates], [1, 6])
        self.assertEqual([candidate.scene.index for candidate in seconds_limited.image_candidates], [4])
        self.assertEqual([candidate.scene.index for candidate in cost_limited.video_candidates], [1])
        self.assertEqual([candidate.scene.index for candidate in cost_limited.image_candidates], [6, 4])
