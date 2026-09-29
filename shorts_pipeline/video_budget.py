from __future__ import annotations

from dataclasses import dataclass

from shorts_pipeline.media_strategy import VideoCandidate


@dataclass(frozen=True)
class VideoModelPricing:
    model: str
    estimated_cost_per_second_usd: float


VIDEO_MODEL_PRICING = {
    "gen4_turbo": VideoModelPricing("gen4_turbo", 0.05),
}
DEFAULT_VIDEO_COST_PER_SECOND_USD = 0.05


@dataclass(frozen=True)
class VideoBudget:
    model: str
    clip_duration_seconds: float
    max_video_seconds: float
    max_cost_usd: float
    estimated_cost_per_second_usd: float


@dataclass(frozen=True)
class VideoBudgetPlan:
    video_candidates: list[VideoCandidate]
    image_candidates: list[VideoCandidate]
    total_video_seconds: float
    estimated_cost_usd: float


def default_cost_per_second(model: str) -> float:
    pricing = VIDEO_MODEL_PRICING.get(model)
    return pricing.estimated_cost_per_second_usd if pricing else DEFAULT_VIDEO_COST_PER_SECOND_USD


def estimate_video_cost(seconds: float, cost_per_second_usd: float) -> float:
    if seconds < 0 or cost_per_second_usd < 0:
        raise ValueError("Video seconds and cost per second must not be negative")
    return round(seconds * cost_per_second_usd, 4)


def apply_video_budget(candidates: list[VideoCandidate], budget: VideoBudget) -> VideoBudgetPlan:
    """Keep high-priority video candidates only while both per-run limits allow them."""
    if budget.clip_duration_seconds <= 0:
        raise ValueError("Video clip duration must be greater than zero")
    if budget.max_video_seconds < 0 or budget.max_cost_usd < 0 or budget.estimated_cost_per_second_usd < 0:
        raise ValueError("Video budget values must not be negative")
    selected: list[VideoCandidate] = []
    fallback: list[VideoCandidate] = []
    total_seconds = 0.0
    for candidate in candidates:
        next_seconds = total_seconds + budget.clip_duration_seconds
        next_cost = estimate_video_cost(next_seconds, budget.estimated_cost_per_second_usd)
        if next_seconds <= budget.max_video_seconds and next_cost <= budget.max_cost_usd:
            selected.append(candidate)
            total_seconds = next_seconds
        else:
            fallback.append(candidate)
    return VideoBudgetPlan(
        video_candidates=selected,
        image_candidates=fallback,
        total_video_seconds=total_seconds,
        estimated_cost_usd=estimate_video_cost(total_seconds, budget.estimated_cost_per_second_usd),
    )
