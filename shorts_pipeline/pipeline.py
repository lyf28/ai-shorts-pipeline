from __future__ import annotations

import logging
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, TypeVar

from shorts_pipeline.config import Settings
from shorts_pipeline.ffmpeg import audio_duration, build_hybrid_video_command, render_video, resolve_ffmpeg, resolve_ffprobe, validate_video
from shorts_pipeline.media_strategy import select_video_candidates
from shorts_pipeline.models import Storyboard
from shorts_pipeline.image_prompts import build_image_prompt
from shorts_pipeline.providers import LocalImageProvider, LocalLLMProvider, LocalTTSProvider, OpenAIImageProvider, OpenAILLMProvider, OpenAITTSProvider, RunwayVideoProvider
from shorts_pipeline.providers.base import ImageProvider, LLMProvider, TTSProvider, VideoProvider
from shorts_pipeline.storage import RunStore
from shorts_pipeline.storyboard import build_storyboard, retime_storyboard, write_subtitles
from shorts_pipeline.video_budget import VideoBudget, apply_video_budget, estimate_video_cost

LOG = logging.getLogger(__name__)
T = TypeVar("T")


def retry(operation: Callable[[], T], attempts: int, label: str) -> T:
    error: Exception | None = None
    for index in range(1, attempts + 1):
        try:
            return operation()
        except Exception as caught:
            error = caught
            LOG.warning("%s failed on attempt %s/%s: %s", label, index, attempts, caught)
    assert error is not None
    raise error


def select_providers(settings: Settings) -> tuple[LLMProvider, ImageProvider, TTSProvider]:
    if settings.llm_provider == "local":
        llm: LLMProvider = LocalLLMProvider()
    elif settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("LLM_PROVIDER=openai requires OPENAI_API_KEY. Set it in your environment or .env before running the pipeline.")
        llm = OpenAILLMProvider(settings.openai_api_key, settings.openai_model, settings.timeout_seconds)
    else:
        raise ValueError("Unsupported LLM_PROVIDER. Use 'local' or 'openai'.")
    if settings.image_provider == "local":
        image: ImageProvider = LocalImageProvider()
    elif settings.image_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("IMAGE_PROVIDER=openai requires OPENAI_API_KEY. Set it in your environment or .env before running the pipeline.")
        image = OpenAIImageProvider(settings.openai_api_key, settings.openai_image_model, settings.timeout_seconds)
    else:
        raise ValueError("Unsupported IMAGE_PROVIDER. Use 'local' or 'openai'.")
    if settings.tts_provider == "local":
        tts: TTSProvider = LocalTTSProvider()
    elif settings.tts_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("TTS_PROVIDER=openai requires OPENAI_API_KEY. Set it in your environment or .env before running the pipeline.")
        tts = OpenAITTSProvider(
            settings.openai_api_key,
            settings.openai_tts_model,
            settings.openai_tts_voice,
            settings.timeout_seconds,
        )
    else:
        raise ValueError("Unsupported TTS_PROVIDER. Use 'local' or 'openai'.")
    return llm, image, tts


def select_video_provider(settings: Settings) -> VideoProvider | None:
    if settings.video_provider == "local":
        return None
    if settings.video_provider == "runway":
        if not settings.runway_api_key:
            raise ValueError("VIDEO_PROVIDER=runway requires RUNWAY_API_KEY. Set it in your environment or .env before running the pipeline.")
        return RunwayVideoProvider(settings.runway_api_key, settings.runway_video_model, settings.timeout_seconds)
    raise ValueError("Unsupported VIDEO_PROVIDER. Use 'local' or 'runway'.")


class Pipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.llm, self.image, self.tts = select_providers(settings)
        self.video = select_video_provider(settings)
        self.store = RunStore(settings.root / "data" / "pipeline.sqlite3")

    def run(self, topic: str | None = None, dry_run: bool = False) -> Path | None:
        run_id = self.store.create()
        work_dir = self.settings.root / "work" / f"run_{run_id}"
        work_dir.mkdir(parents=True, exist_ok=True)
        try:
            idea = retry(lambda: self.llm.generate_idea(topic), self.settings.retries + 1, "idea generation")
            script = retry(lambda: self.llm.generate_script(idea), self.settings.retries + 1, "script generation")
            storyboard = build_storyboard(idea, script)
            prompts = [build_image_prompt(scene) for scene in storyboard.scenes]
            self.store.update(run_id, idea=idea, script=script, storyboard_json=storyboard.to_dict(), prompts_json=prompts, generation_status="storyboard_ready")
            LOG.info("Run %s created %s scenes (%ss total)", run_id, len(storyboard.scenes), sum(s.duration_seconds for s in storyboard.scenes))
            if dry_run:
                self.store.update(run_id, generation_status="dry_run_complete")
                return None
            estimated_total = sum(scene.duration_seconds for scene in storyboard.scenes)
            audio = retry(lambda: self.tts.synthesize(script, estimated_total, work_dir / "narration.wav"), self.settings.retries + 1, "audio generation")
            actual_duration = audio_duration(audio)
            storyboard = retime_storyboard(storyboard, actual_duration)
            prompts = [build_image_prompt(scene) for scene in storyboard.scenes]
            self.store.update(run_id, storyboard_json=storyboard.to_dict(), prompts_json=prompts, generation_status="narration_ready")
            LOG.info("Run %s narration is %.2fs; scene timing was aligned to it", run_id, actual_duration)
            images = [retry(lambda scene=scene: self.image.generate_image(scene, work_dir / f"scene_{scene.index}{self.image.file_extension}"), self.settings.retries + 1, f"scene {scene.index} image") for scene in storyboard.scenes]
            media, media_metadata = self._generate_hybrid_media(storyboard, images, work_dir)
            self.store.update(run_id, media_json=media_metadata, generation_status="media_ready")
            subtitles = work_dir / "subtitles.srt"
            write_subtitles(storyboard, subtitles)
            output_dir = self.settings.root / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            output = output_dir / f"short_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}_{run_id}.mp4"
            render_output = work_dir / "render.mp4"
            ffmpeg = resolve_ffmpeg(self.settings.ffmpeg_bin)
            command = build_hybrid_video_command(ffmpeg, storyboard, media, audio, subtitles, render_output)
            self.store.update(run_id, generation_status="rendering")
            render_video(command, work_dir, self.settings.timeout_seconds, self.settings.retries)
            validate_video(render_output, resolve_ffprobe(self.settings.ffprobe_bin), ffmpeg, self.settings.timeout_seconds)
            shutil.move(str(render_output), str(output))
            self.store.update(run_id, generation_status="completed", output_path=str(output.resolve()))
            LOG.info("Run %s completed: %s", run_id, output)
            return output
        except Exception as error:
            LOG.exception("Run %s failed", run_id)
            self.store.update(run_id, generation_status="failed", error_logs=str(error))
            raise
        finally:
            self.store.close()

    def _generate_hybrid_media(self, storyboard: Storyboard, images: list[Path], work_dir: Path) -> tuple[list[Path], dict[str, object]]:
        media = list(images)
        metadata: dict[str, object] = {
            "provider": self.settings.video_provider,
            "model": self.settings.runway_video_model if self.video else None,
            "requested_video_scenes": 0,
            "requested_video_seconds": 0.0,
            "requested_estimated_cost_usd": 0.0,
            "generated_video_scenes": 0,
            "generated_video_seconds": 0.0,
            "generated_estimated_cost_usd": 0.0,
            "generated_clip_paths": [],
            "fallbacks": [],
        }
        if self.video is None:
            return media, metadata
        budget = VideoBudget(
            model=self.settings.runway_video_model,
            clip_duration_seconds=self.settings.runway_video_duration_seconds,
            max_video_seconds=self.settings.max_video_seconds_per_run,
            max_cost_usd=self.settings.max_video_cost_per_run_usd,
            estimated_cost_per_second_usd=self.settings.runway_video_cost_per_second_usd,
        )
        plan = apply_video_budget(select_video_candidates(storyboard), budget)
        metadata["requested_video_scenes"] = len(plan.video_candidates)
        metadata["requested_video_seconds"] = plan.total_video_seconds
        metadata["requested_estimated_cost_usd"] = plan.estimated_cost_usd
        fallbacks: list[dict[str, object]] = [{"scene_index": candidate.scene.index, "reason": "budget_limit"} for candidate in plan.image_candidates]
        generated_paths: list[str] = []
        generated_seconds = 0.0
        for candidate in plan.video_candidates:
            scene = candidate.scene
            try:
                video = retry(
                    lambda candidate=candidate: self.video.generate_from_image(
                        candidate.scene,
                        images[candidate.scene.index - 1],
                        candidate.motion_prompt,
                        self.settings.runway_video_duration_seconds,
                        work_dir / f"scene_{candidate.scene.index}{self.video.file_extension}",
                    ),
                    self.settings.retries + 1,
                    f"scene {scene.index} video",
                )
            except Exception as error:
                LOG.warning("Scene %s video generation fell back to image motion: %s", scene.index, error)
                fallbacks.append({"scene_index": scene.index, "reason": "generation_failed", "detail": str(error)})
                continue
            media[scene.index - 1] = video
            generated_paths.append(str(video.resolve()))
            generated_seconds += self.settings.runway_video_duration_seconds
        metadata["generated_video_scenes"] = len(generated_paths)
        metadata["generated_video_seconds"] = generated_seconds
        metadata["generated_estimated_cost_usd"] = estimate_video_cost(generated_seconds, self.settings.runway_video_cost_per_second_usd)
        metadata["generated_clip_paths"] = generated_paths
        metadata["fallbacks"] = fallbacks
        return media, metadata
