from __future__ import annotations

import math
import random
from typing import Any

from . import data_loader, line_bank_loader, selectors

try:
    from .repair import repair_candidate
    from .validator import load_rule_bank, validate_candidate
except ImportError:
    from repair import repair_candidate
    from validator import load_rule_bank, validate_candidate


def _recent_memory_set(memory: dict[str, Any], key: str, count: int) -> set[str]:
    values = memory.get(key, [])
    if count <= 0:
        return set()
    return set(values[-count:])


def _push_memory(memory: dict[str, Any], key: str, value: str, max_len: int) -> None:
    seq = list(memory.get(key, []))
    seq.append(value)
    memory[key] = seq[-max_len:]


def persist_batch_memory(batch: list[dict[str, Any]]) -> None:
    data = data_loader.load_data_bank()
    rules = load_rule_bank()
    windows = rules["anti_repeat"].get("memory_windows", {})
    for item in batch:
        _push_memory(data["memory"], "setting_macros", item["setting_macro_id"], windows.get("setting_macros", 50))
        _push_memory(data["memory"], "setting_scene_families", item["scene_family_id"], windows.get("setting_scene_families", 50))
        _push_memory(data["memory"], "setting_base_spaces", item["setting_micro_id"], windows.get("setting_base_spaces", 50))
        _push_memory(data["memory"], "setting_scenes", item["setting_scene_id"], windows.get("setting_scenes", 50))
        _push_memory(data["memory"], "outfit_families", item["outfit_family_id"], windows.get("outfit_families", 50))
        _push_memory(data["memory"], "pose_families", item["pose_family_id"], windows.get("pose_families", 50))
        _push_memory(data["memory"], "camera_framings", item["camera_framing_id"], windows.get("camera_framings", 50))
        _push_memory(data["memory"], "camera_angles", item["camera_angle_id"], windows.get("camera_angles", 50))
    data_loader._save_memory(data["memory"])


def _setting_micro_cap(setting_micro_id: str, setting_micro_rules: dict[str, Any], default_cap: int) -> int:
    if setting_micro_id in set(setting_micro_rules.get("single_use_ids", [])):
        return 1
    return default_cap


def _outfit_compatible_with_required_scene_families(
    outfit_family: dict[str, Any],
    base_spaces: list[dict[str, Any]],
    required_scene_families: set[str],
    style_mode: str,
) -> bool:
    if not required_scene_families:
        return True
    outfit_predicate = selectors._base_space_outfit_predicate(outfit_family, style_mode)
    return any(item.get("scene_family_id") in required_scene_families and outfit_predicate(item) for item in base_spaces)


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
    if tags & {"outdoor", "courtyard", "rooftop", "sunny", "daylight", "sunlit", "summer"}:
        return "urban_outdoor"
    return "indoor"


def _random_scene_group_matches(candidate: dict[str, Any], expected_group: str) -> bool:
    actual_group = _random_scene_group(candidate)
    if expected_group == "outdoor":
        return actual_group in {"urban_outdoor", "water", "nature", "outdoor"}
    return actual_group == expected_group


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


def _build_random_balance_schedules(count: int, rnd: random.Random) -> tuple[list[str], list[bool]]:
    scene_counts = selectors._allocate_counts(
        count,
        {"indoor": 0.4, "urban_outdoor": 0.15, "water": 0.25, "nature": 0.2},
    )
    scene_schedule = selectors._build_group_schedule(scene_counts, max_same_in_row=2, rnd=rnd)
    light_counts = selectors._allocate_counts(count, {"bright": 0.7, "open": 0.3})
    light_schedule = selectors._build_group_schedule(light_counts, max_same_in_row=2, rnd=rnd)
    return scene_schedule, [item == "bright" for item in light_schedule]


def build_candidate(
    data: dict[str, Any],
    rules: dict[str, Any],
    rnd: random.Random,
    ethnicity_group: str,
    body_group: str,
    breast_size_id: str | None,
    pose_group: str,
    framing_group: str,
    vivid_hair: bool,
    identity_core: dict[str, dict[str, Any]] | None = None,
    recent_batch: list[dict[str, Any]] | None = None,
    previous: dict[str, str] | None = None,
    avoid_setting_micro_ids: set[str] | None = None,
    scene_family_counts: dict[str, int] | None = None,
    style_mode: str = "random",
    preferred_ethnicity_ids: set[str] | None = None,
    user_profile: dict[str, Any] | None = None,
    mode: str = "women",
    spicy_level: int | None = None,
    random_scene_group_override: str | None = None,
) -> dict[str, Any]:
    previous = previous or {}
    recent_batch = recent_batch or []
    identity_core = identity_core or {}
    scene_family_counts = scene_family_counts or {}
    profile = selectors._merged_profile(selectors._style_profile(style_mode), user_profile)
    required_age_band_ids = set(profile.get("required_age_band_ids", []))
    required_body_groups = set(profile.get("required_body_groups", []))
    required_hair_ids = set(profile.get("required_hair_ids", []))
    banned_hair_ids = set(profile.get("banned_hair_ids", []))
    required_breast_size_ids = set(profile.get("required_breast_size_ids", []))
    required_eye_color_ids = set(profile.get("required_eye_color_ids", []))
    required_ethnicity_ids = set(profile.get("required_ethnicity_ids", []))
    breast_size = identity_core.get("breast_size") or selectors._choose_generic(
        data["subjects"]["breast_sizes"],
        rnd,
        previous.get("breast_size_id"),
        predicate=selectors._compose_predicates(
            (lambda item: item["id"] == breast_size_id) if breast_size_id else None,
            (lambda item: item["id"] in required_breast_size_ids) if required_breast_size_ids else None,
        ),
    )
    age_predicate = (
        (lambda item: item["id"] in required_age_band_ids)
        if required_age_band_ids
        else selectors._age_predicate(rules["batch_balance"], breast_size["id"], vivid_hair)
    )
    age_band = identity_core.get("age_band") or selectors._choose_generic(data["subjects"]["age_bands"], rnd, previous.get("age_band_id"), predicate=age_predicate)
    ethnicity = identity_core.get("ethnicity") or selectors._choose_ethnicity(
        data["subjects"]["ethnicities"],
        ethnicity_group,
        rnd,
        previous.get("ethnicity_id"),
        preferred_ids=(preferred_ethnicity_ids or set()) | required_ethnicity_ids,
        required_ids=required_ethnicity_ids,
    )
    body_type = identity_core.get("body_type") or selectors._choose_body_type(
        data["subjects"]["body_types"],
        body_group,
        rnd,
        previous.get("body_type_id"),
        predicate=(lambda item: item.get("group") in required_body_groups) if required_body_groups else None,
    )
    beauty_level = identity_core.get("beauty_level") or selectors._choose_generic(data["subjects"]["beauty_levels"], rnd, previous.get("beauty_level_id"))
    hair_color = identity_core.get("hair_color") or selectors._choose_hair_color(
        data["styling"]["hair_colors"],
        rnd,
        age_band["id"],
        vivid_hair,
        ethnicity_group,
        previous.get("hair_color_id"),
        required_ids=set(profile.get("required_hair_color_ids", [])),
        preferred_ids=set(profile.get("preferred_hair_color_ids", [])),
        allow_dyed_natural=bool(profile.get("allow_dyed_natural_hair_colors", False)),
    )
    hair_structure = identity_core.get("hair_structure") or selectors._choose_generic(
        data["styling"]["hair_structures"],
        rnd,
        previous.get("hair_structure_id"),
        predicate=selectors._compose_predicates(
            (lambda item: item["id"] in required_hair_ids) if required_hair_ids else None,
            (lambda item: item["id"] not in banned_hair_ids) if banned_hair_ids else None,
        ),
        preferred_predicate=selectors._style_preference_predicate(profile, ids_key="preferred_hair_ids", tags_key="preferred_hair_tags"),
    )
    eye_color = identity_core.get("eye_color") or selectors._choose_generic(
        data["subjects"]["eye_colors"],
        rnd,
        previous.get("eye_color_id"),
        predicate=(lambda item: item["id"] in required_eye_color_ids) if required_eye_color_ids else None,
        preferred_predicate=selectors._style_preference_predicate(profile, ids_key="preferred_eye_color_ids", tags_key="preferred_eye_color_tags"),
    )
    makeup_style = identity_core.get("makeup_style") or selectors._choose_generic(
        data["styling"]["makeup_styles"],
        rnd,
        previous.get("makeup_style_id"),
        preferred_predicate=selectors._style_preference_predicate(profile, ids_key="preferred_makeup_ids", tags_key="preferred_makeup_tags"),
    )
    scene_group_required_families: set[str] = set()
    if random_scene_group_override == "water":
        scene_group_required_families = {"coastal_pool", "coastal_boardwalk"}
    elif random_scene_group_override == "nature":
        scene_group_required_families = {"courtyard_garden", "garden_conservatory"}
    elif random_scene_group_override == "urban_outdoor":
        scene_group_required_families = {"urban_daylight"}
    elif random_scene_group_override == "indoor":
        scene_group_required_families = {
            "residential_luxury",
            "hospitality_suite",
            "grooming_bath",
            "culture_bookish",
            "creative_gallery",
            "wellness_spa",
            "nightlife_bar",
        }
    effective_required_scene_families = set(profile.get("required_scene_families", []))
    if not effective_required_scene_families and scene_group_required_families:
        effective_required_scene_families = set(scene_group_required_families)
    required_outfit_ids = set(profile.get("required_outfit_ids", []))
    banned_outfit_ids = set(profile.get("banned_outfit_ids", []))
    outfit_family = selectors._choose_generic(
        data["styling"]["outfit_families"],
        rnd,
        previous.get("outfit_family_id"),
        predicate=selectors._compose_predicates(
            (lambda item: item["id"] not in banned_outfit_ids) if banned_outfit_ids else None,
            (lambda item: item["id"] in required_outfit_ids) if required_outfit_ids else None,
            (
                lambda item: _outfit_compatible_with_required_scene_families(
                    item,
                    data["setting_engine"]["base_spaces"],
                    effective_required_scene_families,
                    style_mode,
                )
            )
            if effective_required_scene_families
            else None,
        ),
        preferred_predicate=selectors._style_preference_predicate(profile, ids_key="preferred_outfit_ids", tags_key="preferred_outfit_tags"),
    )
    use_generic_line_banks = style_mode not in {"sport", "fitness"}
    line_outfit_records: list[dict[str, Any]] = []
    if mode == "women" and use_generic_line_banks:
        line_outfit_records = line_bank_loader.records_for_level(
            data.get("line_banks", {}),
            gender="women",
            domain="outfits",
            spicy_level=spicy_level,
        )
    required_material_ids = set(profile.get("required_material_ids", []))
    material = selectors._choose_generic(
        data["styling"]["materials"],
        rnd,
        previous.get("material_id"),
        predicate=selectors._compose_predicates(
            selectors._outfit_material_predicate(outfit_family["id"]),
            (lambda item: item["id"] in required_material_ids) if required_material_ids else None,
        ),
        preferred_predicate=selectors._style_preference_predicate(profile, ids_key="preferred_material_ids", tags_key="preferred_material_tags"),
    )
    color_story = selectors._choose_generic(
        data["styling"]["color_stories"],
        rnd,
        previous.get("color_story_id"),
        predicate=selectors._color_story_predicate(age_band["id"], outfit_family["id"]),
        preferred_predicate=selectors._style_preference_predicate(profile, ids_key="preferred_color_story_ids", tags_key="preferred_color_story_tags"),
    )
    scene_family_id = selectors._choose_scene_family(
        data=data,
        batch_rules=rules["batch_balance"],
        rnd=rnd,
        outfit_family=outfit_family,
        style_mode=style_mode,
        recent_batch=recent_batch,
        scene_family_counts=scene_family_counts,
        previous_family_id=previous.get("scene_family_id"),
        required_families=effective_required_scene_families,
        preferred_families=set(profile.get("preferred_scene_families", [])),
        banned_families=set(profile.get("banned_scene_families", [])),
    )
    base_space = selectors._choose_generic(
        data["setting_engine"]["base_spaces"],
        rnd,
        previous.get("setting_micro_id"),
        predicate=lambda item: item["scene_family_id"] == scene_family_id and selectors._base_space_outfit_predicate(outfit_family, style_mode)(item),
        avoid_ids=avoid_setting_micro_ids,
    )
    line_bank_location = None
    requested_location_domain = str(profile.get("requested_location_domain", "realism") or "realism")
    shared_location_records: list[dict[str, Any]] = []
    if use_generic_line_banks:
        shared_location_records = line_bank_loader.shared_location_records_for_domain(
            data.get("line_banks", {}),
            spicy_level=spicy_level,
            requested_location_domain=requested_location_domain,
        )
    if shared_location_records:
        exact_theme_location_keywords = set(profile.get("exact_theme_location_keywords", []))
        filtered_location_records = [
            record
            for record in shared_location_records
            if line_bank_loader.line_bank_location_matches_scene(
                record,
                scene_family_id=scene_family_id,
                scene_tags=set(base_space.get("tags", [])),
                setting_value=str(base_space.get("value", "")),
                exact_theme_keywords=exact_theme_location_keywords,
                requested_location_domain=requested_location_domain,
            )
        ]
        if filtered_location_records:
            line_bank_location = selectors._choose_generic(
                filtered_location_records,
                rnd,
                previous.get("line_bank_location_id"),
            )
    line_bank_outfit = None
    if line_outfit_records:
        filtered_outfit_records = [
            record
            for record in line_outfit_records
            if line_bank_loader.line_bank_outfit_matches_scene(
                record,
                scene_family_id=scene_family_id,
                style_mode=style_mode,
                scene_tags=set(base_space.get("tags", [])),
                setting_value=str(base_space.get("value", "")),
            )
        ]
        if filtered_outfit_records:
            line_bank_outfit = selectors._choose_generic(
                filtered_outfit_records,
                rnd,
                previous.get("line_bank_outfit_id"),
            )
    setting_macro = selectors._choose_generic(
        data["settings"]["setting_macros"],
        rnd,
        previous.get("setting_macro_id"),
        predicate=selectors._setting_macro_for_base_space_predicate(base_space),
    )
    photo_treatment = selectors._choose_photo_treatment(
        data["photo_treatments"]["profiles"],
        rnd,
        scene_family_id=scene_family_id,
        style_mode=style_mode,
        mode=mode,
        previous_id=previous.get("photo_treatment_id"),
        required_ids=set(profile.get("required_photo_treatment_ids", [])),
        preferred_ids=set(profile.get("preferred_photo_treatment_ids", [])),
        deprioritized_ids=set(profile.get("deprioritized_photo_treatment_ids", [])),
    )
    effective_profile = selectors._merged_profile(profile, selectors._photo_treatment_profile(photo_treatment))
    scene_tags = selectors._scene_semantic_tags(base_space)
    setting_material = selectors._choose_generic(data["setting_engine"]["material_accents"], rnd, previous.get("setting_material_id"), predicate=selectors._setting_material_for_base_space(base_space))
    detail_accent = selectors._choose_generic(data["setting_engine"]["detail_accents"], rnd, previous.get("detail_accent_id"), predicate=selectors._detail_accent_for_base_space(base_space))
    pose_preference_predicate = selectors._style_preference_predicate(
        effective_profile,
        ids_key="preferred_pose_ids",
        tags_key="preferred_pose_tags",
    )
    try:
        pose_family = selectors._choose_generic(
            data["pose_bank"]["pose_families"],
            rnd,
            previous.get("pose_family_id"),
            predicate=selectors._pose_group_for_base_space(base_space, pose_group, style_mode),
            preferred_predicate=pose_preference_predicate,
        )
    except ValueError:
        pose_family = selectors._choose_generic(
            data["pose_bank"]["pose_families"],
            rnd,
            previous.get("pose_family_id"),
            predicate=selectors._pose_for_base_space(base_space, style_mode),
            preferred_predicate=pose_preference_predicate,
        )
    hand_action = selectors._choose_generic(
        data["composition"]["hand_actions"],
        rnd,
        previous.get("hand_action_id"),
        preferred_predicate=selectors._style_preference_predicate(effective_profile, ids_key="preferred_hand_action_ids", tags_key="preferred_hand_action_tags"),
    )
    camera_framing = selectors._choose_generic(
        data["composition"]["camera_framings"],
        rnd,
        previous.get("camera_framing_id"),
        predicate=selectors._framing_for_pose(pose_family, framing_group),
        preferred_predicate=selectors._style_preference_predicate(effective_profile, ids_key="preferred_framing_ids", tags_key="preferred_framing_tags"),
    )
    line_bank_pose = None
    if use_generic_line_banks and mode in {"women", "couples"}:
        pose_gender = "women" if mode == "women" else "couples"
        line_pose_records = line_bank_loader.records_for_level(
            data.get("line_banks", {}),
            gender=pose_gender,
            domain="poses",
            spicy_level=spicy_level,
        )
        if line_pose_records:
            filtered_pose_records = [
                record
                for record in line_pose_records
                if line_bank_loader.line_bank_pose_matches_scene(
                    record,
                    scene_family_id=scene_family_id,
                    scene_tags=set(base_space.get("tags", [])),
                    setting_value=str(base_space.get("value", "")),
                    framing_id=str(camera_framing.get("id", "")),
                )
            ]
            if filtered_pose_records:
                line_bank_pose = selectors._choose_generic(
                    filtered_pose_records,
                    rnd,
                    previous.get("line_bank_pose_id"),
                )
    camera_angle = selectors._choose_generic(data["composition"]["camera_angles"], rnd, previous.get("camera_angle_id"))
    time_of_day = selectors._choose_generic(
        data["composition"]["time_of_day"],
        rnd,
        previous.get("time_of_day_id"),
        predicate=selectors._time_of_day_for_base_space(base_space),
        preferred_predicate=selectors._style_preference_predicate(effective_profile, ids_key="preferred_time_ids", tags_key="preferred_time_tags"),
    )
    atmosphere_cue = selectors._choose_generic(data["setting_engine"]["atmosphere_cues"], rnd, previous.get("atmosphere_cue_id"), predicate=selectors._atmosphere_for_base_space(base_space, time_of_day))
    lighting_family = selectors._choose_generic(
        data["composition"]["lighting_families"],
        rnd,
        previous.get("lighting_family_id"),
        predicate=selectors._lighting_for_base_space(base_space, atmosphere_cue, time_of_day),
        preferred_predicate=selectors._style_preference_predicate(effective_profile, ids_key="preferred_lighting_ids", tags_key="preferred_lighting_tags"),
    )

    def surface_predicate(item: dict[str, Any]) -> bool:
        tags = set(item.get("tags", []))
        if "wet" in tags:
            return bool(scene_tags & selectors._wet_context_tags())
        if "wind" in tags:
            return bool(scene_tags & {"outdoor", "coastal", "rooftop"})
        return True

    surface_state = selectors._choose_generic(data["surface_states"]["surface_states"], rnd, previous.get("surface_state_id"), predicate=surface_predicate)
    banned_mood_ids = set(effective_profile.get("banned_mood_ids", []))
    mood_energy = selectors._choose_generic(
        data["composition"]["mood_energy"],
        rnd,
        previous.get("mood_energy_id"),
        predicate=(lambda item: item["id"] not in banned_mood_ids) if banned_mood_ids else None,
        preferred_predicate=selectors._style_preference_predicate(effective_profile, ids_key="preferred_mood_ids", tags_key="preferred_mood_tags"),
    )
    line_bank_expression = None
    if mode == "women":
        line_expression_records = line_bank_loader.records_for_level(
            data.get("line_banks", {}),
            gender="women",
            domain="expressions",
            spicy_level=spicy_level,
        )
        if line_expression_records:
            line_bank_expression = selectors._choose_generic(
                line_expression_records,
                rnd,
                previous.get("line_bank_expression_id"),
            )
    capture_style = selectors._choose_generic(
        data["composition"]["capture_styles"],
        rnd,
        previous.get("capture_style_id"),
        predicate=selectors._capture_style_for_candidate(base_space, outfit_family),
        preferred_predicate=selectors._style_preference_predicate(effective_profile, ids_key="preferred_capture_ids", tags_key="preferred_capture_tags"),
    )
    lens_look = selectors._choose_generic(data["composition"]["lens_looks"], rnd, previous.get("lens_look_id"))
    prop_cluster = detail_accent
    setting_scene = selectors._compose_setting_scene(base_space, setting_material, detail_accent, atmosphere_cue)
    setting_scene_id = f'{base_space["id"]}__{setting_material["id"]}__{detail_accent["id"]}__{atmosphere_cue["id"]}'
    tags = sorted({*setting_macro.get("tags", []), *scene_tags, *setting_material.get("tags", []), *detail_accent.get("tags", []), *atmosphere_cue.get("tags", []), *outfit_family.get("tags", []), *material.get("tags", []), *lighting_family.get("tags", []), *surface_state.get("tags", []), *ethnicity.get("tags", []), *capture_style.get("tags", []), *camera_framing.get("tags", [])})
    candidate = {
        "route": selectors._infer_route(
            base_space,
            outfit_family,
            pose_family,
            lighting_family,
            data["routes"],
            required_route_ids=set(profile.get("required_route_ids", [])),
            preferred_route_ids=set(profile.get("preferred_route_ids", [])),
        ),
        "age_band_id": age_band["id"],
        "age_band": age_band["value"],
        "breast_size_id": breast_size["id"],
        "breast_size": breast_size["value"],
        "ethnicity_id": ethnicity["id"],
        "ethnicity_group": ethnicity["group"],
        "ethnicity": ethnicity["value"],
        "body_type_id": body_type["id"],
        "body_group": body_type["group"],
        "body_type": body_type["value"],
        "beauty_level_id": beauty_level["id"],
        "beauty_level": beauty_level["value"],
        "hair_color_id": hair_color["id"],
        "hair_color_tags": hair_color.get("tags", []),
        "hair_color": hair_color["value"],
        "eye_color_id": eye_color["id"],
        "eye_color": eye_color["value"],
        "hair_structure_id": hair_structure["id"],
        "hair_structure": hair_structure["value"],
        "makeup_style_id": makeup_style["id"],
        "makeup_style": makeup_style["value"],
        "outfit_family_id": outfit_family["id"],
        "outfit_family": outfit_family["value"],
        "line_bank_outfit_id": line_bank_outfit["id"] if line_bank_outfit is not None else "",
        "line_bank_outfit": line_bank_outfit["value"] if line_bank_outfit is not None else "",
        "material_id": material["id"],
        "material": material["value"],
        "color_story_id": color_story["id"],
        "color_story": color_story["value"],
        "scene_family_id": scene_family_id,
        "setting_macro_id": setting_macro["id"],
        "setting_macro": setting_macro["value"],
        "setting_micro_id": base_space["id"],
        "setting_micro": base_space["value"],
        "line_bank_location_id": line_bank_location["id"] if line_bank_location is not None else "",
        "line_bank_location": line_bank_location["value"] if line_bank_location is not None else "",
        "setting_material_id": setting_material["id"],
        "setting_material": setting_material["value"],
        "detail_accent_id": detail_accent["id"],
        "detail_accent": detail_accent["value"],
        "atmosphere_cue_id": atmosphere_cue["id"],
        "atmosphere_cue": atmosphere_cue["value"],
        "setting_scene_id": setting_scene_id,
        "setting_scene": setting_scene,
        "prop_cluster_id": prop_cluster["id"],
        "prop_cluster": prop_cluster["value"],
        "pose_family_id": pose_family["id"],
        "pose_family": pose_family["value"],
        "pose_render": line_bank_pose["value"] if line_bank_pose is not None else pose_family["value"],
        "line_bank_pose_id": line_bank_pose["id"] if line_bank_pose is not None else "",
        "line_bank_pose": line_bank_pose["value"] if line_bank_pose is not None else "",
        "hand_action_id": hand_action["id"],
        "hand_action": hand_action["value"],
        "camera_framing_id": camera_framing["id"],
        "camera_framing": camera_framing["value"],
        "camera_angle_id": camera_angle["id"],
        "camera_angle": camera_angle["value"],
        "lighting_family_id": lighting_family["id"],
        "lighting_family": lighting_family["value"],
        "time_of_day_id": time_of_day["id"],
        "time_of_day": time_of_day["value"],
        "surface_state_id": surface_state["id"],
        "surface_state": surface_state["value"],
        "mood_energy_id": mood_energy["id"],
        "mood_energy": mood_energy["value"],
        "line_bank_expression_id": line_bank_expression["id"] if line_bank_expression is not None else "",
        "line_bank_expression": line_bank_expression["value"] if line_bank_expression is not None else "",
        "capture_style_id": capture_style["id"],
        "capture_style": capture_style["value"],
        "photo_treatment_id": photo_treatment["id"],
        "photo_treatment": photo_treatment.get("label", photo_treatment["id"]),
        "photo_treatment_category": photo_treatment.get("category", "stylized"),
        "capture_style_render": photo_treatment.get("capture_render", capture_style["value"]),
        "lighting_render": photo_treatment.get("lighting_render", lighting_family["value"]),
        "camera_vibe": photo_treatment.get("camera_vibe", ""),
        "color_grade": photo_treatment.get("color_grade", ""),
        "finish_render": photo_treatment.get("finish", "natural skin texture"),
        "lens_look_id": lens_look["id"],
        "lens_look": lens_look["value"],
        "tags": tags,
    }
    findings = validate_candidate(candidate, rules)
    repaired = repair_candidate(candidate, findings, rules) if findings else candidate
    normalized = selectors._normalize_candidate(data, repaired, style_mode=style_mode)
    repaired_findings = validate_candidate(normalized, rules)
    if any(item["type"] == "hard_conflict" for item in repaired_findings):
        raise ValueError("Candidate still invalid after repair.")
    if selectors._violates_recent_rules(normalized, recent_batch, rules["anti_repeat"]):
        raise ValueError("Candidate rejected by recent anti-repeat rules.")
    return normalized


def generate_batch(
    count: int,
    seed: int = 42,
    identity_lock: bool = False,
    persist_memory: bool = True,
    use_recent_batch_rules: bool = True,
    use_memory_rules: bool = True,
    style_mode: str = "random",
    ethnicity_group_override: str | None = None,
    preferred_ethnicity_ids: set[str] | None = None,
    ethnicity_id_pool: set[str] | None = None,
    user_profile: dict[str, Any] | None = None,
    mode: str = "women",
    spicy_level: int | None = None,
    photo_type_control: str = "balanced",
) -> list[dict[str, Any]]:
    data = data_loader.load_data_bank()
    rules = load_rule_bank()
    batch_rules = rules["batch_balance"]
    profile = selectors._merged_profile(selectors._style_profile(style_mode), user_profile)
    required_scene_families = set(profile.get("required_scene_families", []))
    preferred_scene_families = set(profile.get("preferred_scene_families", []))
    required_breast_size_ids = set(profile.get("required_breast_size_ids", []))
    rnd = random.Random(seed)
    ethnicity_id_schedule: list[str] = []
    if ethnicity_id_pool:
        ethnicity_lookup = {item["id"]: item for item in data["subjects"]["ethnicities"]}
        ethnicity_ids = [item_id for item_id in sorted(ethnicity_id_pool) if item_id in ethnicity_lookup]
        if not ethnicity_ids:
            raise ValueError("No selectable ethnicity ids for the requested race preset.")
        while len(ethnicity_id_schedule) < count:
            wave = list(ethnicity_ids)
            rnd.shuffle(wave)
            ethnicity_id_schedule.extend(wave)
        ethnicity_id_schedule = ethnicity_id_schedule[:count]
        ethnicity_schedule = [ethnicity_lookup[item_id]["group"] for item_id in ethnicity_id_schedule]
    elif ethnicity_group_override:
        ethnicity_schedule = [ethnicity_group_override] * count
    else:
        ethnicity_counts = selectors._allocate_counts(count, batch_rules["ethnicity_target_share"])
        ethnicity_schedule = selectors._build_group_schedule(ethnicity_counts, batch_rules["ethnicity_sequence"]["max_same_group_in_a_row"], rnd)
    body_counts = selectors._allocate_counts(count, profile.get("body_group_target_share", batch_rules["body_group_target_share"]))
    body_schedule = selectors._build_group_schedule(body_counts, batch_rules["body_sequence"]["max_same_group_in_a_row"], rnd)
    breast_size_target_share = profile.get("breast_size_target_share") if not required_breast_size_ids else None
    breast_size_schedule: list[str] = []
    if breast_size_target_share:
        breast_size_counts = selectors._allocate_counts(count, breast_size_target_share)
        breast_size_schedule = selectors._build_group_schedule(breast_size_counts, 1, rnd)
    pose_group_counts = selectors._allocate_counts(count, batch_rules["pose_group_target_share"])
    pose_group_schedule = selectors._build_group_schedule(pose_group_counts, batch_rules["pose_group_sequence"]["max_same_group_in_a_row"], rnd)
    framing_group_counts = selectors._allocate_counts(count, profile.get("framing_group_target_share", batch_rules["framing_group_target_share"]))
    framing_group_schedule = selectors._build_group_schedule(framing_group_counts, batch_rules["framing_group_sequence"]["max_same_group_in_a_row"], rnd)
    photo_type_control = str(photo_type_control or "balanced")
    random_balance_enabled = (
        style_mode == "random"
        and photo_type_control == "balanced"
        and not required_scene_families
    )
    random_scene_schedule, random_bright_schedule = (
        _build_random_balance_schedules(count, rnd) if random_balance_enabled else ([""] * count, [False] * count)
    )
    large_batch = count >= 24
    large_random_balance_batch = large_batch and random_balance_enabled
    vivid_quota = count // 10
    vivid_positions = selectors._spaced_positions(count, vivid_quota)
    max_30_plus = 1 if batch_rules.get("age_rules", {}).get("deprioritize_30_plus") else count
    scene_family_rules = batch_rules.get("scene_family_rules", {})
    setting_micro_rules = batch_rules.get("setting_micro_rules", {})
    max_same_setting_micro_per_batch = setting_micro_rules.get("max_same_per_batch", count)
    avoid_recent_memory_count = setting_micro_rules.get("avoid_recent_memory_count", 0)
    avoid_recent_setting_micros = _recent_memory_set(data["memory"], "setting_base_spaces", avoid_recent_memory_count) if use_memory_rules else set()
    constrained_scene_batch = large_batch and bool(required_scene_families or profile.get("exact_theme_location_keywords"))
    batch: list[dict[str, Any]] = []
    previous: dict[str, str] = {}
    scene_family_counts: dict[str, int] = {}
    setting_micro_counts: dict[str, int] = {}
    identity_core: dict[str, dict[str, Any]] | None = None
    if identity_lock:
        core_vivid = 0 in vivid_positions
        required_age_band_ids = set(profile.get("required_age_band_ids", []))
        required_body_groups = set(profile.get("required_body_groups", []))
        required_hair_ids = set(profile.get("required_hair_ids", []))
        required_breast_size_ids = set(profile.get("required_breast_size_ids", []))
        required_eye_color_ids = set(profile.get("required_eye_color_ids", []))
        required_ethnicity_ids = set(profile.get("required_ethnicity_ids", []))
        breast_size = selectors._choose_generic(data["subjects"]["breast_sizes"], rnd, None, predicate=(lambda item: item["id"] in required_breast_size_ids) if required_breast_size_ids else None)
        age_predicate = (lambda item: item["id"] in required_age_band_ids) if required_age_band_ids else selectors._age_predicate(batch_rules, breast_size["id"], core_vivid)
        age_band = selectors._choose_generic(data["subjects"]["age_bands"], rnd, None, predicate=age_predicate)
        identity_core = {
            "breast_size": breast_size,
            "age_band": age_band,
            "ethnicity": selectors._choose_generic(
                data["subjects"]["ethnicities"],
                rnd,
                None,
                predicate=lambda item: item.get("weight", 0.0) > 0 and (item["id"] in required_ethnicity_ids if required_ethnicity_ids else (not ethnicity_group_override or item.get("group") == ethnicity_group_override)),
                preferred_predicate=(lambda item: item["id"] in ((preferred_ethnicity_ids or set()) | required_ethnicity_ids)) if (preferred_ethnicity_ids or required_ethnicity_ids) else None,
            ),
            "body_type": selectors._choose_generic(data["subjects"]["body_types"], rnd, None, predicate=(lambda item: item.get("group") in required_body_groups) if required_body_groups else None),
            "beauty_level": selectors._choose_generic(data["subjects"]["beauty_levels"], rnd, None),
        }
        identity_core["hair_color"] = selectors._choose_hair_color(
            data["styling"]["hair_colors"],
            rnd,
            identity_core["age_band"]["id"],
            core_vivid,
            identity_core["ethnicity"]["group"],
            None,
            required_ids=set(profile.get("required_hair_color_ids", [])),
            preferred_ids=set(profile.get("preferred_hair_color_ids", [])),
            allow_dyed_natural=bool(profile.get("allow_dyed_natural_hair_colors", False)),
        )
        identity_core["hair_structure"] = selectors._choose_generic(
            data["styling"]["hair_structures"],
            rnd,
            None,
            predicate=(lambda item: item["id"] in required_hair_ids) if required_hair_ids else None,
            preferred_predicate=selectors._style_preference_predicate(profile, ids_key="preferred_hair_ids", tags_key="preferred_hair_tags"),
        )
        identity_core["makeup_style"] = selectors._choose_generic(data["styling"]["makeup_styles"], rnd, None, preferred_predicate=selectors._style_preference_predicate(profile, ids_key="preferred_makeup_ids", tags_key="preferred_makeup_tags"))
        identity_core["eye_color"] = selectors._choose_generic(
            data["subjects"]["eye_colors"],
            rnd,
            None,
            predicate=(lambda item: item["id"] in required_eye_color_ids) if required_eye_color_ids else None,
            preferred_predicate=selectors._style_preference_predicate(profile, ids_key="preferred_eye_color_ids", tags_key="preferred_eye_color_tags"),
        )
    for idx in range(count):
        candidate = None
        retry_plan = [
            {
                "tries": 20 if constrained_scene_batch else 40 if large_random_balance_batch else 80,
                "recent_batch": (batch[-1:] if constrained_scene_batch else batch[-2:] if large_random_balance_batch else batch) if use_recent_batch_rules else [],
                "avoid_setting_micro_ids": avoid_recent_setting_micros,
                "setting_cap": max_same_setting_micro_per_batch,
                "previous": previous,
                "enforce_random_balance": False if large_random_balance_batch else random_balance_enabled,
            }
        ]
        if required_scene_families and not identity_lock:
            retry_plan.append({"tries": 100, "recent_batch": batch[-1:], "avoid_setting_micro_ids": avoid_recent_setting_micros, "setting_cap": max(3, max_same_setting_micro_per_batch), "previous": previous, "enforce_random_balance": False})
            retry_plan.append({"tries": 140, "recent_batch": [], "avoid_setting_micro_ids": set(), "setting_cap": max(6, max_same_setting_micro_per_batch), "previous": {}, "enforce_random_balance": False})
        if not identity_lock:
            retry_plan.append({"tries": 120, "recent_batch": batch[-2:] if use_recent_batch_rules else [], "avoid_setting_micro_ids": set(), "setting_cap": max(3, max_same_setting_micro_per_batch), "previous": previous, "enforce_random_balance": random_balance_enabled})
            retry_plan.append({"tries": 180, "recent_batch": [], "avoid_setting_micro_ids": set(), "setting_cap": max(5, max_same_setting_micro_per_batch), "previous": {}, "enforce_random_balance": random_balance_enabled})
        if identity_lock:
            retry_plan.append({"tries": 120, "recent_batch": batch[-2:], "avoid_setting_micro_ids": set(), "setting_cap": max(3, max_same_setting_micro_per_batch), "previous": previous, "enforce_random_balance": random_balance_enabled})
            retry_plan.append({"tries": 160, "recent_batch": [], "avoid_setting_micro_ids": set(), "setting_cap": max(4, max_same_setting_micro_per_batch), "previous": {}, "enforce_random_balance": random_balance_enabled})
        for retry_stage in retry_plan:
            for _ in range(retry_stage["tries"]):
                try:
                    candidate_profile = user_profile
                    candidate_preferred_ethnicity_ids = preferred_ethnicity_ids
                    if ethnicity_id_schedule:
                        ethnicity_id = ethnicity_id_schedule[idx]
                        candidate_profile = dict(user_profile or {})
                        candidate_profile["required_ethnicity_ids"] = {ethnicity_id}
                        candidate_profile["preferred_ethnicity_ids"] = {ethnicity_id}
                        candidate_preferred_ethnicity_ids = {ethnicity_id}
                    candidate = build_candidate(
                        data=data,
                        rules=rules,
                        rnd=rnd,
                        ethnicity_group=identity_core["ethnicity"]["group"] if identity_lock else ethnicity_schedule[idx],
                        body_group=identity_core["body_type"]["group"] if identity_lock else body_schedule[idx],
                        breast_size_id=breast_size_schedule[idx] if breast_size_schedule else None,
                        pose_group=pose_group_schedule[idx],
                        framing_group=framing_group_schedule[idx],
                        vivid_hair=idx in vivid_positions,
                        identity_core=identity_core,
                        recent_batch=retry_stage["recent_batch"],
                        previous=retry_stage["previous"],
                        avoid_setting_micro_ids=retry_stage["avoid_setting_micro_ids"],
                        scene_family_counts=scene_family_counts,
                        style_mode=style_mode,
                        preferred_ethnicity_ids=candidate_preferred_ethnicity_ids,
                        user_profile=candidate_profile,
                        mode=mode,
                        spicy_level=spicy_level,
                        random_scene_group_override=random_scene_schedule[idx] if retry_stage.get("enforce_random_balance") else None,
                    )
                    if selectors._is_30_plus(candidate["age_band_id"]) and sum(selectors._is_30_plus(item["age_band_id"]) for item in batch) >= max_30_plus:
                        raise ValueError("Too many 30+ candidates for this batch.")
                    family_share = scene_family_rules.get("target_share", {}).get(candidate["scene_family_id"], 0.05)
                    family_cap = max(1, math.ceil(count * family_share) + scene_family_rules.get("cap_slack", 1))
                    if candidate["scene_family_id"] in preferred_scene_families:
                        family_cap = count
                    if scene_family_counts.get(candidate["scene_family_id"], 0) >= family_cap:
                        raise ValueError("Scene family over batch cap.")
                    if setting_micro_counts.get(candidate["setting_micro_id"], 0) >= _setting_micro_cap(candidate["setting_micro_id"], setting_micro_rules, retry_stage["setting_cap"]):
                        raise ValueError("Setting micro over batch cap.")
                    if retry_stage.get("enforce_random_balance"):
                        if not _random_scene_group_matches(candidate, random_scene_schedule[idx]):
                            raise ValueError("Random indoor/outdoor balance target missed.")
                        if random_bright_schedule[idx] and not _is_random_bright_candidate(candidate):
                            raise ValueError("Random bright-light target missed.")
                        if not random_bright_schedule[idx] and _is_random_bright_candidate(candidate):
                            raise ValueError("Random muted-light target missed.")
                    break
                except ValueError:
                    continue
            if candidate is not None:
                break
        if candidate is None:
            raise ValueError(f"Could not generate a non-repeating candidate for batch index {idx}.")
        batch.append(candidate)
        scene_family_counts[candidate["scene_family_id"]] = scene_family_counts.get(candidate["scene_family_id"], 0) + 1
        setting_micro_counts[candidate["setting_micro_id"]] = setting_micro_counts.get(candidate["setting_micro_id"], 0) + 1
        previous = {
            "age_band_id": candidate["age_band_id"],
            "breast_size_id": candidate["breast_size_id"],
            "ethnicity_id": candidate["ethnicity_id"],
            "body_type_id": candidate["body_type_id"],
            "hair_color_id": candidate["hair_color_id"],
            "hair_structure_id": candidate["hair_structure_id"],
            "makeup_style_id": candidate["makeup_style_id"],
            "outfit_family_id": candidate["outfit_family_id"],
            "line_bank_outfit_id": candidate.get("line_bank_outfit_id", ""),
            "material_id": candidate["material_id"],
            "color_story_id": candidate["color_story_id"],
            "scene_family_id": candidate["scene_family_id"],
            "setting_macro_id": candidate["setting_macro_id"],
            "setting_micro_id": candidate["setting_micro_id"],
            "setting_material_id": candidate["setting_material_id"],
            "detail_accent_id": candidate["detail_accent_id"],
            "atmosphere_cue_id": candidate["atmosphere_cue_id"],
            "prop_cluster_id": candidate["prop_cluster_id"],
            "pose_family_id": candidate["pose_family_id"],
            "line_bank_pose_id": candidate.get("line_bank_pose_id", ""),
            "hand_action_id": candidate["hand_action_id"],
            "camera_framing_id": candidate["camera_framing_id"],
            "camera_angle_id": candidate["camera_angle_id"],
            "lighting_family_id": candidate["lighting_family_id"],
            "time_of_day_id": candidate["time_of_day_id"],
            "surface_state_id": candidate["surface_state_id"],
            "mood_energy_id": candidate["mood_energy_id"],
            "line_bank_expression_id": candidate.get("line_bank_expression_id", ""),
            "capture_style_id": candidate["capture_style_id"],
            "lens_look_id": candidate["lens_look_id"],
        }
    if persist_memory:
        persist_batch_memory(batch)
    return batch


def generate_candidate(seed: int = 42) -> tuple[dict[str, Any], list[dict[str, str]], dict[str, Any]]:
    data = data_loader.load_data_bank()
    candidate = generate_batch(1, seed=seed)[0]
    findings = validate_candidate(candidate)
    repaired = repair_candidate(candidate, findings, load_rule_bank()) if findings else candidate
    repaired = selectors._normalize_candidate(data, repaired)
    return candidate, findings, repaired
