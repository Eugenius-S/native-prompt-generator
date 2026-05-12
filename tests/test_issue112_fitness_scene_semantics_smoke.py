from __future__ import annotations

from pathlib import Path

from backend import prompt_service
from backend.engine import line_bank_loader, selectors
from backend.engine.render import prompt_renderer
from backend.services import postprocess

import json


DATA_ROOT = Path(__file__).resolve().parents[1] / "backend" / "engine" / "data"
STYLING = json.loads((DATA_ROOT / "styling.json").read_text(encoding="utf-8"))
SETTING_ENGINE = json.loads((DATA_ROOT / "setting_engine.json").read_text(encoding="utf-8"))
OUTFITS = {item["id"]: item for item in STYLING["outfit_families"]}
BASE_SPACES = {item["id"]: item for item in SETTING_ENGINE["base_spaces"]}


def _base_candidate(
    scene_family_id: str,
    outfit_family_id: str,
    color_story_id: str,
    photo_treatment_id: str = "candid_phone_snapshot",
) -> dict[str, str]:
    return {
        "scene_family_id": scene_family_id,
        "setting_scene_id": "test_setting",
        "camera_framing_id": "waist_up",
        "lighting_family_id": "clean_daylight",
        "outfit_family_id": outfit_family_id,
        "color_story_id": color_story_id,
        "age_band": "22 years old",
        "photo_treatment_id": photo_treatment_id,
        "photo_treatment": "Candid phone snapshot",
        "photo_treatment_category": "stylized",
        "capture_style_render": "smartphone camera feel",
        "lighting_render": "clean natural light with a relaxed phone-camera feel",
        "finish_render": "natural skin texture",
        "hair_structure_id": "soft_waves",
        "hair_structure": "soft loose waves",
    }


def test_issue112_balanced_fitness_remaps_phone_like_treatment() -> None:
    candidate = _base_candidate("urban_daylight", "workout_top_leggings", "sport_clean_white")
    form_state = dict(prompt_service.DEFAULT_FORM_STATE)
    form_state.update(
        {
            "mode": "women",
            "styleMode": "fitness",
            "photoTypeControl": "balanced",
        }
    )

    remapped = postprocess._apply_prompt_constraints(candidate, form_state, spicy_level=5)

    assert remapped["photo_treatment_id"] in {
        "clean_commercial",
        "direct_light_editorial",
        "concept_photo_editorial",
        "advertising_poster_realism",
        "cinematic_poster_realism",
    }
    assert remapped["photo_treatment_id"] not in {
        "candid_phone_snapshot",
        "mirror_selfie",
        "casual_indoor_selfie",
        "disposable_camera",
    }


def test_issue112_active_base_spaces_reject_casual_daywear() -> None:
    active_space = BASE_SPACES["performance_gym_floor"]
    rejected_space = BASE_SPACES["boutique_pilates_studio"]
    assert selectors._base_space_outfit_predicate(OUTFITS["workout_top_leggings"], "fitness")(active_space)
    assert not selectors._base_space_outfit_predicate(OUTFITS["workout_top_leggings"], "fitness")(rejected_space)
    assert not selectors._base_space_outfit_predicate(OUTFITS["shirt_trousers"], "fitness")(active_space)
    assert not selectors._base_space_outfit_predicate(OUTFITS["sweater_jeans"], "fitness")(active_space)


def test_issue112_fitness_activewear_rejects_rooftop_and_wellness_spaces() -> None:
    predicate = selectors._base_space_outfit_predicate(OUTFITS["workout_top_leggings"], "fitness")

    assert not predicate(BASE_SPACES["rooftop_reformer_deck"])
    assert not predicate(BASE_SPACES["wellness_juice_bar"])
    assert not predicate(BASE_SPACES["spa_movement_studio"])
    assert not predicate(BASE_SPACES["thermal_recovery_lounge"])


def test_issue112_fitness_activewear_accepts_active_nature_and_coastal_spaces() -> None:
    predicate = selectors._base_space_outfit_predicate(OUTFITS["workout_top_leggings"], "fitness")

    assert predicate(BASE_SPACES["park_training_lawn"])
    assert predicate(BASE_SPACES["shoreline_workout_pad"])


def test_issue112_active_location_matches_fitness_but_not_bookish() -> None:
    record = line_bank_loader.normalize_line_bank_record(
        "locations",
        "1_3",
        "outdoor running track with red lanes and open stadium light",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert line_bank_loader.line_bank_location_matches_scene(
        record,
        scene_family_id="urban_daylight",
        scene_tags={"outdoor", "sporty", "daylight", "urban"},
        setting_value="sunlit training track with open stadium light and red lanes",
    )
    assert not line_bank_loader.line_bank_location_matches_scene(
        record,
        scene_family_id="culture_bookish",
        scene_tags={"interior", "bookish", "daylight"},
        setting_value="quiet reading room with shelves and polished tables",
    )


def test_issue112_active_location_rejects_terrace_and_rooftop_lines() -> None:
    terrace_record = line_bank_loader.normalize_line_bank_record(
        "locations",
        "1_3",
        "villa stone terrace with olive trees and open view",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    rooftop_record = line_bank_loader.normalize_line_bank_record(
        "locations",
        "1_3",
        "rooftop corner with low wall and pale concrete",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    for record in (terrace_record, rooftop_record):
        assert not line_bank_loader.line_bank_location_matches_scene(
            record,
            scene_family_id="coastal_boardwalk",
            scene_tags={"outdoor", "sporty", "daylight", "coastal", "active"},
            setting_value="shoreline workout pad beside pale stone, open water and bright coastal air",
        )


def test_issue112_fitness_long_hair_gets_headband_hint() -> None:
    candidate = _base_candidate("urban_daylight", "workout_top_leggings", "sport_clean_white")
    candidate["outfit_family_id"] = "zip_jacket_leggings"
    candidate["color_story_id"] = "powder_blue"
    candidate["hair_structure_id"] = "soft_half_up"
    candidate["hair_structure"] = "soft half-up hair with loose lengths"
    form_state = dict(prompt_service.DEFAULT_FORM_STATE)
    form_state.update({"mode": "women", "styleMode": "fitness"})

    constrained = postprocess._apply_prompt_constraints(candidate, form_state, spicy_level=5)

    assert "headband" in constrained["hair_structure_override"]


def test_issue112_medium_hair_does_not_get_headband_hint() -> None:
    candidate = _base_candidate("urban_daylight", "workout_top_leggings", "sport_clean_white")
    candidate["hair_structure_id"] = "shoulder_blowout"
    candidate["hair_structure"] = "shoulder-length blowout"
    form_state = dict(prompt_service.DEFAULT_FORM_STATE)
    form_state.update({"mode": "women", "styleMode": "fitness"})

    constrained = postprocess._apply_prompt_constraints(candidate, form_state, spicy_level=5)

    assert "hair_structure_override" not in constrained


def test_issue112_long_hair_does_not_always_get_headband_hint() -> None:
    candidate = _base_candidate("urban_daylight", "workout_top_leggings", "sport_clean_white")
    form_state = dict(prompt_service.DEFAULT_FORM_STATE)
    form_state.update({"mode": "women", "styleMode": "fitness"})

    constrained = postprocess._apply_prompt_constraints(candidate, form_state, spicy_level=5)

    assert "hair_structure_override" not in constrained


def test_issue112_fitness_color_order_is_not_old_blue_teal_pool() -> None:
    color_order = postprocess._color_order_for_style("fitness", 5)

    assert "black_ivory" in color_order
    assert "red_ivory" in color_order
    assert "terracotta_sand" in color_order
    assert "plum_blush" in color_order
    assert "sport_clean_white" in color_order
    assert color_order[:3] != ["sport_clean_white", "cobalt_white", "aqua_white"]


def test_issue112_active_sets_are_locked_to_athletic_materials() -> None:
    zip_front_predicate = selectors._outfit_material_predicate("zip_front_training_set")
    cross_strap_predicate = selectors._outfit_material_predicate("cross_strap_keyhole_active_set")

    assert zip_front_predicate({"id": "athletic_jersey"})
    assert cross_strap_predicate({"id": "athletic_jersey"})
    assert not zip_front_predicate({"id": "tailored_woven"})
    assert not cross_strap_predicate({"id": "tailored_woven"})
    assert not cross_strap_predicate({"id": "satin"})
    assert not cross_strap_predicate({"id": "vinyl_latex"})


def test_issue112_fitness_outfit_lines_reject_swim_and_lounge_text() -> None:
    swim_record = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "one piece swimsuit",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )
    lounge_record = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "tiny lounge shorts with a soft camisole",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )
    active_record = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "fitted zip top with tiny running shorts",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )

    assert line_bank_loader.line_bank_outfit_matches_scene(
        active_record,
        scene_family_id="coastal_boardwalk",
        style_mode="fitness",
        scene_tags={"outdoor", "sporty", "daylight", "coastal", "active"},
        setting_value="shoreline workout pad beside pale stone, open water and bright coastal air",
    )
    assert not line_bank_loader.line_bank_outfit_matches_scene(
        swim_record,
        scene_family_id="coastal_boardwalk",
        style_mode="fitness",
        scene_tags={"outdoor", "sporty", "daylight", "coastal", "active"},
        setting_value="shoreline workout pad beside pale stone, open water and bright coastal air",
    )
    assert not line_bank_loader.line_bank_outfit_matches_scene(
        lounge_record,
        scene_family_id="urban_daylight",
        style_mode="fitness",
        scene_tags={"interior", "sporty", "daylight", "gym", "active"},
        setting_value="performance gym floor with rubber training lanes, racks and clear daylight",
    )


def test_issue112_fitness_candidates_skip_generic_line_banks() -> None:
    form_state = dict(prompt_service.DEFAULT_FORM_STATE)
    form_state.update(
        {
            "mode": "women",
            "styleMode": "fitness",
            "photoTypeControl": "balanced",
            "batchSize": 1,
            "debugMode": True,
        }
    )

    run = prompt_service.generate_run(form_state)
    candidate = run["prompts"][0]["candidate"]

    assert candidate["line_bank_location"] == ""
    assert candidate["line_bank_outfit"] == ""
    assert candidate["line_bank_pose"] == ""


def test_issue112_fitness_render_adds_trainers_to_active_outfit_block() -> None:
    block = prompt_renderer._format_outfit_block(
        {
            "route": "sports_flirt",
            "tags": ["sporty", "active", "activewear"],
            "outfit_family_id": "workout_top_leggings",
            "outfit_family": "fitted workout top with sculpted leggings",
            "color_story_id": "black_ivory",
            "color_story": "black and ivory palette",
            "material": "athletic jersey",
            "scene_family_id": "urban_daylight",
            "setting_scene_id": "performance_gym_floor__rubber_lane_matte__resistance_bands_mat__warm_afternoon_glow",
            "setting_micro_id": "performance_gym_floor",
            "photo_treatment_id": "clean_commercial",
            "time_of_day_id": "afternoon",
        }
    )

    assert "trainers" in block.lower()


def test_issue112_fitness_render_does_not_duplicate_existing_shoes() -> None:
    block = prompt_renderer._format_outfit_block(
        {
            "route": "sports_flirt",
            "tags": ["sporty", "active", "activewear"],
            "line_bank_outfit": "zip training set with white sneakers",
            "line_bank_outfit_id": "fitness_line_demo",
            "outfit_family_id": "zip_front_training_set",
            "color_story_id": "sport_clean_white",
            "color_story": "clean white athletic story",
            "scene_family_id": "urban_daylight",
            "setting_scene_id": "performance_gym_floor__rubber_lane_matte__resistance_bands_mat__warm_afternoon_glow",
            "setting_micro_id": "performance_gym_floor",
            "photo_treatment_id": "clean_commercial",
            "time_of_day_id": "afternoon",
        }
    )

    assert block.lower().count("sneakers") == 1
    assert "trainers" not in block.lower()
