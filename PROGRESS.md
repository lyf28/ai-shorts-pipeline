# Progress

## Goal

Add configurable OpenAI text-to-speech while preserving the offline local pipeline and aligning scene timing to the rendered narration.

## Planned Commits

1. `chore: add tts provider configuration` - complete.
2. `feat: add openai tts provider` - complete.
3. `feat: align narration timing with scenes` - complete.
4. `test: add tts provider coverage` - complete.
5. `docs: document tts setup` - complete.

## Completed

- Previous goal: protected the original aggregate commit on the pushed `backup/pre-atomic-history-rewrite` branch.
- Previous goal: reconstructed the application as eight independently reviewable engineering commits, plus documentation.
- Previous goal: preserved local providers, SQLite persistence, FFmpeg composition, subtitles, validation, retry handling, logging, dry-run behavior, and automated coverage.
- Added configurable `OPENAI_API_KEY` and `OPENAI_MODEL` settings while keeping `LLM_PROVIDER=local` as the default.
- Added an OpenAI structured-output LLM adapter and explicit OpenAI provider selection.
- Added API-free coverage for OpenAI provider selection and structured-response handling.
- Documented the optional OpenAI LLM setup, model configuration, and explicit missing-key behavior.
- Added `IMAGE_PROVIDER` and `OPENAI_IMAGE_MODEL` configuration while retaining local defaults.
- Replaced the misnamed static visual provider contract with `ImageProvider`.
- Added an OpenAI Images API adapter and visual-prompt generation for portrait scene assets.
- Added deterministic FFmpeg Ken Burns motion for still-image scenes.
- Added API-free coverage for image provider selection, prompting, output handling, and failures.
- Documented OpenAI image setup, portrait scene assets, and FFmpeg motion behavior.
- Added configurable OpenAI TTS model and voice settings while keeping local TTS as the default.
- Added OpenAI Speech API narration provider with configurable model and voice, WAV validation, timeout, retry integration, and explicit provider selection.
- Aligned scene and subtitle durations to the measured WAV narration duration before FFmpeg composition.
- Added API-free TTS tests for provider selection, missing credentials, successful WAV handling, failed responses, and persisted timing alignment.
- Documented local and OpenAI TTS setup, configurable voice/model, WAV output, timing alignment, and AI voice disclosure.

## Verification

- Previous goal: `python -m unittest discover -s tests -v` - 6/6 passed.
- Previous goal: local dry run and full run created and validated a 24-second 1080x1920 H.264/AAC MP4 with burned-in subtitles.
- OpenAI missing-key CLI check: `LLM_PROVIDER=openai` without `OPENAI_API_KEY` exits with an actionable error.
- Full suite: `python -m unittest discover -s tests -v` - 13/13 passed without an OpenAI API request.
- Local regression: `python run.py --dry-run --topic "focus"` and `python run.py --topic "building better habits" --verbose` both passed; the latter created a validated 24-second 1080x1920 H.264/AAC MP4.
- Real OpenAI dry run was not run because `OPENAI_API_KEY` is not configured in this environment.
- OpenAI image missing-key CLI check: `IMAGE_PROVIDER=openai` without `OPENAI_API_KEY` exits with an actionable error.
- Full suite: `python -m unittest discover -s tests -v` - 20/20 passed without an OpenAI image request.
- Local regression: `python run.py --dry-run --topic "focus"` and `python run.py --topic "building better habits" --verbose` both passed; the latter created a validated 24-second 1080x1920 H.264/AAC MP4 with deterministic image motion.
- Real OpenAI image smoke test was not run because `OPENAI_API_KEY` is not configured in this environment.
- TTS configuration regression: `python -m unittest discover -s tests -v` - 20/20 passed without an OpenAI API request.
- TTS provider regression: `python -m compileall -q shorts_pipeline` and `python -m unittest discover -s tests -v` - 20/20 passed; `TTS_PROVIDER=openai` without a key exited with the expected actionable error.
- Narration timing regression: focused tests - 7/7 passed; local dry run passed and a full local run created a validated 24-second 1080x1920 MP4 with aligned subtitle timings.
- TTS coverage: `python -m unittest tests.test_openai_tts_provider -v` - 7/7 passed; full suite - 29/29 passed without an OpenAI API request.
- Final TTS regression: `python -m unittest discover -s tests -v` - 29/29 passed; `python run.py --dry-run --topic "focus"` passed. A real OpenAI TTS smoke test was not run because `OPENAI_API_KEY` is not configured.

## Current Issues

- None.

## Blockers

- None.

## Next Commit

- None; perform final history, working-tree, and remote verification.
