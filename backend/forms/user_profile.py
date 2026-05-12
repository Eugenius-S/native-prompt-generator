from __future__ import annotations

from typing import Any

from .constants import SCENE_FOCUS_PREFERENCES
from .normalizer import _female_custom_appearance_active, _parse_bool
from .runtime_controls import _effective_makeup_control, _effective_outfit_reveal, _exact_theme_location_keywords, _exact_theme_scene_constraints, _requested_location_domain


def _merge_preference_sets(*values: set[str]) -> set[str]:
    merged: set[str] = set()
    for value in values:
        merged |= set(value)
    return merged


FEMALE_OUTFIT_VIBE_PREFERENCES: dict[str, dict[str, set[str]]] = {
    "lifestyle": {
        "preferred_outfit_ids": {"cardigan_skirt", "cardigan_trousers", "blouse_trousers", "shirt_trousers", "sweater_jeans", "wrap_blouse_skirt", "vest_trousers"},
        "preferred_color_story_ids": {"clean_neutrals", "navy_cream", "earthy_soft", "winter_neutrals", "powder_blue"},
    },
    "luxury": {
        "preferred_outfit_ids": {"column_dress", "vest_trousers", "wrap_blouse_skirt", "blouse_trousers", "cami_midi_skirt", "cashmere_shell_trousers", "structured_day_dress"},
        "preferred_color_story_ids": {"black_gold", "champagne_taupe", "chocolate_cream", "slate_blue_ink", "rosewood_smoke"},
    },
    "old_money": {
        "preferred_outfit_ids": {"cashmere_shell_trousers", "structured_day_dress", "mockneck_knit_skirt", "cardigan_trousers", "silk_blouse_midi_skirt"},
        "preferred_color_story_ids": {"navy_cream", "champagne_taupe", "winter_neutrals", "earthy_soft"},
    },
    "romantic": {
        "preferred_outfit_ids": {"cami_midi_skirt", "wrap_blouse_skirt", "column_dress", "halter_trousers", "silk_blouse_midi_skirt"},
        "preferred_color_story_ids": {"powder_blue", "rosewood_smoke", "champagne_taupe", "earthy_soft"},
    },
    "vacation": {
        "preferred_outfit_ids": {"cami_midi_skirt", "wrap_blouse_skirt", "column_dress", "halter_trousers", "mini_dress"},
        "preferred_color_story_ids": {"powder_blue", "earthy_soft", "clean_neutrals", "hot_pink"},
    },
    "sport": {
        "preferred_outfit_ids": {"crop_top_mini_skirt", "polo_pleated_skirt", "workout_top_leggings"},
        "preferred_material_ids": {"athletic_jersey", "crisp_cotton"},
    },
    "fitness": {
        "preferred_outfit_ids": {"polo_pleated_skirt", "workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"},
        "preferred_material_ids": {"athletic_jersey", "crisp_cotton"},
    },
    "nightlife": {
        "preferred_outfit_ids": {"blazer_mini_dress", "cami_midi_skirt", "column_dress", "halter_trousers", "corset_trousers"},
        "preferred_color_story_ids": {"black_gold", "oxblood_noir", "emerald_noir", "hot_pink"},
        "banned_outfit_ids": {"cardigan_skirt", "cardigan_trousers", "shirt_trousers", "sweater_jeans"},
    },
    "cultural_bookish": {
        "preferred_outfit_ids": {"cardigan_skirt", "cardigan_trousers", "shirt_trousers", "blouse_trousers", "silk_blouse_midi_skirt", "mockneck_knit_skirt"},
        "preferred_color_story_ids": {"navy_cream", "earthy_soft", "winter_neutrals", "powder_blue"},
        "banned_outfit_ids": {"mini_dress", "blazer_mini_dress", "bodysuit_trousers", "crop_top_mini_skirt"},
    },
    "creative_artistic": {
        "preferred_outfit_ids": {"vest_trousers", "column_dress", "wrap_blouse_skirt", "halter_trousers", "blazer_mini_dress"},
        "preferred_color_story_ids": {"slate_blue_ink", "rosewood_smoke", "black_gold", "emerald_noir"},
    },
    "urban_day": {
        "preferred_outfit_ids": {"shirt_trousers", "blouse_trousers", "vest_trousers", "structured_day_dress", "sweater_jeans"},
        "preferred_color_story_ids": {"clean_neutrals", "navy_cream", "powder_blue", "earthy_soft"},
    },
    "coastal": {
        "preferred_outfit_ids": {"cami_midi_skirt", "wrap_blouse_skirt", "column_dress", "halter_trousers"},
        "preferred_color_story_ids": {"powder_blue", "clean_neutrals", "earthy_soft", "hot_pink"},
    },
    "studio": {
        "preferred_outfit_ids": {"column_dress", "blazer_mini_dress", "vest_trousers", "halter_trousers", "bodysuit_trousers"},
        "preferred_color_story_ids": {"black_gold", "oxblood_noir", "clean_neutrals", "slate_blue_ink"},
    },
    "cosplay": {
        "preferred_outfit_ids": {"blazer_mini_dress", "bodysuit_trousers", "column_dress"},
    },
    "fantasy": {
        "preferred_outfit_ids": {"column_dress", "halter_trousers", "blazer_mini_dress"},
    },
}

FEMALE_BEAUTY_FINISH_PREFERENCES: dict[str, dict[str, set[str]]] = {
    "fresh_natural": {
        "preferred_makeup_ids": {"fresh_barely_there", "clean_minimal", "groomed_daylight_soft", "natural_pretty"},
        "preferred_photo_treatment_ids": {"candid_phone_snapshot", "analog_35mm", "documentary_still", "casual_indoor_selfie"},
    },
    "polished_soft": {
        "preferred_makeup_ids": {"natural_pretty", "rosy_polished_minimal", "soft_glam_clean"},
        "preferred_photo_treatment_ids": {"clean_commercial", "analog_35mm", "direct_light_editorial", "advertising_poster_realism"},
    },
    "glossy_glam": {
        "preferred_makeup_ids": {"soft_glam_clean", "glossy_soft_glam", "night_out_glam"},
        "preferred_photo_treatment_ids": {"clean_commercial", "advertising_poster_realism", "direct_light_editorial", "studio_seamless"},
    },
    "after_dark": {
        "preferred_makeup_ids": {"glossy_soft_glam", "night_out_glam"},
        "preferred_photo_treatment_ids": {"vintage_flash_photo", "direct_flash_night", "low_key_dramatic", "cinematic_poster_realism"},
    },
}

FRAMING_CONTROL_PREFERENCES: dict[str, dict[str, Any]] = {
    "more_portraits": {
        "preferred_framing_ids": {
            "waist_up",
            "bust_up",
            "close_portrait",
            "head_and_shoulders",
            "below_chest_portrait",
        },
        "framing_group_target_share": {
            "portrait": 1.00,
            "mid": 0.00,
            "full": 0.00,
        },
    },
    "more_full_body": {
        "preferred_framing_ids": {"full_body", "ankle_up"},
        "preferred_pose_tags": {"standing"},
        "framing_group_target_share": {
            "portrait": 0.00,
            "mid": 0.00,
            "full": 1.00,
        },
    },
    "medium_shots": {
        "preferred_framing_ids": {"knee_up", "cowboy_shot"},
        "framing_group_target_share": {
            "portrait": 0.00,
            "mid": 1.00,
            "full": 0.00,
        },
    },
}


PHOTO_TYPE_PREFERENCES: dict[str, dict[str, set[str]]] = {
    "balanced": {
        "preferred_photo_treatment_ids": {
            "direct_light_editorial",
            "concept_photo_editorial",
            "cinematic_poster_realism",
            "advertising_poster_realism",
        },
        "deprioritized_photo_treatment_ids": {
            "candid_phone_snapshot",
            "mirror_selfie",
            "casual_indoor_selfie",
            "analog_35mm",
            "documentary_still",
            "vintage_flash_photo",
            "disposable_camera",
            "studio_seamless",
            "direct_flash_night",
        },
        "preferred_scene_families": {
            "urban_daylight",
            "residential_luxury",
            "courtyard_garden",
            "garden_conservatory",
            "coastal_pool",
            "coastal_boardwalk",
        },
        "banned_scene_families": {"studio", "nightlife_neon"},
        "preferred_capture_ids": {"lifestyle_photo", "fashion_photo"},
        "preferred_lighting_ids": {"clean_daylight", "hard_direct_light", "single_source_contrast"},
    },
    "glossy": {
        "required_photo_treatment_ids": {
            "clean_commercial",
            "direct_light_editorial",
            "concept_photo_editorial",
            "advertising_poster_realism",
            "cinematic_poster_realism",
            "low_key_dramatic",
        },
        "preferred_photo_treatment_ids": {
            "clean_commercial",
            "direct_light_editorial",
            "concept_photo_editorial",
            "advertising_poster_realism",
            "cinematic_poster_realism",
            "low_key_dramatic",
        },
        "deprioritized_photo_treatment_ids": {
            "candid_phone_snapshot",
            "mirror_selfie",
            "casual_indoor_selfie",
            "documentary_still",
            "disposable_camera",
            "studio_seamless",
        },
        "preferred_capture_ids": {"fashion_photo", "editorial_photo"},
        "preferred_lighting_ids": {"clean_daylight", "hard_direct_light", "studio_rim", "single_source_contrast", "tight_spotlight", "warm_interior"},
        "preferred_scene_families": {"urban_daylight", "residential_luxury", "hospitality_suite", "grooming_bath", "garden_conservatory", "courtyard_garden", "coastal_boardwalk"},
        "banned_scene_families": {"studio", "creative_gallery", "nightlife_neon", "wellness_spa"},
    },
    "studio": {
        "required_photo_treatment_ids": {
            "studio_seamless",
            "concept_photo_editorial",
            "advertising_poster_realism",
            "low_key_dramatic",
        },
        "preferred_photo_treatment_ids": {
            "studio_seamless",
            "concept_photo_editorial",
            "advertising_poster_realism",
            "low_key_dramatic",
        },
        "deprioritized_photo_treatment_ids": {
            "candid_phone_snapshot",
            "mirror_selfie",
            "casual_indoor_selfie",
            "documentary_still",
            "disposable_camera",
            "clean_commercial",
        },
        "required_scene_families": {"studio"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo"},
        "preferred_lighting_ids": {"studio_rim", "tight_spotlight", "single_source_contrast"},
    },
    "stylized": {
        "required_photo_treatment_ids": {
            "concept_photo_editorial",
            "cinematic_poster_realism",
            "low_key_dramatic",
            "direct_flash_night",
            "vintage_flash_photo",
            "advertising_poster_realism",
        },
        "preferred_photo_treatment_ids": {
            "concept_photo_editorial",
            "cinematic_poster_realism",
            "low_key_dramatic",
            "direct_flash_night",
            "vintage_flash_photo",
            "advertising_poster_realism",
        },
        "deprioritized_photo_treatment_ids": {
            "candid_phone_snapshot",
            "mirror_selfie",
            "casual_indoor_selfie",
            "documentary_still",
            "disposable_camera",
            "clean_commercial",
            "direct_light_editorial",
            "studio_seamless",
        },
        "preferred_scene_families": {"studio", "creative_gallery", "nightlife_neon", "residential_luxury", "hospitality_suite"},
        "banned_scene_families": {"urban_daylight", "grooming_bath", "wellness_spa", "courtyard_garden", "garden_conservatory", "coastal_boardwalk", "coastal_pool"},
    },
    "amateur": {
        "required_photo_treatment_ids": {
            "candid_phone_snapshot",
            "mirror_selfie",
            "casual_indoor_selfie",
            "disposable_camera",
            "documentary_still",
            "analog_35mm",
            "direct_light_editorial",
        },
        "preferred_photo_treatment_ids": {
            "candid_phone_snapshot",
            "mirror_selfie",
            "casual_indoor_selfie",
            "disposable_camera",
            "documentary_still",
            "analog_35mm",
        },
        "deprioritized_photo_treatment_ids": {
            "studio_seamless",
            "concept_photo_editorial",
            "advertising_poster_realism",
            "low_key_dramatic",
            "clean_commercial",
            "direct_light_editorial",
        },
        "preferred_scene_families": {
            "urban_daylight",
            "culture_bookish",
            "residential_luxury",
            "hospitality_suite",
            "grooming_bath",
            "wellness_spa",
            "coastal_pool",
            "nightlife_bar",
        },
        "banned_scene_families": {"studio", "nightlife_neon"},
        "preferred_capture_ids": {"smartphone_photo", "lifestyle_photo"},
        "preferred_lighting_ids": {"clean_daylight", "soft_overcast", "warm_interior", "practical_lamp"},
    },
    "custom": {},
}


def _merge_profile_preferences(profile: dict[str, Any], additions: dict[str, Any]) -> dict[str, Any]:
    for key, value in additions.items():
        if isinstance(value, set):
            profile[key] = _merge_preference_sets(set(profile.get(key, set())), value)
        else:
            profile[key] = value
    return profile


def _user_style_profile(form_state: dict[str, Any], spicy_level: int) -> dict[str, Any]:
    from backend.prompt_service import (
        HAIR_COLOR_PREFERENCES,
        HAIR_LENGTH_PREFERENCES,
        OUTFIT_REVEAL_PREFERENCES,
        SAME_PERSON_BODY_GROUPS,
        SAME_PERSON_ETHNICITY_IDS,
        WOMEN_BANNED_HAIR_IDS,
        WOMEN_SCENE_FAMILY_FASHION_PREFERENCES,
        _couples_different_persons_identity_constraints,
        _normalize_age_filter,
        _women_active_high_spicy_pose_ids,
    )

    profile: dict[str, Any] = {}
    female_custom_appearance = _female_custom_appearance_active(form_state)
    if form_state.get("photoTreatmentControl") and form_state["photoTreatmentControl"] != "random":
        profile["required_photo_treatment_ids"] = {form_state["photoTreatmentControl"]}
        profile["preferred_photo_treatment_ids"] = {form_state["photoTreatmentControl"]}
    elif form_state["mode"] == "men" and form_state["styleMode"] == "romantic":
        profile["preferred_photo_treatment_ids"] = {
            "analog_35mm",
            "documentary_still",
            "disposable_camera",
            "candid_phone_snapshot",
            "direct_light_editorial",
            "low_key_dramatic",
            "cinematic_poster_realism",
        }
        profile["deprioritized_photo_treatment_ids"] = {"clean_commercial"}
    elif form_state["mode"] == "couples" and form_state["styleMode"] == "random":
        profile["preferred_photo_treatment_ids"] = {
            "candid_phone_snapshot",
            "casual_indoor_selfie",
            "mirror_selfie",
            "disposable_camera",
            "analog_35mm",
            "documentary_still",
            "concept_photo_editorial",
            "direct_light_editorial",
            "cinematic_poster_realism",
            "vintage_flash_photo",
            "advertising_poster_realism",
        }
        profile["deprioritized_photo_treatment_ids"] = {"clean_commercial"}
    elif form_state["mode"] == "women" and form_state["styleMode"] == "lifestyle":
        profile["preferred_photo_treatment_ids"] = {
            "candid_phone_snapshot",
            "analog_35mm",
            "documentary_still",
            "disposable_camera",
            "casual_indoor_selfie",
            "direct_light_editorial",
        }
        profile["deprioritized_photo_treatment_ids"] = {"clean_commercial"}
    elif form_state["mode"] == "women" and form_state["styleMode"] == "random":
        profile["preferred_photo_treatment_ids"] = {
            "clean_commercial",
            "analog_35mm",
            "documentary_still",
            "direct_light_editorial",
            "concept_photo_editorial",
            "cinematic_poster_realism",
            "advertising_poster_realism",
        }
        profile["deprioritized_photo_treatment_ids"] = {"mirror_selfie", "casual_indoor_selfie"}
    elif form_state["mode"] == "women" and form_state["styleMode"] == "fitness":
        profile["preferred_photo_treatment_ids"] = {
            "candid_phone_snapshot",
            "analog_35mm",
            "documentary_still",
            "direct_light_editorial",
        }
        profile["deprioritized_photo_treatment_ids"] = {"clean_commercial", "low_key_dramatic", "studio_seamless"}
    elif form_state["mode"] == "men" and form_state["styleMode"] == "random":
        profile["preferred_photo_treatment_ids"] = {
            "candid_phone_snapshot",
            "analog_35mm",
            "documentary_still",
            "direct_light_editorial",
            "concept_photo_editorial",
            "casual_indoor_selfie",
            "advertising_poster_realism",
            "mirror_selfie",
        }
        profile["deprioritized_photo_treatment_ids"] = {"clean_commercial"}
    elif form_state["mode"] == "men" and form_state["styleMode"] == "nightlife":
        profile["preferred_photo_treatment_ids"] = {
            "vintage_flash_photo",
            "direct_flash_night",
            "candid_phone_snapshot",
            "disposable_camera",
            "cinematic_poster_realism",
            "low_key_dramatic",
        }
        profile["deprioritized_photo_treatment_ids"] = {"clean_commercial"}
    photo_type_control = str(form_state.get("photoTypeControl", "balanced") or "balanced")
    photo_type_profile = PHOTO_TYPE_PREFERENCES.get(photo_type_control, {})
    if photo_type_profile:
        profile = _merge_profile_preferences(profile, photo_type_profile)
        if photo_type_profile.get("deprioritized_photo_treatment_ids") and profile.get("preferred_photo_treatment_ids"):
            profile["preferred_photo_treatment_ids"] = set(profile.get("preferred_photo_treatment_ids", set())) - set(photo_type_profile["deprioritized_photo_treatment_ids"])
        if photo_type_profile.get("banned_scene_families") and profile.get("preferred_scene_families"):
            profile["preferred_scene_families"] = set(profile.get("preferred_scene_families", set())) - set(photo_type_profile["banned_scene_families"])
    if form_state["sceneFocus"] in SCENE_FOCUS_PREFERENCES:
        scene_profile = SCENE_FOCUS_PREFERENCES[form_state["sceneFocus"]]
        profile["required_scene_families"] = set(scene_profile.get("required_scene_families", set()))
        if scene_profile.get("preferred_route_ids"):
            profile["required_route_ids"] = set(scene_profile["preferred_route_ids"])
        for key in ("preferred_route_ids", "preferred_capture_ids"):
            if scene_profile.get(key):
                profile[key] = set(scene_profile[key])
    if form_state["mode"] == "women" and form_state.get("womenSceneFamily") and form_state["womenSceneFamily"] != "random":
        profile["required_scene_families"] = {form_state["womenSceneFamily"]}
        profile["preferred_scene_families"] = _merge_preference_sets(
            set(profile.get("preferred_scene_families", set())),
            {form_state["womenSceneFamily"]},
        )
    exact_theme_scenes, exact_theme_routes = _exact_theme_scene_constraints(form_state)
    exact_theme_location_keywords = _exact_theme_location_keywords(form_state)
    profile["requested_location_domain"] = _requested_location_domain(form_state)
    if exact_theme_scenes:
        explicit_women_scene_family = (
            form_state["mode"] == "women"
            and form_state.get("womenSceneFamily")
            and form_state["womenSceneFamily"] != "random"
        )
        if not explicit_women_scene_family:
            profile["required_scene_families"] = set(exact_theme_scenes)
        profile["preferred_scene_families"] = _merge_preference_sets(
            set(profile.get("preferred_scene_families", set())),
            set(exact_theme_scenes),
        )
    if exact_theme_location_keywords:
        profile["exact_theme_location_keywords"] = set(exact_theme_location_keywords)
    if exact_theme_routes:
        profile["preferred_route_ids"] = _merge_preference_sets(
            set(profile.get("preferred_route_ids", set())),
            set(exact_theme_routes),
        )
    pose_framing_control = str(form_state.get("poseFramingControl", "mixed") or "mixed")
    framing_profile = FRAMING_CONTROL_PREFERENCES.get(pose_framing_control)
    if framing_profile:
        preferred_framing_ids = framing_profile.get("preferred_framing_ids")
        if preferred_framing_ids:
            profile["preferred_framing_ids"] = _merge_preference_sets(
                set(profile.get("preferred_framing_ids", set())),
                set(preferred_framing_ids),
            )
        preferred_pose_tags = framing_profile.get("preferred_pose_tags")
        if preferred_pose_tags:
            profile["preferred_pose_tags"] = _merge_preference_sets(
                set(profile.get("preferred_pose_tags", set())),
                set(preferred_pose_tags),
            )
        framing_group_target_share = framing_profile.get("framing_group_target_share")
        if framing_group_target_share:
            profile["framing_group_target_share"] = dict(framing_group_target_share)
    if not female_custom_appearance:
        outfit_vibe_control = str(form_state.get("outfitVibeControl", "random") or "random")
        if outfit_vibe_control != "random" and form_state["mode"] in {"women", "couples"}:
            outfit_vibe_profile = FEMALE_OUTFIT_VIBE_PREFERENCES.get(outfit_vibe_control, {})
            for key in ("preferred_outfit_ids", "preferred_color_story_ids", "preferred_material_ids", "banned_outfit_ids"):
                values = outfit_vibe_profile.get(key)
                if values:
                    profile[key] = _merge_preference_sets(set(profile.get(key, set())), set(values))
        beauty_finish_control = str(form_state.get("beautyFinishControl", "random") or "random")
        if beauty_finish_control != "random" and form_state["mode"] in {"women", "couples"}:
            beauty_finish_profile = FEMALE_BEAUTY_FINISH_PREFERENCES.get(beauty_finish_control, {})
            for key in ("preferred_makeup_ids", "preferred_photo_treatment_ids"):
                values = beauty_finish_profile.get(key)
                if values:
                    profile[key] = _merge_preference_sets(set(profile.get(key, set())), set(values))
        outfit_reveal = _effective_outfit_reveal(form_state, spicy_level)
        if outfit_reveal in OUTFIT_REVEAL_PREFERENCES:
            profile.update({key: set(value) for key, value in OUTFIT_REVEAL_PREFERENCES[outfit_reveal].items()})
        if form_state["mode"] == "women":
            active_high_spicy_pose_ids = _women_active_high_spicy_pose_ids(spicy_level)
            if active_high_spicy_pose_ids:
                profile["preferred_pose_ids"] = _merge_preference_sets(
                    set(profile.get("preferred_pose_ids", set())),
                    active_high_spicy_pose_ids,
                )
    if form_state["styleMode"] in {"sport", "fitness"} and not female_custom_appearance:
        effective_outfit_reveal = _effective_outfit_reveal(form_state, spicy_level)
        spicy_fitness_outfits = {"zip_front_training_set", "cross_strap_keyhole_active_set"}
        if form_state["styleMode"] == "fitness":
            profile["banned_outfit_ids"] = _merge_preference_sets(
                set(profile.get("banned_outfit_ids", set())),
                {"crop_top_mini_skirt", "swimsuit", "bikini_set", "latex_editorial"},
            )
            profile["preferred_scene_families"] = _merge_preference_sets(
                set(profile.get("preferred_scene_families", set())),
                {"urban_daylight", "courtyard_garden", "coastal_boardwalk"},
            )
            profile["preferred_route_ids"] = _merge_preference_sets(
                set(profile.get("preferred_route_ids", set())),
                {"sports_flirt"},
            )
            safe_fitness_outfits = {"workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"}
            allowed_fitness_outfits = safe_fitness_outfits | (spicy_fitness_outfits if spicy_level >= 6 else set())
            profile["required_outfit_ids"] = allowed_fitness_outfits
            profile["preferred_outfit_ids"] = _merge_preference_sets(set(profile.get("preferred_outfit_ids", set())), allowed_fitness_outfits)
            profile["preferred_material_ids"] = _merge_preference_sets(set(profile.get("preferred_material_ids", set())), {"athletic_jersey"})
            if effective_outfit_reveal == "reserved":
                profile["preferred_color_story_ids"] = {"sport_clean_white", "black_ivory", "sage_stone", "olive_sand", "terracotta_sand"}
            elif effective_outfit_reveal == "balanced":
                profile["preferred_color_story_ids"] = {"sport_clean_white", "black_ivory", "red_ivory", "coral_ivory", "sage_stone", "olive_sand", "terracotta_sand", "mint_cream", "plum_blush"}
            else:
                profile["preferred_color_story_ids"] = {"sport_clean_white", "black_ivory", "red_ivory", "coral_ivory", "sage_stone", "olive_sand", "terracotta_sand", "mint_cream", "plum_blush", "lilac_smoke", "tangerine_cream"}
        elif effective_outfit_reveal == "reserved":
            profile["required_outfit_ids"] = {"workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"}
            profile["preferred_outfit_ids"] = {"workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"}
            profile["preferred_material_ids"] = _merge_preference_sets(set(profile.get("preferred_material_ids", set())), {"athletic_jersey"})
            profile["preferred_color_story_ids"] = {"sport_clean_white", "black_ivory", "sage_stone", "olive_sand"}
        elif effective_outfit_reveal == "balanced":
            profile["required_outfit_ids"] = {"workout_top_leggings", "zip_jacket_leggings", "zip_front_training_set"}
            profile["preferred_outfit_ids"] = {"workout_top_leggings", "zip_jacket_leggings", "zip_front_training_set"}
            profile["preferred_material_ids"] = _merge_preference_sets(set(profile.get("preferred_material_ids", set())), {"athletic_jersey"})
            profile["preferred_color_story_ids"] = {"sport_clean_white", "black_ivory", "red_ivory", "coral_ivory", "sage_stone", "terracotta_sand"}
        else:
            profile["required_outfit_ids"] = {"zip_front_training_set", "cross_strap_keyhole_active_set", "workout_top_leggings"}
            profile["required_material_ids"] = {"athletic_jersey"}
            profile["preferred_outfit_ids"] = {"zip_front_training_set", "cross_strap_keyhole_active_set", "workout_top_leggings"}
            profile["preferred_material_ids"] = _merge_preference_sets(set(profile.get("preferred_material_ids", set())), {"athletic_jersey"})
            profile["preferred_color_story_ids"] = {"sport_clean_white", "black_ivory", "red_ivory", "coral_ivory", "sage_stone", "olive_sand", "terracotta_sand", "mint_cream", "plum_blush", "lilac_smoke", "tangerine_cream"}
    if form_state["styleMode"] == "nightlife":
        profile["banned_outfit_ids"] = {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt"}
        profile["preferred_outfit_ids"] = _merge_preference_sets(set(profile.get("preferred_outfit_ids", set())), {"mini_dress", "blazer_mini_dress", "cami_midi_skirt", "bodysuit_trousers", "corset_trousers"})
        profile["preferred_material_ids"] = _merge_preference_sets(set(profile.get("preferred_material_ids", set())), {"satin", "tailored_woven", "ribbed_knit"})
        profile["preferred_color_story_ids"] = _merge_preference_sets(set(profile.get("preferred_color_story_ids", set())), {"black_gold", "oxblood_noir", "emerald_noir", "clean_neutrals", "hot_pink"})
        if form_state["mode"] == "women":
            profile["banned_outfit_ids"] = _merge_preference_sets(set(profile.get("banned_outfit_ids", set())), {"cardigan_skirt", "cardigan_trousers", "shirt_trousers", "sweater_jeans"})
            profile["preferred_outfit_ids"] = _merge_preference_sets(set(profile.get("preferred_outfit_ids", set())), {"column_dress", "wrap_blouse_skirt", "halter_trousers"})
        if form_state["mode"] == "couples":
            profile["banned_outfit_ids"] = _merge_preference_sets(set(profile.get("banned_outfit_ids", set())), {"polo_pleated_skirt", "workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers", "cardigan_skirt", "cardigan_trousers", "shirt_trousers", "sweater_jeans"})
            profile["preferred_outfit_ids"] = _merge_preference_sets(set(profile.get("preferred_outfit_ids", set())), {"blazer_mini_dress", "cami_midi_skirt", "column_dress", "wrap_blouse_skirt", "halter_trousers"})
    elif form_state["styleMode"] == "lifestyle":
        profile["banned_outfit_ids"] = {"swimsuit", "bikini_set", "latex_editorial", "corset_trousers"}
        profile["preferred_outfit_ids"] = _merge_preference_sets(set(profile.get("preferred_outfit_ids", set())), {"cardigan_skirt", "cardigan_trousers", "blouse_trousers", "shirt_trousers", "polo_pleated_skirt", "cami_midi_skirt", "wrap_blouse_skirt", "vest_trousers", "sweater_jeans"})
        profile["preferred_material_ids"] = _merge_preference_sets(set(profile.get("preferred_material_ids", set())), {"ribbed_knit", "crisp_cotton", "tailored_woven", "satin", "soft_knit_layers", "fluid_crepe"})
        profile["preferred_color_story_ids"] = _merge_preference_sets(set(profile.get("preferred_color_story_ids", set())), {"clean_neutrals", "navy_cream", "earthy_soft", "winter_neutrals", "powder_blue", "champagne_taupe", "chocolate_cream", "rosewood_smoke"})
        if form_state["mode"] == "women" and form_state.get("sceneFocus") == "bookish":
            profile["banned_outfit_ids"] = _merge_preference_sets(set(profile.get("banned_outfit_ids", set())), {"mini_dress", "blazer_mini_dress", "bodysuit_trousers", "polo_pleated_skirt", "workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"})
            profile["preferred_outfit_ids"] = _merge_preference_sets(set(profile.get("preferred_outfit_ids", set())), {"cardigan_skirt", "cardigan_trousers", "shirt_trousers", "sweater_jeans", "blouse_trousers", "wrap_blouse_skirt", "silk_blouse_midi_skirt", "cashmere_shell_trousers", "structured_day_dress", "mockneck_knit_skirt"})
            profile["preferred_color_story_ids"] = _merge_preference_sets(set(profile.get("preferred_color_story_ids", set())), {"navy_cream", "earthy_soft", "winter_neutrals", "powder_blue", "champagne_taupe", "chocolate_cream", "rosewood_smoke"})
        if form_state["mode"] == "couples":
            profile["banned_outfit_ids"] = _merge_preference_sets(set(profile.get("banned_outfit_ids", set())), {"mini_dress", "blazer_mini_dress", "bodysuit_trousers", "polo_pleated_skirt", "workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"})
            profile["preferred_outfit_ids"] = _merge_preference_sets(set(profile.get("preferred_outfit_ids", set())), {"wrap_blouse_skirt", "column_dress", "vest_trousers", "cardigan_skirt", "cardigan_trousers", "shirt_trousers", "sweater_jeans", "blouse_trousers", "silk_blouse_midi_skirt", "cashmere_shell_trousers", "structured_day_dress"})
            profile["preferred_color_story_ids"] = _merge_preference_sets(set(profile.get("preferred_color_story_ids", set())), {"navy_cream", "earthy_soft", "powder_blue", "winter_neutrals", "champagne_taupe", "rosewood_smoke"})
            profile["preferred_photo_treatment_ids"] = _merge_preference_sets(set(profile.get("preferred_photo_treatment_ids", set())), {"candid_phone_snapshot", "analog_35mm", "documentary_still", "disposable_camera", "casual_indoor_selfie", "direct_light_editorial"})
            profile["deprioritized_photo_treatment_ids"] = _merge_preference_sets(set(profile.get("deprioritized_photo_treatment_ids", set())), {"clean_commercial"})
    elif form_state["styleMode"] == "cultural_bookish":
        profile["banned_outfit_ids"] = _merge_preference_sets(set(profile.get("banned_outfit_ids", set())), {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt", "corset_trousers", "mini_dress", "blazer_mini_dress", "bodysuit_trousers"})
        profile["preferred_scene_families"] = _merge_preference_sets(set(profile.get("preferred_scene_families", set())), {"culture_bookish"})
        profile["preferred_outfit_ids"] = _merge_preference_sets(set(profile.get("preferred_outfit_ids", set())), {"cardigan_skirt", "cardigan_trousers", "shirt_trousers", "blouse_trousers", "wrap_blouse_skirt", "silk_blouse_midi_skirt", "cashmere_shell_trousers", "structured_day_dress", "mockneck_knit_skirt", "column_dress", "vest_trousers"})
        profile["preferred_material_ids"] = _merge_preference_sets(set(profile.get("preferred_material_ids", set())), {"soft_knit_layers", "tailored_woven", "fluid_crepe", "crisp_cotton", "ribbed_knit"})
        profile["preferred_color_story_ids"] = _merge_preference_sets(set(profile.get("preferred_color_story_ids", set())), {"navy_cream", "earthy_soft", "winter_neutrals", "powder_blue", "champagne_taupe", "chocolate_cream", "rosewood_smoke"})
        profile["preferred_photo_treatment_ids"] = _merge_preference_sets(set(profile.get("preferred_photo_treatment_ids", set())), {"analog_35mm", "documentary_still", "candid_phone_snapshot", "direct_light_editorial", "disposable_camera"})
        profile["deprioritized_photo_treatment_ids"] = _merge_preference_sets(set(profile.get("deprioritized_photo_treatment_ids", set())), {"clean_commercial"})
    elif form_state["styleMode"] == "romantic":
        profile["banned_outfit_ids"] = _merge_preference_sets(set(profile.get("banned_outfit_ids", set())), {"swimsuit", "bikini_set", "crop_top_mini_skirt", "latex_editorial", "corset_trousers", "mini_dress", "bodysuit_trousers", "cardigan_skirt", "sweater_jeans", "cardigan_trousers", "shirt_trousers", "blouse_trousers"})
        profile["preferred_outfit_ids"] = _merge_preference_sets(set(profile.get("preferred_outfit_ids", set())), {"cami_midi_skirt", "wrap_blouse_skirt", "column_dress", "halter_trousers", "silk_blouse_midi_skirt", "structured_day_dress", "mockneck_knit_skirt"})
        profile["preferred_material_ids"] = _merge_preference_sets(set(profile.get("preferred_material_ids", set())), {"satin", "fluid_crepe", "tailored_woven", "matte_jersey", "ribbed_knit"})
        profile["preferred_color_story_ids"] = _merge_preference_sets(set(profile.get("preferred_color_story_ids", set())), {"powder_blue", "navy_cream", "earthy_soft", "winter_neutrals", "champagne_taupe", "rosewood_smoke", "chocolate_cream"})
        profile["preferred_photo_treatment_ids"] = _merge_preference_sets(set(profile.get("preferred_photo_treatment_ids", set())), {"analog_35mm", "documentary_still", "cinematic_poster_realism", "direct_light_editorial", "candid_phone_snapshot"})
        profile["deprioritized_photo_treatment_ids"] = _merge_preference_sets(set(profile.get("deprioritized_photo_treatment_ids", set())), {"clean_commercial"})
    elif form_state["styleMode"] == "creative_artistic":
        profile["banned_outfit_ids"] = _merge_preference_sets(set(profile.get("banned_outfit_ids", set())), {"polo_pleated_skirt", "workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers", "mini_dress"})
        profile["preferred_outfit_ids"] = _merge_preference_sets(set(profile.get("preferred_outfit_ids", set())), {"vest_trousers", "column_dress", "wrap_blouse_skirt", "halter_trousers", "blazer_mini_dress", "cami_midi_skirt", "blouse_trousers", "apron_workshop_trousers", "silk_blouse_midi_skirt"})
        profile["preferred_material_ids"] = _merge_preference_sets(set(profile.get("preferred_material_ids", set())), {"fluid_crepe", "tailored_woven", "satin", "matte_jersey"})
        profile["preferred_color_story_ids"] = _merge_preference_sets(set(profile.get("preferred_color_story_ids", set())), {"slate_blue_ink", "rosewood_smoke", "powder_blue", "black_gold", "emerald_noir", "chocolate_cream"})
    elif form_state["styleMode"] == "random":
        profile["banned_outfit_ids"] = _merge_preference_sets(set(profile.get("banned_outfit_ids", set())), {"swimsuit", "bikini_set", "latex_editorial"})
        if form_state["mode"] in {"women", "couples"}:
            profile["banned_outfit_ids"] = _merge_preference_sets(set(profile.get("banned_outfit_ids", set())), {"crop_top_mini_skirt"})
        profile["preferred_outfit_ids"] = _merge_preference_sets(set(profile.get("preferred_outfit_ids", set())), {"cami_midi_skirt", "cardigan_skirt", "blouse_trousers", "shirt_trousers", "cardigan_trousers", "vest_trousers", "column_dress", "wrap_blouse_skirt", "halter_trousers", "silk_blouse_midi_skirt", "mockneck_knit_skirt", "cashmere_shell_trousers", "structured_day_dress", "knit_top_trousers", "sweater_jeans", "apron_workshop_trousers"})
        profile["preferred_color_story_ids"] = _merge_preference_sets(set(profile.get("preferred_color_story_ids", set())), {"black_gold", "black_ivory", "teal_cream", "olive_sand", "sage_stone", "butter_denim", "coral_ivory", "plum_blush", "mint_cream", "lilac_smoke", "aqua_white", "terracotta_sand", "cobalt_white", "tangerine_cream", "red_ivory"})
        if form_state["mode"] == "women":
            profile["preferred_outfit_ids"] = set(profile.get("preferred_outfit_ids", set())) - {"mini_dress", "blazer_mini_dress", "bodysuit_trousers"}
            profile["body_group_target_share"] = {
                "lean": 0.35,
                "toned": 0.30,
                "athletic": 0.25,
                "curvy": 0.10,
            }
            profile["breast_size_target_share"] = {
                "small_breasts": 0.10,
                "medium_breasts": 0.40,
                "big_breasts": 0.40,
                "very_big_breasts": 0.07,
                "extra_large_breasts": 0.03,
            }
    elif form_state["styleMode"] == "luxury":
        profile["banned_outfit_ids"] = _merge_preference_sets(set(profile.get("banned_outfit_ids", set())), {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt", "polo_pleated_skirt", "workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"})
        profile["preferred_outfit_ids"] = _merge_preference_sets(set(profile.get("preferred_outfit_ids", set())), {"blazer_mini_dress", "cami_midi_skirt", "bodysuit_trousers", "cardigan_trousers", "blouse_trousers", "vest_trousers", "column_dress", "wrap_blouse_skirt", "halter_trousers", "cashmere_shell_trousers", "structured_day_dress", "silk_blouse_midi_skirt", "mockneck_knit_skirt"})
        profile["preferred_material_ids"] = _merge_preference_sets(set(profile.get("preferred_material_ids", set())), {"satin", "tailored_woven", "fluid_crepe", "matte_jersey"})
        profile["preferred_color_story_ids"] = _merge_preference_sets(set(profile.get("preferred_color_story_ids", set())), {"black_gold", "oxblood_noir", "emerald_noir", "earthy_soft", "navy_cream", "chocolate_cream", "champagne_taupe", "slate_blue_ink", "rosewood_smoke"})
        if form_state["mode"] == "women" and form_state.get("sceneFocus") == "luxury":
            profile["banned_outfit_ids"] = _merge_preference_sets(set(profile.get("banned_outfit_ids", set())), {"bodysuit_trousers", "mini_dress"})
            profile["preferred_outfit_ids"] = _merge_preference_sets(set(profile.get("preferred_outfit_ids", set())), {"vest_trousers", "column_dress", "wrap_blouse_skirt", "blouse_trousers", "cami_midi_skirt", "cashmere_shell_trousers", "structured_day_dress"})
            profile["preferred_color_story_ids"] = _merge_preference_sets(set(profile.get("preferred_color_story_ids", set())), {"navy_cream", "chocolate_cream", "champagne_taupe", "slate_blue_ink", "rosewood_smoke"})
        if form_state["mode"] == "couples":
            profile["banned_outfit_ids"] = _merge_preference_sets(set(profile.get("banned_outfit_ids", set())), {"bodysuit_trousers", "shirt_trousers"})
            profile["preferred_outfit_ids"] = _merge_preference_sets(set(profile.get("preferred_outfit_ids", set())), {"vest_trousers", "column_dress", "wrap_blouse_skirt", "blouse_trousers", "cami_midi_skirt"})
            profile["preferred_color_story_ids"] = _merge_preference_sets(set(profile.get("preferred_color_story_ids", set())), {"navy_cream", "chocolate_cream", "champagne_taupe", "slate_blue_ink", "rosewood_smoke"})
    if form_state["mode"] == "women" and form_state.get("womenSceneFamily") and form_state["womenSceneFamily"] != "random":
        scene_family_profile = WOMEN_SCENE_FAMILY_FASHION_PREFERENCES.get(form_state["womenSceneFamily"], {})
        for key in ("banned_outfit_ids", "preferred_outfit_ids", "preferred_hair_ids", "preferred_makeup_ids", "preferred_capture_ids"):
            values = scene_family_profile.get(key)
            if values:
                profile[key] = _merge_preference_sets(set(profile.get(key, set())), set(values))
    if form_state["mode"] == "women":
        profile["banned_hair_ids"] = _merge_preference_sets(set(profile.get("banned_hair_ids", set())), WOMEN_BANNED_HAIR_IDS)
    if form_state["mode"] == "women" and spicy_level <= 3:
        profile["preferred_pose_ids"] = {"standing_three_quarter", "slow_walk", "seated_sideways", "cross_legged_seated", "legs_to_side_pose", "chair_sideways_pose"}
        profile["preferred_hand_action_ids"] = {"hand_at_waist", "braced_behind"}
        profile["preferred_mood_ids"] = {"calm_confident", "soft_flirty"}
    if spicy_level >= 6:
        profile["banned_mood_ids"] = {"calm_confident"}
    if not female_custom_appearance:
        hair_ids: set[str] = set()
        if form_state["hairLength"] in HAIR_LENGTH_PREFERENCES:
            hair_ids |= HAIR_LENGTH_PREFERENCES[form_state["hairLength"]]
        if form_state["hairstyle"] not in {"random", "custom"}:
            hair_ids = {form_state["hairstyle"]}
        if hair_ids:
            profile["preferred_hair_ids"] = hair_ids
        hair_color_ids = HAIR_COLOR_PREFERENCES.get(form_state["hairColorControl"], set())
        if hair_color_ids:
            profile["required_hair_color_ids"] = set(hair_color_ids)
            profile["preferred_hair_color_ids"] = set(hair_color_ids)
        if form_state["mode"] in {"women", "couples"} and form_state["hairColorControl"] == "random" and _parse_bool(form_state.get("allowDyedNaturalHairColors", False)):
            profile["allow_dyed_natural_hair_colors"] = True
        makeup_control = _effective_makeup_control(form_state, spicy_level)
        if makeup_control != "random":
            profile["preferred_makeup_ids"] = {makeup_control}
        if form_state["eyeColorControl"] != "random":
            profile["required_eye_color_ids"] = {form_state["eyeColorControl"]}
            profile["preferred_eye_color_ids"] = {form_state["eyeColorControl"]}
        if form_state["breastSizeControl"] != "random":
            profile["required_breast_size_ids"] = {form_state["breastSizeControl"]}
    if form_state["mode"] == "couples" and form_state["personMode"] == "different_persons":
        for key, value in _couples_different_persons_identity_constraints(form_state).items():
            if key.startswith("preferred_"):
                profile[key] = _merge_preference_sets(set(profile.get(key, set())), set(value))
            else:
                profile[key] = set(value)
    allowed_ages = _normalize_age_filter(form_state["age"])
    if allowed_ages:
        profile["required_age_band_ids"] = set(allowed_ages)
    if form_state["racePreset"] in SAME_PERSON_ETHNICITY_IDS:
        profile["required_ethnicity_ids"] = {form_state["racePreset"]}
        profile["preferred_ethnicity_ids"] = {form_state["racePreset"]}
    if form_state["personMode"] == "same_person":
        body_groups = SAME_PERSON_BODY_GROUPS.get(form_state["bodyMixPreset"])
        if body_groups:
            profile["required_body_groups"] = set(body_groups)
    return profile
