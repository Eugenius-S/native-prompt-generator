# Native Prompt Generator — Agent Notes

## Purpose
- Local prompt generator for AI photo-session prompts.
- Main goal: make writing prompt batches faster, easier, and more controllable.
- Primary target stack:
  - local web UI
  - Python backend
  - ComfyUI / Z-Image style prompt workflows

## Project Shape
- `app.py` — local HTTP server entrypoint.
- `backend/` — prompt logic, scoring, rendering, storage.
- `frontend/` — local web UI.
- `data/` — local runtime data files.
- `backend/engine/data/` — core content banks and treatment banks.

## Important Working Rules
- Preserve local-first workflow. Do not turn this into a cloud app unless explicitly requested.
- Prefer small, additive changes over big rewrites.
- Do not break the existing generator core just to add a new control.
- New content should be data-driven when possible, not hardcoded in Python.
- Prefer extending:
  - content banks
  - scoring rules
  - render fallbacks
  instead of replacing the engine structure.

## Current Architecture Priorities
- `women`, `men`, and `couples` must all stay working.
- `photo_treatment` is a real internal layer and should be respected in:
  - selection
  - scoring
  - render
  - debug
- `same_person` means locked identity across the batch, not necessarily locked outfit.
- UI changes must not silently desync from backend form normalization.

## Styling / Prompt Philosophy
- Z-Image handles longer prompts fine.
- Do not over-optimize prompt length unless it improves quality/readability.
- Prefer natural photo-language over tag soup.
- The generator should not default too hard into stock/professional output.
- Stylization should stay compatible with scene/style logic and not create nonsense combinations.

## Safety / Quality Rules
- Always run targeted tests after changing scoring, reveal logic, routing, or render fallbacks.
- Run all validation tests locally in this repo.
- Do not use GitHub Actions for testing or validation.
- For broad quality changes, test at least:
  - `women random`
  - `women nightlife`
  - `men romantic`
  - `couples random`
  - `couples lifestyle`
  - `couples nightlife`
- Watch especially for:
  - swimwear leaks in wrong scenes
  - latex leaks in normal modes
  - overuse of `tiny mini skirt`
  - same-color couple clothing drift
  - `men` debug showing women-side scaffold data by mistake

## Logging Discipline
- Record meaningful work in:
  - `CHANGELOG.md`
  - `TEST_LOG.md`
  - `PROJECT_PLAN.md`
- `TEST_LOG.md` should contain actual checked outcomes, not vague claims.
- Large unfinished ideas belong in `PROJECT_PLAN.md`, not in code comments.

## Writing Style
- Chat with the project owner in Russian.
- UI copy should be plain, short, direct, and human.
- Avoid corporate tone, marketing phrasing, filler, and over-explaining obvious things.
- Prefer one message = one idea.
- Issues and task writeups should get to the point fast and stay specific.
- Prefer a simple structure when useful:
  - Problem
  - Context
  - Expected behavior
  - Actual behavior
  - Why it matters
  - Notes
- Prefer phrasing like `Right now...`, `This is confusing because...`, `We should...`, `User expects...`, `Instead, they see...`.

## Content Bank Strategy
- Prefer adding new content through structured banks.
- Use the layered bank approach:
  - `core`
  - `drafts`
  - `overrides`
- New locations / poses / styling atoms should be easy to extend without editing many Python branches.

## Legacy Isolation Rule
- Legacy code and legacy reference leftovers should go into the project-root `_legacy/` folder.
- `_legacy/` is a quarantine zone, not part of the active project surface.
- `_legacy/` must never be pushed to GitHub.
- New main-path code must not import from `_legacy/` directly except through explicit temporary adapters during a controlled migration stage.

## Git Workflow
- This repository is a staging repo.
- Work locally in `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator`.
- Commit small logical batches.
- Push meaningful checkpoints with clear commit messages after tests pass.
- After each finished work stage, always make a `git commit`.
- Close the related GitHub issue when that stage is actually finished.
- Opening a PR is optional and should be used when it helps review, stacked work, or delivery.
- Do not leave a finished stage only in local changes.
- Do not close an issue for a partial pass with remaining acceptance gaps.
