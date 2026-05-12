## Summary

Random output regressed in four linked ways:

1. scene mix became too narrow, with repeated conservatory / greenhouse style backdrops
2. women random pose mix drifted toward modest or lowered poses
3. outfit color spread collapsed into a small recurring set
4. women expression banks lost overt happy / radiant expressions

This pass restores variety through systemic batch-pressure first, then line-bank support.

## Goals

- restore stronger random scene variety
- reduce conservatory / greenhouse repetition
- target random women pose mix:
  - standing or walking: 65
  - seated: 20
  - lower or reclined: 15
- reduce passport-like pose repetition
- widen random color spread so the same 5-7 color stories do not dominate a batch
- add a small set of clearly happy women expressions without any winks

## Non-Goals

- no full rewrite of scoring or selector architecture
- no manual one-off bans for isolated prompts
- no broad rework of men or couples banks unless a shared helper must change

## Approach Options

### Option 1: scoring-only

Adjust only batch penalties and random scoring weights.

Pros:
- fast
- low file churn

Cons:
- weak if women pose and expression banks stay skewed
- easy to regress later

### Option 2: line-banks only

Only expand or rebalance women poses and expressions.

Pros:
- improves source variety

Cons:
- weak against scene and color lock-in already happening above the banks

### Option 3: combined systemic pass

Use scoring and motif pressure to reopen variety, then update women pose and expression banks so the source pool supports that target.

Pros:
- treats the actual root across scenes, colors, and poses
- stable against later line-bank growth

Cons:
- touches both scoring and bank files

Recommended: Option 3.

## Design

### 1. Scene Mix Hardening

Random batches should not over-repeat a single broad motif, especially `garden_nature`, and should push back harder against `conservatory` / `greenhouse` wording.

Changes:
- tighten location motif penalties for repeated `garden_nature`
- add a stronger focus-cap specifically for conservatory / greenhouse style locations
- rebalance random pressure toward a healthier spread across:
  - waterside
  - urban_social
  - interior_lounge
  - nightlife
  - garden_nature

This stays systemic: not a ban on one backdrop, but a lower tolerance for duplicate motif families.

### 2. Women Random Pose Mix

Random needs a stronger vertical bias.

Target mix:
- standing/walking: 65
- seated: 20
- lower/reclined: 15

Changes:
- strengthen scoring reward for standing/walking diversity
- penalize batches that overfill lowered poses
- reduce random tolerance for floor-seated and reclined poses unless the batch already has enough vertical variety
- expand women pose banks with more standing and walking variants
- trim passport-like simple upright portraits in the random path by pressure, not by deleting the framing system

### 3. Random Color Spread

Current random output overuses a small cluster of navy / green / burgundy / powder-blue style stories.

Changes:
- reduce tolerance for repeated dominant color-story groups in one batch
- reward batches that include broader color spread
- keep neutrals available, but stop them from dominating the same batch alongside the same dark tones

This remains a batch-level diversity push, not a ban on specific colors.

### 4. Women Expression Lift

Women expression banks currently have almost no overtly happy / radiant options.

Changes:
- add a small set of happy, open, bright expressions to `1_3`, `4_5`, and `6_8`
- allow broad smile / beaming / joyful energy, but keep them natural and photogenic
- do not reintroduce winks

## Affected Areas

- `backend/services/batch_penalties.py`
- `backend/services/diversity_scoring.py`
- `backend/services/scoring.py` only if glue changes are needed
- `backend/engine/data/overrides/line_banks/women/poses/*.md`
- `backend/engine/data/overrides/line_banks/women/expressions/*.md`

## Validation

Local only.

Minimum validation:
- targeted scene-motif regression
- targeted random women diversity smoke
- line-bank loader tests
- one focused women random live sweep

## Success Criteria

- conservatory / greenhouse no longer dominates random batches
- random women pose mix visually reads as mostly standing/walking
- passport-like plain upright repetition is reduced
- colors no longer cluster around the same small dark set
- happy women expressions show up sometimes without winks
