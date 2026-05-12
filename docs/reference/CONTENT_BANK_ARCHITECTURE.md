# Expandable Content Bank Architecture

Goal:
- the location, pose, hairstyle, makeup, and clothing banks should be extendable without editing generator logic;
- new elements should be added as data files, not hardcoded in Python;
- it should be easy to keep the `core curated bank` and the `idea / draft bank` separate.

## Principle

Generator logic:
- chooses
- filters
- scores

Content bank:
- stores entities
- tags
- weights
- relations
- readiness status

In other words:
- code does not know about a specific `quiet chess club room`
- code only knows `scene_family`, `tags`, `weights`, and `required / banned / preferred`

## How to Store It

A good future schema:

- `backend/engine/data/core/`
  - stable banks that already participate in generation
- `backend/engine/data/drafts/`
  - new ideas that are not connected yet
- `backend/engine/data/overrides/`
  - local user additions

By domain:
- `locations.json`
- `poses.json`
- `hair_styles.json`
- `hair_colors.json`
- `makeup_styles.json`
- `outfit_families.json`
- `materials.json`
- `color_stories.json`

## What Every Record Should Have

Minimum:
- `id`
- `value`
- `tags`
- `weight`
- `status`
- `source`

Useful additions:
- `group`
- `scene_family_id`
- `macro_ids`
- `requires_tags`
- `bans_tags`
- `notes`

Example:

```json
{
  "id": "quiet_chess_club_room",
  "value": "quiet chess club room with green felt tables, wooden clocks and warm pendant lamps in soft blur",
  "group": "culture_bookish",
  "tags": ["interior", "bookish", "quiet", "modest_safe", "public_elegant"],
  "weight": 0.08,
  "status": "draft",
  "source": "modest_prompts_2026_04_17",
  "notes": "good for low-spicy women and couples"
}
```

## Statuses

It is better to introduce right away:
- `draft`
- `reviewed`
- `production`
- `disabled`

Then you can:
- collect raw material quickly
- not move everything into live immediately
- connect only `production`

## How to Connect It Without Pain

Best path:
- loader reads `core`
- then optionally reads `overrides`
- `drafts` do not participate by default

That means:
- wanted to test a new bank
- moved some entries from `draft` to `production`
- or enabled a feature flag for reading `drafts`

## What Not to Do

Bad:
- keep new ideas in code
- spread one entity across 5 files without an id
- hardcode specific scene names in scoring functions
- store only free text without tags and groups

## How to Think About Locations

A location should be decomposable:
- `scene_family`
- `base_space`
- `material_accents`
- `detail_accents`
- `atmosphere_cues`

Then the bank grows easily.

Instead of one rigid line:
- `quiet chess club room with green felt tables...`

You can have:
- `base_space = chess_club_room`
- `material = dark_wood_brass`
- `detail = wooden_clocks`
- `atmosphere = warm_pendant_pools`

## How to Think About Poses

The pose should also be modular:
- `pose_family`
- `hand_action`
- `body_angle`
- `activity_anchor`

And tags:
- `modest_safe`
- `task_anchor`
- `hands_busy`
- `sport_prep`
- `public_space`
- `editorial`

## How to Think About Appearance

Hairstyles and makeup should be separate from subject logic.

For hairstyles:
- `length`
- `texture`
- `structure`
- `formality`
- `sport_safe`

For makeup:
- `intensity`
- `finish`
- `context`
- `night_safe`
- `clean_safe`

Then new records can be added without rewriting the rules.

## Practical Rule for the Project

Any new bank addition should go like this:
1. first into the `draft bank`
2. then manual review
3. only then move it into the `production bank`

## What to Do Next

- split the current banks into a more explicit `core / draft / override` structure
- build a small loader layer instead of directly reading individual JSON files
- add `status` and `source` to existing entities
- make a separate import flow for new ideas from stash files
