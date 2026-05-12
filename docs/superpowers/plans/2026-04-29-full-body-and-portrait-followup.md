# Full-Body And Portrait Follow-Up Implementation Plan

For agentic workers. Keep changes narrow, verify with small targeted tests, and commit after each finished stage.

## Goal

Finish the reopened `#98` full-body framing fix properly and then harden portraits via `#99`.

The problem is not just wording. Full-body still behaves like a portrait lane too often, and portraits still need a safer default crop.

## Confirmed Product Direction

- Use **option 3**: a dedicated hard framing contract for standing full-length shots.
- Do **not** treat `both feet visible` as the universal priority.
- Desired behavior:
  - standing full-body should read as a real full-length camera lane
  - ankles or feet may be visible depending on composition
  - the key requirement is: no collapse back into waist-up / upper-body / portrait crops

## Architecture Direction

- Treat `full_body` and `ankle_up` as a stronger camera contract, not a soft prompt hint.
- Separate standing full-height from seated/lowered full-height behavior.
- Remove portrait contamination from full-body lanes.
- Keep portrait defaults in the pretty zone:
  - head-and-shoulders
  - slightly below chest
- Do not bring back face-only as a common automatic outcome.

## Stage 1 — Reopened `#98` Full-Body Fix

### Intent

Make standing full-body actually behave like a true full-length camera lane:

- camera far enough from the subject
- full standing figure kept in frame
- no accidental fallback into waist-up / upper-body / portrait-like composition
- feet visibility allowed when composition supports it, but not treated as the only success criterion

### Likely Files

- `backend/engine/render/prompt_renderer.py`
- `backend/services/scoring.py`
- `tests/test_issue65_framing_control_smoke.py`
- `tests/test_issue82_framing_render_coherence_smoke.py`

### Steps

- Add/adjust failing tests for standing `full_body` and `ankle_up`.
- Build a dedicated standing full-length framing block instead of reusing portrait/full-figure wording.
- Use wording closer to the successful manual prompts:
  - `full length framing`
  - `camera far enough from the subject`
  - `whole standing figure visible`
  - centered / composed full-height shot
- Make sure full-body lanes cannot keep portrait-like framing language.
- If needed, gate out portrait-ish pose text from standing full-body.
- Run small smokes and only close `#98` after a visual check, not from wording alone.

## Stage 2 — `#99` Portrait Anti-Head-Cut Hardening

### Intent

Portrait defaults should stay attractive and safe:

- no chopped head
- no too-tight face crop by default
- best default zone is chest-up / head-and-shoulders

### Likely Files

- `backend/engine/render/prompt_renderer.py`
- `tests/test_issue65_framing_control_smoke.py`

### Steps

- Add/adjust tests for portrait breathing room above the head.
- Harden the portrait framing safety block.
- Keep `head_and_shoulders` and `below_chest_portrait` as the default beauty winners.
- Keep `face_only` effectively non-default.
- Close `#99` only after confirming the new default look is prettier, not just safer.

## Verification

- Run targeted framing tests only.
- Do one small live sweep for `more_full_body`.
- Do one small live sweep for `more_portraits`.
- Log only real residual failures; avoid wide random reruns unless a regression appears.
