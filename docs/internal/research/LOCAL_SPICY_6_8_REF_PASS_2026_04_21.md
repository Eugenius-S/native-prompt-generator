# Local Spicy 6-8 Reference Pass 2026-04-21

## Scope

- Source folder reviewed: `!poses and outfits/`
- Intended target: new draft-only pose and outfit material for `spicyLevel 6-8`
- Categories covered in this pass:
  - women poses
  - women outfits
  - couples interactions
  - couples outfit coordination notes
- Live banks were not edited in this pass.

## Review Method

1. PNG files were checked metadata-first.
2. Files with direct prompt metadata were mined from `parameters` / `PositivePrompt_*` first.
3. Files without direct prompt metadata were treated as workflow-only or visual-only.
4. `pinterest/` JPG files were reviewed visually immediately.

## Source Counts

- `61` root PNG files reviewed
- `16` Pinterest JPG files reviewed
- `77` total references reviewed
- `37` PNG files exposed direct prompt metadata via `parameters` or `PositivePrompt_*`
- `24` PNG files required workflow parsing or visual review because they had no direct prompt string

## Hard Reject Rules Used

- reject under-18 references entirely
- reject explicit nudity-first or lingerie-only material that cannot be normalized into the project's clothed editorial lane
- reject fetish-coded or explicit body-grab / simulated-act framing
- if the outfit itself is weak but the pose shape is useful, keep only the pose idea

## Explicitly Rejected Source Buckets

- Underage metadata refs:
  - `Romantic_00050_.png`
  - `Romantic_00097_.png`
- Lingerie-only / explicit / unsafe refs kept out of the draft bank:
  - `ComfyUI_00687_.png`
  - `ComfyUI_00689_.png`
  - `ComfyUI_00690_.png`
  - `ComfyUI_00698_.png`
  - `Example_Photos_114.png`
  - `Romantic_00111_.png`
  - most Pinterest frames with thong-first, lingerie-first, or explicit hem-lift framing
- Portrait-only / low-signal refs that did not add a meaningful new pose or outfit family:
  - `caef53b1-3c55-4a75-bae8-053a076cf603.png`
  - `76a6cc4fe7bcedfd35c99a8a8e3f5b54.jpg`
  - `8b4391cf9a0f153e453f261606c8669b.jpg`
  - `e4e3d45abf240c4146dfe4ef591b373e.jpg`

## Draft Deliverables

- `backend/engine/data/drafts/pose_bank/spicy_6_8_local_women_pose_seed.json`
- `backend/engine/data/drafts/styling/spicy_6_8_local_women_outfit_seed.json`
- `backend/engine/data/drafts/pose_bank/spicy_6_8_local_couples_interaction_seed.json`
- `backend/engine/data/drafts/styling/spicy_6_8_local_couples_outfit_seed.json`

## Extraction Notes

- Women metadata yielded the most usable pose/outfit records in these files:
  - `Fashion_00017_.png`
  - `Fashion_00035_.png`
  - `Romantic_00003_.png`
  - `Romantic_00011_.png`
  - `Romantic_00023_.png`
  - `Test_000_00133_.png`
  - `Vintage_00040_.png`
  - `Vintage_00041_.png`
- Couples metadata yielded the cleanest interaction material in these files:
  - `ComfyUI-Fit_00047_.png`
  - `Couple-Dating_3.png`
  - `Fashion_00017_.png`
  - `Fashion_00035_.png`
  - `Travel_00003_.png`
  - `Vacation-New_00072_.png`
  - `Vacation-New_00085_.png`
  - `Vacation-New_00095_.png`
- Pinterest was useful mostly for pose shape or silhouette cues, not for literal promotion of the shown outfit.

## Couples Outfit Handling

- The current engine has no dedicated live `couples outfit bank` schema.
- In this draft pass, couples outfit work is split into:
  - women-side outfit families that can later be promoted into the shared `styling` bank
  - male-side outfit families that fit couple contexts
  - draft-only `coordination_pairs` notes for pair styling direction
- `coordination_pairs` is a research helper structure, not a live generator contract yet.

## Shortlist Summary

- Women draft pose additions: `7`
- Women draft outfit additions: `10`
- Couples draft interaction additions: `8`
- Couples draft outfit additions: `4` male-side families plus `6` coordination notes

## Next Review Question

- Before promotion, check whether the stronger women records overlap too much with the already-promoted 2026-04-21 boudoir pack.
- Most likely first promotion candidates from this local pass:
  - `table_lean_hips_back`
  - `cube_side_twist_knee_hold`
  - `lined_sculptural_mini_dress`
  - `clean_satin_slip_dress`
  - `city_window_close_waist_hold`
  - `table_backhold_press`
  - `male_oversized_tailored_suit`
