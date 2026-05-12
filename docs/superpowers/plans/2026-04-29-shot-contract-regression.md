# Shot Contract Regression Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish issue `#90` by turning the first-pass shot-lane logic into a stronger shared runtime contract for `women`, `men`, and `couples`.

**Architecture:** Extend the shared contract layer instead of scattering more bans through random render paths. Add narrow scoring pressure only where the contract still allows cheap fallback mixes through. Validate with focused contract tests and small runtime sweeps.

**Tech Stack:** Python backend, pytest regression tests, markdown project logs

---

### Task 1: Expand the shared shot contract

**Files:**
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\shot_lane_contracts.py`
- Test: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_shot_lane_contracts.py`
- Test: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_prompt_render_contracts.py`

- [ ] Add broader lane rules for premium/stylized/runtime cases that still leak cheap scene/light combinations.
- [ ] Add focused failing tests for contradictory or cheap combinations before changing implementation.
- [ ] Implement the minimal contract changes to make those tests pass.
- [ ] Run the contract-focused pytest slice.
- [ ] Commit.

### Task 2: Add runtime scoring pressure for surviving cheap fallback mixes

**Files:**
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\services\scoring.py`
- Test: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_issue91_random_quality_balance_smoke.py`
- Test: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_women_treatment_remap_smoke.py`

- [ ] Add targeted failing tests around cheap flat fallback combinations that should lose score.
- [ ] Add narrow penalties only for the still-bad treatment/scene/light combinations.
- [ ] Re-run the affected smoke tests.
- [ ] Commit.

### Task 3: Validate across live runtime slices and update logs

**Files:**
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\PROJECT_PLAN.md`
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\CHANGELOG.md`
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\TEST_LOG.md`

- [ ] Run a small live sweep for `women / men / couples`.
- [ ] Record only real remaining leaks.
- [ ] If `#90` acceptance is met, close the issue.
- [ ] Commit.
