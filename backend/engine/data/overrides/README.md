# Override Content Banks

Use `overrides/` for local corrections on top of the live core bank.

Good use cases:
- adjust weight without editing the base file
- temporarily disable or soften a record
- replace the text of an existing `id`
- add a few local records for testing

What belongs here:
- quick local tuning
- safe hotfixes
- temporary experiments that should affect live output

What does not belong here:
- big raw idea dumps
- unreviewed content batches
- long-term archive material

Current behavior:
- overrides are loaded while `content_bank_config.json` has `"load_overrides": true`

Rule of thumb:
- `drafts` for new ideas
- `overrides` for local live tweaks
- core files for approved stable content
