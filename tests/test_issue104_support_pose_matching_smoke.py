from __future__ import annotations

import json
from pathlib import Path

from backend.engine import selectors


DATA_ROOT = Path(__file__).resolve().parents[1] / "backend" / "engine" / "data"
SETTING_ENGINE = json.loads((DATA_ROOT / "setting_engine.json").read_text(encoding="utf-8"))
POSE_BANK = json.loads((DATA_ROOT / "pose_bank.json").read_text(encoding="utf-8"))
BASE_SPACES = {item["id"]: item for item in SETTING_ENGINE["base_spaces"]}
POSE_FAMILIES = {item["id"]: item for item in POSE_BANK["pose_families"]}


def _pose_allowed(pose_id: str, base_space_id: str, style_mode: str = "random") -> bool:
    predicate = selectors._pose_for_base_space(BASE_SPACES[base_space_id], style_mode)
    return predicate(POSE_FAMILIES[pose_id])


def test_issue104_infers_support_tags_from_scene_values() -> None:
    assert "chair_support" in selectors._scene_semantic_tags(BASE_SPACES["marble_dining_room"])
    assert "sofa_support" in selectors._scene_semantic_tags(BASE_SPACES["hotel_suite_sitting_area"])
    assert "stairs_support" in selectors._scene_semantic_tags(BASE_SPACES["university_courtyard_steps"])
    assert "counter_support" in selectors._scene_semantic_tags(BASE_SPACES["marble_shaker_kitchen"])


def test_issue104_requires_real_support_surfaces_for_seated_and_lying_poses() -> None:
    assert not _pose_allowed("backwards_chair_pose", "powder_room_stone_vanity")
    assert not _pose_allowed("chair_sideways_pose", "city_rooftop_day")
    assert not _pose_allowed("side_lying_lounge", "city_rooftop_day")
    assert not _pose_allowed("counter_hip_lean_collar_touch", "city_rooftop_day")
    assert _pose_allowed("chair_sideways_pose", "marble_dining_room")
    assert _pose_allowed("side_lying_lounge", "hotel_suite_sitting_area")
    assert _pose_allowed("stairs_seated", "university_courtyard_steps")
    assert _pose_allowed("counter_hip_lean_collar_touch", "marble_shaker_kitchen")
