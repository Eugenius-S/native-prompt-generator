# Random Rebalance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebalance `styleMode=random` so it defaults to brighter outdoor-heavy batches with visible water/nature presence, better pose variety, and less cheap flat light.

**Architecture:** Keep the fix narrow and root-cause-oriented. Tighten `candidate_builder` so random generation schedules explicit scene/light/pose targets, then harden `scoring` with random-only batch penalties so safe indoor standing commercial fallbacks stop dominating the final selection.

**Tech Stack:** Python backend, pytest smoke tests, existing `generate_run()` seeded regression pattern.

---

### Task 1: Lock the expected random scene mix in tests

**Files:**
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_issue41_random_balance_smoke.py`
- Test: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_issue41_random_balance_smoke.py`

- [ ] **Step 1: Write the failing test**

Add explicit random group assertions on top of the current outdoor/indoor check:

```python
def test_random_modes_keep_scene_and_light_balance():
    for mode in ("women", "men", "couples"):
        scene_groups, bright_count, findings_count = _random_run_stats(mode)
        assert findings_count == 0
        assert scene_groups["outdoor"] >= 12
        assert scene_groups["indoor"] <= 8
        assert scene_groups["water"] >= 3
        assert scene_groups["nature"] >= 3
        assert bright_count >= 13
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_issue41_random_balance_smoke.py -q`
Expected: FAIL because `water` / `nature` keys are not produced yet or current random mix under-hits them.

- [ ] **Step 3: Write minimal implementation**

In `backend/engine/candidate_builder.py`, expand `_random_scene_group()` so it can classify:

```python
def _random_scene_group(candidate: dict[str, Any]) -> str:
    tags = set(candidate.get("tags", [])) | set(candidate.get("setting_tags", []))
    text = " ".join(
        str(candidate.get(field, "") or "")
        for field in ("line_bank_location", "setting_scene", "setting_micro")
    ).lower()
```

and then return one of:

```python
"water"
"nature"
"urban_outdoor"
"outdoor"
"indoor"
```

with `pool / beach / shore / marina / lagoon / boardwalk / coastal` mapped to `water`, and `garden / park / meadow / field / grove / flowers / greenhouse / conservatory` mapped to `nature`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_issue41_random_balance_smoke.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_issue41_random_balance_smoke.py backend/engine/candidate_builder.py
git commit -m "Add explicit random scene-group balance targets"
```

### Task 2: Make candidate generation schedule water/nature explicitly

**Files:**
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\engine\candidate_builder.py`
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_issue84_random_sunlight_smoke.py`
- Test: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_issue84_random_sunlight_smoke.py`

- [ ] **Step 1: Write the failing test**

Tighten the multi-seed random sunlight smoke so it also requires visible `water` and `nature` share:

```python
def test_random_modes_favor_outdoors_and_sunlight() -> None:
    seeds = (71000111, 72000222, 73000333, 74000444, 75000555)
    for mode in ("women", "men", "couples"):
        scene_groups, bright_count, prompt_count = _collect_random_light_stats(mode, seeds)
        assert prompt_count == len(seeds) * 20
        assert scene_groups["outdoor"] >= 60
        assert scene_groups["water"] >= 12
        assert scene_groups["nature"] >= 12
        assert bright_count >= 70
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_issue84_random_sunlight_smoke.py -q`
Expected: FAIL with current random schedule under-serving `water` and `nature`.

- [ ] **Step 3: Write minimal implementation**

Replace the coarse schedule in `_build_random_balance_schedules()`:

```python
scene_counts = selectors._allocate_counts(
    count,
    {"indoor": 0.4, "urban_outdoor": 0.2, "water": 0.2, "nature": 0.2},
)
scene_schedule = selectors._build_group_schedule(scene_counts, max_same_in_row=2, rnd=rnd)
```

Then add a matcher helper:

```python
def _random_scene_group_matches(candidate: dict[str, Any], expected_group: str) -> bool:
    actual = _random_scene_group(candidate)
    if expected_group == "outdoor":
        return actual in {"urban_outdoor", "water", "nature", "outdoor"}
    return actual == expected_group
```

and keep random enforcement inside `generate_batch()` using the new explicit schedule.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_issue84_random_sunlight_smoke.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/engine/candidate_builder.py tests/test_issue84_random_sunlight_smoke.py
git commit -m "Schedule water and nature explicitly in random mode"
```

### Task 3: Clamp standing dominance with a random-specific pose balance gate

**Files:**
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\engine\candidate_builder.py`
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_issue87_random_pose_variety_smoke.py`
- Test: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_issue87_random_pose_variety_smoke.py`

- [ ] **Step 1: Write the failing test**

Update the pose variety smoke toward the approved random targets:

```python
def test_random_modes_keep_seated_and_lying_poses_visible() -> None:
    seeds = (71000111, 72000222, 73000333, 74000444, 75000555)
    for mode in ("women", "men", "couples"):
        for seed in seeds:
            groups = _random_pose_group_stats(mode, seed)
            assert groups["standing"] <= 9
            assert groups["seated"] >= 5
            assert groups["lying"] >= 2
            assert groups["standing"] < groups["seated"] + groups["lying"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_issue87_random_pose_variety_smoke.py -q`
Expected: FAIL in seeds where random still collapses into standing-heavy batches.

- [ ] **Step 3: Write minimal implementation**

In `generate_batch()`, add a random-only pose schedule separate from the generic pose-group target share:

```python
random_pose_group_schedule = selectors._build_group_schedule(
    selectors._allocate_counts(count, {"standing": 0.45, "seated": 0.30, "lying": 0.25}),
    max_same_in_row=2,
    rnd=rnd,
)
```

Then pass the scheduled group instead of the generic one when:

```python
style_mode == "random" and not required_scene_families and not preferred_scene_families
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_issue87_random_pose_variety_smoke.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/engine/candidate_builder.py tests/test_issue87_random_pose_variety_smoke.py
git commit -m "Clamp standing-heavy pose drift in random mode"
```

### Task 4: Add random-only batch penalties for muted/interior/cheap-light overload

**Files:**
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\backend\services\scoring.py`
- Create: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_issue91_random_quality_balance_smoke.py`
- Test: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\tests\test_issue91_random_quality_balance_smoke.py`

- [ ] **Step 1: Write the failing test**

Create a new focused smoke that checks the overall random quality mix over fixed seeds:

```python
def test_random_mode_limits_interior_muted_and_cheap_light_overload() -> None:
    stats = _collect_random_quality_stats("women", (71000111, 72000222, 73000333, 74000444, 75000555))
    assert stats["interior"] <= 40
    assert stats["muted"] <= 30
    assert stats["cheap_light"] <= 25
```

with helpers that count:

- interior via `candidate_builder._random_scene_group(candidate) == "indoor"`
- muted via `not candidate_builder._is_random_bright_candidate(candidate)`
- cheap light via a new scoring helper keyed off safe flat commercial combinations

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_issue91_random_quality_balance_smoke.py -q`
Expected: FAIL with current random overload.

- [ ] **Step 3: Write minimal implementation**

Add random-only helpers in `backend/services/scoring.py`:

```python
def _random_flat_light_candidate(candidate: dict[str, Any]) -> bool:
    return (
        candidate.get("photo_treatment_id") in {"clean_commercial", "casual_indoor_selfie"}
        and candidate.get("lighting_family_id") in {"clean_daylight", "soft_overcast", "warm_interior"}
        and candidate.get("scene_family_id") in {"residential_luxury", "hospitality_suite", "culture_bookish", "garden_conservatory"}
    )
```

and a batch penalty:

```python
def _random_quality_balance_score(batch: list[dict[str, Any]]) -> int:
    ...
```

that penalizes:

- too many indoor candidates
- too many muted candidates
- too few `water`
- too few `nature`
- too many `standing`
- too many cheap-flat-light candidates

Then wire it into `_batch_score()` only for:

```python
if form_state["styleMode"] == "random":
    score += _random_quality_balance_score(batch)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_issue91_random_quality_balance_smoke.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/services/scoring.py tests/test_issue91_random_quality_balance_smoke.py
git commit -m "Penalize flat interior random batches"
```

### Task 5: Run the narrow regression pack and update project tracking

**Files:**
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\PROJECT_PLAN.md`
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\CHANGELOG.md`
- Modify: `C:\Users\jiraf\Documents\ComfyUI\!Prompt Generator\TEST_LOG.md`

- [ ] **Step 1: Run the focused regression pack**

Run:

```bash
python -m pytest tests/test_issue41_random_balance_smoke.py tests/test_issue84_random_sunlight_smoke.py tests/test_issue87_random_pose_variety_smoke.py tests/test_issue91_random_quality_balance_smoke.py -q
```

Expected: PASS.

- [ ] **Step 2: Run one narrow live sanity pass**

Run a single fixed-seed women random batch and inspect only aggregate symptoms:

```bash
python -m pytest tests/test_issue41_random_balance_smoke.py -q
```

Expected: scene and light mix stay inside the new targets without new hard findings.

- [ ] **Step 3: Update project status**

Add one completed line under the active random-quality issue in:

```md
- [x] rebalance random toward brighter outdoor-heavy batches with explicit water/nature shares, better pose variety, and less flat commercial fallback
```

- [ ] **Step 4: Commit**

```bash
git add PROJECT_PLAN.md CHANGELOG.md TEST_LOG.md
git commit -m "Log random rebalance validation"
```
