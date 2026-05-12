# Safe High-Spicy Boudoir Research 2026-04-21

## Scope

- Adult models only.
- Non-explicit, clothed, suggestive boudoir / glamour / nightlife / editorial references only.
- Excluded on purpose: pornography, sex acts, intercourse, oral sex, masturbation, explicit genital emphasis, nipple-only styling, crotchless items, fully explicit fetishwear.

## Source Provenance

- Open-source pose references used:
  - Shotkit: 31 Boudoir Poses, Ideas and Tips to Make Her Look and Feel Amazing.
  - ExpertPhotography: 33 Best Boudoir Poses for Photographers.
- The pose seed file keeps many source labels recognizable but normalizes them into neutral project-safe ids and descriptions.
- The outfit seed file is a safe editorial synthesis from recurring wardrobe cues in those boudoir guides plus the project's existing styling taxonomy. It is intentionally not a literal import of lingerie-only or undressing-oriented examples.

## Draft Deliverables

- Structured pose draft seed: backend/engine/data/drafts/pose_bank/high_spicy_boudoir_pose_seed.json
- Structured outfit draft seed: backend/engine/data/drafts/styling/high_spicy_boudoir_outfit_seed.json

Both draft files include these review fields per record:

- id
- short_name
- value
- tags
- lane
- recommended_min_spicy
- block_low_spicy or high_spicy_only
- source / notes / safety_note

## Practical Filtering

### Revealing pose ids

- `peek_a_boo_frame`
- `back_one_leg_crossed`
- `stairs_look_up_recline`
- `sofa_legs_stretched`
- `side_lie_hug_torso`
- `perch_lean_back`
- `forward_fold_cross_leg`
- `bed_back_view_turn`
- `hands_up_fixing_hair`
- `back_face_side_s_curve`
- `body_side_on_face_camera`
- `window_silhouette_arch`
- `walking_turn_look`
- `one_hand_head_one_hip`
- `arms_above_head_stand`
- `rear_edge_bed_pose`
- `mirror_hair_adjust`
- `hair_sprawl_recline`

### Pushing_it pose ids

- `heels_over_shoulder`
- `knees_up_arm_support`
- `legs_on_wall`
- `chair_open_angle`
- `chair_kneel_arch`
- `wall_arch_bent_knees`
- `crouch_over_shoulder`
- `squat_grounded_pose`

### Low-spicy block pose ids

- `back_one_leg_crossed`
- `sofa_legs_stretched`
- `bed_back_view_turn`
- `heels_over_shoulder`
- `knees_up_arm_support`
- `body_side_on_face_camera`
- `legs_on_wall`
- `window_silhouette_arch`
- `chair_open_angle`
- `chair_kneel_arch`
- `rear_edge_bed_pose`
- `wall_arch_bent_knees`
- `crouch_over_shoulder`
- `squat_grounded_pose`

### Revealing outfit ids

- `sheer_overlay_slip_dress`
- `blazer_bodysuit_set`
- `halter_cutout_jumpsuit`
- `bodycon_mesh_sleeves`
- `off_shoulder_knit_mini`
- `robe_layered_slip_set`
- `asym_cutout_column_dress`
- `structured_bustier_trousers`
- `ring_halter_trousers`
- `club_cami_wrap_skirt`
- `satin_bodysuit_wide_trousers`

### Pushing_it outfit ids

- `corset_top_mini_skirt_set`
- `longline_bralette_sheer_shirt`
- `open_shirt_bodysuit`
- `harness_trim_blazer_set`
- `cowl_neck_micro_mini`
- `thigh_high_bodysuit_robe`
- `vinyl_trim_bodycon`
- `lace_up_cami_mini`
- `mesh_panel_bodycon`
- `sheer_buttondown_mini`

## Promotion Notes

- These research seeds were promoted into the live core banks on 2026-04-21.
- The draft files remain as a source archive and promotion reference, but live generation now uses the promoted core ids.
- If promoted later, the pose ids should be reviewed against:
  - `HIGH_SPICY_WOMEN_POSE_IDS`
  - `LOW_SPICY_UNSAFE_POSE_IDS`
- If promoted later, the outfit ids should be reviewed against:
  - `HIGH_SPICY_WOMEN_REVEALING_OUTFIT_IDS`
  - `HIGH_SPICY_WOMEN_PUSHING_IT_OUTFIT_IDS`
- Recommended next step after review:
  - promote a smaller subset first,
  - enable drafts locally,
  - test women random / nightlife / luxury at spicy 5 to 8,
  - only then widen scorer and safety lists.
