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

Providers are abstract base classes in `shorts_pipeline/providers/base.py`. The included local implementations make development reproducible. To use a remote model, add an adapter that implements the relevant interface, read its key from the environment, and register it in `select_providers`; do not put credentials in source.

The pipeline logs every phase, retries provider and FFmpeg work, uses subprocess timeouts, records failures in SQLite, and validates the produced file (with `ffprobe` when available).
