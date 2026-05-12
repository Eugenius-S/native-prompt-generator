# Architectural Refactor Skeleton Plan - 2026-04-21

## Mission

- Build a backend/frontend skeleton that makes future changes and new module integration easier.
- Preserve current runtime behavior while restructuring code.
- Keep prompt taste, scoring behavior, API payloads, and stored data stable during this stage.

## Read This First After Model Switch

1. Read this file from top to bottom.
2. Read `PROJECT_PLAN.md` for the live project queue.
3. Run `git status --short` and identify unrelated dirty files before staging anything.
4. Run the phase-gate tests listed below before and after each extraction step.
5. Continue from the first unchecked item in the progress tracker. Do not skip ahead.

## Non-Goals For This Stage

- No feature additions.
- No prompt wording redesign beyond already-approved bugfixes.
- No scoring rebalance.
- No content bank schema rewrite.
- No framework migration such as React, Vue, or TypeScript.
- No renaming of public API endpoints or form keys.
- No changes to `history.json` or `presets.json` payload shape.

## Current Hotspots

| Area | File | Approx. lines | Main problem | First extraction target |
|---|---|---:|---|---|
| Backend orchestration | `backend/prompt_service.py` | 3755 | Form normalization, runtime controls, scoring, postprocess, debug, bootstrap, presets, and run orchestration all live in one file | `backend/forms/`, `backend/services/`, `backend/modes/` |
| Generator core | `backend/engine/generator.py` | 2285 | Data loading, selection predicates, candidate build, memory, and render live together | Follow-up after skeleton stage |
| Legacy men/couples path | `backend/legacy_people.py` | 1230 | Identity build and render path are coupled to legacy orchestration shape | `backend/modes/men.py`, `backend/modes/couples.py` wrappers |
| Frontend app shell | `frontend/app.js` | 1516 | State, API, components, sections, render orchestration, and event handling all live together | `frontend/state/`, `frontend/api/`, `frontend/components/`, `frontend/sections/` |
| Frontend CSS | `frontend/styles.css` | 873 | Tokens, layout, controls, output, and utility styles live together | Split after JS skeleton is stable |
| HTTP entry | `app.py` | 109 | HTTP handler and process startup live in the same file | `backend/api/http_handler.py` |

## Refactor Invariants

- Keep `/api/bootstrap`, `/api/generate`, and `/api/presets` unchanged.
- Keep `get_bootstrap()`, `generate_run()`, `save_preset_record()`, and `delete_preset_record()` callable from the existing import sites until the facade is retired.
- Keep the `DEFAULT_FORM_STATE` keys and current UI option ids unchanged.
- Keep the current `candidate` dictionary shape unchanged until the later engine split phase.
- Keep `backend/prompt_service.py` as the compatibility facade until the end of the backend skeleton stage.
- Keep `frontend/app.js` as the browser entry file until the end of the frontend skeleton stage.
- Make one logical extraction per commit.
- Do not combine backend and frontend behavior changes in the same commit.
- Add or update characterization tests before moving code that has no direct test coverage.

## Current Public Entry Points

- HTTP endpoints:
  - `GET /api/bootstrap` -> bootstrap payload with `defaults`, `options`, `enabledFields`, `disabledFields`, `presets`, `history`.
  - `POST /api/generate` -> `{ "run": generate_run(formState) }`.
  - `POST /api/presets` -> `{ "preset": save_preset_record(name, formState) }`.
  - `DELETE /api/presets?id=...` -> `{ "ok": true }`.
- Backend facade exports in `backend/prompt_service.py`:
  - `get_bootstrap()`
  - `generate_run(form_payload)`
  - `save_preset_record(name, form_state)`
  - `delete_preset_record(preset_id)`
- Startup entry:
  - `app.main()`
  - `app.PromptGeneratorHandler` remains importable until Phase 1 is complete.

## Target Skeleton After This Stage

```text
backend/
  api/
    http_handler.py
  services/
    bootstrap_service.py
    run_service.py
    preset_service.py
    debug_summary.py
  forms/
    constants.py
    normalizer.py
    runtime_controls.py
    user_profile.py
  modes/
    registry.py
    women.py
    men.py
    couples.py
  prompt_service.py        # thin compatibility facade

frontend/
  api/
    client.js
  state/
    store.js
  components/
    controls.js
    cards.js
    icons.js
  sections/
    subject.js
    scene.js
    stylization.js
    output.js
  controllers/
    form_controller.js
  layout/
    shell.js
  app.js                   # thin module entry
```

## Phase-Gate Tests

Run these before the first extraction in a phase and again after the phase commit.

### Backend gate

```powershell
python -m pytest tests/test_routing_validation_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_clothing_color_rendering_smoke.py -q
```

### Frontend gate

```powershell
npm run test:e2e -- tests/e2e/form-controls.spec.js
```

### Optional broader confidence gate before merging the whole skeleton stage

```powershell
python -m pytest tests/test_men_taste_smoke.py tests/test_women_high_spicy_smoke.py -q
```

## Execution Strategy

### Phase 0 - Safety Net And Public Contract Freeze

Goal: make structural moves safe before touching architecture.

- [x] P0.1 Add a smoke test that freezes the top-level `/api/bootstrap` payload keys.
- [x] P0.2 Add a smoke test that freezes the top-level `generate_run()` payload shape: `timestamp`, `formState`, `outputText`, `prompts`, `debug`.
- [x] P0.3 Add a smoke test that verifies `history` and `presets` still serialize as lists of dicts with current keys.
- [x] P0.4 Write down the current public entry points in this file and do not rename them during the skeleton stage.
- [x] P0.5 Confirm the backend and frontend gates are green before any extraction.

### Phase 1 - Backend Entry And Facade Skeleton

Goal: separate HTTP entry and service facade without changing behavior.

- [x] P1.1 Create `backend/api/http_handler.py` and move `PromptGeneratorHandler` there.
- [x] P1.2 Reduce `app.py` to process startup, host/port parsing, and server boot only.
- [x] P1.3 Create `backend/services/bootstrap_service.py` and move `get_bootstrap()` there.
- [x] P1.4 Create `backend/services/preset_service.py` and move `save_preset_record()` and `delete_preset_record()` there.
- [x] P1.5 Keep `backend/prompt_service.py` exporting the same public functions by delegating to the new service modules.
- [x] P1.6 Run backend gate and commit only this entry/facade move.

### Phase 2 - Backend Form Skeleton

Goal: pull form parsing and runtime-control decisions out of `prompt_service.py`.

- [x] P2.1 Create `backend/forms/constants.py`.
  - Move the `ALLOWED_*` sets and alias maps that only validate or normalize form inputs.
- [x] P2.2 Create `backend/forms/normalizer.py`.
  - Move `_parse_bool()`.
  - Move `_normalize_choice()`.
  - Move `_safe_int()`.
  - Move `_clean_text()`.
  - Move `_tokenize_text()`.
  - Move `_female_appearance_mode()`.
  - Move `_male_appearance_mode()`.
  - Move `_female_appearance_prompt()`.
  - Move `_male_appearance_prompt()`.
  - Move `_male_outfit_control_value()`.
  - Move `_female_custom_appearance_active()`.
  - Move `_male_custom_appearance_active()`.
  - Move `_merged_form_state()`.
- [x] P2.3 Create `backend/forms/runtime_controls.py`.
  - Move `_effective_spicy_level()`.
  - Move `_location_strategy_flags()`.
  - Move `_anti_repeat_profile()`.
  - Move `_resolve_runtime_controls()`.
  - Move `_effective_outfit_reveal()`.
  - Move `_effective_makeup_control()`.
  - Move `_infer_theme_style_mode()`.
  - Move `_matched_theme_hints()`.
  - Move `_exact_theme_scene_constraints()`.
- [x] P2.4 Create `backend/forms/user_profile.py`.
  - Move `_merge_preference_sets()`.
  - Move `_user_style_profile()`.
- [x] P2.5 Replace direct internal calls in `backend/prompt_service.py` with imports from the new form modules.
- [x] P2.6 Run backend gate and commit only this form extraction.

### Phase 3 - Backend Run Skeleton

Goal: separate orchestration, mode dispatch, and debug summary from the huge facade file.

- [x] P3.1 Create `backend/modes/registry.py` with a small `ModeHandler` interface.
  - Required methods: `build_profile()`, `render_prompt_batch()`, `post_render_batch()`.
- [x] P3.2 Create `backend/modes/women.py` as a thin wrapper around the current women render path.
- [x] P3.3 Create `backend/modes/men.py` as a thin wrapper around the current legacy men render path.
- [x] P3.4 Create `backend/modes/couples.py` as a thin wrapper around the current legacy couples render path.
- [x] P3.5 Create `backend/services/debug_summary.py`.
  - Move `_photo_treatment_lookup()`.
  - Move `_style_debug_signals()`.
  - Move `_treatment_debug_signals()`.
  - Move `_summarize_debug()`.
- [x] P3.6 Create `backend/services/run_service.py`.
  - Move `_render_mode_prompts()`.
  - Move `generate_run()`.
  - Keep the heavy scoring and batch-selection functions in `prompt_service.py` for now.
- [x] P3.7 Reduce `backend/prompt_service.py` to a compatibility facade plus still-unmoved scoring/postprocess blocks.
- [x] P3.8 Run backend gate and commit only this orchestration split.

### Phase 4 - Frontend Module Entry Skeleton

Goal: create a safe ES-module entry and isolate state and API first.

- [x] P4.1 Change `frontend/index.html` to load `app.js` as `type="module"`.
- [x] P4.2 Create `frontend/api/client.js`.
  - Move `request()`.
  - Add thin wrappers: `loadBootstrap()`, `generateRun()`, `savePresetRequest()`, `deletePresetRequest()`.
- [x] P4.3 Create `frontend/state/store.js`.
  - Move the `state` object.
  - Move `clone()`.
  - Move `disabledFields()`.
  - Move `isDisabled()`.
- [x] P4.4 Keep `frontend/app.js` as the only browser entry and import the new modules from there.
- [x] P4.5 Run frontend gate and commit only this entry/state/API split.

### Phase 5 - Frontend UI Skeleton

Goal: split controls, sections, and controller logic while preserving current markup.

- [x] P5.1 Create `frontend/components/icons.js`.
  - Move `ICONS`.
  - Move `iconMarkup()`.
- [x] P5.2 Create `frontend/components/controls.js`.
  - Move `optionMarkup()`.
  - Move `resolveOption()`.
  - Move `withLegacyCurrentOption()`.
  - Move dropdown helper functions.
  - Move `selectControl()`.
  - Move `field()`.
  - Move `segmentedControl()`.
- [x] P5.3 Create `frontend/components/cards.js`.
  - Move `promptPreviewMarkup()`.
- [x] P5.4 Create `frontend/sections/subject.js`.
  - Move `renderModeButtons()`.
  - Move `renderSubject()`.
  - Move `renderCoreIdentity()`.
- [x] P5.5 Create `frontend/sections/scene.js`.
  - Move `renderIntensitySection()`.
  - Move `renderBatch()`.
  - Move `renderSceneSection()`.
  - Move `renderStylizationSection()`.
- [x] P5.6 Create `frontend/sections/output.js`.
  - Move `renderPresetSection()`.
  - Move `renderDebugSection()`.
  - Move `renderActionDock()`.
  - Move `renderTopbar()`.
  - Move `renderDebugPanel()`.
  - Move `renderLatestPrompts()`.
  - Move `renderPresets()`.
  - Move `renderHistory()`.
  - Move `renderOutputPanel()`.
- [x] P5.7 Create `frontend/controllers/form_controller.js`.
  - Move `normalizeFormDependencies()`.
  - Move `resetForm()`.
  - Move exact-theme helpers.
  - Move `setField()`.
  - Move personalization helpers.
  - Move `generate()`.
  - Move `savePreset()`.
  - Move `removePreset()`.
  - Move `copyText()`.
- [x] P5.8 Reduce `frontend/app.js` to render composition, bootstrap, and event delegation only.
- [x] P5.9 Run frontend gate and commit only this section/controller split.

### Phase 6 - Follow-Up After Skeleton Stage Is Stable

This is explicitly out of scope for the first structural pass, but it is the next logical wave.

- [x] P6.1 Split `backend/engine/generator.py` into `data_loader.py`, `selectors.py`, `candidate_builder.py`, and `render/` modules.
  - 2026-04-21 completion: added `backend/engine/selectors.py` and `backend/engine/candidate_builder.py`, moved selector/profile/normalization plus candidate/batch orchestration behind those modules, and kept `generator.py` as the compatibility surface.
  - Validation: `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_public_contract_smoke.py tests/test_runtime_memory_atomicity.py tests/test_clothing_color_rendering_smoke.py tests/test_routing_validation_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_couples_scene_coherence_smoke.py -q` -> `27 passed`.
- [x] P6.2 Split the still-heavy parts of `backend/prompt_service.py` into scoring, postprocess, and batch-selection modules.
  - 2026-04-21 completion: added `backend/services/scoring.py`, `backend/services/postprocess.py`, and `backend/services/batch_selection.py`, then rewired the heavy `backend/prompt_service.py` helper surface into compatibility delegates so existing callers stay stable.
  - Validation: `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_public_contract_smoke.py tests/test_runtime_memory_atomicity.py tests/test_clothing_color_rendering_smoke.py tests/test_routing_validation_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_men_taste_smoke.py tests/test_women_high_spicy_smoke.py -q` -> `34 passed`.
- [x] P6.3 Split `frontend/styles.css` into tokens, layout, controls, and output styles.
  - 2026-04-21 completion: added `frontend/styles/tokens.css`, `frontend/styles/layout.css`, `frontend/styles/controls.css`, and `frontend/styles/output.css`, then converted `frontend/styles.css` into the stable `@import` entry so the existing browser load path stays unchanged.
  - Validation: `npm run test:e2e -- tests/e2e/form-controls.spec.js` -> `5 passed`.
- [x] P6.4 Rename legacy wrappers only after the new mode registry is stable.
  - 2026-04-21 completion: renamed `WOMEN_MODE_HANDLER`, `MEN_MODE_HANDLER`, and `COUPLES_MODE_HANDLER` to neutral `*_HANDLER` exports, updated `backend/modes/registry.py`, and replaced lingering men/couples wrapper-local `render_legacy_batch` / `legacy_prompts` aliases with mode-neutral names while preserving the existing legacy render implementation behind the wrappers.
  - Validation: `C:/Users/jiraf/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_public_contract_smoke.py tests/test_routing_validation_smoke.py tests/test_couples_scene_coherence_smoke.py tests/test_men_debug_scaffold_smoke.py tests/test_clothing_color_rendering_smoke.py -q` -> `26 passed`.

## File Ownership Map

| Current responsibility | Current file | Target file | Phase |
|---|---|---|---|
| HTTP handler | `app.py` | `backend/api/http_handler.py` | 1 |
| Bootstrap and preset facade | `backend/prompt_service.py` | `backend/services/bootstrap_service.py`, `backend/services/preset_service.py` | 1 |
| Form normalization | `backend/prompt_service.py` | `backend/forms/normalizer.py` | 2 |
| Runtime controls | `backend/prompt_service.py` | `backend/forms/runtime_controls.py` | 2 |
| User profile assembly | `backend/prompt_service.py` | `backend/forms/user_profile.py` | 2 |
| Mode dispatch | `backend/prompt_service.py` | `backend/modes/registry.py` | 3 |
| Debug summary | `backend/prompt_service.py` | `backend/services/debug_summary.py` | 3 |
| Run orchestration | `backend/prompt_service.py` | `backend/services/run_service.py` | 3 |
| Browser state | `frontend/app.js` | `frontend/state/store.js` | 4 |
| Browser API | `frontend/app.js` | `frontend/api/client.js` | 4 |
| Shared UI controls | `frontend/app.js` | `frontend/components/controls.js` | 5 |
| UI sections | `frontend/app.js` | `frontend/sections/*.js` | 5 |
| Form actions | `frontend/app.js` | `frontend/controllers/form_controller.js` | 5 |

## Commit Plan

Use one commit per checked block below.

1. `Extract HTTP handler and service facade shell`
2. `Extract backend form normalization module`
3. `Extract backend runtime controls and user profile modules`
4. `Introduce backend mode registry and run service`
5. `Convert frontend entry to ES modules and extract store/api`
6. `Extract frontend controls and icon modules`
7. `Extract frontend sections and controller shell`

Do not stage unrelated dirty files during these commits.

## Known Risks And How To Avoid Them

### Circular imports

- `backend/prompt_service.py` currently imports `legacy_people` and `generator`.
- New service modules must not import `prompt_service.py` back.
- Keep dependency direction one-way: entry/facade -> services/forms/modes -> engine/legacy.

### Hidden frontend coupling

- `frontend/app.js` mixes render and mutation logic.
- Extract state and API first before moving section renderers.
- Keep event delegation in `app.js` until the section split is finished.

### ES module boot risk

- The frontend split is much easier if `frontend/index.html` loads `app.js` as `type="module"`.
- Make this change in its own commit and verify the page still boots before any larger JS move.

### Oversized commit risk

- A commit that moves both logic and naming at once will be hard to review and hard to roll back.
- If a move also changes behavior, split it into two commits: move first, behavior fix second.

## Definition Of Done For The Skeleton Stage

- `app.py` is a small startup entry instead of the handler implementation.
- `backend/prompt_service.py` becomes a thin facade and orchestration file, not a 3700-line mixed-control monolith.
- `frontend/app.js` becomes a thin entry module instead of holding all state, components, and controllers.
- Public API payloads stay unchanged.
- Backend gate and frontend gate both pass.
- The next model can continue from the first unchecked checklist item in this file without needing to rediscover structure decisions.

## Operator Recommendation

- Stop the first skeleton stage after Phase 5 even if there is still time.
- Do not start the deeper `generator.py` split until the new backend/services and frontend module boundaries are stable.
- The first success condition is not smaller code by itself; it is stable seams that allow later refactors without rediscovering the whole repo.
