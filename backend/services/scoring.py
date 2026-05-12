from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

from backend.legacy_bridge import preview_male_identities
from backend.character_constraints import resolve_character_constraint_segment
from backend.engine import generator
from backend.forms import runtime_controls as form_runtime_controls
from backend.forms.constants import SCENE_FOCUS_PREFERENCES
from backend.forms.normalizer import _clean_text, _female_appearance_prompt, _female_custom_appearance_active, _tokenize_text
from backend.photo_treatment_mix import photo_treatment_mix_bucket, photo_treatment_quality_tier, photo_treatment_tone
from backend.services.batch_penalties import (
    _cheap_contract_fallback_penalty,
    _location_motif_clone_penalty,
    _muted_color_clone_penalty,
    _outfit_silhouette_clone_penalty,
    _scene_family_clone_penalty,
    _scene_outfit_clone_penalty,
    _treatment_outfit_clone_penalty,
)
from backend.services.diversity_scoring import (
    _close_up_angle_diversity_score,
    _same_person_visual_diversity_score,
    _women_random_outfit_color_diversity_score,
    _women_random_pose_mix_score,
)
from backend.services.photo_treatment_lookup import _photo_treatment_lookup
from backend.services.repeat_scoring import _anti_repeat_score
from backend.services import selection_scoring
from backend.services import treatment_balance


AGE_MAP = {
    "18": {"young_18"},
    "young 18": {"young_18"},
    "18-20": {"young_18", "young_19", "young_20"},
    "19": {"young_19"},
    "young 19": {"young_19"},
    "20": {"young_20"},
    "young 20": {"young_20"},
    "21": {"young_21"},
    "young 21": {"young_21"},
    "21-23": {"young_21", "young_22", "young_23"},
    "22": {"young_22"},
    "young 22": {"young_22"},
    "23": {"young_23"},
    "young 23": {"young_23"},
    "25-30": {"mid_20s"},
    "25": {"mid_20s"},
    "26": {"mid_20s"},
    "27": {"mid_20s"},
    "28": {"mid_20s"},
    "29": {"mid_20s"},
    "30+": {"early_30s", "late_30s"},
}

RACE_GROUP_HINTS = {
    "white": {"white", "european", "slavic", "balkan", "nordic", "caucasian"},
    "black": {"black", "african", "afro", "ethiopian", "nigerian"},
    "asian": {"asian", "east asian", "japanese", "korean", "chinese", "thai", "vietnamese"},
    "latina": {"latina", "latino", "hispanic", "brazilian", "colombian", "mexican", "argentinian"},
    "middle_eastern": {"middle eastern", "arab", "persian", "levantine", "turkish"},
    "south_asian": {"south asian", "indian", "pakistani", "bangladeshi", "sri lankan"},
    "mixed": {"mixed", "mixed race", "biracial", "multiracial"},
}

RANDOM_BRIGHT_LIGHTING_IDS = {
    "clean_daylight",
    "hard_direct_light",
    "direct_flash_clean",
    "studio_rim",
    "single_source_contrast",
    "tight_spotlight",
    "silhouette_edge",
}
RANDOM_MUTED_LIGHTING_IDS = {"soft_overcast", "warm_interior", "practical_lamp", "moody_darkness"}
RANDOM_BRIGHT_TREATMENT_IDS = {
    "clean_commercial",
    "direct_light_editorial",
    "disposable_camera",
    "vintage_flash_photo",
    "advertising_poster_realism",
    "cinematic_poster_realism",
}
RANDOM_MUTED_TREATMENT_IDS = {"analog_35mm", "documentary_still", "casual_indoor_selfie", "mirror_selfie"}
RANDOM_BRIGHT_ATMOSPHERE_IDS = {"bright_hard_sun", "warm_afternoon_glow", "soft_filtered_daylight", "controlled_studio_air"}

HIGH_SPICY_WOMEN_REVEALING_POSE_IDS = {
    "over_shoulder_arch_stand",
    "chair_forward_lean",
    "kneeling_arch_turn",
    "peek_a_boo_frame",
    "back_one_leg_crossed",
    "stairs_look_up_recline",
    "sofa_legs_stretched",
    "side_lie_hug_torso",
    "perch_lean_back",
    "forward_fold_cross_leg",
    "bed_back_view_turn",
    "hands_up_fixing_hair",
    "back_face_side_s_curve",
    "body_side_on_face_camera",
    "window_silhouette_arch",
    "walking_turn_look",
    "one_hand_head_one_hip",
    "arms_above_head_stand",
    "rear_edge_bed_pose",
    "mirror_hair_adjust",
    "hair_sprawl_recline",
    "table_lean_hips_back",
    "cube_side_twist_knee_hold",
    "counter_hip_lean_collar_touch",
    "bed_side_knees_angled_sweater_hold",
    "passenger_seat_twist_seatback_hold",
    "doorframe_arm_overhead_s_curve",
}

HIGH_SPICY_WOMEN_PUSHING_IT_POSE_IDS = {
    "heels_over_shoulder",
    "knees_up_arm_support",
    "legs_on_wall",
    "chair_open_angle",
    "chair_kneel_arch",
    "wall_arch_bent_knees",
    "crouch_over_shoulder",
    "squat_grounded_pose",
    "bed_kneel_sheet_grip",
}

HIGH_SPICY_WOMEN_POSE_IDS = HIGH_SPICY_WOMEN_REVEALING_POSE_IDS | HIGH_SPICY_WOMEN_PUSHING_IT_POSE_IDS

LOW_SPICY_UNSAFE_POSE_IDS = {
    "reclined_one_knee_up",
    "side_lying_lounge",
    "prone_elbows_down",
    "over_shoulder_arch_stand",
    "chair_forward_lean",
    "kneeling_arch_turn",
    "back_one_leg_crossed",
    "sofa_legs_stretched",
    "bed_back_view_turn",
    "heels_over_shoulder",
    "knees_up_arm_support",
    "body_side_on_face_camera",
    "legs_on_wall",
    "window_silhouette_arch",
    "chair_open_angle",
    "chair_kneel_arch",
    "rear_edge_bed_pose",
    "wall_arch_bent_knees",
    "crouch_over_shoulder",
    "squat_grounded_pose",
    "bed_kneel_sheet_grip",
}

HIGH_SPICY_WOMEN_REVEALING_OUTFIT_IDS = {
    "sheer_overlay_slip_dress",
    "blazer_bodysuit_set",
    "halter_cutout_jumpsuit",
    "bodycon_mesh_sleeves",
    "off_shoulder_knit_mini",
    "robe_layered_slip_set",
    "asym_cutout_column_dress",
    "structured_bustier_trousers",
    "ring_halter_trousers",
    "club_cami_wrap_skirt",
    "satin_bodysuit_wide_trousers",
    "strappy_cutout_mini_dress",
    "lined_sculptural_mini_dress",
    "lined_satin_mini_dress",
    "buttondown_shirt_dress_open_collar",
    "clean_satin_slip_dress",
    "sequin_evening_sheath_dress",
    "open_trench_mini_dress",
    "zip_front_training_set",
    "cross_strap_keyhole_active_set",
    "deep_v_jersey_jumpsuit",
    "tie_front_blouse_denim_mini",
}

HIGH_SPICY_WOMEN_PUSHING_IT_OUTFIT_IDS = {
    "corset_top_mini_skirt_set",
    "longline_bralette_sheer_shirt",
    "open_shirt_bodysuit",
    "harness_trim_blazer_set",
    "cowl_neck_micro_mini",
    "thigh_high_bodysuit_robe",
    "vinyl_trim_bodycon",
    "lace_up_cami_mini",
    "mesh_panel_bodycon",
    "sheer_buttondown_mini",
    "sheer_mesh_micro_skirt",
    "bandeau_low_rise_mini",
}

HIGH_SPICY_WOMEN_OUTFIT_IDS = HIGH_SPICY_WOMEN_REVEALING_OUTFIT_IDS | HIGH_SPICY_WOMEN_PUSHING_IT_OUTFIT_IDS

HAIR_LENGTH_PREFERENCES = {
    "short": {"sleek_bob", "natural_curls", "blunt_bob"},
    "medium": {"shoulder_blowout", "messy_bun", "polished_low_bun", "tucked_behind_ears_blowout"},
    "long": {"soft_waves", "high_ponytail", "side_braid", "long_straight", "soft_half_up"},
}

HAIR_COLOR_PREFERENCES = {
    "black": {"black_natural"},
    "dark_brown": {"dark_brown_natural"},
    "brown": {"medium_brown_natural", "dark_brown_natural"},
    "light_brown": {"light_brown_natural", "medium_brown_natural"},
    "blonde": {"blonde_natural"},
    "dark_blonde": {"dark_blonde_natural"},
    "red_ginger": {"copper_dyed", "auburn_natural"},
    "auburn": {"auburn_natural", "burgundy_dyed"},
    "gray_silver": {"silver_dyed"},
}

SAME_PERSON_RACE_GROUPS = {
    "mostly_whites": "white",
    "mostly_blacks": "black",
    "mostly_asian": "asian",
    "mostly_latina": "latina",
}

SAME_PERSON_ETHNICITY_IDS = {
    "white_american",
    "white_ukrainian",
    "white_russian",
    "white_polish",
    "white_italian",
    "white_spanish",
    "white_english",
    "black_american",
    "black_british",
    "black_nigerian",
    "latina_colombian",
    "latina_mexican",
    "latina_brazilian",
    "east_asian_chinese",
    "east_asian_japanese",
    "southeast_asian_thai",
    "southeast_asian_vietnamese",
    "southeast_asian_filipina",
    "middle_eastern",
    "south_asian",
}

MIXED_ETHNICITY_GROUPS = {"white", "black", "latina", "asian", "middle_eastern", "south_asian"}
MOSTLY_MIXED_ETHNICITY_IDS = {
    "white_russian",
    "white_ukrainian",
    "white_polish",
    "white_italian",
    "white_spanish",
    "black_american",
    "black_british",
    "black_nigerian",
    "latina_mexican",
    "latina_colombian",
    "latina_brazilian",
    "east_asian_chinese",
    "east_asian_japanese",
    "southeast_asian_thai",
    "southeast_asian_vietnamese",
    "southeast_asian_filipina",
    "middle_eastern",
    "south_asian",
}
RANDOM_DEFAULT_EXCLUDED_ETHNICITY_GROUPS = {"middle_eastern", "south_asian"}


def _mostly_mixed_ethnicity_ids() -> set[str]:
    return selection_scoring._mostly_mixed_ethnicity_ids()


def _random_default_ethnicity_ids() -> set[str]:
    return selection_scoring._random_default_ethnicity_ids()


def _women_active_high_spicy_pose_ids(spicy_level: int) -> set[str]:
    return selection_scoring._women_active_high_spicy_pose_ids(spicy_level)


def _women_active_high_spicy_outfit_ids(spicy_level: int) -> set[str]:
    return selection_scoring._women_active_high_spicy_outfit_ids(spicy_level)


def _normalize_age_filter(value: str) -> set[str] | None:
    return selection_scoring._normalize_age_filter(value)


def _custom_race_group(custom_race: str) -> str | None:
    return selection_scoring._custom_race_group(custom_race)


def _custom_race_preferences(custom_race: str) -> tuple[str | None, set[str]]:
    return selection_scoring._custom_race_preferences(custom_race)


def _custom_race_candidate_score(candidate: dict[str, Any], custom_race: str) -> int:
    return selection_scoring._custom_race_candidate_score(candidate, custom_race)


def _couples_different_persons_identity_constraints(form_state: dict[str, Any]) -> dict[str, set[str]]:
    return selection_scoring._couples_different_persons_identity_constraints(form_state)


def _male_age_matches_request(age_text: str, requested: str) -> bool:
    return selection_scoring._male_age_matches_request(age_text, requested)


def _custom_race_matches_identity_text(custom_race: str, identity: dict[str, Any]) -> bool:
    return selection_scoring._custom_race_matches_identity_text(custom_race, identity)


def _male_race_matches_request(male_identity: dict[str, Any], race_preset: str, custom_race: str = "") -> bool:
    return selection_scoring._male_race_matches_request(male_identity, race_preset, custom_race)


def _explicit_male_identity_constraints_active(form_state: dict[str, Any]) -> bool:
    return selection_scoring._explicit_male_identity_constraints_active(form_state)


def _couples_male_identity_score(
    batch: list[dict[str, Any]],
    form_state: dict[str, Any],
    style_mode: str,
    seed: int,
) -> tuple[int, bool]:
    return selection_scoring._couples_male_identity_score(batch, form_state, style_mode, seed)


def _race_score(batch: list[dict[str, Any]], race_preset: str, custom_race: str = "") -> int:
    return selection_scoring._race_score(batch, race_preset, custom_race)


def _body_score(batch: list[dict[str, Any]], preset: str) -> int:
    return selection_scoring._body_score(batch, preset)


def _style_score(candidate: dict[str, Any], style_mode: str) -> int:
    return selection_scoring._style_score(candidate, style_mode)


def _photo_treatment_candidate_score(candidate: dict[str, Any], style_mode: str, mode: str = "women") -> int:
    treatment_id = candidate.get("photo_treatment_id")
    if not treatment_id:
        return 0
    profile = _photo_treatment_lookup().get(treatment_id)
    if not profile:
        return 0
    score = 0
    harder_lanes = {"concept_photo_editorial", "direct_light_editorial"}
    casual_stylized_lanes = {
        "mirror_selfie",
        "disposable_camera",
        "documentary_still",
        "casual_indoor_selfie",
        "vintage_flash_photo",
        "advertising_poster_realism",
    }
    scene_family = candidate.get("scene_family_id", "")
    capture_id = candidate.get("capture_style_id", "")
    lighting_id = candidate.get("lighting_family_id", "")
    time_id = candidate.get("time_of_day_id", "")
    allowed_scenes = {str(value) for value in profile.get("allowed_scene_families", [])}
    banned_scenes = {str(value) for value in profile.get("banned_scene_families", [])}
    allowed_styles = {str(value) for value in profile.get("allowed_style_modes", [])}
    banned_styles = {str(value) for value in profile.get("banned_style_modes", [])}
    preferred_scenes = {str(value) for value in profile.get("preferred_scene_families", [])}
    preferred_styles = {str(value) for value in profile.get("preferred_style_modes", [])}
    preferred_captures = {str(value) for value in profile.get("preferred_capture_ids", [])}
    preferred_lighting = {str(value) for value in profile.get("preferred_lighting_ids", [])}
    preferred_times = {str(value) for value in profile.get("preferred_time_ids", [])}
    if allowed_scenes and scene_family not in allowed_scenes:
        score -= 24
    if scene_family in banned_scenes:
        score -= 28
    if allowed_styles and style_mode not in allowed_styles and style_mode != "random":
        score -= 18
    if style_mode in banned_styles:
        score -= 24
    if scene_family in preferred_scenes:
        score += 12
    if style_mode in preferred_styles:
        score += 9
    if capture_id in preferred_captures:
        score += 8
    if lighting_id in preferred_lighting:
        score += 8
    if time_id in preferred_times:
        score += 6
    category = candidate.get("photo_treatment_category", "")
    mix_bucket = photo_treatment_mix_bucket(str(treatment_id or ""), str(category or ""))
    quality_tier = photo_treatment_quality_tier(str(treatment_id or ""), str(category or ""))
    treatment_tone = photo_treatment_tone(str(treatment_id or ""), str(category or ""))
    if style_mode == "random":
        score += 3 if category == "stylized" else 2
        if treatment_id in harder_lanes:
            score += 8
        if treatment_id in casual_stylized_lanes:
            score += 6
        if treatment_id == "clean_commercial":
            score += 2
        if _random_flat_light_candidate(candidate):
            score -= 30
        if mode == "women":
            if mix_bucket == "phone_snapshot":
                score -= 10
            elif mix_bucket == "casual_low_end":
                score -= 18
            elif mix_bucket == "editorial_non_phone":
                score += 8
            elif mix_bucket == "polished_glam":
                score += 14
            if quality_tier == "raw_low_end":
                score -= 14
            elif quality_tier == "casual":
                score -= 6
            elif quality_tier == "clean":
                score += 4
            elif quality_tier == "premium":
                score += 6
            if treatment_tone in {"documentary", "snapshot"}:
                score -= 6
            if treatment_tone in {"beauty", "editorial", "cinematic", "dramatic"}:
                score += 4
            if treatment_id in {"direct_light_editorial", "concept_photo_editorial", "cinematic_poster_realism", "advertising_poster_realism", "studio_seamless"}:
                score += 5
            if treatment_id == "clean_commercial":
                score += 1
        if mode == "couples" and treatment_id == "clean_commercial":
            score += 3
    elif style_mode in {"nightlife", "studio", "creative_artistic"}:
        score += 8 if category == "stylized" else -3
        if treatment_id in harder_lanes:
            score += 14
        if style_mode == "nightlife" and treatment_id == "vintage_flash_photo":
            score += 10
        if style_mode == "nightlife" and treatment_id in {"direct_flash_night", "low_key_dramatic", "cinematic_poster_realism"}:
            score += 8
        if style_mode == "nightlife" and treatment_id == "clean_commercial":
            score -= 10
        if mode == "women" and style_mode == "nightlife":
            if treatment_id in {"vintage_flash_photo", "direct_flash_night", "low_key_dramatic", "cinematic_poster_realism", "disposable_camera", "concept_photo_editorial"}:
                score += 8
            if treatment_id == "clean_commercial":
                score -= 10
        if mode == "men" and style_mode == "nightlife":
            if treatment_id in {"direct_flash_night", "low_key_dramatic", "cinematic_poster_realism", "vintage_flash_photo", "direct_light_editorial", "analog_35mm"}:
                score += 12
            if treatment_id == "clean_commercial":
                score -= 18
        if style_mode == "studio" and treatment_id == "advertising_poster_realism":
            score += 10
        if style_mode == "creative_artistic" and treatment_id in {"vintage_flash_photo", "advertising_poster_realism"}:
            score += 8
        if mode == "women" and style_mode == "creative_artistic":
            if treatment_id in {"concept_photo_editorial", "direct_light_editorial", "advertising_poster_realism", "vintage_flash_photo", "documentary_still"}:
                score += 8
            if treatment_id == "clean_commercial":
                score -= 10
    elif style_mode in {"luxury", "romantic"}:
        score += 9 if category == "stylized" else -4
        if treatment_id in harder_lanes:
            score += 15 if style_mode == "luxury" else 11
        if mode == "men" and style_mode == "luxury":
            score += 12 if category == "stylized" else -10
            if treatment_id in {"direct_flash_night", "cinematic_poster_realism", "direct_light_editorial", "analog_35mm", "low_key_dramatic", "documentary_still"}:
                score += 8
            if lighting_id in {"hard_direct_light", "warm_interior", "practical_lamp", "direct_flash_clean", "moody_darkness", "tight_spotlight", "silhouette_edge"}:
                score += 6
            if treatment_id == "clean_commercial":
                score -= 28
        if mode == "men" and style_mode == "romantic":
            score += 16 if category == "stylized" else -14
            if treatment_id in {"analog_35mm", "documentary_still", "disposable_camera", "candid_phone_snapshot", "low_key_dramatic", "direct_light_editorial"}:
                score += 12
            if treatment_id == "clean_commercial":
                score -= 22
        if mode == "women" and style_mode == "luxury":
            if quality_tier == "raw_low_end":
                score -= 24
            elif quality_tier == "casual":
                score -= 18
            if treatment_tone in {"phone", "documentary", "snapshot"}:
                score -= 16
            if treatment_tone in {"beauty", "editorial", "cinematic", "dramatic"}:
                score += 8
            if treatment_id in {"direct_light_editorial", "concept_photo_editorial", "cinematic_poster_realism", "advertising_poster_realism", "vintage_flash_photo"}:
                score += 10
            if treatment_id == "clean_commercial":
                score -= 14
        if mode == "women" and style_mode == "romantic":
            if quality_tier == "raw_low_end":
                score -= 18
            elif quality_tier == "casual":
                score -= 12
            if treatment_tone in {"phone", "documentary", "snapshot"}:
                score -= 10
            if treatment_tone in {"beauty", "editorial", "cinematic", "filmic"}:
                score += 6
            if treatment_id in {"analog_35mm", "documentary_still", "candid_phone_snapshot", "disposable_camera", "direct_light_editorial", "cinematic_poster_realism"}:
                score += 10
            if treatment_id == "clean_commercial":
                score -= 18
        if style_mode == "luxury" and treatment_id in {"casual_indoor_selfie", "advertising_poster_realism", "vintage_flash_photo"}:
            score += 8
    elif style_mode in {"lifestyle", "urban_day"}:
        score += 7 if category == "stylized" else -2
        if treatment_id == "direct_light_editorial":
            score += 8
        if treatment_id in casual_stylized_lanes:
            score += 12
        if mode == "women" and treatment_id in {"candid_phone_snapshot", "analog_35mm", "documentary_still", "casual_indoor_selfie"}:
            score += 10
        if treatment_id == "clean_commercial":
            score -= 10
    elif style_mode in {"cultural_bookish", "creative_artistic"}:
        score += 8 if category == "stylized" else -2
        if treatment_id in casual_stylized_lanes:
            score += 10
        if style_mode == "creative_artistic" and treatment_id in {"concept_photo_editorial", "direct_light_editorial", "advertising_poster_realism"}:
            score += 8
        if style_mode == "creative_artistic" and treatment_id == "clean_commercial":
            score -= 8
    elif style_mode in {"sport", "fitness", "coastal", "vacation"}:
        score += 4 if category == "polished" else -1
        if style_mode == "fitness":
            if mode == "women":
                if category == "stylized":
                    score += 12
                if category == "polished":
                    score -= 6
                if treatment_id in {"candid_phone_snapshot", "analog_35mm", "documentary_still", "direct_light_editorial", "disposable_camera"}:
                    score += 16
                if scene_family == "wellness_spa" and treatment_id in {"candid_phone_snapshot", "analog_35mm", "documentary_still"}:
                    score += 8
                if treatment_id == "clean_commercial":
                    score -= 24
            else:
                if category == "stylized":
                    score += 5
                if treatment_id in {"candid_phone_snapshot", "analog_35mm", "documentary_still", "direct_light_editorial"}:
                    score += 10
                if treatment_id == "clean_commercial":
                    score -= 8
    if mode == "couples" and style_mode == "random":
        if category == "polished":
            score -= 12
        if category == "stylized":
            score += 16
        if treatment_id in {
            "candid_phone_snapshot",
            "casual_indoor_selfie",
            "mirror_selfie",
            "disposable_camera",
            "analog_35mm",
            "cinematic_poster_realism",
            "direct_light_editorial",
            "documentary_still",
            "concept_photo_editorial",
            "vintage_flash_photo",
            "advertising_poster_realism",
        }:
            score += 18
        if treatment_id == "clean_commercial":
            score -= 80
    return score


def _photo_treatment_batch_score(batch: list[dict[str, Any]], style_mode: str, mode: str = "women") -> int:
    return treatment_balance._photo_treatment_batch_score(batch, style_mode, mode)


def _vibe_score(candidate: dict[str, Any], vibe: str) -> int:
    if vibe == "random":
        return 0
    mood = candidate["mood_energy_id"]
    capture = candidate["capture_style_id"]
    makeup = candidate["makeup_style_id"]
    lighting = candidate["lighting_family_id"]
    tags = set(candidate.get("tags", []))
    mapping = {
        "soft": int(mood == "soft_flirty") * 10 + int(lighting == "soft_overcast") * 8,
        "clean": int(lighting == "clean_daylight") * 10 + int("clean" in tags) * 6,
        "sexy": int(mood in {"soft_flirty", "slow_seductive"}) * 10 + int("slutty" in tags) * 6,
        "glam": int(makeup == "night_out_glam") * 10 + int(candidate["beauty_level_id"] == "beautified_glam") * 8,
        "cinematic": int(candidate["route"] == "cinematic_night") * 10 + int(capture == "editorial_photo") * 5,
        "casual": int(capture in {"lifestyle_photo", "smartphone_photo"}) * 10,
        "flirty": int(mood in {"soft_flirty", "bratty"}) * 10,
        "rich": int("luxury" in tags) * 10 + int(candidate["scene_family_id"] in {"residential_luxury", "hospitality_suite"}) * 6,
        "editorial": int(capture == "editorial_photo") * 12,
    }
    return mapping.get(vibe, 0)


def _framing_score(candidate: dict[str, Any], control: str) -> int:
    framing = candidate["camera_framing_id"]
    if control == "random" or control == "mixed":
        return 0
    if control == "more_portraits":
        return 10 if framing in {"waist_up", "bust_up", "close_portrait", "head_and_shoulders", "face_only", "below_chest_portrait"} else -4
    if control == "more_full_body":
        return 10 if framing in {"full_body", "ankle_up"} else -4
    if control == "medium_shots":
        return 10 if framing in {"knee_up", "cowboy_shot"} else -4
    return 0


def _lighting_score(candidate: dict[str, Any], control: str) -> int:
    lighting = candidate["lighting_family_id"]
    if control == "random" or control == "mixed":
        return 0
    if control == "sunny":
        return 10 if lighting == "clean_daylight" else -3
    if control == "indoor_warm":
        return 10 if lighting == "warm_interior" else -3
    if control == "night":
        return 10 if lighting == "neon_night" else -3
    return 0


def _spicy_score(candidate: dict[str, Any], spicy_level: int) -> int:
    mood = candidate["mood_energy_id"]
    route = candidate["route"]
    tags = set(candidate.get("tags", []))
    seductive_signal = 4 if "seductive" in tags else 0
    slutty_signal = 8 if "slutty" in tags else 0
    active_high_spicy_pose_ids = _women_active_high_spicy_pose_ids(spicy_level)
    active_high_spicy_outfit_ids = _women_active_high_spicy_outfit_ids(spicy_level)
    pose_signal = {6: 10, 7: 14, 8: 16}.get(spicy_level, 0) if candidate.get("pose_family_id") in active_high_spicy_pose_ids else 0
    outfit_signal = {6: 6, 7: 8, 8: 10}.get(spicy_level, 0) if candidate.get("outfit_family_id") in active_high_spicy_outfit_ids else 0
    mapping = {
        3: int(mood == "calm_confident") * 12 + int(mood == "soft_flirty") * 6,
        4: int(mood in {"bratty", "soft_flirty"}) * 10,
        5: int(mood == "soft_flirty") * 12 + int(mood == "bratty") * 6,
        6: int(mood == "slow_seductive") * 12 + int(route == "slutty_lifestyle") * 6 + pose_signal + outfit_signal,
        7: int(mood == "slow_seductive") * 12 + int(route == "slutty_lifestyle") * 6 + slutty_signal + seductive_signal + pose_signal + outfit_signal,
        8: int(mood == "slow_seductive") * 12 + int(route == "slutty_lifestyle") * 8 + slutty_signal + seductive_signal + pose_signal + outfit_signal,
    }
    return mapping.get(spicy_level, 0)


def _mode_specific_spicy_score(candidate: dict[str, Any], mode: str, style_mode: str, spicy_level: int) -> int:
    if spicy_level <= 5:
        return 0
    mood = candidate["mood_energy_id"]
    route = candidate["route"]
    scene = candidate["scene_family_id"]
    treatment_id = str(candidate.get("photo_treatment_id", "") or "")
    tags = set(candidate.get("tags", []))
    active_high_spicy_pose_ids = _women_active_high_spicy_pose_ids(spicy_level)
    active_high_spicy_outfit_ids = _women_active_high_spicy_outfit_ids(spicy_level)
    women_pose_bonus = {6: 6, 7: 9, 8: 10}.get(spicy_level, 0) if candidate.get("pose_family_id") in active_high_spicy_pose_ids else 0
    women_outfit_bonus = {6: 5, 7: 7, 8: 8}.get(spicy_level, 0) if candidate.get("outfit_family_id") in active_high_spicy_outfit_ids else 0
    seductive_bonus = 5 if "seductive" in tags else 0
    slutty_bonus = 8 if "slutty" in tags else 0
    score = 0
    if mode == "men":
        mapping = {
            6: int(mood == "slow_seductive") * 8 + int(route == "cinematic_night") * 4,
            7: int(mood == "slow_seductive") * 10 + int(route in {"cinematic_night", "slutty_lifestyle"}) * 5,
            8: int(mood == "slow_seductive") * 12 + int(route in {"cinematic_night", "slutty_lifestyle"}) * 6,
        }
        score += mapping.get(spicy_level, 0)
        if style_mode in {"random", "nightlife", "romantic", "luxury"} and treatment_id in {
            "direct_flash_night",
            "low_key_dramatic",
            "direct_light_editorial",
            "concept_photo_editorial",
            "cinematic_poster_realism",
            "analog_35mm",
            "documentary_still",
        }:
            score += 8 if spicy_level >= 7 else 5
        score += seductive_bonus + slutty_bonus
    elif mode == "couples":
        mapping = {
            6: int(mood == "slow_seductive") * 10 + int(route in {"cinematic_night", "slutty_lifestyle"}) * 4,
            7: int(mood == "slow_seductive") * 12 + int(route in {"cinematic_night", "slutty_lifestyle"}) * 6,
            8: int(mood == "slow_seductive") * 14 + int(route in {"cinematic_night", "slutty_lifestyle"}) * 8,
        }
        score += mapping.get(spicy_level, 0)
        score += women_pose_bonus + women_outfit_bonus + seductive_bonus + slutty_bonus
        if style_mode in {"random", "romantic", "nightlife"} and treatment_id in {
            "direct_flash_night",
            "low_key_dramatic",
            "cinematic_poster_realism",
            "analog_35mm",
            "vintage_flash_photo",
            "direct_light_editorial",
        }:
            score += 8 if spicy_level >= 7 else 5
        if scene in {"nightlife_bar", "nightlife_neon"}:
            score += 5 if spicy_level >= 7 else 3
    return score


def _women_high_spicy_pose_mix_score(batch: list[dict[str, Any]], spicy_level: int) -> int:
    active_pose_ids = _women_active_high_spicy_pose_ids(spicy_level)
    if spicy_level < 6 or not active_pose_ids or not batch:
        return 0
    batch_size = len(batch)
    spicy_pose_ids = [candidate.get("pose_family_id") for candidate in batch if candidate.get("pose_family_id") in active_pose_ids]
    spicy_pose_count = len(spicy_pose_ids)
    unique_spicy_pose_count = len(set(spicy_pose_ids))
    target_spicy_count = math.ceil(batch_size * 0.65)
    ordinary_cap = batch_size - target_spicy_count
    score = min(spicy_pose_count, target_spicy_count) * 6
    score += unique_spicy_pose_count * 4
    if spicy_pose_count < target_spicy_count:
        score -= (target_spicy_count - spicy_pose_count) * 18
    ordinary_pose_count = batch_size - spicy_pose_count
    if ordinary_pose_count > ordinary_cap:
        score -= (ordinary_pose_count - ordinary_cap) * 12
    return score


def _candidate_text_blob(candidate: dict[str, Any]) -> str:
    fields = [
        candidate.get("ethnicity", ""),
        candidate.get("body_type", ""),
        candidate.get("hair_color", ""),
        candidate.get("eye_color", ""),
        candidate.get("hair_structure", ""),
        candidate.get("makeup_style", ""),
        candidate.get("outfit_family", ""),
        candidate.get("material", ""),
        candidate.get("color_story", ""),
        candidate.get("scene_family_id", ""),
        candidate.get("setting_scene", ""),
        candidate.get("route", ""),
        candidate.get("capture_style", ""),
        candidate.get("lighting_family", ""),
        candidate.get("mood_energy", ""),
        " ".join(candidate.get("tags", [])),
    ]
    return " ".join(str(value).lower() for value in fields if value)


def _free_text_overlap_score(candidate: dict[str, Any], text: str, per_token: int, phrase_bonus: int = 0) -> int:
    cleaned = _clean_text(text)
    if not cleaned:
        return 0
    blob = _candidate_text_blob(candidate)
    score = phrase_bonus if cleaned.lower() in blob else 0
    for token in _tokenize_text(cleaned):
        if token in blob:
            score += per_token
    return score


def _appearance_text_score(candidate: dict[str, Any], text: str) -> int:
    return _free_text_overlap_score(candidate, text, per_token=5, phrase_bonus=14)


def _appearance_prompt_profile(text: str) -> dict[str, bool]:
    tokens = set(_tokenize_text(text))
    return {
        "reserved": bool(tokens & {"soft", "clean", "polished", "blouse", "midi", "tailored", "trousers", "cardigan", "knit", "ivory", "minimal"}),
        "sporty": bool(tokens & {"sport", "sporty", "athletic", "workout", "gym", "training", "tennis", "leggings", "jersey"}),
        "nightlife": bool(tokens & {"night", "nightlife", "bar", "cocktail", "club", "party", "glam", "evening"}),
    }


def _appearance_profile_score(candidate: dict[str, Any], text: str) -> int:
    if not text:
        return 0
    profile = _appearance_prompt_profile(text)
    score = 0
    tags = set(candidate.get("tags", []))
    mood = candidate.get("mood_energy_id")
    pose = candidate.get("pose_family_id")
    hand = candidate.get("hand_action_id")
    scene = candidate.get("scene_family_id")
    route = candidate.get("route")
    if profile["reserved"]:
        score += 8 if "reserved" in tags else 0
        score += 12 if mood == "calm_confident" else 5 if mood == "soft_flirty" else -16 if mood in {"slow_seductive", "bratty"} else 0
        score -= 16 if pose in LOW_SPICY_UNSAFE_POSE_IDS else 0
        score -= 8 if hand in {"hand_on_thigh", "touching_strap", "hooked_waistband"} else 0
        score -= 18 if scene in {"nightlife_bar", "nightlife_neon"} else 0
        score -= 12 if route == "cinematic_night" else 0
    if profile["sporty"]:
        score += 12 if scene == "urban_daylight" else -6
        score += 10 if route == "sports_flirt" else -6
        score += 8 if {"sporty", "athletic"} & tags else 0
    if profile["nightlife"]:
        score += 12 if scene in {"nightlife_bar", "nightlife_neon"} else -8
        score += 10 if route == "cinematic_night" else -5
    return score


def _scene_focus_score(candidate: dict[str, Any], scene_focus: str) -> int:
    if scene_focus == "random":
        return 0
    profile = SCENE_FOCUS_PREFERENCES.get(scene_focus)
    if not profile:
        return 0
    score = 0
    tags = set(candidate.get("tags", []))
    if candidate.get("scene_family_id") in profile.get("required_scene_families", set()):
        score += 18
    else:
        score -= 14
    if candidate.get("route") in profile.get("preferred_route_ids", set()):
        score += 10
    if candidate.get("capture_style_id") in profile.get("preferred_capture_ids", set()):
        score += 6
    if tags & profile.get("preferred_tags", set()):
        score += 6
    return score


def _women_scene_family_score(candidate: dict[str, Any], scene_family_id: str) -> int:
    if scene_family_id == "random":
        return 0
    return 30 if candidate.get("scene_family_id") == scene_family_id else -18


def _women_scene_family_batch_score(batch: list[dict[str, Any]], scene_family_id: str) -> int:
    if scene_family_id == "random":
        return 0
    matching = sum(1 for candidate in batch if candidate.get("scene_family_id") == scene_family_id)
    return (matching * 20) - ((len(batch) - matching) * 12)


def _exact_theme_score(candidate: dict[str, Any], exact_theme: str, location_strategy: str) -> int:
    if not exact_theme:
        return 0
    per_token = 10 if location_strategy == "exact_theme" else 5
    phrase_bonus = 24 if location_strategy == "exact_theme" else 10
    score = _free_text_overlap_score(candidate, exact_theme, per_token=per_token, phrase_bonus=phrase_bonus)
    matched_hints = form_runtime_controls._matched_theme_hints(exact_theme)
    tags = set(candidate.get("tags", []))
    for hint in matched_hints:
        if candidate.get("scene_family_id") in hint["scene_families"]:
            score += 18 if location_strategy == "exact_theme" else 8
        if candidate.get("route") in hint["routes"]:
            score += 16 if location_strategy == "exact_theme" else 6
        if tags & hint["tags"]:
            score += 10 if location_strategy == "exact_theme" else 4
    return score


def _exact_theme_batch_score(batch: list[dict[str, Any]], exact_theme: str, location_strategy: str) -> int:
    if location_strategy != "exact_theme" or not exact_theme:
        return 0
    matched_hints = form_runtime_controls._matched_theme_hints(exact_theme)
    if not matched_hints:
        return 0
    preferred_scenes = set().union(*(hint["scene_families"] for hint in matched_hints))
    preferred_routes = set().union(*(hint["routes"] for hint in matched_hints))
    preferred_tags = set().union(*(hint["tags"] for hint in matched_hints))
    score = 0
    for candidate in batch:
        tags = set(candidate.get("tags", []))
        matches = candidate.get("scene_family_id") in preferred_scenes or candidate.get("route") in preferred_routes or bool(tags & preferred_tags)
        score += 26 if matches else -16
    return score


def _random_scene_group(candidate: dict[str, Any]) -> str:
    scene_family_id = str(candidate.get("scene_family_id", "") or "")
    tags = set(candidate.get("tags", [])) | set(candidate.get("setting_tags", []))
    if scene_family_id in {"coastal_pool", "coastal_boardwalk"}:
        return "water"
    if scene_family_id in {"courtyard_garden", "garden_conservatory"}:
        return "nature"
    text = " ".join(
        str(candidate.get(field, "") or "")
        for field in ("line_bank_location", "setting_scene", "setting_micro")
    ).lower()
    if any(
        token in text
        for token in ("poolside", "beach", "shore", "marina", "lagoon", "boardwalk", "waterside", "coastal")
    ):
        return "water"
    if any(
        token in text
        for token in ("garden", "park", "meadow", "field", "grove", "greenhouse", "conservatory", "courtyard")
    ):
        return "nature"
    if scene_family_id in {"urban_daylight"}:
        return "urban_outdoor"
    if tags & {"outdoor", "rooftop", "sunny", "daylight", "sunlit", "summer"}:
        return "urban_outdoor"
    return "indoor"


def _is_random_bright_candidate(candidate: dict[str, Any]) -> bool:
    tags = set(candidate.get("tags", [])) | set(candidate.get("setting_tags", []))
    bright_score = 0
    muted_score = 0
    if tags & {"sunny", "summer", "daylight", "sunlit"}:
        bright_score += 1
    if tags & {"night", "rain", "quiet", "restorative"}:
        muted_score += 1
    if candidate.get("lighting_family_id") == "clean_daylight":
        bright_score += 1
    elif candidate.get("lighting_family_id") in RANDOM_BRIGHT_LIGHTING_IDS:
        bright_score += 2
    if candidate.get("lighting_family_id") == "soft_overcast":
        muted_score += 2
    elif candidate.get("lighting_family_id") in RANDOM_MUTED_LIGHTING_IDS:
        muted_score += 1
    if candidate.get("photo_treatment_id") in RANDOM_BRIGHT_TREATMENT_IDS:
        bright_score += 1
    if candidate.get("photo_treatment_id") in RANDOM_MUTED_TREATMENT_IDS:
        muted_score += 1
    if candidate.get("atmosphere_cue_id") in RANDOM_BRIGHT_ATMOSPHERE_IDS:
        bright_score += 1
    return bright_score >= 2 and bright_score > muted_score


def _random_flat_light_candidate(candidate: dict[str, Any]) -> bool:
    scene_family_id = candidate.get("scene_family_id")
    treatment_id = candidate.get("photo_treatment_id")
    lighting_id = candidate.get("lighting_family_id")
    if scene_family_id not in {"residential_luxury", "hospitality_suite", "culture_bookish", "garden_conservatory"}:
        return False
    if treatment_id == "casual_indoor_selfie" and lighting_id in {"clean_daylight", "soft_overcast", "warm_interior"}:
        return True
    if treatment_id == "clean_commercial" and lighting_id in {"soft_overcast", "warm_interior"}:
        return True
    return False


def _cheap_contract_fallback_candidate(candidate: dict[str, Any]) -> bool:
    scene_family_id = str(candidate.get("scene_family_id", "") or "")
    treatment_id = str(candidate.get("photo_treatment_id", "") or "")
    lighting_id = str(candidate.get("lighting_family_id", "") or "")
    if scene_family_id in {"culture_bookish", "garden_conservatory"}:
        if treatment_id == "clean_commercial" and lighting_id in {"clean_daylight", "soft_overcast", "warm_interior"}:
            return True
    if scene_family_id in {"residential_luxury", "hospitality_suite"}:
        if treatment_id == "clean_commercial" and lighting_id in {"clean_daylight", "soft_overcast", "warm_interior"}:
            return True
        if treatment_id == "casual_indoor_selfie" and lighting_id in {"clean_daylight", "soft_overcast", "warm_interior"}:
            return True
    return False


def _random_light_scene_balance_score(batch: list[dict[str, Any]]) -> int:
    if not batch:
        return 0
    total = len(batch)
    scene_groups = Counter(_random_scene_group(candidate) for candidate in batch)
    outdoor_count = sum(scene_groups.get(group, 0) for group in ("urban_outdoor", "water", "nature", "outdoor"))
    water_count = scene_groups.get("water", 0)
    nature_count = scene_groups.get("nature", 0)
    bright_count = sum(1 for candidate in batch if _is_random_bright_candidate(candidate))
    target_outdoor = round(total * 0.6)
    target_bright = round(total * 0.7)
    target_water = round(total * 0.2)
    target_nature = round(total * 0.2)
    score = 0
    score -= abs(outdoor_count - target_outdoor) * 10
    score -= abs(bright_count - target_bright) * 8
    score -= abs(water_count - target_water) * 14
    score -= abs(nature_count - target_nature) * 14
    score += max(0, 16 - abs(outdoor_count - target_outdoor) * 4)
    score += max(0, 16 - abs(bright_count - target_bright) * 4)
    score += max(0, 20 - abs(water_count - target_water) * 5)
    score += max(0, 20 - abs(nature_count - target_nature) * 5)
    muted_lighting_count = sum(1 for candidate in batch if candidate.get("lighting_family_id") in RANDOM_MUTED_LIGHTING_IDS)
    muted_treatment_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in RANDOM_MUTED_TREATMENT_IDS)
    muted_lighting_cap = max(7, round(total * 0.35))
    muted_treatment_cap = max(7, round(total * 0.35))
    cheap_flat_light_count = sum(1 for candidate in batch if _random_flat_light_candidate(candidate))
    if muted_lighting_count > muted_lighting_cap:
        score -= (muted_lighting_count - muted_lighting_cap) * 8
    if muted_treatment_count > muted_treatment_cap:
        score -= (muted_treatment_count - muted_treatment_cap) * 6
    if cheap_flat_light_count:
        score -= cheap_flat_light_count * 24
    if water_count < target_water:
        score -= (target_water - water_count) * 24
    if nature_count < target_nature:
        score -= (target_nature - nature_count) * 24
    return score


def _outfit_reveal_score(candidate: dict[str, Any], reveal_mode: str) -> int:
    if reveal_mode == "random":
        return 0
    tags = set(candidate.get("tags", []))
    if reveal_mode == "reserved":
        return 18 if "reserved" in tags else -10
    if reveal_mode == "balanced":
        return 12 if "balanced_reveal" in tags or candidate.get("outfit_family_id") in {"mini_dress", "cardigan_trousers", "blouse_trousers", "knit_top_trousers", "silk_blouse_midi_skirt", "structured_day_dress"} else -4
    if reveal_mode == "revealing":
        return 14 if "revealing" in tags or candidate.get("outfit_family_id") == "crop_top_mini_skirt" else -5
    if reveal_mode == "pushing_it":
        return 16 if "pushing_it" in tags or candidate.get("outfit_family_id") in {"latex_editorial", "bikini_set"} else -8
    return 0


def _hair_atom_score(candidate: dict[str, Any], form_state: dict[str, Any]) -> int:
    score = 0
    hair_structure_id = candidate.get("hair_structure_id")
    hair_color_id = candidate.get("hair_color_id")
    hair_tags = set(candidate.get("tags", [])) | set(candidate.get("hair_color_tags", []))
    if form_state["hairstyle"] not in {"random", "custom"}:
        score += 18 if hair_structure_id == form_state["hairstyle"] else -10
    elif form_state["hairLength"] in HAIR_LENGTH_PREFERENCES:
        score += 12 if hair_structure_id in HAIR_LENGTH_PREFERENCES[form_state["hairLength"]] else -6
    if form_state["hairColorControl"] in HAIR_COLOR_PREFERENCES:
        preferred = HAIR_COLOR_PREFERENCES[form_state["hairColorControl"]]
        score += 16 if hair_color_id in preferred else -8
    if form_state["hairstyle"] == "custom" and form_state.get("customHair"):
        score += _free_text_overlap_score(candidate, form_state["customHair"], per_token=5, phrase_bonus=12)
    if form_state["hairColorControl"] == "custom" and form_state.get("customHairColor"):
        score += _free_text_overlap_score(candidate, form_state["customHairColor"], per_token=6, phrase_bonus=14)
    if form_state["hairColorControl"] == "random" and "vivid_colored_hair" in hair_tags:
        score -= 12
    return score


def _makeup_atom_score(candidate: dict[str, Any], makeup_control: str) -> int:
    if makeup_control == "random":
        return 0
    return 16 if candidate.get("makeup_style_id") == makeup_control else -8


def _eye_color_score(candidate: dict[str, Any], control: str) -> int:
    if control == "random":
        return 0
    return 16 if candidate.get("eye_color_id") == control else -8


def _breast_size_score(candidate: dict[str, Any], control: str) -> int:
    if control == "random":
        return 0
    return 18 if candidate.get("breast_size_id") == control else -12


def _character_constraint_score(candidate: dict[str, Any], character_constraint: str) -> int:
    score_text = resolve_character_constraint_segment(candidate=candidate, character_constraint=character_constraint)
    if not score_text:
        return 0
    return _free_text_overlap_score(candidate, score_text, per_token=3, phrase_bonus=6)


def _validation_penalty(findings_count: int, mode: str) -> int:
    if mode == "loose":
        return 0
    if mode == "strict":
        return -500 * findings_count
    return -120 * findings_count




def _batch_score(
    batch: list[dict[str, Any]],
    form_state: dict[str, Any],
    findings_by_index: dict[int, list[dict[str, str]]],
    spicy_level: int,
    seed: int,
) -> tuple[int, bool]:
    score = 0
    hard_fail = False
    female_custom_appearance = _female_custom_appearance_active(form_state)
    low_spicy_unsafe_hand_ids = {"hand_on_thigh", "touching_strap", "hooked_waistband"}
    allowed_ages = _normalize_age_filter(form_state["age"])
    if allowed_ages:
        for candidate in batch:
            if candidate["age_band_id"] in allowed_ages:
                score += 14
            else:
                score -= 18
    score += _race_score(batch, form_state["racePreset"], form_state["customRace"])
    male_identity_score, male_identity_hard_fail = _couples_male_identity_score(batch, form_state, form_state["styleMode"], seed)
    score += male_identity_score
    if male_identity_hard_fail:
        hard_fail = True
    score += _body_score(batch, form_state["bodyMixPreset"])
    score += _anti_repeat_score(batch, form_state["antiRepeat"])
    score += _exact_theme_batch_score(batch, form_state["exactTheme"], form_state["locationStrategy"])
    if form_state["mode"] == "women":
        score += _women_scene_family_batch_score(batch, form_state["womenSceneFamily"])
    effective_outfit_reveal = form_runtime_controls._effective_outfit_reveal(form_state, spicy_level)
    effective_makeup_control = form_runtime_controls._effective_makeup_control(form_state, spicy_level)
    for index, candidate in enumerate(batch):
        score += _style_score(candidate, form_state["styleMode"])
        score += _photo_treatment_candidate_score(candidate, form_state["styleMode"], form_state["mode"])
        score += _scene_focus_score(candidate, form_state["sceneFocus"])
        if form_state["mode"] == "women":
            score += _women_scene_family_score(candidate, form_state["womenSceneFamily"])
        score += _vibe_score(candidate, form_state["styleVibe"])
        score += _framing_score(candidate, form_state["poseFramingControl"])
        score += _lighting_score(candidate, form_state["lightingControl"])
        score += _spicy_score(candidate, spicy_level)
        score += _mode_specific_spicy_score(candidate, form_state["mode"], form_state["styleMode"], spicy_level)
        score += _exact_theme_score(candidate, form_state["exactTheme"], form_state["locationStrategy"])
        score += _character_constraint_score(candidate, form_state["characterConstraint"])
        if female_custom_appearance:
            appearance_prompt = _female_appearance_prompt(form_state)
            score += _appearance_text_score(candidate, appearance_prompt)
            score += _appearance_profile_score(candidate, appearance_prompt)
        else:
            score += _outfit_reveal_score(candidate, effective_outfit_reveal)
            score += _hair_atom_score(candidate, form_state)
            score += _makeup_atom_score(candidate, effective_makeup_control)
            score += _eye_color_score(candidate, form_state["eyeColorControl"])
            score += _breast_size_score(candidate, form_state["breastSizeControl"])
        score += _validation_penalty(len(findings_by_index[index]), form_state["validationMode"])
        if spicy_level <= 3 and candidate.get("pose_family_id") in LOW_SPICY_UNSAFE_POSE_IDS:
            score -= 28
        if spicy_level <= 3 and candidate.get("hand_action_id") in low_spicy_unsafe_hand_ids:
            score -= 10
    if effective_outfit_reveal == "reserved":
        reserved_outfit_counts = Counter(candidate.get("outfit_family_id") for candidate in batch if candidate.get("outfit_family_id"))
        score -= sum(count - 1 for count in reserved_outfit_counts.values() if count > 1) * 8
    if form_state["mode"] == "women":
        score += _women_high_spicy_pose_mix_score(batch, spicy_level)
        if form_state["styleMode"] == "random":
            score += _women_random_outfit_color_diversity_score(batch)
            score += _women_random_pose_mix_score(batch)
    if form_state.get("personMode") == "same_person":
        score += _same_person_visual_diversity_score(batch)
    if form_state["mode"] == "couples":
        couple_color_counts = Counter(candidate.get("color_story_id") for candidate in batch if candidate.get("color_story_id"))
        score -= sum(count - 2 for count in couple_color_counts.values() if count > 2) * 10
        for candidate in batch:
            if candidate.get("outfit_family_id") in {"swimsuit", "bikini_set"} and candidate.get("scene_family_id") not in {"coastal_pool", "coastal_boardwalk"} and form_state["styleMode"] not in {"coastal", "vacation"}:
                score -= 52
            if candidate.get("outfit_family_id") == "latex_editorial" and form_state["styleMode"] not in {"nightlife", "studio", "fantasy", "cosplay"}:
                score -= 44
            if form_state["styleMode"] == "random" and candidate.get("outfit_family_id") in {"swimsuit", "bikini_set"}:
                score -= 48
            if form_state["styleMode"] == "lifestyle" and candidate.get("outfit_family_id") in {"swimsuit", "bikini_set", "crop_top_mini_skirt", "latex_editorial", "corset_trousers"}:
                score -= 36
            if form_state["styleMode"] == "lifestyle" and candidate.get("color_story_id") in {"black_gold", "oxblood_noir", "emerald_noir", "hot_pink"}:
                score -= 14
        if form_state["styleMode"] == "random":
            random_mini_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") == "mini_dress")
            random_clean_neutral_count = sum(1 for candidate in batch if candidate.get("color_story_id") == "clean_neutrals")
            if random_mini_count > 4:
                score -= (random_mini_count - 4) * 8
            if random_clean_neutral_count > 5:
                score -= (random_clean_neutral_count - 5) * 8
        if form_state["styleMode"] == "lifestyle":
            lifestyle_mini_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") == "mini_dress")
            lifestyle_clean_neutral_count = sum(1 for candidate in batch if candidate.get("color_story_id") == "clean_neutrals")
            if lifestyle_mini_count > 3:
                score -= (lifestyle_mini_count - 3) * 10
            if lifestyle_clean_neutral_count > 5:
                score -= (lifestyle_clean_neutral_count - 5) * 10
        if form_state["styleMode"] == "luxury":
            luxury_mini_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") == "mini_dress")
            luxury_clean_neutral_count = sum(1 for candidate in batch if candidate.get("color_story_id") == "clean_neutrals")
            if luxury_mini_count > 4:
                score -= (luxury_mini_count - 4) * 8
            if luxury_clean_neutral_count > 4:
                score -= (luxury_clean_neutral_count - 4) * 10
    if form_state["styleMode"] == "nightlife":
        nightlife_outfit_counts = Counter(candidate.get("outfit_family_id") for candidate in batch if candidate.get("outfit_family_id"))
        score -= sum(count - 1 for count in nightlife_outfit_counts.values() if count > 1) * 10
        mini_dress_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") == "mini_dress")
        crop_top_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") == "crop_top_mini_skirt")
        vinyl_count = sum(1 for candidate in batch if candidate.get("material_id") == "vinyl_latex")
        mini_dress_cap = 3 if form_state["mode"] == "women" else 4
        if mini_dress_count > mini_dress_cap:
            score -= (mini_dress_count - mini_dress_cap) * (12 if form_state["mode"] == "women" else 8)
        if crop_top_count > 3:
            score -= (crop_top_count - 3) * 12
        latex_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") == "latex_editorial")
        if latex_count > 1:
            score -= (latex_count - 1) * 14
        if vinyl_count:
            score -= vinyl_count * 16
    if form_state["styleMode"] == "random":
        random_swimwear_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") in {"swimsuit", "bikini_set"})
        random_latex_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") == "latex_editorial")
        random_crop_top_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") == "crop_top_mini_skirt")
        random_mini_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") == "mini_dress")
        random_outfit_counts = Counter(candidate.get("outfit_family_id") for candidate in batch if candidate.get("outfit_family_id"))
        random_color_story_counts = Counter(candidate.get("color_story_id") for candidate in batch if candidate.get("color_story_id"))
        random_clean_neutral_count = sum(1 for candidate in batch if candidate.get("color_story_id") == "clean_neutrals")
        if random_swimwear_count > 2:
            score -= (random_swimwear_count - 2) * 20
        if random_latex_count:
            score -= random_latex_count * 24
        if random_crop_top_count > 2:
            score -= (random_crop_top_count - 2) * 14
        if form_state["mode"] == "women" and random_mini_count > 3:
            score -= (random_mini_count - 3) * 12
        score -= sum(count - 3 for count in random_outfit_counts.values() if count > 3) * 8
        if form_state["mode"] in {"women", "couples"}:
            score -= sum(count - 1 for count in random_color_story_counts.values() if count > 1) * 4
        if form_state["mode"] == "women" and random_clean_neutral_count > 4:
            score -= (random_clean_neutral_count - 4) * 10
        score += _random_light_scene_balance_score(batch)
    if form_state["styleMode"] == "lifestyle":
        lifestyle_revealing_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") in {"swimsuit", "bikini_set", "crop_top_mini_skirt", "latex_editorial", "corset_trousers"})
        if lifestyle_revealing_count:
            score -= lifestyle_revealing_count * 22
        lifestyle_night_colors = sum(1 for candidate in batch if candidate.get("color_story_id") in {"black_gold", "oxblood_noir", "emerald_noir", "hot_pink"})
        if lifestyle_night_colors > 4:
            score -= (lifestyle_night_colors - 4) * 10
    if form_state["styleMode"] == "romantic" and form_state["mode"] == "women":
        romantic_revealing_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") in {"swimsuit", "bikini_set", "crop_top_mini_skirt", "latex_editorial"})
        romantic_mini_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") == "mini_dress")
        cardigan_skirt_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") == "cardigan_skirt")
        romantic_pool_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") in {"cami_midi_skirt", "wrap_blouse_skirt", "column_dress", "halter_trousers", "silk_blouse_midi_skirt", "structured_day_dress", "mockneck_knit_skirt"})
        if romantic_revealing_count:
            score -= romantic_revealing_count * 24
        if romantic_mini_count > 2:
            score -= (romantic_mini_count - 2) * 16
        if cardigan_skirt_count:
            score -= cardigan_skirt_count * 18
        if romantic_pool_count < 5:
            score -= (5 - romantic_pool_count) * 8
    if form_state["styleMode"] == "creative_artistic" and form_state["mode"] == "women":
        creative_editorial_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") in {"vest_trousers", "column_dress", "wrap_blouse_skirt", "halter_trousers", "blazer_mini_dress"})
        creative_sporty_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") in {"polo_pleated_skirt", "workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"})
        if creative_editorial_count < 5:
            score -= (5 - creative_editorial_count) * 8
        if creative_sporty_count:
            score -= creative_sporty_count * 14
    if form_state["styleMode"] == "luxury":
        luxury_revealing_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") in {"swimsuit", "bikini_set", "latex_editorial"})
        luxury_outfit_counts = Counter(candidate.get("outfit_family_id") for candidate in batch if candidate.get("outfit_family_id"))
        luxury_mini_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") == "mini_dress")
        luxury_clean_neutral_count = sum(1 for candidate in batch if candidate.get("color_story_id") == "clean_neutrals")
        if luxury_revealing_count:
            score -= luxury_revealing_count * 24
        if form_state["mode"] == "women":
            if luxury_mini_count > 2:
                score -= (luxury_mini_count - 2) * 18
            score -= sum(count - 2 for count in luxury_outfit_counts.values() if count > 2) * 10
            if luxury_clean_neutral_count > 3:
                score -= (luxury_clean_neutral_count - 3) * 14
    if form_state["styleMode"] in {"sport", "fitness"} and spicy_level <= 3:
        sporty_outfit_counts = Counter(candidate.get("outfit_family_id") for candidate in batch if candidate.get("outfit_family_id"))
        score -= sum(count - 1 for count in sporty_outfit_counts.values() if count > 1) * 12
        sporty_combo_counts = Counter((candidate.get("outfit_family_id"), candidate.get("material_id"), candidate.get("color_story_id")) for candidate in batch)
        score -= sum(count - 1 for count in sporty_combo_counts.values() if count > 1) * 36
    if form_state["styleMode"] == "fitness":
        fitness_crop_top_count = sum(1 for candidate in batch if candidate.get("outfit_family_id") == "crop_top_mini_skirt")
        fitness_lime_pop_count = sum(1 for candidate in batch if candidate.get("color_story_id") == "lime_pop")
        fitness_clean_neutral_count = sum(1 for candidate in batch if candidate.get("color_story_id") == "clean_neutrals")
        fitness_wellness_count = sum(1 for candidate in batch if candidate.get("scene_family_id") == "wellness_spa")
        fitness_unique_settings = len({candidate.get("setting_scene_id") for candidate in batch if candidate.get("setting_scene_id")})
        fitness_outfit_counts = Counter(candidate.get("outfit_family_id") for candidate in batch if candidate.get("outfit_family_id"))
        if fitness_crop_top_count:
            score -= fitness_crop_top_count * 28
        if fitness_lime_pop_count > 4:
            score -= (fitness_lime_pop_count - 4) * 10
        if fitness_clean_neutral_count > 6:
            score -= (fitness_clean_neutral_count - 6) * 6
        if fitness_wellness_count < 4:
            score -= (4 - fitness_wellness_count) * 8
        if fitness_unique_settings < 4:
            score -= (4 - fitness_unique_settings) * 12
        score -= sum(count - 6 for count in fitness_outfit_counts.values() if count > 6) * 10
    score += _muted_color_clone_penalty(batch, form_state["styleMode"], form_state["mode"])
    score += _outfit_silhouette_clone_penalty(batch, form_state["styleMode"], form_state["mode"])
    score += _scene_outfit_clone_penalty(batch, form_state["styleMode"], form_state["mode"])
    score += _treatment_outfit_clone_penalty(batch, form_state["styleMode"], form_state["mode"])
    score += _cheap_contract_fallback_penalty(batch, form_state["styleMode"], form_state["mode"])
    score += _scene_family_clone_penalty(batch, form_state["styleMode"], form_state["mode"])
    score += _location_motif_clone_penalty(batch, form_state["styleMode"], form_state["locationStrategy"])
    if form_state["validationMode"] == "strict" and any(findings_by_index.values()):
        hard_fail = True
    if form_state["styleMode"] in {"sport", "fitness"} and not any(candidate["route"] == "sports_flirt" for candidate in batch):
        if form_state["styleMode"] == "sport":
            score -= 40
        else:
            if not any(candidate["route"] in {"sports_flirt", "luxury_interior"} for candidate in batch):
                score -= 40
    if form_state["styleMode"] == "nightlife" and not any(candidate["scene_family_id"] in {"nightlife_bar", "nightlife_neon"} for candidate in batch):
        score -= 40
    score += _photo_treatment_batch_score(batch, form_state["styleMode"], form_state["mode"])
    if form_state["mode"] == "men" and form_state["styleMode"] == "romantic":
        clean_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") == "clean_commercial")
        clean_cap = max(5, len(batch) // 4)
        if clean_count > clean_cap:
            score -= (clean_count - clean_cap) * 10
    score += _close_up_angle_diversity_score(batch)
    return score, hard_fail
