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

The default `local` providers require no credentials and generate deterministic text, original abstract visual assets, and a local audio track. The completed MP4 is written to `output/`; run metadata is saved in `data/pipeline.sqlite3`.

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
3. `VideoProvider` creates one visual asset per scene; `TTSProvider` creates audio.
4. FFmpeg concatenates the scene visuals at 1080×1920, adds SRT subtitles, muxes audio, and creates MP4.
5. SQLite records idea, script, storyboard, prompts, generation status, output path, and error logs.

Providers are abstract base classes in `shorts_pipeline/providers/base.py`. The included local implementations make development reproducible. `OpenAILLMProvider` is available for remote idea and script generation; its key and model are read from the environment. Other remote adapters should follow the same pattern and must not put credentials in source.

The pipeline logs every phase, retries provider and FFmpeg work, uses subprocess timeouts, records failures in SQLite, and validates the produced file (with `ffprobe` when available).
