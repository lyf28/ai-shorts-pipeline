# Progress

## Goal

Add a configurable OpenAI LLM provider for idea and short-script generation while preserving the offline local provider as the default development mode.

## Planned Commits

1. `chore: add openai llm configuration` - complete.
2. `feat: add openai llm provider` - complete.
3. `test: add openai llm provider coverage` - complete.
4. `docs: document openai llm setup` - complete.

## Completed

- Previous goal: protected the original aggregate commit on the pushed `backup/pre-atomic-history-rewrite` branch.
- Previous goal: reconstructed the application as eight independently reviewable engineering commits, plus documentation.
- Previous goal: preserved local providers, SQLite persistence, FFmpeg composition, subtitles, validation, retry handling, logging, dry-run behavior, and automated coverage.
- Added configurable `OPENAI_API_KEY` and `OPENAI_MODEL` settings while keeping `LLM_PROVIDER=local` as the default.
- Added an OpenAI structured-output LLM adapter and explicit OpenAI provider selection.
- Added API-free coverage for OpenAI provider selection and structured-response handling.
- Documented the optional OpenAI LLM setup, model configuration, and explicit missing-key behavior.

## Verification

- Previous goal: `python -m unittest discover -s tests -v` - 6/6 passed.
- Previous goal: local dry run and full run created and validated a 24-second 1080x1920 H.264/AAC MP4 with burned-in subtitles.
- OpenAI missing-key CLI check: `LLM_PROVIDER=openai` without `OPENAI_API_KEY` exits with an actionable error.
- Full suite: `python -m unittest discover -s tests -v` - 13/13 passed without an OpenAI API request.
- Local regression: `python run.py --dry-run --topic "focus"` and `python run.py --topic "building better habits" --verbose` both passed; the latter created a validated 24-second 1080x1920 H.264/AAC MP4.
- Real OpenAI dry run was not run because `OPENAI_API_KEY` is not configured in this environment.

## Current Issues

- None.

## Blockers

- None.

## Next Commit

- None; perform final history, working-tree, and remote verification.
