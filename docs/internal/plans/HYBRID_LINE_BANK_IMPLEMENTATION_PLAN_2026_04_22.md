# Hybrid Line-Bank Implementation Plan - 2026-04-22

## Mission

- Add a user-editable hybrid content-bank layer based on line-oriented `.md` files.
- Keep the current structured JSON banks as the source of routing/scoring metadata that cannot safely collapse into plain text.
- Implement the first live wave only for `poses`, `expressions`, and `outfits`.
- Keep men and women on separate line-bank trees so their `poses`, `expressions`, and `outfits` do not mix.
- Keep the first live integration women-first for the modern engine path, while men stay as a separate legacy-bridge follow-up inside the same overall plan.
- Prepare a clear folder and loader contract for future `locations`, `hair`, and `makeup` without wiring those domains yet.

## Why Hybrid Instead Of Full Plain-Text Migration

Current live banks already depend on structured fields such as:

- `id`
- `tags`
- `weight`
- `status`
- `source`
- spicy gates like `high_spicy_only` and `recommended_min_spicy`
- compatibility hints such as scene/style restrictions

That means a full `one line only` migration would remove too much logic from:

- candidate selection
- scene compatibility
- spicy gating
- debug visibility
- promotion workflow

The safe direction is:

1. keep structured core banks intact
2. add a new line-bank override layer for fast user additions
3. auto-normalize line entries into structured records with conservative default metadata
4. only let the new layer participate where the current engine seam is simple enough

## Scope

### In Scope For This Wave

- line-based user banks for `poses`
- line-based user banks for `expressions`
- line-based user banks for `outfits`
- separate line-bank folders for `women` and `men`
- loader and normalization layer for those domains
- explicit project folder for user-editable line banks
- spicy-bucket organization for `1-3`, `4-5`, `6-8`
- validation rules for duplicates, blank lines, comment lines, and minimum text quality
- hard length-budget validation so line banks cannot silently bloat prompts
- tests for loader behavior and at least one end-to-end smoke check per live domain
- docs so another agent can continue without rediscovery

### Explicitly Out Of Scope For This Wave

- no full rewrite of existing JSON banks
- no changes to route/rule file formats
- no migration of `locations`, `hair`, or `makeup` into live line-banks yet
- no replacement of all structured metadata with free text
- no frontend bank editor UI
- no breaking changes to current preset/history payload shape
- no big-bang rewrite of the male legacy render path
- no live spicy-bucket behavior for men until spicy is explicitly wired into male selectors

## Safety Invariants

- If the new line-bank folders are empty, generation output must stay behaviorally unchanged.
- If line-bank loading is disabled or no valid records are found, the current generator paths must continue to work unchanged.
- Women live wiring should land first because it already runs through the modern bank-driven engine path.
- Men should use the same folder contract from day one, but live selection/render wiring must be treated as a separate legacy-bridge step.
- Couples must stay untouched in the first live wave.
- No implementation step should require replacing the existing JSON bank structure.

## Read This First After Model Switch

1. Read this file top to bottom.
2. Read `PROJECT_PLAN.md` and continue from the first unchecked item under the hybrid line-bank wave.
3. Read `backend/engine/data_loader.py` to confirm current bank merge order.
4. Read `backend/engine/candidate_builder.py` to confirm live seams for `pose_families`, `outfit_families`, and `mood_energy`.
5. Read `backend/engine/data/README.md` and preserve the existing `core / drafts / overrides` workflow.
6. Before staging, run `git status --short` and avoid unrelated dirty files.

## Current Technical Reality

### Poses

- Already live as `pose_bank.pose_families`.
- Good fit for line-bank overrides.
- Men and women should use separate line sources even if both later normalize into the same live bank shape.
- Women poses are cheap to wire because the modern candidate builder already selects `pose_bank.pose_families`.
- Men poses are not cheap to wire because the current male path still uses hardcoded string selection in `backend/legacy_people.py`.
- Minimal required synthetic metadata:
  - generated `id`
  - `value`
  - `tags`
  - `weight`
  - `status`
  - `source`
  - spicy bucket flags

### Outfits

- Already live as `styling.outfit_families`.
- Good fit for line-bank overrides.
- Men and women should use separate line sources because their outfit semantics are different.
- Women outfits are already bank-driven in the modern engine path.
- Men outfits already read from structured styling records, but they pass through a male vibe/tag filter in the legacy path.
- Needs stronger default safety than poses because outfits leak into routing and reveal logic faster.
- First pass should use conservative tags and conservative default weight.

### Expressions

- There is no dedicated live `expression` bank yet.
- Women core currently uses `composition.mood_energy`.
- Men and couples still rely heavily on legacy mood strings in `backend/legacy_people.py`.
- Men and women still need separate user banks even if the first render seam lands at different code paths.
- First pass should not try to replace all mood logic.
- Safe first pass:
  - add a dedicated line-bank domain called `expressions`
  - normalize it into a small structured bank
  - wire it as an additive prompt-part seam for women first
  - defer the men-side render seam until the legacy bridge phase
  - keep couples mood handling unchanged unless a later phase explicitly extends it

## Target Folder Contract

Create a dedicated user-editable folder under the existing override layer:

```text
backend/engine/data/overrides/line_banks/
  README.md
  women/
    poses/
      1_3.md
      4_5.md
      6_8.md
    expressions/
      1_3.md
      4_5.md
      6_8.md
    outfits/
      1_3.md
      4_5.md
      6_8.md
    locations/
      .gitkeep
    hair/
      .gitkeep
    makeup/
      .gitkeep
  men/
    poses/
      1_3.md
      4_5.md
      6_8.md
    expressions/
      1_3.md
      4_5.md
      6_8.md
    outfits/
      1_3.md
      4_5.md
      6_8.md
    locations/
      .gitkeep
    hair/
      .gitkeep
    makeup/
      .gitkeep
```

Notes:

- `locations`, `hair`, and `makeup` are placeholders only in this wave.
- `.md` is preferred over `.txt` because comments and small headers stay readable.
- one non-empty non-comment line equals one bank item.
- comments start with `#`.

## File Semantics

Example `women/poses/4_5.md`:

```md
# one item per line
leaning lightly against a railing with a playful side glance
walking mid-step and looking back over the shoulder
seated low on a sofa with one leg stretched and shoulders angled toward camera
```

Loader rules:

- ignore blank lines
- ignore lines starting with `#`
- trim outer whitespace
- preserve inner punctuation as-is
- deduplicate exact repeated lines within the same file
- report duplicates across files in validation output
- reject lines above the configured hard character cap for the domain

## Normalization Rules

Every parsed line becomes a structured record.

### Synthetic Metadata Shape For Poses

```json
{
  "id": "line_pose__women__4_5__<slug>",
  "value": "leaning lightly against a railing with a playful side glance",
  "tags": ["line_bank", "user_override", "pose", "women", "spicy_4_5"],
  "weight": 0.08,
  "status": "user_override",
  "source": "overrides/line_banks/women/poses/4_5.md",
  "recommended_min_spicy": 4,
  "recommended_max_spicy": 5
}
```

### Synthetic Metadata Shape For Outfits

```json
{
  "id": "line_outfit__women__6_8__<slug>",
  "value": "structured bustier-style top with high-waisted tailored trousers",
  "tags": ["line_bank", "user_override", "outfit", "women", "spicy_6_8", "needs_review_defaults"],
  "weight": 0.06,
  "status": "user_override",
  "source": "overrides/line_banks/women/outfits/6_8.md",
  "recommended_min_spicy": 6,
  "recommended_max_spicy": 8
}
```

### Synthetic Metadata Shape For Expressions

```json
{
  "id": "line_expression__women__1_3__<slug>",
  "value": "soft relaxed expression with a quiet confident gaze",
  "tags": ["line_bank", "user_override", "expression", "women", "spicy_1_3"],
  "weight": 0.08,
  "status": "user_override",
  "source": "overrides/line_banks/women/expressions/1_3.md",
  "recommended_min_spicy": 1,
  "recommended_max_spicy": 3
}
```

The same shape should be generated for men, with `men` in both the `id` and tags.

## Prompt-Length Budget Contract

The line-bank layer must stay inside hard prompt-budget guardrails.

Recommended first-pass caps:

- `poses`: 140 chars max per line
- `expressions`: 120 chars max per line
- `outfits`: 160 chars max per line

Recommended render caps:

- never append more than one line-bank item per domain per prompt
- never concatenate multiple user line entries into one segment
- if a selected line exceeds a safe render cap after normalization, skip it and fall back to the base path

Reason:

- users will naturally paste long cinematic phrases
- both women and legacy male prompts already concatenate multiple segments
- without hard caps, token usage will drift upward silently

## Spicy Bucket Contract

- `1-3` means safer, low-spicy pool
- `4-5` means middle lane
- `6-8` means stronger lane

The loader should derive:

- gender from the parent folder name
- domain from the next folder name
- spicy metadata from the filename

This keeps the user workflow simple:

1. choose the right folder
2. append one line
3. restart or reload

## Merge Strategy

Do not replace the existing JSON merge flow.

Instead:

1. load core JSON
2. load draft JSON if enabled
3. load existing JSON overrides if enabled
4. load line-bank overrides if enabled
5. append normalized line records into the matching live bank arrays

Required first-pass mapping:

- `line_banks/women/poses/*` -> women-eligible records inside `pose_bank.pose_families`
- `line_banks/men/poses/*` -> men-only legacy bridge render seam in `backend/legacy_people.py`
- `line_banks/women/outfits/*` -> women-eligible records inside `styling.outfit_families`
- `line_banks/men/outfits/*` -> men-only legacy bridge render seam in `backend/legacy_people.py`
- `line_banks/women/expressions/*` -> women expression seam
- `line_banks/men/expressions/*` -> men-only legacy mood seam in `backend/legacy_people.py`

Important:

- line-bank overrides should stay last in merge order so user additions can appear without touching core files
- but they should still use conservative defaults so they do not overwhelm curated content

## Proposed Backend Seams

### Loader Layer

Primary file:

- `backend/engine/data_loader.py`

Recommended extraction:

- add a helper module such as `backend/engine/line_bank_loader.py`
- keep `data_loader.py` as the orchestrator
- avoid stuffing parser logic directly into `data_loader.py`

Recommended helper functions:

- `load_line_bank_overrides()`
- `parse_line_bank_file(path)`
- `normalize_line_bank_record(domain, bucket, value, path)`
- `merge_line_bank_overrides(bank)`
- `validate_line_bank_length(domain, value)`

### Poses

Primary live seam:

- `backend/engine/candidate_builder.py`

Women live wiring should be straightforward if line items normalize into `pose_bank.pose_families` records compatible with the current selector path.

Men are different:

- the current male path chooses poses through `_choose_male_pose()` in `backend/legacy_people.py`
- that means male line-bank pose enablement is a separate bridge task, not a free side-effect of the women integration

Important:

- normalized women pose records must not leak into male pose selection
- normalized men pose records must not leak into women pose selection

### Outfits

Primary live seam:

- `backend/engine/candidate_builder.py`

Outfit line items should normalize into `styling.outfit_families` records so the current selector path can keep working.

Men are different here too:

- male outfits flow through `_male_style_items()` and `_choose_male_outfit()` in `backend/legacy_people.py`
- synthetic male outfit records will need compatible male vibe/style tags or they will never surface

Important:

- normalized women outfit records must not leak into male outfit selection
- normalized men outfit records must not leak into women outfit selection

### Expressions

Primary files:

- `backend/engine/candidate_builder.py`
- `backend/engine/render/prompt_renderer.py`
- possibly `backend/services/debug_summary.py`

Recommended first-pass design:

- keep current core mood logic intact until the new seam is proven stable
- add an optional `expression` candidate field for women
- render women expressions through controlled prompt wording rather than raw blind concatenation
- expose chosen women expression in debug output

Men legacy bridge design should be a later step because:

- `_male_mood()` is still string-based
- male prompt assembly is still legacy-segment concatenation
- adding men expressions too early creates prompt-bloat risk and doubles integration surface

Do not try to unify couples mood logic in this wave.

## Validation Rules

Validation should fail or warn on:

- unreadable file encoding
- duplicate normalized ids
- empty effective files
- lines under a minimum useful length threshold
- lines above the domain hard cap
- exact duplicates across spicy files in the same domain
- too many repeated starters inside one file if they indicate low-value spam
- total per-domain bank volume large enough to create excessive review/debug noise

Validation should not require users to write JSON.

## Phase Plan

### Phase 0 - Decision Freeze And Folder Contract

Goal: freeze the contract before code changes.

- [x] P0.1 Confirm the folder root as `backend/engine/data/overrides/line_banks/`.
- [x] P0.2 Confirm gender roots: `women/` and `men/`.
- [x] P0.3 Confirm `.md` as the first-pass file format.
- [x] P0.4 Confirm first-pass domains: `poses`, `expressions`, `outfits`.
- [x] P0.5 Confirm future placeholder domains: `locations`, `hair`, `makeup`.
- [x] P0.6 Add a small README inside the new folder explaining the one-line format.

### Phase 1 - Loader Infrastructure

Goal: parse and normalize line-based override records without changing prompt behavior yet.

- [x] P1.1 Add a dedicated line-bank loader helper module.
- [x] P1.2 Parse `.md` files by gender, domain, and spicy bucket.
- [x] P1.3 Generate stable synthetic ids.
- [x] P1.4 Map parsed lines into structured records.
- [x] P1.5 Merge normalized records into the correct men/women seams without cross-leakage.
- [x] P1.6 Add validation/report helpers for duplicates, malformed files, and overlong lines.
- [x] P1.7 Add focused loader tests.

### Phase 2 - Women Live Wiring

Goal: make the first live wave safe by wiring only the modern women path.

- [x] P2.1 Wire normalized women pose line records into the women pose path.
- [x] P2.2 Wire normalized women outfit line records into the women outfit path.
- [x] P2.3 Add an optional women expression seam without replacing `mood_energy`.
- [x] P2.4 Keep selection weights conservative.
- [x] P2.5 Add smoke tests proving custom women pose, outfit, and expression lines can surface in output.
- [x] P2.6 Check low/mid/high spicy buckets behave as intended for women.
- [x] P2.7 Check that the women live wave does not change male or couples outputs.

### Phase 3 - Men Legacy Bridge

Goal: bridge separate men line-banks into the legacy male path only after the women live wave is stable.

- [x] P3.1 Bridge men outfits into the male legacy path with compatible male vibe/style tags.
- [x] P3.2 Bridge men poses into the male legacy path through a dedicated selector seam.
- [x] P3.3 Keep men expressions deferred unless the legacy bridge remains small and token-safe.
- [x] P3.4 Do not enable men spicy-bucket routing until spicy is explicitly threaded through male selectors.
- [x] P3.5 Add smoke tests proving custom men outfit and men pose lines can surface in output.
- [x] P3.6 Recheck prompt length and style drift in male outputs.
- [x] P3.7 Check cross-gender leakage does not happen.

### Phase 4 - Men Expressions Optional Follow-Up

Goal: only add a men expression seam if the legacy bridge stays small, controlled, and token-safe.

- [x] P4.1 Re-evaluate whether men expressions justify their own live seam after Phase 3.
- [x] P4.2 If yes, add a tightly capped men expression selector.
- [x] P4.3 Render it through controlled wording only.
- [x] P4.4 Add debug visibility for the chosen men expression.
- [x] P4.5 Add smoke tests proving custom men expression lines can surface in output.
- [x] P4.6 Check cross-gender expression leakage does not happen.
- [x] P4.7 Abort this phase if prompt length or legacy-bridge complexity spikes too much.

### Phase 5 - Docs And Safety Sweep

Goal: leave the new layer easy to extend and hard to misuse.

- [x] P5.1 Update `backend/engine/data/README.md` with line-bank override workflow.
- [x] P5.2 Update `PROJECT_PLAN.md` progress items.
- [x] P5.3 Update `TEST_LOG.md` with actual executed checks.
- [x] P5.4 Add a short troubleshooting note for duplicate or malformed lines.

## Test Strategy

Minimum focused checks after each live domain:

```powershell
python -m pytest tests/test_routing_validation_smoke.py -q
```

Recommended broader backend gate after poses/outfits/expressions wiring:

```powershell
python -m pytest tests/test_public_contract_smoke.py tests/test_routing_validation_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_clothing_color_rendering_smoke.py -q
```

Additional targeted tests to add in this wave:

- loader normalization test
- duplicate-line validation test
- overlong-line validation test
- custom women pose surfacing smoke
- custom women outfit surfacing smoke
- custom women expression surfacing smoke
- custom men pose surfacing smoke
- custom men outfit surfacing smoke
- custom men expression surfacing smoke only if Phase 4 is enabled
- cross-gender leakage regression checks
- women-wave no-regression checks for current men/couples outputs

## Risks

### Main Risk 1

Synthetic outfit records may be too weakly typed and leak into bad scenes.

Mitigation:

- conservative default tags
- conservative weight
- targeted routing smoke tests

### Main Risk 2

Expressions may overlap awkwardly with existing `mood_energy` wording.

Mitigation:

- additive first pass
- controlled render template
- separate women and men render seams first

### Main Risk 3

Users may spam near-duplicate lines and lower bank quality.

Mitigation:

- duplicate validation
- README guidance
- conservative merge defaults

## Non-Blocking Recommendations Before Implementation Starts

These do not block the first coding pass, but they should be treated as preferred defaults unless the user says otherwise.

1. Keep women and men in separate folder trees from day one.
2. Keep couples extension for a second wave after the separate women/men seams are stable.
3. Keep line files metadata-free in phase 1.
4. If richer user control is needed later, add an optional sidecar format or inline lightweight syntax only after the simple workflow is proven useful.
5. Treat the male path as a legacy bridge task, not as a symmetric copy of the women integration.
6. Do not enable men spicy-bucket behavior until male selectors explicitly accept spicy.

## Done Means

This wave is complete when:

- a user can add one line to a women `poses` file and see it surface in women generation
- a user can add one line to a women `outfits` file and see it surface in women generation
- a user can add one line to a women `expressions` file and see it surface in women generation
- women live wiring leaves current men/couples behavior intact
- the loader tolerates comments and blank lines
- duplicate handling is covered by tests
- overlong lines are rejected by validation
- cross-gender leakage is covered by tests
- `locations`, `hair`, and `makeup` placeholders exist as documented future seams
- `PROJECT_PLAN.md` points back to this file as the detailed execution contract

The following are a successful follow-up bridge, not a requirement for the first live wave:

- a user can add one line to a men `poses` file and see it surface in men generation
- a user can add one line to a men `outfits` file and see it surface in men generation
- a user can add one line to a men `expressions` file and see it surface in men generation when the optional Phase 4 is explicitly completed
