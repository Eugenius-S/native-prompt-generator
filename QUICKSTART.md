Quickstart — Local development and tests
=====================================

1. Run the bundled setup script

```bat
SETUP_PROMPT_GENERATOR_WEB.bat
```

2. Start the app

```bat
START_PROMPT_GENERATOR_WEB.bat
```

Or run the app directly:

```powershell
python app.py
# Open http://127.0.0.1:8765 in your browser
```

3. Run smoke tests

```powershell
python -m pytest -q
```

4. Run browser E2E tests

```powershell
npm install
npx playwright install chromium
npm run test:e2e -- --workers=1 --reporter=line
```

5. Optional: run the app on a custom port

```powershell
$env:PROMPT_GENERATOR_PORT = "8766"
python app.py
```

Notes
- If you change content banks under `backend/engine/data/`, you can toggle loading of `drafts` by editing `backend/engine/data/content_bank_config.json` and setting `"load_drafts": true` for local testing. After verification, promote fragments into the core banks (see `backend/engine/data/CONTENT_BANK_PROMOTION.md`).
- Playwright uses a dedicated fresh app instance via `PROMPT_GENERATOR_PORT=8766`, so local manual sessions on `8765` do not interfere with E2E runs.
