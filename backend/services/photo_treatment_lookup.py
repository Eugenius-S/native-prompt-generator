from __future__ import annotations

import functools
from typing import Any

from backend.engine import generator


@functools.lru_cache(maxsize=1)
def _photo_treatment_lookup() -> dict[str, dict[str, Any]]:
    profiles = generator.load_data_bank()["photo_treatments"]["profiles"]
    return {item["id"]: item for item in profiles}
