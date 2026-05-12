# Issue 105 Implementation Plan

## Scope

Issue `#105` covers impossible or nonsensical scene / pose / outfit combinations that still survive candidate selection after the first support-aware pose pass.

Checked failures behind this plan:

- bed-anchored pose leaking into courtyard / outdoor scenes without real bed support
- vanity / counter / perch pose leaking into boxing-gym scenes
- shoreline / near-water reclining or lying poses pairing with clearly dry, non-wet-friendly outfit lanes

This plan intentionally treats the problem as a shared coherence layer, not as three unrelated one-off bugs.

## Design Constraints

1. Line banks are open-ended.
   - `women/poses/*.md` and `shared/locations/*.md` can grow arbitrarily.
   - The fix must keep working when new pose or location lines are added without another hardcoded Python branch.

2. Static and dynamic paths should share one vocabulary.
   - Static pose selection currently flows through `backend/engine/selectors.py` and mirrored helper logic in `backend/engine/generator.py`.
   - Dynamic line-bank pose/location matching already infers support semantics in `backend/engine/line_bank_loader.py`.
   - The plan should reduce the semantic gap between those paths instead of widening it.

3. Late validation is a backstop, not the primary matcher.
   - Candidate selection should reject obviously wrong combinations early.
   - Validator / repair should only catch residual leaks, not become the main routing mechanism.

4. `#98` remains separate.
   - `#105` is about prop-aware scene / pose / outfit matching.
   - Framing-only cleanup stays in `#98` unless a finding is clearly a framing-contract issue rather than a scene/pose coherence issue.

## Chosen Hybrid Strategy

This implementation should combine:

- `2 + 3`: data-driven pose support contract, aligned with the line-bank support taxonomy
- `4`: explicit dry-coastal vs water-contact split for outfit matching
- `5`: validator / repair backstop for any residual impossible combinations

This is deliberately preferred over adding more `if pose_id == ...` branches.

## Target Architecture

### 1. Shared Support And Context Taxonomy

Create one shared vocabulary for pose / scene / outfit matching, reused by both the static selector path and the line-bank path.

Minimum required tags / concepts:

- support tags: `bed_support`, `chair_support`, `bench_support`, `sofa_support`, `counter_support`, `cabinet_support`, `stairs_support`, `floor_support`
- posture tags: `standing_like`, `seated_like`, `lying_like`, `ground_low_like`
- water-context tags: `dry_coastal`, `wet_context`, `water_contact`, `shoreline_contact`, `pool_edge`, `beach_waterline`

Implementation direction:

- keep `line_bank_loader.infer_pose_line_tags(...)` as the reference language for open-ended markdown banks
- add shared helper functions so `selectors.py` and `generator.py` can infer the same semantics for static `pose_bank.json` entries and base spaces
- avoid introducing a second incompatible tag language

### 2. Data-Driven Pose Contract

Extend static pose handling so required support is inferred from pose tags and optional contract fields, not mostly from pose ids.

Preferred direction:

- enrich `backend/engine/data/pose_bank.json` with optional contract fields such as:
  - `required_support_tags`
  - `allowed_scene_tags`
  - `banned_scene_tags`
  - `water_contact_pose`
  - `dry_only_pose`
- where possible, derive these from existing tags first (`bed`, `floor_or_bed`, `sofa_or_bed`, `perched`, `pool_edge`)
- only add explicit contract fields where plain tag inference is not enough

Goal:

- new or newly edited pose entries should become routable through data, not through a new hardcoded selector branch every time

### 3. Static Selector Refactor

Refactor `_pose_for_base_space(...)` in `backend/engine/selectors.py` to evaluate a generalized pose contract.

Expected flow:

1. infer scene support tags from the base space
2. infer scene context tags including indoor/outdoor, public/private, dry/wet coastal, etc.
3. infer pose support/context contract from the static pose record
4. reject on missing support
5. reject on banned context
6. reject on water-contact mismatch
7. keep a small exception list only for genuinely exceptional poses

Keep mirrored helper logic in `backend/engine/generator.py` aligned in the same pass.

### 4. Dry Coastal vs Water-Contact Outfit Matching

The current coastal/pool outfit gate is too broad for shoreline body-contact poses.

Planned split:

- `dry coastal ambience`
  - boardwalk / terrace / poolside standing or seated poses can still allow non-swimwear feminine or dressy outfits
- `water-contact coastal`
  - poses that are effectively in the water, at the waterline, prone on wet shore, or reclining into surf must require wet-friendly outfit lanes

Implementation direction:

- add a helper that classifies the scene+pose pair as either dry coastal or water-contact coastal
- thread that classification into outfit-family matching in `selectors.py`
- prefer `swimwear`, `wet-friendly`, and narrow soft-coastal lanes for water-contact poses
- reject obviously dry / heavy / wrong-read outfit families in water-contact contexts

### 5. Validator / Repair Backstop

Add a final safety net in:

- `backend/engine/validator.py`
- `backend/engine/repair.py`

Candidate finding classes to add if needed:

- `pose_requires_missing_support`
- `water_contact_pose_without_wet_outfit`
- `perch_pose_in_wrong_scene_context`

Repair should stay conservative.

Preferred behavior:

- if a candidate is fundamentally impossible, do not invent fake support props in repair
- only perform safe normalization when the mismatch is cosmetic rather than structural
- allow strict validation mode to reject these combinations outright

## Implementation Phases

### Phase 1. Regression Anchors First

Add focused tests before changing matcher logic.

Required first-pass coverage:

- courtyard + bed-anchored pose must fail
- boxing gym + vanity/counter/perch pose must fail
- shoreline / near-water lying pose + clearly dry outfit must fail
- control pairs must still pass:
  - bedroom / suite + bed pose
  - true vanity / counter context + perch pose
  - dry coastal standing pose + non-swimwear outfit where appropriate

Test surfaces:

- new `tests/test_issue105_prop_scene_outfit_matching_smoke.py`
- extend `tests/test_line_bank_loader.py` where shared taxonomy inference needs coverage
- extend `tests/test_issue104_support_pose_matching_smoke.py` only if the new checks are still direct continuations of issue 104

### Phase 2. Shared Taxonomy Helpers

Move or duplicate the smallest possible helper set so the following agree on semantics:

- `backend/engine/line_bank_loader.py`
- `backend/engine/selectors.py`
- `backend/engine/generator.py`

The intent is not a giant refactor first. The intent is to get one coherent support/wet vocabulary into all three paths.

### Phase 3. Selector Contract Pass

Replace the current pose-id-heavy special casing with a generalized contract evaluator.

Keep these rules:

- explicit support mismatch is an early hard reject
- public or outdoor scenes should reject bed/vanity/counter poses unless the required support is actually present and contextually sensible
- kneeling / lying / perched poses should not pass just because a broad scene tag like `coastal` or `wellness` is present

### Phase 4. Water-Contact Outfit Gate

Add the dry-vs-wet coastal split and make it influence outfit-family eligibility.

Needed outputs:

- no more lying-near-water + wrong dry editorial outfit combos
- still preserve legitimate dry beach / terrace / boardwalk outfits when the pose is not water-contact

### Phase 5. Validator Backstop

After selector changes, add the validator findings only for residual leak classes that still matter.

This phase should stay small if phases 2 to 4 are done correctly.

## Files Expected To Move

- `backend/engine/selectors.py`
- `backend/engine/generator.py`
- `backend/engine/line_bank_loader.py`
- `backend/engine/data/pose_bank.json`
- `backend/engine/validator.py`
- `backend/engine/repair.py`
- `tests/test_issue104_support_pose_matching_smoke.py`
- `tests/test_line_bank_loader.py`
- `tests/test_issue105_prop_scene_outfit_matching_smoke.py`

## Validation Plan

Minimum required local validation after implementation:

1. focused issue-105 smoke suite
2. `tests/test_issue104_support_pose_matching_smoke.py`
3. relevant `tests/test_line_bank_loader.py` selectors / inference cases
4. one coastal-scene coherence slice if outfit gating changes materially widen or narrow the pool

Live prompt review after the code pass should explicitly re-check the three reported examples plus one control example per class.

## Non-Goals

- not a broad framing rewrite; that remains with `#98`
- not a full rewrite of all static pose metadata in one pass
- not a global validator overhaul unrelated to prop/support/wet-context coherence

## Recommended Commit Slices

1. tests and shared taxonomy helpers
2. selector + generator contract pass
3. water-contact outfit gate
4. validator/repair backstop and log updates

This keeps the work reviewable and lets each stage be locally revalidated before the next one.
