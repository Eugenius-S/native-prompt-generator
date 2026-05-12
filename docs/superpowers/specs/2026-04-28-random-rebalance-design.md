# Random Rebalance Design

## Goal

Fix `random` mode at the root so it stops collapsing into muted indoor standing shots with cheap flat light.

Target output mix:

- `outdoor 60% / indoor 40%`
- `bright-sunny 70% / muted-overcast 30%`
- `water` and `nature` should be first-class random buckets, not rare tails
- standing poses should no longer dominate batches
- cheap flat light should be actively suppressed in random mode

## Problem Summary

Current random behavior is drifting for five linked reasons:

1. Candidate build still treats outdoor as one broad group, so water/nature are not protected shares.
2. Bright-vs-muted balance exists, but it is still too easy for safe commercial / indoor / flat-light candidates to pass.
3. Pose variety is partly protected, but random still over-surfaces standing and upper-body-friendly setups.
4. Shot-lane contracts removed hard contradictions, but they do not yet guarantee a lively random mix.
5. Batch scoring and candidate selection are both active, but the pressure is not aligned tightly enough around random.

## Chosen Approach

Use a narrow combined fix:

1. Tighten candidate-build schedules.
2. Add explicit water/nature grouping inside random.
3. Add batch-level penalties for interior-heavy, muted-heavy, standing-heavy, and cheap-light-heavy batches.

This is preferred over scoring-only or builder-only changes because it fixes both supply and selection pressure without redesigning the whole engine.

## Design

### 1. Random scene schedule

Replace the coarse random scene split with an explicit schedule:

- `indoor: 40%`
- `urban_outdoor: 20%`
- `water: 20%`
- `nature: 20%`

Definitions:

- `water` includes `pool`, `beach`, `shore`, `marina`, `lagoon`, `boardwalk`, `waterside`
- `nature` includes `garden`, `park`, `meadow`, `field`, `grove`, `flowers`, `green natural spaces`
- `urban_outdoor` includes terraces, city streets, plazas, promenades, open-air hospitality, and other non-water, non-nature outdoor scenes

Candidate generation must actively match the scheduled scene group instead of letting all outdoor-capable scenes compete equally.

### 2. Random light schedule

Keep the target:

- `bright: 70%`
- `muted: 30%`

But define `bright` more strictly through a combined signal:

- bright lighting family
- bright treatment lane
- bright atmosphere cue
- daylight / sunny scene tags

Also define a random-only cheap-light class for:

- overly safe `soft clean commercial` style outcomes
- flat low-energy daylight
- cautious interior commercial fallback

These should be penalized at batch level even if they pass basic compatibility checks.

### 3. Random pose schedule

Protect pose variety with explicit random targets:

- `standing: 45%`
- `seated: 30%`
- `reclined_or_lowered: 25%`

Random generation should not rely only on general pose-group balance. It needs a random-specific cap so standing cannot dominate the batch after later selection pressure.

### 4. Random batch scoring hardening

Add random-only batch penalties for:

- too many indoor candidates
- too many muted candidates
- too few `water` candidates
- too few `nature` candidates
- too many standing poses
- too many cheap-flat-light candidates

These penalties must stay narrow to `styleMode=random` so exact-theme and other controlled modes are not distorted.

### 5. Scope boundaries

This pass does not:

- redesign the global shot-lane architecture
- change explicit non-random style modes
- rewrite line-bank content
- add live broad batch sweeps before the narrow regression checks are in place

## Components

Expected touch points:

- `backend/engine/candidate_builder.py`
  - random scene scheduling
  - random light scheduling
  - random pose scheduling if this is where schedule pressure is easiest to enforce
- `backend/services/scoring.py`
  - random-only batch penalties for scene/light/pose balance
- tests
  - focused seeded smokes for scene-group, light, and pose distribution

## Validation

Required checks:

1. seeded random scene-balance smoke
2. seeded random bright-vs-muted smoke
3. seeded random pose-balance smoke
4. one narrow live sanity pass only after the regression checks are green

Success looks like:

- random no longer reads mostly indoor / muted / standing
- water and nature are visibly present in normal random batches
- bright sunny outputs are the dominant default
- cheap flat light becomes an exception rather than the center of gravity

## Risks

- Over-pushing outdoor can make indoor scenes feel too rare.
- Over-pushing bright light can make some random outputs look repetitive if treatment diversity is not preserved.
- Forcing pose quotas too hard can weaken scene coherence if seated/reclined candidates are not filtered carefully enough.

Mitigation:

- keep all new pressure narrow to `random`
- use modest quotas plus batch caps instead of hard per-item forcing wherever possible
- validate with seeded tests before live tuning
