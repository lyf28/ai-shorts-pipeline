# AI Shorts Pipeline

An end-to-end, local-first Python MVP that turns a generated idea into a 24-second, 1080×1920 subtitled MP4. It intentionally has **no social-media upload integration**.

## Quick start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

The default `local` providers require no credentials and generate deterministic text, original abstract image assets, and a local audio track. The completed MP4 is written to `output/`; run metadata is saved in `data/pipeline.sqlite3`.

`imageio-ffmpeg` supplies FFmpeg when it is not installed on PATH. Alternatively set `FFMPEG_BIN` in `.env` to an existing executable. Set `FFPROBE_BIN` too for stream-dimension validation.

## Optional OpenAI LLM

`LLM_PROVIDER=local` is the default and remains fully offline. To generate the idea and 20â€“30 second script with OpenAI instead, install the requirements, copy `.env.example` to `.env`, and set:

```text
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

`OPENAI_MODEL` is configurable; choose a model that supports structured outputs. The provider uses the Responses API with strict JSON schemas for its idea and script fields, then passes the resulting text through the unchanged storyboard and media pipeline. Its prompts require an immediate hook, a simple visual premise, story progression, and a distinct payoff or closing beat rather than generic motivational filler.

When `LLM_PROVIDER=openai`, a missing `OPENAI_API_KEY` stops the pipeline with an actionable error. It does not silently fall back to local mode. Keep the key only in your environment or untracked `.env` file; never commit it.

## Optional OpenAI image generation

`IMAGE_PROVIDER=local` is the offline default. To generate one AI image for every storyboard scene, keep the same `OPENAI_API_KEY` above and set:

```text
IMAGE_PROVIDER=openai
OPENAI_IMAGE_MODEL=gpt-image-2.5-flare
```

`OPENAI_IMAGE_MODEL` is configurable. The OpenAI image provider calls the Images API once per scene and requests a `1024x1536` PNG at low quality; use a model available to your API account. Each output is converted by the existing FFmpeg pipeline into a 1080x1920 scene with deterministic Ken Burns-style zoom and pan, then concatenated with subtitles and audio. This stage generates still images only; it does not generate AI video.

Image prompts are separate visual briefs rather than raw narration. They cover a consistent subject and style, scene action, environment, mood, camera framing, lighting, and subtitle-safe 9:16 composition. The prompt builder is intentionally small so character bibles, style bibles, and reference images can be added later.

When `IMAGE_PROVIDER=openai`, a missing key stops the pipeline with an actionable error and never falls back to local images. OpenAI image generation may require organization verification; consult the official [OpenAI image generation guide](https://developers.openai.com/api/docs/guides/image-generation) for supported models and account requirements.

## Optional OpenAI TTS

`TTS_PROVIDER=local` remains the fully offline default and produces a deterministic WAV audio track. To synthesize the script with OpenAI instead, keep the same `OPENAI_API_KEY` and set:

```text
TTS_PROVIDER=openai
OPENAI_TTS_MODEL=gpt-4o-mini-tts
OPENAI_TTS_VOICE=alloy
```

Both `OPENAI_TTS_MODEL` and `OPENAI_TTS_VOICE` are configurable; select values available to your account. The provider requests WAV audio, validates that it contains frames, and uses the actual rendered narration duration to allocate scene and subtitle timings before FFmpeg composition. This avoids trimming narration to the original fixed 24-second estimate. The speech request asks for clear, natural, concise pacing suitable for short-form voiceover.

When `TTS_PROVIDER=openai`, a missing `OPENAI_API_KEY` stops the pipeline with an actionable error and never falls back to local audio. Keep credentials in the environment or untracked `.env` file. When sharing or publishing an output with an OpenAI-generated voice, clearly disclose that the voice is AI-generated, as required by the [OpenAI text-to-speech guide](https://developers.openai.com/api/docs/guides/text-to-speech).

## Optional Runway hybrid video

`VIDEO_PROVIDER=local` is the default, so the existing offline image-plus-Ken-Burns pipeline remains unchanged and requires no Runway account. To selectively animate high-value storyboard scenes with Runway, install the requirements, use a Runway Dev API key, and set:

```text
VIDEO_PROVIDER=runway
RUNWAY_API_KEY=your_runway_api_key_here
RUNWAY_VIDEO_MODEL=gen4_turbo
RUNWAY_VIDEO_DURATION_SECONDS=4
RUNWAY_VIDEO_COST_PER_SECOND_USD=0.05
MAX_VIDEO_SECONDS_PER_RUN=12
MAX_VIDEO_COST_PER_RUN_USD=0.75
```

The provider uses the official Runway Python SDK to submit an asynchronous image-to-video task, poll its status, and download the resulting MP4. It sends the existing scene image as a data-URI start frame, so use `IMAGE_PROVIDER=openai` (PNG output) for real Runway animation; Runway accepts PNG, JPEG, and WebP start frames. `RUNWAY_VIDEO_MODEL` is configurable and the default `gen4_turbo` is not embedded in pipeline logic. See the official [Runway API getting-started guide](https://docs.dev.runwayml.com/guides/using-the-api/) for account setup and supported model options.

The hybrid strategy marks the opening hook, a middle escalation, and the final payoff as video candidates. Before making any Runway request, it applies both video-seconds and USD limits, keeping higher-priority candidates and automatically retaining image motion for the rest. `RUNWAY_VIDEO_COST_PER_SECOND_USD` is an operator-provided estimate used only for this guardrail; review current pricing in the [Runway billing documentation](https://docs.dev.runwayml.com/usage/billing/) before production use.

If an individual Runway task fails or times out after the configured bounded retry count, only that scene falls back to its original image motion. In contrast, `VIDEO_PROVIDER=runway` with no `RUNWAY_API_KEY` fails immediately with an actionable configuration error. The pipeline records provider, model, requested/generated seconds, estimated costs, generated clip paths, and fallback reasons in the run's `media_json` SQLite field. It never stores API keys.

## Commands

```powershell
python run.py --topic "better sleep"
python run.py --dry-run
python -m unittest discover -s tests -v
```

`--dry-run` generates and saves the idea, script, storyboard, prompts, and status without creating image/audio/video media.

## Pipeline

1. `LLMProvider` creates an idea and 20–30 second script.
2. The script is split into six scenes and persisted as structured storyboard JSON.
3. `ImageProvider` creates one still image asset per scene; `TTSProvider` creates WAV narration and the storyboard is retimed to its measured duration.
4. When selected and within budget, `VideoProvider` turns only high-value image scenes into short MP4 clips; failed clips keep their image-motion fallback.
5. FFmpeg normalizes mixed clips and images at 1080×1920, adds SRT subtitles with aligned timings, muxes audio, and creates MP4.
6. SQLite records idea, script, storyboard, prompts, media cost/fallback metadata, generation status, output path, and error logs.

Providers are abstract base classes in `shorts_pipeline/providers/base.py`. The included local implementations make development reproducible. `OpenAILLMProvider` is available for remote idea and script generation, `OpenAIImageProvider` creates portrait PNG scene assets, `OpenAITTSProvider` creates WAV narration, and `RunwayVideoProvider` creates short image-to-video MP4 clips; all read their key and model settings from the environment. Other remote adapters should follow the same pattern and must not put credentials in source.

The pipeline logs every phase, retries provider and FFmpeg work, uses subprocess timeouts, records failures in SQLite, and validates the produced file (with `ffprobe` when available).
