from __future__ import annotations

from collections import Counter
from typing import Any

from backend.forms.constants import ANTI_REPEAT_PROFILES


def _anti_repeat_score(batch: list[dict[str, Any]], anti_repeat_mode: str) -> int:
    profile = ANTI_REPEAT_PROFILES[anti_repeat_mode]
    score = 0
    for field_name, penalty in profile["field_penalties"].items():
        counts = Counter(candidate.get(field_name) for candidate in batch if candidate.get(field_name))
        duplicates = sum(count - 1 for count in counts.values() if count > 1)
        score -= duplicates * penalty
    score += len({candidate["scene_family_id"] for candidate in batch}) * profile["unique_scene_bonus"]
    score += len({candidate["setting_micro_id"] for candidate in batch}) * profile["unique_setting_bonus"]
    combo_counts = Counter(
        (candidate.get("outfit_family_id"), candidate.get("material_id"), candidate.get("color_story_id"))
        for candidate in batch
    )
    combo_penalty_map = {"low": 10, "normal": 20, "hard": 32, "brutal": 48}
    combo_penalty = combo_penalty_map.get(anti_repeat_mode, 12)
    score -= sum(count - 1 for count in combo_counts.values() if count > 1) * combo_penalty
    return score
