from __future__ import annotations

import random
from collections import Counter
from typing import Any

from backend.character_constraints import build_character_constraint_segment, normalize_character_constraint
from backend.engine import generator
from backend.forms.normalizer import _female_appearance_prompt, _female_custom_appearance_active
from backend.services.photo_treatment_lookup import _photo_treatment_lookup
from backend.services.scoring import LOW_SPICY_UNSAFE_POSE_IDS

_BRIGHT_COLOR_ORDER = [
    "coral_ivory",
    "tangerine_cream",
    "red_ivory",
    "cobalt_white",
    "aqua_white",
    "butter_denim",
    "teal_cream",
    "olive_sand",
    "sage_stone",
    "mint_cream",
    "lilac_smoke",
    "plum_blush",
    "terracotta_sand",
]

_DARK_COLOR_ORDER = [
    "black_gold",
    "black_ivory",
    "slate_blue_ink",
    "emerald_noir",
    "oxblood_noir",
]

_SOFT_COLOR_ORDER = [
    "clean_neutrals",
    "powder_blue",
    "earthy_soft",
    "navy_cream",
    "winter_neutrals",
    "champagne_taupe",
    "rosewood_smoke",
    "soft_camel_cream",
    "dusty_rose_taupe",
    "chocolate_cream",
]

_SOFT_REPEAT_COLOR_STORY_IDS = {"black_ivory", "sport_clean_white"}
_ACTIVE_HEADBAND_LONG_HAIR_IDS = {"soft_waves", "side_braid", "long_straight", "soft_half_up"}


def _color_order_for_style(style_mode: str, spicy_level: int) -> list[str]:
    if style_mode == "nightlife":
        return _DARK_COLOR_ORDER + ["coral_ivory", "red_ivory", "teal_cream", "plum_blush", "cobalt_white"]
    if style_mode in {"luxury", "old_money"}:
        return ["black_ivory", "sage_stone", "teal_cream", "terracotta_sand", "olive_sand"] + _SOFT_COLOR_ORDER + ["black_gold", "plum_blush"]
    if style_mode == "romantic":
        return ["coral_ivory", "plum_blush", "lilac_smoke", "mint_cream", "powder_blue", "aqua_white"] + _SOFT_COLOR_ORDER + ["teal_cream"]
    if style_mode in {"lifestyle", "urban_day", "cultural_bookish"}:
        return ["butter_denim", "teal_cream", "olive_sand", "sage_stone", "mint_cream", "terracotta_sand", "cobalt_white"] + _SOFT_COLOR_ORDER + ["black_ivory"]
    if style_mode == "creative_artistic":
        return ["teal_cream", "plum_blush", "cobalt_white", "coral_ivory", "terracotta_sand"] + _DARK_COLOR_ORDER + _SOFT_COLOR_ORDER
    if style_mode in {"sport", "fitness"}:
        return [
            "sport_clean_white",
            "black_ivory",
            "red_ivory",
            "coral_ivory",
            "sage_stone",
            "olive_sand",
            "terracotta_sand",
            "mint_cream",
            "plum_blush",
            "lilac_smoke",
            "tangerine_cream",
            "butter_denim",
            "cobalt_white",
            "aqua_white",
            "teal_cream",
        ]
    if style_mode in {"coastal", "vacation"}:
        return ["aqua_white", "cobalt_white", "coral_ivory", "butter_denim", "mint_cream", "teal_cream", "terracotta_sand", "black_ivory"] + _SOFT_COLOR_ORDER
    if spicy_level <= 3:
        return ["butter_denim", "teal_cream", "olive_sand", "sage_stone", "mint_cream", "cobalt_white", "black_ivory"] + _SOFT_COLOR_ORDER
    return _BRIGHT_COLOR_ORDER + _DARK_COLOR_ORDER + _SOFT_COLOR_ORDER


def _color_repeat_cap(style_mode: str, color_id: str | None) -> int:
    if color_id in _SOFT_REPEAT_COLOR_STORY_IDS:
        return 2
    if style_mode == "random":
        return 1
    return 2


def _apply_treatment_profile(candidate: dict[str, Any], chosen_profile: dict[str, Any]) -> dict[str, Any]:
    remapped = dict(candidate)
    remapped["photo_treatment_id"] = chosen_profile["id"]
    remapped["photo_treatment"] = chosen_profile.get("label", chosen_profile["id"])
    remapped["photo_treatment_category"] = chosen_profile.get("category", "stylized")
    remapped["capture_style_render"] = chosen_profile.get("capture_render", remapped.get("capture_style_render", remapped.get("capture_style", "photo")))
    remapped["lighting_render"] = chosen_profile.get("lighting_render", remapped.get("lighting_render", remapped.get("lighting_family", "")))
    remapped["camera_vibe"] = chosen_profile.get("camera_vibe", "")
    remapped["color_grade"] = chosen_profile.get("color_grade", "")
    remapped["finish_render"] = chosen_profile.get("finish", remapped.get("finish_render", "natural skin texture"))
    return remapped


def _remap_treatment_by_preferences(candidate: dict[str, Any], preferred_ids: list[str], style_mode: str) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    lookup = _photo_treatment_lookup()
    chosen_profile: dict[str, Any] | None = None
    for treatment_id in preferred_ids:
        profile = lookup.get(treatment_id)
        if not profile:
            continue
        allowed_scenes = {str(value) for value in profile.get("allowed_scene_families", [])}
        banned_scenes = {str(value) for value in profile.get("banned_scene_families", [])}
        allowed_styles = {str(value) for value in profile.get("allowed_style_modes", [])}
        banned_styles = {str(value) for value in profile.get("banned_style_modes", [])}
        if allowed_scenes and scene_family not in allowed_scenes:
            continue
        if scene_family in banned_scenes:
            continue
        if allowed_styles and style_mode not in allowed_styles:
            continue
        if style_mode in banned_styles:
            continue
        chosen_profile = profile
        break
    if not chosen_profile:
        return candidate
    return _apply_treatment_profile(candidate, chosen_profile)


def _remap_couples_random_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "random"
    remap_seed = "|".join(str(candidate.get(key, "") or "") for key in ("scene_family_id", "setting_scene_id", "camera_framing_id", "outfit_family_id", "color_story_id", "age_band"))
    if random.Random(remap_seed).random() > 0.58:
        return candidate
    if scene_family in {"nightlife_bar", "nightlife_neon"}:
        preferred_ids = ["vintage_flash_photo", "direct_flash_night", "cinematic_poster_realism", "documentary_still"]
    elif scene_family in {"residential_luxury", "hospitality_suite", "grooming_bath"}:
        preferred_ids = ["casual_indoor_selfie", "mirror_selfie", "candid_phone_snapshot", "analog_35mm"]
    elif scene_family in {"studio", "creative_gallery"}:
        preferred_ids = ["concept_photo_editorial", "direct_light_editorial", "advertising_poster_realism", "documentary_still"]
    else:
        preferred_ids = ["candid_phone_snapshot", "disposable_camera", "documentary_still", "analog_35mm", "direct_light_editorial"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_women_fitness_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "fitness"
    if scene_family == "wellness_spa":
        preferred_ids = ["candid_phone_snapshot", "analog_35mm", "documentary_still"]
    else:
        preferred_ids = ["candid_phone_snapshot", "analog_35mm", "direct_light_editorial", "documentary_still"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_women_fitness_balanced_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "fitness"
    if scene_family == "wellness_spa":
        preferred_ids = [
            "clean_commercial",
            "direct_light_editorial",
            "advertising_poster_realism",
            "concept_photo_editorial",
        ]
    else:
        preferred_ids = [
            "direct_light_editorial",
            "clean_commercial",
            "advertising_poster_realism",
            "concept_photo_editorial",
            "cinematic_poster_realism",
        ]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_women_lifestyle_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "lifestyle"
    remap_seed = "|".join(str(candidate.get(key, "") or "") for key in ("scene_family_id", "setting_scene_id", "camera_framing_id", "outfit_family_id", "color_story_id", "age_band"))
    if random.Random(remap_seed).random() > 0.68:
        return candidate
    if scene_family in {"culture_bookish", "garden_conservatory"}:
        preferred_ids = ["analog_35mm", "documentary_still", "casual_indoor_selfie", "candid_phone_snapshot"]
    elif scene_family in {"urban_daylight", "courtyard_garden"}:
        preferred_ids = ["candid_phone_snapshot", "disposable_camera", "analog_35mm", "direct_light_editorial"]
    else:
        preferred_ids = ["candid_phone_snapshot", "analog_35mm", "documentary_still", "casual_indoor_selfie"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_women_random_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "random"
    remap_seed = "|".join(str(candidate.get(key, "") or "") for key in ("scene_family_id", "setting_scene_id", "camera_framing_id", "outfit_family_id", "color_story_id", "age_band"))
    if random.Random(remap_seed).random() > 0.28:
        return candidate
    if scene_family in {"nightlife_bar", "nightlife_neon"}:
        preferred_ids = ["cinematic_poster_realism", "direct_flash_night", "concept_photo_editorial", "vintage_flash_photo"]
    elif scene_family in {"residential_luxury", "hospitality_suite", "grooming_bath"}:
        preferred_ids = ["direct_light_editorial", "cinematic_poster_realism", "concept_photo_editorial", "analog_35mm"]
    elif scene_family in {"creative_gallery", "studio"}:
        preferred_ids = ["concept_photo_editorial", "direct_light_editorial", "advertising_poster_realism", "studio_seamless"]
    elif scene_family in {"urban_daylight", "courtyard_garden", "coastal_boardwalk", "wellness_spa"}:
        preferred_ids = ["direct_light_editorial", "analog_35mm", "cinematic_poster_realism", "advertising_poster_realism"]
    else:
        preferred_ids = ["direct_light_editorial", "cinematic_poster_realism", "analog_35mm", "concept_photo_editorial"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_women_balanced_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "random"
    if scene_family in {"culture_bookish", "garden_conservatory", "courtyard_garden"}:
        preferred_ids = ["concept_photo_editorial", "clean_commercial", "direct_light_editorial", "cinematic_poster_realism"]
    elif scene_family in {"residential_luxury", "hospitality_suite", "grooming_bath"}:
        preferred_ids = ["clean_commercial", "direct_light_editorial", "concept_photo_editorial", "cinematic_poster_realism", "advertising_poster_realism"]
    elif scene_family in {"urban_daylight", "coastal_boardwalk", "wellness_spa"}:
        preferred_ids = ["direct_light_editorial", "clean_commercial", "advertising_poster_realism", "concept_photo_editorial"]
    else:
        preferred_ids = ["clean_commercial", "direct_light_editorial", "concept_photo_editorial", "advertising_poster_realism"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_women_romantic_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "romantic"
    remap_seed = "|".join(str(candidate.get(key, "") or "") for key in ("scene_family_id", "setting_scene_id", "camera_framing_id", "outfit_family_id", "color_story_id", "age_band"))
    if random.Random(remap_seed).random() > 0.90:
        return candidate
    if scene_family in {"garden_conservatory", "courtyard_garden"}:
        preferred_ids = ["analog_35mm", "cinematic_poster_realism", "direct_light_editorial", "concept_photo_editorial"]
    elif scene_family == "coastal_pool":
        preferred_ids = ["analog_35mm", "direct_light_editorial", "cinematic_poster_realism", "advertising_poster_realism"]
    else:
        preferred_ids = ["analog_35mm", "cinematic_poster_realism", "direct_light_editorial", "concept_photo_editorial"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_women_nightlife_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "nightlife"
    remap_seed = "|".join(str(candidate.get(key, "") or "") for key in ("scene_family_id", "setting_scene_id", "camera_framing_id", "outfit_family_id", "color_story_id", "age_band"))
    if random.Random(remap_seed).random() > 0.86:
        return candidate
    if scene_family in {"nightlife_bar", "nightlife_neon"}:
        preferred_ids = ["vintage_flash_photo", "direct_flash_night", "cinematic_poster_realism", "low_key_dramatic", "disposable_camera"]
    else:
        preferred_ids = ["vintage_flash_photo", "cinematic_poster_realism", "low_key_dramatic", "documentary_still"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_women_luxury_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "luxury"
    remap_seed = "|".join(str(candidate.get(key, "") or "") for key in ("scene_family_id", "setting_scene_id", "camera_framing_id", "outfit_family_id", "color_story_id", "age_band"))
    if random.Random(remap_seed).random() > 0.80:
        return candidate
    if scene_family == "grooming_bath":
        preferred_ids = ["direct_light_editorial", "cinematic_poster_realism", "concept_photo_editorial", "analog_35mm"]
    elif scene_family in {"residential_luxury", "hospitality_suite"}:
        preferred_ids = ["direct_light_editorial", "cinematic_poster_realism", "concept_photo_editorial", "analog_35mm", "low_key_dramatic"]
    else:
        preferred_ids = ["direct_light_editorial", "cinematic_poster_realism", "analog_35mm", "concept_photo_editorial"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_women_creative_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "creative_artistic"
    remap_seed = "|".join(str(candidate.get(key, "") or "") for key in ("scene_family_id", "setting_scene_id", "camera_framing_id", "outfit_family_id", "color_story_id", "age_band"))
    if random.Random(remap_seed).random() > 0.80:
        return candidate
    if scene_family in {"creative_gallery", "studio"}:
        preferred_ids = ["concept_photo_editorial", "direct_light_editorial", "advertising_poster_realism", "vintage_flash_photo", "documentary_still"]
    else:
        preferred_ids = ["direct_light_editorial", "documentary_still", "vintage_flash_photo", "analog_35mm"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_men_random_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "random"
    remap_seed = "|".join(str(candidate.get(key, "") or "") for key in ("scene_family_id", "setting_scene_id", "camera_framing_id", "outfit_family_id", "color_story_id", "age_band"))
    if random.Random(remap_seed).random() > 0.58:
        return candidate
    if scene_family in {"nightlife_bar", "nightlife_neon"}:
        preferred_ids = ["vintage_flash_photo", "direct_flash_night", "candid_phone_snapshot", "cinematic_poster_realism"]
    elif scene_family in {"residential_luxury", "hospitality_suite", "grooming_bath"}:
        preferred_ids = ["casual_indoor_selfie", "mirror_selfie", "direct_light_editorial", "analog_35mm"]
    elif scene_family in {"creative_gallery", "studio"}:
        preferred_ids = ["concept_photo_editorial", "direct_light_editorial", "advertising_poster_realism", "documentary_still"]
    else:
        preferred_ids = ["candid_phone_snapshot", "analog_35mm", "documentary_still", "direct_light_editorial"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_men_nightlife_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "nightlife"
    remap_seed = "|".join(str(candidate.get(key, "") or "") for key in ("scene_family_id", "setting_scene_id", "camera_framing_id", "outfit_family_id", "color_story_id", "age_band"))
    if random.Random(remap_seed).random() > 0.62:
        return candidate
    if scene_family in {"nightlife_bar", "nightlife_neon"}:
        preferred_ids = ["vintage_flash_photo", "direct_flash_night", "candid_phone_snapshot", "disposable_camera", "cinematic_poster_realism", "low_key_dramatic"]
    else:
        preferred_ids = ["candid_phone_snapshot", "vintage_flash_photo", "cinematic_poster_realism", "low_key_dramatic"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_men_romantic_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "romantic"
    remap_seed = "|".join(str(candidate.get(key, "") or "") for key in ("scene_family_id", "setting_scene_id", "camera_framing_id", "color_story_id", "lighting_family_id"))
    if random.Random(remap_seed).random() > 0.78:
        return candidate
    if scene_family in {"garden_conservatory", "courtyard_garden"}:
        preferred_ids = ["analog_35mm", "documentary_still", "candid_phone_snapshot", "direct_light_editorial", "low_key_dramatic"]
    elif scene_family in {"residential_luxury", "hospitality_suite"}:
        preferred_ids = ["casual_indoor_selfie", "analog_35mm", "direct_light_editorial", "documentary_still", "low_key_dramatic"]
    else:
        preferred_ids = ["analog_35mm", "documentary_still", "direct_light_editorial", "candid_phone_snapshot", "low_key_dramatic"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_men_luxury_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "luxury"
    remap_seed = "|".join(
        str(candidate.get(key, "") or "")
        for key in (
            "scene_family_id",
            "setting_scene_id",
            "camera_framing_id",
            "color_story_id",
            "lighting_family_id",
        )
    )
    if random.Random(remap_seed).random() > 0.76:
        return candidate
    if scene_family == "grooming_bath":
        preferred_ids = ["mirror_selfie", "direct_light_editorial", "analog_35mm", "low_key_dramatic"]
    elif scene_family in {"residential_luxury", "hospitality_suite"}:
        preferred_ids = ["direct_light_editorial", "analog_35mm", "cinematic_poster_realism", "low_key_dramatic", "direct_flash_night"]
    else:
        preferred_ids = ["direct_light_editorial", "analog_35mm", "documentary_still", "cinematic_poster_realism"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_couples_lifestyle_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "lifestyle"
    remap_seed = "|".join(str(candidate.get(key, "") or "") for key in ("scene_family_id", "setting_scene_id", "camera_framing_id", "outfit_family_id", "color_story_id", "age_band"))
    if random.Random(remap_seed).random() > 0.66:
        return candidate
    if scene_family in {"culture_bookish", "garden_conservatory"}:
        preferred_ids = ["analog_35mm", "documentary_still", "candid_phone_snapshot", "casual_indoor_selfie"]
    elif scene_family in {"urban_daylight", "courtyard_garden"}:
        preferred_ids = ["candid_phone_snapshot", "disposable_camera", "analog_35mm", "direct_light_editorial"]
    else:
        preferred_ids = ["candid_phone_snapshot", "analog_35mm", "documentary_still", "casual_indoor_selfie"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _apply_active_headband_hint(candidate: dict[str, Any], form_state: dict[str, Any]) -> dict[str, Any]:
    if form_state.get("mode") != "women":
        return candidate
    if form_state.get("styleMode") not in {"sport", "fitness"}:
        return candidate
    hair_id = str(candidate.get("hair_structure_id", "") or "")
    if hair_id not in _ACTIVE_HEADBAND_LONG_HAIR_IDS:
        return candidate

    hair_text = str(candidate.get("hair_structure_override") or candidate.get("hair_structure") or "").strip()
    if not hair_text or "headband" in hair_text.lower() or "hairband" in hair_text.lower():
        return candidate

    headband_seed = "|".join(
        str(candidate.get(key, "") or "")
        for key in ("scene_family_id", "outfit_family_id", "color_story_id", "hair_structure_id")
    )
    if sum(ord(char) for char in headband_seed) % 100 >= 18:
        return candidate

    remapped = dict(candidate)
    remapped["hair_structure_override"] = f"{hair_text} held back with a slim athletic headband"
    return remapped


def _apply_prompt_constraints(candidate: dict[str, Any], form_state: dict[str, Any], spicy_level: int) -> dict[str, Any]:
    constrained = dict(candidate)
    constrained["person_mode"] = form_state.get("personMode", "different_persons")
    female_custom_appearance = _female_custom_appearance_active(form_state)
    photo_type_control = str(form_state.get("photoTypeControl", "balanced") or "balanced")
    photo_type_override_active = photo_type_control not in {"balanced", "custom"}
    if not photo_type_override_active:
        if form_state.get("mode") == "couples" and form_state.get("styleMode") == "lifestyle" and constrained.get("photo_treatment_id") == "clean_commercial":
            constrained = _remap_couples_lifestyle_treatment(constrained)
        if form_state.get("mode") == "men" and form_state.get("styleMode") == "random" and constrained.get("photo_treatment_id") == "clean_commercial":
            constrained = _remap_men_random_treatment(constrained)
        if form_state.get("mode") == "men" and form_state.get("styleMode") == "nightlife" and constrained.get("photo_treatment_id") == "clean_commercial":
            constrained = _remap_men_nightlife_treatment(constrained)
        if form_state.get("mode") == "men" and form_state.get("styleMode") == "romantic" and constrained.get("photo_treatment_id") == "clean_commercial":
            constrained = _remap_men_romantic_treatment(constrained)
        if form_state.get("mode") == "men" and form_state.get("styleMode") == "luxury" and constrained.get("photo_treatment_id") == "clean_commercial":
            constrained = _remap_men_luxury_treatment(constrained)
        if form_state.get("mode") == "women" and form_state.get("styleMode") == "random" and constrained.get("photo_treatment_id") == "clean_commercial":
            constrained = _remap_women_random_treatment(constrained)
        if form_state.get("mode") == "women" and form_state.get("styleMode") == "lifestyle" and constrained.get("photo_treatment_id") == "clean_commercial":
            constrained = _remap_women_lifestyle_treatment(constrained)
        if form_state.get("mode") == "women" and form_state.get("styleMode") == "romantic" and constrained.get("photo_treatment_id") == "clean_commercial":
            constrained = _remap_women_romantic_treatment(constrained)
        if form_state.get("mode") == "women" and form_state.get("styleMode") == "fitness" and constrained.get("photo_treatment_id") == "clean_commercial":
            constrained = _remap_women_fitness_treatment(constrained)
        if form_state.get("mode") == "women" and form_state.get("styleMode") == "nightlife" and constrained.get("photo_treatment_id") == "clean_commercial":
            constrained = _remap_women_nightlife_treatment(constrained)
        if form_state.get("mode") == "women" and form_state.get("styleMode") == "luxury" and constrained.get("photo_treatment_id") == "clean_commercial":
            constrained = _remap_women_luxury_treatment(constrained)
        if form_state.get("mode") == "women" and form_state.get("styleMode") == "creative_artistic" and constrained.get("photo_treatment_id") == "clean_commercial":
            constrained = _remap_women_creative_treatment(constrained)
        if form_state.get("mode") == "couples" and form_state.get("styleMode") == "random" and constrained.get("photo_treatment_id") == "clean_commercial":
            constrained = _remap_couples_random_treatment(constrained)
    if photo_type_control == "balanced" and form_state.get("mode") == "women" and form_state.get("styleMode") == "random" and constrained.get("photo_treatment_id") in {"candid_phone_snapshot", "mirror_selfie", "casual_indoor_selfie", "disposable_camera", "studio_seamless", "direct_flash_night", "analog_35mm", "documentary_still", "vintage_flash_photo"}:
        constrained = _remap_women_balanced_treatment(constrained)
    if photo_type_control == "balanced" and form_state.get("mode") == "women" and form_state.get("styleMode") == "fitness" and constrained.get("photo_treatment_id") in {"candid_phone_snapshot", "mirror_selfie", "casual_indoor_selfie", "disposable_camera", "analog_35mm", "documentary_still", "vintage_flash_photo", "direct_flash_night"}:
        constrained = _remap_women_fitness_balanced_treatment(constrained)
    if form_state.get("mode") == "women" and form_state.get("styleMode") == "nightlife" and constrained.get("material_id") == "vinyl_latex":
        constrained["material_id"] = "satin"
        constrained["material"] = "satin finish"
    if spicy_level <= 3 and constrained.get("pose_family_id") in LOW_SPICY_UNSAFE_POSE_IDS:
        constrained["pose_family_id"] = "seated_sideways"
        constrained["pose_family"] = "seated sideways with both legs angled to one side"
    if spicy_level <= 3 and constrained.get("hand_action_id") in {"hand_on_thigh", "touching_strap", "hooked_waistband"}:
        constrained["hand_action_id"] = "hand_at_waist"
        constrained["hand_action"] = "one hand at her waist"
    if form_state.get("name"):
        constrained["subject_name"] = form_state["name"]
    if female_custom_appearance:
        constrained["appearance_prompt"] = _female_appearance_prompt(form_state)
    if form_state.get("racePreset") == "other" and form_state.get("customRace"):
        constrained["ethnicity_override"] = form_state["customRace"]
    if form_state.get("exactTheme"):
        constrained["exact_theme"] = form_state["exactTheme"]
    character_constraint = normalize_character_constraint(form_state.get("characterConstraint", ""))
    if character_constraint:
        constrained["character_constraint"] = character_constraint
        constrained["character_constraint_segment"] = build_character_constraint_segment(character_constraint)
    if form_state.get("personMode") == "same_person" and form_state.get("useCoreIdentityPrompt") and form_state.get("coreIdentityPrompt"):
        constrained["core_identity_prompt"] = form_state["coreIdentityPrompt"]
    if not female_custom_appearance and form_state.get("hairstyle") == "custom" and form_state.get("customHair"):
        constrained["hair_structure_override"] = form_state["customHair"]
    if not female_custom_appearance and form_state.get("hairColorControl") == "custom" and form_state.get("customHairColor"):
        constrained["hair_color_override"] = form_state["customHairColor"]
    if not female_custom_appearance and not constrained.get("hair_structure_override"):
        constrained = _apply_active_headband_hint(constrained, form_state)
    return constrained


def _diversify_women_outfit_colors(prompts: list[dict[str, Any]], form_state: dict[str, Any], spicy_level: int) -> list[dict[str, Any]]:
    if form_state["mode"] != "women" or form_state["antiRepeat"] not in {"hard", "brutal"}:
        return prompts
    style_mode = form_state["styleMode"]
    color_order = _color_order_for_style(style_mode, spicy_level)
    color_map = {item["id"]: item for item in generator.load_data_bank()["styling"]["color_stories"] if item["id"] in set(color_order)}
    allowed_colors = set(color_order)
    color_cap_by_style = {
        "random": {"clean_neutrals": 1, "navy_cream": 1, "earthy_soft": 1, "powder_blue": 1, "oxblood_noir": 1, "hot_pink": 1, "rosewood_smoke": 1, "chocolate_cream": 1},
        "lifestyle": {"clean_neutrals": 3},
        "luxury": {"clean_neutrals": 3},
        "fitness": {"sport_clean_white": 2, "cobalt_white": 1, "aqua_white": 1, "teal_cream": 1},
        "sport": {"sport_clean_white": 2, "cobalt_white": 1, "aqua_white": 1, "teal_cream": 1},
    }
    style_caps = color_cap_by_style.get(style_mode, {})
    used_combos: set[tuple[str | None, str | None, str | None]] = set()
    color_counts: Counter[str | None] = Counter()
    pattern_target = max(1, len(prompts) // 6) if style_mode == "random" else 0
    pattern_count = 0
    diversified: list[dict[str, Any]] = []
    for item in prompts:
        prompt_item = dict(item)
        candidate = dict(prompt_item["candidate"])
        combo = (candidate.get("outfit_family_id"), candidate.get("material_id"), candidate.get("color_story_id"))
        current_color_allowed = candidate.get("color_story_id") in allowed_colors
        current_color_cap = _color_repeat_cap(style_mode, candidate.get("color_story_id"))
        needs_shift = (
            combo in used_combos
            or color_counts[candidate.get("color_story_id")] >= current_color_cap
            or (
                candidate.get("color_story_id") in style_caps
                and color_counts[candidate.get("color_story_id")] >= style_caps[candidate.get("color_story_id")]
            )
            or not current_color_allowed
        )
        if needs_shift:
            for color_id in color_order:
                if color_id == candidate.get("color_story_id") or color_id not in color_map:
                    continue
                alt_combo = (candidate.get("outfit_family_id"), candidate.get("material_id"), color_id)
                if alt_combo in used_combos:
                    continue
                if current_color_allowed and color_counts[color_id] >= _color_repeat_cap(style_mode, color_id):
                    continue
                if color_id in style_caps and color_counts[color_id] >= style_caps[color_id]:
                    continue
                candidate["color_story_id"] = color_id
                candidate["color_story"] = color_map[color_id]["value"]
                combo = alt_combo
                prompt_item["candidate"] = candidate
                prompt_item["segments"] = generator.render_candidate_segments(candidate)
                prompt_item["prompt"] = generator.render_candidate_prompt(candidate)
                break
        if (
            pattern_target
            and pattern_count < pattern_target
            and not candidate.get("outfit_render_mode_override")
            and generator._pattern_friendly_outfit(str(candidate.get("outfit_family", "") or ""), set(candidate.get("outfit_tags", []) or []))
        ):
            candidate["outfit_render_mode_override"] = "pattern"
            prompt_item["candidate"] = candidate
            prompt_item["segments"] = generator.render_candidate_segments(candidate)
            prompt_item["prompt"] = generator.render_candidate_prompt(candidate)
            pattern_count += 1
        used_combos.add(combo)
        color_counts[candidate.get("color_story_id")] += 1
        diversified.append(prompt_item)
    return diversified


def _diversify_couples_candidate_colors(scaffolds: list[dict[str, Any]], form_state: dict[str, Any], spicy_level: int) -> list[dict[str, Any]]:
    if form_state["mode"] != "couples" or form_state["antiRepeat"] not in {"hard", "brutal"}:
        return scaffolds
    style_mode = form_state["styleMode"]
    color_order = _color_order_for_style(style_mode, spicy_level)
    color_map = {item["id"]: item for item in generator.load_data_bank()["styling"]["color_stories"] if item["id"] in set(color_order)}
    allowed_colors = set(color_order)
    color_cap_by_style = {
        "random": {"clean_neutrals": 1, "navy_cream": 1, "earthy_soft": 1, "powder_blue": 1, "oxblood_noir": 1, "hot_pink": 1, "rosewood_smoke": 1, "chocolate_cream": 1},
        "lifestyle": {"clean_neutrals": 3},
        "luxury": {"clean_neutrals": 3},
        "fitness": {"sport_clean_white": 2, "cobalt_white": 1, "aqua_white": 1, "teal_cream": 1},
        "sport": {"sport_clean_white": 2, "cobalt_white": 1, "aqua_white": 1, "teal_cream": 1},
    }
    style_caps = color_cap_by_style.get(style_mode, {})
    used_combos: set[tuple[str | None, str | None, str | None]] = set()
    color_counts: Counter[str | None] = Counter()
    pattern_target = max(1, len(scaffolds) // 6) if style_mode == "random" else 0
    pattern_count = 0
    diversified: list[dict[str, Any]] = []
    for item in scaffolds:
        scaffold = dict(item)
        candidate = dict(scaffold["candidate"])
        combo = (candidate.get("outfit_family_id"), candidate.get("material_id"), candidate.get("color_story_id"))
        current_color_allowed = candidate.get("color_story_id") in allowed_colors
        current_color_cap = _color_repeat_cap(style_mode, candidate.get("color_story_id"))
        needs_shift = combo in used_combos or color_counts[candidate.get("color_story_id")] >= current_color_cap or (candidate.get("color_story_id") in style_caps and color_counts[candidate.get("color_story_id")] >= style_caps[candidate.get("color_story_id")]) or not current_color_allowed
        if needs_shift:
            for color_id in color_order:
                if color_id == candidate.get("color_story_id") or color_id not in color_map:
                    continue
                alt_combo = (candidate.get("outfit_family_id"), candidate.get("material_id"), color_id)
                if alt_combo in used_combos:
                    continue
                if current_color_allowed and color_counts[color_id] >= _color_repeat_cap(style_mode, color_id):
                    continue
                if color_id in style_caps and color_counts[color_id] >= style_caps[color_id]:
                    continue
                candidate["color_story_id"] = color_id
                candidate["color_story"] = color_map[color_id]["value"]
                combo = alt_combo
                scaffold["candidate"] = candidate
                break
        if (
            pattern_target
            and pattern_count < pattern_target
            and not candidate.get("outfit_render_mode_override")
            and generator._pattern_friendly_outfit(str(candidate.get("outfit_family", "") or ""), set(candidate.get("outfit_tags", []) or []))
        ):
            candidate["outfit_render_mode_override"] = "pattern"
            scaffold["candidate"] = candidate
            pattern_count += 1
        used_combos.add(combo)
        color_counts[candidate.get("color_story_id")] += 1
        diversified.append(scaffold)
    return diversified
