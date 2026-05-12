# Safe High-Spicy Couples Interaction Research 2026-04-21

## Scope

- Adult couples only.
- Non-explicit, fully clothed, spicy-but-safe interaction references only.
- Target outcome: stronger two-person chemistry for `spicyLevel 5-8` without letting `1-4` drift into the same lane.
- Excluded on purpose: sex acts, intercourse, oral sex, explicit groping, nudity-first posing, lingerie-only removal staging, fetishized restraint, and anything that reads like pornography instead of editorial or intimate portrait direction.

## Source Provenance

- Open-source couple-pose references used:
  - Shotkit: 48 Natural Couple Poses for Weddings, Instagram, Selfies & More.
- Open-source adult boudoir shape references used for non-explicit body-line cues only:
  - ExpertPhotography: 33 Best Boudoir Poses for Photographers.
- The interaction bank is a project-safe synthesis, not a literal import of source wording.

## Draft Deliverable

- Structured couples interaction draft seed: backend/engine/data/drafts/pose_bank/high_spicy_couples_interaction_seed.json

Each record includes:

- `id`
- `short_name`
- `value`
- `style_modes`
- `allowed_scene_families`
- `tags`
- `lane`
- `recommended_min_spicy`
- `high_spicy_only`
- `block_low_spicy`
- `weight`
- `status`
- `source`
- `notes`
- `safety_note`

## Practical Filtering

### Revealing interaction ids

- `forehead_hold_close_frame`
- `wall_lean_waist_draw`
- `banquette_side_press`
- `lap_seat_turned_in`
- `back_hug_neck_brush`
- `stair_pause_hand_pull`
- `couch_recline_leg_cross`
- `window_hold_side_profile`

### Pushing_it interaction ids

- `near_kiss_wall_frame`
- `cross_lap_seat_editorial`
- `sofa_corner_leg_over_lap`
- `mirror_back_hold_gaze`
- `bed_edge_forehead_draw`
- `standing_v_between_knees`
- `dip_hold_cheek_near`
- `window_silhouette_bodyline`

### Low-spicy block interaction ids

- `near_kiss_wall_frame`
- `cross_lap_seat_editorial`
- `sofa_corner_leg_over_lap`
- `mirror_back_hold_gaze`
- `bed_edge_forehead_draw`
- `standing_v_between_knees`
- `dip_hold_cheek_near`
- `window_silhouette_bodyline`
- `lap_seat_turned_in`
- `couch_recline_leg_cross`

## Promotion Notes

- These couples interaction seeds are intended to mirror the reviewed women high-spicy workflow:
  - research in drafts first,
  - promote into live routing after review,
  - verify with smoke coverage,
  - keep low-spicy behavior guarded separately.
- These couples interaction seeds were promoted into the live `backend/engine/data/pose_bank.json` bank on 2026-04-21.
- Live generation now reads them through the dedicated `couple_interactions` bank during couples render routing.
- Recommended live routing contract:
  - `spicyLevel 1-4`: stay on current moderate-safe interaction language
  - `spicyLevel 5-6`: allow `revealing` interactions when style/scene allow them
  - `spicyLevel 7-8`: allow both `revealing` and `pushing_it` interactions when style/scene allow them
