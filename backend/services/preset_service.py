from __future__ import annotations

from typing import Any

from backend.prompt_service import merged_form_state
from backend.storage import delete_preset, save_preset


def save_preset_record(name: str, form_state: dict[str, Any]) -> dict[str, Any]:
    clean_name = (name or "").strip()
    if not clean_name:
        raise ValueError("Preset name is empty.")
    return save_preset(clean_name, merged_form_state(form_state))


def delete_preset_record(preset_id: str) -> None:
    if not preset_id:
        raise ValueError("Preset id is empty.")
    delete_preset(preset_id)
