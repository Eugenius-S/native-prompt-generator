from __future__ import annotations

from backend.shot_lane_contracts import apply_shot_lane_contract, resolve_shot_lane_contract


def test_resolve_shot_lane_contract_separates_seamless_and_direct_light() -> None:
    seamless = resolve_shot_lane_contract(
        {
            "photo_treatment_id": "studio_seamless",
            "scene_family_id": "studio",
        }
    )
    direct_light = resolve_shot_lane_contract(
        {
            "photo_treatment_id": "direct_light_editorial",
            "scene_family_id": "urban_daylight",
        }
    )

    assert seamless["lane_id"] == "seamless_studio"
    assert direct_light["lane_id"] == "editorial_hard_sun"


def test_apply_shot_lane_contract_rewrites_dirty_seamless_studio_setting() -> None:
    contracted = apply_shot_lane_contract(
        {
            "photo_treatment_id": "studio_seamless",
            "scene_family_id": "studio",
            "line_bank_location": "school portrait setup with blue muslin backdrop, stool and direct flash feel",
            "setting_scene": "school portrait setup with blue muslin backdrop, stool and direct flash feel",
        }
    )

    assert contracted["render_contract"]["lane_id"] == "seamless_studio"
    assert "school portrait" not in contracted["setting_scene"]
    assert "stool" not in contracted["setting_scene"]
    assert "seamless" in contracted["setting_scene"]


def test_apply_shot_lane_contract_normalizes_seamless_studio_time_out_of_night() -> None:
    contracted = apply_shot_lane_contract(
        {
            "photo_treatment_id": "advertising_poster_realism",
            "scene_family_id": "studio",
            "setting_scene": "soft pink seamless studio background, clean seamless backdrop and smooth floor falloff",
            "time_of_day": "night",
        }
    )

    assert contracted["time_of_day"] == "bright afternoon"


def test_apply_shot_lane_contract_removes_night_daylight_contradiction() -> None:
    contracted = apply_shot_lane_contract(
        {
            "photo_treatment_id": "clean_commercial",
            "scene_family_id": "urban_daylight",
            "lighting_render": "soft clean commercial light",
            "time_of_day": "night",
            "line_bank_location": "fish market edge with wet stone floor, metal tables and cold daylight",
        }
    )

    assert contracted["render_contract"]["lane_id"] == "clean_daylight_commercial"
    assert contracted["time_of_day"] == "bright afternoon"


def test_apply_shot_lane_contract_removes_cheap_hospitality_location_tail() -> None:
    contracted = apply_shot_lane_contract(
        {
            "photo_treatment_id": "concept_photo_editorial",
            "scene_family_id": "hospitality_suite",
            "line_bank_location": "record store corner with poster wall and narrow aisle",
            "setting_scene": "luxury suite with lacquered wood, marble vanity and city glow",
        }
    )

    assert contracted["line_bank_location"] == ""


def test_apply_shot_lane_contract_normalizes_bright_time_for_dark_lane() -> None:
    contracted = apply_shot_lane_contract(
        {
            "photo_treatment_id": "low_key_dramatic",
            "scene_family_id": "nightlife_bar",
            "line_bank_location": "private cocktail booth with dim amber spill and velvet seating",
            "lighting_render": "low-key dramatic light with strong shadow falloff",
            "time_of_day": "bright afternoon",
        }
    )

    assert contracted["render_contract"]["lane_id"] == "nightlife_flash"
    assert contracted["time_of_day"] == "night"


def test_apply_shot_lane_contract_keeps_practical_studio_tail_in_practical_lane() -> None:
    contracted = apply_shot_lane_contract(
        {
            "photo_treatment_id": "advertising_poster_realism",
            "scene_family_id": "studio",
            "line_bank_location": "red studio set with glossy floor, hard side light and deep shadow falloff",
            "setting_scene": "clean warm gray seamless studio background",
        }
    )

    assert contracted["render_contract"]["lane_id"] == "studio_practical_set"
    assert contracted["line_bank_location"] == "red studio set with glossy floor, hard side light and deep shadow falloff"


def test_apply_shot_lane_contract_blocks_school_portrait_from_practical_studio_lane() -> None:
    contracted = apply_shot_lane_contract(
        {
            "photo_treatment_id": "advertising_poster_realism",
            "scene_family_id": "studio",
            "line_bank_location": "school portrait setup with blue muslin backdrop, stool and direct flash feel",
            "setting_scene": "soft pink seamless studio background",
        }
    )

    assert contracted["render_contract"]["lane_id"] == "studio_practical_set"
    assert contracted["line_bank_location"] == ""


def test_apply_shot_lane_contract_blocks_practical_studio_tail_outside_studio_lane() -> None:
    contracted = apply_shot_lane_contract(
        {
            "photo_treatment_id": "direct_light_editorial",
            "scene_family_id": "urban_daylight",
            "line_bank_location": "red studio set with glossy floor, hard side light and deep shadow falloff",
            "setting_scene": "sunlit city street with stone facade",
        }
    )

    assert contracted["render_contract"]["lane_id"] == "editorial_hard_sun"
    assert contracted["line_bank_location"] == ""
