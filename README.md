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
4. FFmpeg applies deterministic zoom/pan motion, concatenates the scene images at 1080×1920, adds SRT subtitles with the aligned timings, muxes audio, and creates MP4.
5. SQLite records idea, script, storyboard, prompts, generation status, output path, and error logs.

Providers are abstract base classes in `shorts_pipeline/providers/base.py`. The included local implementations make development reproducible. `OpenAILLMProvider` is available for remote idea and script generation, `OpenAIImageProvider` creates portrait PNG scene assets, and `OpenAITTSProvider` creates WAV narration; all read their key and model settings from the environment. Other remote adapters should follow the same pattern and must not put credentials in source.

The pipeline logs every phase, retries provider and FFmpeg work, uses subprocess timeouts, records failures in SQLite, and validates the produced file (with `ffprobe` when available).
