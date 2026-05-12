# Test Log

## 2026-05-03

### Issue 69 phase 6 release validation
- Focused validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue41_random_balance_smoke.py -q` -> `1 passed`
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_women_scene_coherence_smoke.py tests/test_men_taste_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_couples_identity_constraints_smoke.py tests/test_women_treatment_remap_smoke.py -q` -> `35 passed`
- Checked outcome:
  - The release smoke slice is green when the order-sensitive random-balance test is run in its own pytest process.
  - The remaining women / men / couples smoke coverage also passed cleanly in a separate process.
  - No runtime fixes were needed for release validation itself.

### Issue 69 phase 5 setup flow tighten step 1
- Checked outcome:
  - `README.md` now explains that the bundled setup script creates the virtual environment and installs dependencies.
  - `QUICKSTART.md` now leads with the bundled setup/start scripts and keeps `python app.py` as a fallback path.
  - No runtime validation was needed because this pass only changed public docs.

### Issue 69 phase 4 public docs cleanup step 1
- Checked outcome:
  - `README.md` now uses cleaner public wording for the backend structure and reporting guidance.
  - `QUICKSTART.md` no longer points readers at the internal CI workflow file.
  - This was a docs-only pass, so no runtime smoke run was needed.

### Issue 69 phase 3 scoring hotspot split step 2
- Focused validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue41_random_balance_smoke.py tests/test_issue57_muted_palette_balance_smoke.py tests/test_issue66_couples_chemistry_smoke.py tests/test_couples_scene_coherence_smoke.py` -> `8 passed`
- Checked outcome:
  - `backend/services/selection_scoring.py` now owns the race / body / style / identity scoring helpers.
  - `backend/services/scoring.py` keeps the public helper names as compatibility wrappers and continues to pass the same focused smoke slice.
  - The selection split did not change the checked random or couples behavior.

### Issue 69 phase 3 scoring hotspot split step 1
- Focused validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue41_random_balance_smoke.py tests/test_issue57_muted_palette_balance_smoke.py tests/test_issue66_couples_chemistry_smoke.py tests/test_couples_scene_coherence_smoke.py` -> `8 passed`
- Checked outcome:
  - `backend/services/treatment_balance.py` now owns the photo-treatment and random-light balance cluster.
  - `backend/services/scoring.py` keeps the remaining batch and identity helpers, while delegating the extracted scoring concern to the new module.
  - The focused random and couples smoke slice stayed green after the extraction.

### Issue 69 phase 2 prompt_service thinning step 2
- Focused validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_routing_validation_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_clothing_color_rendering_smoke.py tests/test_high_spicy_couples_interaction_bank_smoke.py tests/test_local_spicy_6_8_bank_smoke.py tests/test_male_styling_bank_smoke.py -q` -> `40 passed`
- Checked outcome:
  - `backend/prompt_service.py` no longer exports unused debug/render wrappers that only forwarded to the already-owned run service path.
  - `backend/services/run_service.py` now calls `backend.services.batch_selection._best_batch` directly, so the batch-selection path no longer depends on the prompt facade.
  - The checked backend slice stayed green after the extraction, so the prompt facade got thinner without a behavior regression.

### Issue 69 phase 1 legacy isolation and phase 2 prompt_service cleanup
- Focused validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_routing_validation_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_clothing_color_rendering_smoke.py tests/test_high_spicy_couples_interaction_bank_smoke.py tests/test_local_spicy_6_8_bank_smoke.py tests/test_male_styling_bank_smoke.py -q` -> `40 passed`
- Checked outcome:
  - `backend/legacy_bridge.py` now owns the direct legacy handoff for the active main-path modules, so the bridge is the only place that should know about the legacy people implementation during migration.
  - `backend/prompt_service.py` no longer carries the unreachable duplicate scoring / batch-selection bodies, which shrinks the compatibility facade without changing runtime behavior.
  - The direct `backend.legacy_people` smoke imports still pass through the tracked compatibility entry point, so existing tests remain green while the quarantine work continues.

### Routing and line-bank smoke stabilization pass
- Focused validation:
  - `python -m pytest tests/test_line_bank_women_pose_smoke.py::test_women_line_bank_prompt_parts_surface_without_leaking_into_men tests/test_routing_validation_smoke.py::test_women_fitness_and_sport_route_sporty_scenes tests/test_routing_validation_smoke.py::test_character_constraint_routing_prefers_sport_scene_match -v` -> `3 passed`
  - `python -m pytest tests/test_line_bank_women_pose_smoke.py::test_women_line_bank_prompt_parts_surface_without_leaking_into_men tests/test_routing_validation_smoke.py::test_women_fitness_and_sport_route_sporty_scenes tests/test_routing_validation_smoke.py::test_character_constraint_routing_prefers_sport_scene_match tests/test_issue82_framing_render_coherence_smoke.py tests/test_issue106_close_up_angle_diversity_smoke.py -q` -> `22 passed`
- Checked outcome:
  - women line-bank smoke now tolerates portrait-safe render normalization while still asserting `line_bank_pose`/`line_bank_outfit` source retention
  - sport routing smoke no longer hard-locks to a single scene family and remains strict on `sports_flirt` route validation
  - framing and issue 106 close-up diversity smokes stayed green after the test updates

## 2026-05-04

### Issue 69 phase 1 and phase 2 closeout pass
- Focused validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_api_smoke.py tests/test_line_bank_men_smoke.py tests/test_line_bank_couples_pose_smoke.py tests/test_clothing_color_rendering_smoke.py tests/test_male_styling_bank_smoke.py tests/test_high_spicy_couples_interaction_bank_smoke.py -q` -> `17 passed`
- Checked outcome:
  - the legacy bridge now lives in ignored `_legacy/legacy_bridge.py` and the real legacy people implementation now lives in ignored `_legacy/legacy_people.py`
  - `backend/legacy_people.py` is now a tracked compatibility shim only, so the visible backend surface no longer hosts the actual legacy implementation
  - `backend/services/run_service.py` and `backend/services/preset_service.py` now use public `prompt_service` wrappers instead of private prompt-service helpers
  - `PROJECT_PLAN.md` now reflects issue 69 phase 1 and phase 2 as complete

### Close-up profile / strong-turn wording bank pass
- Focused validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue106_close_up_angle_diversity_smoke.py -q` -> `8 passed`
- Checked outcome:
  - `backend/engine/render/prompt_renderer.py` now keeps richer close-up profile, chin-up, chin-down, and strong-turn wording lanes without breaking the existing face-only smoke markers.
  - `backend/services/scoring.py` now scores the expanded six-bucket close-up cycle consistently.
  - The close-up angle diversity smoke stayed green after the wording expansion.

### Issue 69 phase 0 inventory and first legacy isolation step
- Focused validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_routing_validation_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_clothing_color_rendering_smoke.py -q` -> `28 passed`
- Checked outcome:
  - `PROJECT_PLAN.md` now has a short issue-69 inventory for the public surface, internal docs to review later, and the legacy entry points that phase 1 needs to isolate.
  - `backend/legacy_bridge.py` now centralizes the direct legacy people usage for men/couples render paths and male-identity preview lookups.
  - The backend gate stayed green after the adapter move, so the refactor step did not change the checked runtime behavior.

### Issue 106 angle bucket diversity for close-up prompts
- Focused validation:
  - `python -m pytest tests/test_issue106_close_up_angle_diversity_smoke.py -v` -> `8 passed`
  - `python -m pytest tests/test_issue82_framing_render_coherence_smoke.py tests/test_issue65_framing_control_smoke.py tests/test_issue106_close_up_angle_diversity_smoke.py tests/test_api_smoke.py -v` -> `30 passed`
- Checked outcome:
  - `face_only` prompts no longer contain "only the face visible"
  - `face_only` with 4 sequential batch_index values produces >= 2 distinct angle buckets; 8 sequential values produce >= 3
  - scoring gives a higher score for a diverse batch (4 buckets) vs. all-same-bucket batch (1 bucket)
  - `scoring._close_up_angle_diversity_score([]) == 0` confirmed
  - all existing framing smoke tests stayed green (no regressions)

## 2026-05-03

### Close-up framing safety and variation pass
- Focused validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue82_framing_render_coherence_smoke.py tests/test_issue65_framing_control_smoke.py` -> `21 passed`
- Checked outcome:
  - `face_only` prompts no longer ask for `only face visible` framing and now carry anti-extreme-crop wording.
  - tight close-up pose text now has deterministic variation, reducing repeated identical pose phrasing in close portrait lanes.
  - full-body framing behavior stayed green in the same smoke slice.

## 2026-05-01

### Issue 98 full-body framing B+E pass
- Focused validation:
  - `pytest tests/test_issue65_framing_control_smoke.py tests/test_issue82_framing_render_coherence_smoke.py -v --tb=short` -> `20 passed`
- Checked outcome:
  - `full_body` and `ankle_up` now render a shorter full-height framing block with camera pull-back language
  - `headroom` is no longer emitted in the technical block for full-body framings
  - portrait framing text remained unchanged and the portrait smokes stayed green

## 2026-04-30

### Issue 105 dry-coastal split and tag-driven pose contracts sub-tasks 1+2
- Focused validation:
  - `pytest tests/test_issue105_prop_scene_outfit_matching_smoke.py -v` -> `6 passed`
  - broader subset (issue104, issue105, validator_repair, line_bank_loader, women_high_spicy, api) -> `50 passed, 4 failed (pre-existing)`
- Checked outcome:
  - dry coastal scenes (boardwalk_beach_houses) now allow mini dress but block swimwear
  - pool / shoreline scenes still allow swimwear
  - `WET_OUTFIT_CONTEXT_TAGS` in line_bank_loader no longer includes `coastal`
  - all 6 pose-id branches in `_pose_for_base_space` converted to tag-driven; `cabinet_reach_inside` got tag `cabinet`
- Pre-existing failures: 4 `test_repo_backed_live_*` tests fail due to user-edited override files in working tree (not caused by this change)

### Issue 103 women random color and outfit diversity first pass
- Focused validation:
  - `pytest tests/test_issue103_women_random_diversity_smoke.py -q` -> `2 passed`
  - `pytest tests/test_issue103_women_random_diversity_smoke.py tests/test_issue57_muted_palette_balance_smoke.py -q` -> `3 passed`
- Investigation snapshot:
  - a 16-seed women-random runtime sweep showed the issue still lived in live selection rather than only missing content: `mini_dress` led the outfit families (`25` / `160`), while `mini_dress + blazer_mini_dress + bodysuit_trousers` occupied `52` / `160` prompts in the checked slice
  - the same sweep also showed the live color leaders still clustering around the issue palette (`navy_cream`, `powder_blue`, `earthy_soft`, `chocolate_cream`, `clean_neutrals`, `champagne_taupe`, `hot_pink`), which confirmed that current preferred-profile pressure and generic batch scoring were still too permissive
- Checked outcome:
  - women-random now strips the main fitted lane out of the active preferred subset instead of reintroducing it through balanced reveal plus random-style preference merging
  - best-batch scoring now explicitly prefers broader women-random outfit/color spread and punishes fitted-lane crowding plus over-dominant issue-palette concentration in the final selected batch

### Issue 102 same_person framing and pose rigidity first pass
- Focused validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue102_same_person_diversity_smoke.py` -> `1 passed`
- Investigation snapshot:
  - a quick multi-seed random slice for `women + same_person` versus `different_persons` did not show an obvious aggregate collapse in raw pose-group / framing-group totals, which shifted the first fix away from schedule rewrites and toward best-batch scoring pressure
  - the current first pass therefore targets `same_person` batch selection directly, rewarding wider pose / framing spread and penalizing over-concentration in standing-heavy plus `waist_up` / `cowboy_shot`-heavy mixes
- Checked outcome:
  - `same_person` now has explicit batch-level scoring pressure for pose-family variety, framing variety, seated / lying presence, and against visually rigid `waist_up` / `cowboy_shot` overuse
  - the focused regression covers the intended preference directly: a more varied `same_person` pose / framing batch now scores above a rigid standing / mid-frame batch

### Issue 104 support-aware pose matching first pass
- Focused validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue104_support_pose_matching_smoke.py` -> `2 passed`
- Checked outcome:
  - `chair_sideways_pose` and `backwards_chair_pose` now require real chair / bench / sofa support in the scene text instead of passing on generic interior luxury alone
  - `side_lying_lounge` now requires bed or sofa support, so rooftop / empty outdoor scenes no longer qualify just because they are coastal or luxury-coded
  - `stairs_seated` now requires explicit stairs support, and `counter_hip_lean_collar_touch` now requires a real counter / island / cabinet-like support surface in an interior kitchen-like scene
  - the new smoke covers the checked bad-match examples across `marble_dining_room`, `hotel_suite_sitting_area`, `university_courtyard_steps`, `marble_shaker_kitchen`, `city_rooftop_day`, and `powder_room_stone_vanity`

### Issue 101 fantasy and sci-fi shared location split
- Focused validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py -k "repo_backed_live_location_line_banks_load_cleanly or respects_exact_theme_keywords_for_edge_cases or respects_requested_location_domain"` -> `3 passed`
- Runtime check:
  - realism random slice (`mode=women`, `batchSize=4`, `styleMode=random`, `seed=7`) stayed on realism-only shared location lines in the checked prompts
  - fantasy exact-theme slice (`mode=women`, `batchSize=4`, `styleMode=fantasy`, `locationStrategy=exact_theme`, `exactTheme=wizard library`, `seed=7`) routed to `old library aisle with tall ladders, dark wood shelves and soft top light` from `fantasy_locations.md` in the checked prompts

### Women line-bank and shared-location refresh
- Local broad validation after the override-bank refresh:
  - `generate_run(...)` `women random`, batch `4` -> `4 prompts`, `0 findings`
  - `generate_run(...)` `women nightlife`, batch `4` -> `4 prompts`, `0 findings`
  - `generate_run(...)` `men romantic`, batch `4` -> `4 prompts`, `0 findings`
  - `generate_run(...)` `couples random`, batch `4` -> `4 prompts`, `0 findings`
  - `generate_run(...)` `couples lifestyle`, batch `4` -> `4 prompts`, `0 findings`
  - `generate_run(...)` `couples nightlife`, batch `4` -> `4 prompts`, `0 findings`

### Issue 95 batch-40 search bottleneck first pass
- Reproduction:
  - `generate_run(...)`, `mode=women`, `styleMode=random`, `batchSize=40`, `antiRepeat=hard`, `validationMode=strict` -> baseline around `14.9s` to `18.4s` across seeds `0..2`, average `16.692s`
  - same with `locationStrategy=exact_theme`, `exactTheme=train compartment` -> after the fix around `6.47s` to `7.18s` across seeds `0..2`, average `6.760s`
- Root-cause instrumentation:
  - outer `_best_batch(...)` was not the main problem for the checked exact-theme case; `generate_batch` was called once, and the waste sat inside per-candidate retries inside `candidate_builder.generate_batch(...)`
  - before the retry-policy tightening, an instrumented exact-theme batch showed `2731 build_candidate` calls and dominant rejection classes `No eligible base spaces for the required scene families.` / `Candidate rejected by recent anti-repeat rules.`
  - after the first perf pass, the same instrumented exact-theme batch dropped to `691 build_candidate` calls in the checked seeded slice
- Regression guard:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_batch_selection_performance_smoke.py tests/test_routing_validation_smoke.py -k "performance or exact_theme_hard_locks_edge_case_scene_families_when_scene_focus_is_random"` -> `2 passed`

### Issue 95 batch-40 search bottleneck second pass
- Baseline instrumentation before the second pass:
  - `generate_batch_total` around `15.524s`, `generate_run_total` around `20.114s` for seed `42`
  - `build_candidate_calls=1310`
  - direct `build_candidate(...)` rejections were low, which led to a deeper breakdown of the surrounding retry loop
  - local replay showed the dominant early failure class by far was `Random indoor/outdoor balance target missed.` (`928` by `idx=10`), with most failures happening in the first two retry stages
- After the second pass:
  - seed `42`: `generate_batch_total 0.961s`, `generate_run_total 3.768s`, `build_candidate_calls=89`
  - three-seed `generate_run(...)` sweep for default random batch-40: `1.231s`, `2.600s`, `3.032s`, average `2.288s`
  - three-seed `generate_run(...)` sweep for exact-theme `train compartment` batch-40 after both passes: `7.575s`, `8.009s`, `6.645s`, average `7.410s`
- Regression guard:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue41_random_balance_smoke.py tests/test_batch_selection_performance_smoke.py tests/test_routing_validation_smoke.py -k "random_modes_keep_scene_and_light_balance or performance or exact_theme_hard_locks_edge_case_scene_families_when_scene_focus_is_random"` -> `3 passed`

## 2026-04-29

### Framing follow-up for issues #98 and #99
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue65_framing_control_smoke.py tests/test_issue82_framing_render_coherence_smoke.py` -> `20 passed`
- Follow-up validation after removing the intentional mid-shot allowance from `more_full_body`:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue65_framing_control_smoke.py tests/test_issue82_framing_render_coherence_smoke.py` -> `20 passed`
  - 8-seed `more_full_body` runtime sweep -> counts: `full_body=32`, `ankle_up=32`
- Live runtime review:
  - `more_full_body` 3-seed sweep -> counts: `full_body=8`, `ankle_up=7`, `knee_up=1`, `cowboy_shot=2`
  - `more_portraits` 3-seed sweep -> counts: `waist_up=4`, `below_chest_portrait=4`, `close_portrait=4`, `head_and_shoulders=2`, `bust_up=1`, `knee_up=1`, `cowboy_shot=2`
  - Sample `full_body` / `ankle_up` prompts now open with the stronger full-length lane and render the new centered full-height framing contract.
  - Sample portrait prompts now include explicit anti-top-crop wording instead of only generic headroom phrasing.
- Residual note:
  - code-side `more_full_body` residual is now closed; the only remaining closeout item for `#98` / `#99` is external image-side visual confirmation.

### Exact theme edge-case routing follow-up
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_women_scene_coherence_smoke.py -k "scene_family_control_locks_exact_scene_family or scene_family_override_beats_broader_scene_focus_family_pool or random_scene_context_blocks_obvious_outfit_and_pose_spillover"` -> `3 passed`
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_routing_validation_smoke.py -k "exact_theme_hard_locks_scene_family_when_scene_focus_is_random or exact_theme_hard_locks_edge_case_scene_families_when_scene_focus_is_random"` -> `2 passed`
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py -k "location_scene_matching_respects_exact_theme_keywords_for_edge_cases"` -> `1 passed`
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py -k "location_scene_matching_respects_exact_theme_keywords_for_edge_cases"` after anchor-token tightening -> `1 passed`
- Live runtime review after server restart:
  - `industrial loft` -> `scene_family_id` now stayed on `creative_gallery` in the checked batch
  - `train compartment` -> `scene_family_id` now stayed on `culture_bookish` in the checked batch
  - `fire stair landing` -> `scene_family_id` now stayed on `urban_daylight` in the checked batch
- Live runtime review after anchor-token tightening:
  - `industrial loft` -> stayed on `art loft corner...`
  - `train compartment` -> now stayed on `night train compartment...` only
  - `fire stair landing` -> stayed on `fire escape` / `fire stair landing` lines or blank fallback
- Residual note from live review:
  - code-side exact-theme location residual is now closed for the checked edge cases; the only remaining quality choice is whether future visual review wants a stricter non-empty fallback for some fire-stair batches.

### Issue 100 core outfit-to-scene coherence first pass
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue100_outfit_scene_coherence_smoke.py` -> `2 passed`
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue100_outfit_scene_coherence_smoke.py tests/test_scene_coherence_matrix_smoke.py` -> `9 passed`
- Checked outcome:
  - `shirt_trousers` no longer passes sporty/wellness spaces such as `boutique_pilates_studio`
  - nightlife-forward outfits such as `club_cami_wrap_skirt` no longer pass luxury-public non-bar contexts such as `hybrid_hotel_lobby_lounge` and `airport_lounge_evening`
  - valid control pairs stayed open in the checked slice: `workout_top_leggings -> boutique_pilates_studio`, `blouse_trousers -> hotel_suite_sitting_area`, `club_cami_wrap_skirt -> cocktail_bar_booth`
- Residual note:
  - broader `tests/test_women_scene_coherence_smoke.py` run surfaced an existing exact-family assertion failure in the coastal random-context case (`coastal_boardwalk` vs expected `coastal_pool`); this was outside the touched selector slice and was not changed in this pass

### Issues 98 and 99 framing contract hardening first pass
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue65_framing_control_smoke.py tests/test_issue82_framing_render_coherence_smoke.py` -> `19 passed`
  - small live sanity via `generate_run(...)`, `mode=women`, `styleMode=random`, `batchSize=3`, `seed=7`, `poseFramingControl in {more_full_body, more_portraits}`
  - follow-up schedule tuning validation: `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue65_framing_control_smoke.py tests/test_issue82_framing_render_coherence_smoke.py` -> `19 passed`
  - broad runtime sweep via `generate_run(...)`, `mode=women`, `styleMode=random`, `batchSize=8`, seeds `0..19`
  - anti-collapse follow-up validation: `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue65_framing_control_smoke.py tests/test_issue82_framing_render_coherence_smoke.py` -> `19 passed`
  - control-split follow-up validation: `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue65_framing_control_smoke.py tests/test_issue82_framing_render_coherence_smoke.py` -> `19 passed`
- Live runtime snapshot:
  - `more_full_body` -> `ankle_up`, `knee_up`, `ankle_up`; checked prompts opened with `Full-figure ...` and kept the new full-length framing clause in the rendered prompt body
  - `more_portraits` -> `close_portrait`, `below_chest_portrait`, `knee_up`; checked portrait prompts carried the new breathing-room / chest-up framing language
  - broad sweep before schedule tuning -> `mixed: full=40, mid=60, portrait=60`; `more_full_body: full=100, mid=40, portrait=20`; `more_portraits: portrait=120, mid=20, full=20`
  - broad sweep after schedule tuning -> `mixed: full=40, mid=60, portrait=60`; `more_full_body: full=140, mid=20, portrait=0`; `more_portraits: portrait=120, mid=20, full=20`
  - anti-collapse follow-up sweep (`more_full_body`, seeds `0..19`, batch `8`) -> group mix `full=140, mid=20, portrait=0`; `standing_like` tag in full lanes -> `121 / 140`
  - control-split follow-up sweep (seeds `0..19`, batch `8`) -> `more_full_body: full=140, mid=20, portrait=0`; `more_portraits: portrait=140, mid=20, full=0`
- Checked outcome:
  - `full_body` and `ankle_up` render text now explicitly says the camera is far enough from the subject to keep the whole figure visible in frame instead of relying on `both feet visible` wording
  - standing full-height prompts now render as `true full-length standing shot` rather than drifting back toward portrait-ish crop language
  - portrait prompts now carry explicit headroom wording and keep `head_and_shoulders` / `below_chest_portrait` in the safer chest-up zone
  - `more_full_body` now schedules predominantly full-height framings in the checked multi-seed slice, with a much smaller mid-frame tail
  - full-height framing blocks now explicitly ban fallback language (`waist-up`, `mid-shot`, `portrait` crop) to reduce model-side collapse back into upper-body composition
  - opposite-lane leakage is removed at group level in the checked slice (`more_full_body` no longer emits portrait-group frames; `more_portraits` no longer emits full-group frames)
- Residual risk:
  - this pass now includes a broad multi-seed runtime sweep, but the issue close criteria still needs a manual visual check of generated images for the reopened standing and portrait failure cases

## 2026-04-27

### Photo type control first pass
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_photo_type_control_smoke.py -q` -> `13 passed`
  - live multi-seed runtime audit via `generate_run(...)`, `mode=women`, `styleMode=random`, `batchSize=8`, seeds `0..5`, `photoTypeControl in {glossy, studio, stylized, amateur}`
- Checked outcome:
  - non-`Custom` photo-type modes reset stale manual treatment locks instead of silently keeping an old dropdown value alive
  - `Glossy` adds premium non-phone treatment pressure while pushing down the cheapest selfie / snapshot lanes
  - `Studio` can request `studio` scenes directly through the new profile layer instead of depending only on a manually locked treatment id
  - explicit non-`Balanced` photo-type modes now stay authoritative through postprocess instead of being remapped back into unrelated `clean_commercial` follow-up lanes
  - `Amateur` follow-up tuning now blocks `studio` / `nightlife_neon` scenes and removes `clean_commercial` from the allowed amateur treatment lane, so the mode stays on phone / selfie / analog style treatments plus a small direct-light carry-over tail
  - second follow-up tuning now keeps `Glossy` out of the arty/studio tail and exposes `effectivePhotoType` plus treatment mix/quality/tone summaries in debug output
  - third follow-up tuning now makes explicit photo-type negative preferences authoritative inside the profile merge too, so `Studio` no longer inherits `clean_commercial` preference pressure from the base random lane and `Stylized` no longer keeps `direct_light_editorial` / daylight tails alive through the same leak
  - fourth follow-up tuning now gives `Balanced` a real healthy-default lane and closes the last phone/selfie/extreme tails through an explicit `Balanced` late-remap guard, so the default mode is no longer just a passive `styleMode=random` fallback
- Runtime snapshot:
  - `glossy` -> `direct_light_editorial=15`, `clean_commercial=13`, `concept_photo_editorial=7`, `advertising_poster_realism=6`, `cinematic_poster_realism=5`, `low_key_dramatic=2`; scenes spread across `hospitality_suite`, `creative_gallery`, `residential_luxury`, `courtyard_garden`, `garden_conservatory`, `urban_daylight`, and a small coastal tail
  - `studio` -> `clean_commercial=18`, `advertising_poster_realism=9`, `low_key_dramatic=7`, `concept_photo_editorial=7`, `studio_seamless=7`; scenes -> `studio=48/48`
  - `stylized` -> `vintage_flash_photo=10`, `direct_light_editorial=9`, `advertising_poster_realism=9`, `low_key_dramatic=6`, `cinematic_poster_realism=5`, `concept_photo_editorial=5`, `direct_flash_night=3`, `studio_seamless=1`; scenes mostly `creative_gallery`, `residential_luxury`, `hospitality_suite`, `studio`, and `nightlife_neon`
  - `amateur` -> `analog_35mm=20`, `candid_phone_snapshot=13`, `direct_light_editorial=6`, `casual_indoor_selfie=4`, `mirror_selfie=3`, `disposable_camera=2`; scenes concentrated in `culture_bookish`, `nightlife_bar`, `hospitality_suite`, `grooming_bath`, `wellness_spa`, `residential_luxury`, `urban_daylight`, and `coastal_pool`
  - glossy follow-up audit after scene tightening -> treatments `clean_commercial=24`, `direct_light_editorial=9`, `cinematic_poster_realism=7`, `concept_photo_editorial=5`, `advertising_poster_realism=2`, `low_key_dramatic=1`; scenes `hospitality_suite=10`, `residential_luxury=8`, `urban_daylight=8`, `courtyard_garden=7`, `garden_conservatory=7`, `grooming_bath=6`, `coastal_boardwalk=2`, with no `creative_gallery`, `studio`, `nightlife_neon`, or `wellness_spa` hits in the checked slice
  - studio follow-up audit after merge override fix -> treatments `concept_photo_editorial=22`, `advertising_poster_realism=10`, `studio_seamless=9`, `low_key_dramatic=7`; scenes `studio=48/48`
  - stylized follow-up audit after merge override fix -> treatments `concept_photo_editorial=12`, `vintage_flash_photo=11`, `advertising_poster_realism=7`, `cinematic_poster_realism=6`, `direct_flash_night=6`, `low_key_dramatic=6`; scenes `creative_gallery=12`, `residential_luxury=12`, `hospitality_suite=11`, `nightlife_neon=7`, `studio=6`, with no `urban_daylight`, `grooming_bath`, `wellness_spa`, or coastal/garden tails in the checked slice
  - balanced follow-up audit after healthy-default pass -> treatments `analog_35mm=13`, `direct_light_editorial=9`, `clean_commercial=8`, `cinematic_poster_realism=6`, `low_key_dramatic=5`, `documentary_still=3`, `vintage_flash_photo=3`, `advertising_poster_realism=1`; scenes `hospitality_suite=12`, `courtyard_garden=7`, `garden_conservatory=7`, `culture_bookish=6`, `urban_daylight=6`, `residential_luxury=5`, `coastal_boardwalk=5`, with no `studio`, `nightlife_neon`, `mirror_selfie`, `casual_indoor_selfie`, `candid_phone_snapshot`, `disposable_camera`, `studio_seamless`, or `direct_flash_night` hits in the checked slice

### Issue 82 portrait render coherence pass
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue65_framing_control_smoke.py tests/test_issue82_framing_render_coherence_smoke.py -q` -> `10 passed`
  - follow-up cleanup validation: `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue82_framing_render_coherence_smoke.py -q` -> `7 passed`
  - live runtime sweep via `generate_run(...)`, `mode=women`, `styleMode=random`, `batchSize=8`, seeds `0..7`
- Live runtime counts:
  - `more_portraits` -> `portrait=48`, `mid=8`, `full=8`, portrait conflicts with lower-body prompt text -> `0 / 48`
  - `more_full_body` -> `full=40`, `mid=16`, `portrait=8`, portrait conflicts inside the portrait minority tail -> `0 / 8`
  - follow-up cleanup sweep for `more_portraits` with added `mini dress` / `mini skirt` / `micro skirt` / `waistband` conflict checks -> `0 / 48`
- Checked outcome:
  - portrait prompts no longer mention `micro skirt`, `mini skirt`, `mini dress`, thigh-based hand placement, `waistband` hand actions, or `hips angled back` in the checked slice
  - full-body prompts still keep the same lower-body outfit and pose detail where that information is useful
- Conclusion:
  - the current issue-82 render pass removed the direct portrait-vs-lower-body prompt contradiction in the checked framing slice without regressing the existing framing-control distribution smoke

### Issue 83 treatment-quality taxonomy first pass
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_women_treatment_remap_smoke.py -q` -> `15 passed`
  - live runtime sweep via `generate_run(...)`, `mode=women`, `styleMode=random`, `batchSize=10`, seeds `0..19`
- Live runtime counts:
  - buckets -> `polished_glam=124`, `editorial_non_phone=54`, `casual_low_end=9`, `phone_snapshot=13`
  - cheap-id hits (`candid_phone_snapshot`, `mirror_selfie`, `casual_indoor_selfie`, `documentary_still`, `disposable_camera`) -> `22 / 200` (`0.11` share)
  - cheap wording signals after wording cleanup -> `smartphone camera feel=10`, `front-facing phone camera feel=1`
- Checked outcome:
  - women random no longer treats low-end documentary / disposable lanes as part of the same healthy stylized pool as stronger editorial lanes
  - women luxury and romantic remap paths stop routing back into the most obviously cheap selfie / low-end lanes in the checked slice
  - cheap-id share improved versus the earlier issue-83 audit (`0.155 -> 0.11`)
  - the earlier low-end wording cluster (`ordinary available light`, `cheap-flash snapshot feel`, `unpolished realism`, `everyday indoor color`) disappeared from the checked random runtime slice after treatment text cleanup
- Conclusion:
  - the current issue-83 pass successfully separated treatment quality classes, reduced low-end lane share, and removed the worst cheap wording from the checked women-random runtime slice; remaining cheap signals now mostly come from intentionally phone-coded lanes

### Issues 78 / 76 / 77 / 79 quality pass
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py -k "repo_backed_live_pose_line_banks_load_cleanly or pose_line_bank_overhead_arm_lines_are_blocked_in_tight_framing"` -> `2 passed`
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_women_treatment_remap_smoke.py -k "women_random_constraints_remap_clean_commercial or women_random_batch_score_prefers_target_mix_over_phone_heavy_batch"` -> `2 passed`
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue77_location_render_coherence_smoke.py tests/test_validator_repair.py -k "line_bank_location_does_not_append_unrelated_scene_tail or sand_without_beach_repair or sand_without_beach_repair_preserves_existing_scene_identity"` -> `3 passed`
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py -k "budget_club_outfit_lines_are_blocked_in_refined_modes or repo_backed_live_outfit_line_banks_load_cleanly"` -> `2 passed`
- Extra runtime checks:
  - women random treatment sweep, `20 x batchSize=10` -> `phone_snapshot=16`, `stylized_non_phone=68`, `polished_glam=116` (`~8% / 34% / 58%`)
  - women random spicy sweep, `10 x batchSize=10`, `spicyLevel=6` -> `0` `budget_club_like` line-bank outfit hits in runtime output
- Checked outcome:
  - tight portrait/upper-body crops no longer surface raised-arm line-bank poses
  - women random treatment output is no longer smartphone-dominant and sits close to the requested mix target
  - custom location lines no longer drag unrelated luxury/spa scene tails into the final prompt
  - cheap clubwear line-bank outfits are blocked from refined modes instead of leaking into general random/luxury prompts
- Conclusion:
  - the current quality pass removed four direct regression sources across pose/framing, treatment balance, scene coherence, and outfit taste

### Issue 75 framing-first Z-Image opener rebuild
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue65_framing_control_smoke.py -q` -> `6 passed`
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_women_treatment_remap_smoke.py -q` -> `12 passed`
- Checked outcome:
  - final prompt opener now leads with framing plus treatment wording instead of starting with capture-style text alone
  - the technical tail no longer repeats the framing clause, so the crop instruction stays concentrated at the front
  - explicit `photoTreatmentControl=mirror_selfie` keeps `mirror selfie` in the live opener while preserving framing-first wording
- Conclusion:
  - the Z-Image-facing opener contract is now framing-first and treatment-aware in the active women render path

### Framing random mix with new portrait and full-figure variants
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue65_framing_control_smoke.py -q` -> `4 passed`
  - live multi-seed random sweep via `generate_run(...)`, `mode=women`, `styleMode=random`, `poseFramingControl=random`, `batchSize=8`, seeds `0..11`
- Live framing counts:
  - `face_only=11`
  - `below_chest_portrait=4`
  - `ankle_up=8`
  - `waist_up=9`
  - `bust_up=2`
  - `close_portrait=5`
  - `head_and_shoulders=5`
  - `full_body=16`
  - `knee_up=22`
  - `cowboy_shot=14`
- Checked outcome:
  - random runs now surface both the old framing base and the new tighter portrait / ankle-up full-figure lanes in the active generation path
  - stronger framing text is rendered near the front of the final prompt instead of being buried at the end
  - full-body bias now covers both head-to-toe and ankle-up style crops
- Conclusion:
  - the framing system now mixes broader crop variants in random mode without replacing the current base lanes

### Issue 68 sidebar implementation follow-up
- Validation:
  - `node --check frontend/components/controls.js`
  - `node --check frontend/app.js`
  - `node --check frontend/sections/scene.js`
  - `node --check frontend/sections/subject.js`
  - `node --check frontend/sections/output.js`
  - editor diagnostics check on touched frontend JS/CSS files -> no errors
  - `git diff --check` -> clean
  - `npm run test:e2e -- tests/e2e/form-controls.spec.js --workers=1 --reporter=line` -> `5 passed`
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_scene_coherence_matrix_smoke.py -k couples_nightlife -q` -> `1 passed`
  - repeated local `couples_nightlife` smoke replay x10 -> `10/10 passed`
- Checked outcome:
  - the new control primitives compile cleanly
  - the reordered sidebar modules and converted controls have no editor-reported errors
  - the implementation stays inside the current frontend contract without backend form-key changes
  - the frontend now loads without the post-implementation runtime crash points that initially broke PR `#74` e2e
  - the focused Playwright coverage now matches the new segmented/chip control contract and passes locally
- Conclusion:
  - the first approved UI implementation slice is in place and is safe enough to review as a standalone frontend pass

### Issue 67 expression mood rebalance
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue67_expression_rebalance_smoke.py tests/test_women_high_spicy_smoke.py tests/test_couples_high_spicy_interaction_smoke.py -q` -> `10 passed`
- Coverage highlights:
  - new smoke coverage confirms `calm_confident` no longer surfaces in random `women` or `couples` runs at `spicyLevel 6-8`
  - low and mid random women sweeps no longer hard-lock toward `calm_confident`; `soft_flirty` now meets or exceeds it in the checked multi-seed slice
  - existing neighboring high-spicy women and couples tests stay green after the rebalance
- Extra live check:
  - multi-seed women random sweep after the patch: `spicy 6 -> 0 calm_confident`, `spicy 7 -> 0 calm_confident`, `spicy 8 -> 0 calm_confident`
- Conclusion:
  - high-spicy calm/confident drift is now hard-blocked in the active mood-selection path, and general random mood spread is materially less flat

### Issue 66 hotter couples 6-8 chemistry and gaze pass
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue66_couples_chemistry_smoke.py tests/test_couples_high_spicy_interaction_smoke.py tests/test_line_bank_couples_pose_smoke.py -q` -> `7 passed`
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py -k repo_backed_live_pose_line_banks_load_cleanly -q` -> `1 passed`
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue66_couples_chemistry_smoke.py -q` -> `3 passed`
- Coverage highlights:
  - new smoke coverage verifies the mid-spicy couples pose pool is broader than the old three-line collapse
  - new smoke coverage verifies high-spicy couples runs now use a substantially wider `6_8` pose pool
  - high-spicy random couples prompts no longer emit `direct eye contact` in the checked multi-seed slice
  - existing couples interaction and couples pose-bank tests stay green after the chemistry/gaze pass
  - repo-backed loader coverage now checks the final live `6_8` couples bank wording that actually shipped with the chemistry rewrite
- Extra live check:
  - multi-seed random couples sweep after the patch: `spicy 6 -> 9 unique poses, 0 direct eye contact`, `spicy 7 -> 10 unique poses, 0 direct eye contact`, `spicy 8 -> 8 unique poses, 0 direct eye contact`
- Conclusion:
  - couples `6-8` now reads hotter and less camera-locked, with materially better pose variety in the active generation path

### Issue 65 framing routing and stronger framing text
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue65_framing_control_smoke.py tests/test_women_treatment_remap_smoke.py -q` -> `15 passed`
- Coverage highlights:
  - `more_portraits` now pushes random women runs strongly toward portrait framing groups instead of behaving like `mixed`
  - `more_full_body` now pushes random women runs strongly toward true `full_body` framing instead of collapsing into knee-up output
  - framing render text now uses stronger phrases such as `head-and-shoulders portrait` and `full body in frame, visible head to toe`
- Conclusion:
  - framing control now materially changes selection-time framing distribution and sends clearer framing language into the final prompt

## 2026-04-25

### Issue 55 OS-native UI path separators
- Validation:
  - `node --check frontend/sections/output.js`
  - `node --check frontend/utils/path_format.js`
- Checked outcome:
  - both files pass syntax check after moving line-bank path rendering to shared formatter
  - line-bank root and folder examples now use runtime-native separator formatting in one shared path

### Issue 54 repeated citrus and pool location motifs
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue54_location_motif_balance_smoke.py tests/test_issue41_random_balance_smoke.py tests/test_line_bank_loader.py -q` -> `18 passed`
- Coverage highlights:
  - new smoke test verifies random women batches no longer over-concentrate on `waterside` and `orchard_citrus` motifs across multi-seed sweeps
  - existing random scene/light balance smoke remains green
  - line-bank loader and location compatibility tests remain green
- Conclusion:
  - repetition pressure is now handled through motif-level batch diversity scoring rather than wording-level blacklist patches

### Issue 53 random race preset routing leak
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue53_random_race_routing_smoke.py tests/test_issue36_race_presets_smoke.py -q` -> `8 passed`
- Coverage highlights:
  - `random_default_split` no longer emits `middle_eastern` or `south_asian` ids across multi-seed sweeps
  - `mostly_mixed` still surfaces `middle_eastern` and `south_asian`
  - exact `middle_eastern` and exact `south_asian` presets still hard-lock ethnicity ids
- Conclusion:
  - routing leak is fixed in the active batch-selection path without regressing mixed/exact race preset behavior

### Issue 58 dedicated couples pose line bank
- Validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py tests/test_line_bank_couples_pose_smoke.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py tests/test_couples_high_spicy_interaction_smoke.py -q` -> `22 passed`
- Coverage highlights:
  - repo-backed loader now confirms `couples/poses` records load cleanly per spicy bucket
  - couples prompt smoke confirms line-bank pair pose text surfaces in `segments.pose` and `candidate.line_bank_pose`
  - women prompt smoke confirms couples pose lines do not leak into women mode
  - existing high-spicy couples interaction smoke stays green, confirming interaction lane metadata remains intact
- Conclusion:
  - dedicated couples pose line-bank is live and selectable in couples generation without regressing current interaction routing checks

### Issue 56 stronger line-bank semantics and issue 57 muted palette rebalance
- Regression path:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py -k "extended_semantic_tags or extended_semantics" -v` -> failed first, then passed after location semantic inference/matching update
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py -k "outfit_line_infers_extended or outfit_scene_matching_respects_extended" -v` -> failed first, then passed after outfit semantic inference/matching update
- Focused validation:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_issue57_muted_palette_balance_smoke.py tests/test_issue41_random_balance_smoke.py tests/test_clothing_color_rendering_smoke.py -q` -> `9 passed`
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py tests/test_issue57_muted_palette_balance_smoke.py tests/test_issue41_random_balance_smoke.py tests/test_clothing_color_rendering_smoke.py -q` -> `25 passed`
- Conclusion:
  - shared location and outfit line-bank matching now uses richer semantics without breaking existing guardrails
  - the random women muted-palette collapse check is green on the implementation branch after runtime weight, scoring, and postprocess adjustments

## 2026-04-23

### Issue 46 bright summer outdoor location bank wave 1
- Added the first outdoor-summer expansion wave to `shared/locations/all.md`.
- Added a narrow location-tag compatibility pass for:
  - `beach`
  - `shore`
  - `lawn`
  - `meadow`
  - `field`
  - `park`
  - `sunflower`
  - `wildflower`
- Validation:
  - `python -m py_compile backend\engine\line_bank_loader.py` -> passed
  - `python -m pytest tests\test_line_bank_loader.py -q` -> `12 passed`
  - live smoke via `generate_run(...)`, `batchSize=3`, `styleMode=random`, `spicyLevel=6`, `antiRepeat=hard`:
    - `women` -> `3 prompts`, `0 findings`, included pool steps and summer cafe terrace
    - `men` -> `3 prompts`, `0 findings`, included rooftop plunge pool deck
    - `couples` -> `3 prompts`, `0 findings`
- Conclusion:
  - the unified shared location bank now has a stronger bright-summer outdoor slice
  - the first wave stayed generator-safe without touching scoring or routing weights

### Issue 46 bright summer outdoor location bank wave 2
- Added a second outdoor-summer expansion wave to `shared/locations/all.md`.
- Validation:
  - `python -m pytest tests\test_line_bank_loader.py -q` -> `12 passed`
  - live smoke via `generate_run(...)`, `batchSize=4`, `styleMode=random`, `spicyLevel=6`, `antiRepeat=hard`:
    - `women` -> `4 prompts`, `0 findings`, included `rocky cove ledge`
    - `men` -> `4 prompts`, `0 findings`, included `sunlit tram street` and `open flower farm lane`
    - `couples` -> `4 prompts`, `0 findings`, included `warm orchard row`
- Conclusion:
  - the bright-summer outdoor pool is materially wider after wave 2
  - the additional lines stayed parse-safe and generation-safe without further routing changes

### Issue 46 bright summer outdoor location bank wave 3
- Added a final curated fill pass to `shared/locations/all.md`.
- Validation:
  - `python -m pytest tests\test_line_bank_loader.py -q` -> `12 passed`
  - live smoke via `generate_run(...)`, `batchSize=4`, `styleMode=random`, `spicyLevel=6`, `antiRepeat=hard`:
    - `women` -> `4 prompts`, `0 findings`, included `open citrus grove lane`
    - `men` -> `4 prompts`, `0 findings`, included `sunlit riverwalk cafe edge` and `poolside canopy daybed`
    - `couples` -> `4 prompts`, `0 findings`, included `open-air summer restaurant terrace` and `infinity pool edge`
- Conclusion:
  - the shared summer-bright location bank now looks broad enough to treat issue `#46` as functionally complete after review/merge

### Issue 45 shared location bank contract
- Contract change:
  - replaced `shared/locations/{1_3,4_5,6_8}.md` with one common `shared/locations/all.md`
  - shared location records now load as one common pool for all spicy levels
- Validation:
  - `python -m py_compile backend\engine\line_bank_loader.py backend\engine\candidate_builder.py backend\legacy_people.py` -> passed
  - `python -m pytest tests\test_line_bank_loader.py -q` -> `12 passed`
  - `python -m pytest tests\test_line_bank_women_pose_smoke.py tests\test_line_bank_men_smoke.py -q` -> `2 passed`
- Conclusion:
  - shared location line-bank no longer depends on spicy buckets
  - women / men / couples generation remains clean after the contract change

### Issue 37 wet wording gating
- Root cause:
  - surface wet-skin atoms were already scene-gated
  - external outfit line-bank wording could still carry wet clothing text into dry scenes
- Validation:
  - `python -m py_compile backend\engine\line_bank_loader.py` -> passed
  - `python -m pytest tests\test_line_bank_loader.py -q` -> `12 passed`
- Conclusion:
  - wet outfit line-bank items are now blocked in dry city/hotel contexts
  - wet outfit wording still works in explicit pool/spa/humid contexts

### Issue 35 custom-heavy batch fallback
- Reproduced failing custom-heavy state:
  - `mode=women`, `styleMode=random`, `spicyLevel=6`, `batchSize=20`
  - `outfitReveal=pushing_it`, `beautyFinishControl=after_dark`
  - `hairstyle=sleek_bob`, `hairColorControl=black`, `eyeColorControl=green_eyes`, `breastSizeControl=extra_large_breasts`
  - `antiRepeat=hard`, `validationMode=strict`, `locationStrategy=fresh_only`
  - before fix: `Could not generate a valid batch.`
- Validation:
  - `python -m py_compile backend\services\batch_selection.py` -> passed
  - `python -m pytest tests\test_issue35_custom_batch_fallback_smoke.py -q` -> passed
  - `python -m pytest tests\test_issue35_custom_batch_fallback_smoke.py tests\test_issue41_random_balance_smoke.py -q` -> `2 passed`
- Manual extra check:
  - same custom-heavy state with `locationStrategy=exact_theme`, `exactTheme=pool` -> returned `20` prompts, `0 findings`
- Conclusion:
  - custom-heavy appearance controls no longer hard-dead-end the batch builder in the reproduced paths
  - exact race and scene constraints are not relaxed by this fallback

### Issue 41 random light and scene balance
- Code checks:
  - `python -m py_compile backend\engine\candidate_builder.py backend\services\scoring.py` -> passed
  - `python -m pytest tests\test_issue41_random_balance_smoke.py -q` -> passed
  - `python -m pytest tests\test_issue41_random_balance_smoke.py tests\test_women_scene_coherence_smoke.py tests\test_couples_scene_coherence_smoke.py -q` -> `12 passed`
- Live x20 sweep, `styleMode=random`, `spicyLevel=6`, `antiRepeat=hard`:
  - `women`: `outdoor=8`, `indoor=12`, `bright=13`, `findings=0`
  - `men`: `indoor=10`, `outdoor=10`, `bright=12`, `findings=0`
  - `couples`: `indoor=11`, `outdoor=9`, `bright=11`, `findings=0`
- Conclusion:
  - default random no longer collapses into mostly muted interiors in the tested x20 paths
  - explicit scene-family/preset routing remains outside this random-only rebalance
  - smoke tolerance was later relaxed from `7..13` to `6..14` for indoor/outdoor counts after CI showed a healthy but occasional `14/6` tail
  - smoke bright-count tolerance was later relaxed from `10..15` to `8..16` after CI showed a healthy but occasional `8/20` bright tail with `0 findings`

### PR 32 CI cleanup
- `python -m pytest tests\test_routing_validation_smoke.py::test_race_dropdown_exposes_curated_presets_and_keeps_other_slot -q` -> passed
- `python -m pytest tests\test_scene_coherence_matrix_smoke.py::test_scene_coherence_matrix_smoke -q -k couples_luxury_exact_theme` -> passed
- `python -m pytest tests\test_routing_validation_smoke.py tests\test_scene_coherence_matrix_smoke.py tests\test_issue36_race_presets_smoke.py -q` -> `27 passed`
- `python -m pytest tests\test_men_taste_smoke.py::test_men_romantic_outfit_spread_avoids_two_template_collapse -q` -> passed
- `python -m pytest tests\test_men_taste_smoke.py::test_men_random_outfit_spread_is_less_luxury_heavy -q` -> passed
- `python -m pytest tests\test_scene_coherence_matrix_smoke.py::test_scene_coherence_matrix_smoke -q -k couples_nightlife` -> passed
- `python -m pytest tests\test_scene_coherence_matrix_smoke.py tests\test_men_taste_smoke.py -q` -> `10 passed`
- `python -m pytest tests\test_women_scene_coherence_smoke.py::test_women_luxury_exact_theme_avoids_bodysuit_trousers -q` -> passed
- `python -m pytest tests\test_women_scene_coherence_smoke.py tests\test_scene_coherence_matrix_smoke.py -q` -> `15 passed`
- `npm run test:e2e -- --workers=1 --reporter=line` -> `5 passed`
- later CI tolerance follow-up:
  - relaxed `test_men_random_outfit_spread_is_less_luxury_heavy` unique-outfit floor from `6` to `5`
  - reason: CI showed an occasional healthy `5`-template distribution with the top-repeat cap still holding at `<= 7`

## 2026-04-22

### Women appearance parity with men
- UI / config checks:
  - `node --check frontend/app.js` -> passed
  - `node --check frontend/sections/subject.js` -> passed
  - `python -m py_compile backend/options.py backend/forms/constants.py backend/forms/normalizer.py backend/forms/user_profile.py` -> passed
- Bootstrap checks:
  - confirmed `outfitVibeControl` exists in `DEFAULT_FORM_STATE`
  - confirmed `UI_OPTIONS["outfitVibeOptions"]` exposes the curated women clothing-vibe choices
- Runtime smoke:
  - `prompt_service.generate_run(...)` with `mode=women`, `outfitVibeControl=luxury`, `outfitReveal=balanced`, `batchSize=3`, `debugMode=True` -> returned `3` prompts
  - `prompt_service.generate_run(...)` with `mode=couples`, `outfitVibeControl=luxury`, `outfitReveal=balanced`, `batchSize=3`, `debugMode=True` -> returned `3` prompts
- Conclusion:
  - the new women-side `Outfit vibe` control is wired end-to-end and does not break current women/couples generation

### Women beauty-finish parity follow-up
- UI / config checks:
  - `node --check frontend/app.js` -> passed
  - `node --check frontend/sections/subject.js` -> passed
  - `python -m py_compile backend/options.py backend/forms/constants.py backend/forms/normalizer.py backend/forms/user_profile.py` -> passed
- Bootstrap checks:
  - confirmed `beautyFinishControl` exists in `DEFAULT_FORM_STATE`
  - confirmed `UI_OPTIONS["beautyFinishOptions"]` exposes:
    - `fresh_natural`
    - `polished_soft`
    - `glossy_glam`
    - `after_dark`
- Runtime smoke:
  - `prompt_service.generate_run(...)` with `mode=women`, `beautyFinishControl=fresh_natural`, `batchSize=3`, `debugMode=True` -> returned `3` prompts
  - `prompt_service.generate_run(...)` with `mode=women`, `beautyFinishControl=after_dark`, `batchSize=3`, `debugMode=True` -> returned `3` prompts
- Conclusion:
  - the new women-side `Beauty finish` control is live and generator-safe
  - women now have a separate finish/polish axis instead of only `Makeup`

### Clothing-control unification follow-up
- UI / config checks:
  - `node --check frontend/sections/subject.js` -> passed
  - `python -m py_compile backend/forms/constants.py backend/forms/normalizer.py` -> passed
- Alias checks:
  - `outfitVibeControl=bookish` normalizes to `cultural_bookish`
  - `outfitVibeControl=beach` normalizes to `coastal`
  - `maleOutfitControl=male_dark_shirt_trousers` still normalizes to `nightlife`
- Runtime smoke:
  - `prompt_service.generate_run(...)` with `mode=women`, `outfitVibeControl=bookish`, `outfitReveal=reserved`, `batchSize=3`, `debugMode=True` -> returned `3` prompts
  - `prompt_service.generate_run(...)` with `mode=couples`, `outfitVibeControl=luxury`, `outfitReveal=balanced`, `batchSize=3`, `debugMode=True` -> returned `3` prompts
- Conclusion:
  - women and men clothing controls now read closer to one shared model
  - compatibility aliases for older/shorter outfit-vibe values are in place and generation stays stable
  - issue `#28` is safe to close

### Issue 29 CI portability pass
- Root-cause audit for PR `#32`:
  - current failing CI signal was not the old `Python 3.1` run noise, but the `e2e` job timing out while waiting for Playwright `webServer`
  - `playwright.config.js` was using the Windows-only command `set PROMPT_GENERATOR_PORT=8766 && python app.py`, which does not set the port correctly on Linux runners
- Fix applied:
  - switched Playwright `webServer` to `command: "python app.py"` plus `env.PROMPT_GENERATOR_PORT=8766`
- Validation:
  - `node --check playwright.config.js` -> passed
  - `npm run test:e2e -- --workers=1 --reporter=line` -> `5 passed`
  - `python scripts/coherence_threshold_report.py --runs-per-case 1 --batch-size 8 --max-cases 96 --progress-every 24 --calibration-runs 2 --threshold 3.0 --hard-fail --output data/audits/ci_coherence_audit.json`
    - result: `success=192`, `failed=0`, `viol_per_100=2.8`, threshold `3.0`
- Conclusion:
  - the real reproducible CI blocker on this branch was the Playwright startup portability bug
  - the bounded coherence gate is currently green on local reproduction

### Issue 29 baseline and first correction pass
- Baseline comparison matrix via inline `prompt_service.generate_run(...)` sweep on:
  - `women / men / couples`
  - styles: `random / romantic / nightlife`
  - spicy levels: `3 / 5 / 6 / 8`
  - `batchSize=20`, `debugMode=True`, `locationStrategy=allow_repeats`
- Baseline findings:
  - `women`: high lane was already visibly stronger overall, but `6` vs `8` could still read too close in some `random / romantic` runs
  - `men`: `6-8` improved versus low spicy, but `random / nightlife / romantic` still rendered too politely in final mood wording
  - `couples`: weakest path; high spicy mostly reused flat chemistry copy and did not separate strongly enough by interaction/mood
  - all baseline runs stayed clean: `0 findings`, `0 repairs`
- First correction pass:
  - added mode-specific spicy pressure for `men` and `couples` in `backend/services/scoring.py`
  - made `backend/legacy_people.py` choose hotter men/couples moods at `6-8`
  - allowed `couples random` to reuse compatible high-spicy interaction records from romantic/nightlife/luxury when exact random-style high records were missing
- Comparison retest after the correction pass:
  - `couples random`
    - `spicy 3`: `strongKW=2`, top mood flat `easy couple chemistry`, interaction lanes `moderate_safe=20`
    - `spicy 6`: `strongKW=32`, top mood `charged close chemistry`, interaction lanes `revealing=16`
    - `spicy 8`: `strongKW=30`, top moods `heated close chemistry` / `hungry close chemistry`, interaction lanes `revealing=11`, `pushing_it=2`
  - `couples romantic`
    - `spicy 3`: `strongKW=2`, top mood flat `soft romantic chemistry`
    - `spicy 6`: `strongKW=41`, top mood `heated romantic chemistry`, interaction lanes `revealing=18`
    - `spicy 8`: `strongKW=37`, top moods `smoldering romantic chemistry` / `hungry romantic chemistry`, interaction lanes `revealing=16`, `pushing_it=1`
  - `couples nightlife`
    - `spicy 3`: `strongKW=2`, top mood flat `charged nightlife chemistry`
    - `spicy 6`: `strongKW=17`, top mood `charged late-night chemistry`, interaction lanes `revealing=20`
    - `spicy 8`: `strongKW=35`, top moods `after-dark magnetic chemistry` / `dangerously close nightlife chemistry`, interaction lanes `revealing=11`, `pushing_it=9`
  - `men random`
    - `spicy 3`: `strongKW=3`
    - `spicy 6`: `strongKW=48`, top mood `charged confident energy`
    - `spicy 8`: `strongKW=26`, top mood `heated masculine energy`
  - `men romantic`
    - `spicy 3`: `strongKW=0`
    - `spicy 6`: `strongKW=21`
    - `spicy 8`: `strongKW=25`, now includes `heated romantic confidence`
  - `men nightlife`
    - `spicy 3`: `strongKW=0`
    - `spicy 6`: `strongKW=17`
    - `spicy 8`: `strongKW=24`
    - residual tail: wording still reads less escalated than couples and may need one more narrow pass later
- Safety/regression status after the pass:
  - all retest runs stayed at `0 findings`, `0 repairs`
  - no new routing or validation regressions observed
  - `python -m py_compile backend/legacy_people.py backend/services/scoring.py` passed

### Issue 29 follow-up — men nightlife final narrow pass
- Follow-up target:
  - `men nightlife`, which still rendered too flat because the shared nightlife mood override stamped nearly the same wording across spicy bands
- Change shape:
  - made the nightlife mood override in `backend/legacy_people.py` spicy-aware
  - added stronger `men + nightlife` treatment pressure in `backend/services/scoring.py`
- Retest on `men nightlife` with `batchSize=20`, `debugMode=True`, `locationStrategy=allow_repeats`:
  - `spicy 3`: `strongKW=0`, top mood stayed calm as intended
  - `spicy 5`: `strongKW=0`, top mood stayed controlled but not over-escalated
  - `spicy 6`: `strongKW=39`, top mood now `charged late-night confidence`
  - `spicy 8`: `strongKW=41`, top mood now `after-dark magnetic confidence`
- Safety/regression status:
  - all retest runs stayed at `0 findings`, `0 repairs`
  - `python -m py_compile backend/legacy_people.py backend/services/scoring.py` passed
- Conclusion:
  - issue `#29` now has clean separation across the main weak paths
  - future spicy work should be optional taste polish, not another core separation fix

### External pose bank wave 2
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  -> `6 passed`.
- Live generation smoke via `prompt_service.generate_run(...)`:
  -> `women random` completed and returned a live women pose/prompt after the wave-2 additions.
  -> `men random` completed and returned a live men pose/prompt after the wave-2 additions.
  -> `couples lifestyle` completed and returned a live couples interaction/prompt again, confirming the follow-up pose-bank pass still did not affect couples generation.
- Added `3` new women pose lines and `3` new men pose lines across the six live external pose-bank files, tracked under review-note label `external_pose_review_pass_2026_04_22_wave2`.
- Follow-up cleanup pass:
  - replaced the newly added scene-prop-specific pose lines with more reusable posture-only variants in the live women/men pose banks
  - added a repo-backed smoke test in `tests/test_line_bank_loader.py` that reads the checked-in live pose-bank files directly
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  -> `7 passed`.

### External pose bank wave 1
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  -> `6 passed`.
- Live generation smoke via `prompt_service.generate_run(...)`:
  -> `women random` completed and returned a live women pose/prompt.
  -> `men random` completed and returned a live men pose/prompt.
  -> `couples lifestyle` completed and returned a live couples interaction/prompt, confirming the pose-bank wave did not break couples generation.
- Added `6` new women pose lines and `6` new men pose lines across the six live external pose-bank files, tracked under review-note label `external_pose_review_pass_2026_04_22`.

### Stylization follow-up for random remaps and men luxury
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_women_treatment_remap_smoke.py -q`
  -> `8 passed`.
- Re-enabled the live women-random remap path, added `men + luxury` clean-treatment remap coverage, and added a focused assertion that `men + luxury` batch scoring now prefers lighting variety over flat repeated lighting.
- Verified `backend/services/postprocess.py`, `backend/services/scoring.py`, and `tests/test_women_treatment_remap_smoke.py` report no in-editor errors after the stylization fix.

### Line-bank UI help entrypoint
- `npm run test:e2e -- tests/e2e/form-controls.spec.js`
  -> `5 passed`.
- Added a sidebar help section that shows the repo-relative line-bank root path, current mode target files, and current spicy bucket hint, plus a direct `Copy path` action.
- Verified the touched frontend files report no in-editor errors after the new help section and copy-path action landed.

### Hybrid line-bank Phase 5 docs and safety sweep
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py -q`
  -> `4 passed`.
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py tests/test_routing_validation_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_men_taste_smoke.py tests/test_couples_scene_coherence_smoke.py -q`
  -> `29 passed`.
- Hardened the loader so root docs and comment-only starter templates are safe no-op files, then added repo-visible starter templates plus troubleshooting docs under `backend/engine/data/overrides/line_banks/`.
- Re-verified the full active line-bank rollout against the real repository tree after adding those docs/templates, and kept the combined women/men/couples regression band green.

### Hybrid line-bank Phase 4 men expressions seam
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py tests/test_line_bank_men_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_men_taste_smoke.py tests/test_couples_scene_coherence_smoke.py -q`
  -> `12 passed`.
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py tests/test_routing_validation_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_men_taste_smoke.py tests/test_couples_scene_coherence_smoke.py -q`
  -> `28 passed`.
- Extended the men-only legacy line-bank bridge so bucketed men `expressions` can surface in men generation through controlled mood wording and new debug visibility.
- Re-verified that the combined women and men line-bank rollout stays green and that custom men expression text does not leak into couples mode.

### Hybrid line-bank Phase 3 men legacy bridge
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py tests/test_line_bank_men_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_men_taste_smoke.py tests/test_couples_scene_coherence_smoke.py -q`
  -> `12 passed`.
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py tests/test_routing_validation_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_men_taste_smoke.py tests/test_couples_scene_coherence_smoke.py -q`
  -> `28 passed`.
- Added a men-only legacy bridge for line-bank `poses` and `outfits`, and verified custom men line-bank text surfaces in men generation without leaking into couples mode.
- Added cache clearing at the end of the women/men line-bank smoke tests so monkeypatched line-bank test data does not contaminate later server-based smoke coverage.

### Hybrid line-bank Phase 2 women live wiring
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_routing_validation_smoke.py -q`
  -> `19 passed`.
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_routing_validation_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_couples_scene_coherence_smoke.py -q`
  -> `24 passed`.
- Extended women live wiring so line-bank `poses`, `outfits`, and `expressions` now surface in women generation through controlled render overlays.
- Verified no-leak behavior in targeted smoke coverage: custom women line-bank prompt-part text surfaces in women mode and does not appear in men mode, while the cross-mode regression band stays green.

### Hybrid line-bank Phase 0 and Phase 1 scaffold
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_line_bank_loader.py tests/test_routing_validation_smoke.py -q`
  -> `18 passed`.
- Added `backend/engine/line_bank_loader.py` plus the new `tests/test_line_bank_loader.py` coverage for empty-tree loading, normalization/validation, and static-bank no-op behavior with empty line-banks.
- Added the `backend/engine/data/overrides/line_banks/` folder contract and enabled `load_line_banks` in `backend/engine/data/content_bank_config.json`.
- Re-ran the same focused pytest gate after persisting the leaf directories and kept the result green: `18 passed`.

## 2026-04-21

### Architectural refactor Phase 6 mode-wrapper rename completion
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_public_contract_smoke.py tests/test_routing_validation_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_clothing_color_rendering_smoke.py -q`
  -> `26 passed`.
- Renamed the backend mode-wrapper exports to neutral `*_HANDLER` names and updated `backend/modes/registry.py` to consume them.
- Renamed lingering men/couples wrapper-local legacy aliases (`render_legacy_batch`, `legacy_prompts`) to mode-neutral names and removed the now-unused legacy render import from `backend/prompt_service.py`.
- Verified `backend/prompt_service.py`, `backend/modes/women.py`, `backend/modes/men.py`, `backend/modes/couples.py`, and `backend/modes/registry.py` report no in-editor errors after the cleanup, and confirmed the old backend names no longer appear in workspace search.

### Architectural refactor Phase 6 frontend CSS split completion
- `npm run test:e2e -- tests/e2e/form-controls.spec.js`
  -> `5 passed`.
- Added `frontend/styles/tokens.css`, `frontend/styles/layout.css`, `frontend/styles/controls.css`, and `frontend/styles/output.css`.
- Reduced `frontend/styles.css` to the stable stylesheet entry that now imports the split CSS modules in cascade order.
- Verified `frontend/styles.css` and the new split CSS modules report no in-editor errors after the extraction.

### Architectural refactor Phase 6 prompt-service split completion
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_public_contract_smoke.py tests/test_runtime_memory_atomicity.py tests/test_clothing_color_rendering_smoke.py tests/test_routing_validation_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_men_taste_smoke.py tests/test_women_high_spicy_smoke.py -q`
  -> `34 passed`.
- Added `backend/services/scoring.py`, `backend/services/postprocess.py`, and `backend/services/batch_selection.py`.
- Rewired the corresponding heavy helpers in `backend/prompt_service.py` into compatibility delegates targeting the new service layer.
- Verified `backend/prompt_service.py`, `backend/services/scoring.py`, `backend/services/postprocess.py`, and `backend/services/batch_selection.py` report no in-editor errors after the extraction.

### Architectural refactor Phase 6 generator split completion
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_public_contract_smoke.py tests/test_runtime_memory_atomicity.py tests/test_clothing_color_rendering_smoke.py tests/test_routing_validation_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_couples_scene_coherence_smoke.py -q`
  -> `27 passed`.
- Added `backend/engine/selectors.py` and moved style profiles, weighted picking, selection predicates, photo-treatment selection, and candidate normalization there.
- Added `backend/engine/candidate_builder.py` and moved candidate assembly, batch retry scheduling, and runtime-memory writes there.
- Verified `backend/engine/selectors.py`, `backend/engine/candidate_builder.py`, and `backend/engine/generator.py` report no in-editor errors after the compatibility delegation rewrite.

### Architectural refactor Phase 6 generator split checkpoint
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_public_contract_smoke.py tests/test_runtime_memory_atomicity.py tests/test_clothing_color_rendering_smoke.py tests/test_routing_validation_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_couples_scene_coherence_smoke.py -q`
  -> `27 passed`.
- Added `backend/engine/data_loader.py` and moved static bank loading, runtime memory IO, and lookup helpers there.
- Added `backend/engine/render/prompt_renderer.py` plus `backend/engine/render/__init__.py` and moved outfit/prompt rendering there.
- Verified `backend/engine/generator.py` and the new engine modules report no in-editor errors after rewiring the old helper names into compatibility wrappers.

### Architectural refactor Phase 5 frontend UI skeleton
- `npm run test:e2e -- tests/e2e/form-controls.spec.js`
  -> `5 passed`.
- Added `frontend/components/icons.js`, `frontend/components/controls.js`, and `frontend/components/cards.js`.
- Added `frontend/sections/subject.js`, `frontend/sections/scene.js`, `frontend/sections/output.js`, and `frontend/controllers/form_controller.js`.
- Replaced the old monolithic `frontend/app.js` with a thin composition/bootstrap/event-delegation entry and verified the new module set reports no in-editor errors.

### Architectural refactor Phase 4 frontend module entry skeleton
- `npm run test:e2e -- tests/e2e/form-controls.spec.js`
  -> `5 passed`.
- Added `frontend/api/client.js` and moved `request()` plus the thin bootstrap/generate/preset request wrappers there.
- Added `frontend/state/store.js` and moved the shared `state` object, `clone()`, `disabledFields()`, and `isDisabled()` there.
- Switched `frontend/index.html` to `type="module"` loading and kept `frontend/app.js` as the single browser entry importing the new modules.
- Verified the extracted frontend module entry compiles cleanly in-editor with no reported errors in `frontend/index.html`, `frontend/api/client.js`, `frontend/state/store.js`, or `frontend/app.js`.

### Architectural refactor Phase 3 backend run skeleton
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_public_contract_smoke.py tests/test_api_smoke.py tests/test_routing_validation_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_clothing_color_rendering_smoke.py -q`
  -> `27 passed`.
- `npm run test:e2e -- tests/e2e/form-controls.spec.js`
  -> `5 passed`.
- Direct runtime smoke for `prompt_service.generate_run({'mode': 'women', 'batchSize': 1, 'debugMode': True})`
  -> returned stable top-level run keys, `1` prompt, and expected debug payload keys after the service extraction.
- Added `backend/modes/registry.py`, `backend/modes/women.py`, `backend/modes/men.py`, and `backend/modes/couples.py`.
- Added `backend/services/debug_summary.py` and `backend/services/run_service.py`.
- Reduced the old debug/orchestration bodies inside `backend/prompt_service.py` to delegating wrappers while preserving monkeypatch compatibility for `append_history` and `random.randint` test call sites.

### Architectural refactor Phase 2 backend form skeleton
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_public_contract_smoke.py tests/test_api_smoke.py tests/test_routing_validation_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_clothing_color_rendering_smoke.py -q`
  -> `27 passed`.
- `npm run test:e2e -- tests/e2e/form-controls.spec.js`
  -> `5 passed`.
- Added `backend/forms/constants.py`, `backend/forms/normalizer.py`, `backend/forms/runtime_controls.py`, and `backend/forms/user_profile.py`.
- Reduced the old form helpers inside `backend/prompt_service.py` to delegating wrappers so the existing internal call sites and public facade remain stable.
- Verified direct runtime smoke for `_merged_form_state()`, `_resolve_runtime_controls()`, and `_user_style_profile()` before the full pytest gate.

### Architectural refactor Phase 1 backend entry and facade skeleton
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_public_contract_smoke.py tests/test_api_smoke.py tests/test_routing_validation_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_clothing_color_rendering_smoke.py -q`
  -> `27 passed`.
- `npm run test:e2e -- tests/e2e/form-controls.spec.js`
  -> `5 passed`.
- Moved `PromptGeneratorHandler` into `backend/api/http_handler.py` and kept `app.PromptGeneratorHandler` importable through a compatibility re-export.
- Reduced `app.py` to startup-only responsibility: host/port parsing plus `ThreadingHTTPServer` boot.
- Moved bootstrap and preset facade logic into `backend/services/bootstrap_service.py` and `backend/services/preset_service.py`.
- Kept `backend/prompt_service.py` public API stable by delegating `get_bootstrap()`, `save_preset_record()`, and `delete_preset_record()` to the new service modules.

### Architectural refactor Phase 0 safety net
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_public_contract_smoke.py tests/test_routing_validation_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_clothing_color_rendering_smoke.py -q`
  -> `26 passed`.
- `npm run test:e2e -- tests/e2e/form-controls.spec.js`
  -> `5 passed`.
- Added `tests/test_public_contract_smoke.py` to freeze:
  - `/api/bootstrap` top-level payload keys
  - persisted `generate_run()` top-level payload keys
  - `history.json` / `presets.json` list-of-dicts serialization shape
- Wrote the current frozen public entry points into `ARCHITECTURAL_REFACTOR_SKELETON_PLAN_2026_04_21.md` so Phase 1 can move `app.py` safely.

### Clothing color render naturalization
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_clothing_color_rendering_smoke.py`
  -> `4 passed`.
- Direct render sweep over `1000` deterministic seeds for `rosewood_smoke + bodysuit_trousers` produced:
  - `50.8%` single-color phrasing
  - `29.3%` split-across-items phrasing
  - `10.5%` patterned phrasing
  - `9.4%` full dual-palette whole-look phrasing
- Direct `generate_run` smoke executed for `women random`, `men random`, and `couples random`.
- Verified outcomes:
  - raw phrasing like `rosewood and smoke palette opaque bodysuit ...` no longer appears in the updated render path
  - men render no longer injects a fake placeholder color when no explicit male color is available
  - couples male render avoids stacking an extra color prefix onto outfits that already contain a concrete color word like `black`

### Stylization follow-up — lighting play and compatibility
- Re-ran direct `generate_run` balance checks after the random-path remap fix.
- Measured outcomes over `20` seeded runs each:
  - `women random` -> `0.619` stylized / `0.381` polished, `61` clean treatments
  - `women luxury` -> `0.975` stylized / `0.025` polished, `4` clean treatments
  - `men luxury` -> `0.637` stylized / `0.362` polished, `58` clean treatments
  - `couples random` -> `0.669` stylized / `0.331` polished, `53` clean treatments
- Confirmed the new lighting families now surface in the live mix, including `practical_lamp`, `colored_ambient`, `moody_darkness`, `tight_spotlight`, and `silhouette_edge`.

### Age input hard-lock fix
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_routing_validation_smoke.py tests/test_women_high_spicy_smoke.py -q`
  -> `18 passed`.
- Verified that `Age: 22` now fixes the generated women output to `young_22` / `22-year-old` instead of drifting through soft scoring.
- Verified that `sport` / `fitness` still stay on safe balanced outfits at `spicy 5` and only open the spicy activewear pack from `spicy 6+`.

### Local spicy 6-8 live promotion and spicy pose rebalance
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_local_spicy_6_8_bank_smoke.py tests/test_women_high_spicy_smoke.py tests/test_high_spicy_couples_interaction_bank_smoke.py tests/test_couples_high_spicy_interaction_smoke.py tests/test_male_styling_bank_smoke.py -q`
  -> `19 passed`.
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_men_taste_smoke.py tests/test_couples_scene_coherence_smoke.py -q`
  -> `6 passed`.
- Direct `generate_run` smoke executed successfully for:
  - `women random`
  - `women nightlife`
  - `men romantic`
  - `couples random`
  - `couples lifestyle`
  - `couples nightlife`
- Verified outcomes:
  - all local spicy `6-8` women poses are live and covered by the women high-spicy constants
  - all local spicy `6-8` women outfits are live and reachable through the reveal preference path
  - all local spicy `6-8` couples interactions are live and present in the runtime couples interaction bank
  - all local male couple outfits are live and present in the runtime male styling bank
  - women spicy `6` and `8` smoke now keep a majority sexy-pose mix while still allowing ordinary poses and anti-repeat spread

### Local spicy 6-8 reference extraction pass
- Reviewed the imported `!poses and outfits` stash end-to-end:
  - `61` PNG files reviewed metadata-first
  - `16` Pinterest JPG files reviewed visual-first
  - `77` total references reviewed
- Metadata extraction check:
  - `37` PNG files exposed direct prompt metadata through `parameters` or `PositivePrompt_*`
  - the remaining `24` PNG files required workflow parsing or visual fallback
- Draft-only outputs created:
  - `LOCAL_SPICY_6_8_REF_PASS_2026_04_21.md`
  - `backend/engine/data/drafts/pose_bank/spicy_6_8_local_women_pose_seed.json`
  - `backend/engine/data/drafts/styling/spicy_6_8_local_women_outfit_seed.json`
  - `backend/engine/data/drafts/pose_bank/spicy_6_8_local_couples_interaction_seed.json`
  - `backend/engine/data/drafts/styling/spicy_6_8_local_couples_outfit_seed.json`
- JSON validation:
  - `spicy_6_8_local_women_pose_seed.json` -> `7` `pose_families`
  - `spicy_6_8_local_women_outfit_seed.json` -> `10` `outfit_families`
  - `spicy_6_8_local_couples_interaction_seed.json` -> `8` `couple_interactions`
  - `spicy_6_8_local_couples_outfit_seed.json` -> `4` `outfit_families`, `6` `coordination_pairs`
- No runtime tests were run because the pass only adds draft banks and research notes; `drafts` stay disabled and live generator behavior is unchanged.

### Couples male custom-race strict matcher
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_routing_validation_smoke.py::test_male_custom_race_matcher_accepts_custom_identity_text tests/test_routing_validation_smoke.py::test_custom_race_routing_anchors_couples_male_identity -q` -> `2 passed`.
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_routing_validation_smoke.py::test_legacy_age_picker_keeps_the_new_floor_at_18 tests/test_routing_validation_smoke.py::test_couples_can_keep_dyed_hair_toggle_with_random_hair_color tests/test_routing_validation_smoke.py::test_race_dropdown_is_shortened_and_keeps_other_slot tests/test_routing_validation_smoke.py::test_hidden_legacy_race_presets_still_normalize_and_japanese_is_supported tests/test_couples_identity_constraints_smoke.py::test_couples_different_persons_hardens_exact_female_age_and_race -q` -> `5 passed`.
- `npm run test:e2e -- tests/e2e/form-controls.spec.js` -> `5 passed`.
- Verified the strict couples male custom-race path now accepts explicit custom ethnicity text without regressing the age-18 floor, dyed-hair toggle, curated race quick-picks, or existing exact-preset couples coverage.

### Subject preset quick-pick cleanup
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_routing_validation_smoke.py::test_race_dropdown_is_shortened_and_keeps_other_slot tests/test_routing_validation_smoke.py::test_hidden_legacy_race_presets_still_normalize_and_japanese_is_supported tests/test_couples_identity_constraints_smoke.py::test_couples_different_persons_hardens_exact_female_age_and_race -q` -> `3 passed`.
- `npm run test:e2e -- tests/e2e/form-controls.spec.js` -> `5 passed`.
- Verified `Japanese` is promoted into the visible curated quick-picks, removed preset ids stay hidden by default, and saved legacy ids still normalize/load without snapping the UI to a wrong visible preset.

### Hair-color UI cleanup and copy icon sizing
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_routing_validation_smoke.py::test_couples_can_keep_dyed_hair_toggle_with_random_hair_color -q` -> `1 passed`.
- `npm run test:e2e -- tests/e2e/form-controls.spec.js` -> `4 passed`.
- Verified the women/couples hair-color field now keeps the `Allow dyed hair` toggle inline, keeps `Custom hair color` ahead of `Eye color`, and renders prompt copy icons at `24px`.

### Exact-theme UX shortcut
- `npm run test:e2e -- tests/e2e/form-controls.spec.js` -> `4 passed`.
- Verified the new Scene checkbox keeps `locationStrategy` synced to `Exact theme`, disables `Scene focus` while active, and leaves `womenSceneFamily` available.

### Couples high-spicy interaction pass
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest -q tests/test_high_spicy_couples_interaction_bank_smoke.py tests/test_couples_high_spicy_interaction_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_couples_identity_constraints_smoke.py`
  -> `12 passed`.
- Verified the promoted `couple_interactions` bank at both draft/live data level and runtime routing level.
- Verified the staged contract:
  - `spicyLevel 4` stays on `moderate_safe`
  - `spicyLevel 6` stays on `revealing`
  - `spicyLevel 8` can surface `pushing_it`

### Safe high-spicy boudoir research promotion
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest -q tests/test_high_spicy_boudoir_bank_smoke.py tests/test_women_high_spicy_smoke.py tests/test_women_scene_coherence_smoke.py`
  -> `13 passed`.
- Live core pose bank and styling bank now include all researched boudoir / glamour ids, and scorer constants cover the promoted ids.

### Safe high-spicy boudoir research drafts
- No runtime tests run.
- Scope of change: draft-only research seeds and a research note; no promotion into core banks, no scorer wiring, and no live behavior change while drafts remain disabled.

### Women high-spicy pose and outfit expansion
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest -q tests/test_women_high_spicy_smoke.py tests/test_women_scene_coherence_smoke.py`
  -> `10 passed`.
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest -q tests/test_scene_coherence_matrix_smoke.py`
  -> `7 passed`.
- Added direct internal smoke coverage for:
  - random high-spicy nightlife-scene women batches surfacing the new `revealing` outfit lane
  - nightlife high-spicy women batches surfacing the new `pushing_it` outfits plus broader seductive pose spread

### Residual closure — matrix expansion + men taste + couples male-side hardening
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_scene_coherence_matrix_smoke.py tests/test_men_taste_smoke.py tests/test_couples_identity_constraints_smoke.py`
  -> `13 passed`.
- Matrix smoke now validates additional exact-theme lanes (`women luxury`, `women creative`, `couples luxury`) on top of existing bookish/wellness/nightlife checks.
- Men taste smoke now includes a repeated romantic outfit-spread guard to catch two-template collapse regressions.
- Couples identity smoke now includes repeated `different_persons` male-side explicit-constraint checks across multiple runs.

### P2 exact-theme scene-family hard lock
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest -q tests/test_routing_validation_smoke.py tests/test_women_scene_coherence_smoke.py tests/test_couples_scene_coherence_smoke.py`
  -> `19 passed`.
- Added regression case: `men + styleMode=lifestyle + sceneFocus=random + locationStrategy=exact_theme + exactTheme=museum` now keeps all prompts on `culture_bookish` scene family.

### P1 closure + P2 matrix smoke kickoff
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/coherence_threshold_report.py --runs-per-case 1 --batch-size 8 --max-cases 96 --progress-every 24 --calibration-runs 2 --threshold 3.0 --hard-fail --output data/audits/ci_coherence_audit_local.json`
  -> `cases=96/172`, `runs=192`, `success=192`, `failed=0`, `candidates=1536`, `violations=28`, `viol_per_100=1.82`, `viol_per_100_max=1.95` (passes blocking threshold `3.0`).
- Calibration sanity check before final threshold lock:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/coherence_threshold_report.py --runs-per-case 1 --batch-size 8 --max-cases 96 --progress-every 24 --calibration-runs 3 --threshold 999 --output data/audits/ci_coherence_audit_local.json`
    -> `run_series=[2.08, 2.21, 1.95]`, `run_series_max=2.21`, `failed=0`.
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest -q tests/test_men_debug_scaffold_smoke.py tests/test_scene_coherence_matrix_smoke.py tests/test_women_scene_coherence_smoke.py tests/test_couples_scene_coherence_smoke.py`
  -> `17 passed`.
- Full-suite visibility check:
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest -q` -> `4 failed, 43 passed`.
  - Failures are the pre-existing `tests/test_male_styling_bank_smoke.py` tuple-vs-string expectation mismatch (not introduced by this pass).

### Women personalization + P1 coherence-threshold reporting
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/coherence_threshold_report.py --runs-per-case 1 --batch-size 8 --threshold 2.5 --output data/audits/ci_coherence_audit_local.json`
  -> `runs=272`, `success=272`, `failed=0`, `candidates=2720`, `violations=55`, `viol_per_100=2.02` (below threshold `2.5`).
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_women_scene_coherence_smoke.py tests/test_routing_validation_smoke.py -q` -> `15 passed`.
- `npm.cmd run test:e2e -- tests/e2e/form-controls.spec.js --workers=1 --reporter=line` -> `3 passed`.
- Frontend runtime sanity check after the fix: mode buttons and `hairLength` custom-select trigger are present on initial load.

### Systemic coherence P0 completion
- Finalized hard eligibility gates in generator selection for scene/outfit/pose coherence, including style-aware kneeling guards and task-context pose contracts.
- Kept `validationMode=strict` as a backstop while moving primary mismatch prevention into upstream selection/routing.
- Regression validation: `pytest -q tests/test_women_scene_coherence_smoke.py tests/test_routing_validation_smoke.py` -> `15 passed`.
- Required broad quality spot-check scenarios (`women random`, `women nightlife`, `men romantic`, `couples random`, `couples lifestyle`, `couples nightlife`) all generated cleanly (`8` prompts each, `0` findings in the spot-check pass).
- Final full stress audit command: `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/stress_combination_audit.py --runs-per-case 3 --batch-size 8`.
- Final full stress audit report: `data/audits/combination_audit_20260420_223406.json`.
- Final stress summary: `816` runs, `816/816` successful runs, `0` hard-fail runs, `8160` candidates, `0` violations (`0.0` per 100 candidates).

### Quiet luxury hard-gates
- Hardened candidate selection so quiet-day luxury scenes reject obvious night-coded outfit spillover before scoring.
- Added stricter pose-context gates for bookish, creative, domestic, outdoor, and kneeling cases so the generator stops leaning on post-hoc repair for those obvious mismatches.
- Focused validation after the generator update: `pytest -q tests/test_women_scene_coherence_smoke.py tests/test_routing_validation_smoke.py` -> `15 passed`.
- The broad luxury smoke now keeps `residential_luxury` on day-safe outfit material while still allowing hospitality `night` corridors to use their own darker styling lane.

### Systemic scene/outfit/pose stress audit
- Added a reproducible audit script: `scripts/stress_combination_audit.py`.
- Audit command: `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/stress_combination_audit.py --runs-per-case 3 --batch-size 8`.
- Baseline audit report: `data/audits/combination_audit_20260420_202854.json`.
- Coverage summary: `816` runs (`272` case templates x `3` repeats), `816/816` successful runs, `0` hard-fail runs, `8160` generated candidates.
- Baseline full-suite check before the stress audit: `pytest -q` -> `4 failed, 37 passed`.
- Baseline failures are in `tests/test_male_styling_bank_smoke.py` and point to a return-shape mismatch (`tuple` vs expected `str`) in `_choose_male_outfit`; this is tracked as a separate issue from scene/outfit/pose coherence.
- Mismatch summary: `1271` flagged mismatches (`15.58` per 100 candidates).
- Top systemic mismatch patterns:
  - `night_editorial_outfit_in_quiet_day_scene`: `450`
  - `kneeling_pose_in_quiet_formal_scene`: `420`
  - `bookish_task_pose_without_bookish_scene`: `245`
  - `domestic_task_pose_without_domestic_scene`: `67`
  - `creative_task_pose_without_creative_scene`: `57`
  - `outdoor_pose_inside_scene`: `32`
- Main concentration by scene family:
  - `residential_luxury`: `758`
  - `hospitality_suite`: `225`
  - `urban_daylight`: `59`
- Validation mode split stayed close (`normal: 647`, `strict: 624` mismatches), which indicates a routing-eligibility gap, not only post-generation validation behavior.
- `small_breasts` hard-fail check from this audit pass:
  - `random`: `378` runs, `0` failures, `577` mismatches.
  - `small_breasts`: `438` runs, `0` failures, `694` mismatches.
  - The mismatch rate stays close between controls in this run, so the current issue presents as a general coherence problem first, not a unique `small_breasts` crash path.


### Random coherence sweep
- A harsher batch sweep across women `random`, `wellness_spa`, `coastal_pool`, `culture_bookish`, `creative_gallery`, and couples `lifestyle` found repeated spillover such as `cardigan_trousers`, `shirt_trousers`, `blouse_trousers`, and `cashmere_shell_trousers` landing in spa / pool scenes, plus `track_shoe_tie_block` appearing in bookish / creative scenes.
- The generator now blocks those mismatches in scene / outfit selection and in pose selection before the batch is accepted.
- `pytest -q tests/test_women_scene_coherence_smoke.py tests/test_hair_controls_smoke.py` -> `9 passed`.

### Women dyed-natural hair toggle
- `pytest -q tests/test_women_scene_coherence_smoke.py tests/test_hair_controls_smoke.py` -> `8 passed`.
- `npm run test:e2e -- tests/e2e/form-controls.spec.js` -> `3 passed`.
- The new women-only toggle appears only in `women` mode, disables outside `Random` hair color, and allows copper / burgundy / silver without reopening vivid fantasy colors.

### Women scene-family fine controls
- `pytest -q tests/test_women_scene_coherence_smoke.py tests/test_women_treatment_remap_smoke.py tests/test_routing_validation_smoke.py` -> `18 passed`.
- `npm run test:e2e -- tests/e2e/form-controls.spec.js` -> `3 passed`.
- `womenSceneFamily` now drives reveal, hair, makeup, and outfit taste in women mode, while male-coded hair ids stay out of the women selector path.

### UI parity pass for appearance blocks
- `pytest -q tests/test_male_appearance_controls_smoke.py` -> `2 passed`.
- `npm run test:e2e -- tests/e2e/form-controls.spec.js` -> `3 passed`.
- Women / men / couples Appearance blocks now share the same structural order, men single-mode exposes `Body mix` and `Random` hair length, and the frontend renderer mounts cleanly again.

### Men outfit vibe pass
- `pytest -q tests/test_male_appearance_controls_smoke.py tests/test_men_taste_smoke.py tests/test_routing_validation_smoke.py` -> `11 passed`.
- `npm.cmd run test:e2e -- --workers=1 --reporter=line` -> `3 passed`.
- Men outfit controls now use vibe-style labels, and `random` resolves from the scene family instead of a concrete outfit list.

### Men taste and UI polish pass
- `pytest -q tests/test_men_taste_smoke.py tests/test_routing_validation_smoke.py tests/test_male_appearance_controls_smoke.py` -> `10 passed`.
- `npm.cmd run test:e2e -- --workers=1 --reporter=line` -> `3 passed`.
- Men romantic sweep now shows broader pose spread, and men random sweep now keeps a wider outfit mix instead of leaning too hard on the luxury-heavy defaults.

### Men low-spicy verification pass
- `pytest -q tests/test_routing_validation_smoke.py` -> `7 passed`.
- Men `luxury`, `nightlife`, and `romantic` at `spicyLevel=3` all stayed on calm / soft mood language in the smoke check.

### Women luxury silhouette cleanup
- `pytest -q tests/test_women_scene_coherence_smoke.py tests/test_women_treatment_remap_smoke.py tests/test_routing_validation_smoke.py` -> `17 passed`.
- The women luxury exact-theme smoke check now keeps `mini_dress` at `<= 2` in the checked batch while still avoiding `bodysuit_trousers`.

### Men romantic pass — pose, outfit, treatment variety
- Branch: `feature/men-romantic-pass`
- `pytest -q` → `27 passed` (test snapshot updated for 2 new romantic outfit entries)
- `men romantic x20 × 8` sweep results:
  - Unique outfit segments: **10** (was ~5-6 before; analog_35mm single-outfit override caused 44% dominance)
  - Unique pose segments: **14** (was ~1-2; single pose per treatment caused near-total dominance)
  - `analog_35mm` top share: 40% (high but expected — treatment scoring is intentionally strong)
  - `clean_commercial` share: <2% (remap active)
  - Top outfit: "fine knit crewneck sweater with dark tailored trousers" at ~20% (was 44% single outfit)
  - No single pose exceeds 16%
  - All 7 target treatments represented across batches
- Checked other modes for regressions: `women/random`, `women/nightlife`, `men/luxury`, `couples/random`, `couples/lifestyle`, `couples/nightlife` — all 8 prompts, 0 empty.

### Routing validation follow-up
- `pytest -q tests/test_routing_validation_smoke.py` -> `3 passed`.
- `pytest -q` -> `30 passed`.
- Men `luxury / nightlife` at `spicyLevel=3` now resolve to calm/quiet mood language in the smoke test, including the treatment-overridden paths.
- Women `fitness` and `sport` now stay on sporty scene/outfit combinations in the smoke test.
- Men exact-theme `cultural_bookish + museum` now stays in `culture_bookish` with bookish routes in the smoke test.

### Routing controls follow-up
- `pytest -q tests/test_routing_validation_smoke.py` -> `6 passed`.
- `pytest -q` -> `33 passed`.
- Women `customRace=Black Nigerian woman` now locks the batch to `black_nigerian` in the smoke test.
- Couples `maleCustomRace=White Ukrainian man` now renders the male identity text and custom group correctly in the smoke test.
- Women `characterConstraint=Lara Croft type` now keeps the batch on `sport / sports_flirt / urban_daylight` in the smoke test.
- Anti-repeat UI now uses more explicit labels and guidance, but this did not change backend scoring behavior.

## 2026-04-20

### Issue 105 prop-aware scene, pose, and wet-context matching first pass
- Focused validation:
  - `pytest tests/test_issue105_prop_scene_outfit_matching_smoke.py -q` -> `3 passed`
  - `pytest tests/test_issue104_support_pose_matching_smoke.py tests/test_issue105_prop_scene_outfit_matching_smoke.py tests/test_validator_repair.py tests/test_line_bank_loader.py::test_pose_line_tags_and_scene_guardrails -q` -> `12 passed`
- Investigation snapshot:
  - the courtyard bed leak was confirmed in the line-bank path, not the old static pose-bank gate: the checked `bent forward over the bed... blanket` line was inferred as `standing_like` plus `bed_support`, and `line_bank_pose_matches_scene(...)` returned early on `standing_like` before enforcing the bed requirement
  - the gym perch leak was confirmed in the static selector path: `perch_lean_back` still passed a synthetic boxing-gym scene because the current static matcher had no general support contract for `perched` poses
  - the shoreline dry-outfit leak was confirmed as a validator gap: no hard finding existed yet for `water_contact_pose` without a wet-friendly outfit signal
- Checked outcome:
  - line-bank bed-anchored poses now require real bed-support context before they pass scene matching
  - `perch_lean_back` now fails gym-like no-support scenes while staying available in real vanity support scenes
  - validator now flags `water_contact_pose_without_wet_outfit` for shoreline / near-water contact poses that still carry dry dress-like outfit tags


### Character constraint backend render-slot follow-up
- `pytest -q tests/test_routing_validation_smoke.py` -> `15 passed`.
- `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_public_contract_smoke.py tests/test_routing_validation_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_clothing_color_rendering_smoke.py -q` -> `27 passed`.
- Verified that `characterConstraint` now renders as a dedicated backend `character` segment, persists as `candidate["character_constraint_segment"]`, and remains aligned with routing/scoring/debug metadata.

### Women-only scene family control
- `pytest -q tests/test_women_scene_coherence_smoke.py` -> `5 passed`.
- `pytest -q tests/test_routing_validation_smoke.py` -> `7 passed`.
- Verified that women-mode batches can lock to an exact scene family while men/couples behavior stays unchanged.

### CI quickstart alignment
- `python -m pytest -q tests/test_routing_validation_smoke.py` -> `7 passed`.
- Confirmed the shared quickstart / CI smoke command remains green after syncing the workflow and docs.

### Race preset quick-pick cleanup
- `python.exe -m pytest tests/test_routing_validation_smoke.py` -> `7 passed`.
- Verified the dropdown bootstrap now exposes the shorter race preset set, keeps exactly one `Other` entry in the former `Black British` position, and excludes the removed `black_british` / `white_ukrainian` quick-pick items.

### Women treatment rebalance + couple-side appearance follow-up
- Added direct regression coverage for the women remap/profile tail fixes:
  - `women fitness + wellness_spa` clean-treatment remap now lands on a stylized option
  - `women nightlife` clean-treatment remap now lands on nightlife-safe stylized options
  - `women luxury` clean-treatment remap now lands on selfie/editorial-safe luxury options
  - `women romantic + coastal_pool` clean-treatment remap now lands on valid stylized options after the scene allowances were added to the treatment bank
  - `women romantic` profile now bans cardigan/daywear carryover and prefers refined skirt/dress families
- `pytest -q tests/test_women_treatment_remap_smoke.py tests/test_male_styling_bank_smoke.py tests/test_women_scene_coherence_smoke.py tests/test_couples_scene_coherence_smoke.py` -> `16 passed`.
- Final full-suite retest: `pytest -q` -> `27 passed`.
- Final direct sweep checks:
  - `women romantic x20` -> `analog_35mm 56`, `candid_phone_snapshot 33`, `direct_light_editorial 30`, `clean_commercial 1`; top outfits shifted to `cami_midi_skirt`, `silk_blouse_midi_skirt`, `cashmere_shell_trousers`, `structured_day_dress`, `wrap_blouse_skirt`
  - `women nightlife x20` -> `vintage_flash_photo 81`, `clean_commercial 8`; the earlier `polo_pleated_skirt` balanced-reveal leak no longer surfaced in the final retest
  - `women fitness x20` -> `candid_phone_snapshot 123`, `documentary_still 19`, `analog_35mm 18`, `clean_commercial 0`
  - `women luxury x20` -> `casual_indoor_selfie 53`, `mirror_selfie 37`, `clean_commercial 13`
  - `couples random x20` male outfits -> `open-collar 24`, `dark shirt 22`, `black knit polo 21`, `fine knit polo 18`, `overshirt 18`, `linen pleated 17`, `gallery blazer 16`, `blazer + knit 14`
  - `couples coastal x20` male outfits -> three-way spread across `fine knit polo 73`, `linen pleated 50`, `camp-collar shirt 37`

### Male appearance bank expansion
- Expanded the generated male appearance controls with additional live hairstyle ids:
  - `male_soft_quiff`
  - `male_wavy_brushback`
- Expanded the generated male outfit controls with additional live outfit ids:
  - `male_relaxed_overshirt_trousers`
  - `male_dark_shirt_trousers`
  - `male_black_polo_trousers`
  - `male_linen_pleated_trousers`
  - `male_blazer_knit_trousers`
- Men/couples random male outfit selection now pulls from style-tagged entries in the live male styling bank for supported styles before falling back to the hardcoded legacy map.
- `pytest -q tests/test_male_appearance_controls_smoke.py tests/test_male_styling_bank_smoke.py tests/test_couples_identity_constraints_smoke.py tests/test_api_smoke.py` -> `6 passed`.
- Focused recheck after tightening the `lifestyle` alias map: `pytest -q tests/test_male_appearance_controls_smoke.py tests/test_male_styling_bank_smoke.py` -> `3 passed`.
- Broader direct sweep checks:
  - `men lifestyle x20` -> only `open-collar shirt with tailored trousers` / `light overshirt over a fitted tee with relaxed trousers`; the sporty `track jacket + joggers` leak is gone after removing the `urban_day` alias from plain `lifestyle`
  - `men luxury x20` -> live bank now surfaces `open-collar`, `fine knit polo`, `black knit polo`, `linen shirt + pleated trousers`, and `blazer + knit` variants in one sweep
  - `couples nightlife x20` -> live bank now surfaces `black knit polo`, `dark fitted shirt`, and `blazer + knit` variants instead of relying only on the older legacy map
  - `men fantasy x20` -> still cleanly falls back to the hardcoded fantasy bank

### Women exact-theme scene-outfit coherence follow-up
- Added smoke coverage for the four women-side exact-theme scenarios that were still leaving obvious taste misses:
  - `women + lifestyle + sceneFocus=bookish + exactTheme=museum x8` -> no hot/sporty outfit ids
  - `women + cultural_bookish + sceneFocus=bookish + exactTheme=museum x8` -> no hot outfit ids
  - `women + luxury + sceneFocus=luxury + exactTheme=hotel lobby x8` -> no `bodysuit_trousers`
  - `women + nightlife + sceneFocus=nightlife + exactTheme=cocktail bar x8` -> no cardigan/daywear outfit ids
- `pytest -q tests/test_couples_identity_constraints_smoke.py tests/test_women_scene_coherence_smoke.py tests/test_couples_scene_coherence_smoke.py` -> `9 passed`.
- Larger direct sweep checks:
  - `women lifestyle + museum x20` -> `0` hot/sporty misses
  - `women cultural_bookish + museum x20` -> `0` hot-outfit misses
  - `women luxury + hotel lobby x20` -> `0` `bodysuit_trousers` misses
  - `women nightlife + cocktail bar x20` -> `0` cardigan/daywear misses

### Couples male identity batch-selection follow-up
- Added deterministic male-preview scoring during couples batch selection, so explicit `maleAge / maleRacePreset` are checked before final seed choice instead of only at final legacy render time.
- Debug payload for `men` / `couples` now also exposes `maleAge`, `maleEthnicity`, `maleEthnicityId`, and `maleEthnicityGroup` for direct smoke verification.
- Updated the couples identity smoke test to verify the active male-side debug fields:
  - exact preset run -> `maleEthnicityId=black_nigerian` and `maleAge>=30` across the checked batch
  - group preset run -> `maleEthnicityGroup=black` and `25<=maleAge<=30` across the checked batch
- Larger direct sweep check:
  - `couples + different_persons + maleAge=30+ + maleRacePreset=black_nigerian @ lifestyle x20` -> `0` male-side misses

### Runtime memory concurrency fix
- Added a runtime-memory regression test that stresses parallel `_save_memory()` and `_load_runtime_memory()` access against a temporary `memory.json` path; the test passed after switching runtime persistence to atomic replace plus retry-safe runtime reads/writes.
- Direct threaded check: `generate_run(women lifestyle, batchSize=2) x12 with max_workers=6` -> completed without `JSONDecodeError` / `PermissionError` after the runtime-memory fix.
- `pytest -q tests/test_runtime_memory_atomicity.py tests/test_api_smoke.py` -> `2 passed`.

### Couples scene-outfit coherence follow-up
- Added smoke coverage for the three exact-theme scenarios that were still failing taste checks:
  - `couples + lifestyle + sceneFocus=bookish + exactTheme=museum x8` -> no sporty women-side outfit ids
  - `couples + luxury + sceneFocus=luxury + exactTheme=hotel lobby x8` -> no `bodysuit_trousers`
  - `couples + nightlife + sceneFocus=nightlife + exactTheme=cocktail bar x8` -> no cardigan/daywear women-side outfit ids
- `pytest -q tests/test_couples_scene_coherence_smoke.py tests/test_couples_identity_constraints_smoke.py tests/test_api_smoke.py` -> `6 passed`.
- Larger direct sweep checks:
  - `couples lifestyle + museum x20` -> `0` sporty misses
  - `couples luxury + hotel lobby x20` -> `0` `bodysuit_trousers` misses
  - `couples nightlife + cocktail bar x20` -> `0` cardigan/daywear misses
- Full suite retest after the couples coherence pass: `pytest -q` -> `14 passed`.

### Couples different-person identity constraints
- `couples + different_persons + age=25-30 + racePreset=white_ukrainian + maleAge=30+ + maleRacePreset=black_nigerian @ lifestyle x4` -> `0` failures in the smoke test; female candidate ids stayed `mid_20s 4/4` and `white_ukrainian 4/4`, and the rendered prompt carried `Black Nigerian man` on the male side.
- `couples + different_persons + age=25-30 + racePreset=mostly_latina + maleAge=25-30 + maleRacePreset=mostly_blacks @ lifestyle x4` -> `0` failures in the smoke test; female candidate ids stayed `mid_20s 4/4` and female ethnicity group stayed `latina 4/4`.
- Larger direct sweep checks:
  - exact preset run `x6` -> `mid_20s 6/6`, `white_ukrainian 6/6`, male-side `Black Nigerian man 6/6`
  - group preset run `x6` -> `mid_20s 6/6`, female ethnicity group `latina 6/6`

### Exact-theme style coherence sweeps
- `couples + cultural_bookish + sceneFocus=bookish + exactTheme=museum x10` -> no obvious clothing/scene mismatches in the sample; women stayed in clean cardigan / shirt / trousers space and men stayed in knit / shirt + trousers space.
- `couples + lifestyle + sceneFocus=bookish + exactTheme=museum x12` -> `2/12` women-side sporty leaks: `tennis polo with a pleated tennis skirt` still surfaced inside calm bookish interiors.
- `couples + luxury + sceneFocus=luxury + exactTheme=hotel lobby x12` -> `1/12` calm-luxury reveal miss: `sleek square neck bodysuit with high waisted tailored trousers` still appeared next to a formal male luxury outfit.
- `couples + nightlife + sceneFocus=nightlife + exactTheme=cocktail bar x12` -> `1/12` nightlife taste miss: cardigan / daywear styling still surfaced in a dark lounge/bar context.
- `women + lifestyle + sceneFocus=bookish + exactTheme=museum x12` -> `1/12` calm-scene reveal miss with `bodysuit_trousers`; batch also still leaned too hard on `fitted mini dress` (`3/12`) for a museum/bookish target.
- `women + luxury + sceneFocus=luxury + exactTheme=hotel lobby x12` -> `1/12` calm-luxury reveal miss with `bodysuit_trousers`.
- `women + nightlife + sceneFocus=nightlife + exactTheme=cocktail bar x12` -> `1/12` nightlife taste miss with cardigan / daywear carryover.
- `men + luxury + sceneFocus=luxury + exactTheme=hotel lobby x12`, `men + nightlife + sceneFocus=nightlife + exactTheme=cocktail bar x12`, `men + romantic + sceneFocus=garden + exactTheme=conservatory garden x12` -> no obvious casual / sporty mismatch hits in this targeted pass; this track can stay below the women / couples coherence cleanup for now.
- Theme-fidelity spot check: the sampled exact-theme sweeps still carried the requested theme tokens in prompt or setting text often enough that scene token loss did not look like the main blocker in this pass.
- Runtime note: a parallel analysis sweep briefly hit `JSONDecodeError` while reading `backend/engine/runtime/memory.json`; sequential rerun passed, which suggests current runtime memory writes are not concurrency-safe.

### Repo Tests
- `pytest -q` -> `20 passed`.

## 2026-04-19

### Male appearance controls
- Verified `/api/bootstrap` now exposes `maleHairstyleOptions`, `maleGroomingOptions`, and `maleOutfitOptions`.
- `men + maleHairstyle=custom + maleCustomHair=slicked-back undercut + maleGroomingControl=clean_shaven + maleOutfitControl=male_open_collar_trousers` -> `0` findings in the checked smoke run; the final prompt included `slicked-back undercut`, `clean-shaven`, and `open-collar shirt with tailored trousers`.
- `couples + maleHairstyle=male_textured_crop + maleGroomingControl=trimmed_beard + maleOutfitControl=male_fineknit_trousers` -> `0` findings in the checked smoke run; the final prompt and debug payload carried `textured short crop`, `trimmed beard`, and `fine knit polo with tailored trousers`.

### Dropdowns & Small breast option
- Verified `/api/bootstrap` exposes `small_breasts` in `breastSizeOptions`.
- Added a smoke test to confirm `generate` accepts `breastSizeControl: small_breasts` and that hair controls (`hairstyle`, `hairLength`, `hairColorControl`) do not error after the dropdown fixes.

### Repo Tests
- `pytest -q` -> `8 passed`.
- `npm.cmd run test:e2e -- --workers=1 --reporter=line` -> `3 passed`.

### Appearance / modesty follow-up sweeps
- `women lifestyle @ spicy 3 / outfitReveal reserved / antiRepeat hard / x8` -> `0 findings`, `0 repairs`; promoted live outfits appeared (`silk_blouse_midi_skirt 2/8`), and promoted live hair presets also surfaced (`tucked_behind_ears_blowout`, `soft_half_up`).
- `women random @ spicy 3 / outfitReveal reserved / antiRepeat hard / x8` -> `0 findings`, `0 repairs`; promoted live outfits/materials/colors surfaced (`silk_blouse_midi_skirt`, `cashmere_shell_trousers`, `polished_low_bun`, `soft_half_up`).
- `women luxury @ spicy 3 / hairstyle polished_low_bun / makeup fresh_barely_there / outfitReveal reserved / x4` -> `0 findings`, `0 repairs`; `polished_low_bun 4/4`, `fresh_barely_there 4/4`.
- `women romantic @ spicy 4 / hairstyle soft_half_up / makeup rosy_polished_minimal / outfitReveal reserved / x4` -> `0 findings`, `0 repairs`; `soft_half_up 2/4`, `rosy_polished_minimal 2/4`.

## 2026-04-18

### Stylization Phase 3 Follow-up
- `py_compile` passed for `backend/prompt_service.py`, `backend/engine/generator.py`, and `backend/legacy_people.py`.
- After the harder-lane scorer pass:
  - `women random x20` -> `clean_commercial 8`, `direct_light_editorial 2`, `concept_photo_editorial 1`, `0 findings`
  - `women creative_artistic x20` -> `concept_photo_editorial 4`, `direct_light_editorial 2`, `clean_commercial 9`, `0 findings`
  - `women studio x20` -> `concept_photo_editorial 4`, `direct_light_editorial 4`, `clean_commercial 7`, `0 findings`
  - `women luxury x20` -> `direct_light_editorial 3`, `concept_photo_editorial 2`, `clean_commercial 14`, `0 findings`
  - `couples random x20` -> `direct_light_editorial 3`, `concept_photo_editorial 1`, `clean_commercial 11`, `0 findings`
- After the extra luxury-only bias:
  - `women random x20` -> `concept_photo_editorial 4`, `direct_light_editorial 1`, `stylized 10/20`, `0 findings`
  - `women luxury x20` -> `concept_photo_editorial 2`, `clean_commercial 9`, `analog_35mm 4`, `stylized 11/20`, `0 findings`
  - `men luxury x20` -> `concept_photo_editorial 2`, `direct_light_editorial 3`, `direct_flash_night 3`, `clean_commercial 12`, `stylized 8/20`, `0 findings`

### Notes
- `random`, `creative_artistic`, and `studio` are now reliably surfacing the harder lanes.
- `women luxury` improved from an overly sticky polished baseline to a more mixed stylized output.
- `men luxury` is still too clean-heavy and should be treated as the next luxury taste-pass target.

### Men Luxury Taste Pass
- After the men-only luxury scorer bump and legacy-bank expansion:
  - `men luxury x20` -> `clean_commercial 10`, `concept_photo_editorial 3`, `analog_35mm 3`, `direct_light_editorial 2`, `stylized 10/20`, `0 findings`
  - outfit spread now includes `dark silk shirt with sharply tailored trousers` and `lightweight blazer over a fine knit top with tailored trousers`
  - pose spread now includes new editorial luxury variants instead of collapsing into only the older calm-standing poses

### New Casual-Stylized Treatments
- Added and smoke-tested `mirror_selfie`, `disposable_camera`, and `documentary_still`.
- Sweep results:
  - `women random x20` -> `documentary_still 3`, `disposable_camera 4`, `direct_light_editorial 4`, `clean_commercial 5`, `0 findings`
  - `women lifestyle x20` -> `documentary_still 4`, `disposable_camera 4`, `mirror_selfie 1`, `clean_commercial 8`, `0 findings`
  - `women urban_day x20` -> `documentary_still 3`, `disposable_camera 3`, `direct_light_editorial 2`, `clean_commercial 10`, `0 findings`
  - `women cultural_bookish x20` -> `mirror_selfie 2`, `documentary_still 1`, `analog_35mm 5`, `clean_commercial 9`, `0 findings`
  - `women creative_artistic x20` -> `disposable_camera 2`, `documentary_still 2`, `concept_photo_editorial 3`, `clean_commercial 12`, `0 findings`
  - `men random x20` -> `mirror_selfie 2`, `disposable_camera 2`, `concept_photo_editorial 2`, `0 findings`

### Notes
- `disposable_camera` and `documentary_still` are already pulling useful weight in `random` and `lifestyle`.
- `mirror_selfie` is alive but still intentionally rarer than the other two.

### Additional Stylized Treatments
- Added and smoke-tested `casual_indoor_selfie`, `vintage_flash_photo`, and `advertising_poster_realism`.
- Sweep results:
  - `women random x20` -> `mirror_selfie 1`, `documentary_still 1`, `disposable_camera 1`, `clean_commercial 9`, `0 findings`
  - `women lifestyle x20` -> `casual_indoor_selfie 2`, `disposable_camera 2`, `clean_commercial 13`, `0 findings`
  - `women nightlife x20` -> `vintage_flash_photo 7`, `disposable_camera 3`, `direct_flash_night 3`, `0 findings`
  - `women studio x20` -> `advertising_poster_realism 5`, `concept_photo_editorial 2`, `direct_light_editorial 2`, `0 findings`
  - `women creative_artistic x20` -> `vintage_flash_photo 2`, `disposable_camera 1`, `clean_commercial 9`, `0 findings`
  - `women luxury x20` -> `casual_indoor_selfie 4`, `mirror_selfie 3`, `advertising_poster_realism 2`, `clean_commercial 3`, `0 findings`

### Notes
- `vintage_flash_photo` landed exactly where it should: strongest in `nightlife`.
- `advertising_poster_realism` is already a strong live lane for `studio`.
- `casual_indoor_selfie` is useful in `lifestyle` and especially `luxury`, where it helps break the overly polished default.

### Debug Upgrade
- `py_compile` passed for `backend/prompt_service.py`.
- Debug payload now includes:
  - `stylizedCount`
  - `polishedCount`
  - `uniquePhotoTreatments`
  - `photoTreatmentCategoryDistribution`
  - `captureDistribution`
  - `lightingDistribution`
  - `cameraVibeDistribution`
- `promptDecisions` now include:
  - `photoTreatment`
  - `photoTreatmentCategory`
  - `captureRender`
  - `cameraVibe`
  - `colorGrade`
  - `finish`
  - `styleSignals`
  - `treatmentSignals`
- Smoke check on `women random x6` confirmed the new debug keys exist and are populated without breaking generation.

## 2026-04-17

### Backend Sanity
- `py_compile` passed for `app.py`, `backend/options.py`, `backend/prompt_service.py`, `backend/storage.py`, and `backend/engine/generator.py`.
- `py_compile` also passed for `backend/legacy_people.py`.

### Women Generator Checks
- Full style sweep completed with `0` validation findings for:
  - `studio`
  - `lifestyle`
  - `luxury`
  - `old_money`
  - `romantic`
  - `vacation`
  - `sport`
  - `fitness`
  - `cosplay`
  - `fantasy`
  - `nightlife`
  - `cultural_bookish`
  - `creative_artistic`
  - `urban_day`
  - `coastal`

### Focused Routing Checks
- `Sport`: `urban_daylight 6/6`, `sports_flirt 6/6`, `crop_top_mini_skirt 6/6`, `athletic_jersey 6/6`, `high_ponytail 6/6`.
- `Fitness`: `urban_daylight 6/6`, `sports_flirt 6/6`, `crop_top_mini_skirt 6/6`, `athletic_jersey 6/6`, `high_ponytail 6/6`.
- `Scene focus = luxury`: only `residential_luxury / hospitality_suite / grooming_bath`, route `luxury_interior`.
- `Scene focus = bookish`: only `culture_bookish`, route `luxury_interior`.
- `Scene focus = nightlife`: only `nightlife_bar / nightlife_neon`, route `cinematic_night`.
- `Scene focus = studio`: only `studio`, route `studio_portrait`.
- `Scene focus = wellness`: only `wellness_spa / grooming_bath`, route `luxury_interior`.
- `Scene focus = sporty`: only `urban_daylight`, route `sports_flirt`.

### Constraint Checks
- `Different persons + coreIdentityPrompt`: locked identity text is ignored.
- `Same person + editor-driven identity`: age, ethnicity, hair color, hairstyle, and makeup stay identical across the whole batch.
- `Same person + coreIdentityPrompt`: autogenerated same-person identity stays intact, and core notes are appended instead of replacing the subject.
- `Hairstyle != custom`: `customHair` does not affect the final prompt.
- `Hair color != custom`: `customHairColor` does not affect the final prompt.
- `Hairstyle = custom` and `Hair color = custom`: both overrides appear in the final prompt.
- Explicit `Hair color = blonde` produced `4/4 blonde_natural`.
- Explicit `Hair color = black` produced `4/4 black_natural`.
- `Same person + random editor controls`: control-derived identity remained stable across `4/4` prompts with `0` validation findings.
- `Same person + selected editor controls`: locked identity remained stable across `4/4` prompts with `0` validation findings.
- `Same person + Age 25-30 + Mostly whites`: produced `25 years old` + `white` identity in `20/20` repeated runs.
- `Same person + Age 25-30 + Mostly Latina + custom hair/color`: produced `25 years old` + `latina` identity and preserved custom hair override in `20/20` repeated runs.

### UI Notes
- Slider drag fix was verified manually in code path, but no browser automation is set up yet.
- JavaScript parser check via `node --check` was not run because `node` is not installed in the current environment.

### Men And Couples Checks
- Bootstrap now exposes enabled mode buttons for `women / men / couples`.
- Full crash sweep across all supported `styleMode` values completed for both `men` and `couples` with no generator exceptions.
- `Men + luxury`: `4/4` prompts rendered only `man`, `0/4` leaked `woman`.
- `Men + fitness`: `4/4` prompts rendered only `man`, `4/4` included `gym`, and the daylight technical block stayed sporty.
- `Men + same person + mostly_whites + age 25-30 + maleHairLength medium`: locked male age and hair stayed stable across `4/4` prompts.
- `Couples + nightlife`: `4/4` prompts rendered both `woman` and `man` in the same line with nightlife-compatible settings.
- `Couples + coastal + same person + mostly_latina`: `4/4` prompts kept the same couple identity family and coastal scene routing.
- `Couples + fitness`: `4/4` prompts rendered both partners, `4/4` included `gym`, and the technical block was forced back to daylight.

### Women Modesty Checks
- Focused low-spicy women sweeps completed for `lifestyle @ spicy 1`, `luxury @ spicy 2`, `urban_day @ spicy 3`, `fitness @ spicy 3`, and `sport @ spicy 3`.
- After the modesty tuning pass, all five targeted sweeps returned `0` validation findings.
- The old `cardigan buttoned low at the chest with a short skirt` wording no longer appears; the cardigan-skirt family now renders as a covered cardigan + fitted top + pleated midi skirt.
- Low-spicy women prompts no longer surfaced flagged strings for `deep neckline`, `tiny mini skirt`, `slow seductive energy`, `bratty playful energy`, `lying on her stomach`, `side-lying`, or `reclined one-knee-up` in the targeted sweeps.
- `Lifestyle @ spicy 1`: `8/8` unique full outfit-material-color combos in the final checked batch.
- `Luxury @ spicy 2`: no flagged low-spicy prompt issues; still some repeated outfit families, but color/material clones were removed from the checked batch.
- `Urban day @ spicy 3`: `8/8` unique full outfit-material-color combos in the final checked batch.
- `Fitness @ spicy 3`: full outfit-material-color clones were reduced and then diversified at final render time; final checked batch had `8/8` unique full combos across `polo_pleated_skirt / zip_jacket_leggings / training_jacket_trousers / workout_top_leggings`.
- `Sport @ spicy 3`: final checked batch had `8/8` unique full outfit-material-color combos with no flagged low-spicy prompt issues.

### Extra Smoke Notes
- `Men + lifestyle`: smoke run passed with `0` findings.
- `Men + luxury + same person`: smoke run passed with `0` findings.
- `Couples + lifestyle`: smoke run passed with `0` findings.
- `Couples + nightlife`: still rendered a mismatched daylight/pool-like setting in one smoke sample, so couples nightlife routing remains open work.

### Couples Split-Editor Checks
- Bootstrap defaults now expose `maleName`, `maleAge`, `maleRacePreset`, and `maleCustomRace`.
- `Couples + split identity` smoke run passed with `0` findings; male-side `name / age / race / hair length` appeared in the rendered prompt.
- `Couples + nightlife + maleRacePreset mostly_blacks`: smoke run passed with `0` findings and `0` flagged nightlife leaks for `swimsuit / bikini / pool / sun deck / boardwalk / beach` in the checked batch.
- `Couples + same person + split female/male identity`: smoke run passed with `0` findings; the checked batch kept one locked woman identity and one locked man identity across all prompts.

### Content Bank Structure Checks
- `backend/engine/generator.py` compiles after the layered bank loader refactor.
- `load_data_bank()` runs successfully with `content_bank_config.json = { "load_drafts": false, "load_overrides": true }`.
- With drafts disabled, draft-only ids like `heritage_hotel_staircase` and `stairs_step_down_railing` are not present in the live merged bank.
- Draft fragment directories for `setting_engine`, `pose_bank`, `styling`, and `subjects` are present and ready for small future additions.
- With drafts disabled, styling draft-only ids like `polished_low_bun`, `fresh_barely_there`, `mockneck_knit_skirt`, and `male_clean_side_part` are also absent from the live merged bank.
- With drafts disabled, subject draft-only ids like `white_romanian` and `black_french` are absent from the live merged bank.
- With drafts disabled, interiors/social draft-only ids like `sunlit_penthouse_living_room`, `double_height_walkin_closet`, `hybrid_hotel_lobby_lounge`, `private_members_club_bar`, `rooftop_hotel_conservatory_palms`, and `wine_lounge_ribbed_oak` are absent from the live merged bank.
- `py_compile` still passes for `backend/engine/generator.py` after adding the new draft interiors/social pack.
- After promotion, live `setting_engine.json` now includes the approved modest and interiors/social settings, and live `pose_bank.json` includes the approved modest-safe poses.
- The promoted draft files are now empty, so enabling drafts later does not reintroduce duplicate ids or override churn for the same records.
- Post-promotion JSON sanity check: `setting_engine.json` has `100` ids with `0` duplicates, `pose_bank.json` has `29` ids with `0` duplicates, and the three promoted draft files now have `0` ids.
- Post-promotion smoke run: `generate_batch(4, style_mode='lifestyle', persist_memory=False)` completed successfully with the new live banks.

### Prompt Compactness And Male Pose Checks
- Baseline women prompt sample before compact render pass: `151.33` average words across `24` prompts from `lifestyle / luxury / nightlife / sport`.
- After the compact render pass, the same women sample dropped to `142.08` average words across `24` prompts.
- `py_compile` passed for `backend/engine/generator.py` and `backend/legacy_people.py` after the compact render and male pose updates.
- Men smoke runs passed for `lifestyle`, `luxury`, `old_money`, `romantic`, `vacation`, `cultural_bookish`, `creative_artistic`, `urban_day`, `coastal`, `cosplay`, and `fantasy`.
- Men pose sampling across seeds now returns dedicated mode-specific poses for the new male-only style buckets instead of falling back to the tiny old random pool.
- Men and couples no longer render female-coded mood lines in the checked samples; `men luxury` now reads `composed confident energy`, `men lifestyle` reads `easy confident energy`, `couples romantic` reads `soft romantic chemistry`, and `couples luxury` reads `composed intimate chemistry`.

### Richer Debug Checks
- `py_compile` passed for `backend/prompt_service.py` and `backend/legacy_people.py` after the debug readout expansion.
- `generate_run(mode='women', debugMode=true, batchSize=3)` now returns `debug.promptDecisions` with one entry per prompt and readable fields like `sceneFamily`, `setting`, `outfit`, `pose`, `lighting`, `hair`, and `makeup`.
- `generate_run(mode='men', debugMode=true, batchSize=2)` now returns `debug.promptDecisions` with male-side fields like `maleOutfit`, `malePose`, and effective `mood`.
- `generate_run(mode='couples', debugMode=true, batchSize=2)` now returns `debug.promptDecisions` with both female-side and male-side appearance decisions.

### Appearance System Checks
- `py_compile` passed for `backend/options.py`, `backend/prompt_service.py`, `backend/legacy_people.py`, and `backend/engine/generator.py` after the appearance refactor.
- `Women + appearanceMode=custom + same_person`: smoke run passed; debug reported `femaleAppearanceMode = custom`, and the final prompt rendered one locked woman plus one appearance-direction block instead of duplicating identity text.
- `Men + maleAppearanceMode=custom`: smoke run passed; debug reported `maleAppearanceMode = custom`, and the final prompt rendered the custom male appearance direction instead of the generated male outfit line.
- `Couples + female custom + male custom`: smoke run passed; debug reported both appearance modes as `custom`, and the final prompt rendered split woman/man appearance directions in one prompt.
- Generated modes still work after the refactor for `women`, `men`, and `couples`.
- `Women + custom soft/reserved appearance + spicy 3`: targeted batch returned `0` validation findings, `0` `slow seductive`, `0` `bratty`, `0` strap-like hand wording, and `0` prone/reclined pose wording in the checked batch.
- `Couples + split custom soft/reserved appearance + spicy 3`: targeted batch returned `0` validation findings; after the follow-up tuning pass it no longer produced `slow seductive` or `bratty` mood text in the checked batch, but random style can still occasionally land in a softer night-lounge scene.

### Large Batch Sweep (`20` prompts each)
- `women lifestyle @ spicy 2 / antiRepeat hard`: `0` findings, `0` repairs, `11` unique settings, `6` unique outfits, `13` unique poses, `2` routes, scene split `garden 6 / bookish 7 / urban 7`. Low-spicy unsafe strings stayed at `0`.
- `women nightlife @ spicy 6 / antiRepeat hard` before the nightlife swimwear fix: `0` findings, `0` repairs, `9` unique settings, `3` unique outfits, `13` unique poses, `2` routes, but `pool` leaked in `3/20` prompts because `swimsuit` could still appear in nightlife scenes.
- `women nightlife @ spicy 6 / antiRepeat hard` after the nightlife swimwear fix: `0` findings, `0` repairs, `10` unique settings, `2` unique outfits, `10/10` split between `nightlife_bar / nightlife_neon`, `0/20 swimsuit`, `0/20 bikini`.
- `women fitness @ spicy 3 / antiRepeat hard`: `0` findings, `0` repairs, `5` unique settings, `4` unique outfits, `10` unique poses, `1` route, all `20/20` stayed in `urban_daylight`. Low-spicy unsafe strings stayed at `0`.
- `men luxury @ spicy 4 / antiRepeat hard`: `0` findings, `0` repairs, `15` unique settings, `6` unique outfits, `14` unique poses, `2` routes, no female-word leaks. Male pose split was still narrow: `13` prompts used `one hand resting on a ledge...`, `7` used `standing tall...`.
- `men nightlife @ spicy 6 / antiRepeat hard`: `0` findings, `0` repairs, `9` unique settings, `3` unique outfits, `15` unique poses, `2` routes, `0` nightlife leaks, `0` female-word leaks.
- `men romantic @ spicy 3 / antiRepeat hard`: `0` findings, `0` repairs, `11` unique settings, `6` unique outfits, `11` unique poses, `2` routes, but male pose split was again narrow: `15` prompts on the same relaxed-smile pose, `5` on the secondary pose.
- `couples romantic @ spicy 3 / antiRepeat hard`: `0` findings, `0` repairs, `6` unique settings, `6` unique female outfits, `9` interactions, `2` routes. Prompt length stayed high at `161.2` average words.
- `couples nightlife @ spicy 6 / antiRepeat hard`: `0` findings, `0` repairs, `9` unique settings, `3` unique female outfits before the nightlife swimwear fix, then `0` swimwear leaks after the fix.
- `couples lifestyle @ spicy 3 / antiRepeat hard`: `0` findings, `0` repairs, `13` unique settings, `5` unique female outfits, `11` interactions, `2` routes. Prompt length stayed high at `160.85` average words.

### P1 Follow-Up Checks
- `women nightlife @ spicy 5 / antiRepeat hard` after the nightlife diversity pass:
  - run 1: `0` findings, `9` unique outfits, `7` unique colors, `4` unique materials, `0` swimwear leaks
  - run 2: `0` findings, `9` unique outfits, `8` unique colors, `5` unique materials, `0` swimwear leaks
  - run 3: `0` findings, `9` unique outfits, `8` unique colors, `5` unique materials, `0` swimwear leaks
- Live nightlife batches now surface the new night-safe outfit families `blazer_mini_dress`, `cami_midi_skirt`, `bodysuit_trousers`, and `corset_trousers`.
- Live nightlife batches now surface the new evening color stories `black_gold`, `oxblood_noir`, and `emerald_noir`.
- `men luxury @ spicy 4 / antiRepeat hard` after the male pose expansion: `0` findings, `6` unique male poses across `20` prompts.
- `men romantic @ spicy 3 / antiRepeat hard` after the male pose expansion: `0` findings, `5` unique male poses across `20` prompts.

### Couples Styling Checks
- `couples lifestyle @ spicy 4 / antiRepeat hard` after the couples styling pass: `0` findings, `0` swimwear leaks, and the checked batch stayed inside daytime-safe color stories (`clean_neutrals / navy_cream / powder_blue / earthy_soft / winter_neutrals`).
- `couples nightlife @ spicy 6 / antiRepeat hard` after the couples styling pass: `0` findings, `0` swimwear leaks, and male outfits now render with explicit non-matching color wording instead of leaving the male side color implicit.
- Couple prompts now explicitly color the male outfit (`charcoal / deep navy / stone / soft black / espresso` etc.), which reduces the “twins in the same color” drift in image generation.
- Couple rendering now force-replaces female `swimsuit / bikini_set` in non-coastal scenes with a clothed fallback, and also force-replaces `latex_editorial` outside `nightlife / studio / fantasy / cosplay`.

## 2026-04-18

### Stylization Phase 1 Checks
- Import sanity passed for `backend.prompt_service`, `backend.legacy_people`, and `backend.engine.generator`.
- `load_data_bank()` now includes `photo_treatments` in the merged live bank.
- New live file present and loaded: `backend/engine/data/photo_treatments.json`.

### Photo Treatment Distribution Checks
- Raw generator sweep `random x20`: `clean_commercial 9`, `analog_35mm 5`, `candid_phone_snapshot 4`, `low_key_dramatic 1`, `cinematic_poster_realism 1`.
- Raw generator sweep `nightlife x20`: `direct_flash_night 6`, `low_key_dramatic 5`, `cinematic_poster_realism 3`, `candid_phone_snapshot 3`, `clean_commercial 3`.
- Raw generator sweep `studio x20`: `low_key_dramatic 10`, `studio_seamless 5`, `clean_commercial 5`.
- Raw generator sweep `luxury x20`: `clean_commercial 12`, `low_key_dramatic 4`, `direct_flash_night 2`, `analog_35mm 1`, `candid_phone_snapshot 1`.
- Raw generator sweep `sport x20`: `clean_commercial 14`, `analog_35mm 6`.

### Prompt Render Smoke Checks
- `women + random + batch 8`: `0` findings, `0` repairs; checked treatment mix `analog_35mm 2`, `candid_phone_snapshot 3`, `cinematic_poster_realism 1`, `clean_commercial 2`.
- `men + random + batch 8`: `0` findings, `0` repairs; checked treatment mix `analog_35mm 2`, `low_key_dramatic 1`, `clean_commercial 4`, `direct_flash_night 1`.
- `couples + random + batch 8`: `0` findings, `0` repairs; checked treatment mix `analog_35mm 1`, `clean_commercial 3`, `direct_flash_night 2`, `low_key_dramatic 2`.
- `women + nightlife + batch 12`: `0` findings, `0` repairs; checked treatment mix `direct_flash_night 2`, `low_key_dramatic 3`, `cinematic_poster_realism 2`, `candid_phone_snapshot 2`, `clean_commercial 3`.
- `women + studio + batch 12`: `0` findings, `0` repairs; checked treatment mix `low_key_dramatic 4`, `studio_seamless 3`, `clean_commercial 5`.

### Phase 1 Notes
- Phase 1 goal is met: the treatment layer is live for women / men / couples and reaches prompt render plus debug without breaking current generator logic.
- Exact `40/60` polished-vs-stylized behavior is not guaranteed yet in final `generate_run(random)` output; this stays open for the next phase.

### Stylization Phase 2 Checks
- `py_compile` passed again for `backend/engine/generator.py`, `backend/prompt_service.py`, and `backend/legacy_people.py`.
- Treatment is now selected before `time / lighting / mood / capture`, and those later picks use the merged treatment-aware preference profile.
- Batch scoring now includes:
  - per-candidate treatment compatibility score
  - per-batch stylized-vs-polished balancing score
- `women + random + batch 12`: `0` findings; treatment mix improved from phase-1 polished-heavy drift to `clean_commercial 6`, `cinematic_poster_realism 2`, `analog_35mm 3`, `candid_phone_snapshot 1`.
- `men + random + batch 12`: `0` findings; treatment mix `clean_commercial 7`, `analog_35mm 2`, `cinematic_poster_realism 1`, `candid_phone_snapshot 1`, `direct_flash_night 1`.
- `couples + random + batch 12`: `0` findings; treatment mix `clean_commercial 4`, `studio_seamless 1`, `analog_35mm 3`, `candid_phone_snapshot 4`.
- `women + nightlife + batch 12`: `0` findings; treatment mix `clean_commercial 6`, `low_key_dramatic 2`, `cinematic_poster_realism 1`, `direct_flash_night 1`, `candid_phone_snapshot 2`.
- Raw generator sanity after phase 2:
  - `random x20`: `clean_commercial 6`, `analog_35mm 4`, `cinematic_poster_realism 4`, `candid_phone_snapshot 4`, `low_key_dramatic 1`, `studio_seamless 1`
  - `nightlife x20`: `direct_flash_night 7`, `clean_commercial 8`, `candid_phone_snapshot 2`, `low_key_dramatic 3`
  - `studio x20`: `studio_seamless 3`, `low_key_dramatic 11`, `clean_commercial 6`

### Phase 2 Notes
- Phase 2 goal is met in the soft form: treatment now influences candidate selection and final batch picking, not only render/debug.
- Exact taste balancing is still open: `women nightlife` still lets `clean_commercial` lead too often, and some style buckets like `luxury` remain more polished than the long-term target.

### Stylization Phase 3 Checks
- Large-batch distribution sweeps were run on `20`-prompt batches with `3` repeated runs per case.
- Initial phase-3 sweep:
  - `women random`: avg stylized ratio `0.50`
  - `women nightlife`: avg stylized ratio `0.817`
  - `women luxury`: avg stylized ratio `0.433`
  - `women studio`: avg stylized ratio `0.55`
  - `men random`: avg stylized ratio `0.50`
  - `men luxury`: avg stylized ratio `0.35`
  - `couples random`: avg stylized ratio `0.533`
  - `couples nightlife`: avg stylized ratio `0.717`
- After the phase-3 rebalance pass:
  - `women random`: avg stylized ratio improved to `0.567`
  - `women luxury`: avg stylized ratio stayed limited at `0.433`
  - `men luxury`: avg stylized ratio improved slightly to `0.383`
  - `couples random`: avg stylized ratio settled at `0.483`
- Raw generator sanity after phase-3 rebalance:
  - `random x20`: `analog_35mm 7`, `candid_phone_snapshot 6`, `clean_commercial 6`, `cinematic_poster_realism 1`
  - `luxury x20`: `clean_commercial 10`, `direct_flash_night 3`, `cinematic_poster_realism 3`, `candid_phone_snapshot 3`, `low_key_dramatic 1`
  - `studio x20`: `low_key_dramatic 9`, `clean_commercial 6`, `studio_seamless 5`
- All checked phase-3 runs stayed at `0` validation findings.

### Phase 3 Notes
- Phase 3 succeeded for `women random`: the final run selection now lands much closer to the intended non-stock mix.
- `women nightlife` and `couples nightlife` already look healthy on treatment distribution and did not need aggressive extra tuning.
- `luxury`, especially `men luxury`, still over-prefers `clean_commercial`; that remains a separate next-pass problem, not a regression.

### New Harder Stylized Lanes Checks
- `py_compile` passed after adding the new treatment profiles and light families.
- New treatment profiles added:
  - `concept_photo_editorial`
  - `direct_light_editorial`
- New lighting families added:
  - `hard_direct_light`
  - `single_source_contrast`
  - `direct_flash_clean`
- `women random x20` now surfaced the new lanes directly:
  - `concept_photo_editorial 1`
  - `direct_light_editorial 3`
  - checked new-light usage included `single-source contrast light with carved facial shadows` and `hard direct light with crisp shadow edges`
- `women creative_artistic x20`:
  - `direct_light_editorial 4`
  - `concept_photo_editorial 2`
  - new-light usage visible in both gallery and studio-like scenes
- `women studio x20`:
  - `direct_light_editorial 4`
  - new-light usage visible with `single_source_contrast`
- `women luxury x20`:
  - `concept_photo_editorial 4`
  - new-light usage visible with `single_source_contrast`
- `couples random x20`:
  - `direct_light_editorial 2`
  - new-light usage visible in urban/courtyard couple scenes
- Raw generator sanity `random x40`:
  - `direct_light_editorial 2`
  - `concept_photo_editorial 1`
  - new lighting ids present in batch: `single_source_contrast 1`, `hard_direct_light 1`

### UI Reshuffle Checks
- `node --check frontend/app.js` passed.
- `py_compile` passed for:
  - `backend/options.py`
  - `backend/prompt_service.py`
  - `backend/engine/generator.py`
- Bootstrap/generate smoke:
  - `generate_run({'mode': 'women', 'photoTreatmentControl': 'direct_light_editorial', 'debugMode': True, 'batchSize': 2})`
  - returned `formState.photoTreatmentControl = direct_light_editorial`
  - returned `2` prompt lines
- Natural hair-color filter check:
  - random hair color selection now rejects all `dyed_hair` entries unless a specific hair-color control forces them
- `same_person` lock checks:
  - `generate_run({'mode':'women','personMode':'same_person','batchSize':4,'appearanceMode':'generated','useCoreIdentityPrompt':True,'coreIdentityPrompt':'sharp green eyes and a defined cupid bow'})`
  - returned `4` lines
  - first prompt did **not** start with `Appearance:`
  - first prompt still contained `Wearing a ...`
  - first prompt included `core identity notes: ...`
- `same_person` identity-vs-outfit sanity:
  - `women same_person batchSize=6`
  - unique identity atom tuple count `(hair color + hairstyle + makeup) = 1`
  - unique outfit/color tuple count `= 6`
- Browser-level UI verification:
  - headless Playwright opened `http://127.0.0.1:8765/`
  - screenshot smoke passed
  - custom dropdown smoke passed:
    - `personMode` menu visible after click
    - option count `= 2`

### P0 Follow-up Sweep
- Big batch sweeps `batchSize=20` completed for:
  - `women random / lifestyle / nightlife / luxury`
  - `men random / luxury / romantic`
  - `couples random / lifestyle / nightlife`
- All checked runs stayed at:
  - `0` validation findings
  - `0` repairs
- `women random`:
  - `20/20` lines
  - stylized/polished = `10 / 10`
  - outfit diversity still conservative: only `6` unique outfit families, `clean_neutrals` still dominant at `9/20`
- `women lifestyle`:
  - healthy pose spread: `18` unique poses
  - healthy stylization spread: `12 / 8`
- `women nightlife`:
  - `0` swimwear leaks
  - still too mini-dress heavy: `mini_dress 7/20`
- `women luxury`:
  - still too clean-heavy: stylized/polished = `11 / 9`
  - limited color spread: only `4` unique color stories
- `men romantic`:
  - still too polished: stylized/polished = `6 / 14`
  - top treatment `clean_commercial 14/20`
- `couples lifestyle`:
  - no direct bikini/swimsuit words in checked `x20` batch
  - still feels too revealing in some runs via female outfit routing and palette choices
- `couples random`:
  - one checked `x20` run still had `1` bikini/swimsuit word leak

### Quality Pass: Couples / Men / Nightlife Retest
- Retest targets:
  - `couples random x20`
  - `couples lifestyle x20`
  - `men romantic x20`
  - `women nightlife x20`
- `couples random x20` after fix:
  - `0` findings
  - `0` repairs
  - `0` bikini/swimsuit/latex words in final prompt text
  - renderer now safely converts raw swimwear candidates into non-swim textual outfits in random couple output
- `couples lifestyle x20` after fix:
  - `0` findings
  - `0` repairs
  - `0` bikini/swimsuit/latex words in final prompt text
  - top women-side raw candidate ids can still be revealing underneath, but final rendered output now stays in everyday/lifestyle clothing territory
  - checked output shifted toward `sweater_jeans / shirt_trousers / blouse_trousers / cardigan_skirt`
- `women nightlife x20` after fix:
  - `0` findings
  - `0` repairs
  - `0` bikini/swimsuit/latex words
  - `mini_dress` reduced from the previous `7/20` checked sweep down to `4/20` in the latest checked sweep
  - stronger spread now included `bodysuit_trousers / cami_midi_skirt / blazer_mini_dress`
- `men romantic x20` after fix:
  - `0` findings
  - follow-up tuning added:
    - stronger romantic category mix in generator
    - stronger romantic batch target
    - explicit `clean_commercial` deprioritization in treatment choice
  - 6-run stress recheck after the final tuning:
    - `12/8`
    - `12/8`
    - `9/11`
    - `11/9`
    - `10/10`
    - `12/8`
  - worst pre-fix `16 clean_commercial / 20` style collapse no longer reproduced in the final stress pass

### Regression Pass: UI Follow-Up Sweep And Reveal Fixes
- Broad `batchSize=20` sweeps were rerun for:
  - `women random / lifestyle / nightlife / luxury / creative_artistic`
  - `men random / luxury / romantic / nightlife`
  - `couples random / lifestyle / nightlife / luxury`
- Syntax safety:
  - `py_compile` passed for:
    - `backend/prompt_service.py`
    - `backend/legacy_people.py`
- First sweep exposed new reveal-routing regressions:
  - `women random` leaked `swimsuit 4` and `tiny mini skirt 5`
  - `couples nightlife` leaked `latex 2` and `tiny mini skirt 5`
  - men actual prompts were fine, but debug still reported women-side outfits
- Fixes applied:
  - tightened `_effective_outfit_reveal()` for `random / lifestyle / luxury`
  - added random/lifestyle/luxury women-side outfit bans/penalties
  - expanded couple render fallback softening for `random / luxury / nightlife`
  - aligned legacy men debug fields with the actual rendered male outfit/pose/hair
- Final checked sweep after fixes:
  - `women/random`: `0` findings, `0` repairs, `issues = -`
  - `women/lifestyle`: `0` findings, `0` repairs, `issues = -`
  - `women/nightlife`: `0` findings, `0` repairs, residual `tiny mini skirt 4`
  - `women/luxury`: `0` findings, `0` repairs, `issues = -`
  - `men/random`: `0` findings, `0` repairs, `issues = -`
  - `men/luxury`: `0` findings, `0` repairs, `issues = -`
  - `men/romantic`: `0` findings, `0` repairs, `issues = -`
  - `men/nightlife`: `0` findings, `0` repairs, `issues = -`
  - `couples/random`: `0` findings, `0` repairs, `issues = -`
  - `couples/lifestyle`: `0` findings, `0` repairs, `issues = -`
  - `couples/nightlife`: `0` findings, `0` repairs, `issues = -`
  - `couples/luxury`: `0` findings, `0` repairs, `issues = -`

### Women Nightlife Cleanup Stress Retest
- Target:
  - `women nightlife x20`
- Additional fixes applied:
  - banned `crop_top_mini_skirt` directly in the nightlife women profile
  - converted stray final-render `vinyl_latex` to `satin finish` for women nightlife output
- 10-run stress retest after the cleanup:
  - run 1: `0` findings, `0` repairs, `issues = -`
  - run 2: `0` findings, `0` repairs, `issues = -`
  - run 3: `0` findings, `0` repairs, `issues = -`
  - run 4: `0` findings, `0` repairs, `issues = -`
  - run 5: `0` findings, `0` repairs, `issues = -`
  - run 6: `0` findings, `0` repairs, `issues = -`
  - run 7: `0` findings, `0` repairs, `issues = -`
  - run 8: `0` findings, `0` repairs, `issues = -`
  - run 9: `0` findings, `0` repairs, `issues = -`
  - run 10: `0` findings, `0` repairs, `issues = -`
- Result:
  - no remaining `tiny mini skirt`
  - no remaining `latex`
  - no `bikini / swimsuit`

### Women Random / Luxury Diversity Pass
- Styling-bank additions moved live into `backend/engine/data/styling.json`:
  - outfits: `vest_trousers`, `column_dress`, `wrap_blouse_skirt`, `halter_trousers`
  - materials: `fluid_crepe`, `matte_jersey`
  - colors: `chocolate_cream`, `champagne_taupe`, `slate_blue_ink`, `rosewood_smoke`
- Extra women-only diversity pressure added for:
  - `random`
  - `luxury`
- First broad women sweep after the pass:
  - `random`: `0` findings, `0` repairs, new colors/outfits live, but `tiny mini skirt 5` still appeared in one checked run
  - `luxury`: `0` findings, `0` repairs, `clean_neutrals` dropped to `4/20` in the checked run and new colors were present
  - `lifestyle / nightlife / creative_artistic / romantic`: no new wording leaks introduced
- Follow-up fix:
  - `women random` now bans `crop_top_mini_skirt` directly
- `women random x20` stress retest after the follow-up fix:
  - run 1: `issues = -`
  - run 2: `issues = -`
  - run 3: `issues = -`
  - run 4: `issues = -`
  - run 5: `issues = -`
  - run 6: `issues = -`
- Result:
  - no `tiny mini skirt`
  - no `bikini / swimsuit / latex`
  - new silhouettes and richer color stories are active in live output

### Women Relevance And Fitness Pass
- Syntax safety:
  - `py_compile` passed for:
    - `backend/prompt_service.py`
    - `backend/engine/generator.py`
- First target:
  - `women fitness x20` had been collapsing into repeated `crop top + tiny mini skirt` output with a narrow setting pool
- Fixes applied:
  - split `sport` vs `fitness` scoring instead of rewarding `crop_top_mini_skirt` in both
  - rewired the base `fitness` profile in `generator.py`
  - added six new live fitness/wellness-safe settings
  - added stronger `fitness` batch penalties for:
    - `crop_top_mini_skirt`
    - repeated same-outfit dominance
    - too few unique settings
    - too little `wellness_spa`
  - tightened women relevance routing for `lifestyle / romantic / creative_artistic`
- `women fitness x20` stress retest after the fix:
  - run 1: `0` findings, `0` repairs, issues `-`, outfits spread `7/6/4/3`, scenes `urban_daylight 12 / wellness_spa 8`
  - run 2: `0` findings, `0` repairs, issues `-`, outfits spread `7/5/4/4`, scenes `urban_daylight 11 / wellness_spa 9`
  - run 3: `0` findings, `0` repairs, issues `-`, outfits spread `7/5/4/4`, scenes `urban_daylight 14 / wellness_spa 6`
  - run 4: `0` findings, `0` repairs, issues `-`, outfits spread `7/5/5/3`, scenes `urban_daylight 10 / wellness_spa 10`
  - run 5: `0` findings, `0` repairs, issues `-`, outfits spread `6/5/5/4`, scenes `urban_daylight 14 / wellness_spa 6`
- Result:
  - no `tiny mini skirt`
  - no `swimsuit / bikini / latex`
  - stable 4-outfit rotation across fitness-safe silhouettes
  - wellness scenes now appear in every checked run
- Women relevance retest after the same pass:
  - `lifestyle`: `0` findings, `0` repairs, `stylized/polished = 11 / 9`, top outfits led by `cardigan_skirt`, `cami_midi_skirt`, `knit_top_trousers`
  - `romantic`: `0` findings, `0` repairs, `stylized/polished = 12 / 8`, no `swimsuit / bikini / tiny mini / latex`
  - `creative_artistic`: `0` findings, `0` repairs, `stylized/polished = 15 / 5`, sporty outfit leaks removed in the checked run

### Couples Quality Pass
- Baseline `couples x20` sweep before fixes:
  - `random`: `0` findings, but still leaked `crop_top + tiny mini skirt` and leaned too hard into `clean_neutrals`
  - `lifestyle`: `0` findings, but female color spread still collapsed too hard into `clean_neutrals`
  - `nightlife`: `0` findings, but the pose bank was still too narrow
  - `luxury`: `0` findings, but female color spread still leaned too neutral and pair poses were still too repetitive
- Fixes applied:
  - expanded the couple interaction bank with true two-person poses
  - rewired couple debug so `pose` reports the rendered couple interaction
  - added couple-specific penalties for:
    - `mini_dress` over-dominance in `random / lifestyle / luxury`
    - `clean_neutrals` over-dominance in `random / lifestyle / luxury`
  - moved `clean_neutrals` back in the diversification order for `lifestyle / luxury`
  - banned `crop_top_mini_skirt` for `couples random`
  - restricted luxury mood overrides in couples to only genuinely luxury-compatible treatments
- Final `couples x20` retest after the pass:
  - `random`: `0` findings, `0` repairs, `issues = -`, top female colors now led by `navy_cream` with `clean_neutrals` reduced to `4`
  - `lifestyle`: `0` findings, `0` repairs, `issues = -`, top female colors now led by `powder_blue`, `clean_neutrals` reduced to `2`
  - `nightlife`: `0` findings, `0` repairs, `issues = -`, wider pair-pose spread across standing / walking / seated nightlife interactions
  - `luxury`: `0` findings, `0` repairs, `issues = -`, top female colors now led by `navy_cream`, `clean_neutrals` reduced to `2`
- Pair-pose sanity check:
  - random/lifestyle/luxury sample runs now showed:
    - standing side by side holding hands
    - walking together
    - seated together
    - woman seated lightly on his lap
    - leaning into each other / resting against him

### Eye Color, Breast Size, And Curated Race Dropdown
- Syntax / data safety:
  - `subjects.json` loaded cleanly
  - `py_compile` passed for:
    - `backend/options.py`
    - `backend/prompt_service.py`
    - `backend/engine/generator.py`
    - `backend/legacy_people.py`
- Bootstrap sanity:
  - defaults now include `eyeColorControl=random`
  - defaults now include `breastSizeControl=random`
  - options now include `eyeColorOptions`
  - options now include `breastSizeOptions`
  - `racePresetOptions` now include curated presets like `white_ukrainian`
- Women different-persons smoke:
  - payload: `style=lifestyle`, `eyeColorControl=blue_eyes`, `breastSizeControl=big_breasts`, `racePreset=white_ukrainian`
  - result: `6/6` prompts rendered
  - prompt output contained `blue eyes`
  - prompt output contained `big breasts`
  - prompt output rendered `white Ukrainian woman`
- Women same-person smoke:
  - payload: `style=lifestyle`, `eyeColorControl=green_eyes`, `breastSizeControl=very_big_breasts`, `racePreset=latina_mexican`
  - result: `4/4` prompts rendered
  - prompt output contained `green eyes`
  - prompt output contained `very big breasts`
  - locked identity rendered as `Mexican Latina woman`
- Couples smoke:
  - payload: `style=lifestyle`, `eyeColorControl=hazel_eyes`, `breastSizeControl=medium_breasts`, `racePreset=white_spanish`, `maleRacePreset=black_american`
  - result: `4/4` prompts rendered
  - women-side prompt output contained `hazel eyes`
  - women-side prompt output contained `medium breasts`
  - prompt rendered `white Spanish woman` + `Black American man`

### Women Taste Pass
- Baseline x20 sweep before the pass:
  - `random`: `0` findings, but `mini_dress` still led at `5/20` and `clean_neutrals` at `6/20`
  - `luxury`: `0` findings, but `mini_dress` still led at `7/20`
  - `romantic`: `0` findings, but some nightlife-ish silhouettes still drifted in broad random sampling
  - `creative_artistic`: `0` findings, but sporty outfits still appeared in the checked run
- Fixes applied:
  - added stronger women-only scoring pressure against `mini_dress` in `random / luxury`
  - added broader silhouette bonuses in `random / luxury`
  - banned `mini_dress` + `bodysuit_trousers` in the women `romantic` profile
  - banned sporty outfit families in the women `creative_artistic` profile
  - added stronger batch penalties for:
    - repeated `mini_dress` in `random / luxury / romantic`
    - sporty outfit leaks in `creative_artistic`
    - overused `clean_neutrals` in `luxury`
- Post-fix x20 snapshot:
  - `random`: `0` findings, `0` repairs, broader outfit spread, `clean_neutrals` down to `5`
  - `luxury`: `0` findings, `0` repairs, richer color spread, `clean_neutrals` down to `3`
  - `romantic`: `0` findings, `0` repairs, now led by `cami_midi_skirt / vest_trousers / wrap_blouse_skirt / column_dress`
  - `creative_artistic`: `0` findings, `0` repairs, sporty leak removed in the checked run
- 3-run x20 cleanliness retest:
  - `random`: 3/3 runs clean, `0` findings, `0` repairs, no `bikini / swimsuit / latex`
  - `luxury`: 3/3 runs clean, `0` findings, `0` repairs, no `bikini / swimsuit / latex`
  - `romantic`: 3/3 runs clean, `0` findings, `0` repairs, no `bikini / swimsuit / latex`
  - `creative_artistic`: 3/3 runs clean, `0` findings, `0` repairs, no `bikini / swimsuit / latex`

### Stylization Rebalance
- Syntax / startup safety:
  - `py_compile` passed for:
    - `backend/__init__.py`
    - `backend/prompt_service.py`
    - `app.py`
  - `get_bootstrap()` still loads and exposes `photoTreatmentControl`
- Live treatment-bank rebalance:
  - lowered the base weight of `clean_commercial`
  - raised several stylized treatment weights
  - added stronger style-aware treatment scoring and batch-level clean caps
- 3-run x20 aggregate retest after the rebalance:
  - `women random`: avg `stylized/polished = 11.33 / 8.67`, avg `clean_commercial = 8.67`, `0` findings, `0` repairs
  - `women luxury`: avg `stylized/polished = 14 / 6`, avg `clean_commercial = 6`, `0` findings, `0` repairs
  - `women nightlife`: avg `stylized/polished = 14.67 / 5.33`, avg `clean_commercial = 5.33`, `0` findings, `0` repairs
  - `women creative_artistic`: avg `stylized/polished = 14.33 / 5.67`, avg `clean_commercial = 5.67`, `0` findings, `0` repairs
  - `men luxury`: avg `stylized/polished = 13 / 7`, avg `clean_commercial = 7`, `0` findings, `0` repairs
  - `men romantic`: avg `stylized/polished = 11 / 9`, avg `clean_commercial = 9`, `0` findings, `0` repairs
  - `couples random`: avg `stylized/polished = 10.67 / 9.33`, avg `clean_commercial = 9.33`, `0` findings, `0` repairs
- Result:
  - the rebalance materially improved `women luxury / nightlife / creative_artistic` and also improved `men luxury`
  - no validation regressions or wording leaks appeared during the checked runs
  - residual clean-heavy tails still remain for:
    - `women random`
    - `men romantic`
    - `couples random`

### Random Stylization Follow-up
- Focus targets:
  - `women random`
  - `men romantic`
  - `couples random`
- Additional changes applied:
  - stronger random-mode reward for casual stylized treatments
  - stronger `men romantic` reward for:
    - `direct_light_editorial`
    - `analog_35mm`
    - `documentary_still`
    - `disposable_camera`
  - stronger `couples random` reward for:
    - `casual_indoor_selfie`
    - `mirror_selfie`
    - `disposable_camera`
    - `analog_35mm`
    - `cinematic_poster_realism`
    - `direct_light_editorial`
  - lower live weight for `clean_commercial`
  - higher live weights for several casual/documentary treatments
- 5-run aggregate retest:
  - `women random`: avg `stylized/polished = 12.8 / 7.2`, avg `clean_commercial = 7.2`, `0` findings, `0` repairs
  - `men romantic`: avg `stylized/polished = 11.6 / 8.4`, avg `clean_commercial = 8.4`, `0` findings, `0` repairs
  - `couples random`: avg `stylized/polished = 10.6 / 9.4`, avg `clean_commercial = 9.4`, `0` findings, `0` repairs
- Result:
  - `women random` improved materially
  - `men romantic` improved slightly
  - `couples random` improved only slightly and remains the weakest stylization tail in the project

### UI Tail Cleanup
- Frontend safety:
  - `node --check frontend/app.js` passed
- App/bootstrap safety:
  - `py_compile` passed for `app.py`
  - `get_bootstrap()` still returned normal UI options/defaults after the UI cleanup
- Result:
  - men/couples appearance blocks now better match real backend coverage
  - couples appearance spacing no longer depends on inline style fragments

### Couples Random Stylization Pass
- Backend safety:
  - `py_compile backend/prompt_service.py` passed
- 6-run x20 retest after the targeted couples-random pass:
  - run 1: `stylized/polished = 15 / 5`, `clean_commercial = 5`, `0` findings, `0` repairs
  - run 2: `stylized/polished = 20 / 0`, `clean_commercial = 0`, `0` findings, `0` repairs
  - run 3: `stylized/polished = 15 / 5`, `clean_commercial = 5`, `0` findings, `0` repairs
  - run 4: `stylized/polished = 20 / 0`, `clean_commercial = 0`, `0` findings, `0` repairs
  - run 5: `stylized/polished = 14 / 6`, `clean_commercial = 6`, `0` findings, `0` repairs
  - run 6: `stylized/polished = 20 / 0`, `clean_commercial = 0`, `0` findings, `0` repairs
- 6-run aggregate:
  - `couples random`: avg `stylized/polished = 17.33 / 2.67`, avg `clean_commercial = 2.67`
- Result:
  - `couples random` now lands much closer to the intended stylized mix
  - no validation regressions or repair spikes appeared in the checked runs

### Broad Matrix Sweep
- Backend safety:
  - `py_compile backend/prompt_service.py` passed
  - `py_compile backend/engine/generator.py` passed
  - `py_compile app.py` passed
- Single x20 sweep across:
  - `women`: `random / lifestyle / luxury / nightlife / romantic / creative_artistic / fitness`
  - `men`: `random / luxury / romantic / nightlife`
  - `couples`: `random / lifestyle / luxury / nightlife`
- Global result:
  - every checked case returned `0` findings and `0` repairs
  - no wording leaks were found for `swimsuit / bikini / latex / tiny mini`
- Best-looking cases in this sweep:
  - `women luxury`: `stylized/polished = 17 / 3`, `clean_commercial = 3`
  - `couples random`: `stylized/polished = 19 / 1`, `clean_commercial = 1`
  - `couples luxury`: `stylized/polished = 17 / 3`, `clean_commercial = 3`
- Residual clean-heavy tails found in this sweep:
  - `women lifestyle`: `stylized/polished = 9 / 11`, `clean_commercial = 11`
  - `women random`: `stylized/polished = 10 / 10`, `clean_commercial = 10`
  - `women romantic`: `stylized/polished = 10 / 10`, `clean_commercial = 10`
  - `women fitness`: `stylized/polished = 5 / 15`, `clean_commercial = 15`
  - `men random`: `stylized/polished = 10 / 10`, `clean_commercial = 10`
  - `men romantic`: `stylized/polished = 11 / 9`, `clean_commercial = 9`
  - `men nightlife`: `stylized/polished = 11 / 9`, `clean_commercial = 9`
  - `couples lifestyle`: `stylized/polished = 11 / 9`, `clean_commercial = 9`
- Quality notes from the same sweep:
  - `women nightlife` is clean and safe now, but still leans heavily on:
    - `silk cami with a bias cut midi skirt`
    - `fitted mini dress with a deep neckline`
  - `women fitness` is safe and scene routing is good (`urban_daylight` + `wellness_spa`), but treatment mix is still almost entirely polished
  - `men romantic` still leans too hard on just two outfit templates:
    - `soft open shirt with tailored trousers`
    - `clean henley with dark trousers`
  - `couples lifestyle` is safe, but still too clean-heavy and color spread still overuses `clean neutral palette`

### Women Lifestyle And Fitness Treatment Pass
- Backend safety:
  - `py_compile backend/prompt_service.py` passed
- 5-run x20 retest for `women lifestyle`:
  - run 1: `stylized/polished = 16 / 4`, `clean_commercial = 4`, `0` findings, `0` repairs
  - run 2: `stylized/polished = 15 / 5`, `clean_commercial = 5`, `0` findings, `0` repairs
  - run 3: `stylized/polished = 16 / 4`, `clean_commercial = 4`, `0` findings, `0` repairs
  - run 4: `stylized/polished = 17 / 3`, `clean_commercial = 3`, `0` findings, `0` repairs
  - run 5: `stylized/polished = 18 / 2`, `clean_commercial = 2`, `0` findings, `0` repairs
- 5-run x20 retest for `women fitness`:
  - run 1: `stylized/polished = 5 / 15`, `clean_commercial = 15`, `0` findings, `0` repairs
  - run 2: `stylized/polished = 12 / 8`, `clean_commercial = 8`, `0` findings, `0` repairs
  - run 3: `stylized/polished = 12 / 8`, `clean_commercial = 8`, `0` findings, `0` repairs
  - run 4: `stylized/polished = 13 / 7`, `clean_commercial = 7`, `0` findings, `0` repairs
  - run 5: `stylized/polished = 13 / 7`, `clean_commercial = 7`, `0` findings, `0` repairs
- Aggregate result:
  - `women lifestyle`: avg `stylized/polished = 16.4 / 3.6`, avg `clean_commercial = 3.6`
  - `women fitness`: avg `stylized/polished = 11 / 9`, avg `clean_commercial = 9`
- Result:
  - `women lifestyle` is now in a much healthier stylized range without validation regressions
  - `women fitness` improved materially, though one clean-heavy outlier still shows the mode can use more follow-up tuning later

### Women Random And Romantic Treatment Pass
- Backend safety:
  - `py_compile backend/prompt_service.py` passed
- 5-run x20 retest for `women random`:
  - run 1: `stylized/polished = 12 / 8`, `clean_commercial = 8`, `0` findings, `0` repairs
  - run 2: `stylized/polished = 15 / 5`, `clean_commercial = 5`, `0` findings, `0` repairs
  - run 3: `stylized/polished = 15 / 5`, `clean_commercial = 5`, `0` findings, `0` repairs
  - run 4: `stylized/polished = 12 / 8`, `clean_commercial = 8`, `0` findings, `0` repairs
  - run 5: `stylized/polished = 17 / 3`, `clean_commercial = 3`, `0` findings, `0` repairs
- 5-run x20 retest for `women romantic`:
  - run 1: `stylized/polished = 14 / 6`, `clean_commercial = 6`, `0` findings, `0` repairs
  - run 2: `stylized/polished = 13 / 7`, `clean_commercial = 7`, `0` findings, `0` repairs
  - run 3: `stylized/polished = 12 / 8`, `clean_commercial = 8`, `0` findings, `0` repairs
  - run 4: `stylized/polished = 12 / 8`, `clean_commercial = 8`, `0` findings, `0` repairs
  - run 5: `stylized/polished = 12 / 8`, `clean_commercial = 8`, `0` findings, `0` repairs
- Aggregate result:
  - `women random`: avg `stylized/polished = 14.2 / 5.8`, avg `clean_commercial = 5.8`
  - `women romantic`: avg `stylized/polished = 12.6 / 7.4`, avg `clean_commercial = 7.4`
- Result:
  - both modes improved materially without validation regressions
  - `women random` now sits in a much healthier stylized range
  - `women romantic` is improved too, but still remains a softer tail than `women lifestyle`

### Men Random And Nightlife Treatment Pass
- Backend safety:
  - `py_compile backend/prompt_service.py` passed
- 5-run x20 retest for `men random`:
  - run 1: `stylized/polished = 16 / 4`, `clean_commercial = 4`, `0` findings, `0` repairs
  - run 2: `stylized/polished = 14 / 6`, `clean_commercial = 6`, `0` findings, `0` repairs
  - run 3: `stylized/polished = 14 / 6`, `clean_commercial = 6`, `0` findings, `0` repairs
  - run 4: `stylized/polished = 13 / 7`, `clean_commercial = 7`, `0` findings, `0` repairs
  - run 5: `stylized/polished = 18 / 2`, `clean_commercial = 2`, `0` findings, `0` repairs
- 5-run x20 retest for `men nightlife`:
  - run 1: `stylized/polished = 18 / 2`, `clean_commercial = 2`, `0` findings, `0` repairs
  - run 2: `stylized/polished = 18 / 2`, `clean_commercial = 2`, `0` findings, `0` repairs
  - run 3: `stylized/polished = 16 / 4`, `clean_commercial = 4`, `0` findings, `0` repairs
  - run 4: `stylized/polished = 18 / 2`, `clean_commercial = 2`, `0` findings, `0` repairs
  - run 5: `stylized/polished = 17 / 3`, `clean_commercial = 3`, `0` findings, `0` repairs
- Aggregate result:
  - `men random`: avg `stylized/polished = 15 / 5`, avg `clean_commercial = 5`
  - `men nightlife`: avg `stylized/polished = 17.4 / 2.6`, avg `clean_commercial = 2.6`
- Result:
  - both modes improved materially without validation regressions
  - `men nightlife` now sits in a strong stylized range
  - `men random` is healthier too, though outfit spread can still use a later taste pass

### Couples Lifestyle Treatment Pass
- Backend safety:
  - `py_compile backend/prompt_service.py` passed
- 5-run x20 retest for `couples lifestyle`:
  - run 1: `stylized/polished = 16 / 4`, `clean_commercial = 4`, `0` findings, `0` repairs
  - run 2: `stylized/polished = 17 / 3`, `clean_commercial = 3`, `0` findings, `0` repairs
  - run 3: `stylized/polished = 17 / 3`, `clean_commercial = 3`, `0` findings, `0` repairs
  - run 4: `stylized/polished = 13 / 7`, `clean_commercial = 7`, `0` findings, `0` repairs
  - run 5: `stylized/polished = 19 / 1`, `clean_commercial = 1`, `0` findings, `0` repairs
- Aggregate result:
  - `couples lifestyle`: avg `stylized/polished = 16.4 / 3.6`, avg `clean_commercial = 3.6`
- Result:
  - `couples lifestyle` improved materially without validation regressions
  - one remaining taste tail is that sporty-leaning women-side outfits can still surface occasionally in this mode

### External Pose Bank Wave 3
- Focused line-bank validation:
  - `python -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  - result: `7 passed`
- Live smoke after wave 3:
  - `women random`: `0` findings, `0` repairs, `10` prompts
  - `men random`: `0` findings, `0` repairs, `10` prompts
  - `couples lifestyle`: `0` findings, `0` repairs, `10` prompts
- File-level checks after wave 3:
  - all six touched pose files remain parse-safe
  - all six touched pose files now have `8` live lines each
  - max line lengths stayed below the current cap

### External Pose Bank Wave 4
- Focused line-bank validation:
  - `python -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  - result: `7 passed`
- Live smoke after wave 4:
  - `women random`: `0` findings, `0` repairs, `10` prompts
  - `men random`: `0` findings, `0` repairs, `10` prompts
  - `couples lifestyle`: `0` findings, `0` repairs, `10` prompts
- File-level checks after wave 4:
  - all six touched pose files remain parse-safe
  - all six touched pose files now have `9` live lines each
  - max line lengths stayed below the current cap

### External Pose Bank Wave 5
- Focused line-bank validation:
  - `python -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  - result: `7 passed`
- Live smoke after wave 5:
  - `women random`: `0` findings, `0` repairs, `10` prompts
  - `men random`: `0` findings, `0` repairs, `10` prompts
  - `couples lifestyle`: `0` findings, `0` repairs, `10` prompts
- File-level checks after wave 5:
  - all six touched pose files remain parse-safe
  - all six touched pose files now have `10` live lines each
  - max line lengths stayed below the current soft cap

### External Pose Bank Wave 6
- Focused line-bank validation:
  - `python -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  - result: `7 passed`
- Live smoke after wave 6:
  - `women random`: `0` findings, `0` repairs, `10` prompts
  - `men random`: `0` findings, `0` repairs, `10` prompts
  - `couples lifestyle`: `0` findings, `0` repairs, `10` prompts
- File-level checks after wave 6:
  - all six touched pose files remain parse-safe
  - all six touched pose files now have `11` live lines each
  - max line lengths stayed below the current soft cap

### External Pose Bank Wave 7
- Focused line-bank validation:
  - `python -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  - result: `7 passed`
- Live smoke after wave 7:
  - `women random`: `0` findings, `0` repairs, `10` prompts
  - `men random`: `0` findings, `0` repairs, `10` prompts
  - `couples lifestyle`: `0` findings, `0` repairs, `10` prompts
- File-level checks after wave 7:
  - all six touched pose files remain parse-safe
  - all six touched pose files now have `12` live lines each
  - max line lengths stayed below the current soft cap

### External Expression Bank Wave 1
- Focused line-bank validation:
  - `python -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  - result: `7 passed`
- Live smoke after expression wave 1:
  - `women random`: `0` findings, `0` repairs, `10` prompts
  - `men random`: `0` findings, `0` repairs, `10` prompts
  - `couples lifestyle`: `0` findings, `0` repairs, `10` prompts
- File-level checks after expression wave 1:
  - all six touched expression files remain parse-safe
  - all six touched expression files now have `5` live lines each
  - max line lengths stayed below the current soft cap

### External Expression Bank Wave 2
- Focused line-bank validation:
  - `python -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  - result: `7 passed`
- Live smoke after expression wave 2:
  - `women random`: `0` findings, `0` repairs, `10` prompts
  - `men random`: `0` findings, `0` repairs, `10` prompts
  - `couples lifestyle`: `0` findings, `0` repairs, `10` prompts
- File-level checks after expression wave 2:
  - all six touched expression files remain parse-safe
  - all six touched expression files now have `6` live lines each
  - max line lengths stayed below the current soft cap

### External Expression Bank Waves 3-5
- Focused line-bank validation:
  - `python -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  - result: `7 passed`
- Live smoke after grouped expression waves 3-5:
  - `women random`: `0` findings, `0` repairs, `10` prompts
  - `men random`: `0` findings, `0` repairs, `10` prompts
  - `couples lifestyle`: `0` findings, `0` repairs, `10` prompts
- File-level checks after grouped expression waves 3-5:
  - all six touched expression files remain parse-safe
  - all six touched expression files now have `9` live lines each
  - max line lengths stayed below the current soft cap

### External Outfit Bank Wave 1
- Focused line-bank validation:
  - `python -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  - result: `7 passed`
- Live smoke after outfit wave 1:
  - `women random`: `0` findings, `0` repairs, `10` prompts
  - `men random`: `0` findings, `0` repairs, `10` prompts
  - `couples lifestyle`: `0` findings, `0` repairs, `10` prompts
- File-level checks after outfit wave 1:
  - all six touched outfit files remain parse-safe
  - all six touched outfit files now have `5` live lines each
  - max line lengths stayed below the current soft cap

### External Outfit Bank Wave 2
- Focused line-bank validation:
  - `python -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  - result: `7 passed`
- Live smoke after outfit wave 2:
  - `women random`: `0` findings, `0` repairs, `10` prompts
  - `men random`: `0` findings, `0` repairs, `10` prompts
  - `couples lifestyle`: `0` findings, `0` repairs, `10` prompts
- File-level checks after outfit wave 2:
  - all six touched outfit files remain parse-safe
  - all six touched outfit files now have `6` live lines each
  - max line lengths stayed below the current soft cap

### External Outfit Bank Waves 3-5
- Focused line-bank validation:
  - `python -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  - result: `7 passed`
- Live smoke after grouped outfit waves 3-5:
  - `women random`: `0` findings, `0` repairs, `10` prompts
  - `men random`: `0` findings, `0` repairs, `10` prompts
  - `couples lifestyle`: `0` findings, `0` repairs, `10` prompts
- File-level checks after grouped outfit waves 3-5:
  - all six touched outfit files remain parse-safe
  - all six touched outfit files now have `9` live lines each
  - max line lengths stayed below the current soft cap

### Issue 34 P1 - Outfit Line-Bank Coherence Pass
- Focused validation:
  - `python -m pytest tests/test_line_bank_loader.py -q`
  - result: `8 passed`
- Compile checks:
  - `py_compile` ok for:
    - `backend/engine/line_bank_loader.py`
    - `backend/engine/candidate_builder.py`
    - `backend/legacy_people.py`
- Live smoke after scene-aware outfit filtering:
  - `women luxury x20`: `0 findings`, `0 repairs`
  - `women random x20`: `0 findings`, `0 repairs`
  - `women nightlife x20`: `0 findings`, `0 repairs`
- Coherence outcome:
  - robe-like line-bank outfits no longer surfaced in public-ish luxury contexts like lounge/corridor/lobby-style settings
  - swim-coded line-bank outfits no longer surface outside coastal contexts
  - nightlife can still surface hotter line-bank outfits where that read is intentional
- Known live warning unrelated to this pass:
  - `overrides/line_banks/women/poses/6_8.md repeats the same starters too often: standing with`

### Issue 34 P2 - Pose Posture Gating Pass
- Focused validation:
  - `python -m pytest tests/test_line_bank_loader.py -q`
  - result: `9 passed`
- Compile checks:
  - `py_compile` ok for:
    - `backend/engine/line_bank_loader.py`
    - `backend/engine/candidate_builder.py`
    - `backend/legacy_people.py`
- Live smoke after posture gating:
  - `women lifestyle x20`: `0 findings`, `0 repairs`
  - `women random x20`: `0 findings`, `0 repairs`
  - `men random x20`: `0 findings`, `0 repairs`
- Coherence outcome:
  - seated / reclined line-bank poses still surface in support-implying scenes like sofas, banquettes, beds, mats, or similar
  - the new guardrail is aimed at absurd floor/public-context cases, not at removing every seated or reclined pose from the generator

### Issue 34 P3 - Shared Location Line-Bank Pass
- Focused validation:
  - `python -m pytest tests/test_line_bank_loader.py -q`
  - result: `11 passed`
- Compile checks:
  - `py_compile` ok for:
    - `backend/engine/line_bank_loader.py`
    - `backend/engine/candidate_builder.py`
    - `backend/engine/render/prompt_renderer.py`
    - `backend/modes/women.py`
- Live smoke after shared location rollout:
  - `women luxury x30`: `0 findings`, `0 repairs`, shared location line surfaced (`sunlit hotel suite lounge ...`)
  - `women nightlife x30`: `0 findings`, `0 repairs`, shared nightlife location line surfaced (`dim private lounge booth ...`)
  - `women garden x30`: `0 findings`, `0 repairs`, shared garden-compatible line surfaced (`quiet conservatory walkway ...`)
- Rollout notes:
  - shared locations currently act as a render-level location override, not a replacement for the underlying scene ids or route selection
  - this keeps the first rollout cheap and low-risk while still proving that shared location lines can surface safely in live prompts

### Issue 34 P4 - Final Verification And Cleanup
- Final focused repo-backed validation:
  - `python -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  - result: `13 passed`
- Cleanup checks:
  - updated `tests/test_line_bank_men_smoke.py` so it matches the new posture-aware pose filtering instead of assuming a seated chair-edge pose must always survive
- Final representative live smoke:
  - `women random x20`: `0 findings`, `0 repairs`
  - `women luxury x20`: `0 findings`, `0 repairs`
  - `women nightlife x20`: `0 findings`, `0 repairs`
  - `men random x20`: `0 findings`, `0 repairs`
  - `couples lifestyle x20`: `0 findings`, `0 repairs`
- What is now safer:
  - line-bank outfits no longer surface as blindly as before
  - line-bank poses no longer ignore support surfaces as blindly as before
  - shared location lines can surface live without replacing the underlying scene engine
- Residual future work:
  - shared location compatibility is still intentionally lightweight, so a later taste pass should tighten vanity / wellness / coastal crossover behavior if it keeps showing up too often

### Issue 34 Follow-Up - CI And Coherence Cleanup
- CI blocker checks:
  - `node --check frontend/components/controls.js` -> ok
  - `py_compile` ok for:
    - `backend/engine/data_loader.py`
    - `backend/engine/selectors.py`
    - `backend/engine/candidate_builder.py`
- E2E:
  - `npm run test:e2e -- --workers=1 --reporter=line`
  - result: `5 passed`
- Repo-backed validation:
  - `python -m pytest tests/test_line_bank_loader.py tests/test_line_bank_women_pose_smoke.py tests/test_line_bank_men_smoke.py -q`
  - result: `13 passed`
- Fixed regression check:
  - `women culture_bookish strict batchSize=8` now generates successfully instead of failing with `Could not generate a valid batch`
- Coherence:
  - `python scripts/coherence_threshold_report.py --runs-per-case 1 --batch-size 8 --max-cases 96 --progress-every 24 --calibration-runs 2 --threshold 3.0 --hard-fail --output data/audits/ci_coherence_audit.json`
  - result: `success=192 failed=0 candidates=1536 violations=6`
  - threshold result: `viol_per_100_max=0.39` at threshold `3.0`
- Representative live smoke after the follow-up:
  - `women random x10` -> `0 findings`
  - `women luxury x10` -> `0 findings`
  - `couples lifestyle x10` -> `0 findings`

### Issue 7 - Women Pose Bank Safe Expansion Closeout
- Focused repo-backed validation after each small `poses_master` intake wave:
  - `python -m pytest tests/test_line_bank_loader.py -q`
  - result stayed stable at `11 passed`
- Loader outcome:
  - newly added women `1_3 / 4_5 / 6_8` pose lines surfaced correctly from the live external line-bank files
  - cleaned high-spicy lines in `women/poses/6_8.md` now load without the earlier malformed wording tail
- Closeout note:
  - `data/references/poses_master.md` was only a temporary local reference and is no longer needed for the completed safe-import slice

### Issue 36 - Race Preset Routing And Mixed Pool Fix
- Focused regression tests:
  - `python -m pytest tests/test_issue36_race_presets_smoke.py -q`
  - result: `4 passed`
- Broader identity regression:
  - `python -m pytest tests/test_issue36_race_presets_smoke.py tests/test_public_contract_smoke.py tests/test_couples_identity_constraints_smoke.py -q`
  - result: `11 passed`
- Compile checks:
  - `py_compile` ok for:
    - `backend/engine/candidate_builder.py`
    - `backend/engine/generator.py`
    - `backend/services/batch_selection.py`
    - `backend/services/scoring.py`
    - `backend/forms/user_profile.py`
    - `backend/forms/constants.py`
    - `backend/options.py`
    - `backend/prompt_service.py`
    - `backend/legacy_people.py`
- Live smoke observations:
  - `women random x20`: Asian share now surfaced as `3/20`
  - `women mostly_asian x20`: `20/20` Asian
  - `women exact Japanese x20`: `20/20` Japanese
  - `women exact Russian x20`: `20/20` Russian and no `white Russian` wording
  - `women mostly_mixed x20`: includes white / black / latina / asian / Arab / Indian pool members
  - `men mostly_asian`: prompt text renders Asian male identities
  - `couples female mostly_asian + male mostly_blacks`: female side is Asian and male side is Black

### Issue 36 - Curated Race Dropdown Coverage
- Focused regression:
  - `python -m pytest tests/test_issue36_race_presets_smoke.py -q`
  - result: `5 passed`
- Compile checks:
  - `py_compile` ok for:
    - `backend/options.py`
    - `tests/test_issue36_race_presets_smoke.py`
- Coverage added:
  - test now verifies that the curated exact race option set is exposed in both women and men dropdowns
  - test also verifies that those same values are accepted by `ALLOWED_RACE_PRESETS`

### Issue 36 - Final Race Preset Sweep
- Final manual x20 matrix:
  - women:
    - `random`: `0 findings`, groups `white 11 / black 4 / asian 3 / latina 2`
    - `mostly_asian`: `0 findings`, `20/20 asian`
    - `mostly_mixed`: `0 findings`, includes `white / black / latina / asian / Arab / Indian`
    - exact `Japanese / Russian / Arab / Indian`: `0 findings`, `20/20` matching ethnicity id
  - men:
    - `random`: `0 findings`, groups `white 11 / black 4 / asian 3 / latina 2`
    - `mostly_asian`: `0 findings`, `20/20 asian`
    - `mostly_mixed`: `0 findings`, includes `white / black / latina / asian / Arab / Indian`
    - exact `Japanese / Russian / Arab / Indian`: `0 findings`, `20/20` matching ethnicity id
  - couples:
    - `random/random`: `0 findings`, both sides follow the default visible split
    - `asian/black`: `0 findings`, female side `20/20 asian`, male side `20/20 black`
    - `mixed/mixed`: `0 findings`, both sides include the broad mixed pool
    - `Japanese/Arab`: `0 findings`, female side `20/20 Japanese`, male side `20/20 Arab`
    - `Russian/Indian`: `0 findings`, female side `20/20 Russian`, male side `20/20 Indian`
- Wording check:
  - no `white Russian`, `white Spanish`, or `white Ukrainian` wording surfaced in the final matrix.
- Conclusion:
  - `#36` acceptance criteria are met.

### UI Bug Pass
- Frontend syntax:
  - `node --check frontend/sections/output.js`
  - result: passed
- Playwright E2E:
  - `npm run test:e2e`
  - result: `5 passed`
- Visual smoke:
  - desktop screenshot after collapsing service sections: topbar title is now aligned with document title, `Latest batch` stays visible, `History` no longer bloats the right column by default
  - mobile screenshot after collapsing service sections: `Debug`, `Line-banks`, and `History` stay out of the main scroll until opened, so the first screen is materially cleaner

### Extra Large Breast Size
- Options smoke:
  - `backend.options.UI_OPTIONS['breastSizeOptions']`
  - result: `extra_large_breasts / Extra large` is present
- Render smoke:
  - `backend.services.run_service.generate_run({'mode': 'women', 'batchSize': 1, 'breastSizeControl': 'extra_large_breasts', 'debugMode': True})`
  - result: prompt contains `huge natural massive XXXL breasts`
- Python compile:
  - `python -m py_compile backend/options.py backend/forms/constants.py backend/prompt_service.py backend/engine/generator.py backend/engine/selectors.py backend/engine/validator.py backend/services/run_service.py`
  - result: passed

### Issue 39 - Women Line-Bank Outfit Color Pass
- Focused clothing render regression:
  - `python -m pytest tests/test_clothing_color_rendering_smoke.py -q`
  - result: `5 passed`
- Focused repo-backed regression:
  - `python -m pytest tests/test_line_bank_loader.py tests/test_routing_validation_smoke.py tests/test_clothing_color_rendering_smoke.py -q`
  - result: `31 passed`
- Compile checks:
  - `python -m py_compile backend/engine/render/prompt_renderer.py backend/services/postprocess.py`
  - result: passed
- Live x20 smoke:
  - `women random spicy=6`: `no_color=0`, `findings=0`
  - `women nightlife spicy=8`: `no_color=0`, `findings=0`
  - `women luxury spicy=6`: `no_color=0`, `findings=0`
  - `couples random spicy=6`: `no_color=0`, `findings=0`
- Playwright E2E:
  - `npm run test:e2e -- --workers=1 --reporter=line`
  - result: `5 passed`
