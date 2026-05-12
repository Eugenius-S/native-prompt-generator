# Shot Lane Contracts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** remove the cheap-light / contradictory-scene regression by making treatment, lighting, and setting render through authoritative shot-lane contracts instead of loosely compatible fragments.

**Architecture:** add a small render-contract layer that sits between `photo_treatment` and final prompt rendering. The layer decides whether a prompt is a true seamless studio lane, a practical studio/set lane, a hard-sun editorial lane, a clean daylight commercial lane, or another controlled branch, and then constrains scene/render output accordingly. The first pass should stay narrow: women random/default paths plus studio/seamless handling.

**Tech Stack:** Python backend, data-driven JSON banks, existing prompt renderer / candidate builder / postprocess path, pytest smoke tests.

---

### Task 1: Lock the project status and execution order

**Files:**
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\PROJECT_PLAN.md`
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\CHANGELOG.md`
- Test: none

- [ ] Add issue `#90` as the critical root-cause track for treatment/light/scene regression.
- [ ] Add issue `#89` as the dedicated seamless-studio contract track.
- [ ] State the execution order clearly: render-contract layer first, seamless-studio split second, regression tests third.
- [ ] Commit this planning/status pass before broad implementation continues.

### Task 2: Add authoritative shot-lane contract metadata

**Files:**
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\engine\data\photo_treatments.json`
- Create: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\shot_lane_contracts.py`
- Test: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_shot_lane_contracts.py`

- [ ] Add explicit shot-lane metadata to the treatment profiles or map them centrally in `backend/shot_lane_contracts.py`.
- [ ] Keep the first lane set intentionally small:
  - `seamless_studio`
  - `studio_practical_set`
  - `editorial_hard_sun`
  - `clean_daylight_commercial`
  - `controlled_dark_interior`
  - `nightlife_flash`
- [ ] Cover the lane lookup with a narrow unit test that proves `studio_seamless` and `concept/direct-light` no longer collapse into one generic stylized bucket.

### Task 3: Make the lane authoritative over setting and technical render

**Files:**
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\engine\render\prompt_renderer.py`
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\legacy_people.py`
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\services\postprocess.py`
- Test: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_prompt_render_contracts.py`

- [ ] Stop treating `lighting_render`, `time_of_day`, and `setting_scene` as fully independent prompt fragments.
- [ ] Route final render through the lane contract so the lane can:
  - override bad time/light combinations
  - force seamless background wording when appropriate
  - suppress cheap/stage-like setting tails in premium lanes
- [ ] Add focused render tests for the exact failure shapes:
  - `night` must not coexist with `cold daylight`
  - seamless studio must not render `school portrait setup`
  - seamless studio must not render visible set/practical clutter

### Task 4: Split seamless studio from practical studio/set scenes

**Files:**
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\engine\data\photo_treatments.json`
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\engine\candidate_builder.py`
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\engine\line_bank_loader.py` only if a narrow compatibility change is required
- Test: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_studio_scene_contracts.py`

- [ ] Treat `studio_seamless` as a real contract, not merely a preferred scene family.
- [ ] Keep practical/stage/set scenes available for other lanes, but do not let them surface under the seamless lane.
- [ ] Add narrow tests proving:
  - seamless lane -> clean backdrop wording only
  - practical studio/set lane -> may keep stage/set flavor

### Task 5: Validate and close the implementation stage

**Files:**
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\TEST_LOG.md`
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\CHANGELOG.md`
- Test:
  - `python -m pytest tests\test_shot_lane_contracts.py -q`
  - `python -m pytest tests\test_prompt_render_contracts.py -q`
  - `python -m pytest tests\test_studio_scene_contracts.py -q`

- [ ] Run the targeted contract tests.
- [ ] Log exactly what root contradictions were blocked.
- [ ] Commit the stage as one logical checkpoint.
- [ ] Close only the issue that is truly finished; keep the broader one open if more live sweep work remains.
