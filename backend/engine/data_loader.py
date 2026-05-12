from __future__ import annotations

import functools
import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

from .line_bank_loader import empty_line_bank_overrides, merge_line_bank_overrides


ROOT = Path(__file__).resolve().parent
DATA_ROOT = ROOT / "data"
CONTENT_BANK_CONFIG_PATH = DATA_ROOT / "content_bank_config.json"
MEMORY_PATH = ROOT / "runtime" / "memory.json"
DEFAULT_RUNTIME_MEMORY = {
    "schema_version": 1,
    "items": [],
    "setting_macros": [],
    "setting_scene_families": [],
    "setting_base_spaces": [],
    "setting_scenes": [],
    "outfit_families": [],
    "pose_families": [],
    "camera_framings": [],
    "camera_angles": [],
}
STATIC_BANK_FILES = {
    "subjects": "subjects.json",
    "styling": "styling.json",
    "settings": "settings.json",
    "setting_engine": "setting_engine.json",
    "composition": "composition.json",
    "photo_treatments": "photo_treatments.json",
    "prompt_openers": "prompt_openers.json",
    "pose_bank": "pose_bank.json",
    "surface_states": "surface_states.json",
    "routes": "routes.json",
}
RUNTIME_MEMORY_IO_LOCK = threading.RLock()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _retry_file_access(operation: Any, attempts: int = 200, delay: float = 0.02) -> Any:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return operation()
        except PermissionError as error:
            last_error = error
            if attempt == attempts - 1:
                raise
            # Windows file handles may briefly block atomic replace; use a small linear backoff.
            time.sleep(delay * (1 + min(attempt, 20) * 0.1))
    if last_error is not None:
        raise last_error
    raise RuntimeError("File access retry loop exited without a result.")


def _write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.stem}-",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)
        _retry_file_access(lambda: os.replace(temp_path, path))
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)


def _load_runtime_memory() -> dict[str, Any]:
    with RUNTIME_MEMORY_IO_LOCK:
        if not MEMORY_PATH.exists():
            return dict(DEFAULT_RUNTIME_MEMORY)
        return _retry_file_access(lambda: _read_json(MEMORY_PATH))


def _save_memory(memory: dict[str, Any]) -> None:
    with RUNTIME_MEMORY_IO_LOCK:
        _write_json_atomic(MEMORY_PATH, memory)


def _merge_data(base: Any, overlay: Any) -> Any:
    if isinstance(base, dict) and isinstance(overlay, dict):
        merged = {key: value for key, value in base.items()}
        for key, value in overlay.items():
            if key in merged:
                merged[key] = _merge_data(merged[key], value)
            else:
                merged[key] = value
        return merged
    if isinstance(base, list) and isinstance(overlay, list):
        combined = list(base) + list(overlay)
        if combined and all(isinstance(item, dict) and item.get("id") for item in combined):
            merged_by_id: dict[str, Any] = {}
            order: list[str] = []
            for item in base:
                item_id = item["id"]
                merged_by_id[item_id] = item
                order.append(item_id)
            for item in overlay:
                item_id = item["id"]
                if item_id in merged_by_id:
                    merged_by_id[item_id] = _merge_data(merged_by_id[item_id], item)
                else:
                    merged_by_id[item_id] = item
                    order.append(item_id)
            return [merged_by_id[item_id] for item_id in order]
        return overlay
    return overlay


def _lookup_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in items}


def _content_bank_config() -> dict[str, bool]:
    if not CONTENT_BANK_CONFIG_PATH.exists():
        return {"load_drafts": False, "load_overrides": True, "load_line_banks": True}
    data = _read_json(CONTENT_BANK_CONFIG_PATH)
    load_overrides = bool(data.get("load_overrides", True))
    return {
        "load_drafts": bool(data.get("load_drafts", False)),
        "load_overrides": load_overrides,
        "load_line_banks": bool(data.get("load_line_banks", load_overrides)),
    }


def _layer_fragment_paths(layer_name: str, bank_name: str) -> list[Path]:
    layer_root = DATA_ROOT / layer_name
    paths: list[Path] = []
    direct_file = layer_root / f"{bank_name}.json"
    if direct_file.exists():
        paths.append(direct_file)
    bank_dir = layer_root / bank_name
    if bank_dir.exists():
        paths.extend(sorted(path for path in bank_dir.glob("*.json") if path.is_file()))
    return paths


@functools.lru_cache(maxsize=1)
def _load_static_data_bank() -> dict[str, Any]:
    config = _content_bank_config()
    bank: dict[str, Any] = {}
    for bank_name, file_name in STATIC_BANK_FILES.items():
        merged = _read_json(DATA_ROOT / file_name)
        if config["load_drafts"]:
            for path in _layer_fragment_paths("drafts", bank_name):
                merged = _merge_data(merged, _read_json(path))
        if config["load_overrides"]:
            for path in _layer_fragment_paths("overrides", bank_name):
                merged = _merge_data(merged, _read_json(path))
        bank[bank_name] = merged
    if config["load_line_banks"]:
        return merge_line_bank_overrides(bank, enabled=True)
    bank["line_banks"] = empty_line_bank_overrides(enabled=False)
    return bank


def load_data_bank() -> dict[str, Any]:
    return {
        **_load_static_data_bank(),
        "memory": _load_runtime_memory(),
    }
