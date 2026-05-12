# Generator System Spec

Purpose: build a standalone prompt generator with deep randomization, semantic validation, anti-repeat control, and a chat-driven operator workflow.

This is not a prompt library.
This is the blueprint for how the generator should think and assemble prompts.

## Target Workflow

Normal operating mode:

1. user gives a task
2. Codex adjusts data, weights, bans, or routes
3. generator produces drafts
4. validator catches mismatches
5. repair pass fixes drafts
6. Codex reviews weak spots and updates rules
7. final prompts are returned

Short version:

- standalone generator = engine
- chat = operator, editor, debugger, and taste correction layer

## Core Rule

Randomization must happen across the whole prompt structure, not just on the surface.

Bad:

- one fixed shell
- random woman
- random hair color
- random outfit color

Good:

- scene family
- setting
- base space
- setting material accent
- setting detail accent
- atmosphere cue
- micro-setting
- material language
- prop cluster
- subject casting
- body and beauty read
- hair
- styling
- outfit family
- pose family
- hand action
- framing
- camera angle
- light family
- time of day
- mood
- capture style

## Assembly Pipeline

```text
compose -> validate_semantics -> repair -> validate_repetition -> output
```

## Layer Model

Every prompt should be assembled from modular layers.

```text
route
subject
age_band
ethnicity
body_type
beauty_level
hair_color
hair_structure
makeup_style
outfit_family
material
color_story
setting_macro
scene_family
setting_micro
prop_cluster
pose_family
hand_action
camera_framing
camera_angle
lighting_family
time_of_day
surface_state
mood_energy
capture_style
lens_look
```

## Route Presets

Routes prevent nonsense combinations and keep generation coherent.

Base route list:

- casual_candid
- slutty_lifestyle
- studio_portrait
- luxury_interior
- sports_flirt
- amateur_phone
- cinematic_night
- fantasy_cosplay
- sci_fi_character
- sweet_soft

## Identity Lock Mode

Some batches need one stable model in different looks.

In identity-lock mode:

- keep the same identity core across the batch
- identity core means age band, ethnicity group, ethnicity, body type, and beauty level
- allow variation in hair color, hair structure, makeup, outfit, setting, pose, framing, and light

Use this when the user wants:

- one model in different looks
- one girl across many settings
- outfit and styling exploration without changing who she is

Each route defines:

- allowed setting families
- allowed outfit families
- allowed pose families
- allowed light families
- banned combinations
- style intensity range

## Data Model For Entries

Every item in the generator bank should store compatibility metadata.

```json
{
  "id": "marble_primary_bathroom",
  "layer": "setting_micro",
  "value": "marble primary bathroom with a sculptural tub, deep veining, built-in bench, arched doorway, soft reflected daylight",
  "tags": ["indoor", "luxury", "bathroom", "stone", "dry_or_wet_possible"],
  "weight": 0.8,
  "rarity": "common",
  "requires_any_tags": ["interior", "luxury_interior", "hotelized_living"],
  "forbids_any_tags": ["sports_field", "industrial_garage"],
  "soft_conflicts": ["gritty_documentary"],
  "used_recently_score": 0
}
```

## Weighted Randomization

Do not use flat random choice.

Use:

- base weight
- rarity modifier
- route modifier
- recent-use penalty
- similarity penalty
- user-priority bonus

High-level logic:

```text
effective_weight =
base_weight
* route_bonus
* user_bonus
* rarity_bonus
- recent_use_penalty
- similarity_penalty
```

## Two-Stage Composition

Generate in two passes.

Pass 1: macro frame

- route
- scene family
- outfit family
- pose family
- framing
- energy

Pass 2: detail fill

- setting macro
- base space
- setting material
- detail accent
- atmosphere cue
- hair
- hand action
- surface state
- lighting details
- lens look

This prevents fake variety where only hair or nationality changes inside the same shell.

## Scene Family Planning

Do not pick locations as flat isolated ids.

First pick a scene family, then a base space inside that family.

Examples of scene families:

- residential_luxury
- hospitality_suite
- grooming_bath
- culture_bookish
- creative_gallery
- garden_conservatory
- courtyard_garden
- urban_daylight
- coastal_pool
- coastal_boardwalk
- wellness_spa
- nightlife_bar
- nightlife_neon
- studio

This is the main fix against comfort-setting dominance.
The generator should reduce repetition at the family level first, not only at the exact location id level.

## Semantic Validation

Validator must check internal logic, not only syntax.

Validation classes:

- hard_conflict
- soft_conflict
- style_warning
- repeat_warning

### Hard Conflict Examples

- wet skin in dry library
- swimsuit in corporate office
- winter coat with sweaty glossy shoulders
- natural ginger read on a Black woman when not explicitly styled as dyed hair

### Soft Conflict Examples

- nightclub glam in sunrise tennis court
- latex in a cozy breakfast nook
- heavy editorial makeup in candid grocery run

### Required Context Examples

- wet hair requires at least one of: pool, spa, shower, beach, rain, humidity
- post-workout flush requires gym, sport, or exertion context
- sand on legs requires beach or dunes

## Surface-State Validation

Surface-state tags must be checked separately.

```json
{
  "id": "wet_skin_sheen",
  "layer": "surface_state",
  "requires_any_tags": ["pool", "beach", "spa", "shower", "rain", "humid"],
  "forbids_any_tags": ["library", "dry_studio", "office", "winter_chalet"],
  "severity": "hard",
  "fix_if_failed": "remove_surface_state"
}
```

## Hair / Ethnicity Logic

Do not encode dumb impossibility bans.
Encode natural read vs dyed read.

Example:

```json
{
  "ethnicity_group": "black",
  "natural_hair_palette": ["black", "dark_brown", "deep_brown"],
  "allowed_dyed_palette": ["blonde", "burgundy", "blue", "pink", "silver", "lavender", "copper"],
  "disallow_implicit_natural_read": ["ginger", "copper_red"]
}
```

Meaning:

- copper hair is allowed if clearly dyed
- accidental natural redhead read is not allowed by default

## Repair Pass

Validator should not only reject.
It should try to repair.

Repair priority:

1. remove a small conflicting detail
2. swap micro-setting
3. swap outfit detail
4. swap pose family
5. regenerate larger scene block

Example:

- `wet skin` + `library`
- fix = remove `wet skin`

Not:

- destroy the entire prompt if one detail is wrong

## Anti-Repeat Memory

Memory must track recent outputs.

At minimum keep:

- last 50 opening phrases
- last 50 setting macros
- last 50 setting micros
- last 50 outfit families
- last 50 pose families
- last 50 camera framings
- last 50 camera angles
- last 50 archetypes

## Repetition Validator

Reject a candidate if it overlaps too heavily with recent prompts.

Simple fail examples:

- same setting macro + same pose family + same outfit family
- same archetype + same opening phrase style
- same blonde in pink micro dress logic with cosmetic edits only

## Freshness Rules

Generator must not treat good refs or prompt libraries as reusable shells.

Hard freshness rules:

- do not reuse whole prompt skeletons
- do not rotate the same winning location
- do not change only woman, hair color, or outfit color
- if a line is recognizably similar to an existing library line, rewrite it

## Beauty Control

Women should still read beautified and flattering by default.

Even when the route is:

- sweet
- casual
- candid
- amateur

Avoid:

- awkward facial read
- unflattering realism
- random ugly outputs caused by under-specified beauty cues

## Suggested File Layout

```text
data/
  subjects.json
  styling.json
  settings.json
  setting_engine.json
  composition.json
  surface_states.json
  routes.json
rules/
  compatibility_rules.json
  repair_rules.json
  anti_repeat_rules.json
runtime/
  memory.json
generator.py
validator.py
repair.py
```

## Prompt Output Structure

By default, render prompts in this order:

1. capture concept first
2. model identity block second
3. outfit and pose block third
4. scene assembly after that
5. technical photo parameters at the end

Example skeleton:

```text
Editorial photo of a stunning ...
She wears ...
She is ...
The setting is ...
... direct eye contact ...
... framing, angle, light, time, lens, photo params
```

## Operator Model

The user should not have to think in technical internals.

Normal user commands:

- make 100 gen-z studio prompts
- add more luxury bathrooms
- reduce pink blondes
- ban repeated arcade girls
- push more fantasy and sci-fi
- generate 30 and keep only the strongest

System response:

- Codex edits weights, bans, routes, or data
- runs the generator
- checks failures
- repairs the system
- returns prompts

## Practical Goal

The generator should produce prompts that are:

- more varied
- more coherent
- less template-like
- less repetitive
- easier to steer in batches
- safer against stupid mismatches
