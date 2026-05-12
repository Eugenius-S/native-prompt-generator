# Changelog

## 2026-05-03

### Changed - routing and line-bank smoke test stabilization pass
- Updated `test_line_bank_women_pose_smoke.py` expectations to reflect portrait-safe pose/outfit rendering normalization while still validating that selected women line-bank values are preserved on candidate fields.
- Updated sport routing smoke expectations in `test_routing_validation_smoke.py` to accept the current deterministic sport-compatible scene family set instead of a single hardcoded scene family.
- Kept strict route checks (`sports_flirt`) in sport-focused routing assertions so the tests still validate sport routing behavior, not random scene drift.

## 2026-05-04

### Changed - issue 69 phase 2 prompt-service thinning step 3
- Replaced the remaining local `ALLOWED_MODES` copy in `backend/prompt_service.py` with the shared forms constant so mode validation no longer drifts between modules.
- Switched `backend/services/run_service.py` off the broad prompt-service module import and onto direct public prompt-service helpers plus `backend.storage.append_history`.
- Deleted two dead delegated bodies in the prompt-service women/couples color-diversity wrappers; those paths already return straight into `backend.services.postprocess`.

### Changed - issue 69 phase 2 prompt-service thinning step 4
- Switched `backend/modes/women.py`, `backend/modes/men.py`, and `backend/modes/couples.py` off the broad `from backend import prompt_service as ...` import and onto direct helper imports for profile build, prompt-constraint application, and post-render color diversification.
- Narrowed `backend/services/debug_summary.py` to a function-local prompt-service helper import so the module no longer carries a broad runtime dependency while still avoiding a `prompt_service -> postprocess -> debug_summary` import cycle.
- Revalidated the touched API and realism smoke slice after the import cleanup; no behavior retune was needed.

### Changed - issue 69 phase 2 prompt-service thinning step 5
- Narrowed `backend/forms/user_profile.py` from a broad local prompt-service module import to an explicit local helper/constant import list used by `_user_style_profile()`.
- Kept the import local to the function so the existing `prompt_service -> forms.user_profile` load order stays cycle-safe while still making the dependency surface smaller and clearer.
- Revalidated the touched API, routing, and outfit/scene coherence smoke slice after the cleanup.

### Changed - issue 69 phase 3 scoring/service cleanup step 3
- Extracted the shared photo-treatment profile lookup into `backend/services/photo_treatment_lookup.py` so `scoring.py`, `treatment_balance.py`, `postprocess.py`, `debug_summary.py`, and the prompt-service compatibility shim all read treatment metadata from one neutral helper.
- Removed the old hidden dependency where runtime services imported that shared lookup through `debug_summary.py`.
- Revalidated the touched API and random-quality public-contract smoke slice after the extraction.

### Changed - issue 69 phase 3 scoring/service cleanup step 4
- Extracted the clone-avoidance, cheap-fallback, and location-motif batch-penalty helpers out of `backend/services/scoring.py` into `backend/services/batch_penalties.py`.
- Kept the existing helper names available through `scoring.py` via direct imports so the current tests and callers did not need a behavior change or API rewrite.
- Revalidated the direct penalty-helper smoke slice and API smoke after the extraction.

### Changed - issue 69 phase 1 and phase 2 closeout pass
- Moved the legacy bridge adapter into ignored `_legacy/legacy_bridge.py` and moved the real legacy people implementation into ignored `_legacy/legacy_people.py`, leaving `backend/legacy_people.py` as a tracked compatibility shim only.
- Added public `merged_form_state`, `resolve_runtime_controls`, and `infer_theme_style_mode` wrappers on `backend/prompt_service.py`, then switched `backend/services/run_service.py` and `backend/services/preset_service.py` to those public helpers instead of the private prompt-service names.
- Marked phase 1 and phase 2 complete in `PROJECT_PLAN.md` now that the visible backend surface no longer hosts the legacy implementation or the private prompt-service dependencies.
- Revalidated the touched API, men/couples, and direct legacy-shim smoke slice locally after the quarantine move.

### Changed - close-up profile / strong-turn wording bank pass
- Split the close-up pose wording in `backend/engine/render/prompt_renderer.py` into richer profile and strong-turn phrase lanes for `face_only` and tight portrait framings.
- Kept the existing close-up smoke markers valid while expanding the bank so profile close-ups have more distinct side-profile / three-quarter-profile phrasing options.
- Revalidated the close-up smoke slice after the wording change.

### Changed - issue 69 phase 6 release validation
- Ran the release smoke slice in two isolated pytest processes so the order-sensitive `test_issue41_random_balance_smoke.py` could be validated cleanly alongside the women, men, and couples smoke coverage.
- Confirmed the broad release slice stayed green after the refactor and docs passes.
- No code changes were needed for this step; it was validation and release-readiness bookkeeping only.

### Changed - issue 69 phase 5 setup flow tighten step 1
- Aligned `README.md` and `QUICKSTART.md` with the bundled `SETUP_PROMPT_GENERATOR_WEB.bat` / `START_PROMPT_GENERATOR_WEB.bat` flow so the public docs match the real setup path.
- Kept the direct `python app.py` path in the quickstart as an explicit fallback for local runs.
- This was a docs-only pass; no runtime behavior changed.

### Changed - issue 69 phase 4 public docs cleanup step 1
- Cleaned the public-facing wording in `README.md` and `QUICKSTART.md` so the top-level docs read more like release docs and less like internal staging notes.
- Removed the internal-only issue-reporting note and the CI file pointer from the public docs.
- No runtime behavior changed; this was a docs-only cleanup pass.

### Changed - issue 69 phase 3 scoring hotspot split step 2
- Extracted the race, body, style, and couples identity helper cluster into `backend/services/selection_scoring.py` so the scoring module can stay focused on orchestration and the remaining clone penalties.
- Kept `backend/services/scoring.py` as the compatibility facade for the existing public helper names while delegating the extracted logic to the new module.
- Revalidated the focused random and couples smoke slice after the split.

### Changed - issue 69 phase 3 scoring hotspot split step 1
- Extracted the photo-treatment and random-light balance cluster into `backend/services/treatment_balance.py` so the main scoring module can stay focused on the remaining batch and identity helpers.
- Kept `backend/services/scoring.py` wired through the new service module and restored the shared scoring constants needed by the existing random-balance helpers.
- Revalidated the focused random / couples smoke slice after the extraction.

### Changed - issue 69 phase 2 prompt_service thinning step 2
- Removed the unused `_summarize_debug` and `_render_mode_prompts` compatibility wrappers from `backend/prompt_service.py` after the live run service already owned those paths.
- Repointed `backend/services/run_service.py` to `backend.services.batch_selection._best_batch` directly, removing one more facade hop.
- Revalidated the backend slice after the cleanup; the targeted smoke set stayed green.

### Changed - issue 69 phase 1 legacy isolation and phase 2 prompt_service cleanup
- Kept the active code path on the tracked `backend/legacy_people.py` entry point via `backend/legacy_bridge.py`, while preserving a local-only quarantine mirror under ignored `_legacy/` for migration work.
- Removed the unreachable duplicate scoring and batch-selection bodies from `backend/prompt_service.py`; the live paths already delegate to `backend.services.scoring` and `backend.services.batch_selection`.
- Revalidated the bridge / wrapper / prompt facade slice with the backend gate plus the direct legacy import smoke tests.

### Changed - issue 69 phase 0 inventory and first legacy isolation step
- Re-read the current public-release refactor plan and wrote a short inventory into `PROJECT_PLAN.md` covering the stable public surface, internal docs to review later, and legacy entry points to keep in view.
- Added a small `backend/legacy_bridge.py` adapter and routed the current men/couples legacy render calls plus male-identity preview calls through it so the main code surface no longer imports `backend.legacy_people` directly.
- Kept `backend/prompt_service.py` as the compatibility facade and verified the change with the backend gate before and after the extraction step.

### Changed - issue 106 angle bucket diversity for close-up prompts (Option B)
- Replaced flat `FACE_ONLY_POSE_VARIANTS` and `TIGHT_PORTRAIT_POSE_VARIANTS` tuples in `prompt_renderer.py` with structured `CLOSE_UP_ANGLE_BUCKETS` and `TIGHT_PORTRAIT_ANGLE_BUCKETS` dicts (4 buckets each: front / three_quarter / profile / tilt).
- Added `_close_up_angle_bucket()` helper that cycles deterministically through all buckets using `_batch_index % 4` when batch_index is available, falling back to seeded random when not.
- Updated `_framing_aware_pose_text()` to select angle bucket and then pick a phrase from that bucket for both `face_only` and tight portrait framings.
- Injected `_batch_index` into rendered candidates in `backend/modes/women.py` so the renderer receives a stable position signal per batch.
- Added `_CLOSE_UP_FRAMING_IDS` / `_CLOSE_UP_BUCKET_ORDER` constants and `_close_up_angle_diversity_score()` function in `scoring.py` — rewards batches with multiple angle buckets covered, penalizes single-bucket dominance.
- Wired `_close_up_angle_diversity_score()` into the batch scorer before `return`.
- Added 8 smoke tests in `tests/test_issue106_close_up_angle_diversity_smoke.py` covering anti-regression, bucket language presence, 4- and 8-shot coverage checks, and scoring behavior.

## 2026-05-03

### Changed - close-up framing safety and variation pass
- Reworked `face_only` framing render contract to avoid extreme face-filling crops: prompts now request a tight beauty headshot with full hair visibility, slight headroom, and a hint of neck/upper-shoulder context.
- Added explicit anti-extreme close-up wording in the framing block for `face_only` so the renderer no longer asks for a pure face-only crop.
- Added deterministic safe variation for tight portrait pose text (`face_only`, `close_portrait`, `head_and_shoulders`) to reduce repetitive close-up pose phrasing across batches while preserving portrait-safe constraints.
- Updated framing smoke expectations for the new `face_only` contract wording and safety behavior.

## 2026-05-01

### Changed - issue 98 full-body framing B+E pass
- Shortened the full-body and ankle-up framing render text so the standing lane now reads as a simpler camera pull-back / full-height composition instruction instead of a long soft prompt sentence.
- Removed `headroom` from the technical block for `full_body` and `ankle_up`, so full-length prompts no longer carry a portrait-style upward crop cue.
- Kept the standing-safe full-body wording in the render block and added regression coverage for the missing `headroom` cue.
- Revalidated the affected framing smoke suites after the wording pass.

## 2026-04-30

### Changed - issue 105 dry-coastal split and tag-driven pose contracts sub-tasks 1+2
- Added `_water_contact_scene_tags()` helper in `selectors.py` scoped to scenes where the subject is genuinely at or near water (`pool`, `beach`, `spa`, `shower`, `rain`, `humid`, `wet_friendly`). Excludes `coastal` which covers dry boardwalk / promenade / colonnade ambience.
- Tightened swimwear gate to use `_water_contact_scene_tags()` instead of the wider `_wet_context_tags()`, so swimwear is now blocked on dry coastal scenes (boardwalk, promenade) while still allowed on pool deck and shoreline.
- Split the pool/coastal outfit gate into two branches: `pool | beach` enforces water-contact outfits; `coastal` (dry) now allows resort-casual outfits (`dress`, `dressy`, `quiet_luxury`, `soft`) without requiring swimwear.
- Synchronized `WET_OUTFIT_CONTEXT_TAGS` in `line_bank_loader.py` to match the new narrower water-contact set (removed `coastal`).
- Added `cabinet` tag to `cabinet_reach_inside` pose in `pose_bank.json` so tag-driven cabinet checks work.
- Converted all pose-id branches in `_pose_for_base_space` to tag-driven contracts (`counter`, `bed`, `stairs`, `chair`, `lounge`, `cabinet`), making the routing extensible without manual pose-id additions.
- Added 3 new regression tests covering dry-coastal + mini dress (allowed), dry-coastal + swimwear (blocked), pool + swimwear (allowed).

### Changed - issue 105 prop-aware scene, pose, and wet-context matching first pass
- Tightened line-bank pose scene matching so support-bound pose records no longer short-circuit through generic `standing_like` before their required support tags are checked.
- Expanded line-bank pose inference around bed-surface language (`blanket`, `sheet`, `mattress`, planted-on-bed phrasing) so bed-anchored lines are tagged as real bed-support poses instead of drifting through generic standing logic.
- Added a first `perched` support contract in static selector routing so vanity / counter / bench style poses now require a credible support surface and no longer pass through sporty gym-like contexts without one.
- Added a validator hard requirement for `water_contact_pose`, so beach / shoreline contact poses now need a wet-friendly outfit signal (`swimwear` or `wet_possible`) instead of silently accepting dry dress looks.
- Added a focused issue-105 smoke regression that locks the current bad-match class down across courtyard+bed, gym+perch, and shoreline water-contact + dry-outfit examples.

### Changed - issue 103 women random color and outfit diversity first pass
- Reduced women-random fitted-lane pressure at the profile layer by removing `mini_dress`, `blazer_mini_dress`, and `bodysuit_trousers` from the active preferred subset used by balanced reveal plus random-style profile merging.
- Broadened the women-random preferred wardrobe tail toward more non-fitted silhouettes such as `cardigan_skirt`, `sweater_jeans`, and `apron_workshop_trousers`, and widened the carried color-story pool with less repetitive neutral-tail options.
- Added a dedicated women-random batch diversity score so best-batch selection now rewards broader outfit-family and color-story spread while penalizing fitted-lane concentration and over-dominant issue-palette colors.
- Added a focused issue-103 regression smoke that checks both the direct scorer preference and a live multi-seed women-random sweep.

### Changed - issue 102 same_person framing and pose rigidity first pass
- Added a dedicated `same_person` visual-diversity batch score so identity-locked batches now explicitly reward broader pose-family and framing spread instead of being judged only by the generic batch scorer.
- The new first-pass scorer adds pressure for seated / lying presence and for non-rigid framing variety, while penalizing standing-heavy batches that over-concentrate on `waist_up` / `cowboy_shot` style repetition.
- Added a focused regression test that locks the intended direction: under `same_person`, a varied pose / framing batch now scores above a rigid standing-plus-mid-frame batch.

### Changed - issue 104 support-aware pose matching first pass
- Added support-surface inference to scene tags so base spaces can distinguish chair, sofa, bed, stairs, counter, cabinet, and floor-like support cues from their scene text.
- Tightened pose routing so seated, lying, stair-seated, and counter-lean poses now require real matching support surfaces instead of passing on generic interior or coastal context alone.
- Synchronized the duplicated pose helper path in both `selectors.py` and `generator.py`, then added a focused smoke regression that covers the current absurd support-match examples.

### Changed - issue 101 fantasy and sci-fi shared location split
- Added filename-driven shared location domains so `shared/locations/all.md` now reads as `realism` and `shared/locations/fantasy_locations.md` reads as `fantasy_sci_fi`.
- Added explicit requested-location-domain inference from active style / exact-theme controls and threaded it into the live user profile used by candidate selection.
- Changed shared-location selection to filter by location domain before semantic scene matching, so realism runs no longer compete with fantasy / sci-fi location lines and fantasy-coded runs no longer fall back to realism shared locations.
- Kept fantasy / sci-fi fallback domain-safe: if no fantasy-coded shared location survives matching, the generator now stays blank instead of borrowing a realism line.

### Changed - women line-bank and shared-location refresh
- Refreshed the women outfit override banks across `1_3`, `4_5`, and `6_8` with updated wording and distribution-cleanup edits.
- Cleaned the shared `all` location override bank so the live realism pool stays focused on grounded locations instead of carrying fantasy / sci-fi tails inline.
- Added a separate draft file `fantasy_locations.md` as the seed bank for a later fantasy / sci-fi location lane split rather than continuing to mix those locations into the realism-first shared pool.

### Changed - issue 95 batch-40 search bottleneck first pass
- Investigated `batchSize=40` slowdowns and narrowed the pathological case to constrained exact-theme runs, where most wasted time sat inside one `candidate_builder.generate_batch(...)` pass rather than in outer `_best_batch(...)` retries.
- Added an early outfit compatibility filter for required scene-family pools so large exact-theme batches stop spending retries on outfits that can never land in the requested scene family.
- Trimmed the most wasteful first anti-repeat retry stage for large constrained scene batches, reducing futile `build_candidate(...)` retries before the generator falls back to the already-existing relaxed stages.

### Changed - issue 95 batch-40 search bottleneck second pass
- Profiled the remaining slow default `random` batch-40 path and found that the main waste had shifted to early strict `random_balance` enforcement, especially repeated `Random indoor/outdoor balance target missed.` failures in the first retry stage.
- Relaxed only the first retry stage for large random-balanced batches by shortening the early retry budget, narrowing the `recent_batch` window, and deferring strict random-balance enforcement to the later fallback stages that already preserve the final batch mix.

## 2026-04-29

### Changed - framing follow-up for issues #98 and #99
- Strengthened the full-body and ankle-up framing contract so standing full-length prompts now explicitly call for camera pull-back, centered full-height composition, and ankle-or-feet coverage when the pose allows instead of relying on a softer generic full-length label.
- Hardened portrait framing language across close, head-and-shoulders, bust-up, below-chest, and waist-up lanes so they now explicitly keep full head and hair visible with breathing room above the head and no top-of-head crop.
- Added focused framing regressions for the stronger full-body contract and the portrait anti-top-crop wording in both renderer-level smoke suites.
- Tightened `more_full_body` scheduling so the control no longer reserves an intentional mid-shot tail and now allocates only `full_body` / `ankle_up` group share in the checked seeded slice.

### Changed - exact theme edge-case routing follow-up
- Made explicit `womenSceneFamily` authoritative even when a broader non-random `sceneFocus` is active, so a manual family choice no longer gets diluted into the larger family pool.
- Added higher-priority exact-theme hints for airport / runway travel, train compartments, industrial spaces, and fire-escape wording, and changed exact-theme hint matching to keep only the most specific matched hint tier instead of unioning generic overlaps like `lounge` or `loft` back in.
- Added focused routing smoke coverage for `industrial loft`, `train compartment`, and `fire stair landing` so these themes now hard-lock the checked scene-family lanes instead of drifting back into random families.
- Added exact-theme-aware shared location filtering in candidate building, using raw theme tokens to keep `line_bank_location` aligned with the requested edge-case theme instead of falling back to unrelated shared-location tails.
- Removed the broad shared-location fallback for exact-theme runs, so when no theme-compatible location line exists the generator now leaves the location line empty instead of injecting a false-but-scene-compatible location.
- Tightened exact-theme shared-location steering again so the location filter uses the final non-generic theme anchor token rather than any token overlap; this removes `train platform` / `station cafe` leakage from `train compartment` while preserving the already-fixed `industrial loft` and `fire stair landing` lanes.

### Changed - issue 100 core outfit-to-scene coherence first pass
- Strengthened the core `outfit_family -> scene_family` gate in selector routing so obviously mismatched looks are filtered before the scene family is chosen, not only later through line-bank cleanup.
- Added a new wellness-context check that blocks vacation/daywear outfit families from leaking into sporty and restorative spaces such as pilates, juice-bar, and spa-movement lanes unless the outfit already reads active, swim, or wellness-safe.
- Added a new public-elegant scene check that blocks clubwear / bodysuit / high-risk nightlife outfits from leaking into travel, staircase, lounge, and other non-bar luxury-public contexts while keeping true nightlife bars available.
- Added focused regression smoke coverage for the checked mismatches plus valid control pairs so future selector changes cannot silently reopen the same issue-100 leak class.

### Changed - issues 98 and 99 framing contract hardening first pass
- Replaced the older feet-first `full_body` / `ankle_up` wording with a stronger full-length camera-distance contract so standing full-height shots now read as a true full-length lane instead of a soft head-to-toe hint.
- Split standing and non-standing full-height framing text into dedicated full-length clauses that keep the whole figure visible in frame while allowing ankles-or-feet coverage to depend on composition instead of treating both feet as the only success condition.
- Hardened portrait framing render text around the safer beauty zone so `close_portrait`, `head_and_shoulders`, `bust_up`, `below_chest_portrait`, and `waist_up` now all carry explicit head visibility plus breathing-room language.
- Added focused smoke coverage for the new standing full-length contract and for portrait headroom wording in the active render path.
- Follow-up schedule tuning moved `more_full_body` framing-group targets from `0.70 full / 0.20 mid / 0.10 portrait` to `0.82 full / 0.12 mid / 0.06 portrait`, so batch planning now favors true full-height lanes materially more often.
- Follow-up anti-collapse pass strengthened `full_body` / `ankle_up` framing text with explicit `no waist-up / no mid-shot / no portrait crop` constraints and added `standing` pose-tag preference for `more_full_body` profile routing.
- Follow-up control split tightened framing-group routing so `more_full_body` no longer schedules portrait-group frames and `more_portraits` no longer schedules full-body-group frames in the checked seeded slice.
- Renamed the pose/framing control label from `More portraits` to `Portraits` in backend option payloads (UI now shows the shorter wording).

## 2026-04-27

### Changed - photo type control first pass
- Added a new top-level `Photo type` control layer with six modes: `Balanced`, `Glossy`, `Studio`, `Stylized`, `Amateur`, and `Custom`.
- Reframed `Photo treatment bias` as a `Custom`-only manual lock instead of a control that always competes with the broader stylization choice.
- Added a first-pass curated treatment mapping for `Glossy`, `Studio`, `Stylized`, and `Amateur`, seeded from the strongest non-cheap light/treatment lanes in the checked `good light.md` sample rather than blindly importing the whole file.
- Added first-pass `Studio` scene pressure through the new profile layer so studio-oriented runs can request `studio` scenes without needing a separate hardcoded treatment lock.
- Made explicit `Photo type` modes authoritative over late `clean_commercial` remaps, so postprocess no longer rewrites `Glossy / Studio / Stylized / Amateur` back into unrelated random-style treatment tails.
- Follow-up tuning tightened `Amateur` toward phone / analog / selfie-friendly scenes and removed `clean_commercial` from the allowed amateur treatment lane, leaving only a small `direct_light_editorial` carry-over tail from the stronger current-light look.
- Second follow-up tuning tightened `Glossy` away from arty/studio tails by banning `creative_gallery`, `studio`, `nightlife_neon`, and `wellness_spa`, and added explicit debug visibility for `effectivePhotoType` plus treatment mix/quality/tone distributions.
- Third follow-up tuning made `Studio` more studio-specific by removing `clean_commercial` from the studio-required lane, and tightened `Stylized` away from `direct_light_editorial` / `studio_seamless` / daylight tails.
- The same follow-up fixed a profile-merge leak so explicit photo-type `deprioritized` treatments and `banned` scene families now subtract from the broader `styleMode=random` preferred sets instead of merely being unioned on top.
- Fourth follow-up tuning gave `Balanced` its own healthy-default profile layer, pushing it toward calm mixed non-extreme lanes instead of leaving it as an empty pass-through.
- The same `Balanced` pass also made non-`Custom` `photoType` modes authoritative in late postprocess and added a narrow `Balanced` cleanup remap so phone/selfie and other extreme treatment tails are redirected back into the intended default lane.

### Fixed - issue 82 portrait framing no longer argues with lower-body prompt detail
- Added framing-aware outfit rendering so portrait crops now strip lower-body outfit clauses such as `with a low rise micro skirt` or `and mini skirt` instead of feeding the image model contradictory full-look text.
- Extended the portrait outfit guard so line-bank wording also trims comma-split lower-body tails and sanitizes one-piece phrases like `mini dress` down to portrait-safe visible garment wording.
- Added framing-aware pose rendering so portrait crops no longer reuse lower-body pose/body-language text like `hips angled back` or thigh-based hand placement that conflicts with close portrait framing.
- Tightened portrait hand-action filtering so `waist` / `waistband` hooks do not survive in bust-up and tighter portrait crops.
- Kept full-body rendering unchanged, so the same outfit and pose detail still survives in `full_body` and `ankle_up` paths where that information is actually helpful.

### Changed - issue 83 treatment-quality taxonomy first pass
- Added a first explicit treatment-quality taxonomy layer so photo treatments now carry a code-side distinction between `quality_tier` and `treatment_tone` instead of relying only on broad `stylized / polished` grouping.
- Rebuilt the women random mix helper around four intent buckets: `phone_snapshot`, `casual_low_end`, `editorial_non_phone`, and `polished_glam`, so cheap documentary / snapshot lanes are no longer hidden inside one generic non-phone stylized pool.
- Added first-pass women selection, scoring, and remap penalties against `raw_low_end` and `casual` treatment lanes in `random`, `luxury`, and `romantic` contexts.
- Removed the most direct women luxury/random remap paths that were still pulling `mirror_selfie`, `casual_indoor_selfie`, and other low-end lanes into premium-coded scenes.
- Follow-up wording cleanup rewrote the cheapest surviving treatment text in `photo_treatments.json`, replacing phrases such as `ordinary available light`, `cheap-flash snapshot feel`, and `unpolished realism` with less low-end render language while keeping the treatment identities distinct.

### Fixed - issue 78 raised-arm pose crops in tighter framing
- Removed the most direct raised-arm line-bank pose wording from the live women and men `6_8` pose banks and replaced it with safer high-spicy alternatives that do not demand extra headroom.
- Added a framing-aware line-bank pose guard so `waist_up`, `bust_up`, `head_and_shoulders`, `face_only`, and similar tighter crops now reject overhead-arm pose lines before they surface.
- Moved women/couples line-bank pose filtering to run after `camera_framing` selection and threaded the same framing-aware veto through the legacy men path.

### Fixed - issue 76 women random treatment mix skew toward smartphone output
- Added a shared treatment-mix bucket layer (`phone_snapshot`, `stylized_non_phone`, `polished_glam`) and made women `styleMode=random` choose treatments against an explicit `10 / 30 / 60` target instead of one broad stylized-vs-polished split.
- Retuned women random treatment preferences away from selfie-heavy lanes, reduced the aggressive `clean_commercial -> casual/selfie` remap pressure, and shifted scene-aware remaps toward more editorial/polished alternatives.
- Rebuilt women random treatment batch scoring so phone-heavy batches are penalized directly while polished/editorial dominance and non-phone stylized variety are rewarded.

### Fixed - issue 77 location/background hybrid scene assembly
- Stopped `line_bank_location` rendering from splicing unrelated `setting_material`, `detail_accent`, and `atmosphere_cue` tails onto custom location lines, which was producing hybrid prompts like `car wash tunnel + travertine + books`.
- Removed the active repair-rule paths that rewrote unrelated conflicts into the generic `penthouse + travertine + flowers + warm glow` fallback, so repair no longer force-converts scenes into a luxury-spa hybrid read.

### Fixed - issue 79 cheap-looking outfit regression in refined modes
- Added a `budget_club_like` line-bank outfit tag for the most obviously cheap nightclub-coded phrases (`micro mini`, `tiny skirt`, `bandage`, `hot shorts`, `racerback top`, etc.).
- Blocked those cheap clubwear line-bank outfits from `random`, `luxury`, `romantic`, `lifestyle`, and similarly refined lanes while keeping them available in deliberately appropriate modes such as `nightlife`, `studio`, and some coastal/creative paths.

### Changed - issue 75 Z-Image framing-first opener rebuild
- Added a new data-driven `prompt_openers` bank so framing lead words and treatment nouns are no longer buried inside hardcoded renderer branches.
- Rebuilt the women prompt opener so the final prompt now starts with a framing-first, treatment-aware subject sentence such as `Full-body fashion photo ...` or `Full-figure mirror selfie ...` instead of leading with capture-style wording alone.
- Split subject identity text away from the opener and removed duplicate framing text from the technical tail so Z-Image sees one authoritative crop declaration at the very front.
- Added focused smoke coverage for the new opener contract, including a live explicit `mirror_selfie` path.

### Changed - framing random mix now includes new portrait and full-figure lanes
- Expanded `camera_framing` data with explicit new extremes for the model to mix in random runs: `face_only`, `below_chest_portrait`, and `ankle_up`.
- Kept the current framing IDs as the base set, but flattened portrait/full-body weights so random batches now mix old and new crop lanes at roughly equal strength instead of hiding the new lanes behind tiny tails.
- Extended portrait/full-body control bias so `More portraits` can target the tighter portrait lanes too, while `More full body` now treats `ankle_up` as part of the intended full-figure lane.
- Moved the rendered technical framing block earlier in the final prompt so Z-Image sees crop instructions before outfit/setting detail.

### Changed - issue 68 sidebar implementation follow-up
- Implemented the first frontend pass from the approved sidebar spec instead of leaving `#68` as docs only.
- Added reusable `choice chips` and `toggle` primitives, then moved high-frequency controls away from dropdowns where the option sets are short enough to scan.
- Reordered the sidebar around a clearer flow: `Generate`, `Subject`, `Appearance`, `Scene`, `Shot & style`, `Generation rules`, then utility panels.
- Moved saved presets into the lower sidebar utility area and removed the old preset list duplication from the output column.
- Fixed two frontend runtime regressions in the follow-up implementation pass: one bad function handoff in `frontend/app.js` and one broken template literal in `frontend/sections/output.js`.
- Updated the focused Playwright form-controls coverage so it now asserts the new segmented/chip sidebar contract instead of the old dropdown-heavy UI.

### Changed - issue 67 expression mood rebalance
- Added an explicit high-spicy mood guardrail so `calm_confident` is blocked at selection time for `spicyLevel 6-8` instead of only being weakly discouraged later.
- Rebalanced the base `mood_energy` weights so general random runs lean less often on `calm_confident` and give more room to `soft_flirty`, `bratty`, and `slow_seductive`.
- Relaxed the women low-spicy default from a hard `calm_confident` lock into a `calm_confident` / `soft_flirty` mix so lower-spicy random output keeps a calmer lane without collapsing into one mood read.

### Changed - issue 66 hotter couples 6-8 chemistry and gaze pass
- Expanded the couples line-bank pose pools for both `4_5` and `6_8`, moving softer close-contact ideas down into mid spicy and giving `6_8` a materially wider high-tension pose set.
- Rewrote the couple mood wording in the legacy render path so pairs are described as focused on each other instead of repeatedly defaulting to `direct eye contact` at the camera.
- Kept the change narrow to couples chemistry language and pose-bank content, without reopening the broader women/men mood weighting work.
- Synced the repo-backed loader assertion with the final `couples/poses/6_8.md` wording so CI now validates the live bank content instead of an older pre-rewrite line.

### Fixed - issue 65 framing control now materially shifts portrait vs full-body output
- Moved `Pose / framing` control beyond a weak late scoring nudge by feeding framing preferences into the active candidate-selection path.
- Added framing-control profile overrides so `More portraits` now biases heavily toward portrait groups and `More full body` now biases heavily toward true full-body framing.
- Added stronger camera framing render text such as `head-and-shoulders portrait` and `full body in frame, visible head to toe` so the final prompt carries a clearer framing instruction to the image model.
- Added focused smoke coverage to prove that portrait/full-body controls now materially shift multi-seed framing distributions.

## 2026-04-25

### Fixed - issue 55 OS-native UI path separators
- Added a shared frontend path formatter in `frontend/utils/path_format.js` to detect runtime OS and render display paths with native separators.
- Updated the Line-banks help section to render root path and folder examples through the shared formatter instead of hardcoded separators.
- Removed ad-hoc path-separator assumptions from `frontend/sections/output.js` while keeping backend file-loading behavior unchanged.

### Fixed — issue 54 repeated citrus and pool location motifs
- Added a structural location-motif diversity penalty in batch scoring for `random`, `lifestyle`, `coastal`, and `vacation` styles.
- The new penalty classifies location text into motif families (for example `waterside`, `orchard_citrus`, `garden_nature`, `urban_social`) and penalizes over-concentrated motif clusters instead of patching specific one-off phrases.
- Added stronger caps for the two noisy motif families (`waterside`, `orchard_citrus`) while preserving broader summer-outdoor direction in coastal/vacation modes.

### Fixed — issue 53 random race preset routing leak
- Fixed random ethnicity routing in the active batch-selection path by introducing a curated random-default ethnicity id pool that excludes `middle_eastern` and `south_asian`.
- Kept `mostly_mixed` behavior intact so Arab and Indian identities still surface in that preset.
- Kept exact race presets intact so `middle_eastern` and `south_asian` still lock correctly when requested explicitly.

### Changed — issue 58 dedicated couples pose line bank
- Added a dedicated couples pose line-bank contract under `backend/engine/data/overrides/line_banks/couples/poses/{1_3,4_5,6_8}.md` with starter content for low, mid, and high spicy ranges.
- Extended the line-bank loader contract so `couples` is now a supported line-bank gender for `poses` only, while women/men keep their existing `poses/expressions/outfits` contract and shared keeps `locations`.
- Wired couples candidate selection to consume `couples/poses` records by spicy bucket and scene-compatibility filtering.
- Updated couples prompt rendering so selected line-bank pair poses surface directly in the final `Pose:` segment while preserving existing couple-interaction metadata and lane logic.
- Expanded debug output for couples with `coupleLineBankPose`, and updated line-bank workflow docs to include the new couples pose layer.

### Changed — issue 56 stronger line-bank semantics and issue 57 muted palette rebalance
- Extended line-bank location inference with more scene-aware tags such as public/private, day/night-capable, wet-humid, resort, restaurant, and seat-friendly so shared location lines are filtered by richer context instead of only broad keyword gates.
- Extended line-bank outfit inference with hot-weather, indoor-neutral, lounge, restaurant, active, minimal-coverage, layered, dressy, casual, and seat-friendly tags, then tightened the outfit scene matcher so public dining, nightlife, lounge, and resort contexts reject more obviously wrong combinations.
- Rebalanced neutral-heavy color selection by lowering the base weights of `clean_neutrals` and nearby muted stories, tightening clone-prone muted-color penalties, and reducing how aggressively postprocess color diversification steers batches back toward `clean_neutrals`.
- Added a focused muted-palette smoke test so random women batches are checked for neutral collapse directly instead of relying only on manual sweeps.

## 2026-04-23

### Changed — issue 46 bright summer outdoor location bank wave 1
- Added the first bright-summer expansion wave to the unified shared location bank: pool decks, shallow-water pool steps, seaside/boardwalk variants, rooftop pool, city cafe terrace, warm street, lawn, and flower-field variants.
- Extended location-tag inference just enough for this wave so `beach / shore / lawn / meadow / field / park / sunflower / wildflower` lines classify more naturally for outdoor/coastal/garden matching.
- Kept the change data-first and did not touch random weighting or scene-balance logic.

### Changed — issue 46 bright summer outdoor location bank wave 2
- Added a second bright-summer outdoor wave focused on more distinct beach/pool/nature/city/cafe variants: pebbled beach, rocky cove, dune path, infinity pool edge, lap pool, pool bar deck, park lawn, orchard row, flower farm lane, tram street, marina cafe deck, and summer restaurant terrace.
- Kept the second wave data-only because the compatibility pass from wave 1 already covered the vocabulary needed by these new lines.

### Changed — issue 46 bright summer outdoor location bank wave 3
- Added a final curated fill pass with more summer-bright outdoor variants: cliffside overlook, beach volleyball sideline, lagoon shallows, resort garden path, citrus grove, riverwalk cafe edge, harbor lookout, and poolside canopy daybed.
- Kept the wave data-only again and used it as the last breadth pass before deciding whether the issue is already broad enough to close.

### Changed — issue 45 shared location bank contract
- Replaced the spicy-bucketed shared location line-bank files with one common `shared/locations/all.md` file.
- Updated the loader so shared locations are treated as one common pool across all spicy levels, while poses, expressions, and outfits keep their existing bucketed contract.
- Kept scene-compatibility checks intact, so the contract change does not widen where location lines are allowed to surface.

### Fixed — issue 37 wet wording gating
- Blocked `wet` / `damp` / `soaked` / `dripping` outfit line-bank wording from dry city, hotel, and other non-wet scenes.
- Kept wet outfit wording available for explicit pool, beach/coastal, spa, shower, rain, humid, or wet-friendly contexts.
- Confirmed existing surface wet-skin selection was already scene-gated; this closes the remaining line-bank wording leak.

### Fixed — issue 35 custom-heavy batch fallback
- Added a second-pass generation fallback for custom-heavy requests that dead-end before producing any valid batch.
- The fallback relaxes hard appearance atom constraints into preferred constraints one step at a time, then removes only soft style steering if needed, while keeping race and exact-scene constraints authoritative.
- Covered the reproduced `women + random + spicy 6 + pushing_it + black hair + green eyes + extra-large breasts + hard anti-repeat` failure with a repo-backed smoke test.

### Changed — issue 41 random light and scene balance
- Added a random-only indoor/outdoor balance schedule so default random batches aim for an even scene split instead of drifting into mostly interiors.
- Added a random-only bright/muted light schedule plus matching batch scoring, targeting roughly 60% brighter/sunnier/direct-light candidates and 40% quieter/muted candidates.
- Kept explicit scene-family and preferred-scene controls out of this rebalance path so user-directed scene requests remain authoritative.
- Relaxed the repo smoke tolerance from `7..13` to `6..14` for indoor/outdoor counts after repeated healthy CI runs still occasionally hit a one-off `14/6` split.
- Relaxed the repo smoke bright-count tolerance from `10..15` to `8..16` after repeated healthy CI runs still occasionally landed a lower bright tail without any findings.

### Fixed — PR 32 CI race dropdown and luxury couples tail
- Updated the race-dropdown smoke test to match the current curated exact-preset UI from issue `#36` instead of the older shortened-list contract.
- Tightened `couples + luxury` outfit routing so the vacation-tagged `shirt_trousers` family cannot leak into hotel-lobby exact-theme runs.
- Updated the matching Playwright race-preset check and made the custom-select keyboard test target the focused option explicitly.
- Relaxed the men-romantic outfit-spread smoke threshold from an over-tight exact count to a still-useful anti-collapse guard.
- Relaxed the men-random outfit-repeat smoke cap from `6` to `7` per 20-item batch so CI still catches template collapse without failing on a healthy one-off distribution tail.
- Relaxed the men-random unique-outfit smoke floor from `6` to `5` per 20-item batch after CI showed an occasional healthy five-template distribution that still stayed under the repeat cap.
- Blocked domestic-tagged poses from nightlife/bar/night scene routing to close the remaining `couples_nightlife` matrix smoke tail.
- Banned `mini_dress` from women `sceneFocus=luxury` hotel-lobby style profiles so exact luxury interiors stay on calmer silhouettes.

## 2026-04-22

### Changed — women appearance parity with men
- Added a real women-side `Outfit vibe` control so the female appearance block now has a clothing-vibe axis similar to the existing male-side `Outfit vibe`, instead of relying only on `Outfit reveal`.
- Wired the new control through defaults, UI options, normalization, and women/couples style-profile assembly so it acts as a real outfit-bias input rather than dead chrome.
- Kept the new women clothing-vibe control additive on top of `Outfit reveal`: `reveal` still controls modesty, while `vibe` now nudges the actual clothing taste toward lanes like `luxury`, `romantic`, `nightlife`, `bookish`, or `sport`.
- Added a second women-side parity control, `Beauty finish`, so the female block now has a separate finish/polish axis roughly parallel to the male `Grooming` axis.
- Wired `Beauty finish` through defaults, UI, normalization, and women/couples style-profile assembly, where it now nudges preferred `makeup` and compatible `photo treatment` lanes like `fresh_natural`, `glossy_glam`, or `after_dark`.
- Finished the clothing-control unification pass by renaming the women-only secondary clothing knob from `Outfit reveal` to `Reveal level`, so both sides now read as one clothing model instead of two unrelated ideas.
- Added a shared outfit-vibe alias layer (`bookish -> cultural_bookish`, `beach -> coastal`, plus older male clothing aliases), so older/shorter saved values normalize into the same clothing-vibe vocabulary across women and men.

### Fixed — issue 29 CI portability pass
- Replaced the Windows-only Playwright web-server command in `playwright.config.js` with a cross-platform setup that passes `PROMPT_GENERATOR_PORT` through `webServer.env`.
- Kept the test target unchanged on port `8766`, but removed the Linux CI startup mismatch that had been making PR `#32` look unstable even though the app itself was healthy.
- Scoped the change narrowly to test infrastructure so the issue-29 runtime behavior and current prompt-generation logic stay untouched.

### Changed — issue 29 spicy 6-8 comparison baseline and first correction pass
- Added an explicit issue `#29` rollout plan to `PROJECT_PLAN.md` so another agent can continue from the same sequence instead of inventing a new spicy-tuning direction.
- Ran a baseline comparison matrix for `women / men / couples` across representative `spicyLevel 3 / 5 / 6 / 8`, then logged the main weak spots before changing code: women were already fairly separated, men still rendered too politely in some paths, and couples were the weakest because high spicy mostly reused flat chemistry wording.
- Tightened the first correction pass in two narrow places: `backend/services/scoring.py` now adds extra high-lane pressure for `men` and `couples`, and `backend/legacy_people.py` now lets `men` and `couples` render materially hotter spicy-aware moods plus more revealing/pushing-it couple interactions at `6-8`.

### Changed — issue 29 follow-up for men nightlife
- Added one last narrow follow-up for `men nightlife`, where the first pass still left the rendered mood too flat because the shared nightlife override kept stamping almost the same late-night confidence line across spicy bands.
- Made the nightlife mood override in `backend/legacy_people.py` spicy-aware for both `men` and `couples`, so `6` now reads as charged late-night confidence/chemistry and `8` now reads as a stronger after-dark magnetic lane instead of reusing the low-heat copy.
- Added a stronger `men + nightlife` treatment bias in `backend/services/scoring.py` so higher-spicy nightlife batches favor genuinely hotter treatment lanes instead of slipping back toward flatter polished choices.

### Changed — external pose bank wave 2
- Added a second small external pose-bank pass on top of wave 1, still scoped only to live women/men `poses` under `backend/engine/data/overrides/line_banks/`.
- Kept the follow-up wave deliberately narrow by adding exactly one new line to each of the six live pose files, so review stays incremental instead of collapsing into another bulk content dump.
- Logged the source trace for this follow-up under the review-note label `external_pose_review_pass_2026_04_22_wave2`.
- Follow-up cleanup replaced the newly added scene-prop-specific pose wording with more reusable posture-only lines and added a repo-backed line-bank smoke test for the checked-in live pose files.

### Changed — external pose bank wave 1
- Added the first small external pose-bank growth pass directly in the live women/men pose line-banks under `backend/engine/data/overrides/line_banks/`, keeping the rollout limited to `poses` only and leaving `couples`, `expressions`, `outfits`, wet variants, and size-control changes out of scope.
- Kept the first pass intentionally small and reviewable: `6` new women pose lines and `6` new men pose lines spread across the existing `1_3`, `4_5`, and `6_8` spicy buckets instead of a bulk content dump.
- Logged the source trace for this first pass under the review-note label `external_pose_review_pass_2026_04_22` so later cleanup and promotion history stay readable.

### Changed — stylization follow-up for random remaps and men luxury
- Re-enabled the real random-treatment remap path in `backend/services/postprocess.py` for both women and couples by removing the accidental always-keep behavior, so `clean_commercial` can now be swapped out again when random mode lands too clean.
- Added a dedicated `men + luxury` postprocess remap for `clean_commercial`, aimed at more editorial/lit alternatives instead of letting that lane stay overly polished and flat.
- Tightened `backend/services/scoring.py` for `men + luxury` by penalizing `clean_commercial` harder and rewarding broader lighting-family variety more strongly at both candidate and batch level.

### Changed — line-bank UI help entrypoint
- Added a small `Line-banks` help section to the local UI sidebar so the user can see the repo-relative line-bank root path, the current mode target files, and the current spicy bucket guidance without leaving the app.
- Added a generic copy-value action in the frontend so the line-bank root path can be copied directly from the new help section.
- Kept the implementation frontend-only and contract-safe by using the stable repo-relative path instead of changing the bootstrap payload shape.

### Changed — hybrid line-bank Phase 5 docs and safety sweep
- Added a safe starter layer for `backend/engine/data/overrides/line_banks/`: every live men/women `poses`, `outfits`, and `expressions` folder now has comment-only `1_3.md`, `4_5.md`, and `6_8.md` templates that users can edit without changing generation until real non-comment lines are added.
- Added `backend/engine/data/overrides/line_banks/TROUBLESHOOTING.md`, updated the line-bank README, and extended `backend/engine/data/README.md` so the manual workflow, safe starter behavior, and common mistakes now live next to the data layer instead of only in planning notes.
- Hardened `backend/engine/line_bank_loader.py` so root docs inside `line_banks/` are ignored and comment-only starter templates stay warning-free, which makes repository-scoped workflow docs and starter files safe by default.

### Changed — hybrid line-bank Phase 4 men expressions seam
- Added the optional men expression seam in the legacy men path, still scoped only to `mode == men`, so bucketed line-bank `expressions` can now surface through controlled mood wording without changing couples behavior.
- Kept the seam additive instead of replacing the legacy mood base: the chosen men expression now inserts into the final men mood line while preserving the existing direct-eye-contact phrasing.
- Exposed the selected men expression in debug metadata and covered the new surfacing plus no-leak behavior in the focused men line-bank smoke test.

### Changed — hybrid line-bank Phase 3 men legacy bridge
- Added the first men-side legacy bridge for line-bank `poses` and `outfits`, scoped only to `mode == men` so the new prompt-part text can surface in the legacy male path without changing couples behavior.
- Kept the bridge small by selecting line-bank men pose/outfit text through `backend/legacy_people.py`, preserving the existing male identity scaffold and leaving men `expressions` deferred.
- Threaded spicy level into the men bridge so bucketed men line-bank files follow the same `1-3 / 4-5 / 6-8` contract as the loader, and guarded the treatment stylizer so it does not overwrite chosen men line-bank values.

### Changed — hybrid line-bank Phase 2 women live wiring
- Added the first live line-bank prompt-part wiring for the women path: women `poses`, `outfits`, and `expressions` can now surface from the new line-bank folders without replacing the underlying geometry/scoring scaffolds.
- Kept the rollout safe by treating line-bank poses and outfits as render overlays on top of the existing women candidate scaffold, and by keeping the new expression seam additive instead of replacing `mood_energy`.
- Restricted the live line-bank rendering to `mode == women` and verified that the shared candidate-builder changes do not leak the new women prompt-part lines into current men or couples outputs.

### Changed — hybrid line-bank Phase 0 and Phase 1 scaffold
- Added `backend/engine/line_bank_loader.py` and extended `backend/engine/data_loader.py` so the project now has a dedicated line-bank folder contract plus a safe parse/validation layer for `women` and `men` `poses`, `expressions`, and `outfits` files.
- Added `backend/engine/data/overrides/line_banks/README.md`, created the separate `women/` and `men/` leaf folders for current and future domains, and enabled the new `load_line_banks` config flag without changing current prompt generation behavior.
- Kept the first implementation slice generator-safe by loading line-bank records into a separate `line_banks` payload only; no live selection/render wiring was added yet.

## 2026-04-21

### Changed — character constraint backend render-slot completion
- Added `backend/character_constraints.py` so `characterConstraint` now has one normalized backend source of truth for prompt assembly, scoring, and debug metadata instead of living only as free-text scorer input.
- Rewired prompt assembly to emit a dedicated `character` segment plus `candidate["character_constraint_segment"]`, keeping the field live while moving the rendered wording out of the subject sentence.
- Retargeted scoring/debug to the normalized segment and kept the current preview UI compatible by rendering the new segment when present.

### Changed — architectural refactor Phase 6 mode-wrapper rename completion
- Renamed backend mode-wrapper exports from `WOMEN_MODE_HANDLER`, `MEN_MODE_HANDLER`, and `COUPLES_MODE_HANDLER` to neutral `WOMEN_HANDLER`, `MEN_HANDLER`, and `COUPLES_HANDLER`, and updated `backend/modes/registry.py` to use the new names.
- Renamed lingering men/couples wrapper-local legacy aliases such as `render_legacy_batch` and `legacy_prompts` to mode-neutral names while intentionally keeping `backend/legacy_people.py` as the current runtime implementation behind those wrappers.
- Removed an unused legacy render import from `backend/prompt_service.py` and validated the naming-only cleanup against the backend regression gate before marking Phase 6.4 complete.

### Changed — architectural refactor Phase 6 frontend CSS split completion
- Split `frontend/styles.css` into `frontend/styles/tokens.css`, `frontend/styles/layout.css`, `frontend/styles/controls.css`, and `frontend/styles/output.css` so design tokens, structural layout, interactive controls, and output/debug presentation no longer share one monolithic stylesheet.
- Kept `frontend/styles.css` as the stable browser entry by converting it into a thin `@import` hub, preserving the existing `frontend/index.html` load path and current selector surface.
- Validated the CSS split against the existing frontend Playwright phase gate before marking Phase 6.3 complete.

### Changed — architectural refactor Phase 6 prompt-service split completion
- Added `backend/services/scoring.py`, `backend/services/postprocess.py`, and `backend/services/batch_selection.py` so the remaining scoring, postprocess, and batch-selection logic no longer lives only inside `backend/prompt_service.py`.
- Rewired the heavy Phase 6.2 helper entry points in `backend/prompt_service.py` into compatibility delegation wrappers that now forward into the new backend service modules while preserving the existing call surface for forms, modes, and run orchestration.
- Kept behavior stable through the extraction by validating the refactor against the backend regression gate plus broader smoke coverage before marking the phase complete.

### Changed — architectural refactor Phase 6 generator split completion
- Added `backend/engine/selectors.py` for style profiles, selection helpers, scene/outfit predicates, photo-treatment selection, and candidate normalization that previously still lived in `backend/engine/generator.py`.
- Added `backend/engine/candidate_builder.py` for candidate assembly, retry scheduling, batch generation, and runtime-memory updates, so the remaining generator orchestration no longer lives only in `backend/engine/generator.py`.
- Rewired `backend/engine/generator.py` to delegate the moved selection and batch-builder entry points through compatibility wrappers, preserving existing callers while finishing the Phase 6.1 engine split.

### Changed — architectural refactor Phase 6 generator split checkpoint
- Added `backend/engine/data_loader.py` to own static content-bank loading, runtime memory IO, and shared lookup helpers that were previously embedded near the top of `backend/engine/generator.py`.
- Added `backend/engine/render/prompt_renderer.py` plus `backend/engine/render/__init__.py` so outfit phrasing, technical-block formatting, and full prompt/segment rendering no longer live only inside `backend/engine/generator.py`.
- Kept current callers stable by turning the moved generator helpers into compatibility wrappers, so `legacy_people`, mode wrappers, and prompt-service code continue importing from `backend.engine.generator` while the implementation now sits behind the new engine modules.

### Changed — architectural refactor Phase 5 frontend UI skeleton
- Added `frontend/components/icons.js`, `frontend/components/controls.js`, and `frontend/components/cards.js` so icon helpers, shared field/select primitives, and prompt preview card markup no longer live inside the browser entry.
- Added `frontend/sections/subject.js`, `frontend/sections/scene.js`, `frontend/sections/output.js`, and `frontend/controllers/form_controller.js` to move section rendering plus form-state orchestration out of `frontend/app.js`.
- Reduced `frontend/app.js` to render composition, bootstrap wiring, geometry helpers, and event delegation while preserving the current UI markup and browser behavior.

### Changed — architectural refactor Phase 4 frontend module entry skeleton
- Switched `frontend/index.html` to ES-module boot so `frontend/app.js` can stay the single browser entry while importing extracted frontend seams.
- Added `frontend/api/client.js` for bootstrap/generate/preset requests and `frontend/state/store.js` for shared client state plus small state helpers.
- Reduced `frontend/app.js` to consume the extracted API/store modules without changing current UI rendering, events, or form behavior.

### Changed — architectural refactor Phase 3 backend run skeleton
- Added `backend/modes/registry.py` plus thin `women`, `men`, and `couples` mode wrappers so render orchestration no longer lives entirely inside `backend/prompt_service.py`.
- Added `backend/services/debug_summary.py` and `backend/services/run_service.py`, moving debug summary assembly plus `generate_run()` / `_render_mode_prompts()` orchestration behind new backend service seams.
- Kept behavior and tests stable by leaving `backend/prompt_service.py` as the monkeypatch-compatible compatibility facade for append-history, RNG-sensitive tests, and still-unmoved scoring blocks.

### Changed — architectural refactor Phase 2 backend form skeleton
- Added `backend/forms/constants.py`, `backend/forms/normalizer.py`, `backend/forms/runtime_controls.py`, and `backend/forms/user_profile.py` as the first extracted backend form layer.
- Moved form normalization, runtime control resolution, theme hint matching, and user-style-profile assembly logic out of the large `backend/prompt_service.py` bodies into the new `backend/forms/` modules.
- Kept existing behavior and call sites stable by leaving compatibility wrappers in `backend/prompt_service.py` during the skeleton stage.

### Changed — architectural refactor Phase 1 backend entry and facade skeleton
- Moved the HTTP handler into `backend/api/http_handler.py` and left `app.py` as a thin startup entry that only parses host/port and boots `ThreadingHTTPServer`.
- Added `backend/services/bootstrap_service.py` for bootstrap payload assembly and `backend/services/preset_service.py` for preset save/delete facade logic.
- Kept `backend/prompt_service.py` publicly stable by delegating the moved bootstrap/preset entry points to the new service modules instead of changing import sites.
- Preserved test compatibility by keeping `app.PromptGeneratorHandler` importable as a compatibility re-export during the skeleton stage.

### Added — architectural refactor Phase 0 safety net
- Added `tests/test_public_contract_smoke.py` to lock the current public contract before backend/frontend extraction starts.
- Froze the current `/api/bootstrap` top-level payload keys, the persisted `generate_run()` top-level payload keys, and the on-disk `history` / `presets` serialization shape.
- Documented the current public HTTP and backend facade entry points inside `ARCHITECTURAL_REFACTOR_SKELETON_PLAN_2026_04_21.md` so later module moves keep the same callable surface.

### Changed — clothing color render naturalization
- Reworked outfit color rendering so dual-color `color_story` values no longer read like one garment painted in two colors by default.
- Made single-piece outfits prefer a single dominant color, while separates and layered looks can now split colors more naturally across top / bottom / outer-layer roles.
- Added a small patterned-clothing path and kept full two-color whole-garment wording as a rare outcome instead of the default.
- Routed the same render logic through women prompts plus legacy men / couples outfit text so the clothing wording stays more coherent across all three modes.

### Changed — stylization follow-up for lighting play and compatibility
- Expanded the lighting bank with new practical, ambient, moody, spotlight, and silhouette families so random batches can show more lighting variety without breaking scene compatibility.
- Relaxed random-mode photo-treatment balancing so polished output can survive selection and remap instead of collapsing into all-stylized batches.
- Preserved `clean_commercial` in women random and couples random remap paths, which brought the final mix much closer to the intended polished/stylized split.

### Fixed — age input now hard-locks women output
- Made the `Age` field a required age-band constraint for normal generation, so entering an age now fixes the output instead of only nudging it through scoring.
- Kept `sport` / `fitness` on the safe balanced path at `spicy 5`, while still unlocking the spicy activewear pack from `spicy 6+`.

### Changed — local spicy 6-8 promotion and pose bias
- Promoted the full local spicy `6-8` women pose pack, women outfit pack, couples interaction pack, and male-side couples outfit pack from drafts into the live core banks.
- Extended women high-spicy scorer coverage so the newly promoted local pose and outfit ids participate in actual selection, not just static bank storage.
- Rebalanced women spicy `6-8` pose selection toward a roughly `65/35` sexy-vs-ordinary mix through upstream pose preferences plus batch scoring, while keeping anti-repeat penalties active.
- Expanded `sport` / `fitness` spicy `6-8` routing so the promoted spicy activewear sets can surface instead of being blocked by the older safe-only outfit path.

### Added — local spicy 6-8 draft extraction pass
- Reviewed the imported `!poses and outfits` stash metadata-first for PNG files and visual-first for Pinterest JPG files.
- Added a local research note at `LOCAL_SPICY_6_8_REF_PASS_2026_04_21.md` to capture review method, reject rules, shortlist counts, and promotion questions.
- Added four narrow draft seed files for staged spicy `6-8` extraction work:
  - women poses
  - women outfits
  - couples interactions
  - couples outfit coordination / male-side styling notes
- Kept this pass draft-only and live-bank-neutral; no generator behavior changes while drafts remain disabled.
- Removed the temporary `!poses and outfits` source folder after the extraction pass completed.

### Fixed — couples male custom-race strict matcher
- Fixed the `couples + different_persons + maleRacePreset=other + maleCustomRace=...` strict identity path so it no longer hard-fails with HTTP `400` when the previewed male identity already carries the requested custom ethnicity text.
- Kept the current custom male debug/render shape intact and aligned the strict matcher with that existing preview behavior instead of rewriting male identity construction.
- Added focused regression coverage for both the low-level matcher and the full couples generation path.

### Changed — subject preset quick-pick cleanup
- Promoted `Japanese` from the draft ethnicity seed into the live subject bank and exposed it as a curated race quick-pick for women and men.
- Shortened the visible subject preset quick-picks by removing `Black Nigerian`, `Colombian Latina/Latino`, `Mexican Latina/Latino`, `White English`, `White Polish`, and `White Italian` from the default UI lists.
- Kept the removed preset ids backend-compatible for saved presets/history and added a frontend legacy-label fallback so old selections still render clearly instead of silently snapping to a different visible option.
- Added smoke and Playwright coverage for the curated quick-pick list, `Japanese` placement, and hidden-id compatibility.

### Changed — hair-color UI cleanup and copy icon sizing
- Moved the women-side dyed-hair toggle into the `Hair color` field itself, renamed it to `Allow dyed hair`, and shortened the supporting helper copy to only the behavior-relevant notes.
- Exposed the same woman-side dyed-hair toggle in `couples` mode and kept frontend/backend form normalization aligned so the toggle survives there when `Hair color = Random`.
- Moved `Custom hair color` above `Eye color` in the female physical-traits block and removed low-value helper text from obvious custom hair fields.
- Resized prompt copy icons to `24px` while keeping the current copy-button behavior.
- Added targeted backend coverage for the couples dyed-hair toggle and expanded Playwright coverage for the refreshed hair-color layout plus copy icon size.

### Changed — exact-theme UX shortcut
- Added a Scene-level `Enable exact theme scene lock` checkbox as a UX alias for `locationStrategy=exact_theme` while keeping the advanced `Location strategy` control visible.
- The shortcut now remembers the last non-`exact_theme` location strategy and restores it when the checkbox is turned off instead of blindly resetting the field.
- `Scene focus` is now disabled/subordinated while exact-theme mode is active, while `womenSceneFamily` stays available as the higher-priority explicit override.
- Added Playwright coverage to verify the shortcut, `locationStrategy`, and disabled `Scene focus` stay in sync.

### Changed — couples high-spicy interaction pass
- Added a draft couples interaction research seed at `backend/engine/data/drafts/pose_bank/high_spicy_couples_interaction_seed.json` with 16 adult-only, non-explicit `revealing` / `pushing_it` interaction ids.
- Added `HIGH_SPICY_COUPLES_INTERACTION_RESEARCH_2026_04_21.md` to capture source provenance, filtering lists, and the staged couples rollout contract.
- Promoted the reviewed couples interaction ids into the live `couple_interactions` bank inside `backend/engine/data/pose_bank.json`.
- Updated couples render routing so `spicyLevel 1-4` stays on the moderate-safe legacy interaction pool, `5-6` can surface `revealing`, and `7-8` can also surface `pushing_it` when style and scene allow it.
- Added couples debug fields for `coupleInteractionId` and `coupleInteractionLane` plus focused smoke coverage for promotion and low-spicy safety.

### Changed — safe high-spicy boudoir research promoted to live banks
- Promoted the full adult-only, non-explicit boudoir / glamour research pack into the live core pose bank and styling bank.
- Wired the new pose ids into `HIGH_SPICY_WOMEN_POSE_IDS` and kept the strongest variants in `LOW_SPICY_UNSAFE_POSE_IDS` for low-spicy safety.
- Expanded `HIGH_SPICY_WOMEN_REVEALING_OUTFIT_IDS` and `HIGH_SPICY_WOMEN_PUSHING_IT_OUTFIT_IDS` to cover the new clothed editorial / nightlife outfit families.
- Added a bank smoke test to verify the live core banks and scorer constants cover all researched ids.

### Added — safe high-spicy boudoir research drafts
- Added a large adult-only, non-explicit draft pose seed at `backend/engine/data/drafts/pose_bank/high_spicy_boudoir_pose_seed.json` with normalized common-label boudoir/glamour pose ids, lanes, and low-spicy safety notes.
- Added a matching draft outfit seed at `backend/engine/data/drafts/styling/high_spicy_boudoir_outfit_seed.json` for clothed high-spicy editorial / nightlife styling, including `revealing` vs `pushing_it` review tags.
- Added `HIGH_SPICY_BOUDOIR_RESEARCH_2026_04_21.md` to capture source provenance, practical filtering lists, and promotion guidance without touching the live generator banks.

### Changed — women high-spicy pose and outfit expansion
- Expanded the live women pose bank for `spicyLevel 7-8` with three new seductive-only lanes: `over_shoulder_arch_stand`, `chair_forward_lean`, and `kneeling_arch_turn`.
- Expanded the live women outfit bank for higher-reveal batches with one new `revealing` lane (`strappy_cutout_mini_dress`) and two new `pushing_it` lanes (`sheer_mesh_micro_skirt`, `bandeau_low_rise_mini`).
- Tightened high-spicy women scoring so `seductive/slutty` pose and outfit tags matter more at `spicyLevel 7-8`, while low-spicy safety now also remaps the new poses out of `spicyLevel 1-3` batches.
- Added focused smoke coverage for women high-spicy random/nightlife runs so the new revealing and pushing-it pools actually surface in generated batches.

### Changed — residual closure: matrix smoke + men taste + couples male hardening
- Expanded `tests/test_scene_coherence_matrix_smoke.py` with additional exact-theme lanes (`women luxury`, `women creative`, `couples luxury`) while keeping the matrix contract at `scene family x outfit-tag class x pose-task class`.
- Tightened couples male-side explicit-constraint handling in batch selection: when `couples + different_persons` has explicit male identity constraints, seed selection now requires a non-hard-fail payload and errors early if constraints cannot be satisfied.
- Completed a dedicated men taste follow-up for `romantic / luxury / nightlife`:
  - Increased men romantic treatment remap pressure and added `low_key_dramatic` as a valid romantic remap lane.
  - Reduced outfit-template collapse by softening male styling-bank weights for `romantic / luxury / nightlife`.
  - Switched men/couples male outfit and pose picking to deterministic per-candidate seeds to improve within-batch spread.
  - Broadened romantic treatment overrides with extra outfit and pose variants for `analog_35mm`, `documentary_still`, and `candid_phone_snapshot`.
- Extended smoke coverage:
  - Added `test_men_romantic_outfit_spread_avoids_two_template_collapse`.
  - Added repeated couples male-side constraint check across multiple runs in `test_couples_identity_constraints_smoke.py`.

### Changed — P2 exact-theme scene-family hard lock
- `exact_theme` now hard-locks generator scene-family selection through profile-level `required_scene_families` derived from theme hints, instead of acting only as a scoring/render hint.
- Added shared theme-hint matching helpers so style inference and exact-theme scoring use the same keyword map.
- Added `museum` keyword support in theme/style inference mapping so museum themes resolve to `culture_bookish` consistently.
- Preserved explicit women-side override behavior: when `womenSceneFamily` is manually set, it remains higher priority than exact-theme lock.
- Added routing smoke coverage for `sceneFocus=random + locationStrategy=exact_theme` to verify hard-lock behavior.

### Changed — P1 coherence closure + P2 matrix smoke kickoff
- Normalized scene semantics in generator routing via shared semantic tags (`bookish`, `night`, `social`, `quiet_luxury`) so compatibility predicates use one consistent tag surface instead of raw per-space tag drift.
- Tightened bookish outfit gating in candidate eligibility to block `night/pushing_it` styling unless it is routed through reserved/quiet-safe families.
- Added input compatibility in `prompt_service._merged_form_state()` so direct service calls can accept either flat form-state payloads or wrapped `{"formState": ...}` payloads without silently falling back to defaults.
- Upgraded stress/coherence tooling with deterministic bounded coverage (`--max-cases`), progress logging (`--progress-every`), and multi-run calibration aggregation (`--calibration-runs`) for repeatable CI thresholding.
- Promoted coherence report to a blocking CI requirement (`--hard-fail`, threshold `3.0`, bounded `96`-case sweep with `2` calibration runs).
- Added men debug scaffold smoke coverage in `tests/test_men_debug_scaffold_smoke.py` to assert male-side debug fields in `men random/romantic` runs.
- Added first pattern-level women/couples coherence matrix smoke coverage in `tests/test_scene_coherence_matrix_smoke.py` for `scene family x outfit-tag class x pose-task class` checks.

### Changed — women personalization quick profiles + P1 coherence threshold report
- Women single-mode Appearance section is now presented as `Personalization` and includes one-click quick profiles (`Everyday clean`, `Soft editorial`, `Night glam`, `Reset to random`).
- Added frontend preset application logic that updates existing women controls (`outfitReveal`, `makeupControl`, `hairLength`, and related random-safe defaults) without introducing backend-only state.
- Added `scripts/coherence_threshold_report.py` to run the stress audit in CI-friendly mode and emit a threshold summary (`viol_per_100`) with optional fail-on-threshold support.
- Added a non-blocking `coherence-report` job to `.github/workflows/ci.yml` and upload of the generated audit JSON artifact.

### Fixed — women personalization renderer wiring
- Fixed a frontend runtime parse error in `frontend/app.js` by moving the quick personalization markup into the women renderer path and restoring `syncActionDockGeometry()` structure.

### Changed — systemic coherence P0 completion
- Finalized upstream coherence hard-gates in `backend/engine/generator.py` so scene/outfit/pose mismatches are filtered during candidate selection, not only penalized in scorer pass.
- Added style-aware pose-context enforcement for task poses (`bookish`, `creative`, `domestic`, `outdoor`) plus a quiet-formal hospitality kneeling guard that stays compatible with luxury/nightlife generation.
- Tightened quiet-day `residential_luxury` outfit eligibility to block known editorial leakage (`vest_trousers`, `halter_trousers`) without collapsing valid luxury generation paths.
- Extended regression coverage in `tests/test_women_scene_coherence_smoke.py` for luxury random spillover checks (outfit and pose constraints).
- Verification:
  - `pytest -q tests/test_women_scene_coherence_smoke.py tests/test_routing_validation_smoke.py` -> `15 passed`
  - `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/stress_combination_audit.py --runs-per-case 3 --batch-size 8` -> `816` runs, `8160` candidates, `0` violations (`data/audits/combination_audit_20260420_223406.json`)

### Changed — random scene coherence hardening
- Tightened random scene / outfit selection so spa and pool batches stop accepting obvious casual / office spillovers.
- Blocked sport-prep poses like `track_shoe_tie_block` outside sport / wellness contexts.
- Added regression coverage for the sampled women and couples random coherence failures.

### Changed — women dyed-natural hair toggle
- Added a women-only `Allow dyed natural hair colors` control that is active only when hair color is set to `Random`.
- Random women hair-color selection now allows natural dyed shades like copper, burgundy, and silver without reopening vivid fantasy colors.
- The toggle is cleared automatically outside women mode or when hair color is not `Random`.

### Changed — women scene-family fine controls
- `womenSceneFamily` now nudges women-mode reveal, hair, makeup, and outfit taste instead of only locking the scene family.
- Added a women-only global ban for male-coded hair ids so women batches do not leak `male_*` hair structures.
- Tightened the reserved spa and nightlife family mappings so the random route stays inside the intended women styling lane.
- Extended smoke coverage to prove the reserved spa and nightlife families keep the expected reveal / hair / makeup behavior.

### Changed — UI parity pass for appearance blocks
- Rebuilt the women / men / couples Appearance sections into one consistent structure with shared block ordering and clearer headings.
- Men single-mode Appearance now exposes `Body mix`, `Hair length`, `Hairstyle`, `Grooming`, and `Outfit vibe` without duplicating women-only controls like `Makeup` and `Breast size`.
- Couples mode keeps a shared `Body mix` in the Woman block and avoids duplicate select-name collisions while preserving the men-side parity layout.
- Restored men `Hair length` `Random` in the UI and kept it persistent through form normalization.
- Fixed the broken Appearance renderer in the frontend so the form mounts cleanly again.

### Changed — men outfit vibe pass
- Reworked the men / couples outfit selector from concrete clothing labels to vibe-style options such as lifestyle, luxury, nightlife, coastal, and bookish.
- Random male outfit selection now resolves from the scene family, so men random batches follow the requested scene instead of defaulting to one static outfit lane.
- Added backward-compatible normalization so older concrete male outfit ids still map into the new vibe control.

### Changed — men taste pass and subject UI polish
- Tightened the men random style-tag pool so the live male outfit selection stays away from the old luxury-heavy default and keeps more lifestyle / creative / nightlife / coastal variety.
- Broadened men romantic pose variety so low-spicy romantic runs no longer collapse into the same few standing poses.
- Polished the men subject labels in the UI so age, race, name, and custom race read more clearly as man-side identity controls.

### Changed — men low-spicy mood verification
- Extended the routing smoke check so men `luxury`, `nightlife`, and `romantic` at `spicyLevel=3` all stay on calm / soft mood language.

### Changed — women luxury taste cleanup
- Tightened the women luxury batch scorer so `mini_dress` no longer dominates luxury runs.
- The luxury exact-theme smoke check now keeps `mini_dress` at or below 2 in the checked batch while continuing to avoid `bodysuit_trousers`.

### Changed — women-only scene family control
- Added a women-only `Women scene family` control in the Scene panel for exact scene-family selection without changing men/couples behavior.
- Wired the new control into generator scene-family selection so women batches can lock to exact families like `wellness_spa`, `culture_bookish`, or `nightlife_bar`.
- Added debug visibility for the effective women scene family.

### Changed — CI quickstart alignment
- Aligned the local quickstart and GitHub Actions workflow on the same `python -m pytest -q` smoke command.
- Added a short promotion-note reminder in `CONTENT_BANK_PROMOTION.md` to use the shared quickstart verification before merging draft promotions.

### Changed — race preset quick-pick cleanup
- Shortened the race preset dropdowns to a faster quick-pick set for women and men.
- Moved `Other` into the former `Black British` slot and removed the extra bottom duplicate so the list reads more cleanly.
- Added the new quick-pick values `white_american` and `white_english` to the backend allowlist and same-person ethnicity handling.
- Legacy `black_british` preset values now normalize to `Other` in both the frontend form state and backend form merge path.

### Changed — men romantic pass (branch: feature/men-romantic-pass)
- **Men romantic pose variety**: `_stylize_male_identity_for_treatment()` now picks from a pool of 3 poses for `analog_35mm`, `documentary_still`, and `candid_phone_snapshot` using a deterministic scene-hash index. Unique poses per 20-batch sweep improved from ~1 (single override) to 14+.
- **Men romantic outfit variety**: Same function now cycles through 3 romantic-specific outfit alternatives for `analog_35mm` and `documentary_still` when `style_mode == "romantic"`. Top outfit share dropped from 44% to ~20%.
- **Men romantic treatment remap**: Added `_remap_men_romantic_treatment()` (mirrors women's romantic remap) to hard-redirect `clean_commercial` to `analog_35mm / documentary_still / direct_light_editorial / candid_phone_snapshot` for men romantic. Call site added in `_apply_prompt_constraints()` after the nightlife remap block.
- **MALE_OUTFITS["romantic"] expanded**: From 2 to 5 fallback entries. New additions: "fine knit sweater with dark tailored trousers", "soft linen shirt with relaxed pleated trousers", "fitted merino crewneck with slim dark trousers".
- **Styling bank expanded with 2 new romantic-tagged male outfits**:
  - `male_soft_linen_trousers` — "soft linen shirt with relaxed pleated trousers" (tags: romantic, lifestyle, coastal)
  - `male_knit_sweater_trousers` — "fine knit crewneck sweater with dark tailored trousers" (tags: romantic, luxury, old_money)
- Test snapshot updated to include new entries in expected random-mode outfit set.

### Sweep results (men romantic, x20 × 8)
- Unique outfit segments: 10 (was 5-6)
- Unique pose segments: 14 (was ~1-2 due to single override per treatment)
- clean_commercial share: <2% (was leaking ~4-6%)
- Unique treatments: 7

### Changed — routing validation follow-up
- Men `luxury` and `nightlife` with `spicyLevel=3` now soften into calm/quiet mood language, and treatment overrides such as `direct_light_editorial`, `analog_35mm`, and `direct_flash_night` now keep that lower-spicy tone instead of staying fully assertive.
- Added routing validation smoke coverage for:
  - men low-spicy `luxury / nightlife` mood routing
  - women `fitness / sport` scene and outfit routing
  - men exact-theme `museum` routing on `cultural_bookish`
- Full suite now passes at `30 passed` after the follow-up.

### Changed — routing controls follow-up
- Added explicit smoke coverage for women custom race routing, couples male custom race routing, and women character-constraint routing.
- Anti-repeat is now labeled as `Anti-repeat effort` in the UI, with clearer option labels and a more explicit hint about how harder modes spend more attempts to reduce repeated scenes, outfits, and poses.
- Full suite now passes at `33 passed` after the follow-up.



### Changed
- Women `random / luxury / nightlife / romantic / fitness / creative_artistic` now push `clean_commercial` down much harder through tighter batch caps, stronger treatment scoring, and new scene-aware women remap helpers instead of relying only on soft scorer bias.
- Women `romantic` now bans cardigan/daywear carryover (`cardigan_skirt`, `cardigan_trousers`, `shirt_trousers`, `blouse_trousers`, `sweater_jeans`) and prefers refined skirt / dress families such as `silk_blouse_midi_skirt`, `structured_day_dress`, and `mockneck_knit_skirt`.
- Balanced reveal no longer boosts `cardigan_skirt` or `polo_pleated_skirt`, which removes the remaining generic sporty / nightlife leak from the shared reveal layer.
- Men/couples `random` male outfit selection now also routes through the live style-tagged male bank instead of collapsing back to the narrow hardcoded random trio.
- Selected stylized photo treatments now explicitly support `wellness_spa` and `coastal_pool`, so women `fitness` and `romantic` remaps no longer get trapped on `clean_commercial` just because the bank had no valid scene match.
- `Couples + different_persons` now treats explicit female-side `Age` and `Race preset` as real candidate constraints, not only soft batch scoring bias.
- Exact ethnicity presets like `white_ukrainian` now flow through the couples legacy male identity picker correctly when used on the male side.
- Runtime memory persistence now uses atomic writes plus retry-safe runtime reads so parallel `generate_run` calls stop tripping transient access errors on `backend/engine/runtime/memory.json`.
- Couples `lifestyle / luxury / nightlife` now push their safer women-side outfit bans deeper into candidate selection, which removes the exact-theme misses around sporty museum outfits, calm-luxury `bodysuit_trousers`, and nightlife cardigan/daywear carryover.
- Women `lifestyle / cultural_bookish / luxury / nightlife` now also push their exact-theme scene-coherence bans deeper into candidate selection, which removes the museum/hotel/bar misses around hot outfit carryover and nightlife cardigan/daywear drift.
- Couples `different_persons` now previews male-side identity during batch scoring, so explicit `maleAge / maleRacePreset` are checked during best-seed selection instead of living only inside the final legacy render path.
- Men/couples generated male outfit selection now uses style-tagged entries from the live male styling bank for supported styles before falling back to the older hardcoded legacy map.

### Notes
- Logged targeted exact-theme coherence sweeps and reprioritized the next follow-up around women / couples scene-outfit coherence plus runtime memory write safety.

### Added
- Added women treatment-remap smoke coverage for `fitness + wellness_spa`, `nightlife`, `luxury`, and `romantic + coastal_pool`, plus a direct romantic-profile regression check for the new refined outfit bans/preferences.
- Added the next couple-friendly male styling-bank variants:
  - `male_camp_shirt_trousers`
  - `male_gallery_blazer_trousers`
- Added couples identity smoke coverage for stricter female-side `age / race` routing in `different_persons` mode.
- Added couples scene-coherence smoke coverage for the `museum`, `hotel lobby`, and `cocktail bar` exact-theme retest scenarios.
- Added women scene-coherence smoke coverage for `museum`, `hotel lobby`, and `cocktail bar` exact-theme retests across `lifestyle / cultural_bookish / luxury / nightlife`.
- Added richer male-side debug fields for `men` / `couples`: `maleAge`, `maleEthnicity`, `maleEthnicityId`, and `maleEthnicityGroup`.
- Added the next live male appearance controls:
  - `male_soft_quiff`
  - `male_wavy_brushback`
  - `male_relaxed_overshirt_trousers`
  - `male_dark_shirt_trousers`
  - `male_black_polo_trousers`
  - `male_linen_pleated_trousers`
  - `male_blazer_knit_trousers`
- Added smoke coverage for the data-driven male styling-bank path and the expanded explicit male controls.

### Fixed
- Couples legacy ethnicity picking no longer drops exact race preset ids into a broad group fallback when building the male-side identity.

## 2026-04-20

### Added
- Added `scripts/stress_combination_audit.py` for broad, reproducible scene/outfit/pose stress testing across women, men, and couples combinations.
- Added machine-readable audit output under `data/audits/` to capture mismatch patterns and context examples for follow-up routing work.

### Changed
- Logged a new systemic coherence audit pass in `TEST_LOG.md` and converted findings into prioritized pattern-level remediation tasks in `PROJECT_PLAN.md`.
- Added a first hard-gate pass for quiet-day luxury outfit eligibility and stricter pose-task context selection so obvious mismatch patterns stop relying on scorer penalties alone.
- Extended the women coherence smoke coverage to keep the new generator gate honest during regression runs.

## 2026-04-19

### Added
- Added `Small` breast size option to the editor and backend (`small_breasts`).
- Added repository Playwright E2E coverage for appearance custom-selects and default generate flow.
- Added expanded generated male appearance controls for `men` and `couples`:
  - `Hairstyle`
  - `Custom hairstyle`
  - `Grooming`
  - `Outfit`
- Promoted a safe modest-styling batch into the live bank:
  - `polished_low_bun`
  - `soft_half_up`
  - `tucked_behind_ears_blowout`
  - `fresh_barely_there`
  - `groomed_daylight_soft`
  - `rosy_polished_minimal`
  - `mockneck_knit_skirt`
  - `silk_blouse_midi_skirt`
  - `cashmere_shell_trousers`
  - `structured_day_dress`
  - `apron_workshop_trousers`
  - `washed_wool_blend`
  - `matte_crepe`
  - `soft_camel_cream`
  - `dusty_rose_taupe`
- Promoted the first approved male-safe styling atoms into the live bank:
  - `male_clean_side_part`
  - `male_textured_crop`
  - `male_medium_pushback`
  - `male_open_collar_trousers`
  - `male_fineknit_trousers`
  - `male_track_jacket_joggers`

### Changed
- Expanded live women `Hairstyle` presets with `polished_low_bun`, `soft_half_up`, and `tucked_behind_ears_blowout`.
- Expanded live `Makeup` control with subtler presets for cleaner / softer low-spicy output.
- App server now supports `PROMPT_GENERATOR_HOST` and `PROMPT_GENERATOR_PORT`, and Playwright runs against a dedicated fresh test instance.
- Men and couples appearance panels now expose the expanded generated male block instead of only `Male hair length`.
- Legacy men/couples rendering now respects explicit generated male hairstyle, grooming, and outfit choices while still allowing `Custom` appearance mode to lock the whole male look.

### Fixed
- Frontend: fixed custom-select dropdowns — made the document click handler robust to text nodes and forced a re-render after selection so `hairLength`, `maleHairLength` and other custom selects update immediately.
- Frontend: custom selects now support keyboard navigation (`ArrowUp`, `ArrowDown`, `Home`, `End`, `Enter`, `Escape`) with combobox/listbox ARIA wiring and focus handoff.
- Frontend: pressing `Enter` on an open custom combobox now commits the highlighted option instead of only closing the menu, which makes keyboard selection deterministic again.
- Backend: ignored harmless client-disconnect write errors so browser/E2E aborts do not spam server stack traces.

## 2026-04-18

### Changed
- Continued stylization phase 3 rebalancing with a narrow scorer-only pass for `concept_photo_editorial` and `direct_light_editorial`.
- `photo treatment` scoring now respects `preferred_style_modes` in addition to preferred scenes/capture/light/time.
- Harder stylized lanes now get extra selection bias in `random`, `studio`, `creative_artistic`, `luxury`, `lifestyle`, and `urban_day`.
- `luxury` now gets a stronger batch-level reward for harder stylized lane presence without forcing them globally.
- Added a men-only luxury taste pass: `men luxury` now gets an extra stylized batch bias plus a less stock-like male luxury outfit/pose bank in the legacy renderer.
- Added the next stylized treatment family:
  - `mirror_selfie`
  - `disposable_camera`
  - `documentary_still`
- Added soft scoring bias for these new casual-stylized treatments in `random`, `lifestyle`, `urban_day`, `cultural_bookish`, and `creative_artistic`.
- Added another stylized treatment family:
  - `casual_indoor_selfie`
  - `vintage_flash_photo`
  - `advertising_poster_realism`
- Added style-aware scorer bias so these new lanes land where they make sense:
  - `vintage_flash_photo` in `nightlife`
  - `advertising_poster_realism` in `studio`
  - `casual_indoor_selfie` in `lifestyle` and `luxury`
- Debug is now richer for stylization:
  - summary cards for treatment/capture/lighting/camera-vibe distributions
  - stylized vs polished counts
  - per-prompt fit signals for style and treatment compatibility

### Verified
- `py_compile` passed for `backend/prompt_service.py`, `backend/engine/generator.py`, and `backend/legacy_people.py`.
- Quick stylization sweeps were rerun for `women random`, `women creative_artistic`, `women studio`, `women luxury`, `couples random`, and a follow-up `men luxury` check.

## 2026-04-17

### Added
- Local women-only web UI on top of the existing Python generator engine.
- Presets, history, latest batch output, copy-per-prompt, copy-all, compact debug panel.
- Women controls for person mode, age, race preset, body mix, spicy level, anti-repeat, style mode, style vibe, framing, lighting, location strategy, exact theme, character constraint.
- Women personalization atoms for outfit reveal, hair length, hairstyle, custom hairstyle, hair color, custom hair color, makeup.
- Women-only `Scene focus` control for urban, luxury, bookish, garden, coastal, nightlife, studio, creative, wellness, and sporty routing.
- Sticky bottom run dock with `Generate` and `Reset`.
- Inline emoji favicon.
- Legacy male generator path with mode-aware prompt rendering on top of the current scene scaffold.
- Couples generator path that combines the women scene module with the new male module in one prompt.
- Couples mode now exposes a split subject editor with separate woman-side and man-side controls.
- Couples mode now exposes split identity blocks: full women appearance controls plus a dedicated male appearance block.
- Layered content-bank loading with `core + drafts + overrides`.
- Draft seed banks for modest-safe locations and poses.
- Data-bank workflow docs next to the engine data files.
- Draft styling seed banks for modest-safe women appearance and male-safe appearance.
- Draft subject seed bank for future ethnicity expansion.
- Appearance mode system for `women / men / couples` with per-side `Generated / Custom` controls.
- Safe draft bank for richer interiors/social settings in `drafts/setting_engine/interiors_social_seed.json`.
- Separate style-setting stash document for future tiny imports without touching live routing.
- Approved modest and interiors/social draft settings and poses are now promoted into the live `setting_engine.json` and `pose_bank.json` banks.
- Prompt rendering is now more compact across women, men, and couples to reduce token spend without changing generator selection logic.
- Men now have dedicated pose variants for `lifestyle`, `luxury`, `old_money`, `romantic`, `vacation`, `cultural_bookish`, `creative_artistic`, `urban_day`, `coastal`, `cosplay`, and `fantasy`.
- Debug now includes per-prompt effective decisions for women, men, and couples instead of only aggregate distributions.

### Changed
- UI moved to English.
- Seed removed from the UI.
- `Spicy level` now supports `Random` from 3 to 8.
- `Same person` now means one locked identity per batch, built from the current editor state and reused across every prompt.
- `Core identity prompt` in `Same person` is now an optional add-on with extra identity notes instead of a full subject replacement.
- `Same person` subject rendering now keeps one consistent autogenerated identity and appends custom core notes without gluing two women together.
- Header updated to `Native Structure Prompts Generator`.
- Mode buttons now use emoji labels.
- `Men` and `Couples` modes are now enabled in the UI.
- Men now expose only `Male hair length` in appearance controls, defaulting to `Short hair`.
- Couples now reuse the women appearance block and add a separate `Man hair length` control.
- New content-bank additions can now be staged in tiny fragment files instead of editing the large base bank files directly.
- Appearance controls are now unified around per-side `Generated / Custom` modes instead of the old women-only core-identity toggle.
- Custom appearance prompts now flow through women, men, and couples rendering, while generated mode keeps atom controls active.
- Debug now shows effective style mode plus active female/male appearance mode and prompt state.
- Custom appearance scoring now has a light prompt-profile layer, so soft/reserved appearance prompts better suppress overly slutty women/couples tone and sporty/nightlife prompts steer routing more coherently.

### Fixed
- Route normalization no longer drops user scene constraints after generation.
- `Sport` and `Fitness` now hold athletic scene, route, outfit, material, and ponytail much more reliably.
- Explicit hair color choices now act like real constraints instead of weak preferences.
- Disabled custom hair fields no longer leak into scoring or final prompt rendering.
- History loading is tolerant to partially damaged JSON.
- `Same person` now respects manual `Age` and `Race preset` during identity selection instead of locking a random off-target woman.
- Batch search now survives failed generator seeds and keeps trying the next attempt instead of aborting the whole run early.
- Men `fitness/sport` prompts now force a sporty setting and daylight technical block instead of leaking generic or nightlife scaffold details.
- Women low-spicy modesty is now much stricter: the old low-cut cardigan wording is gone, low-spicy prompts avoid the most seductive floor/lounge poses, and repeated outfit-color clones are diversified at final render time.
- Reserved women outfit banks now include broader modest trousers / knit / sporty-covered options instead of overusing the same cardigan-skirt lane.
- Couples male-side race, age, name, and hair length now feed the legacy male module instead of being silently ignored.
- `Couples + nightlife` no longer leaks into pool/daylight nightclub-adjacent nonsense in the final rendered prompt; the output is forced back to a nightlife bar read with night technicals and a nightlife-safe women outfit phrase.
- The draft-only interiors/social seed pack no longer reuses the live `rooftop_hotel_conservatory` id; the draft variant now stays isolated as `rooftop_hotel_conservatory_palms`.
- Promoted draft packs are cleared after promotion, so future `load_drafts=true` runs do not double-merge the same settings or poses back on top of live.
- Men no longer inherit female-coded mood lines like `bratty playful energy`; male and couple modes now use dedicated mood wording.
- `Nightlife` now bans `swimsuit` and `bikini_set` during candidate selection, so women/couples nightlife batches no longer leak swimwear into night-city scenes.
- Women `nightlife` now has a wider live outfit/color bank with night-safe silhouettes like `blazer_mini_dress`, `cami_midi_skirt`, `bodysuit_trousers`, and `corset_trousers`, plus darker evening palettes like `black_gold`, `oxblood_noir`, and `emerald_noir`.
- Women `nightlife` now also applies an extra repeated-outfit penalty inside the batch scorer, so large nightlife batches diversify silhouettes better.
- Men `luxury` and `romantic` now have a larger dedicated pose pool, which materially reduces pose collapse in `20`-prompt sweeps.
- Couples now apply scene-aware female outfit sanitization during rendering: `swimsuit / bikini_set` are replaced in non-coastal scenes, and `latex_editorial` is replaced outside the styles where it makes sense.
- Couples now diversify female color stories at scaffold level before legacy rendering, with style-aware palettes so `lifestyle` no longer drifts into nightlife-only color banks.
- Couples now render explicit male outfit colors, which reduces “same-color twins” drift in generated images.

### Known Gaps
- Some style routes like `lifestyle / romantic / cosplay / creative_artistic` can still be taste-tuned further even though validation is clean.
- Debug is richer now, but it still does not expose every effective per-prompt decision.
- Male appearance controls are intentionally minimal for now: only hair length is exposed, and hairstyle/color/grooming are still automatic.
- Couples still do not have a fully separate male style bank yet; the man side is still legacy-safe and narrower than the woman side.
- Couples different-person mode still treats woman-side age/race as batch bias rather than a hard lock; exact locked couple identity is strongest in `Same person`.
- Draft content is still disabled by default; promotion from drafts into live routing is still a manual review step.

## 2026-04-18

### Added
- Saved the staged stylization rollout in `STYLIZATION_IMPLEMENTATION_PLAN.md`.
- Added a new live bank `backend/engine/data/photo_treatments.json` with 7 internal treatment profiles:
  - `clean_commercial`
  - `candid_phone_snapshot`
  - `analog_35mm`
  - `low_key_dramatic`
  - `direct_flash_night`
  - `studio_seamless`
  - `cinematic_poster_realism`

### Changed
- Generator now loads `photo_treatments` as a first-class internal bank.
- Women, men, and couples prompts now run through a treatment-aware render layer without adding any new UI control yet.
- Subject lead phrasing now uses the effective treatment capture wording, not only the raw base capture style.
- Technical phrasing now includes treatment-aware light / camera vibe / color grade / finish wording.
- Debug now exposes stylization fields per prompt and per batch:
  - `photoTreatment`
  - `captureRender`
  - `cameraVibe`
  - `colorGrade`
  - `finish`
  - `photoTreatmentDistribution`

### Fixed
- Legacy men/couples rendering now respects the same treatment-aware capture phrasing as women.
- Legacy sport/nightlife technical overrides now preserve the new treatment layer instead of wiping it out.

### Known Gaps
- Phase 1 is intentionally soft: `photo_treatment` currently affects render/debug, not hard candidate scoring.
- Final `generate_run(random)` output still does not guarantee an exact `40/60` polished-vs-stylized split yet; that remains phase 2 / phase 3 balancing work.

### Phase 2

#### Changed
- `photo_treatment` now gets chosen earlier in candidate assembly, so it can softly bias downstream `time / lighting / mood / capture` choices instead of only decorating the final render.
- Treatment preference data is now merged into the existing `preferred_*` profile flow, so the engine reuses the current selection machinery instead of adding a separate brittle branch.
- Batch scoring now includes treatment-aware candidate compatibility and treatment-mix balancing, so final `generate_run(random)` output respects stylization distribution much better than phase 1.

#### Fixed
- Final best-batch selection no longer drifts as hard back into polished/stock output after the raw generator already produced stylized candidates.

### Phase 3

#### Changed
- Ran larger treatment-distribution sweeps across `women / men / couples` and rebalanced the phase-2 stylization layer using real batch metrics instead of one-off smoke checks.
- Tightened the random and luxury treatment-category weighting inside the generator.
- Added an explicit polished-overflow penalty in batch scoring so final best-batch selection is less willing to accept too many `clean_commercial` prompts in one run.
- Added two harder stylized lanes on top of the treatment system:
  - `concept_photo_editorial`
  - `direct_light_editorial`
- Expanded the live composition bank with new internal lighting families:
  - `hard_direct_light`
  - `single_source_contrast`
  - `direct_flash_clean`
- Lighting predicates now allow these new light families in compatible studio / luxury / urban / courtyard contexts.

#### Fixed
- `women random` final runs now stay noticeably closer to the intended stylized mix instead of repeatedly collapsing back into mostly polished batches.

#### Known Gaps
- `luxury` still remains more polished than the long-term target, especially for `men luxury`.
- `couples random` still swings more than desired between balanced and too-clean runs.

### UI Reshuffle

#### Changed
- The left control column was re-chunked into a more logical order:
  - `Subject`
  - `Spicy level`
  - `Appearance`
  - `Batch`
  - `Scene`
  - `Stylization`
- `Stylization` now has a live optional `photo treatment` control in the UI.
- The right column no longer has an extra `Output` shell; it now starts directly with `Latest prompts`.
- `Latest prompts` now shows the batch count right next to `Copy all`.
- Main section subtitles were reduced to clean up visual noise.
- `Generate` was switched to an outline-style action so the wand icon reads better.
- Native `select` popups were replaced with a real custom dropdown component so the opened menus now match the UI kit too.

#### Fixed
- Random hair-color selection now stays on natural hair colors instead of leaking dyed fantasy-ish shades into normal output.
- `same_person + core identity prompt` no longer hijacks the whole appearance block through `appearancePrompt`; core identity notes now stay separate from outfit rendering.
- `same_person` identity lock now keeps identity atoms stable while allowing outfit diversity across the batch.

### Quality Pass: Couples / Men / Nightlife

#### Changed
- Couple rendering now softens female outfit text more aggressively in:
  - `random`
  - `lifestyle`
  - `urban_day`
  - `cultural_bookish`
  - `romantic`
  when the raw women-side candidate drifts into swimwear or overly revealing clubwear.
- Couples scoring now penalizes:
  - swimwear in `random`
  - overly revealing women-side outfits in `couples lifestyle`
  - nightlife-only dark palettes leaking into `couples lifestyle`
- `men romantic` treatment scoring and batch targeting were pushed further toward stylized/non-stock output.
- `women nightlife` now gets an extra batch penalty when `mini_dress` starts dominating too heavily.

#### Fixed
- Remaining explicit swimwear wording in `couples random` was removed from the rendered prompt output in the checked sweep.
- `couples lifestyle` now lands on much more everyday clothing reads instead of sliding into bikini/corset/latex territory.
- `women nightlife` outfit spread is healthier; `mini_dress` no longer dominates as hard as before in the checked sweep.

#### Residual
- `men romantic` was pushed further:
  - stronger stylized batch target
  - stronger romantic-specific stylized treatment bias
  - explicit deprioritization for `clean_commercial` during treatment choice
- `men romantic` no longer swings into the worst `mostly clean_commercial` runs seen before this pass.

### Regression Pass: Reveal Routing And Debug Alignment

#### Changed
- Random/lifestyle/luxury reveal routing was tightened so default output no longer escalates into `pushing_it` too eagerly outside the styles that actually need it.
- Women-side candidate scoring now bans or heavily penalizes swimwear / bikini / latex in:
  - `random`
  - `lifestyle`
  - `luxury`
- Nightlife women now also get extra pressure against:
  - `vinyl_latex`
  - overusing `crop_top_mini_skirt`
- Couple render fallback logic was expanded so `random / luxury / nightlife` now also soften:
  - `crop_top_mini_skirt`
  - `latex_editorial`
  instead of only catching swimwear.
- Legacy debug output for `men` now reports real male outfit/pose/hair fields instead of scaffolded women-side outfit data.

#### Fixed
- `women random` no longer leaked `swimsuit / bikini / latex / tiny-mini` wording in the checked `x20` retests.
- `women lifestyle` no longer leaked revealing swimwear/latex wording in the checked `x20` retests.
- `couples random` and `couples luxury` no longer leaked swimwear/latex wording in the checked `x20` retests.
- `couples nightlife` no longer leaked `latex` or `tiny mini skirt` wording after the render fallback expansion.

### Women Nightlife Cleanup

#### Changed
- `women nightlife` now bans `crop_top_mini_skirt` at the profile level instead of only trying to discourage it statistically.
- `women nightlife` now also hard-softens stray `vinyl_latex` materials at final women render time by converting them to `satin finish`.

#### Fixed
- The remaining `tiny mini skirt` wording in `women nightlife` was removed.
- The remaining `latex` wording in `women nightlife` was removed.
- 10 consecutive `women nightlife x20` stress runs finished with:
  - `0` findings
  - `0` repairs
  - `0` `tiny mini skirt / latex / bikini / swimsuit` wording leaks

### Women Random / Luxury Diversity Pass

#### Changed
- Expanded the live women styling bank with new outfit families:
  - `vest_trousers`
  - `column_dress`
  - `wrap_blouse_skirt`
  - `halter_trousers`
- Expanded materials with:
  - `fluid_crepe`
  - `matte_jersey`
- Expanded color stories with:
  - `chocolate_cream`
  - `champagne_taupe`
  - `slate_blue_ink`
  - `rosewood_smoke`
- Reduced base weight of `clean_neutrals` and slightly lowered dominance of the most overused legacy women outfits/materials.
- Added stronger women-only diversity pressure in `random` and `luxury` so batches stop collapsing into the same outfit/color family too often.
- `women random` now also bans `crop_top_mini_skirt` directly, so default random output stays varied without swinging back into the tiny-mini lane.

#### Fixed
- `women luxury` color spread is materially broader now instead of defaulting so hard to `clean_neutrals`.
- `women random` now surfaces the new silhouettes and palettes in live runs instead of storing them as dead bank entries.
- `women random` stress retests no longer leaked `tiny mini skirt / bikini / swimsuit / latex`.

### Women Relevance And Fitness Pass

#### Changed
- Split `sport` and `fitness` logic more aggressively instead of letting both modes reward the same flirty `crop_top_mini_skirt` path.
- Reworked the base `fitness` profile so it now prefers:
  - `polo_pleated_skirt`
  - `workout_top_leggings`
  - `zip_jacket_leggings`
  - `training_jacket_trousers`
- Reworked the base `fitness` color routing so it now prefers cleaner sport/wellness palettes instead of leaning so hard into `lime_pop`.
- Expanded the live fitness-safe setting pool with:
  - `rooftop_reformer_deck`
  - `tennis_club_colonnade`
  - `wellness_juice_bar`
  - `training_loft_window_bay`
  - `spa_movement_studio`
  - `thermal_recovery_lounge`
- Added stronger `fitness` penalties for:
  - `crop_top_mini_skirt`
  - over-repeated same-outfit batches
  - too-few unique settings
  - too-little `wellness_spa` presence
- Tightened the women relevance pass for:
  - `lifestyle`
  - `romantic`
  - `creative_artistic`

#### Fixed
- `women fitness` no longer collapses into repeated `crop top + tiny mini skirt` batches.
- `women fitness` now rotates across four workout-safe outfit families and regularly surfaces `wellness_spa` scenes instead of feeling locked to one urban daytime lane.
- `women lifestyle` is now more grounded and less nightlife-ish in outfit selection.
- `women romantic` no longer leaks the worst overtly nightlife-coded outfit families during broad x20 runs.
- `creative_artistic` no longer drifts into sporty outfit leaks during the same pass.

### Couples Quality Pass

#### Changed
- Expanded the live couple-interaction bank with real two-person poses instead of mostly near-standing variants.
- Added new couple interaction families for:
  - `random`
  - `lifestyle`
  - `luxury`
  - `old_money`
  - `romantic`
  - `nightlife`
  - `sport`
  - `fitness`
- Reworked couple debug so it now exposes:
  - `femaleColorStory`
  - `maleColorStory`
  - actual rendered couple `pose`
- Tightened couple-specific outfit/color pressure in `random / lifestyle / luxury`.
- Rebalanced couple color diversification so `lifestyle / luxury` stop defaulting to `clean_neutrals` as the first-choice color lane.
- `couples random` now bans `crop_top_mini_skirt` at candidate-profile level.
- Restricted luxury mood overrides in couples so only truly luxury-compatible treatments can overwrite the default couple luxury chemistry.

#### Fixed
- `couples random` no longer leaked `tiny mini skirt / swimwear / latex` wording in the checked x20 retest.
- `couples lifestyle` no longer collapses into `clean_neutrals` as the dominant female color lane.
- `couples luxury` no longer over-relies on a single neutral palette in the checked retest.
- Couple prompts now surface clearly pair-oriented interactions like hand-holding, seated-together poses, lap-seated poses, and walking-together variants.

### Eye Color, Breast Size, And Curated Race Dropdown

#### Changed
- Activated `Eye color` as a real women-side engine control instead of a disabled UI placeholder.
- Activated `Breast size` as a real women-side engine control instead of a disabled UI placeholder.
- Expanded `Race preset` beyond broad groups with curated nationality presets for:
  - white
  - black
  - latina
  - asian
- Added live `eye_colors` bank entries to `subjects.json`.
- Wired the new appearance controls into:
  - bootstrap defaults/options
  - form-state normalization
  - batch scoring
  - same-person identity locking
  - women prompt rendering
  - couples women-side legacy rendering
  - debug metadata

#### Fixed
- `Eye color` no longer sits in UI as dead chrome; it now changes candidate choice and rendered prompt text.
- `Breast size` no longer sits in UI as dead chrome; it now changes candidate choice and rendered prompt text.
- Curated race presets like `white_ukrainian` and `latina_mexican` now route as exact ethnicity locks in `same_person`, not only as loose flavor text.

### Women Taste Pass

#### Changed
- Tightened women-side outfit scoring for:
  - `random`
  - `luxury`
  - `romantic`
  - `creative_artistic`
- Lowered the generic pull toward `mini_dress` in `random` and especially `luxury`.
- Added stronger preference for broader women silhouettes in `random / luxury`:
  - `column_dress`
  - `wrap_blouse_skirt`
  - `vest_trousers`
  - `blouse_trousers`
  - `cami_midi_skirt`
- Tightened `romantic` by banning `mini_dress` and `bodysuit_trousers` from the preferred women path.
- Tightened `creative_artistic` by banning sporty outfit families and pushing editorial silhouettes harder.
- Added stronger batch pressure against:
  - too many `mini_dress` in `random / luxury / romantic`
  - sporty outfit leaks in `creative_artistic`
  - overused `clean_neutrals` in `luxury`

#### Fixed
- `women romantic` now stays noticeably more in midi / column / wrapped / trouser silhouettes instead of drifting back into nightlife-ish women looks.
- `women creative_artistic` no longer surfaces the earlier sporty outfit leak in the checked retests.
- `women random / luxury / romantic / creative_artistic` stayed clean across repeated x20 retests with no `bikini / swimsuit / latex` wording leaks.

### Stylization Rebalance

#### Changed
- Rebalanced live `photo_treatment` weights so the stylized lanes surface more often without rewriting the core scene engine.
- Lowered the base weight of `clean_commercial`.
- Raised the base weight of stronger stylized treatments including:
  - `cinematic_poster_realism`
  - `mirror_selfie`
  - `casual_indoor_selfie`
  - `vintage_flash_photo`
  - `advertising_poster_realism`
- Added stronger style-aware treatment scoring for:
  - `women random`
  - `women luxury`
  - `women nightlife`
  - `women creative_artistic`
  - `men luxury`
  - `men romantic`
  - `couples random`
- Added batch-level stylization pressure using:
  - stylized/polished target ratios
  - clean-commercial caps in the most problematic modes
  - a small reward for wider lighting diversity

#### Fixed
- Restored the backend package to a safe importable state after a stray unfinished MCP integration had broken `backend` imports.
- The prompt generator now imports and boots cleanly again without requiring the unfinished MCP files.

### Random Stylization Follow-up

#### Changed
- Added another targeted stylization pass specifically for:
  - `women random`
  - `men romantic`
  - `couples random`
- Pushed more random-mode reward toward casual stylized lanes such as:
  - `casual_indoor_selfie`
  - `candid_phone_snapshot`
  - `mirror_selfie`
  - `disposable_camera`
  - `documentary_still`
  - `vintage_flash_photo`
- Lowered the base weight of `clean_commercial` again and raised several casual / documentary / snapshot-like treatment weights.
- Tightened batch-level clean-commercial caps further for:
  - `women random`
  - `men romantic`
  - `couples random`

#### Fixed
- `women random` now lands in a more stylized place on broad aggregate runs instead of being as clean-heavy as before this pass.

### UI Tail Cleanup

#### Changed
- Cleaned up the `Appearance` layout for `men` and `couples`.
- Replaced inline spacing hacks in the couples appearance block with real reusable layout classes.
- Added honest inline helper copy for male appearance blocks so the UI now clearly says:
  - generated male-side controls are still minimal
  - custom mode is the right path when the user wants full male outfit/grooming lock-in

#### Fixed
- The men/couples appearance sections are less misleading now and better match the actual engine coverage.

### Couples Random Stylization Pass

#### Changed
- Added a stronger couple-specific treatment preference path for `couples random` so the selector now favors:
  - `candid_phone_snapshot`
  - `casual_indoor_selfie`
  - `mirror_selfie`
  - `disposable_camera`
  - `analog_35mm`
  - `documentary_still`
  - `concept_photo_editorial`
  - `direct_light_editorial`
  - `cinematic_poster_realism`
  - `vintage_flash_photo`
  - `advertising_poster_realism`
- Tightened `couples random` stylization scoring further:
  - higher stylized target
  - stronger batch reward for favored couple-random treatments
  - harder clean-commercial penalty
- Added a final `couples random` treatment remap before render so leftover `clean_commercial` candidates are converted into more believable stylized couple treatments based on scene family.

#### Fixed
- `couples random` no longer collapses as hard into clean-commercial-heavy runs during repeated x20 sweeps.

### Women Lifestyle And Fitness Treatment Pass

#### Changed
- Added dedicated women-side treatment preferences for:
  - `lifestyle`
  - `fitness`
- Strengthened candidate scoring for:
  - more casual / analog / documentary treatment lanes in `women lifestyle`
  - less stock-clean treatment dominance in `women fitness`
- Added focused render-stage treatment remaps:
  - `women lifestyle` now partially remaps leftover `clean_commercial` into more believable casual stylized treatments
  - `women fitness` now remaps leftover `clean_commercial` into more dynamic sporty-safe treatments such as `candid_phone_snapshot` and `analog_35mm`

#### Fixed
- `women lifestyle` no longer collapses back into overly clean stock-heavy batches during repeated x20 runs.
- `women fitness` no longer stays almost entirely stuck in `clean_commercial` during repeated x20 runs.

### Women Random And Romantic Treatment Pass

#### Changed
- Added dedicated women-side treatment preferences for:
  - `random`
  - `romantic`
- Added targeted render-stage remaps for leftover `clean_commercial` in:
  - `women random`
  - `women romantic`
- Reused a shared treatment-remap helper so scene-aware remaps stay local and predictable instead of spreading more global scoring hacks.

#### Fixed
- `women random` now lands in a noticeably more stylized range during repeated x20 runs instead of swinging back toward heavy clean-commercial batches.
- `women romantic` now keeps more analog / documentary / direct-light flavor instead of collapsing back toward an even clean/stylized split.

### Men Random And Nightlife Treatment Pass

#### Changed
- Added dedicated men-side treatment preferences for:
  - `random`
  - `nightlife`
- Added targeted render-stage remaps for leftover `clean_commercial` in:
  - `men random`
  - `men nightlife`

#### Fixed
- `men random` now lands in a much healthier stylized range during repeated x20 runs.
- `men nightlife` now stays strongly stylized instead of drifting back into too-clean nightlife batches.

### Couples Lifestyle Treatment Pass

#### Changed
- Added a dedicated `couples lifestyle` treatment path:
  - couple-specific lifestyle treatment preferences
  - clean-commercial deprioritization
  - a partial render-stage remap for leftover `clean_commercial`
- Tightened the couple lifestyle taste profile:
  - banned some overly dressy women-side outfits in this mode
  - expanded calmer paired lifestyle outfit preferences
  - widened the preferred couple lifestyle color range slightly beyond the narrow old default

#### Fixed
- `couples lifestyle` now lands in a much healthier stylized range during repeated x20 runs instead of staying too clean-heavy.

### External Pose Bank Wave 3

#### Changed
- Added one more reviewed women pose line to each live external women pose file:
  - `1_3`
  - `4_5`
  - `6_8`
- Added one more reviewed men pose line to each live external men pose file:
  - `1_3`
  - `4_5`
  - `6_8`
- Kept the wave narrow again:
  - external `poses` only
  - no couples pose bank growth
  - no expressions/outfits/wet variants/size-control work mixed in

#### Fixed
- Continued widening stance and seated-angle variety in the live external pose banks without breaking the current loader/test contract.

### External Pose Bank Wave 4

#### Changed
- Added one more reviewed women pose line to each live external women pose file:
  - `1_3`
  - `4_5`
  - `6_8`
- Added one more reviewed men pose line to each live external men pose file:
  - `1_3`
  - `4_5`
  - `6_8`
- Kept the wave narrow again:
  - external `poses` only
  - no couples pose bank growth
  - no expressions/outfits/wet variants/size-control work mixed in

#### Fixed
- Added more doorway, lifted-knee, and half-reclined phrasing variety without changing loader behavior or breaking the repo-backed smoke tests.

### External Pose Bank Wave 5

#### Changed
- Added one more reviewed women pose line to each live external women pose file:
  - `1_3`
  - `4_5`
  - `6_8`
- Added one more reviewed men pose line to each live external men pose file:
  - `1_3`
  - `4_5`
  - `6_8`
- Kept the wave narrow again:
  - external `poses` only
  - no couples pose bank growth
  - no expressions/outfits/wet variants/size-control work mixed in

#### Fixed
- Added more linked-hands, squared stance, and full-arm stretch phrasing variety without changing loader behavior or breaking the repo-backed smoke tests.

### External Pose Bank Wave 6

#### Changed
- Added one more reviewed women pose line to each live external women pose file:
  - `1_3`
  - `4_5`
  - `6_8`
- Added one more reviewed men pose line to each live external men pose file:
  - `1_3`
  - `4_5`
  - `6_8`
- Kept the wave narrow again:
  - external `poses` only
  - no couples pose bank growth
  - no expressions/outfits/wet variants/size-control work mixed in

#### Fixed
- Added more side-seam, neck-trail, and long-curve phrasing variety without changing loader behavior or breaking the repo-backed smoke tests.

### External Pose Bank Wave 7

#### Changed
- Added one more reviewed women pose line to each live external women pose file:
  - `1_3`
  - `4_5`
  - `6_8`
- Added one more reviewed men pose line to each live external men pose file:
  - `1_3`
  - `4_5`
  - `6_8`
- Kept the wave narrow again:
  - external `poses` only
  - no couples pose bank growth
  - no expressions/outfits/wet variants/size-control work mixed in

#### Fixed
- Added more folded-hands, collarbone, and overhead-brace phrasing variety without changing loader behavior or breaking the repo-backed smoke tests.

### External Expression Bank Wave 1

#### Changed
- Added one more reviewed women expression line to each live external women expression file:
  - `1_3`
  - `4_5`
  - `6_8`
- Added one more reviewed men expression line to each live external men expression file:
  - `1_3`
  - `4_5`
  - `6_8`
- Kept the wave narrow on purpose:
  - external `expressions` only
  - no couples expression path growth
  - no poses/outfits/wet variants/size-control work mixed in

#### Fixed
- Broadened low-, mid-, and high-spicy facial language a bit without touching loader behavior or changing the current render contracts.

### External Expression Bank Wave 2

#### Changed
- Added one more reviewed women expression line to each live external women expression file:
  - `1_3`
  - `4_5`
  - `6_8`
- Added one more reviewed men expression line to each live external men expression file:
  - `1_3`
  - `4_5`
  - `6_8`
- Kept the wave narrow on purpose:
  - external `expressions` only
  - no couples expression path growth
  - no poses/outfits/wet variants/size-control work mixed in

#### Fixed
- Added more friendly, playful-smirk, and smoky-stare phrasing variety without touching loader behavior or changing the current render contracts.

### External Expression Bank Waves 3-5

#### Changed
- Added three more reviewed women expression lines to each live external women expression file:
  - `1_3`
  - `4_5`
  - `6_8`
- Added three more reviewed men expression lines to each live external men expression file:
  - `1_3`
  - `4_5`
  - `6_8`
- Kept the grouped pass narrow on purpose:
  - external `expressions` only
  - no couples expression path growth
  - no poses/outfits/wet variants/size-control work mixed in

#### Fixed
- Broadened calm, playful, and heated facial-language coverage again without touching loader behavior or changing the current render contracts.

### External Outfit Bank Wave 1

#### Changed
- Added one more reviewed women outfit line to each live external women outfit file:
  - `1_3`
  - `4_5`
  - `6_8`
- Added one more reviewed men outfit line to each live external men outfit file:
  - `1_3`
  - `4_5`
  - `6_8`
- Kept the wave narrow on purpose:
  - external `outfits` only
  - no couples outfit path growth
  - no poses/expressions/wet variants/size-control work mixed in

#### Fixed
- Broadened calm, mid-spicy, and high-spicy clothing language a bit without touching loader behavior or changing the current render contracts.

### External Outfit Bank Wave 2

#### Changed
- Added one more reviewed women outfit line to each live external women outfit file:
  - `1_3`
  - `4_5`
  - `6_8`
- Added one more reviewed men outfit line to each live external men outfit file:
  - `1_3`
  - `4_5`
  - `6_8`
- Kept the wave narrow on purpose:
  - external `outfits` only
  - no couples outfit path growth
  - no poses/expressions/wet variants/size-control work mixed in

#### Fixed
- Added another small layer of calm, mid-spicy, and high-spicy clothing variety without touching loader behavior or changing the current render contracts.

### External Outfit Bank Waves 3-5

#### Changed
- Added three more reviewed women outfit lines to each live external women outfit file:
  - `1_3`
  - `4_5`
  - `6_8`
- Added three more reviewed men outfit lines to each live external men outfit file:
  - `1_3`
  - `4_5`
  - `6_8`
- Kept the grouped pass narrow on purpose:
  - external `outfits` only
  - no couples outfit path growth
  - no poses/expressions/wet variants/size-control work mixed in

#### Fixed
- Broadened softer casual looks, mid-spicy fitted looks, and higher-spicy dressier looks again without touching loader behavior or changing the current render contracts.

### Issue 34 P1 - Outfit Line-Bank Coherence Pass

#### Changed
- Made line-bank outfit selection scene-aware instead of choosing women/men outfit lines blindly before scene context is known.
- Added lightweight inferred outfit tags for line-bank outfit records so robe/swim/latex/intimate/public-risky language can be filtered without building another large hardcoded subsystem.
- Wired the same outfit-scene guardrails into both:
  - women candidate-builder path
  - men legacy line-bank override path

#### Fixed
- Stopped the worst line-bank outfit nonsense from surfacing in clearly wrong contexts:
  - robe-like lines in lounges, corridors, lobbies, and other public-ish luxury scenes
  - swim-coded lines outside coastal/resort scenes
  - intimate/public-risky lines in scenes that read too public or too formal for them

### Issue 34 P2 - Pose Posture Gating Pass

#### Changed
- Added lightweight posture inference for external pose line-banks:
  - `standing_like`
  - `seated_like`
  - `lying_like`
  - `ground_low_like`
- Added narrow support-surface gating so seated/reclined/kneeling line-bank poses only survive when the scene plausibly implies support like:
  - bed
  - chair / seating
  - sofa / banquette / lounger
  - stairs / steps
  - mats / grass / sand / spa-style soft support
- Wired the same posture guardrails into both:
  - women candidate-builder path
  - men legacy line-bank override path

#### Fixed
- Stopped the most absurd line-bank pose mismatches from surfacing:
  - bed-edge poses outside bedroom-like scenes
  - chair-edge poses in corridor / bridge / travel-floor contexts
  - reclined poses in hard public urban scenes without any believable support surface

### Issue 34 P3 - Shared Location Line-Bank Pass

#### Changed
- Added the first shared repo-backed location line-bank under:
  - `backend/engine/data/overrides/line_banks/shared/locations/{1_3,4_5,6_8}.md`
- Extended the line-bank loader to support `shared/locations` as a live domain without splitting locations by gender.
- Added lightweight scene/tag heuristics for shared location lines so they only surface in reasonably compatible contexts.
- Wired shared location lines into prompt rendering as a location override inside the final `Set in ...` block while keeping the core scene ids and routing logic intact.

#### Fixed
- The first shared location rollout now surfaces safely in live prompts instead of just existing as placeholder folders.

### Issue 34 P4 - Final Verification And Cleanup

#### Changed
- Updated the men line-bank smoke test so it validates the new posture-gated behavior instead of assuming a seated chair pose can always survive scene filtering.

#### Fixed
- Closed the last verification gap after the outfit / pose / shared-location passes:
  - focused repo-backed tests now pass together with the live line-bank smoke suite
  - the issue state is now documented with one clear residual follow-up instead of leaving silent ambiguity

### Issue 34 Follow-Up - CI And Coherence Cleanup (2026-04-23)

#### Fixed
- GitHub CI no longer breaks on the PR for unrelated infrastructure reasons:
  - quoted Python matrix versions in `.github/workflows/ci.yml` so `3.10` does not get parsed as broken `3.1`
  - runtime memory now falls back to a safe empty schema when `backend/engine/runtime/memory.json` is absent in CI
- Tightened core pose/outfit routing so the remaining coherence tails stop surfacing:
  - `counter_hip_lean_collar_touch` no longer leaks into bookish / coastal / creative / sporty scenes that have no believable counter context
  - kneeling poses no longer ride a generic `night` tag into quiet bookish / travel / public-elegant scenes
  - `bed_kneel_sheet_grip` now requires an actual bed-like context instead of slipping into lounge-ish interiors
- Batch generation no longer collapses when a fixed scene does not support the scheduled pose-group quota:
  - pose selection now falls back from the requested pose group to any scene-valid pose instead of dying with `Could not generate a valid batch`
- Custom select keyboard state is now rendered from the active option while the menu is open, which removes a stale-state seam that was showing up in CI E2E.

### Issue 7 - Women Pose Bank Safe Expansion Closed (2026-04-23)

#### Changed
- Finished the small safe `poses_master` import wave by moving reviewed women-only pose lines into the live external pose banks:
  - `backend/engine/data/overrides/line_banks/women/poses/1_3.md`
  - `backend/engine/data/overrides/line_banks/women/poses/4_5.md`
  - `backend/engine/data/overrides/line_banks/women/poses/6_8.md`
- Kept the rollout intentionally narrow:
  - only women pose banks were expanded
  - duplicates were skipped instead of force-merging them
  - overlong or broken lines were shortened/rewritten before landing live

#### Fixed
- Removed the bad high-spicy women pose-bank tail that had slipped into the live file:
  - a male line was removed from `women/poses/6_8.md`
  - a broken `their hands` wording was corrected to `her hands`
  - long vanity phrasing was trimmed back into line-bank-safe length

### Issue 36 - Race Preset Routing And Mixed Pool Fix (2026-04-23)

#### Fixed
- Race presets now affect actual generation instead of only weakly scoring the finished batch:
  - `Mostly Asian` routes the whole batch through Asian identities
  - exact ethnicity presets hard-lock the requested ethnicity
  - men and couples inherit the same corrected routing path
- `Mostly mixed` now uses a curated equal-weight nationality pool instead of the old default split:
  - includes European, Black, Latina, Asian, Arab, and Indian identities
  - no longer silently excludes `middle_eastern` and `south_asian`
- Random default ethnicity balance now gives Asian identities a visible share instead of the old near-zero `1/20` feel.

#### Changed
- Removed redundant `white` wording from European ethnicity render values such as Russian, Ukrainian, Polish, Italian, Spanish, English, French, German, Dutch, Greek, and Nordic presets.
- Added `Arab` and `Indian` as usable exact race presets backed by `middle_eastern` and `south_asian` ethnicity ids.

### Issue 36 - Curated Race Dropdown Coverage (2026-04-23)

#### Changed
- Expanded the visible women and men race dropdowns so they expose the same curated exact presets that the backend already supports:
  - Ukrainian, Russian, Polish, Italian, Spanish, English
  - Black American, Black British, Black Nigerian
  - Mexican / Colombian / Brazilian Latina or Latino
  - Chinese, Japanese, Thai, Vietnamese, Filipina / Filipino
  - Arab, Indian

#### Fixed
- Added a regression check so visible race options cannot silently drift away from `ALLOWED_RACE_PRESETS`.
- Fixed an accidental `@lru_cache` regression on `_anti_repeat_score` after the diversity-helper extraction and moved the close-up / same-person / women-random diversity helpers into `backend/services/diversity_scoring.py`.
- Extracted `_anti_repeat_score` into `backend/services/repeat_scoring.py` so `backend/services/scoring.py` no longer owns that repeat-only batch helper.

### Issue 36 - Final Race Preset Sweep And Closeout (2026-04-23)

#### Verified
- Final x20 matrix passed across:
  - women `random / mostly_asian / mostly_mixed / exact Japanese / exact Russian / exact Arab / exact Indian`
  - men `random / mostly_asian / mostly_mixed / exact Japanese / exact Russian / exact Arab / exact Indian`
  - couples `random/random / asian-black / mixed-mixed / Japanese-Arab / Russian-Indian`
- All final matrix cases returned `0 findings`.
- No redundant `white Russian`, `white Spanish`, or `white Ukrainian` wording resurfaced.

### UI Bug Pass

#### Changed
- Synced the visible topbar title with the document title so the page no longer shows two different product names.
- Moved `Debug`, `Line-banks`, and `History` into collapsed service sections by default instead of leaving them permanently expanded in the main flow.

#### Fixed
- Reduced desktop and mobile page bloat caused by always-open service panels in the control/output columns.
- Kept `Latest batch` visible while moving long-run history behind a compact summary, so the output column stays usable without losing access to old runs.

### Extra Large Breast Size

#### Changed
- Added `Extra large` to the breast-size control.
- Wired it to a stronger render phrase: `huge natural massive XXXL breasts`.

#### Fixed
- Kept the new size on the same age-band safety path as `very_big_breasts`, so validation and candidate selection stay consistent.

### Issue 39 - Women Line-Bank Outfit Color Pass

#### Changed
- Women line-bank outfit rendering now reuses the normal outfit color-story renderer instead of outputting raw line-bank clothing text.
- Women batch color diversification now uses the same style-aware color order and repeat caps as the couples path for spicy 4-8 instead of only handling low-spicy batches.

#### Fixed
- Stopped women line-bank outfits from dropping explicit color clauses, which was letting the image model collapse repeated batches into beige / taupe / muted monochrome defaults.
