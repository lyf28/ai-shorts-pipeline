# AGENTS.md

## Project Overview

This repository contains an autonomous short-form AI video generation pipeline.

The system is intended to automatically:

1. Generate a short-form video concept.
2. Generate a short script.
3. Convert the script into structured scenes.
4. Generate a storyboard.
5. Generate visual assets for each scene.
6. Generate optional narration, sound effects, or background audio.
7. Assemble the assets into a vertical short-form video.
8. Add subtitles or captions.
9. Perform automated quality checks.
10. Save generation metadata and results.

The long-term goal is to support automated publishing, analytics collection, performance feedback, and content strategy optimization.

The current priority is to build a reliable local end-to-end MVP first.

---

# Core Objective

The primary MVP objective is:

```bash
python run.py
```

must successfully produce a valid vertical short-form MP4 file inside:

```text
output/
```

The MVP should work even when real external AI providers are unavailable by using mock or dry-run providers.

A feature is not considered complete merely because code exists.

It must be tested and verified through real execution whenever possible.

---

# Development Philosophy

Prioritize:

1. End-to-end functionality
2. Reliability
3. Testability
4. Modularity
5. Clear failure behavior
6. Low manual intervention
7. Simple architecture before complex architecture

Do not overengineer the MVP.

Prefer a straightforward Python pipeline over unnecessary multi-agent systems.

Build the simplest architecture that can later support additional providers, analytics, publishing, and automated optimization.

---

# Autonomous Development Loop

Codex must continuously follow this workflow:

```text
INSPECT
→ PLAN
→ IMPLEMENT
→ TEST
→ INSPECT RESULTS
→ FIX
→ RETEST
→ REVIEW DIFF
→ COMMIT
→ PUSH
→ CONTINUE
```

Do not stop after writing code.

Do not assume an implementation works without running it.

Do not stop simply because one milestone was committed and pushed.

Continue until the overall project goal is complete or a genuine external blocker requires user intervention.

---

# When Codex May Stop

Codex may stop only when one of the following is true:

## A. The goal is fully complete

All required Definition of Done criteria have been verified.

## B. A blocker requires user action

Examples:

- API credentials are missing.
- OAuth authorization is required.
- GitHub authentication is unavailable.
- Repository permissions prevent pushing.
- A paid external service requires the user to make a purchasing decision.
- An external provider requires manual approval.

## C. Progress is impossible after reasonable attempts

If repeated attempts fail, clearly document:

- what failed;
- what was attempted;
- relevant errors;
- why additional autonomous work is unlikely to help;
- what specific user action is required.

Ordinary programming errors are not blockers.

The following should normally be solved autonomously:

- failing tests;
- dependency issues;
- path problems;
- Python errors;
- FFmpeg errors;
- incorrect imports;
- malformed configuration;
- provider abstraction bugs;
- serialization errors;
- retry behavior;
- test failures;
- formatting problems.

---

# Repository Inspection

Before making significant changes, inspect the repository.

At minimum, check:

```bash
git status
git branch --show-current
git remote -v
```

Also inspect:

- existing source files;
- tests;
- project configuration;
- README;
- AGENTS.md;
- PROGRESS.md;
- recent Git history when relevant.

Do not overwrite existing architecture without first understanding it.

---

# Project Architecture

Keep major concerns separated.

Suggested logical components include:

```text
ideation
scripting
storyboard
media generation
audio generation
composition
subtitles
quality validation
persistence
configuration
scheduling
publishing
analytics
```

The exact file structure may evolve, but responsibilities should remain cleanly separated.

Avoid creating unnecessary layers or abstractions.

---

# Provider Architecture

External AI services must be replaceable.

Use provider interfaces or equivalent abstractions for services such as:

```text
LLMProvider
ImageProvider
VideoProvider
TTSProvider
AudioProvider
```

Application logic should not depend directly on a single vendor whenever practical.

Example implementations may include:

```text
MockVideoProvider
OpenAIVideoProvider
MockTTSProvider
OpenAITTSProvider
```

Provider-specific API behavior must remain isolated from the rest of the pipeline.

---

# Mock and Dry-Run Support

External API availability must not block local development.

If an external API key is unavailable:

1. Do not stop the entire project.
2. Implement the provider interface.
3. Create a mock or dry-run implementation.
4. Exercise the rest of the pipeline end-to-end.
5. Document which credential will eventually be needed.

The local pipeline should be testable without spending money or calling paid services.

---

# MVP Scope

The first MVP should support:

- idea generation;
- script generation;
- storyboard creation;
- scene representation;
- pluggable media providers;
- optional audio or narration;
- FFmpeg-based composition;
- subtitles;
- metadata persistence;
- structured logging;
- retry behavior;
- error handling;
- dry-run execution;
- local end-to-end testing.

The MVP should generate a vertical video suitable for short-form platforms.

Preferred output dimensions:

```text
1080x1920
```

---

# Out of Scope for Initial MVP

Do not implement these until the local video-generation pipeline works reliably:

- automatic YouTube publishing;
- automatic TikTok publishing;
- automatic Instagram publishing;
- automatic public posting;
- trend scraping at scale;
- automated revenue optimization;
- autonomous content strategy agents;
- complex distributed orchestration;
- Airflow or Kubernetes unless genuinely necessary.

Build the foundation first.

---

# Python Standards

Use modern Python practices.

Prefer:

- type hints;
- small focused functions;
- dataclasses or structured models where useful;
- clear module boundaries;
- readable naming;
- explicit exception handling.

Avoid:

- unnecessary global state;
- giant functions;
- deeply nested logic;
- silent exception swallowing;
- unnecessary framework dependencies.

---

# Configuration

Runtime configuration should come from:

- environment variables;
- `.env`;
- structured config files when appropriate.

Do not hard-code:

- API keys;
- access tokens;
- OAuth credentials;
- secrets;
- account identifiers that should be configurable.

Provide:

```text
.env.example
```

with placeholder values only.

Never place real secrets inside `.env.example`.

---

# Secrets Policy

Never commit secrets.

Examples include:

- API keys;
- bearer tokens;
- passwords;
- OAuth refresh tokens;
- service account keys;
- cookies;
- private certificates;
- SSH private keys.

Before every commit, inspect changes for accidental secret exposure.

If a secret is discovered in tracked content:

1. remove it from tracked files;
2. replace it with environment-based configuration;
3. do not expose the secret in logs or commit messages;
4. notify the user if credential rotation may be required.

---

# Persistence

Use SQLite for the MVP unless there is a strong reason to use something else.

Store useful generation metadata such as:

- generation ID;
- created timestamp;
- idea;
- script;
- storyboard;
- prompts;
- provider names;
- generation status;
- retries;
- errors;
- output file paths;
- duration;
- quality-check results.

Do not store sensitive API credentials in SQLite.

---

# Logging

Use structured and useful logging.

Logs should help diagnose:

- which pipeline stage failed;
- which generation ID failed;
- which provider was involved;
- retry count;
- relevant error information;
- output file location.

Do not log secrets.

Avoid excessive noisy logs.

---

# Error Handling

External service calls should support:

- timeout;
- retry;
- clear error messages;
- bounded retry count;
- structured logging.

Avoid infinite retries.

A failed upstream stage must not silently produce invalid downstream output.

For recoverable failures:

```text
FAIL
→ RETRY
→ VALIDATE
→ CONTINUE
```

For unrecoverable failures:

- mark the generation appropriately;
- preserve useful diagnostics;
- exit cleanly.

---

# FFmpeg

FFmpeg should be used for deterministic media composition where appropriate.

The pipeline should handle:

- vertical resolution;
- frame rate consistency;
- clip concatenation;
- audio tracks;
- subtitle overlays;
- duration normalization.

FFmpeg failures must be surfaced clearly.

Do not ignore non-zero FFmpeg exit codes.

---

# Output Validation

Generated videos must be validated before being considered successful.

Use tools such as:

```bash
ffprobe
```

where available.

At minimum verify:

- file exists;
- file size is greater than zero;
- video stream exists;
- duration is greater than zero;
- dimensions are valid;
- output can be decoded;
- expected format is produced.

A file merely existing does not mean generation succeeded.

---

# Quality Gate

The pipeline should eventually support automated quality validation.

Initial checks may include:

- output exists;
- correct aspect ratio;
- acceptable duration;
- valid audio stream when expected;
- no missing scenes;
- no corrupt clips;
- subtitles are generated when required;
- no obvious blank output;
- no failed placeholder media in production mode.

Quality checks should return explicit pass/fail results.

Do not publish failed outputs.

---

# Testing

Tests are mandatory for non-trivial application logic.

Prefer unit tests for:

- parsing;
- configuration;
- storyboard structure;
- provider interfaces;
- persistence;
- retry logic;
- file naming;
- validation;
- quality checks.

Use integration tests for:

- pipeline orchestration;
- FFmpeg composition;
- SQLite persistence;
- dry-run pipeline execution.

External paid API calls should normally be mocked during automated tests.

---

# Testing Loop

After meaningful changes:

```text
IMPLEMENT
→ RUN RELEVANT TESTS
→ INSPECT FAILURE
→ FIX
→ RUN AGAIN
```

Do not postpone all testing until the end.

Run the smallest relevant test set during development, then run the complete test suite before major milestones.

---

# Never Fake Success

Do not:

- replace real test execution with claims that tests should pass;
- suppress failing tests;
- delete valid tests merely to make CI green;
- hard-code expected outputs solely to satisfy tests;
- skip required runtime verification;
- create empty placeholder output files and treat them as successful generation.

Actual verification is required.

---

# Git Workflow

Git is part of the autonomous development workflow.

Codex should maintain a clean and useful Git history.

The normal workflow is:

```text
IMPLEMENT
→ TEST
→ REVIEW
→ COMMIT
→ PUSH
→ CONTINUE
```

---

# Conventional Commits

All commit messages must use Conventional Commit-style prefixes.

Allowed prefixes:

```text
feat:
fix:
docs:
test:
refactor:
chore:
perf:
```

Examples:

```text
feat: add storyboard generation pipeline

feat: add pluggable video provider

fix: handle ffmpeg composition failures

fix: retry transient provider errors

docs: document local setup process

test: add end-to-end dry run coverage

refactor: extract media provider interfaces

chore: configure environment loading

perf: reduce unnecessary media re-encoding
```

Commit summaries must be:

- written in English;
- concise;
- specific;
- meaningful.

Do not use vague commits such as:

```text
update
changes
fix stuff
work
wip
misc
```

---

# Atomic Commits

Commits should represent meaningful, independently understandable milestones.

Do not commit every file modification separately.

Good example:

```text
feat: add pluggable video provider
```

This commit may contain:

- provider interface;
- mock provider;
- tests;
- configuration updates;
- documentation updates.

Bad example:

```text
feat: add interface
feat: add class
fix: typo
test: test class
```

when all changes belong to one logical unit.

---

# Commit Requirements

Before creating a commit:

1. Run relevant tests.
2. Ensure required tests pass.
3. Inspect:

```bash
git status
git diff
```

4. Check for secrets.
5. Check for temporary files.
6. Check for accidental generated media.
7. Remove unnecessary debug output.
8. Update documentation if behavior changed.
9. Update `PROGRESS.md` when a milestone changed.

Do not commit known failing code unless explicitly required for an unusual recovery workflow.

---

# Automatic Push

After completing a meaningful milestone and creating a successful commit, push it to the configured GitHub remote.

Use:

```bash
git push
```

If the current branch has no upstream and the remote is known:

```bash
git push -u origin <current-branch>
```

Do not ask for confirmation before every normal push.

A successful push does not mean the overall task is finished.

Continue to the next milestone if the project goal is still incomplete.

---

# Git Remote Rules

Before pushing, verify the configured remote.

Use:

```bash
git remote -v
```

Do not invent repository URLs.

If no GitHub remote exists, report it as a user-action blocker.

If the remote exists but authentication fails, report the authentication blocker only after confirming the issue cannot be fixed safely from the current environment.

---

# Git Safety

Never use:

```bash
git push --force
git push --force-with-lease
```

unless the user explicitly requests history rewriting and understands the consequences.

Do not:

- delete remote branches;
- rewrite shared history;
- discard unknown remote changes;
- overwrite other contributors' work;
- reset published commits destructively.

If remote changes exist:

1. fetch;
2. inspect;
3. integrate safely;
4. resolve conflicts;
5. run tests again;
6. push.

---

# .gitignore

Ensure `.gitignore` covers local and generated artifacts where appropriate.

Typical entries include:

```text
.env
.venv/
venv/
__pycache__/
.pytest_cache/
*.pyc
*.log
output/
tmp/
temp/
cache/
*.mp4
*.wav
*.mp3
*.sqlite
*.db
```

However, do not blindly ignore files that are intentionally part of the repository.

Keep:

```text
.env.example
source code
tests
prompt templates
configuration templates
README.md
AGENTS.md
PROGRESS.md
```

---

# Generated Media

Generated media should normally not be committed.

Examples:

- generated MP4 files;
- temporary frames;
- generated voice tracks;
- cached AI outputs;
- temporary render assets.

If small fixtures are needed for tests, keep only carefully selected test assets.

---

# PROGRESS.md

Maintain:

```text
PROGRESS.md
```

as a concise project status file.

It should include:

## Completed

What currently works.

## Verification

What tests or commands were actually executed.

## Current Issues

Known failures or limitations.

## Blockers

Only genuine external blockers.

## Next Step

The next concrete development milestone.

Do not create separate commits solely for trivial `PROGRESS.md` changes.

Include progress updates in the milestone commit they belong to.

---

# README

Keep `README.md` aligned with actual project behavior.

Document:

- project purpose;
- supported workflow;
- prerequisites;
- Python version;
- FFmpeg requirement;
- environment setup;
- `.env` configuration;
- install commands;
- how to run tests;
- how to run the pipeline;
- dry-run usage;
- expected output location;
- known limitations.

Do not document commands that have not been verified.

---

# Dependency Policy

Prefer mature and minimal dependencies.

Do not add a new dependency when standard Python or an existing dependency is sufficient.

When adding dependencies:

- explain the purpose through code structure or documentation;
- update dependency files;
- ensure installation remains reproducible.

Avoid unnecessary heavyweight frameworks.

---

# Dependency Installation

When appropriate and permitted, Codex may install development dependencies required to run tests or the pipeline.

Do not:

- install unnecessary system-wide software;
- change unrelated machine configuration;
- uninstall unrelated packages;
- make destructive global environment changes.

Prefer isolated Python environments.

---

# External Services

Never purchase services automatically.

Never upgrade paid plans automatically.

Never enable potentially expensive API usage without explicit configuration.

Prefer mocks during development.

When real providers are enabled, make cost-producing behavior explicit and configurable.

---

# API Cost Safety

External generation can become expensive.

Support controls such as:

- dry-run mode;
- configurable provider;
- generation limits;
- retry limits;
- optional cost metadata;
- development mocks.

Never create an uncontrolled infinite generation loop.

---

# Publishing Safety

Automatic public publishing is not part of the MVP.

Until explicitly implemented and enabled:

- do not upload to YouTube;
- do not upload to TikTok;
- do not upload to Instagram;
- do not publish content publicly.

Future publishing functionality must be disabled by default.

Recommended configuration:

```text
PUBLISH_ENABLED=false
```

Publishing must require an explicit configuration change.

---

# Future Publishing Architecture

When publishing is eventually implemented, keep it separate from generation.

Suggested flow:

```text
Generate
→ Validate
→ Quality Gate
→ Approve
→ Schedule
→ Publish
```

Never publish content that failed validation.

Store platform IDs and publishing status in persistence.

---

# Future Analytics

Analytics may later track metrics such as:

- views;
- watch time;
- average percentage viewed;
- retention;
- likes;
- comments;
- shares;
- subscriber gains;
- upload time;
- story type;
- hook type;
- character;
- visual style.

Do not build advanced optimization logic until sufficient real data exists.

---

# Future Feedback Loop

Eventually, analytics may influence future content generation.

Conceptual architecture:

```text
Analytics
    ↓
Performance Analysis
    ↓
Strategy
    ↓
Idea Generation
    ↓
Script
    ↓
Storyboard
    ↓
Video Generation
    ↓
Quality Gate
    ↓
Publishing
    ↓
Analytics
```

The optimization system should learn from aggregated performance rather than blindly repeating one successful video.

---

# Content Diversity

Avoid generating near-duplicate videos repeatedly.

Future systems should track:

- topic similarity;
- script similarity;
- storyboard similarity;
- character reuse;
- hook reuse;
- story structure repetition.

The objective is repeatable format, not duplicate content.

---

# Prompt Management

Prompts should preferably live outside application logic when practical.

Example:

```text
prompts/
    idea.md
    script.md
    storyboard.md
```

This makes experimentation easier without changing pipeline code.

Prompt versions may be stored with generation metadata.

---

# File Naming

Generated outputs should use predictable and collision-safe names.

For example:

```text
output/
    2026-09-29_001/
        metadata.json
        storyboard.json
        subtitles.srt
        final.mp4
```

or use generation UUIDs.

Avoid silently overwriting previous generations.

---

# Deterministic Development

Where possible, make development behavior reproducible.

Mocks should support deterministic outputs.

Tests should not depend unnecessarily on random values.

If randomness is required, expose or seed it when practical.

---

# Cleanup

Temporary generation assets should be organized and cleaned safely.

Do not delete user-created files.

Only remove temporary artifacts known to belong to the pipeline.

Avoid destructive wildcard deletion outside project-owned directories.

---

# Code Review Before Commit

Before committing a milestone, inspect the implementation for:

- duplicated code;
- accidental complexity;
- weak naming;
- silent failures;
- unhandled edge cases;
- unnecessary dependencies;
- secrets;
- temporary debug code;
- stale comments;
- inaccurate README instructions.

Prefer small corrections before committing rather than accumulating cleanup debt.

---

# Final Verification

Before declaring the MVP complete, Codex must perform a final verification process.

At minimum:

## 1. Check repository state

```bash
git status
```

## 2. Run the complete automated test suite

Example:

```bash
pytest
```

Use the project's actual test command if different.

## 3. Run the pipeline

```bash
python run.py
```

## 4. Verify output

Confirm that a generated MP4 actually exists.

## 5. Validate the generated MP4

Use `ffprobe` or equivalent tooling.

Verify:

- video stream exists;
- duration is greater than zero;
- dimensions are valid;
- output is vertical;
- file can be decoded.

## 6. Verify documentation

Ensure setup and execution instructions in `README.md` match actual behavior.

## 7. Inspect Git changes

Check:

```bash
git diff
git status
```

Ensure there are no:

- secrets;
- accidental binaries;
- temporary files;
- debugging artifacts;
- unexplained generated assets.

## 8. Update progress

Update `PROGRESS.md` with final status and verification results.

## 9. Commit

Create an appropriate Conventional Commit.

Example:

```text
feat: complete end-to-end shorts generation pipeline
```

## 10. Push

Push the completed milestone to GitHub.

If any verification step fails:

```text
IMPLEMENT
→ TEST
→ FIX
→ RETEST
```

Do not declare completion.

---

# Definition of Done for the MVP

The MVP is complete only when all of the following are true:

- `python run.py` executes successfully;
- the pipeline runs from beginning to end;
- a real valid MP4 is generated;
- output is vertical;
- output duration is greater than zero;
- mock or dry-run mode works without paid external APIs;
- provider interfaces exist;
- configuration uses environment variables;
- no secrets are committed;
- SQLite persistence works;
- logging exists;
- error handling exists;
- retry behavior exists for relevant external operations;
- automated tests pass;
- README instructions are accurate;
- generated media is not accidentally committed;
- Git history contains meaningful Conventional Commits;
- completed milestones have been pushed to GitHub.

Only then may the MVP be considered complete.

---

# Autonomous Continuation Rule

After each successful milestone:

```text
TEST
→ REVIEW DIFF
→ COMMIT
→ PUSH
```

Then immediately determine:

```text
Is the overall project goal complete?
```

If no:

continue to the next highest-priority milestone.

Do not wait for the user merely because one milestone was completed.

Only stop for:

- completed project goal;
- genuine external blocker;
- explicit user interruption.

---

# Priority Order

When choosing what to work on next, use this priority:

1. Broken end-to-end execution
2. Failing tests
3. Missing core MVP functionality
4. Reliability and error handling
5. Provider abstraction
6. Output quality validation
7. Documentation
8. Refactoring
9. Nice-to-have features

Do not spend time polishing architecture while the main pipeline still does not run.

---

# General Rule

Whenever uncertain, prefer:

```text
simple
working
tested
observable
recoverable
```

over:

```text
complex
clever
untested
fragile
overengineered
```

The goal is not to produce the most elaborate architecture.

The goal is to build a reliable autonomous AI short-form video pipeline that actually works.