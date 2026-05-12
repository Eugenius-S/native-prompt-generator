# Content Bank Workflow

This folder now has three layers:

- `core`
  - the current live bank in the root `*.json` files
- `drafts`
  - small candidate fragments that stay disabled by default
- `overrides`
  - local tweaks that sit on top of core

Why this matters:
- smaller edits
- lower prompt cost for future updates
- easier review of new locations, poses, hairstyles, makeup, and outfits

Recommended workflow:
1. Add raw ideas to `drafts/<bank_name>/some_topic.json`.
2. Keep each fragment small and focused.
3. Mark every new record with `status` and `source`.
4. Review the fragment in isolation.
5. Promote approved records into the core bank only when they are stable.

Examples:
- new modest locations -> `drafts/setting_engine/modest_prompts_seed.json`
- new modest poses -> `drafts/pose_bank/modest_prompts_seed.json`
- new hairstyle or makeup additions -> `drafts/styling/*.json`
- new ethnicity or subject additions -> `drafts/subjects/*.json`

Config:
- `content_bank_config.json` controls whether drafts and overrides are loaded
- current safe default is drafts off, overrides on

## Line-Bank Override Workflow

The `overrides/line_banks/` folder now adds a user-editable layer for fast text-only additions.

What it is for:

- quick local additions to `poses`
- quick local additions to `outfits`
- quick local additions to `expressions`

What stays true:

- the main JSON banks still hold the structured routing/scoring metadata
- line-banks are an additive override layer, not a full bank replacement
- women and men stay on separate line-bank trees

Current live scope:

- `overrides/line_banks/women/poses/*.md`
- `overrides/line_banks/women/outfits/*.md`
- `overrides/line_banks/women/expressions/*.md`
- `overrides/line_banks/men/poses/*.md`
- `overrides/line_banks/men/outfits/*.md`
- `overrides/line_banks/men/expressions/*.md`

Current non-live placeholders:

- `locations/`
- `hair/`
- `makeup/`

File contract:

- one non-comment line = one item
- comment lines start with `#`
- valid live filenames are `1_3.md`, `4_5.md`, and `6_8.md`

Safe repo scaffolding:

- root docs inside `overrides/line_banks/` are ignored by the loader
- comment-only starter templates inside live folders are safe and do not change generation output

See these files for the manual workflow:

- `overrides/line_banks/README.md`
- `overrides/line_banks/TROUBLESHOOTING.md`
