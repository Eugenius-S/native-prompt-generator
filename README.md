# Native Prompt Generator

A local prompt generator for neural photo sessions.
Created for Z-Image, but compatible with any model that supports a native prompt structure.

## Goal

The project exists to make writing prompts for AI photo sessions faster, easier, and more controllable.

Instead of assembling prompts by hand every time, the generator builds structured prompts from reusable banks and UI controls.

## What It Does

- generates prompts for:
  - women
  - men
  - couples
- supports local web UI
- keeps presets and history
- supports debug output for prompt decisions
- supports appearance controls for hair length, hairstyle, hair color, makeup, eye color, breast size, and outfit reveal
- uses structured content banks for:
  - scenes
  - styling
  - poses
  - routes
  - photo treatment / stylization

## Current Direction

Main product direction:

- simplify prompt writing for neural photo shoots
- keep output flexible and high-volume
- reduce repetitive manual prompt crafting
- improve stylistic range beyond generic stock-photo output

## Project Structure

- `frontend/`
  - local web UI
- `backend/`
  - prompt assembly
  - generator logic
  - storage
  - mode rendering
- `backend/engine/data/`
  - core content banks
- `backend/engine/data/drafts/`
  - draft additions before promotion into live banks

## Run Locally

First-time setup:

```bat
SETUP_PROMPT_GENERATOR_WEB.bat
```

This script creates `.venv` if needed, installs Python requirements, and installs Node dependencies when `package.json` is present.

Use:

```bat
START_PROMPT_GENERATOR_WEB.bat
```

Or run the app directly:

```powershell
python app.py
```

Optional custom port:

```powershell
$env:PROMPT_GENERATOR_PORT = "8766"
python app.py
```

## Tests

Backend smoke / unit tests:

```powershell
pytest -q
```

Browser E2E tests:

```powershell
npm install
npx playwright install chromium
npm run test:e2e -- --workers=1 --reporter=line
```

## Notes

- logs, runtime memory, and local history/presets are excluded from git
- maintainer-only planning, logs, and research notes live under `docs/internal/`

- Playwright E2E runs use a dedicated app instance on `127.0.0.1:8766`, so an already open local session on `8765` will not pollute the test run.

## Reporting Issues

Use GitHub Issues for bug reports and feature requests.

- Bug report: include steps to reproduce, expected vs actual behavior, environment (OS, Python, commit/branch), and logs or screenshots.
- Feature request: describe the idea, rationale, and example usage.
