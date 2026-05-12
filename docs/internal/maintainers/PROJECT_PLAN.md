# Prompt Generator Web Plan

## Issue Closeout Plan

- Stage 1: finish `#83` and lock the cheap-light / low-end treatment drift down with live validation.
  - Status: complete in code and validation; `Balanced` now keeps premium/editorial as the default lane.
  - Exit criteria: random / balanced / polished slices stop surfacing cheap documentary or phone-looking light as a dominant tail.
  - Required checks: treatment-mix audit, lighting/treatment compatibility audit, cheap-signal wording sweep.
- Stage 2: finish `#82` and keep framing fully honest.
  - Status: validated green after the latest sweep.
  - Exit criteria: portrait / full-body control stays stable in live smoke and render text no longer fights the crop.
  - Required checks: framing distribution smoke, portrait lower-body conflict smoke, full-body retention smoke.
- Stage 3: sweep the remaining taste regressions in `#79`, `#78`, `#77`, and `#76` as one coherent quality pass.
  - Status: validation green after the latest sweep; no remaining regressions in the checked tests.
  - Exit criteria: the prompt set stops reading budget / hybrid / chopped / smartphone-heavy in the checked lanes.
  - Required checks: outfit-taste sweep, raised-arm crop sweep, scene-coherence sweep, random-treatment mix sweep.
- Stage 4: after the sweep, update logs and leave only `#21`, `#1`, and `#69` open on purpose.
  - Exit criteria: all other open issues are either closed or explicitly removed from the active queue.
  - Notes: `#21` is a future safe module, `#1` is the umbrella roadmap, `#69` is post-stabilization refactor work.

## Current Focus

- [ ] Issue `#109`: random mix regression across scenes, poses, colors, and women expressions.
  - [x] reduce repeated conservatory / greenhouse style random backdrops and broaden scene motif spread
  - [x] push women random pose mix toward `standing/walking 65`, `seated 20`, `lower/reclined 15`
  - [x] reduce passport-like pose repetition in random
  - [x] widen random color-story spread so the same dark green / navy / burgundy / powder-blue cluster stops dominating
  - [x] add a few clearly happy / radiant women expressions with no winks
  - [ ] do one more live quality sweep and decide whether the scene mix still needs another narrow pass before closing
  - [ ] expand women random color-story library and clamp exact repeated color pairs inside a batch

- [ ] Issue `#112`: sport / fitness outfit-to-scene matching and dedicated banks.
  - [x] make `photoType=Balanced` override the old women-fitness phone/selfie treatment bias
  - [x] tighten activewear base-space matching so gym / pilates / training scenes stop accepting casual daywear
  - [x] teach shared location matching about active contexts (`gym`, `track`, `court`, `trail`, `stadium`, `locker`, `pilates`, `yoga`)
  - [x] add a first small active-location expansion to the shared location bank
  - [x] disable generic women line-bank overlays for `sport/fitness` so active presets stay on active engine scenes / outfits / poses instead of leaking rooftop / hotel / sensual fashion tails
  - [ ] add more sporty / fitness outfits and scene lines that mostly stay inside that category
  - [ ] do a live sporty/fitness sweep and decide whether gym / locker / outdoor-run coverage still needs another narrow pass

- [ ] Follow-up realism / framing pass.
  - [x] `#105` support / prop semantic hardening for sink / mirror / bed / mattress style poses in scenes that do not contain those supports
  - [x] `#100` outfit-to-scene semantic hardening after new outfit-bank additions
  - [x] `#107` remove face-close portrait crops from automatic portrait lanes
  - [x] `#108` add clean-shaven underarm rule for women arms-up poses

- [x] Issue `#69`: post-stabilization refactor and public-release cleanup.
  - [x] phase 0: inventory / freeze / baseline local checks
    - [x] backend gate green on the current tree: routing validation, couples scene coherence, men debug scaffold, and clothing color rendering all passed locally.
    - [x] public-facing surface to keep stable for now: `app.py`, `backend/api/`, `backend/forms/`, `backend/modes/`, `backend/services/`, `frontend/`, `tests/`, `README.md`, `QUICKSTART.md`, `SETUP_PROMPT_GENERATOR_WEB.bat`, `START_PROMPT_GENERATOR_WEB.bat`.
    - [x] internal docs and planning notes to review later for public-release cleanup: `ARCHITECTURAL_REFACTOR_SKELETON_PLAN_2026_04_21.md`, `HIGH_SPICY_BOUDOIR_RESEARCH_2026_04_21.md`, `HIGH_SPICY_COUPLES_INTERACTION_RESEARCH_2026_04_21.md`, `HYBRID_LINE_BANK_IMPLEMENTATION_PLAN_2026_04_22.md`, `IDEA_BANK_POSES_LOCATIONS.md`, `LOCAL_SPICY_6_8_REF_PASS_2026_04_21.md`, `MODEST_LOCATION_POSE_BANK.md`, `PROMPT_GENERATOR_WEB_TZ.md`, `STYLE_SETTING_STASH_2026_04_17.md`, `STYLIZATION_IMPLEMENTATION_PLAN.md`, `Z_IMAGE_STYLIZATION_NOTES.md`, `Z_IMAGE_STYLIZATION_NOTES_SUPPLEMENT_2026_04_18.md`.
    - [x] current legacy entry points to keep in view for the isolation phase: `backend/legacy_people.py` as a tracked compatibility shim, the quarantined `_legacy/legacy_people.py` implementation, the `backend/prompt_service.py` compatibility facade, the `app.py` HTTP bootstrap path, and the temporary `_legacy/legacy_bridge.py` quarantine seam.
  - [x] phase 1: isolate legacy code so it stops polluting the main project surface
    - [x] moved the legacy bridge adapter into ignored `_legacy/legacy_bridge.py` and removed the tracked `backend/legacy_bridge.py` path.
    - [x] moved the real legacy implementation into ignored `_legacy/legacy_people.py` and left `backend/legacy_people.py` as a thin compatibility shim.
  - [x] phase 2: extract `backend/prompt_service.py` into thinner behavior-preserving backend services
    - [x] added public `merged_form_state`, `resolve_runtime_controls`, and `infer_theme_style_mode` wrappers on `backend/prompt_service.py`.
    - [x] switched `backend/services/run_service.py` to the public prompt-service API instead of the private helper names.
    - [x] switched `backend/services/preset_service.py` to the public form-state wrapper too, so the remaining service callers no longer depend on prompt-service private helpers.
    - [x] removed the duplicated local `ALLOWED_MODES` definition from `backend/prompt_service.py`, pointed `backend/services/run_service.py` at the shared forms constant directly, and deleted two dead delegated fallback bodies from the prompt-service color-diversity wrappers.
    - [x] switched `backend/modes/{women,men,couples}.py` off the broad prompt-service module import and onto direct helper imports; also kept `backend/services/debug_summary.py` on a function-local prompt-service import to avoid the `postprocess -> debug_summary -> prompt_service` cycle while still narrowing that dependency.
    - [x] narrowed `backend/forms/user_profile.py` from a broad local prompt-service module import to a local named-helper import set, keeping the cycle-safe call timing while making the dependency surface explicit.
  - [x] phase 3: split scoring / selector hotspots by concern without taste retuning
    - [x] extracted the photo-treatment and random-light balance cluster into `backend/services/treatment_balance.py` and kept the focused smoke slice green.
    - [x] extracted the race / body / style / identity selection helpers into `backend/services/selection_scoring.py` and kept the same focused smoke slice green.
    - [x] extracted the shared photo-treatment profile lookup into `backend/services/photo_treatment_lookup.py` so scoring, postprocess, debug summary, treatment balance, and the prompt-service shim stop depending on `debug_summary.py` for that shared runtime helper.
    - [x] extracted the clone / cheap-fallback / location-motif batch-penalty cluster into `backend/services/batch_penalties.py` and kept the direct penalty helper tests plus API smoke green without changing the score weights.
    - [x] extracted the close-up / same-person / women-random diversity helper cluster into `backend/services/diversity_scoring.py` and kept the close-up smoke plus API smoke green after fixing the accidental `_anti_repeat_score` cache decorator regression.
    - [x] extracted the anti-repeat batch-scoring helper into `backend/services/repeat_scoring.py` and kept the API/public smoke slice green without changing repeat weights.
  - [x] phase 4: clean root/docs/internal residue for future public release
    - [x] cleaned the public README / QUICKSTART wording and removed internal-only issue-reporting references.
    - [x] moved maintainer-only plans, logs, and research notes out of the root into `docs/internal/*`.
    - [x] removed tracked GitHub Actions workflow and tracked VS Code workspace settings from the public repo surface.
  - [x] phase 5: tighten public-facing docs (`README`, `QUICKSTART`, setup/run flow)
    - [x] aligned the quickstart and README setup steps with the bundled setup / start scripts.
  - [x] phase 6: final release-readiness sweep with local validation only
    - [x] release smoke slice passed after isolating the order-sensitive random-balance test into its own pytest process.
  - [x] closeout: final structural passes landed, maintainer docs updated, and the issue can stay closed unless a new public-release cleanup bug appears.

- [ ] New issue: profile / strong-turn close-up pose lane brainstorm.
  - Goal: make close-up and face-led prompt lanes use explicit profile / strong-turn phrasing instead of collapsing into one generic head-angle pattern.
  - Exit criteria: profile, three-quarter, chin-up, chin-down, and strong-turn variants all have a clear bank / scoring path and batch output stops repeating one default close-up phrase.
  - [ ] define a dedicated pose-phrase bank for profile (`side profile`, `three-quarter`, `chin-up/down`) and strong head tilt variants
  - [ ] add a deterministic diversity target for close portrait lanes so face-led batches avoid repeating one default head-angle phrase
  - [ ] separate close-up pose language from full-body / mid-shot phrasing so framing and angle wording do not fight each other
  - [ ] add focused smoke checks for close-up pose diversity and anti-extreme-crop compliance

- [ ] Issue `#98`: finish the full-body framing follow-up.
  - [x] B+E pass landed: shorter full-body / ankle-up framing wording and no full-body `headroom` cue in the technical block.
  - [x] targeted framing smokes are green after the pass.
  - [x] visual confirmation / broader batch sweep check completed; full-body contract now treated as closeout-ready.
- [ ] Issue `#102`: reduce `same_person` framing and pose rigidity.
  - [x] measure `same_person` framing-group and posture-family spread against non-locked runs
  - [ ] identify whether identity lock plus retry / previous-candidate reuse is over-constraining pose and framing variation
  - [ ] recover more seated / lying variety in `same_person` without breaking identity consistency
  - [x] add a focused regression around `same_person` visual diversity preference in batch scoring

- [x] Issue `#103`: broaden women color and outfit diversity in live output.
  - [x] re-measure live `color_story_id` and `outfit_family_id` dominance after the latest content refresh
  - [x] reduce repeated beige / brown / navy / light-blue / pink overuse in broad women sweeps
  - [x] stop fitted mini-dress / bodycon lanes from crowding out the rest of the wardrobe

- [ ] Issue `#105`: tighten prop-aware scene / pose / outfit matching for impossible support and wet-context combos.
  - [x] cover courtyard+bed, gym+vanity-perch, and shoreline-lying + dry-outfit failures with focused local regressions
  - [x] add a first shared support-contract pass so line-bank bed poses and static `perched` poses stop passing impossible no-support scenes
  - [x] add a first validator backstop for `water_contact_pose` without wet-friendly outfit tags
  - [x] unify static pose-bank matching with `mirror/sink` support requirements so vanity poses no longer pass roadside scenes
  - [ ] keep sweeping for any remaining missing support classes before closing the issue
  - [ ] replace the remaining pose-id-heavy support gating with a fuller data-driven pose contract where possible
  - [ ] split dry coastal ambience from true water-contact coastal contexts earlier in outfit-family matching instead of relying only on validator backstop
  - [ ] implement against the detailed execution notes in `ISSUE105_PROP_MATCHING_IMPLEMENTATION_PLAN_2026_04_30.md`

- [ ] Issue `#104`: stop absurd scene-pose support matching and recover seated variety.
  - [x] block indoor support-object logic from leaking into outdoor / coastal / street contexts unless the scene explicitly contains that support
  - [ ] recover seated / lying pose incidence in scenes that genuinely support them
  - [x] cover the current bad-match examples with focused regressions

- [x] Fantasy / sci-fi location split follow-up.
  - [x] keep shared `locations/all.md` realism-only and route fantasy / sci-fi locations exclusively through `fantasy_locations.md`
  - [x] decide how semantic matching should explicitly understand fantasy / sci-fi location lanes instead of treating them as generic shared-location text
  - [x] implement domain-first shared-location matching so realism and fantasy / sci-fi banks no longer cross-fallback through generic semantic overlap

- [ ] Issue `#95`: investigate slow generation on batch size `40`.
  - [x] reproduce `batchSize=40` timing in a controlled runtime slice
  - [x] separate outer `_best_batch(...)` retries from inner `candidate_builder.generate_batch(...)` retries
  - [x] confirm the checked pathological case lives inside constrained exact-theme candidate retries, not outer full-batch regeneration
  - [x] land a first perf pass that removes futile exact-theme retries caused by impossible outfit-to-scene-family starts and by an overlong strict first anti-repeat stage
  - [x] decide whether baseline non-exact-theme `batchSize=40` still needs a second pass after more measurements
  - [x] land a second perf pass for large random-balanced batch-40 runs by deferring strict balance enforcement out of the earliest retry stage
  - [ ] decide whether issue `#95` should now be closed after manual runtime acceptance

- [ ] Framing follow-up: finish the reopened `#98` full-body fix and harden `#99` portrait safety.
  - [x] read the renderer contract and current framing smokes before changing wording again
  - [x] strengthen standing `full_body` / `ankle_up` wording around camera pull-back and centered full-height composition
  - [x] strengthen portrait framing wording with explicit anti-top-crop language across the beauty portrait lanes
  - [x] rerun the targeted framing smoke tests
  - [x] remove the remaining `knee_up` / `cowboy_shot` minority under `more_full_body` by tightening the control profile to pure full-group scheduling

- [ ] Exact-theme location follow-up: keep shared `line_bank_location` aligned with edge-case theme text after scene-family hard locks.
  - [x] make manual `womenSceneFamily` override beat broader `sceneFocus` family pools
  - [x] hard-lock `industrial loft`, `train compartment`, and `fire stair landing` onto stable scene-family lanes through higher-priority exact-theme hints
  - [x] add a first shared location-line pass so exact themes stop inheriting unrelated ship-deck / museum-room / coastal tails inside the now-correct scene family
  - [x] tighten `train compartment` from train-adjacent travel lines down to compartment-only lines through anchor-token shared-location matching

- [x] Issue `#100`: systematically strengthen outfit-to-scene coherence matching.
  - [x] verify the root leak sits in the core `outfit_family -> scene_family` selector gate rather than only in line-bank cleanup
  - [x] add a first semantic compatibility pass for sporty/wellness spaces so vacation/daywear outfits stop leaking into pilates / juice-bar / spa-movement contexts
  - [x] add a first semantic compatibility pass for luxury-public non-bar spaces so clubwear / bodysuit nightlife looks stop leaking into travel, staircase, and lounge contexts
  - [x] add focused smoke coverage for the checked mismatch classes and confirm valid control pairs still pass
  - [x] confirm no second selector-gate pass is needed for the checked industrial / transit / fire-stair edge cases; the remaining work sat in exact-theme routing rather than the issue `#100` core outfit-to-scene gate

- [ ] Issue `#98`: make full-body framing use real camera distance and standing-safe coverage.
  - [x] add explicit `camera pulled back` framing language for standing `full_body` and `ankle_up` prompts
  - [x] keep seated/non-standing full-height prompts on a wider full-figure wording instead of reusing the standing wording blindly
  - [x] make `more_full_body` score only true `full_body` / `ankle_up` framings instead of also rewarding `knee_up` / `cowboy_shot`
  - [x] replace wording-only fix with a dedicated standing full-length framing contract
  - [x] do not require both feet as the universal success rule; the real goal is a true full-length standing lane that no longer collapses into portrait crops
  - [ ] validate against the user's live standing full-body failures; if needed, strengthen the contract with centered full-length wording and standing-safe pose compatibility

- [ ] Issue `#99`: harden portrait anti-head-cut framing and keep chest-up beauty default.
  - [x] reduce automatic `face_only` share in random and `more_portraits`
  - [x] bias portraits back toward `head_and_shoulders` and `below_chest_portrait`
  - [x] add a portrait-safe framing clause so ordinary portrait crops keep full head and hair with breathing room above the head
  - [x] harden render-layer portrait wording so the safe default zone reads chest-up / head-and-shoulders instead of a too-tight top crop
  - [ ] validate against live portrait head-cut failures and keep `face_only` non-default

- [ ] Follow-up for `#98` / `#99`:
  - [x] land the first render-layer hardening pass with focused smoke coverage
  - [x] do one small runtime sanity sweep for `more_full_body` and `more_portraits`
  - [x] run broad multi-seed runtime framing sweep and tune `more_full_body` group scheduling toward full-height dominance
  - [x] add anti-collapse full-height wording (`no waist-up/mid/portrait crop`) and standing-pose preference inside `more_full_body`
  - [x] remove opposite-lane cross leak at group level (`more_full_body -> no portrait group`, `more_portraits -> no full group`) and rename UI label to `Portraits`
  - [ ] do broader live visual validation before closing either issue

- [x] Issue `#90`: root-cause treatment / lighting / scene regression after semantic matching changes.
  - [x] write the shared shot-contract design down so future work stays contract-driven instead of turning into scattered bans and scoring hacks
  - [x] add an authoritative `shot lane` / render-contract layer so treatment, light, and setting stop behaving like loosely compatible fragments
  - [x] make the lane contract authoritative over contradictory combinations such as `night + daylight`, premium/editorial treatment with cheap scene tails, and stage/studio drift
  - [x] cover the root regression with focused render/contract tests before any new broad taste tuning
  - [x] harden shared-location semantic matching so `studio`, `hospitality_suite`, `culture_bookish`, and `garden_conservatory` stop inheriting obviously wrong fallback tails
  - [x] block `creative_like` apartment/gallery tails from luxury suite scenes so `residential_luxury` stops borrowing artist-loft location flavor
  - [x] extend the first-pass render contract with cheap-tail stripping for premium interior scenes and with reverse normalization for dark/night lanes that still carried daytime wording
  - [x] close the biggest remaining shared-location matcher gaps for `creative_gallery`, `nightlife_*`, luxury/hospitality wet/coastal tails, and daytime scenes inheriting night-only location text
  - [x] add explicit runtime scoring pressure against cheap flat fallback treatment/scene/light combinations that still survive the contract
  - [x] validate the broader contract in live sweeps, then carry remaining studio-specific cleanup into `#89`

- [x] Issue `#89`: true seamless-studio contract.
  - [x] split `seamless studio background` from `practical studio/set` scenes as separate intentional lanes
  - [x] make seamless lanes render only clean single-color backdrop language instead of `school portrait`, `stage`, or visible setup clutter
  - [x] keep practical stylized studio/set scenes available, but only in their own lane

- [x] Issue `#92`: true face close-up portrait lane.
  - [x] strengthen the `face_only` framing contract so it reads as a real face-close crop instead of collapsing back into chest-up portrait language
  - [x] strip body/outfit noise from `face_only` prompts so the lane stays face-led
  - [x] slightly raise the random portrait share for `face_only` / tighter close portrait variants without breaking the broader portrait mix

- [x] Issue `#93`: reliable full-body framing with ankles-or-feet in frame.
  - [x] add an explicit full-body framing clause so `full_body` prompts clearly demand feet-in-frame coverage
  - [x] add an explicit ankle-up framing clause so `ankle_up` prompts clearly demand full-height coverage to the ankles
  - [x] keep the existing broader framing distribution stable while making the full-height lanes read more literally to the model

- [x] Issue `#97`: rebalance portraits away from aggressive face-only crops and add anti head-cut safety.
  - [x] reduce automatic `face_only` share in random and `more_portraits`
  - [x] bias portraits back toward `head_and_shoulders` and `below_chest_portrait`
  - [x] add a portrait-safe framing clause so ordinary portrait crops keep full head and hair with breathing room above the head

- [x] Issue `#86`: rebalance women random body type distribution.
  - [x] add a women-random body-group override so curved bodies stay near the target 10% share
  - [x] cover the distribution with a seeded regression smoke

- [x] Issue `#85`: rebalance women random breast size distribution.
  - [x] add a women-random breast-size schedule so the batch mix stays near the target split
  - [x] cover the distribution with a seeded regression smoke

- [x] Issue `#87`: recover sitting and lying pose variety in random mode.
  - [x] add a seeded regression smoke that checks standing, seated, and lying buckets across women / men / couples
  - [x] confirm the current random pose mix keeps seated and lying / reclined poses visible instead of collapsing into standing-heavy batches

- [x] Issue `#84`: make random mode favor more outdoors and sunlight.
  - [x] treat daylight / sunlit / sunny / summer tags as outdoor-like in the random balance helpers
  - [x] raise the random outdoor and sunlight targets so random batches drift less into indoor / low-sun tails
  - [x] add a focused multi-seed random sunlight regression test and update the legacy baseline smoke

- [x] Issue `#88`: harden random-mode location coherence for seasonal balcony / rooftop tails.
  - [x] add a winter-like location tag for snow / winter / alpine lines
  - [x] make location matching consult the active `setting_value` again so seasonal tails can be rejected early
  - [x] cover the change with a focused location-matching regression test

- [x] Photo type control first pass.
  - [x] curate the first-pass treatment lanes from `good light.md` instead of importing the whole file blindly
  - [x] define six top-level modes: `Balanced`, `Glossy`, `Studio`, `Stylized`, `Amateur`, `Custom`
  - [x] keep `Photo treatment bias` only as a `Custom`-only manual lock instead of letting it fight the higher-level mode control
  - [x] first-pass curated lane mapping:
    - `Glossy` -> `clean_commercial`, `direct_light_editorial`, `concept_photo_editorial`, `advertising_poster_realism`, with cheap phone/selfie lanes pushed down
    - `Studio` -> `studio_seamless`, `concept_photo_editorial`, `clean_commercial`, plus `studio` scene-family pressure
    - `Stylized` -> `concept_photo_editorial`, `cinematic_poster_realism`, `low_key_dramatic`, `direct_flash_night`, `vintage_flash_photo`, `advertising_poster_realism`
    - `Amateur` -> `candid_phone_snapshot`, `mirror_selfie`, `casual_indoor_selfie`, `disposable_camera`, `documentary_still`, with a small carry-over lane through `analog_35mm` / `clean_commercial` / `direct_light_editorial`
  - [x] implementation slice:
    - backend: add `photoTypeControl` default + normalization + first-pass profile layer in `backend/forms/user_profile.py`
    - frontend: add a `Photo type` slider in `Stylization` using the same range-control pattern as `Spicy level`
    - interaction: disable `Photo treatment bias` unless `Photo type == Custom`
  - [x] follow-up pass: validate the mix against live prompts and tighten `Amateur` so it stops over-falling back into `clean_commercial`
  - [x] second follow-up pass: tighten `Glossy` scene palette away from `creative_gallery` / `studio` / `nightlife_neon` / `wellness_spa` and expose `Photo type` in debug output with bucket/quality/tone summaries
  - [x] third follow-up pass: make `Studio` more studio-specific by removing the `clean_commercial` dependency, tighten `Stylized` away from `direct_light_editorial` / daylight tails, and make explicit photo-type `deprioritized` / `banned` values override the base `styleMode=random` preferred sets
  - [x] fourth follow-up pass: give `Balanced` a real healthy-default lane instead of an empty fallback, and make it authoritative over late random remaps so it stops inheriting phone/selfie and studio/nightlife tails

- [x] Issue `#82`: stop portrait/full-body framing prompts from fighting the requested crop in render text.
  - [x] add framing-aware outfit rendering so portrait crops stop surfacing lower-body outfit clauses
  - [x] add framing-aware pose rendering so portrait crops stop surfacing lower-body pose/body-language detail
  - [x] cover the fix with focused render smoke tests plus the existing framing-control regression suite

- [x] Issue `#83`: stop cheap-looking light / treatment drift through a real treatment-quality taxonomy.
  - [x] phase 1: add explicit treatment metadata for `quality_tier` and `treatment_tone` instead of relying on loose handpicked id lists
  - [x] phase 2: rebuild women random mix routing around the new taxonomy so `phone`, `raw_low_end`, `editorial_non_phone`, and `polished_glam` are separated on purpose
  - [x] phase 3: add first-pass style/scene-aware scoring and remap penalties so glam / premium contexts stop selecting low-end documentary / selfie lanes
  - [x] phase 4: rewrite the worst low-end treatment wording only after routing/scoring no longer depends on those lanes
  - [x] phase 5: add focused regression gates for low-end treatment share and cheap-signal wording in final prompt output
  - [x] stage 6: tighten the `Balanced` default lane so premium / editorial output is the healthy default instead of a passive low-end fallback

- [x] Issue `#78`: remove raised-arm line-bank poses that crop badly in tighter framing.
  - [x] replace the most direct overhead-arm women/men `6_8` line-bank pose text
  - [x] add a framing-aware line-bank pose veto for tight portrait/upper-body crops
  - [x] wire the same veto through both women/couples and legacy men paths

- [x] Issue `#76`: rebalance women random treatment mix toward `~10% phone / ~30% non-phone stylized / ~60% polished-editorial`.
  - [x] add explicit treatment-mix buckets instead of relying only on `stylized` vs `polished`
  - [x] retune women random treatment selection, remap pressure, and batch scoring around the target mix
  - [x] verify the new runtime mix with a focused multi-seed sweep

- [x] Issue `#77`: remove direct background hybrid injectors.
  - [x] stop `line_bank_location` from splicing unrelated material/accent/atmosphere tails into custom locations
  - [x] remove repair-rule paths that force unrelated conflicts into the generic luxury/spa fallback

- [x] Issue `#79`: recover premium look quality by blocking the cheapest line-bank outfit phrases in refined modes.
  - [x] tag the most budget nightclub-coded outfit lines explicitly
  - [x] block those lines in `random / luxury / romantic / lifestyle` while keeping them for appropriate nightlife/studio lanes

- [x] Issue `#68` implementation follow-up from the approved sidebar spec.
  - [x] add reusable `chips` and `toggle` primitives
  - [x] move `Generate` to the top with `mode`, `spicy level`, `batch size`, and `debug`
  - [x] convert short high-frequency controls away from dropdowns where practical
  - [x] move saved presets into the sidebar utility area

- [x] Issue `#67`: rebalance expression mood weights and remove `calm / confident` at spicy `6-8`.
  - [x] add an explicit high-spicy ban for `calm_confident` in the active mood-selection path
  - [x] reduce baseline `calm_confident` pressure in general random generation
  - [x] keep low-spicy women on a calmer lane without forcing one mood id only
  - [x] add focused women/couples mood-distribution smoke coverage

- [x] Issue `#66`: hotter couples `6-8` pose bank and stronger chemistry / gaze layer.
  - [x] expand the dedicated couples `4_5` and `6_8` pose pools so pairs stop collapsing into three repeated setups
  - [x] move softer close-contact ideas down into the mid-spicy lane
  - [x] remove camera-locked `direct eye contact` from the active high-spicy couples mood path
  - [x] add focused couples chemistry / gaze regression coverage

- [ ] Next UI follow-up after this implementation pass.
  - [ ] tighten `Appearance` density further if the chips rows feel too tall in couples mode
  - [ ] consider removing the duplicate batch-size control from the action dock if review says the top `Generate` block is enough
  - [ ] run a visual browser pass and, if needed, add a narrow frontend regression check

- [x] Issue `#65`: make portrait and full-body framing controls actually work.
  - [x] move framing control influence into active candidate selection instead of relying only on late scoring
  - [x] bias portrait/full-body runs through framing-group share overrides
  - [x] strengthen final prompt framing language so portrait/full-body instructions read more literally to the image model
  - [x] cover the behavior with a focused multi-seed framing smoke test

- [x] Issue `#75`: rebuild Z-Image prompt opener around a framing-first, treatment-aware structure.
  - [x] add a data-driven opener bank keyed by `camera_framing_id` and `photo_treatment_id`
  - [x] split subject identity text from the opener so the final prompt starts with the shot declaration itself
  - [x] remove duplicate framing from the late technical tail so the opener stays authoritative
  - [x] cover the new opener contract with focused smoke checks, including an explicit selfie-treatment path

- [x] Issue `#55`: render file paths with OS-native separators in UI.
  - [x] add one shared frontend path formatter for runtime-native separators
  - [x] route line-bank help paths through the shared formatter
  - [x] remove hardcoded path separator assumptions from the UI rendering path
  - [x] verify updated frontend files pass syntax checks

- [x] Issue `#54`: reduce repeated orange-tree and pool-background motifs at the source.
  - [x] introduce location-motif clustering in scoring (`waterside`, `orchard_citrus`, etc.)
  - [x] apply batch-level penalties for over-concentrated motif clusters in random/lifestyle/coastal/vacation modes
  - [x] keep exact-theme path untouched
  - [x] verify random women motif spread with a dedicated multi-seed smoke test

- [x] Issue `#53`: constrain Arab and Indian routing out of `Random` preset.
  - [x] route `random_default_split` through an explicit ethnicity id pool that excludes `middle_eastern` and `south_asian`
  - [x] keep `mostly_mixed` behavior unchanged so Arab/Indian still surface there
  - [x] keep exact `middle_eastern` / `south_asian` presets unchanged
  - [x] cover behavior with focused race-routing smoke tests

- [x] Issue `#58`: add a dedicated couples pose line-bank layer.
  - [x] extend line-bank loader contract for `couples/poses` while keeping existing women/men/shared contracts stable
  - [x] add live couples pose starter files in `backend/engine/data/overrides/line_banks/couples/poses/{1_3,4_5,6_8}.md`
  - [x] wire couples candidate selection and couples render surfacing for line-bank pair poses
  - [x] cover repo-backed loading and couples prompt surfacing with focused tests

- [x] Issue `#56`: strengthen semantic matching for location and outfit line banks.
  - [x] extend inferred location tags beyond the current shallow indoor/outdoor/coastal/etc. pass
  - [x] extend inferred outfit tags so public/private, lounge, dining, active, and hot-weather contexts can filter more accurately
  - [x] prove the new behavior with focused regression tests in `tests/test_line_bank_loader.py`
- [x] Issue `#57`: reduce beige and muted palette dominance as part of the same runtime pass.
  - [x] lower the heaviest neutral color-story weights
  - [x] tighten clone-prone muted-color penalties and clean-neutral caps in active runtime paths
  - [x] add a focused smoke test for random women color spread

- [x] **Critical UI pass:** align the Appearance blocks between women / men / couples into one clear schema and do not move on to other tasks until that is finished.
  - [x] Bring the shared blocks to one order and naming logic so subject / appearance / scene read the same in every mode.
  - [x] Keep only the female-specific fields where they are actually needed: `Makeup` and `Breast size` only for women.
  - [x] Shape the clothing axis so women and men have the same entry points, but different semantics: women use `Outfit reveal`, men use `Outfit vibe`, or one shared block with different sub-controls.
  - [x] Check whether men `Body mix` is needed in the UI; if so, expose it explicitly, if not, remove the hidden backend/UI asymmetry.
  - [x] Make helper text and debug labels consistent so the differences look intentional rather than accidental.
  - [x] Separately decide how to present the women-only `Women scene family` so it looks like an intentional exception, not a broken shared schema.

- [x] Stylization phase 1: internal `photo_treatment` layer added to render/debug.
- [x] Stylization phase 2: `photo_treatment` tied into selection and batch scoring.
- [x] Stylization phase 3: first rebalance pass completed for `random / creative_artistic / studio / luxury`.
- [x] Harder stylized lanes `concept_photo_editorial` and `direct_light_editorial` now surface in live batches instead of staying buried.
- [x] `men luxury` taste pass: less clean-heavy, more editorial outfit and pose variety.
- [x] Added the next treatment family: `mirror selfie / disposable camera / documentary still`.
- [x] Added the next treatment family: `casual indoor selfie / vintage flash / advertising poster realism`.
- [x] Debug upgraded: stylization summary cards plus per-prompt style/treatment fit signals.
- [x] `photo treatment` is exposed in UI as an optional stylization control.
- [x] Issue `#39` first pass: women line-bank outfits now keep explicit color clauses, and women spicy `4-8` batches reuse couples-style color repeat caps.
- [x] Issue `#41`: default random batches now target ~50/50 indoor/outdoor and ~60/40 bright/muted light balance without overriding explicit scene controls.
- [x] Issue `#35`: custom-heavy batch generation now has a staged fallback instead of failing outright when hard appearance atoms overconstrain the pool.
- [x] Issue `#37`: wet outfit wording from line-banks now requires explicit wet/pool/spa/humid context instead of leaking into dry scenes.
- [x] Issue `#45`: shared location line-bank now uses one common `all.md` file instead of spicy-bucketed files.
- [x] Issue `#46`: expand the unified shared location bank with bright summer outdoor scenes, then do a light compatibility pass.
  - [x] wave 1: added the first bright-summer outdoor expansion slice plus a narrow location-tag compatibility pass
  - [x] wave 2: continued growing beaches / pool angles / nature / summer city / cafe variants without bloating near-duplicates
  - [x] wave 3: added one last curated fill pass

Keep this file as a live project status: what is done, what comes next, and what is waiting in the queue.

## Done

- [x] PR `#32` CI cleanup: race-dropdown smoke now reflects the curated preset contract, and `couples + luxury + exact_theme` no longer allows the vacation-tagged `shirt_trousers` tail.

- [x] Clothing color render naturalization completed.
  - Outfit wording no longer treats most dual-color stories as one unrealistic whole-garment palette.
  - Separates and layered looks can now distribute color across garment roles, with a small patterned path and a rare kept dual-color whole-look path.
  - The same helper now covers women render plus legacy men / couples outfit text.
  - Follow-up `#39` fixed the women line-bank bypass: raw line-bank outfit text now goes through the color-story renderer instead of letting the image model invent beige defaults.

- [x] Local spicy `6-8` live promotion and scoring rebalance completed.
  - Promoted the full local women pose/outfit pack plus the local couples interaction pack into live banks.
  - Promoted the local male-side couples outfit pack into the live styling bank.
  - Rebalanced women spicy `6-8` pose selection toward a sexy-pose majority while keeping anti-repeat active.
  - Kept `coordination_pairs` as draft-only research notes because there is still no live couples outfit-pair contract.

- [x] Local spicy `6-8` reference extraction pass completed as a draft-only staging step.
  - Reviewed the imported `!poses and outfits` stash metadata-first for PNG and visual-first for Pinterest JPG.
  - Added four narrow draft seed files plus `LOCAL_SPICY_6_8_REF_PASS_2026_04_21.md`.
  - Kept the pass out of live generation pending overlap review against the already-promoted 2026-04-21 high-spicy packs.

- [x] Safe high-spicy couples interaction pass completed for issue `#4`.
  - Added a reviewed adult-only, non-explicit couples interaction research pack with 16 spicy-but-safe interaction ids in `backend/engine/data/drafts/pose_bank/`.
  - Promoted the reviewed interactions into live routing with clear spicy gating: `1-4` stays on moderate-safe legacy interaction language, `5-6` can surface `revealing`, and `7-8` can also surface `pushing_it` when style/scene allow it.
  - Added debug visibility plus smoke coverage for promoted couples interaction ids and low-spicy safety.
- [x] Safe high-spicy women research seed pack prepared in drafts.
  - Added a large adult-only, non-explicit pose seed bank and matching outfit seed bank under `backend/engine/data/drafts/`.
  - Added a separate research note with source provenance plus `revealing` / `pushing_it` / low-spicy-block review lists.
  - Kept the work out of live generation pending smaller promotion and scorer/safety review.
- [x] Safe high-spicy women research pack promoted into live banks.
  - Merged all researched pose ids into the core pose bank and all researched outfit ids into the core styling bank.
  - Extended the women high-spicy scorer constants so the new ids are actually usable in generation.
  - Added a bank smoke test to lock the promotion in place.
- [x] Men generator path enabled.
- [x] Couples generator path enabled.
- [x] Men UI reduced to a minimal legacy-safe appearance block with `Male hair length`.
- [x] Couples UI now combines the women appearance block with a separate `Man hair length` control.
- [x] Men outfit vibe pass: `maleOutfitControl` now uses vibe-style values and scene-aware random routing instead of concrete clothing labels.
- [x] Critical UI parity pass completed for women / men / couples appearance blocks.

- [x] Local web UI is running on a Python HTTP server.
- [x] Women mode works.
- [x] Men and Couples are enabled in the UI.
- [x] Output is formatted as `1 prompt = 1 line`.
- [x] Latest prompts: each prompt has `Copy`.
- [x] Latest prompts: `Copy all` is available.
- [x] History: only `Copy` remains.
- [x] Presets: save / load / delete.
- [x] Debug panel: compact view with the main distributions.
- [x] Seed removed from the UI.
- [x] `Spicy level` supports `Random`, which picks a value from 3 to 8.
- [x] UI translated to English.
- [x] Gray disabled controls instead of `planned / wired` labels.
- [x] Preset and Debug are split into separate sections.
- [x] Women filters are wired for:
  - [x] person mode
  - [x] age
  - [x] race preset
  - [x] body mix preset
  - [x] validation mode
  - [x] style mode
  - [x] style vibe
  - [x] pose / framing control
  - [x] lighting control
  - [x] location strategy
- [x] Race pool expanded according to the rules:
  - [x] split white nations instead of one `white European`
  - [x] expanded Black pool
  - [x] expanded Latina pool
  - [x] carefully expanded Asian pool
  - [x] excluded by default for Middle Eastern / South Asian
- [x] START bat fixed so it launches the current `app.py`, not a stray process from another cwd.
- [x] Visual style shifted toward `soft-orange`.

## Next

### Hybrid Line-Bank Override Wave (2026-04-22)

- Detailed execution plan: `HYBRID_LINE_BANK_IMPLEMENTATION_PLAN_2026_04_22.md`.
- [x] P0: freeze the hybrid contract with separate `women/` and `men/` line-bank trees under `backend/engine/data/overrides/line_banks/`.
- [x] P1: add loader/validation infrastructure for line-based `poses`, `expressions`, and `outfits`, keyed by gender as well as spicy bucket, with hard length-budget caps.
- [x] P2: ship the first live wave only through the women engine path and prove it does not change current men/couples behavior.
- [x] P3: treat men as a separate legacy-bridge follow-up for poses/outfits; do not assume the same integration cost as women.
- [x] P4: keep men expressions gated behind an explicit optional follow-up instead of forcing them into the first live wave.
- [x] P5: leave placeholder seams for future `locations`, `hair`, and `makeup` line-banks, plus docs and troubleshooting notes.
- [x] Small UI help entrypoint added for line-banks so the local file path and current mode/spicy targets are visible from the sidebar.

### Issue #7 - Content-Bank Follow-Up: Next Safe Expansions And Promotions (2026-04-22)

- Scope rule: this wave is about small safe content growth, not about re-proving the bank architecture.
- Decision: all new women/men pose additions should be authored in the external line-banks first under `backend/engine/data/overrides/line_banks/`, not injected straight into the large core JSON banks.
- Guardrail: couples do not get a live line-bank pose path yet; new couples interaction or appearance growth should still start in `drafts` until there is a real couples-side external-bank contract.

- [x] P0: keep the intake and promotion rules locked for future waves.
  - [x] treat external women/men `poses` line-banks as the default entrypoint for future pose writing, review, and spicy-bucket sorting
  - [x] keep `expressions`, wet variants, and male/couples appearance growth on the smallest safe path first: draft fragments unless there is already a live low-risk seam
  - [x] do not open `hair`, `makeup`, or `locations` line-banks in this issue unless a concrete content pressure appears during later small waves

- [x] P1: for the next pose growth wave, continue using external banks only.
  - [x] reviewed `poses_master` as temporary source material instead of dumping it directly into core banks
  - [x] moved only cleaned, unique women pose lines into live `1_3 / 4_5 / 6_8` external banks
  - [x] stopped after the safe women pose slice instead of turning `#7` back into a giant umbrella issue

- [x] Close issue `#7` once the safe pose-import slice is logged and pushed.
  - Follow-up content growth should now happen under newer focused issues (`#34`, `#36`, `#37`, etc.) instead of re-opening the old broad bucket.

### Issue #29 - Make Spicy Levels 6-8 Feel Clearly Stronger (2026-04-22)

- Goal: make final prompt output at `spicyLevel 6-8` feel materially hotter than `1-5`, not just slightly stronger.
- Scope:
  - compare `1-5` against `6-8` across `women / men / couples`
  - tune wording, routing, scorer pressure, and postprocess only where the high lane still feels too soft
  - keep `1-5` stable so low and moderate ranges do not drift upward by accident
- Handoff rule:
  - another agent should start from this exact sequence, not improvise a different direction first

### Issue #36 - Race Presets And Ethnicity Routing (2026-04-23)

- [x] P1: reproduce the bug.
  - [x] confirmed `Mostly Asian` and exact presets were not controlling normal women/men batches strongly enough
  - [x] confirmed random default only surfaced Asians at the old tiny share
  - [x] confirmed European wording still rendered redundant `white Russian` / `white Spanish` style phrases
- [x] P2: fix race preset routing.
  - [x] group presets now drive the ethnicity schedule directly
  - [x] exact presets now use a required ethnicity id schedule
  - [x] men and couples route through the same corrected preset path
- [x] P3: restore Asian visibility in random.
  - [x] default random ethnicity target share now gives Asian identities a visible batch share
- [x] P4: rebuild `Mostly mixed`.
  - [x] curated equal-weight mixed pool now includes European / Black / Latina / Asian / Arab / Indian identities
- [x] P5: clean wording.
  - [x] European ethnicity render values no longer carry redundant `white` prefixes
- [x] P6: regression tests and logs.
  - [x] added `tests/test_issue36_race_presets_smoke.py`
  - [x] updated old couples identity expectation from `white Ukrainian` to `Ukrainian`
- [x] P7: expose the supported exact presets in the UI.
  - [x] women dropdown now shows the curated exact preset pool
  - [x] men dropdown now shows the same backend-supported exact preset pool with male-friendly labels
  - [x] added regression coverage so dropdown values and allowed normalized values stay aligned
- [x] P6 closeout sweep:
  - [x] final x20 matrix passed for `random / mostly_asian / mostly_mixed / exact presets`
  - [x] covered `women / men / couples`
  - [x] no `white Russian / white Spanish / white Ukrainian` wording resurfaced
  - [x] close `#36`

- [x] P0: baseline comparison sweep
  - [x] ran a baseline matrix for `women / men / couples` comparing representative `3/5` against `6/8`
  - [x] logged where `6-8` still read only marginally stronger in final prompts
  - [x] baseline findings split:
    - women already separate well overall, but `6` vs `8` can still feel too close in some `random / romantic` runs
    - men were better than low spicy, but `random / nightlife / romantic` still leaned too polite in final mood wording
    - couples were the weakest path: high spicy mostly looked like the same chemistry copy with only mild wording drift
    - no evidence that postprocess was the main blocker; the weaker separation was mostly in scorer pressure plus legacy men/couples render wording

- [x] P1: first high-lane correction pass
  - [x] tightened scorer and routing where the baseline showed weak separation, focused on `men` and `couples`
  - [x] kept the pressure additive on `6-8` instead of broad shifts to `1-5`
  - [x] kept couples contact-rule changes narrow: only spicy-aware interaction selection and mood wording, not a wider rewrite of issue `#4`

- [x] P2: regression and comparison retest
  - [x] reran the same matrix after the first correction pass
  - [x] confirmed `6-8` now reads clearly stronger for `couples`, and noticeably stronger for `men`, while `1-5` stayed stable
  - [x] logged before/after conclusions in `TEST_LOG.md`

- [x] P3: if needed, do one follow-up tightening pass only on the weakest remaining mode
  - [x] final narrow follow-up went into `men nightlife`, which had still been flattened by a shared late-night mood override
  - [x] kept scope narrow and did not widen it into a new broad spicy rewrite
  - [x] issue `#29` can now be treated as complete; future spicy tuning should be taste polish, not core separation repair
- [x] P4: clean up issue-29 CI instability before merge
  - [x] audited PR `#32` and confirmed the actionable blocker was Playwright `webServer` portability, not a fresh smoke/coherence regression
  - [x] replaced the Windows-only `set PROMPT_GENERATOR_PORT=8766 && python app.py` test launcher with a cross-platform `webServer.env` setup
  - [x] reran local `e2e` and the bounded `coherence-report` command after the fix and recorded both in `TEST_LOG.md`
- [x] P5: close the women-vs-men appearance-option gap that was still making the female block feel thinner
  - [x] added a real women-side `Outfit vibe` control next to `Outfit reveal`
  - [x] wired the control through defaults, normalization, UI, and women/couples style-profile selection
  - [x] verified that `women` and `couples` still generate normally with the new clothing-vibe bias active
- [x] P6: add one more women-side finish/grooming-adjacent control so the female block is not just longer, but structurally closer to the male block
  - [x] added `Beauty finish` next to the existing women `Makeup`
  - [x] wired it through defaults, normalization, UI, and women/couples style-profile preferences
  - [x] verified that women generation still runs cleanly with both low-polish and high-polish finish presets
- [x] P7: finish issue `#28` clothing-control unification instead of leaving women/men half-aligned
  - [x] kept `Outfit vibe` as the shared first clothing control on both sides
  - [x] renamed the women-only secondary control to `Reveal level`, so it now reads like a refinement of the same clothing model rather than a separate system
  - [x] added a shared outfit-vibe alias layer for shorter/legacy values and verified women/couples runtime smoke before closing the issue
  - [x] prefer one more narrow pass over broad global retuning
  - [x] close `#29`

### Issue #34 - Line-Bank Follow-Up: Outfits, Pose Gating, And Shared Location Bank (2026-04-22)

- Goal: make the line-bank layer smarter and less dumb in real scenes, without turning it into another giant hardcoded subsystem.
- Scope:
  - tighten outfit line-bank coherence against scene context
  - split pose line-banks by posture family and gate seated/lying poses where they make no physical sense
  - add the first shared repo-backed location line-bank, spicy-bucketed but not gender-split
- Handoff rule:
  - execute this issue in small safe slices with repo-backed tests and live smoke after each slice

- [ ] P0: lock the rollout shape before coding
  - [ ] keep this issue data-first where possible, but allow narrow routing/gating rules where pure data is not enough
  - [ ] do not mix this issue with another broad styling or UI pass
  - [ ] treat women/men/couples smoke as mandatory after every sub-step because line-banks now touch live prompt text

- [x] P1: outfit line-bank coherence pass
  - [x] review the current outfit line-bank surfacing path and identify where line-bank outfits ignore scene reality
  - [x] add narrow scene-aware bans / soft gates so obviously wrong pairings stop surfacing
  - [x] explicitly target nonsense like:
    - [x] bathrobe / robe-like outfits in restaurant / lobby / formal luxury scenes
    - [x] beach/pool-coded clothing in inland lifestyle / urban / bookish scenes
    - [x] obviously too-homewear-coded looks in public formal scenes unless the route truly supports it
  - [x] rerun broad women / men / couples smoke after the pass and log examples that were removed
  - Notes:
    - women outfit line-bank selection now waits for scene context instead of firing before scene/base-space choice
    - men legacy outfit line-bank overrides now use the same scene-aware filtering seam
    - conservative guardrails are intentional here; better to drop a bad line-bank outfit than surface nonsense in a public-facing scene

- [x] P2: pose-bank posture split and physical-scene gating
  - [x] split pose-bank entries into posture families:
    - [x] standing
    - [x] seated
    - [x] lying
  - [x] keep the split practical and lightweight; do not add extra posture classes unless a real need appears
  - [x] add scene-aware gating so seated / lying poses cannot surface in scenes with no believable support surface
  - [x] explicitly block absurd cases like:
    - [x] sitting on hotel corridor / lobby floors
    - [x] lying on asphalt / random pavement / random hard public ground
    - [x] reclining where the scene does not imply a bed, sofa, chaise, floor cushion, grass, sand, or similar support
  - [x] rerun line-bank tests and live smoke after the posture split
  - Notes:
    - the split is currently heuristic, inferred from line text, not a separate authored posture schema yet
    - `ground_low_like` was added as a pragmatic extra seam for kneeling/low-to-ground lines so they can be blocked in public hard-floor contexts without overcomplicating the model

- [x] P3: shared location line-bank
  - [x] add a new shared line-bank path for locations
  - [x] do not split locations by gender
  - [x] split only by spicy buckets, matching the existing line-bank workflow
  - [x] keep the first rollout simple:
    - [x] one shared bank
    - [x] loader + validation
    - [x] repo-backed smoke test
    - [x] one live smoke proving the location lines can surface safely
  - [x] do not invent extra categories unless the first pass shows a real need
  - Notes:
    - the first shared location rollout is render-level, not a full replacement of `setting_micro_id` / scene routing
    - scene compatibility is still lightly guarded by inferred location tags so obviously wrong nightlife/coastal/bookish/wellness mismatches do not surface

- [x] P4: final verification and cleanup
  - [x] rerun focused repo-backed tests for outfits / poses / locations
  - [x] rerun representative live smoke for women / men / couples
  - [x] log what got safer and what still remains future work
  - [x] only after that decide whether this issue is merge-ready or needs one more narrow cleanup pass
  - [x] add the next reviewed women pose lines into `backend/engine/data/overrides/line_banks/women/poses/{1_3,4_5,6_8}.md`
  - [x] add the next reviewed men pose lines into `backend/engine/data/overrides/line_banks/men/poses/{1_3,4_5,6_8}.md`
  - [x] keep each promotion batch small and themed so rollback/review stays simple instead of mixing many unrelated pose styles at once
  - [x] log which source pack each future promoted pose batch came from so future cleanup does not turn into archaeology
  - Merge-readiness:
    - `#34` is now merge-ready as a functional line-bank pass
    - one honest residual tail remains for later: tighten shared-location taste matching, especially vanity/wellness/coastal crossover
    - CI/coherence follow-up is now also closed:
      - workflow matrix parsing is fixed
      - runtime memory fallback is fixed
      - the last `Could not generate a valid batch` culture-bookish edge case is fixed through pose-group fallback
      - coherence now passes again at `viol_per_100_max=0.39 / threshold 3.0`
    - [x] close `#34`

- [x] First practical slice for this issue: `External pose bank wave 1`.
  - target files:
    - `backend/engine/data/overrides/line_banks/women/poses/1_3.md`
    - `backend/engine/data/overrides/line_banks/women/poses/4_5.md`
    - `backend/engine/data/overrides/line_banks/women/poses/6_8.md`
    - `backend/engine/data/overrides/line_banks/men/poses/1_3.md`
    - `backend/engine/data/overrides/line_banks/men/poses/4_5.md`
    - `backend/engine/data/overrides/line_banks/men/poses/6_8.md`
  - out of scope for wave 1:
    - couples pose/interaction growth
    - expressions
    - outfits
    - wet variants
    - size-control changes
    - opening live `hair`, `makeup`, or `locations` line-banks
  - batch size cap:
    - add at most `6` new women pose lines total in the first pass
    - add at most `6` new men pose lines total in the first pass
    - do not add more than `3` new lines to any single spicy bucket in wave 1
  - content shape rule:
    - every new line must stay atomic, reusable, and under the existing `140` char cap
    - do not add scene-prop-specific lines that only make sense in one narrow location unless that location pressure is already recurring in live runs
    - prefer poses that widen body posture, movement, and camera-ready stance variety before adding more niche sensual micro-poses
  - source logging rule:
    - every wave-1 addition must be traceable to one named external source pack or review note in the commit message, `PROJECT_PLAN.md`, or follow-up log entry
    - wave-1 review note label: `external_pose_review_pass_2026_04_22`
  - acceptance criteria:
    - all 6 target files remain parse-safe line-banks with no cap violations
    - new lines surface only in `women` or `men` as intended and do not affect couples behavior
    - the first pass stays obviously reviewable in one diff without looking like a bulk content dump
    - checked outcomes are recorded in `TEST_LOG.md` after the content lands
  - validation target for wave 1:
    - run the narrowest line-bank validation/smoke coverage for touched pose files first
    - then recheck representative live outputs for `women random` and `men random`
    - only after that consider a second small pose wave
  - status:
    - first wave completed with `6` new women pose lines and `6` new men pose lines across the six live pose files
    - validated with focused line-bank tests plus live `women random`, `men random`, and `couples lifestyle` generation smoke

- [x] Second practical slice for this issue: `External pose bank wave 2`.
  - target files:
    - `backend/engine/data/overrides/line_banks/women/poses/1_3.md`
    - `backend/engine/data/overrides/line_banks/women/poses/4_5.md`
    - `backend/engine/data/overrides/line_banks/women/poses/6_8.md`
    - `backend/engine/data/overrides/line_banks/men/poses/1_3.md`
    - `backend/engine/data/overrides/line_banks/men/poses/4_5.md`
    - `backend/engine/data/overrides/line_banks/men/poses/6_8.md`
  - scope rule:
    - keep the same narrow scope as wave 1 and continue only `women/men` external `poses`
    - keep `couples`, `expressions`, `outfits`, wet variants, and size-control work out of this pass
  - batch size:
    - add exactly `1` new line to each of the six live pose files
    - keep the wave incremental enough that the stacked PR stays easy to review on top of wave 1
  - source logging rule:
    - wave-2 review note label: `external_pose_review_pass_2026_04_22_wave2`

- [x] Third practical slice for this issue: `External pose bank wave 3`.
  - target files:
    - `backend/engine/data/overrides/line_banks/women/poses/1_3.md`
    - `backend/engine/data/overrides/line_banks/women/poses/4_5.md`
    - `backend/engine/data/overrides/line_banks/women/poses/6_8.md`
    - `backend/engine/data/overrides/line_banks/men/poses/1_3.md`
    - `backend/engine/data/overrides/line_banks/men/poses/4_5.md`
    - `backend/engine/data/overrides/line_banks/men/poses/6_8.md`
  - scope rule:
    - same narrow scope again: only `women/men` external `poses`
    - keep `couples`, `expressions`, `outfits`, wet variants, and size-control work out of this pass
  - batch size:
    - add exactly `1` new line to each of the six live pose files
  - content intent:
    - widen stance and seated-angle variety a bit more instead of adding narrower prop-bound lines
    - keep every added line atomic and under the current `140` char cap
  - source logging rule:
    - wave-3 review note label: `external_pose_review_pass_2026_04_22_wave3`
  - validation target:
    - rerun the focused line-bank tests
    - rerun live smoke for `women random`, `men random`, and `couples lifestyle`
  - status:
    - third wave completed with `6` new pose lines total, one per touched file
    - validation passed for focused line-bank tests and the same live smoke trio
  - acceptance criteria:
    - all six files remain parse-safe line-banks with no cap violations
    - the new lines widen stance and posture variety without turning into scene-specific micro-routes
    - couples generation remains unaffected in the same live smoke used for wave 1
  - status:
    - second wave completed with `3` new women pose lines and `3` new men pose lines across the same six live pose files
    - validated with the same focused line-bank tests plus live `women random`, `men random`, and `couples lifestyle` generation smoke
    - follow-up cleanup removed the new scene-prop-specific pose wording before any further wave
    - focused coverage now includes a repo-backed loader smoke test that reads the checked-in live pose-bank files instead of only synthetic temp banks

- [x] Fourth practical slice for this issue: `External pose bank wave 4`.
  - target files:
    - `backend/engine/data/overrides/line_banks/women/poses/1_3.md`
    - `backend/engine/data/overrides/line_banks/women/poses/4_5.md`
    - `backend/engine/data/overrides/line_banks/women/poses/6_8.md`
    - `backend/engine/data/overrides/line_banks/men/poses/1_3.md`
    - `backend/engine/data/overrides/line_banks/men/poses/4_5.md`
    - `backend/engine/data/overrides/line_banks/men/poses/6_8.md`
  - scope rule:
    - keep the same narrow scope as wave 3 and continue only `women/men` external `poses`
    - keep `couples`, `expressions`, `outfits`, wet variants, and size-control work out of this pass
  - batch size:
    - add exactly `1` new line to each of the six live pose files
    - keep the wave incremental enough that the stacked PR stays easy to review on top of wave 3
  - source logging rule:
    - wave-4 review note label: `external_pose_review_pass_2026_04_22_wave4`
  - validation target:
    - run the same focused line-bank tests
    - recheck representative live outputs for `women random`, `men random`, and `couples lifestyle`
  - status:
    - fourth wave completed with `3` new women pose lines and `3` new men pose lines across the same six live pose files
    - validated with the same focused line-bank tests plus live `women random`, `men random`, and `couples lifestyle` generation smoke

- [x] Fifth practical slice for this issue: `External pose bank wave 5`.
  - target files:
    - `backend/engine/data/overrides/line_banks/women/poses/1_3.md`
    - `backend/engine/data/overrides/line_banks/women/poses/4_5.md`
    - `backend/engine/data/overrides/line_banks/women/poses/6_8.md`
    - `backend/engine/data/overrides/line_banks/men/poses/1_3.md`
    - `backend/engine/data/overrides/line_banks/men/poses/4_5.md`
    - `backend/engine/data/overrides/line_banks/men/poses/6_8.md`
  - scope rule:
    - keep the same narrow scope as wave 4 and continue only `women/men` external `poses`
    - keep `couples`, `expressions`, `outfits`, wet variants, and size-control work out of this pass
  - batch size:
    - add exactly `1` new line to each of the six live pose files
    - keep the wave incremental enough that the stacked PR stays easy to review on top of wave 4
  - source logging rule:
    - wave-5 review note label: `external_pose_review_pass_2026_04_22_wave5`
  - validation target:
    - run the same focused line-bank tests
    - recheck representative live outputs for `women random`, `men random`, and `couples lifestyle`
  - status:
    - fifth wave completed with `3` new women pose lines and `3` new men pose lines across the same six live pose files
    - validated with the same focused line-bank tests plus live `women random`, `men random`, and `couples lifestyle` generation smoke

- [x] Sixth practical slice for this issue: `External pose bank wave 6`.
  - target files:
    - `backend/engine/data/overrides/line_banks/women/poses/1_3.md`
    - `backend/engine/data/overrides/line_banks/women/poses/4_5.md`
    - `backend/engine/data/overrides/line_banks/women/poses/6_8.md`
    - `backend/engine/data/overrides/line_banks/men/poses/1_3.md`
    - `backend/engine/data/overrides/line_banks/men/poses/4_5.md`
    - `backend/engine/data/overrides/line_banks/men/poses/6_8.md`
  - scope rule:
    - keep the same narrow scope as wave 5 and continue only `women/men` external `poses`
    - keep `couples`, `expressions`, `outfits`, wet variants, and size-control work out of this pass
  - batch size:
    - add exactly `1` new line to each of the six live pose files
    - keep the wave incremental enough that the stacked PR stays easy to review on top of wave 5
  - source logging rule:
    - wave-6 review note label: `external_pose_review_pass_2026_04_22_wave6`
  - validation target:
    - run the same focused line-bank tests
    - recheck representative live outputs for `women random`, `men random`, and `couples lifestyle`
  - status:
    - sixth wave completed with `3` new women pose lines and `3` new men pose lines across the same six live pose files
    - validated with the same focused line-bank tests plus live `women random`, `men random`, and `couples lifestyle` generation smoke

- [x] Seventh practical slice for this issue: `External pose bank wave 7`.
  - target files:
    - `backend/engine/data/overrides/line_banks/women/poses/1_3.md`
    - `backend/engine/data/overrides/line_banks/women/poses/4_5.md`
    - `backend/engine/data/overrides/line_banks/women/poses/6_8.md`
    - `backend/engine/data/overrides/line_banks/men/poses/1_3.md`
    - `backend/engine/data/overrides/line_banks/men/poses/4_5.md`
    - `backend/engine/data/overrides/line_banks/men/poses/6_8.md`
  - scope rule:
    - keep the same narrow scope as wave 6 and continue only `women/men` external `poses`
    - keep `couples`, `expressions`, `outfits`, wet variants, and size-control work out of this pass
  - batch size:
    - add exactly `1` new line to each of the six live pose files
    - keep the wave incremental enough that the stacked PR stays easy to review on top of wave 6
  - source logging rule:
    - wave-7 review note label: `external_pose_review_pass_2026_04_22_wave7`
  - validation target:
    - run the same focused line-bank tests
    - recheck representative live outputs for `women random`, `men random`, and `couples lifestyle`
  - status:
    - seventh wave completed with `3` new women pose lines and `3` new men pose lines across the same six live pose files
    - validated with the same focused line-bank tests plus live `women random`, `men random`, and `couples lifestyle` generation smoke

- [ ] P2: keep male-side and couple-side appearance growth draft-first.
  - [ ] add the next male-side hairstyle / grooming / outfit candidates as narrow draft fragments, not broad core-bank dumps
  - [ ] add the next couples-side appearance or interaction candidates as narrow draft fragments with explicit adult-safe notes
  - [ ] only promote reviewed draft fragments after focused smoke checks prove they do not leak into the wrong mode, scene, or spicy range

- [ ] P3: expand adult expression coverage in small passes.
  - [ ] review where women/men expression language still feels shallow or repetitive in live runs
  - [ ] add the next adult-safe expression lines in the smallest supported seam first, preferring existing women/men expression line-banks where they already fit
  - [ ] avoid mixing expression expansion with wet-look or size-control work in the same promotion batch

- [ ] P4: expand outfit coverage in small passes.
  - [x] first practical slice for this issue: `External outfit bank wave 1`
    - target files:
      - `backend/engine/data/overrides/line_banks/women/outfits/1_3.md`
      - `backend/engine/data/overrides/line_banks/women/outfits/4_5.md`
      - `backend/engine/data/overrides/line_banks/women/outfits/6_8.md`
      - `backend/engine/data/overrides/line_banks/men/outfits/1_3.md`
      - `backend/engine/data/overrides/line_banks/men/outfits/4_5.md`
      - `backend/engine/data/overrides/line_banks/men/outfits/6_8.md`
    - scope rule:
      - keep this pass on `women/men` external `outfits` only
      - keep `couples`, `poses`, `expressions`, wet variants, and size-control work out of this pass
    - batch size:
      - add exactly `1` new line to each of the six live outfit files
    - source logging rule:
      - outfit review note label: `external_outfit_review_pass_2026_04_22_wave1`
    - validation target:
      - run the focused line-bank tests
      - recheck representative live outputs for `women random`, `men random`, and `couples lifestyle`
    - status:
      - first outfit wave completed with `3` new women outfit lines and `3` new men outfit lines across the same six live outfit files
      - validated with the same focused line-bank tests plus live `women random`, `men random`, and `couples lifestyle` generation smoke
  - [x] second practical slice for this issue: `External outfit bank wave 2`
    - target files:
      - `backend/engine/data/overrides/line_banks/women/outfits/1_3.md`
      - `backend/engine/data/overrides/line_banks/women/outfits/4_5.md`
      - `backend/engine/data/overrides/line_banks/women/outfits/6_8.md`
      - `backend/engine/data/overrides/line_banks/men/outfits/1_3.md`
      - `backend/engine/data/overrides/line_banks/men/outfits/4_5.md`
      - `backend/engine/data/overrides/line_banks/men/outfits/6_8.md`
    - scope rule:
      - keep this pass on `women/men` external `outfits` only
      - keep `couples`, `poses`, `expressions`, wet variants, and size-control work out of this pass
    - batch size:
      - add exactly `1` new line to each of the six live outfit files
    - source logging rule:
      - outfit review note label: `external_outfit_review_pass_2026_04_22_wave2`
    - validation target:
      - run the focused line-bank tests
      - recheck representative live outputs for `women random`, `men random`, and `couples lifestyle`
    - status:
      - second outfit wave completed with `3` new women outfit lines and `3` new men outfit lines across the same six live outfit files
      - validated with the same focused line-bank tests plus live `women random`, `men random`, and `couples lifestyle` generation smoke
  - [x] grouped follow-up slice for this issue: `External outfit bank waves 3-5`
    - target files:
      - `backend/engine/data/overrides/line_banks/women/outfits/1_3.md`
      - `backend/engine/data/overrides/line_banks/women/outfits/4_5.md`
      - `backend/engine/data/overrides/line_banks/women/outfits/6_8.md`
      - `backend/engine/data/overrides/line_banks/men/outfits/1_3.md`
      - `backend/engine/data/overrides/line_banks/men/outfits/4_5.md`
      - `backend/engine/data/overrides/line_banks/men/outfits/6_8.md`
    - scope rule:
      - keep this grouped pass on `women/men` external `outfits` only
      - keep `couples`, `poses`, `expressions`, wet variants, and size-control work out of this pass
    - batch size:
      - add exactly `3` new lines to each of the six live outfit files
      - stop at wave 5 and switch the next slice away from outfits
    - source logging rule:
      - outfit review note label: `external_outfit_review_pass_2026_04_22_wave3_5`
    - validation target:
      - run the focused line-bank tests once after the grouped pass
      - recheck representative live outputs for `women random`, `men random`, and `couples lifestyle`
    - status:
      - grouped outfit waves `3-5` completed with `9` new women outfit lines and `9` new men outfit lines total across the same six live outfit files
      - validated with the same focused line-bank tests plus live `women random`, `men random`, and `couples lifestyle` generation smoke
  - [x] first practical slice for this issue: `External expression bank wave 1`
    - target files:
      - `backend/engine/data/overrides/line_banks/women/expressions/1_3.md`
      - `backend/engine/data/overrides/line_banks/women/expressions/4_5.md`
      - `backend/engine/data/overrides/line_banks/women/expressions/6_8.md`
      - `backend/engine/data/overrides/line_banks/men/expressions/1_3.md`
      - `backend/engine/data/overrides/line_banks/men/expressions/4_5.md`
      - `backend/engine/data/overrides/line_banks/men/expressions/6_8.md`
    - scope rule:
      - keep this pass on `women/men` external `expressions` only
      - keep `couples`, `poses`, `outfits`, wet variants, and size-control work out of this pass
    - batch size:
      - add exactly `1` new line to each of the six live expression files
    - source logging rule:
      - expression review note label: `external_expression_review_pass_2026_04_22_wave1`
    - validation target:
      - run the focused line-bank tests
      - recheck representative live outputs for `women random`, `men random`, and `couples lifestyle`
    - status:
      - first expression wave completed with `3` new women expression lines and `3` new men expression lines across the same six live expression files
      - validated with the same focused line-bank tests plus live `women random`, `men random`, and `couples lifestyle` generation smoke
  - [x] second practical slice for this issue: `External expression bank wave 2`
    - target files:
      - `backend/engine/data/overrides/line_banks/women/expressions/1_3.md`
      - `backend/engine/data/overrides/line_banks/women/expressions/4_5.md`
      - `backend/engine/data/overrides/line_banks/women/expressions/6_8.md`
      - `backend/engine/data/overrides/line_banks/men/expressions/1_3.md`
      - `backend/engine/data/overrides/line_banks/men/expressions/4_5.md`
      - `backend/engine/data/overrides/line_banks/men/expressions/6_8.md`
    - scope rule:
      - keep this pass on `women/men` external `expressions` only
      - keep `couples`, `poses`, `outfits`, wet variants, and size-control work out of this pass
    - batch size:
      - add exactly `1` new line to each of the six live expression files
    - source logging rule:
      - expression review note label: `external_expression_review_pass_2026_04_22_wave2`
    - validation target:
      - run the focused line-bank tests
      - recheck representative live outputs for `women random`, `men random`, and `couples lifestyle`
    - status:
      - second expression wave completed with `3` new women expression lines and `3` new men expression lines across the same six live expression files
      - validated with the same focused line-bank tests plus live `women random`, `men random`, and `couples lifestyle` generation smoke
  - [x] grouped follow-up slice for this issue: `External expression bank waves 3-5`
    - target files:
      - `backend/engine/data/overrides/line_banks/women/expressions/1_3.md`
      - `backend/engine/data/overrides/line_banks/women/expressions/4_5.md`
      - `backend/engine/data/overrides/line_banks/women/expressions/6_8.md`
      - `backend/engine/data/overrides/line_banks/men/expressions/1_3.md`
      - `backend/engine/data/overrides/line_banks/men/expressions/4_5.md`
      - `backend/engine/data/overrides/line_banks/men/expressions/6_8.md`
    - scope rule:
      - keep this grouped pass on `women/men` external `expressions` only
      - keep `couples`, `poses`, `outfits`, wet variants, and size-control work out of this pass
    - batch size:
      - add exactly `3` new lines to each of the six live expression files
      - stop at wave 5 and switch the next slice to outfits
    - source logging rule:
      - expression review note label: `external_expression_review_pass_2026_04_22_wave3_5`
    - validation target:
      - run the focused line-bank tests once after the grouped pass
      - recheck representative live outputs for `women random`, `men random`, and `couples lifestyle`
    - status:
      - grouped expression waves `3-5` completed with `9` new women expression lines and `9` new men expression lines total across the same six live expression files
      - validated with the same focused line-bank tests plus live `women random`, `men random`, and `couples lifestyle` generation smoke

- [ ] P4: add wet variants only behind hard scene compatibility.
  - [ ] stage `wet skin`, `wet hair`, and `wet clothing` variants in draft fragments first
  - [ ] limit first-pass eligibility to scenes that naturally justify it, such as pool / spa / shower-adjacent luxury / beach / rain-specific contexts
  - [ ] add focused checks so wet variants do not leak into bookish, dry interior, sporty daylight, or otherwise nonsense combinations

- [ ] P5: split bigger size-control expansion into its own compatibility-first pass.
  - [ ] map which current preset keys and saved values would break if new size controls or value enums are added
  - [ ] decide whether backward-compat aliases or form normalization shims are enough before any UI exposure
  - [ ] only ship the bigger size-control expansion after preset/history migration risk is explicitly checked and logged

- [ ] Validation and logging for every mini-wave.
  - [ ] after each promotion, run the smallest focused smoke set for the touched slice first, then recheck representative live modes
  - [ ] minimum broad sample after meaningful content changes: `women random`, `men romantic`, `couples lifestyle`, and any directly affected wet or appearance lane
  - [ ] record actual checked outcomes in `TEST_LOG.md`, note promotions in `CHANGELOG.md`, and keep unfinished follow-ups here instead of hiding them in code comments

- [x] Architectural refactor: backend/frontend skeleton.
  - Detailed execution plan: `ARCHITECTURAL_REFACTOR_SKELETON_PLAN_2026_04_21.md`.
  - First hard target: turn `app.py`, `backend/prompt_service.py`, and `frontend/app.js` into thin entry/facade files without changing API or prompt output.
  - Phase 0 safety net is complete: public contract smoke coverage added and both backend/frontend gates are green.
  - Phase 1 backend entry/facade split is complete: HTTP handler moved out of `app.py`, bootstrap/preset service shells added, and compatibility exports kept stable.
  - Phase 2 backend form split is complete: `backend/forms/*` now holds normalization/runtime/user-profile logic, and `backend/prompt_service.py` delegates through the new layer.
  - Phase 3 backend run split is complete: mode wrappers, debug-summary service, and run-service orchestration now sit behind the compatibility facade.
  - Phase 4 frontend module entry split is complete: ES-module boot is live, and `frontend/api/client.js` plus `frontend/state/store.js` now sit under the existing app entry.
  - Phase 5 frontend UI skeleton is complete: shared components, section renderers, and form controller logic now sit under `frontend/components/*`, `frontend/sections/*`, and `frontend/controllers/form_controller.js`.
  - Skeleton-stage refactor target is complete. Any next step is a follow-up wave, not part of the initial thin-entry skeleton pass.
  - Phase 6.1 follow-up wave is complete: `backend/engine/data_loader.py`, `backend/engine/selectors.py`, `backend/engine/candidate_builder.py`, and `backend/engine/render/prompt_renderer.py` now hold the engine responsibilities while `backend/engine/generator.py` stays as the compatibility surface for existing callers.
  - Phase 6.2 follow-up wave is complete: `backend/services/scoring.py`, `backend/services/postprocess.py`, and `backend/services/batch_selection.py` now hold the extracted prompt-service scoring/postprocess/batch-selection logic while `backend/prompt_service.py` delegates through the compatibility facade.
  - Phase 6.3 follow-up wave is complete: `frontend/styles/tokens.css`, `frontend/styles/layout.css`, `frontend/styles/controls.css`, and `frontend/styles/output.css` now hold the extracted stylesheet responsibilities while `frontend/styles.css` stays as the stable browser entry.
  - Phase 6.4 follow-up wave is complete: backend mode-wrapper exports and wrapper-local aliases now use mode-neutral names, while `backend/legacy_people.py` remains the underlying men/couples implementation behind the stable registry seam.
  - The skeleton-plan architectural follow-up checklist is now complete through Phase 6.4; any further structural pass should be scoped as a new follow-up wave.

- [x] Personalization block for Women.
  - Added a dedicated women personalization section in UI with one-click quick profiles (`Everyday clean`, `Soft editorial`, `Night glam`, `Reset to random`) mapped to existing reveal/makeup/hair controls.

### UX / UI Issue Queue (2026-04-21)

- [x] Issue `#19` UI/UX: exact-theme shortcut over `locationStrategy`.
  - [x] Add a checkbox-style shortcut that syncs to `locationStrategy=exact_theme`.
  - [x] Disable/subordinate `Scene focus` while the shortcut is active.
  - [x] Keep `womenSceneFamily` available as the higher-priority explicit override.
  - [x] Add UI smoke coverage so the shortcut and advanced control stay in sync.
- [x] Issue `#15` UI cleanup: hair-color controls, microcopy, and copy icon sizing.
  - [x] Rename the dyed-hair toggle microcopy and keep the label next to the checkbox.
  - [x] Place the dyed-hair toggle directly next to the women hair-color control and mirror it in couples woman-side UI.
  - [x] Keep frontend/backend form normalization aligned so the couples woman-side toggle survives when `Hair color = Random`.
  - [x] Move `Custom hair color` above `Eye color`.
  - [x] Resize prompt copy icons to `24px` and trim low-value helper text.
- [x] Issue `#16` UI cleanup: subject preset quick-picks.
  - [x] Promote `Japanese` into the live subject path.
  - [x] Shorten visible race quick-picks in bootstrap/UI without breaking old preset ids.
  - [x] Recheck preset/history backward compatibility and exact-preset smoke coverage.
- [x] Issue `#18` bugfix: couples male custom-race strict matcher.
  - [x] Keep `maleRacePreset=other + maleCustomRace=...` usable in `couples + different_persons` after strict identity hardening.
  - [x] Align strict matching with the existing previewed custom male ethnicity text instead of rewriting current male custom debug/render output.
  - [x] Add focused regression coverage for both the matcher and the end-to-end couples request path.
- [x] Issue `#17` future UX/render cleanup: `Character constraint`.
  - [x] Add the dedicated backend render slot.
    - `characterConstraint` now derives a normalized `character_constraint_segment` during prompt assembly and renders through its own `character` segment next to the subject block.
    - The live field stays backward-compatible: the existing input remains in place, while scoring/debug now read from the normalized segment source of truth.
  - [x] Keep preview/debug compatibility stable.
    - Prompt preview now shows the dedicated segment when present, so the backend render-slot change does not disappear in the current UI cards.
    - Debug prompt decisions now carry both the raw `characterConstraint` text and the normalized segment string for future visibility work without changing current UI wording.

### Random Coherence Sweep

- [x] P0: harden random women / couples scene routing so pool, spa, bookish, and creative scenes stop accepting obvious outfit spillovers.
- [x] P0: block sport-prep poses like `track_shoe_tie_block` outside sport / wellness contexts.
- [x] P0: add regression coverage for the sampled bad random combinations.
- [x] P1: audit men random / romantic candidate scaffolds if their debug output becomes user-visible.
  - Added dedicated smoke coverage for `men random/romantic` debug decisions so men runs assert male scaffold fields directly (`maleOutfit`, `malePose`, `maleHair`, `maleGrooming`) and prevent women-side fallback leaks.
- [x] P2: decide whether `exact_theme` should hard-lock scene family selection instead of only surfacing the theme in render text.
  - Decision: `exact_theme` now hard-locks scene-family selection via `required_scene_families` derived from theme hints (instead of scoring-only influence).
  - Guardrail: explicit women-side `womenSceneFamily` keeps priority when manually set, so exact-theme lock does not override that explicit control.

### Systemic Coherence Follow-up (2026-04-20 audit)

- [x] P0: move outfit-scene coherence from scorer penalties to hard eligibility gates in candidate selection.
  - Added rule-based eligibility gating in candidate selection (`_base_space_outfit_predicate`) so obvious scene-outfit mismatches are filtered before scoring.
  - Quiet-day `residential_luxury` now blocks `vest_trousers` / `halter_trousers` leakage in random/luxury sweeps.
- [x] P0: add a pose-task context contract in the routing layer (not post-hoc repair).
  - Enforced task-context guards for `bookish`, `creative`, `domestic`, and `outdoor` task poses directly in pose selection.
  - Added a style-aware quiet-formal kneeling guard for `hospitality_suite` base spaces while keeping luxury/nightlife generation feasible.
- [x] P0: keep `validationMode=strict` as a backstop, but stop relying on it as the primary quality gate.
  - Coherence mismatches are now filtered upstream in selection/routing for both `normal` and `strict` validation modes.
  - Full stress audit (`data/audits/combination_audit_20260420_223406.json`): `816` runs, `8160` candidates, `0` violations (`0.0` per 100 candidates).
- [x] P1: normalize and tighten scene-tag taxonomy used by compatibility checks.
  - Added semantic scene-tag normalization in generator routing so `quiet_luxury` / `night` / `social` / `bookish` checks stay consistent across outfit/material/detail/atmosphere/pose eligibility.
- [x] P1: add a repeatable CI-facing coherence audit threshold.
  - Kept `scripts/stress_combination_audit.py` as the reproducible harness and fixed direct invocation shape to match backend form normalization.
  - Added bounded deterministic audit coverage (`max-cases`) plus progress logging to keep CI runtime predictable and avoid silent long-running jobs.
  - Calibrated bounded CI settings on local runs (`max-cases=96`, `calibration-runs=2`) and promoted coherence report to blocking guard in CI with `--hard-fail --threshold 3.0`.
- [x] P2: expand women/couples coherence smoke tests from single-issue checks to pattern-level matrix checks.
  - Matrix smoke now covers women/couples bookish/wellness/nightlife plus luxury and creative exact-theme lanes with per-class scene/outfit/pose contracts.

### 1. Outfit modesty / reveal

- [x] Add a dedicated clothing control.
- [x] Modes:
  - [x] Random
  - [x] Reserved
  - [x] Balanced
  - [x] Revealing
  - [x] Pushing it
- [x] In `Random`, tie the choice to `style vibe` and `spicy level`.
- [x] Pull in and normalize the outfit families / materials / exposure bands base.
- [x] Separate out a safe mapping between vibe, reveal level, and outfit routing.

### 2. Hair length / hairstyle

- [x] Add a hair-length control:
  - [x] Random
  - [x] Short hair
  - [x] Medium hair
  - [x] Long hair
- [x] Add baseline hairstyle presets from engine data.
- [x] Add an optional text input for a manual hair constraint.
- [x] Decide priorities: preset vs manual input.

### 3. Hair color

- [x] Add a hair-color control:
  - [x] Random
  - [x] Black
  - [x] Dark brown
  - [x] Brown
  - [x] Light brown
  - [x] Blonde
  - [x] Dark blonde
  - [x] Red / ginger
  - [x] Auburn
  - [x] Gray / silver
- [x] Add an optional text input for a manual color constraint.
- [x] Exclude fantasy / vivid colors from `Random`:
  - [x] blue
  - [x] pink
  - [x] green
  - [x] purple
  - [x] etc
- [x] Added an `allow dyed natural-ish colors` toggle for copper / burgundy.

### 4. Makeup

- [x] Pull in a proper makeup bank from the current / legacy rules.
- [x] Add a makeup style control.
- [x] In `Random`, tie makeup to `style vibe` and `spicy level`.
- [x] Make the behavior so clean / soft / glam / night-out do not conflict with outfit reveal.

## Planned After That

- [x] Validation pass for women style routing:
  - [x] Verify that `Fitness` actually produces sporty outfit / pose / vibe / scene combinations.
  - [x] Verify that `Sport` actually produces sporty outfit / pose / vibe / scene combinations.
  - [x] Walk through the style presets and compare the expected visual output with the actual one.
  - [x] If routing is too weak, strengthen the weights and/or hard filters.
- [x] `Custom race` routing.
- [x] `Exact theme` routing.
- [x] `Character constraint` routing.
- [x] More explicit anti-repeat settings from the UI.
- [x] Women-only fine controls for scene families.
  - [x] `womenSceneFamily` now nudges reveal, hair, makeup, and outfit taste instead of only locking the scene family.
- [x] Better debug readout with effective decisions per run.
- [x] Appearance block mode switch: `Generated` vs `Custom`.
  - [x] Add top radio buttons for appearance mode.
  - [x] Default state: generated mode active, dropdowns enabled, custom input disabled.
  - [x] Custom mode: disable outfit / hair / makeup controls and enable one free-text appearance input.
  - [x] Extend this beyond women: men and couples now use per-side appearance modes too.
- [x] Expand male appearance controls beyond hair length.
- [x] Add dedicated couples-side controls beyond the current shared women block + male hair length setup.

## Notes

- First, keep deepening the Women path.
- Add new controls only if they are actually wired into the engine; otherwise keep them disabled.
- Personalization needs one proper source of truth for the banks:
  - first look at the current generator data / rules
  - use legacy as a secondary source only if the new bank is missing something

## Next Working Notes

- [x] Women modesty / clothing pass completed:
  - [x] broader modest outfit bank
  - [x] safer low-spicy pose / hand-action / mood behavior
  - [x] final-batch color diversification for duplicate outfit clones
- [ ] Minimal men verification follow-up:
  - [ ] review men luxury / nightlife taste level
  - [x] decide whether low-spicy men also need calmer mood routing
- [x] Couples next phase:
  - [x] separate women block and men block in UI
  - [x] separate women atoms and men atoms in couples mode
  - [x] fix `couples + nightlife` routing so it stops leaking into daylight / pool-like settings in the final rendered prompt
- [ ] Couples follow-up:
  - [x] decide whether couples different-person mode needs harder woman-side age/race enforcement
  - [x] expand the male-side appearance block beyond hair length
  - [x] add separate male-side outfit/grooming controls if the legacy path is no longer enough

## Residual TODO

## Immediate Priorities (2026-04-20 exact-theme sweep)

- [x] Done: women exact-theme scene-outfit coherence pass for calm interiors and nightlife
  - [x] stop `mini_dress` / `bodysuit_trousers` from surfacing in women-side `lifestyle + bookish / museum`
  - [x] stop hotter outfit carryover in `women cultural_bookish + museum`
  - [x] stop `bodysuit_trousers` from surfacing in `women luxury + hotel lobby`
  - [x] stop cardigan / soft daywear carryover from surfacing in `women nightlife`
- [x] Done: couples exact-theme scene-outfit coherence pass for calm interiors and nightlife
  - [x] stop `tennis polo / pleated tennis skirt` from surfacing in `couples lifestyle + bookish / museum` and similar calm interiors
  - [x] stop cardigan / soft daywear carryover from surfacing in `couples nightlife`
  - [x] push the safer couples `lifestyle / luxury / nightlife` outfit logic deeper into candidate selection, not only final rendering
- [x] Done: make runtime memory writes safe under parallel `generate_run`
  - [x] write `backend/engine/runtime/memory.json` atomically or behind a file lock so concurrent runs do not expose empty JSON
- [x] P1: finish couples `different_persons` identity hardening on the male side
  - [x] score male-side `age / race` against a deterministic legacy preview during batch selection, not only final render
  - [x] expose effective male-side age / ethnicity in debug so the stricter path is visible in smoke checks
  - [x] expand the male-side hairstyle / outfit bank and route supported styles through the data-driven male styling bank instead of relying only on the narrow hardcoded legacy outfit map
  - [x] add the next couple-side appearance additions after the male-side bank expansion
- [x] P2: close the dedicated men taste pass after the women / couples coherence cleanup
  - men romantic/luxury/nightlife now use broader treatment remap pressure and less-collapsed outfit/pose selection.

- [ ] Couples:
  - [x] do a women-side scene / outfit coherence pass for `lifestyle / luxury / nightlife`; the current exact-theme retest no longer shows `tennis` in museum lifestyle, `bodysuit_trousers` in calm luxury, or cardigan carryover in nightlife after the deeper candidate-selection bans
  - [x] make `different_persons` stricter for both sides, not just a soft batch bias; female-side `age / race` remain hard-constrained during candidate search, and male-side explicit constraints now enforce non-hard-fail seed selection.
  - [x] expand the male appearance block beyond `maleHairLength`
  - [x] add male-side outfit / grooming controls if the current legacy path stays too narrow
  - [x] expand the male-side hairstyle / outfit bank with additional live options and move supported style routing onto data-bank entries before hardcoded fallback
  - [x] review couples luxury / lifestyle / nightlife taste quality on bigger sweeps, not only smoke runs
  - [x] expand couples interaction intensity for `spicyLevel 5-8` while keeping `1-4` in the current moderate-safe range
    - couples now use a dedicated live `couple_interactions` bank with style/scene-compatible `revealing` and `pushing_it` lanes gated by spicy level at render time
  - [~] keep tuning couples lifestyle color spread; this pass fixed the worst `clean_neutrals` collapse, but broader color taste can still improve later
  - [~] keep tuning `couples lifestyle` taste; the mode is no longer too clean-heavy, but occasional sporty-leaning women-side outfits can still surface
  - [x] close the remaining `couples random` reveal leak in final rendered prompt output
  - [x] tone down `couples lifestyle` female outfit routing so it stays more everyday and less accidentally revealing at render level
  - [x] push the safer `couples lifestyle` outfit logic deeper into candidate selection, not only final rendering
  - [x] add a much broader couples interaction / pose bank instead of overusing the current near-standing variants
  - [x] add more true two-person poses: standing side by side holding hands, closer embrace variants, hand-at-waist variants, seated-together variants, woman sitting on his lap, leaning-against-him variants, walking-together variants
  - [x] separate calm / romantic / nightlife / sporty couple pose families so interaction style matches scene and styling better

- [ ] Men:
  - [x] do a dedicated taste pass for `luxury / nightlife / romantic`; updated remap pressure plus diversified deterministic outfit/pose selection removed the strongest romantic template collapse.
  - [x] decide whether low-spicy men also need calmer mood routing; `luxury / nightlife / romantic` now stay on calm / soft moods at `spicyLevel=3`
  - [x] decide whether men need explicit race/name/age UI polish similar to couples-side male controls
  - [x] enlarge male pose variety for `luxury` and `romantic`
  - [x] expand the generated hairstyle / outfit bank with more explicit male controls and let supported styles pull from the live male styling bank before fallback
  - [x] keep tuning men `romantic`; pose/outfit spread is now broader in repeated smoke runs.
  - [x] rebalance `men romantic` treatments; remap pressure now keeps romantic out of clean-commercial collapse more consistently.
  - [x] do a broader stylization/taste pass for `men random`; the live random pool now keeps a wider lifestyle / creative / nightlife / coastal mix without over-leaning on luxury defaults
  - [x] broaden `men romantic` outfit spread; repeated smoke runs no longer collapse heavily into two templates.

- [ ] Women:
  - [x] do a dedicated scene / outfit coherence pass for `lifestyle / cultural_bookish / luxury / nightlife`; the current exact-theme smoke checks and x20 sweeps no longer show `mini_dress` / `bodysuit_trousers` in museum or luxury runs or cardigan/daywear carryover in nightlife
  - [x] expand women high-spicy pose coverage for `spicyLevel 7-8`
  - [x] expand women high-spicy outfit coverage for `spicyLevel 7-8`
  - [~] keep tuning repeated outfit-family pressure so low-spicy batches diversify not only by color/material but also by silhouette; this pass improved the worst romantic/nightlife tails, but broad random/luxury silhouette taste can still improve later
  - [~] review whether `cardigan_skirt` should stay in reserved mode long-term or be replaced by a cleaner modest family; it is now removed from romantic and balanced-reveal bias, but the broader reserved pool can still be revisited later
  - [x] do the next women relevance pass on `lifestyle / romantic / creative_artistic / fitness`
  - [x] nightlife women no longer leak swimwear, and the first nightlife diversity pass is done with new non-swim outfit families plus darker evening palettes
  - [x] remove the last nightlife wording leaks (`tiny mini skirt`, `latex`) so women nightlife runs stay clean in repeated `x20` stress retests
  - [ ] keep rebalancing nightlife women weights; the latest pass is clean now, but `mini_dress` spread and overall taste can still be improved later
  - [x] remove the worst default random/lifestyle reveal leaks so broad sweeps no longer produce bikini/swimsuit/latex wording outside the modes that really need it
  - [x] broaden `women random` and `women luxury` outfit/color diversity with new live outfits, materials, and richer palettes
  - [x] tighten `women luxury` mini_dress pressure; the luxury exact-theme smoke check now stays at `mini_dress <= 2`, while `women random` can still use a later taste pass
  - [x] do a dedicated treatment rebalance for `women romantic`; scene-aware remaps plus new `coastal_pool` treatment allowances removed the old clean-commercial collapse in the latest stress retests
  - [x] broaden `fitness` women with a larger sporty-safe urban/wellness setting pool without breaking the athletic route
  - [x] rebalance `women fitness` treatment mix; `wellness_spa` now remaps into candid/analog/documentary lanes instead of falling back to `clean_commercial`
  - [~] keep taste-tuning `romantic` and `creative_artistic`; the major leaks are fixed, but final silhouette balance can still improve later
  - [x] expand women random color-story library and clamp exact repeated color pairs inside a batch; postprocess no longer drags random women back into the old beige/navy/pink palette loop
  - [ ] do a dedicated sport/fitness semantic pass so activewear, active poses, and gym/stadium/track/outdoor-run locations match each other instead of leaking into locker-room or luxury-interior nonsense

- [ ] Lighting / Stylization:
  - [x] save staged rollout plan in `STYLIZATION_IMPLEMENTATION_PLAN.md`
  - [x] phase 1: add internal `photo_treatment` bank and wire it into render/debug for women / men / couples without touching UI
  - [x] phase 2: let `photo_treatment` softly influence candidate selection and scene/light compatibility instead of being render-only
  - [x] phase 3: run large-batch sweeps and do the first balancing pass using real treatment-distribution metrics
  - [x] redesign default random output mix so it is not mostly clean stock/editorial
  - [~] target rough default split: about `40%` polished professional / stock-like, about `60%` more stylized / expressive looks in final `generate_run(random)` output, not only in raw generator sweeps
  - [~] follow-up rebalance for `luxury`; the latest pass improved it, but `clean_commercial` still over-prefers `men luxury` more than it should
  - [~] follow-up rebalance for `couples random`; the latest targeted pass pushed it much closer to the intended stylized mix, but later taste-tuning can still improve treatment spread and consistency
  - [x] add explicit stylization lanes instead of hoping current randomization discovers them on its own
  - [x] add concept-photo lane with stronger stylized framing / mood / lighting logic
  - [x] add selfie / phone-camera lane with believable casual optics and composition
  - [x] add darker low-light / night-photo lane that still keeps faces readable
  - [x] add direct-light / hard-shadow lane
  - [x] add studio seamless-background lane with stronger stylized portrait behavior
  - [ ] add more lighting play in the random pool: direct flash, practical lights, colored ambient, moody darkness, tighter spotlight, silhouette-ish setups where appropriate
  - [ ] make stylization interact sanely with scene/style mode so it does not create nonsense combinations
  - [~] run large-batch relevance sweeps after this pass and log how often each stylization lane appears; aggregate passes are done, but more rebalancing is still needed mainly for `men romantic / couples random`
  - [~] large-batch sweeps now show `couples random` in a much better place, and `women lifestyle / women fitness` also improved; next stylization follow-up should focus more on `women random / women romantic / men random / men nightlife / couples lifestyle`
  - [x] expose `photo treatment` in UI as an optional stylization control

- [ ] Shared engine / UI:
  - [x] make `backend/engine/runtime/memory.json` writes atomic / locked so concurrent runs cannot trigger transient `JSONDecodeError`
  - [x] `Appearance mode` (`Generated / Custom`) for the full appearance block
  - [x] richer debug readout with effective per-prompt decisions
  - [x] align legacy men debug decisions with the actual rendered male outfit / pose / hair instead of scaffold-only women-side fields
  - [x] re-chunk the control column into `Subject -> Spicy level -> Appearance -> Batch -> Scene -> Stylization`
  - [x] remove the outer `Output` shell so the right column starts directly with `Latest prompts`
  - [x] move the latest prompt count next to `Copy all`
  - [x] switch random hair-color picking to natural-only output by default
  - [x] browser-level UI verification with headless Playwright smoke/screenshots
  - [x] replace native `select` popups with a real custom combobox/dropdown so opened menus also match the UI kit, not only the closed field
  - [x] review `same_person` lock granularity for female outfit / hair / color so it does not feel wrongly sticky
  - [x] wire the new `Eye color` UI control into the engine
  - [x] wire the new `Breast size` UI control into the engine
  - [x] add an `Extra large` breast-size preset with stronger repeated render wording for models that respond better to weighted phrasing
  - [x] expand race presets beyond broad groups with a curated top-nationality dropdown plus proper routing
  - [x] refactor content banks so locations / poses / hair / makeup are easier to extend without touching generator logic
  - [x] split content loading into `core / drafts / overrides`
  - [x] support `status` and `source` fields in new content-bank entities
  - [x] promote reviewed draft banks into live routing in small batches
  - [x] committed Playwright E2E coverage for live custom-select flows
  - [x] keyboard-accessible combobox navigation and ARIA state wiring for custom selects
  - [x] sync the visible topbar name with the document title so the app does not show two product names at once
  - [x] collapse service UI by default (`Debug`, `Line-banks`, `History`) so the main flow stays focused on generation instead of support tooling
  - [x] move the next hairstyle / makeup / outfit additions into draft fragments instead of editing large core banks directly
  - [x] move the next ethnicity / subject additions into draft fragments instead of editing the core subjects bank directly
  - [x] add the next couple-side and male-side appearance additions through draft fragments first
  - [ ] couples prompts are still materially longer than women/men prompts in large sweeps, but this is now low priority because Z-Image/ComfyUI prompt length is acceptable; only revisit if quality/readability suffers
  - [x] rebalance `styleMode=random` so broad random batches hold a brighter outdoor-heavy mix with explicit `water / nature` shares, lower interior dominance, and less cheap flat commercial fallback
