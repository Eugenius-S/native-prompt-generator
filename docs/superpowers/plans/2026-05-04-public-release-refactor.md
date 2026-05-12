# Public Release Refactor Implementation Plan

For agentic workers, especially smaller models. Work in narrow stages. Do not mix unrelated cleanup and extraction in one commit.

## Mission

Refactor the project gradually while preparing the repository for a future public release.

This is **not** a rewrite. This is a staged cleanup and extraction pass with low risk and local-only validation.

## Hard Rules

- Run tests locally only.
- Do not use GitHub Actions for validation.
- Make one logical step per commit.
- Do not change public API payloads unless a stage explicitly says so.
- Prefer behavior-preserving extraction over redesign.
- If a stage grows, split it again.
- Keep legacy isolated instead of letting it keep leaking into the main project surface.

## Main Goals

1. Isolate legacy code so it stops dominating the main project shape.
2. Split the worst hot files into clearer backend/frontend units.
3. Stop carrying dead, intermediate, or internal-only repo clutter toward the public version.
4. Tighten public-facing docs and repo structure for outside users.

## Non-Goals

- No broad engine rewrite.
- No framework migration.
- No prompt-quality retuning unless a stage explicitly uncovers a real regression.
- No silent API contract changes.

## Current Hotspots

- `backend/prompt_service.py`
- `backend/services/scoring.py`
- `backend/legacy_people.py`
- `backend/engine/selectors.py`
- `backend/engine/generator.py`
- `frontend` app shell / section wiring

## Phase 0 — Inventory And Freeze

### Goal

Create a safe map before moving code.

### Steps

- Re-read:
  - `docs/internal/maintainers/AGENTS.md`
  - `docs/internal/maintainers/PROJECT_PLAN.md`
  - `docs/internal/plans/ARCHITECTURAL_REFACTOR_SKELETON_PLAN_2026_04_21.md`
- Run local baseline tests that cover current generator health.
- Make a short inventory list:
  - public-facing files to keep
  - internal docs to archive or move later
  - obviously dead or stale files
  - legacy code entry points

### Exit

- Baseline is green locally.
- Inventory is written down in `docs/internal/maintainers/PROJECT_PLAN.md` or a short dedicated note.

## Phase 1 — Legacy Isolation

### Goal

Push legacy paths into a clearly named isolated zone so they stop cluttering the main code surface.

### Required Target

- Use the project-root `_legacy/` folder as the quarantine location.
- `_legacy/` must stay gitignored and must never be pushed to GitHub.
- Treat `_legacy/` as a temporary holding area, not as part of the public project architecture.

### Steps

- Identify everything still serving the legacy people pipeline.
- Move or wrap legacy-specific code into `_legacy/` or behind adapters that point to `_legacy/`.
- Keep compatibility shims where needed so runtime behavior does not change.
- Make sure new work does not keep importing legacy helpers directly.

### Preferred Outcome

- legacy code still works if needed
- but main code paths stop depending on it casually
- `_legacy/` does not leak back into public/main-path structure

### Exit

- `legacy_people` usage is visibly reduced or routed through clearer wrappers/facades.

## Phase 2 — Backend Facade Extraction

### Goal

Start with the biggest orchestration file and split responsibility without changing behavior.

### Primary Target

- `backend/prompt_service.py`

### Steps

- Extract pure helpers first:
  - bootstrap-related
  - presets/history storage
  - run orchestration helpers
  - debug summary helpers
- Leave `prompt_service.py` as a compatibility facade during the phase.
- Add/update characterization tests if extraction touches unprotected behavior.

### Exit

- `prompt_service.py` is thinner
- behavior remains stable
- tests still pass locally

## Phase 3 — Scoring And Selector Cleanup

### Goal

Reduce risk in the two most change-heavy logic surfaces after `prompt_service.py`.

### Primary Targets

- `backend/services/scoring.py`
- `backend/engine/selectors.py`

### Steps

- Split by concern, not by arbitrary size:
  - scene/outfit compatibility
  - framing/pose diversity
  - treatment/light pressure
  - anti-repeat / anti-clone rules
- Keep public call sites stable while extracting internal modules.
- Do not retune taste on purpose during this phase.

### Exit

- scoring logic is easier to locate by topic
- selector logic has clearer sub-boundaries

## Phase 4 — Repository Cleanup For Public Release

### Goal

Stop shipping obvious internal clutter as if it were part of the public product.

### Steps

- Review root-level docs and notes.
- Split files into buckets:
  - keep public
  - move to archive/internal
  - delete if dead
- Remove old intermediate instructions that are no longer used.
- Keep only docs that help:
  - run the app
  - understand architecture
  - contribute safely

### Important

Do this in small batches. Do not delete a huge pile blindly.

### Exit

- root becomes cleaner
- obvious staging residue is reduced
- maintainer-only notes no longer dominate the root tree

## Phase 5 — Public-Facing Documentation Pass

### Goal

Make the repo understandable to an outside user.

### Minimum Targets

- `README.md`
- `QUICKSTART.md`
- setup/run instructions
- short architecture overview

### Steps

- Rewrite docs for an external reader, not only for the owner.
- Remove references that only make sense inside the current private workflow.
- Keep instructions short and accurate.

### Exit

- a new user can understand what the project is and how to run it locally

## Phase 6 — Release Readiness Sweep

### Goal

Do a last pass to ensure the repo now looks like a real public project, not an active private staging area.

### Steps

- Re-run targeted local tests.
- Check top-level tree again.
- Check for accidental internal-only instructions still exposed.
- Check that setup/start flow and docs match reality.

### Exit

- repo shape is coherent
- no obvious internal junk dominates the public surface

## Suggested Execution Order For GPT 5.4 Mini High

1. Phase 0
2. Phase 1
3. Phase 2
4. Phase 3
5. Phase 4
6. Phase 5
7. Phase 6

If a phase feels too big, stop and split it before coding.

## Commit Discipline

- one phase can contain several commits
- but each commit must be one clean idea
- after each finished sub-stage:
  - run local tests
  - commit
  - update `docs/internal/maintainers/PROJECT_PLAN.md`
  - close/update issue only if that stage is truly done
