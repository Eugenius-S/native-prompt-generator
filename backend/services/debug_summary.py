from __future__ import annotations

from collections import Counter
from typing import Any

from backend.character_constraints import resolve_character_constraint_segment
from backend.engine import generator
from backend.forms.constants import SCENE_FOCUS_PREFERENCES
from backend.photo_treatment_mix import (
    photo_treatment_mix_bucket,
    photo_treatment_quality_tier,
    photo_treatment_tone,
)
from backend.services.photo_treatment_lookup import _photo_treatment_lookup


def _style_debug_signals(candidate: dict[str, Any], style_mode: str, scene_focus: str) -> dict[str, list[str]]:
    matched: list[str] = []
    misses: list[str] = []
    scene = candidate.get("scene_family_id", "")
    route = candidate.get("route", "")
    capture = candidate.get("capture_style_id", "")
    rules: dict[str, tuple[set[str], set[str], set[str]]] = {
        "studio": ({"studio"}, {"studio_portrait"}, {"editorial_photo", "fashion_photo"}),
        "lifestyle": ({"urban_daylight", "culture_bookish", "garden_conservatory"}, {"casual_candid", "amateur_phone"}, {"lifestyle_photo", "smartphone_photo"}),
        "luxury": ({"residential_luxury", "hospitality_suite", "grooming_bath"}, {"luxury_interior"}, {"editorial_photo", "fashion_photo"}),
        "old_money": ({"residential_luxury", "culture_bookish", "garden_conservatory"}, {"luxury_interior", "casual_candid"}, {"editorial_photo", "lifestyle_photo"}),
        "romantic": ({"courtyard_garden", "garden_conservatory", "coastal_pool"}, {"casual_candid"}, {"lifestyle_photo", "editorial_photo"}),
        "vacation": ({"coastal_boardwalk", "coastal_pool", "hospitality_suite", "wellness_spa"}, {"casual_candid", "luxury_interior", "slutty_lifestyle"}, {"lifestyle_photo", "fashion_photo"}),
        "sport": ({"urban_daylight"}, {"sports_flirt"}, {"fashion_photo", "lifestyle_photo"}),
        "fitness": ({"urban_daylight", "wellness_spa"}, {"sports_flirt", "luxury_interior"}, {"fashion_photo", "lifestyle_photo"}),
        "cosplay": ({"studio"}, {"fantasy_cosplay"}, {"editorial_photo", "fashion_photo"}),
        "fantasy": ({"studio"}, {"fantasy_cosplay"}, {"editorial_photo", "fashion_photo"}),
        "nightlife": ({"nightlife_bar", "nightlife_neon"}, {"cinematic_night"}, {"editorial_photo", "fashion_photo"}),
        "cultural_bookish": ({"culture_bookish"}, {"casual_candid", "luxury_interior"}, {"editorial_photo", "lifestyle_photo"}),
        "creative_artistic": ({"creative_gallery"}, {"casual_candid"}, {"editorial_photo", "fashion_photo"}),
        "urban_day": ({"urban_daylight"}, {"casual_candid", "amateur_phone"}, {"lifestyle_photo", "smartphone_photo"}),
        "coastal": ({"coastal_boardwalk", "coastal_pool"}, {"slutty_lifestyle", "casual_candid"}, {"lifestyle_photo", "fashion_photo"}),
    }
    scenes, routes, captures = rules.get(style_mode, (set(), set(), set()))
    if scenes:
        (matched if scene in scenes else misses).append(f'scene {"fit" if scene in scenes else "off"}')
    if routes:
        (matched if route in routes else misses).append(f'route {"fit" if route in routes else "off"}')
    if captures:
        (matched if capture in captures else misses).append(f'capture {"fit" if capture in captures else "off"}')
    focus = SCENE_FOCUS_PREFERENCES.get(scene_focus)
    if focus:
        required = set(focus.get("required_scene_families", set()))
        preferred_routes = set(focus.get("preferred_route_ids", set()))
        if required:
            (matched if scene in required else misses).append(f'focus-scene {"fit" if scene in required else "off"}')
        if preferred_routes:
            (matched if route in preferred_routes else misses).append(f'focus-route {"fit" if route in preferred_routes else "off"}')
    return {"matched": matched, "misses": misses}


def _treatment_debug_signals(candidate: dict[str, Any], style_mode: str) -> dict[str, list[str]]:
    matched: list[str] = []
    misses: list[str] = []
    profile = _photo_treatment_lookup().get(candidate.get("photo_treatment_id", ""))
    if not profile:
        return {"matched": matched, "misses": misses}
    scene = candidate.get("scene_family_id", "")
    capture = candidate.get("capture_style_id", "")
    lighting = candidate.get("lighting_family_id", "")
    time_id = candidate.get("time_of_day_id", "")
    preferred_scenes = {str(value) for value in profile.get("preferred_scene_families", [])}
    preferred_styles = {str(value) for value in profile.get("preferred_style_modes", [])}
    preferred_captures = {str(value) for value in profile.get("preferred_capture_ids", [])}
    preferred_lighting = {str(value) for value in profile.get("preferred_lighting_ids", [])}
    preferred_times = {str(value) for value in profile.get("preferred_time_ids", [])}
    if preferred_scenes:
        (matched if scene in preferred_scenes else misses).append(f'treatment-scene {"fit" if scene in preferred_scenes else "off"}')
    if preferred_styles:
        (matched if style_mode in preferred_styles else misses).append(f'treatment-style {"fit" if style_mode in preferred_styles else "off"}')
    if preferred_captures:
        (matched if capture in preferred_captures else misses).append(f'treatment-capture {"fit" if capture in preferred_captures else "off"}')
    if preferred_lighting:
        (matched if lighting in preferred_lighting else misses).append(f'treatment-light {"fit" if lighting in preferred_lighting else "off"}')
    if preferred_times:
        (matched if time_id in preferred_times else misses).append(f'treatment-time {"fit" if time_id in preferred_times else "off"}')
    return {"matched": matched, "misses": misses}


def _summarize_debug(
    prompts: list[dict[str, Any]],
    form_state: dict[str, Any],
    spicy_level: int,
    effective_location_strategy: str,
    effective_anti_repeat: str,
    effective_style_mode: str,
) -> dict[str, Any]:
    from backend.prompt_service import (
        _effective_makeup_control,
        _effective_outfit_reveal,
        _female_appearance_mode,
        _female_appearance_prompt,
        _female_custom_appearance_active,
        _male_appearance_mode,
        _male_appearance_prompt,
    )

    def prompt_debug_meta(item: dict[str, Any], index: int) -> dict[str, Any]:
        candidate = item["candidate"]
        return {
            "index": index + 1,
            "route": candidate.get("route", ""),
            "sceneFamily": candidate.get("scene_family_id", ""),
            "setting": candidate.get("setting_micro", ""),
            "outfit": candidate.get("outfit_family", ""),
            "material": candidate.get("material", ""),
            "color": candidate.get("color_story", ""),
            "pose": candidate.get("pose_family", ""),
            "hand": candidate.get("hand_action", ""),
            "framing": candidate.get("camera_framing", ""),
            "lighting": candidate.get("lighting_family", ""),
            "time": candidate.get("time_of_day", ""),
            "mood": candidate.get("mood_energy", ""),
            "photoTreatment": candidate.get("photo_treatment", ""),
            "photoTreatmentCategory": candidate.get("photo_treatment_category", ""),
            "cameraVibe": candidate.get("camera_vibe", ""),
            "colorGrade": candidate.get("color_grade", ""),
            "finish": candidate.get("finish_render", ""),
            "hair": candidate.get("hair_structure_override") or candidate.get("hair_structure", ""),
            "hairColor": candidate.get("hair_color_override") or candidate.get("hair_color", ""),
            "makeup": candidate.get("makeup_style", ""),
            "capture": candidate.get("capture_style", ""),
            "captureRender": candidate.get("capture_style_render") or candidate.get("capture_style", ""),
            "repairApplied": bool(item.get("repairApplied")),
            "findingsCount": len(item.get("findings", [])),
        }

    def enrich_debug_meta(raw_item: dict[str, Any], index: int) -> dict[str, Any]:
        meta = dict(raw_item.get("debugMeta") or prompt_debug_meta(raw_item, index))
        candidate = raw_item["candidate"]
        character_constraint = str(candidate.get("character_constraint", "") or "")
        character_segment = resolve_character_constraint_segment(candidate=candidate)
        if character_constraint:
            meta["characterConstraint"] = character_constraint
        if character_segment:
            meta["characterConstraintSegment"] = character_segment
        meta["styleSignals"] = _style_debug_signals(candidate, effective_style_mode, form_state["sceneFocus"])
        meta["treatmentSignals"] = _treatment_debug_signals(candidate, effective_style_mode)
        return meta

    prompt_decisions = [enrich_debug_meta(item, index) for index, item in enumerate(prompts)]
    scene_families = Counter(item["candidate"]["scene_family_id"] for item in prompts)
    framings = Counter(item["candidate"]["camera_framing"] for item in prompts)
    poses = Counter(item["candidate"]["pose_family"] for item in prompts)
    treatments = Counter(item["candidate"].get("photo_treatment_id", "") for item in prompts if item["candidate"].get("photo_treatment_id"))
    treatment_categories = Counter(item["candidate"].get("photo_treatment_category", "") for item in prompts if item["candidate"].get("photo_treatment_category"))
    treatment_mix_buckets = Counter(
        photo_treatment_mix_bucket(item["candidate"].get("photo_treatment_id", ""), item["candidate"].get("photo_treatment_category", ""))
        for item in prompts
        if item["candidate"].get("photo_treatment_id")
    )
    treatment_quality_tiers = Counter(
        photo_treatment_quality_tier(item["candidate"].get("photo_treatment_id", ""), item["candidate"].get("photo_treatment_category", ""))
        for item in prompts
        if item["candidate"].get("photo_treatment_id")
    )
    treatment_tones = Counter(
        photo_treatment_tone(item["candidate"].get("photo_treatment_id", ""), item["candidate"].get("photo_treatment_category", ""))
        for item in prompts
        if item["candidate"].get("photo_treatment_id")
    )
    captures = Counter(item["candidate"].get("capture_style_render") or item["candidate"].get("capture_style", "") for item in prompts if item["candidate"].get("capture_style_render") or item["candidate"].get("capture_style"))
    lightings = Counter(item["candidate"].get("lighting_family", "") for item in prompts if item["candidate"].get("lighting_family"))
    camera_vibes = Counter(item["candidate"].get("camera_vibe", "") for item in prompts if item["candidate"].get("camera_vibe"))
    repairs = sum(1 for item in prompts if item["repairApplied"])
    findings = sum(len(item["findings"]) for item in prompts)
    stylized_count = treatment_categories.get("stylized", 0)
    polished_count = treatment_categories.get("polished", 0)
    return {
        "batchSize": len(prompts),
        "identityLock": form_state["personMode"] == "same_person",
        "effectiveSpicyLevel": spicy_level,
        "effectiveStyleMode": effective_style_mode,
        "effectivePhotoType": str(form_state.get("photoTypeControl", "balanced") or "balanced"),
        "effectiveLocationStrategy": effective_location_strategy,
        "effectiveAntiRepeat": effective_anti_repeat,
        "effectiveSceneFocus": form_state["sceneFocus"],
        "effectiveWomenSceneFamily": form_state["womenSceneFamily"] if form_state["mode"] == "women" else "off",
        "effectiveOutfitReveal": "custom" if _female_custom_appearance_active(form_state) else _effective_outfit_reveal(form_state, spicy_level),
        "effectiveMakeup": "custom" if _female_custom_appearance_active(form_state) else _effective_makeup_control(form_state, spicy_level),
        "femaleAppearanceMode": _female_appearance_mode(form_state) if form_state["mode"] in {"women", "couples"} else "off",
        "femaleAppearancePrompt": _female_appearance_prompt(form_state),
        "maleAppearanceMode": _male_appearance_mode(form_state) if form_state["mode"] in {"men", "couples"} else "off",
        "maleAppearancePrompt": _male_appearance_prompt(form_state),
        "stylizedCount": stylized_count,
        "polishedCount": polished_count,
        "uniquePhotoTreatments": len(treatments),
        "photoTreatmentDistribution": dict(treatments),
        "photoTreatmentCategoryDistribution": dict(treatment_categories),
        "photoTreatmentMixBucketDistribution": dict(treatment_mix_buckets),
        "photoTreatmentQualityTierDistribution": dict(treatment_quality_tiers),
        "photoTreatmentToneDistribution": dict(treatment_tones),
        "captureDistribution": dict(captures),
        "lightingDistribution": dict(lightings),
        "cameraVibeDistribution": dict(camera_vibes),
        "sceneFamilyDistribution": dict(scene_families),
        "framingDistribution": dict(framings),
        "poseDistribution": dict(poses),
        "repairAppliedCount": repairs,
        "validationFindingCount": findings,
        "promptDecisions": prompt_decisions,
    }
