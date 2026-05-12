from __future__ import annotations

import json
from pathlib import Path

from backend.engine import line_bank_loader, selectors, validator


DATA_ROOT = Path(__file__).resolve().parents[1] / "backend" / "engine" / "data"
SETTING_ENGINE = json.loads((DATA_ROOT / "setting_engine.json").read_text(encoding="utf-8"))
POSE_BANK = json.loads((DATA_ROOT / "pose_bank.json").read_text(encoding="utf-8"))

BASE_SPACES = {item["id"]: item for item in SETTING_ENGINE["base_spaces"]}
POSE_FAMILIES = {item["id"]: item for item in POSE_BANK["pose_families"]}


def test_issue105_line_bank_bed_pose_needs_real_bed_support() -> None:
    record = line_bank_loader.normalize_line_bank_record(
        "poses",
        "6_8",
        "bent forward over the bed with both hands planted on the blanket, glancing back over her shoulder",
        line_bank_loader.LINE_BANK_ROOT / "women" / "poses" / "6_8.md",
        gender="women",
    )

    assert not line_bank_loader.line_bank_pose_matches_scene(
        record,
        scene_family_id="courtyard_garden",
        scene_tags={"outdoor", "sunny", "daylight"},
        setting_value="villa courtyard with terracotta walls, white plaster and bougainvillea",
    )
    assert line_bank_loader.line_bank_pose_matches_scene(
        record,
        scene_family_id="residential_luxury",
        scene_tags={"interior", "luxury", "bedroom"},
        setting_value="tailored bedroom suite with upholstered headboard wall and crisp bedding",
    )


def test_issue105_line_bank_sink_mirror_pose_needs_real_vanity_support() -> None:
    record = line_bank_loader.normalize_line_bank_record(
        "poses",
        "4_5",
        "standing near a mirror with one hand on the sink and shoulders angled",
        line_bank_loader.LINE_BANK_ROOT / "women" / "poses" / "4_5.md",
        gender="women",
    )

    assert not line_bank_loader.line_bank_pose_matches_scene(
        record,
        scene_family_id="urban_daylight",
        scene_tags={"outdoor", "sunny", "daylight", "urban"},
        setting_value="dusty highway shoulder with open road and dry grass",
    )
    assert line_bank_loader.line_bank_pose_matches_scene(
        record,
        scene_family_id="grooming_bath",
        scene_tags={"interior", "luxury", "bathroom", "dressing_space"},
        setting_value="elegant powder room anchored by a dramatic stone vanity and an oversized mirror",
    )


def test_issue105_selector_blocks_mirror_pose_without_mirror_support() -> None:
    roadside_scene = {
        "id": "dusty_highway_shoulder",
        "scene_family_id": "urban_daylight",
        "tags": ["outdoor", "sunny", "daylight", "urban", "travel"],
        "value": "dusty highway shoulder with open road and dry grass",
    }
    roadside_predicate = selectors._pose_for_base_space(roadside_scene)
    vanity_predicate = selectors._pose_for_base_space(BASE_SPACES["glam_vanity_corner"])

    assert not roadside_predicate(POSE_FAMILIES["mirror_hair_adjust"])
    assert vanity_predicate(POSE_FAMILIES["mirror_hair_adjust"])


def test_issue105_selector_blocks_bed_pose_without_bed_support() -> None:
    canyon_scene = {
        "id": "red_canyon_wall",
        "scene_family_id": "courtyard_garden",
        "tags": ["outdoor", "sunny", "daylight"],
        "value": "red canyon wall with smooth stone curves and dry ground",
    }
    canyon_predicate = selectors._pose_for_base_space(canyon_scene)
    bedroom_predicate = selectors._pose_for_base_space(BASE_SPACES["tailored_bedroom_suite"])

    assert not canyon_predicate(POSE_FAMILIES["rear_edge_bed_pose"])
    assert bedroom_predicate(POSE_FAMILIES["rear_edge_bed_pose"])


def test_issue105_selector_blocks_chair_pose_without_real_seat_support() -> None:
    roadside_scene = {
        "id": "dusty_highway_shoulder",
        "scene_family_id": "urban_daylight",
        "tags": ["outdoor", "sunny", "daylight", "urban", "travel"],
        "value": "dusty highway shoulder with open road and dry grass",
    }
    roadside_predicate = selectors._pose_for_base_space(roadside_scene)
    lounge_predicate = selectors._pose_for_base_space(BASE_SPACES["record_listening_room"])

    assert not roadside_predicate(POSE_FAMILIES["chair_sideways_pose"])
    assert lounge_predicate(POSE_FAMILIES["chair_sideways_pose"])


def test_issue105_ground_seat_pose_rejects_park_path_hard_surface() -> None:
    park_path_scene = {
        "id": "green_park_path",
        "scene_family_id": "courtyard_garden",
        "tags": ["outdoor", "sunny", "daylight", "garden"],
        "value": "green park path with trimmed grass and stone paving",
    }
    park_path_predicate = selectors._pose_for_base_space(park_path_scene)

    assert not park_path_predicate(POSE_FAMILIES["forward_fold_cross_leg"])


def test_issue105_perch_pose_rejects_gym_context_without_real_support() -> None:
    gym_scene = {
        "id": "boxing_gym_wall",
        "scene_family_id": "wellness_spa",
        "tags": ["interior", "sporty", "wellness", "daylight"],
        "value": "boxing gym wall with worn floor, matte paint and a hanging heavy bag",
    }
    gym_predicate = selectors._pose_for_base_space(gym_scene)
    vanity_predicate = selectors._pose_for_base_space(BASE_SPACES["glam_vanity_corner"])

    assert not gym_predicate(POSE_FAMILIES["perch_lean_back"])
    assert vanity_predicate(POSE_FAMILIES["perch_lean_back"])


def test_issue105_validator_flags_water_contact_pose_with_dry_outfit() -> None:
    candidate = {
        "tags": ["coastal", "beach", "water_contact_pose", "dress", "dry"],
        "beauty_level": "beautified and flattering",
    }
    swimwear_control = {
        "tags": ["coastal", "beach", "water_contact_pose", "swimwear", "wet_possible"],
        "beauty_level": "beautified and flattering",
    }

    findings = validator.validate_candidate(candidate)
    swimwear_findings = validator.validate_candidate(swimwear_control)

    assert any(item.get("id") == "water_contact_pose_without_wet_outfit" for item in findings)
    assert not any(item.get("id") == "water_contact_pose_without_wet_outfit" for item in swimwear_findings)


def test_issue105_dry_coastal_allows_mini_dress_outfit() -> None:
    """Dry coastal boardwalk: mini_dress (dress/feminine) должен проходить предикат."""
    boardwalk = BASE_SPACES["boardwalk_beach_houses"]
    outfit_families = {item["id"]: item for item in json.loads(
        (DATA_ROOT / "styling.json").read_text(encoding="utf-8")
    )["outfit_families"]}

    mini_dress = outfit_families["mini_dress"]
    predicate = selectors._base_space_outfit_predicate(mini_dress, "random")
    assert predicate(boardwalk), "mini_dress must be allowed at dry coastal boardwalk"


def test_issue105_dry_coastal_blocks_swimwear() -> None:
    """Dry coastal boardwalk: swimsuit должен быть заблокирован (нет pool/beach/spa в тегах)."""
    boardwalk = BASE_SPACES["boardwalk_beach_houses"]
    outfit_families = {item["id"]: item for item in json.loads(
        (DATA_ROOT / "styling.json").read_text(encoding="utf-8")
    )["outfit_families"]}

    swimsuit = outfit_families["swimsuit"]
    predicate = selectors._base_space_outfit_predicate(swimsuit, "random")
    assert not predicate(boardwalk), "swimsuit must be blocked at dry coastal boardwalk (no pool/spa in scene tags)"


def test_issue105_pool_scene_allows_swimwear() -> None:
    """Pool scene: swimsuit должен проходить (pool в тегах)."""
    pool_scene = BASE_SPACES["poolside_steps"]
    outfit_families = {item["id"]: item for item in json.loads(
        (DATA_ROOT / "styling.json").read_text(encoding="utf-8")
    )["outfit_families"]}

    swimsuit = outfit_families["swimsuit"]
    predicate = selectors._base_space_outfit_predicate(swimsuit, "random")
    assert predicate(pool_scene), "swimsuit must be allowed at pool scene"
