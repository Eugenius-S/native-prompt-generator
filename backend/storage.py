from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any
from uuid import uuid4


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
HISTORY_PATH = DATA_DIR / "history.json"
PRESETS_PATH = DATA_DIR / "presets.json"
_LOCK = threading.Lock()


def _ensure_file(path: Path, default_value: list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(default_value, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_list(path: Path) -> list[dict[str, Any]]:
    _ensure_file(path, [])
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        recovered: list[dict[str, Any]] = []
        index = 0
        while index < len(raw):
            while index < len(raw) and raw[index].isspace():
                index += 1
            if index >= len(raw):
                break
            try:
                chunk, index = decoder.raw_decode(raw, index)
            except json.JSONDecodeError:
                break
            if isinstance(chunk, list):
                recovered.extend(item for item in chunk if isinstance(item, dict))
            elif isinstance(chunk, dict):
                recovered.append(chunk)
        if recovered:
            _write_list(path, recovered)
        return recovered
    if not isinstance(data, list):
        return []
    return data


def _write_list(path: Path, payload: list[dict[str, Any]]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def list_history(limit: int = 20) -> list[dict[str, Any]]:
    with _LOCK:
        items = _read_list(HISTORY_PATH)
    return items[:limit]


def append_history(entry: dict[str, Any], limit: int = 40) -> dict[str, Any]:
    with _LOCK:
        items = _read_list(HISTORY_PATH)
        payload = {"id": uuid4().hex, **entry}
        items.insert(0, payload)
        _write_list(HISTORY_PATH, items[:limit])
    return payload


def list_presets() -> list[dict[str, Any]]:
    with _LOCK:
        return _read_list(PRESETS_PATH)


def save_preset(name: str, form_state: dict[str, Any]) -> dict[str, Any]:
    record = {
        "id": uuid4().hex,
        "name": name.strip(),
        "formState": form_state,
    }
    with _LOCK:
        items = [item for item in _read_list(PRESETS_PATH) if item.get("name", "").strip().lower() != record["name"].lower()]
        items.insert(0, record)
        _write_list(PRESETS_PATH, items[:50])
    return record


def delete_preset(preset_id: str) -> None:
    with _LOCK:
        items = [item for item in _read_list(PRESETS_PATH) if item.get("id") != preset_id]
        _write_list(PRESETS_PATH, items)
