Content bank promotion workflow
================================

This file describes the recommended local workflow for adding draft fragments and promoting them into the core content banks.

1) Add a small fragment to `backend/engine/data/drafts/<bank_name>/your_fragment.json`.
   - Keep fragments focused and small (one or a few related records).
   - Add metadata fields: `id`, `status`, `source` (e.g. `drafts/2026-04-19/my_addition`), and an optional `notes` field.

2) Test locally with drafts enabled
   - Edit `backend/engine/data/content_bank_config.json` and set `"load_drafts": true`.
   - Run the app: `python app.py` and use the UI to exercise the new entries.
   - Prefer small batch runs (batchSize 3-10) while testing.

3) Verify and iterate
   - Use the debug panel in the UI to confirm selection, weights, and compatibility.
   - Adjust `weight`, `tags`, and `requires_any_tags` in the fragment until behavior matches expectation.

4) Promote into core
   - When stable, copy or merge the fragment into the core bank under `backend/engine/data/<bank_name>.json` or into a small subfile under the core folder.
   - Ensure `id` is unique in core.
   - Add `status: approved` and set `source` to the fragment path or PR reference.

5) Turn drafts off and run final checks
   - Set `"load_drafts": false` in `content_bank_config.json` and run a few larger batch sweeps to verify no regressions.
   - Use the same `python -m pytest -q` smoke check from `QUICKSTART.md` before promoting or merging the change.
   - If the change touches the web UI or startup flow, also run the browser E2E command from `QUICKSTART.md` before promoting.

Notes
-----
- Files in `overrides/` are applied on top of the merged core+drafts; use overrides for local tuning without touching core.
- The generator merges using `_merge_data()` in `backend/engine/generator.py`, which merges by `id` when records have an `id` field.
- Prefer promoting small increments and opening a PR for review with explicit `status` and testing notes.
