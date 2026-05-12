from __future__ import annotations

from typing import Any

from backend.options import DEFAULT_FORM_STATE, DISABLED_FIELDS, ENABLED_FIELDS, UI_OPTIONS
from backend.storage import list_history, list_presets


def get_bootstrap() -> dict[str, Any]:
    return {
        "defaults": DEFAULT_FORM_STATE,
        "options": UI_OPTIONS,
        "enabledFields": sorted(ENABLED_FIELDS),
        "disabledFields": sorted(DISABLED_FIELDS),
        "presets": list_presets(),
        "history": list_history(),
    }
