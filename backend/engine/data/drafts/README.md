# Draft Content Banks

Use `drafts/` for new content that is not ready for live generation yet.

Why this folder exists:
- keep experiments in tiny files
- avoid editing large base banks for every new idea
- let review happen without touching live behavior

Default behavior:
- drafts are ignored while `content_bank_config.json` has `"load_drafts": false`
- live generation stays on the core bank plus optional overrides

Low-credit workflow:
1. Put a small fragment into `drafts/<bank_name>/topic_name.json`.
2. Keep one topic per file.
3. Add `status` and `source` fields to every new record.
4. Review the fragment first.
5. Only after review, either enable drafts temporarily or move the approved records into the core bank.

Supported bank names:
- `setting_engine`
- `pose_bank`
- `styling`
- `subjects`
- any other file name that already exists in `backend/engine/data/*.json`

Merge rules:
- dict -> merge by key
- list of objects with `id` -> merge by `id`, append new records
- simple lists without `id` -> overlay replaces the base list
