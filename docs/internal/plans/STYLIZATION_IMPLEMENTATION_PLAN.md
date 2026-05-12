# Stylization Implementation Plan

## Goal

Add a new internal `photo_treatment` layer on top of the current engine without breaking the existing scene / outfit / pose logic.

Target behavior for default random:

- around `40%` clean polished professional look
- around `60%` more stylized photo treatments

## Phase 1

Safe internal rollout:

- add `photo_treatments.json`
- select one treatment per candidate internally
- do not add UI yet
- do not make treatment a hard scorer axis yet
- use treatment only for:
  - early prompt phrasing
  - technical render phrasing
  - debug readout

Success criteria:

- no regressions in existing women / men / couples generation
- prompts still validate
- debug shows effective treatment per prompt

## Phase 2

Soft engine influence:

- treatment starts biasing compatible scene / light / capture combinations
- still no hard locks unless obviously required
- keep treatment secondary to `styleMode`

Success criteria:

- stylized lanes become visible in real batches
- no obvious contradictions like nightlife flash in bright garden daylight

## Phase 3

Verification and rebalance:

- large sweeps for `women / men / couples`
- log real distribution of treatments
- tune weights and compatibility

Checks:

- distribution is close to intended mix
- no excessive stock look dominance
- no broken or contradictory prompt wording

## Phase 4

Optional UI exposure:

- add `Photo treatment` control only if the internal layer proves useful
- keep `Random` as the default

Possible UI values:

- Random
- Clean commercial
- Candid snapshot
- Analog film
- Low-key dramatic
- Direct flash night
- Studio seamless
- Cinematic

## Phase 1 Profile Set

Start with 7 internal profiles:

1. `clean_commercial`
2. `candid_phone_snapshot`
3. `analog_35mm`
4. `low_key_dramatic`
5. `direct_flash_night`
6. `studio_seamless`
7. `cinematic_poster_realism`

## Guardrails

- treatment is an overlay, not a replacement for current `styleMode`
- current core banks stay authoritative for scene / outfit / pose
- rollout order:
  1. data bank
  2. render/debug
  3. soft compatibility influence
  4. sweeps and rebalance
  5. optional UI
