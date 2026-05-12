# Line Bank Semantics And Palette Balance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Strengthen semantic matching for line-bank locations and outfits, then reduce beige and muted palette dominance in normal batch output without brittle wording hacks.

**Architecture:** Keep the fix centered in the current line-bank inference and matching layer so the generator gets better scene understanding before any scoring rebalance happens. After the semantic layer is stronger, rebalance color-story weights and muted-clone penalties so random and lifestyle batches stop collapsing into neutral-heavy output.

**Tech Stack:** Python, pytest, JSON data banks, GitHub issue/PR workflow

---

**Execution branch:** `Eugenius-S/issue56-line-bank-semantics`

**Issue handling:** Move issue `#56` to in progress before implementation starts. Keep issue `#57` open while implementing this branch, then either close it from the same PR if smoke results show the beige problem is resolved, or open a small follow-up PR only if a measurable muted-color tail remains.

### Task 1: Add Location Semantics Regression Tests

**Files:**
- Modify: `tests/test_line_bank_loader.py`
- Test: `tests/test_line_bank_loader.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_location_line_infers_extended_semantic_tags() -> None:
    terrace = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "sunlit city cafe terrace with woven chairs, striped shade and bright summer pavement",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    suite = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "sunlit hotel suite lounge with a low sofa, tall drapes and a restrained city view",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    booth = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "dim private lounge booth with mirror, lacquer and amber spill",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    cabana = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "poolside cabana threshold with pale curtains and bright coastal glare",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert {"public_like", "day_capable", "restaurant_like", "seat_friendly"} <= set(terrace["tags"])
    assert {"private_like", "home_like", "seat_friendly"} <= set(suite["tags"])
    assert {"night_capable", "private_like", "seat_friendly"} <= set(booth["tags"])
    assert {"resort_like", "wet_humid_like", "day_capable"} <= set(cabana["tags"])


def test_location_scene_matching_respects_extended_semantics() -> None:
    terrace = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "sunlit city cafe terrace with woven chairs, striped shade and bright summer pavement",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    booth = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "dim private lounge booth with mirror, lacquer and amber spill",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert line_bank_loader.line_bank_location_matches_scene(
        terrace,
        scene_family_id="urban_daylight",
        scene_tags={"outdoor", "public_elegant", "dining", "social"},
        setting_value="sunlit cafe terrace with woven chairs",
    )
    assert not line_bank_loader.line_bank_location_matches_scene(
        terrace,
        scene_family_id="grooming_bath",
        scene_tags={"spa", "private"},
        setting_value="quiet bath mirror corner",
    )
    assert line_bank_loader.line_bank_location_matches_scene(
        booth,
        scene_family_id="nightlife_bar",
        scene_tags={"social", "night", "lounge"},
        setting_value="private lacquer booth with amber lamp glow",
    )
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_line_bank_loader.py -k "extended_semantic_tags or extended_semantics" -v`

Expected: FAIL with missing tags such as `public_like`, `private_like`, `day_capable`, `night_capable`, `resort_like`, or incorrect scene-compatibility assertions.

- [ ] **Step 3: Write the minimal implementation**

```python
def infer_location_line_tags(value: str) -> set[str]:
    lowered = str(value or "").strip().lower()
    tags: set[str] = set()

    if any(token in lowered for token in ("rooftop", "terrace", "courtyard", "garden", "poolside", "boardwalk", "promenade", "marina", "cabana", "beach", "shore", "lawn", "meadow", "field", "park")):
        tags.add("outdoor_like")
    else:
        tags.add("indoor_like")

    if any(token in lowered for token in ("cafe", "restaurant", "terrace", "boardwalk", "street", "promenade", "bar", "lobby", "hotel elevator lobby")):
        tags.add("public_like")
    if any(token in lowered for token in ("bedroom", "suite", "bathroom", "vanity", "dressing room", "closet", "apartment", "living room", "kitchen", "home")):
        tags.add("private_like")
    if any(token in lowered for token in ("sunlit", "bright", "daylight", "midday", "late-morning", "afternoon", "golden-hour")):
        tags.add("day_capable")
    if any(token in lowered for token in ("dim", "lamp glow", "after-dark", "nightclub", "cocktail", "amber spill", "evening")):
        tags.add("night_capable")
    if any(token in lowered for token in ("pool", "lagoon", "beach", "shore", "spa", "shower", "humid", "coastal", "marina", "cabana")):
        tags.add("wet_humid_like")
    if any(token in lowered for token in ("chair", "chairs", "sofa", "banquette", "booth", "daybed", "bench", "lounger", "stool")):
        tags.add("seat_friendly")
    if any(token in lowered for token in ("hallway", "corridor", "walkway", "promenade", "street", "path", "turn", "lookout steps")):
        tags.add("pass_through_like")
    if any(token in lowered for token in ("bedroom", "living room", "kitchen", "apartment", "balcony", "window seat", "closet")):
        tags.add("home_like")
    if any(token in lowered for token in ("cafe", "restaurant", "cocktail lounge", "terrace", "bar deck")):
        tags.add("restaurant_like")
    if any(token in lowered for token in ("poolside", "marina", "cabana", "seaside", "boardwalk", "resort", "beach")):
        tags.add("resort_like")

    return tags


def line_bank_location_matches_scene(record: dict[str, Any], *, scene_family_id: str, scene_tags: set[str] | None = None, setting_value: str = "") -> bool:
    scene_key = str(scene_family_id or "").strip().lower()
    context_tags = {str(tag).strip().lower() for tag in (scene_tags or set())}
    tags = set(record.get("tags", [])) | infer_location_line_tags(record.get("value", ""))

    if "restaurant_like" in tags and not (context_tags & {"dining", "social", "public_elegant"} or scene_key in {"urban_daylight", "nightlife_bar"}):
        return False
    if "private_like" in tags and context_tags & {"spa", "wellness"} and "wellness_like" not in tags:
        return False
    if "pass_through_like" in tags and context_tags & {"bedroom", "spa"}:
        return False
    if "resort_like" in tags and scene_key not in {"coastal_pool", "coastal_boardwalk"}:
        return False

    return True
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/test_line_bank_loader.py -k "extended_semantic_tags or extended_semantics or repo_backed_live_location_line_banks" -q`

Expected: PASS, with all new location semantics tests green and existing location loading still green.

- [ ] **Step 5: Commit**

```bash
git add tests/test_line_bank_loader.py backend/engine/line_bank_loader.py
git commit -m "feat: strengthen line-bank location semantics"
```

### Task 2: Add Outfit Semantics Regression Tests And Matching

**Files:**
- Modify: `tests/test_line_bank_loader.py`
- Modify: `backend/engine/line_bank_loader.py`
- Test: `tests/test_line_bank_loader.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_outfit_line_infers_extended_semantic_tags() -> None:
    sundress = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "1_3",
        "light sundress with flat sandals",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "1_3.md",
        gender="women",
    )
    trousers = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "1_3",
        "linen blouse with loose trousers",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "1_3.md",
        gender="women",
    )
    robe = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "open satin robe over a matching lace set",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )
    sporty = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "1_3",
        "zip jacket with leggings and running shoes",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "1_3.md",
        gender="women",
    )

    assert {"hot_weather_ok", "casual_like"} <= set(sundress["tags"])
    assert {"indoor_neutral_ok", "restaurant_ok", "seat_friendly"} <= set(trousers["tags"])
    assert {"lounge_ok", "minimal_coverage", "dressy_like"} <= set(robe["tags"])
    assert {"active_ok", "casual_like"} <= set(sporty["tags"])


def test_outfit_scene_matching_respects_extended_semantics() -> None:
    dress = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "1_3",
        "linen blouse with a midi skirt",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "1_3.md",
        gender="women",
    )
    robe = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "open satin robe over a matching lace set",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )
    leggings = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "1_3",
        "zip jacket with leggings and running shoes",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "1_3.md",
        gender="women",
    )

    assert line_bank_loader.line_bank_outfit_matches_scene(
        dress,
        scene_family_id="urban_daylight",
        style_mode="lifestyle",
        scene_tags={"public_elegant", "dining", "social"},
        setting_value="sunlit cafe terrace with woven chairs",
    )
    assert not line_bank_loader.line_bank_outfit_matches_scene(
        robe,
        scene_family_id="urban_daylight",
        style_mode="lifestyle",
        scene_tags={"public_elegant", "dining", "social"},
        setting_value="sunlit cafe terrace with woven chairs",
    )
    assert not line_bank_loader.line_bank_outfit_matches_scene(
        leggings,
        scene_family_id="nightlife_bar",
        style_mode="nightlife",
        scene_tags={"night", "social", "dining"},
        setting_value="velvet booth with low lamp glow",
    )
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_line_bank_loader.py -k "outfit_line_infers_extended or outfit_scene_matching_respects_extended" -v`

Expected: FAIL with missing tags such as `hot_weather_ok`, `restaurant_ok`, `lounge_ok`, `active_ok`, or public/private gating mismatches.

- [ ] **Step 3: Write the minimal implementation**

```python
def infer_outfit_line_tags(value: str) -> set[str]:
    lowered = str(value or "").strip().lower()
    tags: set[str] = set()

    if any(token in lowered for token in ("tank", "shorts", "sundress", "sandals", "bikini coverup", "sleeveless")):
        tags.add("hot_weather_ok")
    if any(token in lowered for token in ("blouse", "trousers", "knit", "midi skirt", "polo", "button shirt")):
        tags.add("indoor_neutral_ok")
    if any(token in lowered for token in ("robe", "slip dress", "soft knit set", "lounge set", "lace set")):
        tags.add("lounge_ok")
    if any(token in lowered for token in ("dress", "blouse", "tailored trousers", "midi skirt", "heels")):
        tags.add("restaurant_ok")
    if any(token in lowered for token in ("leggings", "running shoes", "workout", "sport", "shorts")):
        tags.add("active_ok")
    if any(token in lowered for token in ("bikini", "bra", "panties", "sheer", "open satin robe", "deep-cut", "lace set")):
        tags.add("minimal_coverage")
    if any(token in lowered for token in ("jacket", "cardigan", "coat", "overshirt", "blazer", "robe")):
        tags.add("layered_like")
    if any(token in lowered for token in ("satin", "tailored", "heels", "evening", "lace set", "midi skirt")):
        tags.add("dressy_like")
    if any(token in lowered for token in ("tee", "tank", "denim", "simple shirt", "casual", "sundress", "leggings")):
        tags.add("casual_like")
    if any(token in lowered for token in ("midi skirt", "trousers", "knit set", "soft skirt", "slip dress")):
        tags.add("seat_friendly")

    return tags


def line_bank_outfit_matches_scene(record: dict[str, Any], *, scene_family_id: str, style_mode: str = "random", scene_tags: set[str] | None = None, setting_value: str = "") -> bool:
    scene_key = str(scene_family_id or "").strip().lower()
    lowered_setting = str(setting_value or "").strip().lower()
    context_tags = {str(tag).strip().lower() for tag in (scene_tags or set())}
    tags = set(record.get("tags", [])) | infer_outfit_line_tags(record.get("value", ""))

    publicish_context = bool(
        context_tags & {"public_elegant", "travel", "urban", "street", "dining", "social"}
        or any(token in lowered_setting for token in ("restaurant", "cafe", "lobby", "street", "bar", "terrace"))
    )

    if "restaurant_ok" in tags and scene_key == "nightlife_bar" and "dressy_like" not in tags:
        return False
    if "active_ok" in tags and (context_tags & {"dining", "public_elegant"}):
        return False
    if "lounge_ok" in tags and publicish_context and style_mode not in {"nightlife", "studio"}:
        return False
    if "minimal_coverage" in tags and publicish_context and style_mode not in {"nightlife", "studio", "coastal"}:
        return False
    if "hot_weather_ok" in tags and scene_key in {"grooming_bath", "residential_luxury"} and "indoor_neutral_ok" not in tags:
        return False

    return True
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/test_line_bank_loader.py -k "outfit_line_infers_extended or outfit_scene_matching_respects_extended or outfit_line_tags_and_scene_guardrails" -q`

Expected: PASS, with new outfit semantics tests green and existing outfit guardrails unchanged.

- [ ] **Step 5: Commit**

```bash
git add tests/test_line_bank_loader.py backend/engine/line_bank_loader.py
git commit -m "feat: strengthen line-bank outfit semantics"
```

### Task 3: Rebalance Muted Color Stories And Tighten Clone Penalties

**Files:**
- Create: `tests/test_issue57_muted_palette_balance_smoke.py`
- Modify: `backend/engine/data/styling.json`
- Modify: `backend/services/scoring.py`
- Test: `tests/test_issue57_muted_palette_balance_smoke.py`
- Test: `tests/test_issue41_random_balance_smoke.py`
- Test: `tests/test_clothing_color_rendering_smoke.py`

- [ ] **Step 1: Write the failing smoke test**

```python
from collections import Counter

from backend.prompt_service import _merged_form_state, generate_run


CLONE_PRONE_MUTED = {
    "clean_neutrals",
    "champagne_taupe",
    "rosewood_smoke",
}


def _run_random_women_color_stats(seed: int) -> tuple[Counter[str], int]:
    state = _merged_form_state(
        {
            "mode": "women",
            "batchSize": 20,
            "debugMode": "on",
            "styleMode": "random",
            "spicyLevel": "6",
            "antiRepeat": "hard",
            "seed": str(seed),
        }
    )
    result = generate_run(state)
    prompts = result["prompts"]
    colors = Counter(prompt["candidate"].get("color_story_id") for prompt in prompts if prompt.get("candidate"))
    findings = sum(len(prompt.get("findings", [])) for prompt in prompts)
    return colors, findings


def test_random_women_batches_reduce_muted_palette_dominance() -> None:
    aggregate = Counter()
    findings_total = 0

    for seed in range(8):
        colors, findings = _run_random_women_color_stats(seed)
        aggregate.update(colors)
        findings_total += findings

    total = sum(aggregate.values())
    clone_prone_muted_total = sum(aggregate[color_id] for color_id in CLONE_PRONE_MUTED)

    assert findings_total == 0
    assert aggregate["clean_neutrals"] / total <= 0.18
    assert clone_prone_muted_total / total <= 0.30
    assert len([color_id for color_id, count in aggregate.items() if count >= 4]) >= 5
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_issue57_muted_palette_balance_smoke.py -v`

Expected: FAIL because `clean_neutrals` and clone-prone muted colors still take too large a share of total output.

- [ ] **Step 3: Write the minimal implementation**

```json
"color_stories": [
  {"id": "clean_neutrals", "weight": 0.28},
  {"id": "powder_blue", "weight": 0.30},
  {"id": "navy_cream", "weight": 0.30},
  {"id": "earthy_soft", "weight": 0.22},
  {"id": "winter_neutrals", "weight": 0.14},
  {"id": "chocolate_cream", "weight": 0.15},
  {"id": "champagne_taupe", "weight": 0.12},
  {"id": "rosewood_smoke", "weight": 0.11},
  {"id": "soft_camel_cream", "weight": 0.10},
  {"id": "dusty_rose_taupe", "weight": 0.08}
]
```

```python
def _muted_color_clone_penalty(batch: list[dict[str, Any]], style_mode: str, mode: str) -> int:
    if mode not in {"women", "couples"}:
        return 0
    style_caps = {
        "random": {"combined": 4, "per_color": 2, "combined_penalty": 14, "per_color_penalty": 12},
        "lifestyle": {"combined": 4, "per_color": 2, "combined_penalty": 14, "per_color_penalty": 12},
        "luxury": {"combined": 3, "per_color": 2, "combined_penalty": 16, "per_color_penalty": 14},
    }
    ...


if form_state["styleMode"] == "random":
    random_clean_neutral_count = sum(1 for candidate in batch if candidate.get("color_story_id") == "clean_neutrals")
    if form_state["mode"] == "women" and random_clean_neutral_count > 3:
        score -= (random_clean_neutral_count - 3) * 12

if form_state["styleMode"] == "lifestyle":
    lifestyle_clean_neutral_count = sum(1 for candidate in batch if candidate.get("color_story_id") == "clean_neutrals")
    if lifestyle_clean_neutral_count > 4:
        score -= (lifestyle_clean_neutral_count - 4) * 12

if form_state["styleMode"] == "luxury":
    luxury_clean_neutral_count = sum(1 for candidate in batch if candidate.get("color_story_id") == "clean_neutrals")
    if luxury_clean_neutral_count > 3:
        score -= (luxury_clean_neutral_count - 3) * 12
```

- [ ] **Step 4: Run the focused validation suite**

Run: `pytest tests/test_issue57_muted_palette_balance_smoke.py tests/test_issue41_random_balance_smoke.py tests/test_clothing_color_rendering_smoke.py -q`

Expected: PASS, with muted-color dominance reduced, random balance still intact, and outfit color rendering unaffected.

- [ ] **Step 5: Commit**

```bash
git add tests/test_issue57_muted_palette_balance_smoke.py backend/engine/data/styling.json backend/services/scoring.py
git commit -m "feat: rebalance muted palette selection"
```

### Task 4: Final Verification, Project Logs, And GitHub Status Updates

**Files:**
- Modify: `CHANGELOG.md`
- Modify: `TEST_LOG.md`
- Modify: `PROJECT_PLAN.md`

- [ ] **Step 1: Update project logs**

```markdown
## [Unreleased]
- strengthen line-bank location and outfit semantics for scene-aware matching
- reduce muted color-story dominance in random and lifestyle batches
```

```markdown
2026-04-25
- `pytest tests/test_line_bank_loader.py -q` -> PASS
- `pytest tests/test_issue57_muted_palette_balance_smoke.py tests/test_issue41_random_balance_smoke.py tests/test_clothing_color_rendering_smoke.py -q` -> PASS
```

```markdown
- Issue #56: in progress -> done after merge
- Issue #57: validate from same branch; close only if muted-balance smoke stays green after merge
```

- [ ] **Step 2: Run the final verification bundle**

Run: `pytest tests/test_line_bank_loader.py tests/test_issue57_muted_palette_balance_smoke.py tests/test_issue41_random_balance_smoke.py tests/test_clothing_color_rendering_smoke.py -q`

Expected: PASS with no new failures.

- [ ] **Step 3: Push branch and open PR**

```bash
git push -u origin Eugenius-S/issue56-line-bank-semantics
gh pr create --title "Strengthen line-bank semantics and rebalance muted palettes" --body "## Summary
- strengthen inferred semantics for line-bank locations and outfits
- improve scene-aware line-bank matching
- rebalance muted color stories and clone penalties

## Test Plan
- [x] pytest tests/test_line_bank_loader.py -q
- [x] pytest tests/test_issue57_muted_palette_balance_smoke.py tests/test_issue41_random_balance_smoke.py tests/test_clothing_color_rendering_smoke.py -q

Closes #56
Refs #57"
```

- [ ] **Step 4: Update issue status after PR creation**

```bash
gh issue comment 56 --body "Implementation branch is up and PR is open for semantic matching improvements and muted palette rebalance."
gh issue comment 57 --body "Muted palette dominance is being validated from the #56 branch. Closing from that PR only if the focused smoke remains green."
```

- [ ] **Step 5: Commit remaining log changes**

```bash
git add CHANGELOG.md TEST_LOG.md PROJECT_PLAN.md
git commit -m "docs: record semantics and palette balance verification"
```

## Self-Review

- Spec coverage: Task 1 and Task 2 implement the new semantic classification and matching requirements from issue `#56`. Task 3 applies the required structural muted-palette rebalance for issue `#57`. Task 4 covers verification and the requested issue/PR status updates.
- Placeholder scan: No `TODO`, `TBD`, or undefined commands remain. Every task has concrete files, code snippets, and verification commands.
- Type consistency: The plan uses the current names `infer_location_line_tags`, `infer_outfit_line_tags`, `line_bank_location_matches_scene`, `line_bank_outfit_matches_scene`, `_muted_color_clone_penalty`, and the real test file paths already present in the repository.
