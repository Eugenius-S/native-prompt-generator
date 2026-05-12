# Scene / Outfit / Pose / Portrait Follow-Up Plan

For agentic workers. Keep changes small, local-test every stage, and commit after each finished step.

## Goal

Fix the newly surfaced realism / framing regressions without patching isolated examples one by one.

The failures fall into four linked buckets:

1. support / prop mismatch
2. outfit-to-scene mismatch
3. portrait framing too face-close
4. arms-up women poses lacking a clean underarm cue

## Execution Order

1. `#105` — support / prop semantic hardening
2. `#100` — outfit-to-scene semantic hardening
3. `#107` — remove face-close portrait crops from automatic portrait lanes
4. `#108` — clean-shaven underarm rule for women arms-up poses

This order matters. The first two fix structural realism. The last two are narrower beauty/render passes.

## Stage 1 — `#105` Support / Prop Semantic Hardening

Status:
- [x] done
- [x] `mirror/sink` support now requires a real vanity-style scene support
- [x] `bed/mattress` support regressions kept covered
- [x] selector-level `chair` support regressions now covered too

### Problem

Poses that require a real support object still leak into scenes that do not contain that support.

Examples:
- sink / mirror support pose on a highway shoulder
- kneeling-on-bed / mattress pose in a canyon scene

### Direction

Do not hardcode only those examples.

Instead:
- strengthen pose support taxonomy
- strengthen scene support-object taxonomy
- require compatibility before the candidate survives

### Likely Files

- `backend/engine/line_bank_loader.py`
- `backend/engine/selectors.py`
- `backend/services/scoring.py`
- pose-bank / line-bank normalization helpers if needed

### Tasks

- audit current pose support tags vs. what the scene matcher actually enforces
- make `sink`, `mirror vanity`, `bed`, `mattress`, `chair`, `counter`, `bench`, `railing` style supports explicit where needed
- block pose families that require those supports when the scene does not have them
- add focused local regressions for:
  - roadside + sink/mirror pose
  - canyon + bed/mattress pose
  - roadside + chair pose

## Stage 2 — `#100` Outfit-To-Scene Semantic Hardening

Status:
- [x] done
- [x] stronger mismatch coverage for pool / beach / sporty training / lab-industrial contexts
- [x] added focused regressions for tailored-bodysuit pool looks, sporty shirt-trousers, lab+dressy nightlife, and lingerie-like beach outfits
- [x] widened scene/outfit tags now also cover aquarium tunnel, private dining room, and fire-stair landing mismatches without case-by-case bans

### Problem

Outfit families and scene families still combine into socially or functionally wrong prompts.

Examples:
- blazer/bodysuit in aquarium tunnel
- evening dress in laboratory
- linen-shirt/trousers in boutique gym
- underwear-like beach output that is not swimwear
- lounge camisole + tiny shorts on a fire stair landing

### Direction

Do not solve this with a pile of exact prompt bans.

Instead:
- classify outfits by context
- classify scenes by context
- score compatibility between them early
- do a small line-bank cleanup only after the matcher is stronger

### Likely Files

- `backend/services/scoring.py`
- `backend/services/selection_scoring.py`
- `backend/engine/selectors.py`
- relevant women / men / shared line-bank outfit files

### Tasks

- define / reuse outfit context tags such as:
  - `swim`
  - `lingerie_or_underwear`
  - `lounge`
  - `tailored`
  - `nightlife`
  - `fitness`
  - `resort`
  - `casual_day`
  - `editorial_only`
- define / reuse scene context tags such as:
  - `water_leisure`
  - `dining`
  - `lab_industrial`
  - `fitness`
  - `residential`
  - `nightlife`
  - `resort`
- penalize obvious context mismatches early
- then audit newly added outfit line-banks against the new matcher
- add focused local regressions for the concrete examples above

## Stage 3 — `#107` Automatic Portrait Cleanup

Status:
- [x] done
- [x] `face_only` removed from automatic portrait pools
- [x] random and `more_portraits` keep chest-up / head-and-shoulders defaults instead of face-dominant crops
- [x] manual `face_only` rendering path kept intact for direct candidates and targeted tests

### Problem

Automatic portrait lanes still sometimes render too close to the face.

### Direction

Keep portrait defaults attractive:
- head-and-shoulders
- chest-up / slightly below chest

Do not let `face close-up` / `tight beauty headshot` survive in normal automatic portrait pools.

### Likely Files

- `backend/engine/render/prompt_renderer.py`
- framing selection / scheduling code if needed
- portrait smoke tests

### Tasks

- [x] remove face-close wording from automatic portrait pools
- [x] keep anti-head-cut safety
- [x] validate that normal portrait output stays chest-up instead of face-dominant

## Stage 4 — `#108` Women Arms-Up Hygiene Rule

Status:
- [x] done
- [x] raised-arm women poses now add a narrow `clean-shaven underarms` cue in the render layer
- [x] non-raised-arm prompts stay unchanged

### Problem

Women arms-up poses can produce visible underarm hair in glam/polished output.

### Direction

Keep this narrow and cheap:
- only women
- only poses that clearly expose underarms
- render-level hygiene cue

### Likely Files

- `backend/engine/render/prompt_renderer.py`
- pose tagging helpers if needed

### Tasks

- [x] detect `arms_up` / `underarm_visible` poses
- [x] add `clean-shaven underarms` style wording in those cases
- [x] verify non-arms-up prompts do not change

## Validation Rules

- local tests only
- no GitHub Actions
- after each stage:
  - run targeted tests
  - commit
  - update `PROJECT_PLAN.md`
  - close only the issue that is truly finished

## Suggested Minimal Validation Per Stage

- `#105`: support/scene regressions + a small route smoke
- `#100`: outfit/scene regressions + one broad women random smoke
- `#107`: portrait framing smoke
- `#108`: render smoke for women arms-up vs non-arms-up
