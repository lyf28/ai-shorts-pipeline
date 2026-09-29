# AGENTS.md

## 1. Project Purpose

This repository contains an autonomous short-form AI video generation pipeline.

The long-term system should be capable of:

1. Generating short-form video ideas.
2. Writing short scripts.
3. Converting scripts into structured scenes.
4. Producing storyboards.
5. Generating visual assets or video clips.
6. Generating narration, music, or sound effects when needed.
7. Composing vertical short-form videos.
8. Adding subtitles.
9. Running automated quality checks.
10. Persisting generation metadata.
11. Scheduling content generation.
12. Publishing approved content.
13. Collecting performance analytics.
14. Using historical performance to improve future content decisions.

The current priority is reliability and incremental engineering.

Do not optimize for maximum feature count.

Optimize for:

- working software;
- clear architecture;
- small reviewable commits;
- reproducible tests;
- safe automation;
- low manual intervention.

---

# 2. Primary MVP Goal

The local MVP is successful when:

```bash
python run.py
```

can execute the complete local pipeline and produce a valid vertical MP4 inside:

```text
output/
```

The local MVP must remain testable without paid external APIs by supporting mock or local providers.

A feature is not complete merely because code exists.

A feature is complete only when:

1. implementation exists;
2. relevant tests pass;
3. the actual execution path has been exercised where practical;
4. errors are handled;
5. related documentation or configuration is updated;
6. the work has been committed as its own appropriate Git checkpoint.

---

# 3. Highest-Priority Rule: Incremental Git History

Small, reviewable Git commits are a mandatory project requirement.

They are not optional cleanup performed after implementation.

Codex MUST NOT build several completed subsystems and commit them together later.

The project must evolve through incremental Git checkpoints.

The unit of review is the commit, not the push.

---

# 4. Mandatory Development State Machine

For every independently meaningful unit of work, follow this exact state machine:

```text
INSPECT
→ PLAN ONE UNIT
→ IMPLEMENT ONE UNIT
→ TEST THAT UNIT
→ FIX IF NEEDED
→ RETEST
→ REVIEW DIFF
→ COMMIT THAT UNIT
→ OPTIONAL PUSH
→ BEGIN NEXT UNIT
```

The following workflow is forbidden:

```text
PLAN EVERYTHING
→ IMPLEMENT EVERYTHING
→ TEST EVERYTHING
→ COMMIT EVERYTHING
```

Codex MUST NOT begin implementation of the next planned engineering unit while the current completed unit remains uncommitted.

This is a hard checkpoint rule.

---

# 5. Commit Plan Before Implementation

Before beginning a multi-step task, Codex must create a commit plan.

The plan should identify the expected sequence of independently reviewable commits.

Example:

```text
1. chore: initialize project structure
2. feat: add pipeline data models
3. feat: add provider interfaces
4. feat: add local development providers
5. feat: add storyboard generation
6. feat: add sqlite run persistence
7. feat: add ffmpeg composition
8. feat: add pipeline orchestration
9. test: add end-to-end dry run coverage
10. docs: document local pipeline setup
```

The plan may evolve during implementation.

However, commit boundaries must remain small and coherent.

Record the current plan in `PROGRESS.md`.

---

# 6. One Primary Idea Per Commit

Every commit must have exactly one primary engineering purpose.

Good examples:

```text
feat: add pipeline data models
feat: add llm provider interface
feat: add local llm provider
feat: add storyboard generation
feat: add sqlite run persistence
feat: add ffmpeg video composition
feat: add subtitle rendering
feat: add pipeline orchestration
fix: handle missing ffmpeg executable
test: add storyboard validation coverage
docs: document local setup
```

Bad examples:

```text
feat: build entire pipeline
feat: finish MVP
feat: complete shorts generator
feat: add providers database ffmpeg and tests
feat: implement full local video system
```

---

# 7. Forbidden Aggregate Commits

Do NOT create a commit that introduces multiple independently meaningful subsystems.

For example, these concerns should normally be separate commits:

- data models;
- configuration;
- provider interfaces;
- individual provider implementations;
- storyboard generation;
- persistence;
- retry logic;
- FFmpeg composition;
- subtitle generation;
- quality validation;
- pipeline orchestration;
- publishing;
- analytics.

Completing the overall project goal is NOT justification for combining these into one final commit.

A final commit named something like:

```text
feat: complete local shorts generation pipeline
```

is forbidden if it contains several independently implementable pieces.

---

# 8. Commit Size Heuristics

There is no absolute line-count limit.

However, Codex must treat a large diff as a warning sign.

Before committing, check:

```bash
git diff --stat
git diff
git status
```

Codex must reconsider the commit boundary if:

- several major modules are being introduced;
- multiple unrelated directories changed;
- the commit contains several distinct behaviors;
- the commit contains hundreds of lines across unrelated subsystems;
- some part of the work could reasonably have been committed earlier.

Large commits are allowed only when the changes are inherently inseparable.

---

# 9. Independent Revert Test

Before committing, ask:

> Can this commit be reverted independently without conceptually undoing unrelated functionality?

If the answer is no, reconsider the boundary.

Also ask:

> Does this commit contain more than one main engineering idea?

If yes, split it.

---

# 10. Tests and Feature Commits

Tests directly associated with a feature MAY be included in the same commit.

Example:

```text
feat: add storyboard generation
```

may contain:

- storyboard implementation;
- storyboard models directly needed by it;
- storyboard unit tests.

Do not create artificial micro-commits such as:

```text
feat: add storyboard class
test: test storyboard class
fix: storyboard typo
```

when those changes naturally form one coherent implementation unit.

The goal is not maximum commit count.

The goal is clean conceptual boundaries.

---

# 11. Configuration and Documentation Changes

Small configuration or documentation changes required by a feature may be included with that feature.

Example:

```text
feat: add openai llm provider
```

may include:

- provider implementation;
- `.env.example` entry;
- related README setup instructions;
- provider tests.

Do not combine unrelated documentation or configuration work.

---

# 12. Conventional Commits

All commits must use Conventional Commit-style prefixes.

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

Commit messages must:

- be written in English;
- be concise;
- describe the actual change;
- avoid vague wording.

Good:

```text
feat: add storyboard generation
fix: retry transient video provider failures
docs: document ffmpeg setup
test: add pipeline dry run coverage
refactor: extract media provider interface
chore: configure environment loading
```

Bad:

```text
update
changes
fix stuff
work
misc
wip
done
finish project
```

---

# 13. Commit Timing

Commit immediately after an independently meaningful unit becomes complete and verified.

Do not intentionally accumulate several completed milestones in the working tree.

Correct:

```text
implement provider interface
→ test
→ commit

implement local provider
→ test
→ commit

implement storyboard
→ test
→ commit
```

Incorrect:

```text
implement provider interface
implement local provider
implement storyboard
implement database
implement ffmpeg
→ one commit
```

---

# 14. Push Behavior

Multiple small commits may be pushed together.

A push does not need to happen after every individual commit.

Example:

```text
COMMIT A
COMMIT B
COMMIT C
→ PUSH
```

is acceptable.

However:

```text
IMPLEMENT A
IMPLEMENT B
IMPLEMENT C
→ COMMIT ABC
→ PUSH
```

is not acceptable.

Again:

> The unit of review is the commit, not the push.

---

# 15. Automatic Push

When a remote exists and authentication is available, Codex may automatically push completed commits.

Normal command:

```bash
git push
```

If an upstream is not configured:

```bash
git push -u origin <current-branch>
```

Do not stop merely because a push succeeded.

If the overall goal is incomplete, continue with the next planned unit.

---

# 16. Repository Inspection

Before making significant changes, inspect:

```bash
git status
git branch --show-current
git remote -v
git log --oneline --decorate -15
```

Also inspect relevant:

- source files;
- tests;
- README;
- `AGENTS.md`;
- `PROGRESS.md`;
- configuration;
- dependency manifests.

Do not modify architecture blindly.

---

# 17. Existing Work Must Be Respected

Do not overwrite or revert existing user work without understanding it.

Do not:

- discard unknown changes;
- remove files merely because they appear unused;
- reset uncommitted work without inspection;
- rewrite published history unless the user explicitly requested it.

If unrelated user modifications exist, preserve them.

---

# 18. History Rewrite Exception

Normally, published history must not be rewritten.

History rewriting is allowed only when the user explicitly requests it.

When explicitly authorized:

1. fetch the latest remote state;
2. verify the target branch;
3. create a backup reference;
4. push the backup reference;
5. reconstruct the history;
6. verify the reconstructed repository;
7. use `--force-with-lease`, never plain `--force`;
8. abort if the remote changed unexpectedly.

Never silently rewrite shared history.

---

# 19. Git Safety

Do not use:

```bash
git push --force
```

Use:

```bash
git push --force-with-lease
```

only when the user explicitly authorized history rewriting.

Never:

- destroy unknown remote changes;
- delete remote branches without explicit instruction;
- remove another contributor's work;
- overwrite a changed remote branch blindly.

---

# 20. Final Verification Is NOT a Commit Boundary

Final verification happens after incremental implementation commits already exist.

Do not create a synthetic final commit merely because the project is now complete.

For example, do NOT create:

```text
feat: complete MVP
```

if no new focused implementation belongs in that commit.

At final verification:

```bash
git status
git log --oneline --decorate -20
```

If the working tree is clean, do not create another commit.

If final verification reveals a bug, fix only that bug and commit it appropriately.

Example:

```text
fix: correct ffmpeg output validation
```

---

# 21. Project Architecture

Keep major concerns separated.

Suggested components:

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

Avoid unnecessary layers.

Do not introduce complex orchestration until the simpler pipeline works.

---

# 22. Provider Architecture

External services must be replaceable.

Use abstractions for appropriate service categories such as:

```text
LLMProvider
ImageProvider
VideoProvider
TTSProvider
AudioProvider
```

Provider-specific behavior must remain isolated from pipeline orchestration.

Potential implementations may include:

```text
LocalLLMProvider
OpenAILLMProvider
MockVideoProvider
OpenAIVideoProvider
MockTTSProvider
OpenAITTSProvider
```

Do not tightly couple application logic to one vendor.

---

# 23. Mock and Local Development

Missing external API credentials must not block local development.

If credentials are unavailable:

1. create the provider abstraction;
2. provide a mock/local implementation;
3. continue developing the pipeline;
4. test end-to-end locally;
5. document what credentials will later be required.

The local pipeline should remain usable without spending money.

---

# 24. Current MVP Scope

The local MVP should support:

- idea generation;
- script generation;
- structured scenes;
- storyboard generation;
- pluggable providers;
- local/mock media generation;
- optional narration;
- FFmpeg composition;
- subtitles;
- metadata persistence;
- logging;
- retry handling;
- error handling;
- dry-run behavior;
- local integration testing.

Preferred final output:

```text
1080x1920 MP4
```

---

# 25. Initial MVP Out of Scope

Until the local generation pipeline is reliable, avoid implementing:

- automatic YouTube publishing;
- automatic TikTok publishing;
- automatic Instagram publishing;
- fully autonomous public posting;
- large-scale trend scraping;
- revenue optimization;
- complex multi-agent architecture;
- Kubernetes;
- Airflow;
- distributed orchestration.

---

# 26. Python Standards

Prefer modern, readable Python.

Use:

- type hints;
- small focused functions;
- clear module ownership;
- dataclasses or structured models when useful;
- explicit error handling;
- dependency injection where helpful.

Avoid:

- giant functions;
- unnecessary global state;
- deep nesting;
- silent exception swallowing;
- unnecessary frameworks.

---

# 27. Secrets

Never commit:

- API keys;
- passwords;
- OAuth tokens;
- refresh tokens;
- cookies;
- service credentials;
- SSH private keys;
- private certificates.

Use environment variables.

Provide:

```text
.env.example
```

with placeholders only.

Before every commit, inspect the diff for secrets.

---

# 28. Configuration

Runtime configuration should come from:

- environment variables;
- `.env`;
- structured config when justified.

Never hard-code credentials.

Provider selection should be configurable.

---

# 29. Persistence

SQLite is preferred for the local MVP.

Useful persisted fields include:

- generation ID;
- timestamps;
- idea;
- script;
- storyboard;
- prompts;
- provider names;
- generation status;
- retry counts;
- error details;
- output path;
- quality results.

Do not store secrets in SQLite.

---

# 30. Logging

Logs should identify:

- pipeline stage;
- generation ID;
- provider;
- retries;
- useful errors;
- output location.

Never log secrets.

Avoid noisy debug output in committed production code.

---

# 31. Retry and Failure Handling

External calls should have:

- timeout;
- bounded retry;
- clear failure messages;
- structured logging.

Never create infinite retries.

Recoverable behavior:

```text
FAIL
→ RETRY
→ VALIDATE
→ CONTINUE
```

Unrecoverable failures must be recorded clearly and must not silently corrupt downstream output.

---

# 32. FFmpeg

Use FFmpeg for deterministic media composition when appropriate.

Support:

- vertical resolution;
- consistent frame rate;
- scene concatenation;
- audio;
- subtitles;
- duration normalization.

Treat non-zero FFmpeg exit status as failure.

---

# 33. Output Validation

A generated MP4 must be validated.

Use `ffprobe` where available.

Check at least:

- file exists;
- file size is non-zero;
- video stream exists;
- duration is greater than zero;
- dimensions are valid;
- file is decodable;
- expected vertical format exists.

File existence alone does not mean success.

---

# 34. Quality Gate

Outputs should eventually support automated checks for:

- aspect ratio;
- duration;
- missing scenes;
- corrupt clips;
- subtitle generation;
- audio when expected;
- blank frames;
- placeholder media leaking into production.

A failed quality gate must prevent publishing.

---

# 35. Testing

Use unit tests for logic such as:

- configuration;
- parsing;
- storyboard generation;
- persistence;
- retry behavior;
- validation;
- provider interfaces.

Use integration tests for:

- pipeline orchestration;
- SQLite;
- FFmpeg;
- dry-run execution.

Paid APIs should normally be mocked in automated tests.

---

# 36. Mandatory Test Loop

After meaningful changes:

```text
IMPLEMENT
→ RUN RELEVANT TESTS
→ INSPECT FAILURE
→ FIX
→ RETEST
```

Do not postpone all tests until the end.

---

# 37. Never Fake Success

Do not:

- claim tests passed without running them;
- suppress failing tests;
- delete valid tests to get green output;
- replace real execution with assumptions;
- create empty output files and call them successful;
- hard-code fake results merely to satisfy tests.

Verification must be real.

---

# 38. .gitignore

Typical local/generated artifacts should be ignored when appropriate:

```text
.env
.venv/
venv/
__pycache__/
.pytest_cache/
*.pyc
*.log
output/
work/
tmp/
temp/
cache/
*.mp4
*.wav
*.mp3
*.sqlite
*.db
```

Do not blindly ignore files intentionally required by the repository.

Keep important source assets such as:

```text
.env.example
README.md
AGENTS.md
PROGRESS.md
source code
tests
prompt templates
config templates
```

---

# 39. Generated Media

Do not normally commit:

- generated videos;
- generated audio;
- temporary frames;
- cached AI responses;
- render intermediates.

Small intentional test fixtures are allowed when justified.

---

# 40. PROGRESS.md

Maintain `PROGRESS.md`.

It should contain:

## Goal

Current overall task.

## Planned Commits

The planned incremental commit sequence.

## Completed

Completed engineering units.

## Verification

Commands and tests actually executed.

## Current Issues

Known problems.

## Blockers

Only genuine external blockers.

## Next Commit

The next specific commit planned.

After each commit, update the plan before beginning the next unit if necessary.

Do not batch many unrelated progress updates into a standalone commit unless documentation itself is the intended change.

---

# 41. README

Keep `README.md` aligned with actual behavior.

Document:

- project purpose;
- requirements;
- Python setup;
- FFmpeg setup;
- environment configuration;
- install commands;
- tests;
- dry-run behavior;
- pipeline execution;
- output location;
- limitations.

Do not document commands that were never verified.

---

# 42. Dependency Policy

Prefer minimal, mature dependencies.

Do not add a dependency if standard Python or an existing dependency is sufficient.

Prefer isolated Python environments.

Do not modify unrelated machine-wide software.

---

# 43. External Cost Safety

Never:

- purchase a service;
- upgrade a plan;
- start uncontrolled paid generation;
- create unbounded API loops.

Support:

- dry-run mode;
- mocks;
- retry limits;
- provider configuration;
- generation limits.

---

# 44. Publishing Safety

Automatic public publishing is not part of the initial MVP.

Future publishing should be disabled by default.

Recommended:

```text
PUBLISH_ENABLED=false
```

Future publishing flow should resemble:

```text
Generate
→ Validate
→ Quality Gate
→ Approve
→ Schedule
→ Publish
```

Never publish failed output.

---

# 45. Future Analytics

Future analytics may include:

- views;
- watch time;
- retention;
- average percentage viewed;
- likes;
- comments;
- shares;
- subscriber gains;
- upload time;
- story type;
- hook type;
- character;
- visual style.

Do not implement complex optimization until enough real data exists.

---

# 46. Future Feedback Loop

Potential future architecture:

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

Do not blindly duplicate successful content.

Optimize patterns while preserving content diversity.

---

# 47. Prompt Management

Prefer storing prompts outside application logic when practical.

Example:

```text
prompts/
    idea.md
    script.md
    storyboard.md
```

Generation metadata may record prompt versions.

---

# 48. Output Naming

Avoid overwriting previous runs.

Prefer generation IDs or timestamped directories.

Example:

```text
output/
    2026-09-29_001/
        metadata.json
        storyboard.json
        subtitles.srt
        final.mp4
```

---

# 49. Temporary Files

Temporary files must stay inside known project-owned directories.

Never delete arbitrary user directories.

Do not use unsafe broad wildcard deletion.

---

# 50. Before Every Commit

Perform this checklist:

1. Verify the current unit is complete.
2. Run relevant tests.
3. Fix failures.
4. Run tests again.
5. Run:

```bash
git status
git diff --stat
git diff
```

6. Check for secrets.
7. Check for generated media.
8. Remove temporary debugging code.
9. Check whether the diff has exactly one main purpose.
10. Split the diff if multiple independent purposes exist.
11. Commit using a Conventional Commit message.
12. Update `PROGRESS.md` appropriately.
13. Continue only after the commit exists.

---

# 51. Final Verification

Before declaring a larger goal complete:

1. Run the full automated test suite.
2. Run the relevant end-to-end pipeline.
3. Verify output files.
4. Validate media with FFmpeg/ffprobe where applicable.
5. Verify README instructions.
6. Run:

```bash
git status
git log --oneline --decorate -20
```

7. Confirm major engineering milestones are represented as separate commits.
8. Confirm there is no giant aggregate implementation commit.
9. Confirm no secrets or generated artifacts were committed.

If the working tree is clean, do not create a synthetic final commit.

If verification reveals a bug:

```text
FIX
→ TEST
→ COMMIT THAT FIX
```

---

# 52. Definition of Done for the Local MVP

The local MVP is complete only when:

- `python run.py` succeeds;
- an actual valid vertical MP4 is produced;
- mock/local mode works without paid APIs;
- provider abstractions exist;
- configuration is externalized;
- no secrets are committed;
- persistence works;
- logging works;
- retry/error handling exists;
- automated tests pass;
- documentation is accurate;
- generated media is excluded from source control;
- Git history contains small meaningful Conventional Commits;
- major subsystems are not collapsed into one aggregate commit.

---

# 53. When Codex May Stop

Codex may stop only when:

## A. The current requested goal is complete

and all verification requirements passed.

## B. A genuine external blocker requires user action

Examples:

- missing API credentials;
- OAuth authorization;
- unavailable GitHub authentication;
- repository permission failure;
- paid service decision;
- manual provider approval.

## C. Reasonable autonomous attempts have failed

If so, document:

- exact failure;
- attempts made;
- actual error;
- why further autonomous attempts are unlikely to help;
- exact user action required.

Normal bugs are not blockers.

---

# 54. Autonomous Continuation Rule

After every commit:

1. inspect `PROGRESS.md`;
2. identify the next planned commit;
3. continue automatically;
4. do not wait for the user unless blocked.

A successful commit or push does not mean the task is finished.

Continue until the requested goal is complete.

---

# 55. Priority Order

When deciding what to do next:

1. protect user work and repository safety;
2. keep commit boundaries correct;
3. fix broken execution;
4. fix failing tests;
5. implement missing core functionality;
6. improve reliability;
7. improve validation;
8. improve documentation;
9. refactor;
10. add optional features.

---

# 56. Final Engineering Principle

Prefer:

```text
small
working
tested
reviewable
observable
recoverable
```

over:

```text
large
clever
batched
untested
fragile
overengineered
```

A task is not successfully completed if the software works but the Git history violates the required incremental commit structure.