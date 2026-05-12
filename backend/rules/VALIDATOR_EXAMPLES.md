# Validator & Repair — Examples and how to reproduce

This document gives concrete candidate examples that exercise `validate_candidate()` and `repair_candidate()` logic. Use these examples in a REPL or quick test while tuning rules.

1) Wet skin in a dry bookish/library setting

Candidate (minimal):

```py
candidate = {
    "tags": ["wet", "bookish", "library"],
    "beauty_level": "beautified and flattering",
}
```

Expected validator finding:
- `wet_skin_in_dry_bookish_space` (hard_conflict)

Repair behavior (based on `repair_rules.json`):
- `remove_small_conflicting_detail` or `swap_surface_state` — the repair will remove `wet`/`sand`/`flush` tags and set `surface_state` to `dry_clean`.

2) Swimwear in an office-like setting

Candidate:

```py
candidate = {
    "tags": ["swimwear", "office", "formal_restaurant"],
    "beauty_level": "beautified and flattering",
}
```

Expected validator finding:
- `swimwear_in_office_like_setting` (hard_conflict)

Repair behavior:
- `swap_outfit_detail` then `swap_setting_micro` — repair may swap the outfit to a `mini_dress` and replace the micro-setting with a compatible luxury interior.

3) Sand details without beach context

Candidate:

```py
candidate = {
    "tags": ["sand", "sunny", "porch"],
    "beauty_level": "beautified and flattering",
}
```

Expected validator finding:
- `sand_without_beach_context` (hard_conflict)

Repair behavior:
- `remove_small_conflicting_detail` or `swap_setting_micro` — repair will remove `sand` and/or move to a coastal micro-setting.

4) Vivid colored hair on disallowed age band

Candidate:

```py
candidate = {
    "tags": ["vivid_colored_hair"],
    "hair_color_tags": ["vivid_colored_hair"],
    "age_band_id": "early_30s",
    "beauty_level": "beautified and flattering",
}
```

Expected validator finding:
- `vivid_colored_hair_age_mismatch` (hard_conflict)

Repair behavior:
- Validator flags the mismatch; repair may not automatically change age but will surface the finding for reroll or forced change depending on `repair_rules` mapping.

5) Breast size vs age rules

Candidate:

```py
candidate = {
    "breast_size_id": "very_big_breasts",
    "age_band_id": "early_30s",
    "beauty_level": "beautified and flattering",
}
```

Expected validator finding:
- `very_big_breasts_age_mismatch` (hard_conflict)

Repair behavior:
- Validator will flag; repair may attempt small fixes but in many cases the generator should reroll the candidate to satisfy batch rules.

How to run these quickly

```py
from backend.engine.validator import validate_candidate, load_rule_bank
from backend.engine.repair import repair_candidate

rules = load_rule_bank()
findings = validate_candidate(candidate, rules)
print(findings)
repaired = repair_candidate(candidate, findings, rules)
print(repaired)
```

Notes
- The repair pass applies actions per `repair_rules.json` `fix_map` entries until the finding is resolved or the repair priority list is exhausted.
- These examples pair with tests and can be expanded to automated unit tests that assert the presence/absence of specific findings after repair.
