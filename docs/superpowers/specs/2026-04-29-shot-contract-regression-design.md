# Shot Contract Regression Design

## Problem

After the newer semantic matching and compatibility passes, treatment, light, scene family, and location tails can still combine into prompts that are technically valid but read cheap, flat, or internally contradictory.

Typical failure modes:
- premium/editorial treatment paired with weak or accidental scene tails
- light/time blocks that fight the location or scene mood
- safe fallback lanes (`clean_commercial` and similar) dominating contexts where they flatten the image
- location tails that stay semantically compatible on paper but still cheapen luxury, studio, or stylized output

This affects `women`, `men`, and `couples`, so the fix must live above mode-specific content banks.

## Goal

Make treatment, light, scene, and location render as one coherent shot contract instead of loosely compatible fragments.

Success criteria:
- premium/editorial lanes stop drifting into cheap-looking random output
- contradictory treatment/light/scene combinations are normalized or blocked early
- fixes apply consistently across `women`, `men`, and `couples`
- new line-bank content is less likely to reintroduce the regression

## Non-Goals

- no large rewrite of the generator architecture
- no giant blacklist forest of one-off phrase bans
- no attempt to solve every studio-specific edge case here; true seamless studio remains a follow-up issue

## Recommended Approach

Use one shared shot-contract layer plus narrow scoring pressure.

Why this approach:
- stronger than local scoring tweaks
- safer than scattering special cases across render paths
- reusable for future line-bank growth

## Design

### 1. Shared Shot Contract Layer

Introduce or extend one authoritative compatibility layer that decides:
- which `photo_treatment` lanes are allowed with which `scene_family`
- which light/time families are allowed for a given treatment + scene pair
- which location tail tags are banned or deprioritized for that contract
- what wins when treatment intent and fallback location text disagree

The contract should be shared by `women`, `men`, and `couples`.

### 2. Render Authority Order

Render authority should become explicit:
1. shot contract
2. treatment intent
3. scene family
4. location tail
5. generic light/time fallback

Meaning:
- a weak fallback light block must not override a stronger treatment/scene contract
- a cheap but technically matching location tail must not degrade a premium lane

### 3. Runtime Scoring Hardening

Add narrow scoring pressure for:
- cheap flat safe-fallback treatment reuse in premium/random contexts
- contradictory light/scene pairs
- empty accidental interior tails
- low-value fallback combinations that read like budget lifestyle photography

This scoring layer should support the contract, not replace it.

### 4. Rollout Plan

#### Phase 1
- finish the shared contract pass for all runtime modes
- normalize the main bad combinations in `random`, `balanced`, `glossy`, and stylized lanes

#### Phase 2
- run live sweeps across `women / men / couples`
- log only real surviving leaks
- tighten the contract where the live output still reads cheap

#### Phase 3
- move to the narrower studio-only issue `#89`
- keep seamless studio separate from practical studio/set scenes

## Validation

Required checks:
- targeted contract/render tests
- random live slices for `women / men / couples`
- focus on:
  - cheap flat light drift
  - contradictory time/light wording
  - premium treatment degraded by cheap scene tails
  - weak accidental interior/location tails

## Risks

- too-strict contracts can reduce variety
- too many scoring penalties can hide real root causes
- partial fixes in only one render path can create mode drift between `women`, `men`, and `couples`

## Decision

Implement the root fix as a shared shot-contract layer with explicit render authority and narrow scoring hardening, then use `#89` for the studio-specific follow-up.
