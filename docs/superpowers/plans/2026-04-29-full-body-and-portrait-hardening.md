# Full-Body And Portrait Hardening Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:subagent-driven-development` or `superpowers:executing-plans`. Do not broad-refactor the framing system. Fix the contract narrowly and validate with live sweeps.

**Goal:** finish reopened issue `#98` and new issue `#99` without disturbing the now-stable light / studio / portrait base.

**Context:**
- `#98` was closed too early. Current framing text is not enough to force reliable standing full-body shots.
- `#99` tracks portrait anti-head-cut hardening and keeping chest-up beauty framing as the attractive default.
- The user already confirmed that ChatGPT-style prompts succeed more reliably when they use explicit camera distance and stronger full-length wording.

---

## Task 1: Re-fix `#98` at the contract level

**Files:**
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\engine\render\prompt_renderer.py`
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\services\scoring.py`
- Modify if needed: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\forms\user_profile.py`
- Test: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_issue65_framing_control_smoke.py`
- Test: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_issue82_framing_render_coherence_smoke.py`

- [ ] Add a stronger dedicated full-body contract block, not just a generic framing note.
- [ ] Make standing `full_body` / `ankle_up` explicitly say:
  - full length framing from head to toe
  - both feet fully visible, where applicable
  - subject centered in frame
  - camera far enough from the subject to keep the whole figure visible
- [ ] Keep seated/non-standing full-height prompts on a different wording path so the system does not reuse standing language blindly.
- [ ] Remove any remaining scoring preference that rewards `knee_up` / `cowboy_shot` under `more_full_body`.
- [ ] If live sweeps still fail, the next narrow escalation should be: standing-safe pose gating for full-body, not a broad rewrite.
- [ ] Run tests and a small live sweep.
- [ ] Commit.

## Task 2: Harden `#99` without bringing face-only back

**Files:**
- Modify if needed: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\engine\render\prompt_renderer.py`
- Modify if needed: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\engine\data\composition.json`
- Modify if needed: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\forms\user_profile.py`
- Test: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_issue65_framing_control_smoke.py`
- Test: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_issue82_framing_render_coherence_smoke.py`

- [ ] Keep `face_only` non-default.
- [ ] Bias portrait defaults toward `head_and_shoulders` and `below_chest_portrait`.
- [ ] Strengthen portrait-safe wording:
  - full head and hair visible
  - comfortable space above the head
  - no tight crop at the top
- [ ] Validate that the prettier chest-up beauty framing remains the dominant automatic portrait behavior.
- [ ] Commit.

## Task 3: Validate with the exact user failure mode

**Run live sweeps, not only pytest.**

- [ ] Run `women + more_full_body` live batches and inspect whether standing shots now actually show full height.
- [ ] Run `women + random / more_portraits` live batches and inspect whether portraits avoid ugly top-of-head crops.
- [ ] If `#98` still fails in live standing shots, leave it open and document the remaining leak precisely instead of pretending it is done.
- [ ] If `#99` is visually stable, close it.
- [ ] Update `PROJECT_PLAN.md`.
- [ ] Commit.

## Notes for the next agent

- Do **not** solve `#98` with more random synonyms only. The issue is that the model still treats many of these prompts as portrait/beauty shots with a decorative full-body clause.
- The user's successful external prompts suggest that explicit camera distance + full-length wording + simpler standing-safe pose phrasing matters more than our current generic framing sentence.
- The user specifically said ultra-tight face close-up is not a good automatic default. Do not swing back toward that lane.
