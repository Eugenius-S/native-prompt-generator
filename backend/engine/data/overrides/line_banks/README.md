# Line-Bank Override Workflow

This folder holds user-editable line-based banks that sit next to the existing JSON override layer.

Current live implementation status:

- folder contract: enabled
- loader and validation: enabled
- women live wiring:
  - `poses`: enabled
  - `outfits`: enabled
  - `expressions`: enabled
- men live wiring:
  - `poses`: enabled
  - `outfits`: enabled
  - `expressions`: enabled
- couples live wiring:
  - `poses`: enabled
- shared live wiring:
  - `locations`: enabled

That means:

- you can prepare line-bank files now
- the loader can parse and validate them now
- women line-bank `poses`, `outfits`, and `expressions` can now surface in women generation
- men line-bank `poses`, `outfits`, and `expressions` can now surface only in men generation
- couples line-bank `poses` can now surface in couples generation as a dedicated pair-pose layer
- shared line-bank `locations` can now surface in generation as a render-level location override when scene tags match
- couples `outfits` and `expressions` still stay on current behavior until later phases land
- comment-only template files are safe to keep in the repo and do not change generation output
- root docs in this folder are ignored by the loader, so workflow notes can live next to the banks

## Folder Shape

```text
line_banks/
  women/
    poses/
    expressions/
    outfits/
    locations/
    hair/
    makeup/
  men/
    poses/
    expressions/
    outfits/
    locations/
    hair/
    makeup/
  couples/
    poses/
  shared/
    locations/
```

Only these domains are parsed right now:

- `poses`
- `expressions`
- `outfits`
- `couples/poses`
- `shared/locations`

The rest are placeholders for a later phase.

## File Naming

Use one of these filenames inside the gendered live domain folders:

- `1_3.md`
- `4_5.md`
- `6_8.md`

Example:

```text
line_banks/women/poses/4_5.md
line_banks/men/outfits/6_8.md
line_banks/couples/poses/4_5.md
```

For the shared live location bank, use one common file:

- `shared/locations/all.md`

The repo now includes comment-only starter templates in the live folders.

Workflow:

1. open the matching `1_3.md`, `4_5.md`, or `6_8.md` file
2. replace comment lines with your own entries
3. keep one real item per line
4. rerun generation

For shared locations:

1. open `shared/locations/all.md`
2. replace comment lines with your own entries
3. keep one real item per line
4. rerun generation

## Line Format

- one non-empty non-comment line = one item
- lines starting with `#` are comments
- blank lines are ignored

Example:

```md
# women / poses / 4_5
leaning lightly against a railing with a playful side glance
walking mid-step and looking back over the shoulder
```

## Hard Caps

- `poses`: `140` chars max per line
- `expressions`: `120` chars max per line
- `outfits`: `160` chars max per line
- `locations`: `140` chars max per line

Overlong lines are rejected by validation.

## Notes

- keep entries short and atomic
- do not paste whole prompt paragraphs here
- do not assume women and men banks are interchangeable
- current generator behavior should not change just because these folders exist
- if a template file still contains only `#` comment lines, it is treated as a no-op
- see `TROUBLESHOOTING.md` in this folder for common mistakes and recovery steps

## Included Starter Files

Live domain starter templates now exist for:

- `women/poses/{1_3,4_5,6_8}.md`
- `women/outfits/{1_3,4_5,6_8}.md`
- `women/expressions/{1_3,4_5,6_8}.md`
- `men/poses/{1_3,4_5,6_8}.md`
- `men/outfits/{1_3,4_5,6_8}.md`
- `men/expressions/{1_3,4_5,6_8}.md`
- `couples/poses/{1_3,4_5,6_8}.md`

Placeholder folders now include `.gitkeep` files so the future `locations`, `hair`, and `makeup` seams stay visible in the repo.
