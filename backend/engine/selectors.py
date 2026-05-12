from __future__ import annotations

from functools import lru_cache
import math
import random
from typing import Any

from backend.photo_treatment_mix import (
    WOMEN_RANDOM_TREATMENT_MIX_TARGETS,
    photo_treatment_mix_bucket,
    photo_treatment_quality_tier,
    photo_treatment_tone,
)

from . import data_loader


STYLE_PROFILES: dict[str, dict[str, Any]] = {
    "studio": {
        "preferred_scene_families": {"studio"},
        "preferred_outfit_ids": {"mini_dress", "crop_top_mini_skirt", "latex_editorial"},
        "preferred_pose_tags": {"standing", "seated", "editorial"},
        "preferred_lighting_ids": {"studio_rim"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo"},
        "preferred_route_ids": {"studio_portrait"},
    },
    "lifestyle": {
        "preferred_scene_families": {"urban_daylight", "culture_bookish", "garden_conservatory"},
        "preferred_outfit_ids": {"mini_dress", "cardigan_trousers", "blouse_trousers", "knit_top_trousers", "sweater_jeans", "shirt_trousers"},
        "preferred_capture_ids": {"lifestyle_photo", "smartphone_photo"},
        "preferred_makeup_ids": {"natural_pretty", "soft_glam_clean"},
        "preferred_pose_tags": {"standing", "movement", "seated"},
    },
    "luxury": {
        "preferred_scene_families": {"residential_luxury", "hospitality_suite", "grooming_bath"},
        "preferred_outfit_ids": {"mini_dress", "cardigan_trousers", "blouse_trousers", "knit_top_trousers", "shirt_trousers"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo"},
        "preferred_route_ids": {"luxury_interior"},
    },
    "old_money": {
        "preferred_scene_families": {"residential_luxury", "culture_bookish", "garden_conservatory", "hospitality_suite"},
        "preferred_outfit_ids": {"cardigan_skirt", "cardigan_trousers", "blouse_trousers", "knit_top_trousers", "shirt_trousers"},
        "preferred_makeup_ids": {"soft_glam_clean", "natural_pretty"},
        "preferred_capture_ids": {"editorial_photo", "lifestyle_photo"},
    },
    "romantic": {
        "preferred_scene_families": {"courtyard_garden", "garden_conservatory", "coastal_pool"},
        "preferred_outfit_ids": {"mini_dress", "crop_top_mini_skirt", "cardigan_skirt"},
        "preferred_hair_ids": {"soft_waves", "side_braid"},
        "preferred_makeup_ids": {"natural_pretty", "soft_glam_clean"},
        "preferred_capture_ids": {"lifestyle_photo", "editorial_photo"},
        "preferred_lighting_ids": {"soft_overcast", "clean_daylight"},
    },
    "vacation": {
        "preferred_scene_families": {"coastal_pool", "coastal_boardwalk", "hospitality_suite", "wellness_spa"},
        "preferred_outfit_ids": {"swimsuit", "bikini_set", "crop_top_mini_skirt"},
        "preferred_capture_ids": {"lifestyle_photo", "fashion_photo"},
        "preferred_lighting_ids": {"clean_daylight", "soft_overcast"},
    },
    "sport": {
        "preferred_scene_families": {"urban_daylight", "courtyard_garden", "coastal_boardwalk"},
        "preferred_outfit_ids": {"workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"},
        "preferred_material_ids": {"athletic_jersey"},
        "preferred_color_story_ids": {"sport_clean_white", "black_ivory", "red_ivory", "coral_ivory", "olive_sand", "terracotta_sand"},
        "preferred_hair_ids": {"high_ponytail", "side_braid", "soft_half_up", "long_straight"},
        "preferred_makeup_ids": {"natural_pretty", "soft_glam_clean"},
        "preferred_pose_tags": {"standing", "movement"},
        "preferred_lighting_ids": {"clean_daylight"},
        "preferred_capture_ids": {"fashion_photo", "lifestyle_photo"},
        "preferred_route_ids": {"sports_flirt"},
    },
    "fitness": {
        "preferred_scene_families": {"urban_daylight", "courtyard_garden", "coastal_boardwalk"},
        "preferred_outfit_ids": {"workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers", "zip_front_training_set", "cross_strap_keyhole_active_set"},
        "preferred_material_ids": {"athletic_jersey"},
        "preferred_color_story_ids": {"sport_clean_white", "black_ivory", "red_ivory", "coral_ivory", "sage_stone", "olive_sand", "terracotta_sand", "mint_cream", "plum_blush"},
        "preferred_hair_ids": {"high_ponytail", "side_braid", "soft_half_up", "long_straight", "soft_waves"},
        "preferred_makeup_ids": {"natural_pretty", "soft_glam_clean"},
        "preferred_pose_tags": {"standing", "movement"},
        "preferred_lighting_ids": {"clean_daylight"},
        "preferred_capture_ids": {"fashion_photo", "lifestyle_photo"},
        "preferred_route_ids": {"sports_flirt"},
    },
    "cosplay": {
        "preferred_scene_families": {"studio", "nightlife_neon"},
        "preferred_outfit_ids": {"latex_editorial", "mini_dress"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo"},
        "preferred_lighting_ids": {"studio_rim", "neon_night"},
        "preferred_route_ids": {"fantasy_cosplay"},
    },
    "fantasy": {
        "preferred_scene_families": {"studio", "nightlife_neon"},
        "preferred_outfit_ids": {"latex_editorial", "mini_dress"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo"},
        "preferred_lighting_ids": {"studio_rim", "neon_night"},
        "preferred_route_ids": {"fantasy_cosplay"},
    },
    "nightlife": {
        "preferred_scene_families": {"nightlife_bar", "nightlife_neon"},
        "preferred_outfit_ids": {"mini_dress", "latex_editorial"},
        "preferred_makeup_ids": {"night_out_glam"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo"},
        "preferred_lighting_ids": {"neon_night", "warm_interior"},
        "preferred_time_ids": {"night"},
        "preferred_route_ids": {"cinematic_night"},
    },
    "cultural_bookish": {
        "preferred_scene_families": {"culture_bookish"},
        "preferred_outfit_ids": {"cardigan_skirt", "cardigan_trousers", "knit_top_trousers", "blouse_trousers", "shirt_trousers"},
        "preferred_capture_ids": {"lifestyle_photo", "editorial_photo"},
        "preferred_makeup_ids": {"natural_pretty", "soft_glam_clean"},
    },
    "creative_artistic": {
        "preferred_scene_families": {"creative_gallery"},
        "preferred_outfit_ids": {"mini_dress", "crop_top_mini_skirt", "latex_editorial"},
        "preferred_capture_ids": {"editorial_photo", "fashion_photo", "lifestyle_photo"},
    },
    "urban_day": {
        "preferred_scene_families": {"urban_daylight"},
        "preferred_outfit_ids": {"mini_dress", "cardigan_trousers", "blouse_trousers", "sweater_jeans", "shirt_trousers"},
        "preferred_capture_ids": {"lifestyle_photo", "smartphone_photo", "fashion_photo"},
        "preferred_lighting_ids": {"clean_daylight", "soft_overcast"},
        "banned_scene_families": {"nightlife_bar", "nightlife_neon", "studio"},
    },
    "coastal": {
        "preferred_scene_families": {"coastal_pool", "coastal_boardwalk"},
        "preferred_outfit_ids": {"swimsuit", "bikini_set", "mini_dress"},
        "preferred_capture_ids": {"lifestyle_photo", "fashion_photo", "editorial_photo"},
        "preferred_lighting_ids": {"clean_daylight", "soft_overcast"},
    },
}


def _weighted_pick(items: list[dict[str, Any]], rnd: random.Random) -> dict[str, Any]:
    weights = [max(item.get("weight", 0.0), 0.0) for item in items]
    total = sum(weights)
    if total <= 0:
        raise ValueError("No selectable items: all weights are zero.")
    return rnd.choices(items, weights=weights, k=1)[0]


def _weighted_pick_filtered(
    items: list[dict[str, Any]],
    rnd: random.Random,
    predicate: Any | None = None,
    avoid_id: str | None = None,
    avoid_ids: set[str] | None = None,
    preferred_predicate: Any | None = None,
) -> dict[str, Any]:
    filtered = [item for item in items if item.get("weight", 0.0) > 0]
    if predicate is not None:
        filtered = [item for item in filtered if predicate(item)]
    if preferred_predicate is not None:
        preferred = [item for item in filtered if preferred_predicate(item)]
        if preferred:
            filtered = preferred
    if avoid_ids:
        preferred = [item for item in filtered if item["id"] not in avoid_ids]
        if preferred:
            filtered = preferred
    if avoid_id is not None:
        preferred = [item for item in filtered if item["id"] != avoid_id]
        if preferred:
            filtered = preferred
    return _weighted_pick(filtered, rnd)


def _style_profile(style_mode: str | None) -> dict[str, Any]:
    if not style_mode:
        return {}
    return STYLE_PROFILES.get(style_mode, {})


def _merged_profile(base_profile: dict[str, Any], user_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    merged: dict[str, Any] = {key: (set(value) if isinstance(value, set) else value) for key, value in base_profile.items()}
    union_keys = {
        "preferred_scene_families",
        "banned_scene_families",
        "banned_outfit_ids",
        "banned_hair_ids",
        "banned_mood_ids",
        "preferred_route_ids",
        "preferred_capture_ids",
        "preferred_lighting_ids",
        "preferred_time_ids",
        "preferred_color_story_ids",
        "preferred_material_ids",
        "preferred_hair_ids",
        "preferred_eye_color_ids",
        "preferred_makeup_ids",
        "preferred_pose_tags",
        "preferred_pose_ids",
        "preferred_framing_ids",
        "preferred_framing_tags",
        "preferred_hand_action_ids",
        "preferred_mood_ids",
    }
    for key, value in (user_profile or {}).items():
        if isinstance(value, set):
            if key in union_keys and isinstance(merged.get(key), set):
                merged[key] = set(merged[key]) | set(value)
            else:
                merged[key] = set(value)
        else:
            merged[key] = value
    return merged


def _profile_value_set(profile: dict[str, Any], key: str) -> set[str]:
    return {str(value) for value in profile.get(key, []) if str(value).strip()}


def _photo_treatment_profile(profile: dict[str, Any] | None) -> dict[str, Any]:
    if not profile:
        return {}
    mapped: dict[str, Any] = {}
    for key in (
        "preferred_scene_families",
        "banned_scene_families",
        "preferred_route_ids",
        "preferred_capture_ids",
        "preferred_lighting_ids",
        "preferred_time_ids",
        "preferred_pose_ids",
        "preferred_pose_tags",
        "preferred_framing_ids",
        "preferred_framing_tags",
        "preferred_mood_ids",
        "preferred_color_story_ids",
        "preferred_material_ids",
        "preferred_makeup_ids",
        "preferred_hair_ids",
        "preferred_eye_color_ids",
    ):
        values = _profile_value_set(profile, key)
        if values:
            mapped[key] = values
    return mapped


def _style_preference_predicate(
    profile: dict[str, Any],
    *,
    ids_key: str | None = None,
    tags_key: str | None = None,
    field_name: str = "id",
) -> Any | None:
    preferred_ids = set(profile.get(ids_key or "", [])) if ids_key else set()
    preferred_tags = set(profile.get(tags_key or "", [])) if tags_key else set()
    if not preferred_ids and not preferred_tags:
        return None

    def predicate(item: dict[str, Any]) -> bool:
        if preferred_ids and item.get(field_name) in preferred_ids:
            return True
        if preferred_tags and preferred_tags & set(item.get("tags", [])):
            return True
        return False

    return predicate


def _infer_route(
    base_space: dict[str, Any],
    outfit_family: dict[str, Any],
    pose_family: dict[str, Any],
    lighting_family: dict[str, Any],
    routes_bank: dict[str, Any],
    required_route_ids: set[str] | None = None,
    preferred_route_ids: set[str] | None = None,
) -> str:
    required_route_ids = required_route_ids or set()
    preferred_route_ids = preferred_route_ids or set()
    route_candidates: list[tuple[int, str]] = []
    setting_tags = set(base_space.get("tags", []))
    outfit_tags = set(outfit_family.get("tags", []))
    pose_tags = set(pose_family.get("tags", []))
    light_tags = set(lighting_family.get("tags", []))
    combined_tags = setting_tags | outfit_tags | pose_tags | light_tags

    for route in routes_bank.get("routes", []):
        route_id = route["id"]
        if required_route_ids and route_id not in required_route_ids:
            continue
        banned = set(route.get("banned_tags", []))
        if banned & combined_tags:
            continue
        score = 0
        if set(route.get("allowed_setting_tags", [])) & setting_tags:
            score += 3
        if set(route.get("allowed_outfit_tags", [])) & outfit_tags:
            score += 3
        if set(route.get("allowed_pose_tags", [])) & pose_tags:
            score += 2
        if set(route.get("allowed_light_tags", [])) & light_tags:
            score += 2
        if route_id in preferred_route_ids:
            score += 5
        min_score = 4 if required_route_ids else 6
        if score >= min_score:
            route_candidates.append((score, route_id))

    if not route_candidates:
        return "default"
    route_candidates.sort(reverse=True)
    return route_candidates[0][1]


def _allocate_counts(total: int, shares: dict[str, float]) -> dict[str, int]:
    raw = {key: total * value for key, value in shares.items()}
    counts = {key: math.floor(value) for key, value in raw.items()}
    remainder = total - sum(counts.values())
    leftovers = sorted(raw.items(), key=lambda item: item[1] - counts[item[0]], reverse=True)
    for key, _ in leftovers[:remainder]:
        counts[key] += 1
    return counts


def _build_group_schedule(counts: dict[str, int], max_same_in_row: int, rnd: random.Random) -> list[str]:
    remaining = counts.copy()
    sequence: list[str] = []
    while sum(remaining.values()) > 0:
        candidates = []
        for group, count in remaining.items():
            if count <= 0:
                continue
            if max_same_in_row == 1 and sequence and sequence[-1] == group:
                continue
            if max_same_in_row > 1 and len(sequence) >= max_same_in_row and all(x == group for x in sequence[-max_same_in_row:]):
                continue
            candidates.append((group, count))
        if not candidates:
            candidates = [(group, count) for group, count in remaining.items() if count > 0]
        max_count = max(count for _, count in candidates)
        strongest = [group for group, count in candidates if count == max_count]
        chosen = rnd.choice(strongest)
        sequence.append(chosen)
        remaining[chosen] -= 1
    return sequence


def _spaced_positions(count: int, quota: int) -> set[int]:
    if quota <= 0:
        return set()
    return {max(0, min(count - 1, round((idx + 1) * count / (quota + 1)) - 1)) for idx in range(quota)}


def _group_base_spaces_by_family(base_spaces: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in base_spaces:
        grouped.setdefault(item["scene_family_id"], []).append(item)
    return grouped


def _violates_recent_rules(
    candidate: dict[str, Any],
    recent_batch: list[dict[str, Any]],
    anti_repeat_rules: dict[str, Any],
) -> bool:
    if not recent_batch:
        return False
    window = anti_repeat_rules.get("recent_window", 3)
    recent = recent_batch[-window:]
    hard_ban_fields = anti_repeat_rules.get("recent_hard_ban_fields", [])
    similarity_fields = anti_repeat_rules.get("recent_similarity_fields", [])
    reject_at = anti_repeat_rules.get("recent_similarity_reject_at", 3)
    for prev in recent:
        for field in hard_ban_fields:
            if candidate.get(field) and candidate.get(field) == prev.get(field):
                return True
        score = 0
        for field in similarity_fields:
            if candidate.get(field) and candidate.get(field) == prev.get(field):
                score += 1
        if score >= reject_at:
            return True
    return False


def _choose_ethnicity(
    ethnicities: list[dict[str, Any]],
    group: str,
    rnd: random.Random,
    previous_id: str | None,
    preferred_ids: set[str] | None = None,
    required_ids: set[str] | None = None,
) -> dict[str, Any]:
    required_ids = required_ids or set()
    preferred_ids = (preferred_ids or set()) | required_ids
    return _weighted_pick_filtered(
        ethnicities,
        rnd,
        predicate=(lambda item: item["id"] in required_ids) if required_ids else (lambda item: item.get("group") == group),
        avoid_id=previous_id,
        preferred_predicate=(lambda item: item["id"] in preferred_ids) if preferred_ids else None,
    )


def _compose_predicates(*predicates: Any | None) -> Any | None:
    active = [predicate for predicate in predicates if predicate is not None]
    if not active:
        return None

    def predicate(item: dict[str, Any]) -> bool:
        return all(check(item) for check in active)

    return predicate


def _choose_body_type(
    body_types: list[dict[str, Any]],
    group: str,
    rnd: random.Random,
    previous_id: str | None,
    predicate: Any | None = None,
) -> dict[str, Any]:
    return _weighted_pick_filtered(
        body_types,
        rnd,
        predicate=_compose_predicates(
            lambda item: item.get("group") == group,
            predicate,
        ),
        avoid_id=previous_id,
    )


def _choose_hair_color(
    hair_colors: list[dict[str, Any]],
    rnd: random.Random,
    age_band_id: str,
    vivid_allowed: bool,
    ethnicity_group: str,
    previous_id: str | None,
    required_ids: set[str] | None = None,
    preferred_ids: set[str] | None = None,
    allow_dyed_natural: bool = False,
) -> dict[str, Any]:
    required_ids = required_ids or set()
    effective_avoid_id = previous_id
    if required_ids and previous_id in required_ids and len(required_ids) == 1:
        effective_avoid_id = None

    def predicate(item: dict[str, Any]) -> bool:
        tags = set(item.get("tags", []))
        requires = item.get("requires_age_bands", [])
        if requires and age_band_id not in requires:
            return False
        if required_ids and item["id"] not in required_ids:
            return False
        if required_ids and "vivid_colored_hair" in tags and not vivid_allowed:
            return False
        if required_ids and vivid_allowed and "vivid_colored_hair" not in tags:
            return False
        if not required_ids and "dyed_hair" in tags:
            if not allow_dyed_natural or item["id"] not in {"copper_dyed", "burgundy_dyed", "silver_dyed"}:
                return False
        if not required_ids and ethnicity_group == "black" and item["id"] == "copper_dyed":
            return False
        if not required_ids and ethnicity_group == "black" and item["id"] == "blonde_natural":
            return False
        return True

    return _weighted_pick_filtered(
        hair_colors,
        rnd,
        predicate=predicate,
        avoid_id=effective_avoid_id,
        preferred_predicate=(lambda item: item["id"] in preferred_ids) if preferred_ids else None,
    )


def _choose_generic(
    items: list[dict[str, Any]],
    rnd: random.Random,
    previous_id: str | None,
    predicate: Any | None = None,
    avoid_ids: set[str] | None = None,
    preferred_predicate: Any | None = None,
) -> dict[str, Any]:
    return _weighted_pick_filtered(
        items,
        rnd,
        predicate=predicate,
        avoid_id=previous_id,
        avoid_ids=avoid_ids,
        preferred_predicate=preferred_predicate,
    )


def _age_predicate(batch_rules: dict[str, Any], breast_size_id: str, vivid_hair: bool) -> Any | None:
    age_rules = batch_rules.get("age_rules", {})
    vivid_age_bands = set(batch_rules.get("vivid_colored_hair", {}).get("allowed_age_bands", []))
    big_age_bands = set(age_rules.get("big_breasts_age_bands", []))
    very_big_age_bands = set(age_rules.get("very_big_breasts_age_bands", []))
    gen_z_age_bands = set(age_rules.get("gen_z_age_bands", []))
    allowed: set[str] | None = None
    if breast_size_id == "big_breasts" and big_age_bands:
        allowed = set(big_age_bands)
    elif breast_size_id in {"very_big_breasts", "extra_large_breasts"} and very_big_age_bands:
        allowed = set(very_big_age_bands)
    if vivid_hair and vivid_age_bands:
        allowed = set(vivid_age_bands) if allowed is None else allowed & vivid_age_bands
    if vivid_hair and gen_z_age_bands:
        allowed = set(gen_z_age_bands) if allowed is None else allowed & gen_z_age_bands
    if not allowed:
        return None
    return lambda item: item["id"] in allowed


def _wet_context_tags() -> set[str]:
    return {"pool", "beach", "spa", "shower", "rain", "humid", "coastal", "wet_friendly"}


def _water_contact_scene_tags() -> set[str]:
    """Scenes where the subject is genuinely at or near water. Excludes dry coastal ambience (boardwalks, promenades)."""
    return {"pool", "beach", "spa", "shower", "rain", "humid", "wet_friendly"}


@lru_cache(maxsize=1024)
def _scene_support_tags_cached(setting_value: str) -> frozenset[str]:
    lowered = str(setting_value or "").strip().lower()
    support_tags: set[str] = set()
    if any(token in lowered for token in ("chair", "chairs", "stool", "stools", "bench", "banquette", "booth")):
        support_tags.add("chair_support")
    if any(token in lowered for token in ("sofa", "couch", "chaise", "ottoman", "lounger", "daybed", "day bed", "divan")):
        support_tags.add("sofa_support")
    if any(token in lowered for token in ("bed", "bedding", "headboard")):
        support_tags.add("bed_support")
    if any(token in lowered for token in ("stairs", "stair", "step", "steps")):
        support_tags.add("stairs_support")
    if any(token in lowered for token in ("counter", "island", "vanity", "worktop", "kitchen island", "prep island")):
        support_tags.add("counter_support")
    if any(token in lowered for token in ("mirror", "mirrored", "reflection", "triptych mirrors")):
        support_tags.add("mirror_support")
    if any(token in lowered for token in ("sink", "basin", "vanity", "washstand")):
        support_tags.add("sink_support")
    if any(token in lowered for token in ("cabinet", "cupboard", "wardrobe", "shelves", "pantry")):
        support_tags.add("cabinet_support")
    if any(token in lowered for token in ("floor", "ground", "mat", "deck", "patio", "sand", "grass")):
        support_tags.add("floor_support")
    if any(token in lowered for token in ("grass", "sand", "lawn", "meadow", "blanket", "mat", "daybed", "lounger", "poolside")):
        support_tags.add("soft_ground_support")
    return frozenset(support_tags)


def _scene_support_tags(base_space: dict[str, Any]) -> set[str]:
    return set(_scene_support_tags_cached(str(base_space.get("value", ""))))


@lru_cache(maxsize=1024)
def _scene_semantic_tags_cached(
    setting_value: str,
    scene_family_id: str,
    raw_tags: tuple[str, ...],
) -> frozenset[str]:
    tags = set(raw_tags)
    normalized = set(tags)
    normalized |= set(_scene_support_tags_cached(setting_value))
    if scene_family_id == "culture_bookish" or "bookish" in tags:
        normalized.add("bookish")
    if tags & {"night", "nightlife", "bar", "neon"} or scene_family_id in {"nightlife_bar", "nightlife_neon"}:
        normalized.add("night")
    if tags & {"social", "lounge", "club", "bar", "nightlife", "public_elegant"} or scene_family_id in {"nightlife_bar", "nightlife_neon"}:
        normalized.add("social")
    if tags & {"luxury", "hotelized_living", "quiet_luxury"}:
        normalized.add("quiet_luxury")
    if scene_family_id in {"residential_luxury", "hospitality_suite", "grooming_bath", "wellness_spa"} and "night" not in normalized:
        normalized.add("quiet_luxury")
    return frozenset(normalized)


def _scene_semantic_tags(base_space: dict[str, Any]) -> set[str]:
    raw_tags = tuple(sorted(str(tag) for tag in base_space.get("tags", [])))
    return set(
        _scene_semantic_tags_cached(
            str(base_space.get("value", "")),
            str(base_space.get("scene_family_id", "")),
            raw_tags,
        )
    )


def _public_elegant_scene(tags: set[str]) -> bool:
    if tags & {"public_elegant", "travel", "stairs", "modest_safe"}:
        return True
    if tags & {"social", "lounge", "day_to_night"} and "night" not in tags:
        return True
    return False


def _wellness_scene(tags: set[str]) -> bool:
    return bool(tags & {"sporty", "wellness"})


def _active_scene(tags: set[str]) -> bool:
    return bool(tags & {"sporty", "active"})


def _nightlife_forward_outfit(outfit_tags: set[str]) -> bool:
    return bool(outfit_tags & {"clubwear", "pushing_it", "slutty", "bodysuit"})


def _active_ready_outfit(outfit_tags: set[str]) -> bool:
    return bool(outfit_tags & {"sporty", "athletic", "activewear", "sport", "fitness", "wellness"})


def _wellness_ready_outfit(outfit_tags: set[str]) -> bool:
    active_tags = {"sporty", "athletic", "activewear", "sport", "fitness", "wellness", "swimwear"}
    restorative_tags = {"soft", "quiet_luxury", "modest_safe", "dress", "wellness", "swimwear"}
    blocked_tags = {"vacation", "coastal", "clubwear", "pushing_it", "slutty"}
    if outfit_tags & active_tags:
        return True
    if outfit_tags & restorative_tags and not (outfit_tags & blocked_tags):
        return True
    return False


def _outfit_material_predicate(outfit_id: str) -> Any:
    allowed_map = {
        "mini_dress": {"satin", "ribbed_knit", "vinyl_latex"},
        "crop_top_mini_skirt": {"satin", "ribbed_knit", "athletic_jersey"},
        "swimsuit": {"satin", "athletic_jersey"},
        "bikini_set": {"satin", "athletic_jersey"},
        "cardigan_skirt": {"ribbed_knit"},
        "latex_editorial": {"vinyl_latex"},
        "cardigan_trousers": {"soft_knit_layers", "ribbed_knit", "tailored_woven"},
        "blouse_trousers": {"tailored_woven", "crisp_cotton", "satin"},
        "knit_top_trousers": {"soft_knit_layers", "tailored_woven"},
        "sweater_jeans": {"soft_knit_layers", "ribbed_knit"},
        "polo_pleated_skirt": {"athletic_jersey"},
        "workout_top_leggings": {"athletic_jersey"},
        "shirt_trousers": {"crisp_cotton", "tailored_woven"},
        "zip_jacket_leggings": {"athletic_jersey"},
        "training_jacket_trousers": {"athletic_jersey"},
        "zip_front_training_set": {"athletic_jersey"},
        "cross_strap_keyhole_active_set": {"athletic_jersey"},
    }
    allowed = allowed_map.get(outfit_id)
    if not allowed:
        return None
    return lambda item: item["id"] in allowed


def _color_story_predicate(age_band_id: str, outfit_id: str) -> Any:
    young_ids = {"young_18", "young_19", "young_20", "young_21", "young_22", "young_23"}
    sporty_outfit_ids = {"crop_top_mini_skirt", "swimsuit", "bikini_set", "polo_pleated_skirt", "workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"}
    active_training_outfit_ids = {
        "workout_top_leggings",
        "zip_jacket_leggings",
        "training_jacket_trousers",
        "zip_front_training_set",
        "cross_strap_keyhole_active_set",
    }

    def predicate(item: dict[str, Any]) -> bool:
        tags = set(item.get("tags", []))
        if "gen_z" in tags and age_band_id not in young_ids:
            return False
        if "sporty" in tags and outfit_id not in sporty_outfit_ids:
            return False
        return True

    return predicate


def _base_space_outfit_predicate(outfit_family: dict[str, Any], style_mode: str = "random") -> Any:
    outfit_tags = set(outfit_family.get("tags", []))
    outfit_id = outfit_family["id"]
    relaxed_editorial_styles = {"nightlife", "studio", "fantasy", "cosplay", "creative_artistic"}
    quiet_day_residential_luxury_block_ids = {"vest_trousers", "halter_trousers"}
    active_training_styles = {"sport", "fitness"}
    active_training_outfit_ids = {
        "workout_top_leggings",
        "zip_jacket_leggings",
        "training_jacket_trousers",
        "zip_front_training_set",
        "cross_strap_keyhole_active_set",
    }
    active_training_space_ids = {
        "running_track_sprint_lane",
        "stadium_stair_run",
        "performance_gym_floor",
        "park_training_lawn",
        "forest_trail_warmup",
        "shoreline_workout_pad",
        "beach_workout_cove",
    }

    def is_quiet_day_scene(tags: set[str]) -> bool:
        return bool(tags & {"sunny", "daylight"}) and not bool(tags & {"night", "nightlife", "bar"})

    def predicate(item: dict[str, Any]) -> bool:
        tags = _scene_semantic_tags(item)
        scene_family_id = str(item.get("scene_family_id", ""))
        if "swimwear" in outfit_tags and not (tags & _water_contact_scene_tags()):
            return False
        if _active_scene(tags) and not _active_ready_outfit(outfit_tags):
            return False
        if "sporty" in outfit_tags and not (tags & {"sporty", "wellness"}):
            return False
        if style_mode in active_training_styles and "sporty" in outfit_tags:
            if outfit_id not in active_training_outfit_ids:
                return False
            if item.get("id") not in active_training_space_ids:
                return False
            if not (tags & {"sporty", "outdoor", "nature", "coastal", "gym", "track", "stadium", "active"}):
                return False
        if scene_family_id in {"residential_luxury", "culture_bookish", "garden_conservatory", "courtyard_garden", "urban_daylight"}:
            if outfit_tags & {"night", "pushing_it"} and not (outfit_tags & {"reserved", "quiet_luxury", "modest_safe", "soft"}):
                return False
        if style_mode not in relaxed_editorial_styles and is_quiet_day_scene(tags):
            if outfit_tags & {"night", "pushing_it"} and not (outfit_tags & {"reserved", "quiet_luxury", "modest_safe"}):
                return False
            if outfit_id in quiet_day_residential_luxury_block_ids and scene_family_id == "residential_luxury":
                return False
        if tags & {"pool", "beach"}:
            # True water-contact: pool deck, shoreline — swimwear and resort outfits are valid.
            allowed_water_tags = {"swimwear", "wet_possible", "dress", "feminine", "balanced_reveal", "summer", "coastal"}
            if not (outfit_tags & allowed_water_tags):
                return False
        elif tags & {"coastal"}:
            # Dry coastal ambience (boardwalk, promenade, colonnade) — resort-casual; no swimwear required.
            # Only allow resort-appropriate dress/feminine looks; block city-tailored or knitwear.
            allowed_coastal_tags = {"dress", "feminine", "balanced_reveal", "dressy", "summer", "coastal"}
            if style_mode in active_training_styles and "sporty" in outfit_tags:
                allowed_coastal_tags |= {"sporty", "athletic", "activewear", "wellness"}
            if not (outfit_tags & allowed_coastal_tags):
                return False
        if tags & {"spa", "bathroom", "dressing_space"}:
            allowed_spa_tags = {"swimwear", "soft", "quiet_luxury", "modest_safe", "balanced_reveal", "dress", "spa", "wellness"}
            if outfit_id == "swimsuit" and not (tags & _wet_context_tags()):
                return False
            if outfit_tags & {"trousers"} and not (outfit_tags & {"quiet_luxury", "modest_safe", "dress"}):
                return False
            if not (outfit_tags & allowed_spa_tags):
                return False
        if "bookish" in tags and outfit_tags & {"night", "pushing_it"} and not (outfit_tags & {"reserved", "quiet_luxury", "modest_safe", "soft"}):
            return False
        if tags & {"bookish", "creative"} and outfit_tags & {"sporty", "swimwear"}:
            return False
        if _wellness_scene(tags) and not _wellness_ready_outfit(outfit_tags):
            return False
        if _public_elegant_scene(tags) and _nightlife_forward_outfit(outfit_tags):
            return False
        return True

    return predicate


def _setting_macro_for_base_space_predicate(base_space: dict[str, Any]) -> Any:
    allowed = set(base_space.get("macro_ids", []))
    return lambda item: item["id"] in allowed and item["id"] != "fantasy_location"


def _choose_scene_family(
    data: dict[str, Any],
    batch_rules: dict[str, Any],
    rnd: random.Random,
    outfit_family: dict[str, Any],
    style_mode: str,
    recent_batch: list[dict[str, Any]],
    scene_family_counts: dict[str, int],
    previous_family_id: str | None,
    required_families: set[str] | None = None,
    preferred_families: set[str] | None = None,
    banned_families: set[str] | None = None,
) -> str:
    family_rules = batch_rules.get("scene_family_rules", {})
    target_share = family_rules.get("target_share", {})
    recent_window = family_rules.get("recent_window", 3)
    avoid_recent_memory_count = family_rules.get("avoid_recent_memory_count", 0)
    eligible_base_spaces = [item for item in data["setting_engine"]["base_spaces"] if _base_space_outfit_predicate(outfit_family, style_mode)(item)]
    if not eligible_base_spaces:
        raise ValueError("No eligible base spaces for the selected outfit family.")
    grouped = _group_base_spaces_by_family(eligible_base_spaces)
    required_families = required_families or set()
    if required_families:
        required_grouped = {family_id: items for family_id, items in grouped.items() if family_id in required_families}
        if required_grouped:
            grouped = required_grouped
        else:
            raise ValueError("No eligible base spaces for the required scene families.")
    if preferred_families:
        preferred_grouped = {family_id: items for family_id, items in grouped.items() if family_id in preferred_families}
        if preferred_grouped:
            grouped = preferred_grouped
    recent_family_ids = {item.get("scene_family_id") for item in recent_batch[-recent_window:]}
    memory_avoid_ids = set()
    if avoid_recent_memory_count > 0:
        values = data["memory"].get("setting_scene_families", [])
        memory_avoid_ids = set(values[-avoid_recent_memory_count:])
    preferred_families = preferred_families or set()
    banned_families = banned_families or set()

    def build_pool(excluded_recent: bool, excluded_memory: bool) -> list[dict[str, Any]]:
        pool: list[dict[str, Any]] = []
        for family_id, items in grouped.items():
            if family_id in banned_families:
                continue
            if excluded_recent and family_id in recent_family_ids and len(grouped) > 1:
                continue
            if excluded_memory and family_id in memory_avoid_ids and len(grouped) > 1:
                continue
            weight = target_share.get(family_id, 0.04)
            weight *= math.sqrt(len(items))
            weight /= 1 + (scene_family_counts.get(family_id, 0) * 1.65)
            if previous_family_id and family_id == previous_family_id:
                weight *= 0.3
            if preferred_families and family_id in preferred_families:
                weight *= 7
            pool.append({"id": family_id, "weight": max(weight, 0.001)})
        return pool

    for excluded_recent, excluded_memory in ((True, True), (True, False), (False, True), (False, False)):
        family_pool = build_pool(excluded_recent, excluded_memory)
        if family_pool:
            return _weighted_pick(family_pool, rnd)["id"]
    raise ValueError("Could not choose a scene family.")


def _setting_material_for_base_space(base_space: dict[str, Any]) -> Any:
    tags = _scene_semantic_tags(base_space)

    def predicate(item: dict[str, Any]) -> bool:
        item_tags = set(item.get("tags", []))
        item_id = item["id"]
        if "studio" in tags:
            return item_id == "seamless_clean"
        if "sporty" in tags and "spa" not in tags:
            if "interior" in tags:
                return item_id in {"rubber_lane_matte", "oak_lacquer"}
            return item_id in {"sunbleached_court_stone", "white_stucco_tile", "pale_concrete_glass"}
        if tags & {"nightlife", "night", "neon", "bar"}:
            return bool(item_tags & {"night", "interior"})
        if tags & {"outdoor", "coastal", "pool", "summer"}:
            return bool(item_tags & {"outdoor", "sunny", "urban"})
        if tags & {"luxury", "interior", "bookish", "hotelized_living"}:
            return bool(item_tags & {"luxury", "interior"})
        return True

    return predicate


def _detail_accent_for_base_space(base_space: dict[str, Any]) -> Any:
    tags = _scene_semantic_tags(base_space)
    base_id = base_space["id"]

    def predicate(item: dict[str, Any]) -> bool:
        item_id = item["id"]
        if "studio" in tags:
            return item_id == "clean_floor_shadow"
        if "spa" in tags:
            return item_id == "rolled_towels_tea"
        if "sporty" in tags and "spa" not in tags:
            if "coastal" in tags:
                return item_id in {"water_bottle_towel", "court_lines_bench"}
            if "interior" in tags:
                return item_id in {"water_bottle_towel", "resistance_bands_mat"}
            return item_id in {"water_bottle_towel", "court_lines_bench"}
        if "bookish" in tags:
            return item_id in {"stacked_art_books", "framed_canvases_books"}
        if tags & {"nightlife", "night", "bar", "neon"}:
            if "neon" in tags:
                return item_id in {"glowing_strip_lights", "mirror_brass_barware", "champagne_bucket"}
            return item_id in {"bar_hardware_glassware", "mirror_brass_barware", "champagne_bucket"}
        if base_id in {"hotel_sun_deck", "poolside_steps", "boardwalk_beach_houses"}:
            return item_id in {"sunglasses_towel_nearby", "sun_umbrellas_loungers"}
        if base_id in {"sunlit_mediterranean_courtyard", "resort_palm_walkway", "indoor_courtyard_breakfast_room"}:
            return item_id in {"terracotta_greenery", "citrus_pots", "fresh_flowers"}
        if tags & {"outdoor", "coastal", "sunny", "summer"}:
            return item_id in {"terracotta_greenery", "fresh_flowers"}
        if tags & {"luxury", "hotelized_living", "interior"}:
            return item_id in {"silver_coffee_service", "fresh_flowers", "sheer_drapes_cityline", "framed_canvases_books"}
        return True

    return predicate


def _atmosphere_for_base_space(base_space: dict[str, Any], time_of_day: dict[str, Any]) -> Any:
    tags = _scene_semantic_tags(base_space)
    time_id = time_of_day["id"]

    def predicate(item: dict[str, Any]) -> bool:
        item_id = item["id"]
        if "studio" in tags:
            return item_id == "controlled_studio_air"
        if time_id == "night":
            if tags & {"nightlife", "neon", "bar"}:
                return item_id in {"moody_amber_pools", "clean_city_night", "urban_evening_glow"}
            if tags & {"urban", "outdoor"}:
                return item_id in {"clean_city_night", "urban_evening_glow"}
            return item_id in {"moody_amber_pools", "urban_evening_glow"}
        if tags & {"outdoor", "coastal", "sunny", "summer"}:
            return item_id in {"bright_hard_sun", "warm_afternoon_glow"}
        if tags & {"interior", "luxury", "hotelized_living"}:
            return item_id in {"soft_filtered_daylight", "warm_afternoon_glow", "soft_stone_reflections"}
        return True

    return predicate


def _time_of_day_for_base_space(base_space: dict[str, Any]) -> Any:
    tags = set(base_space.get("tags", []))

    def predicate(item: dict[str, Any]) -> bool:
        time_id = item["id"]
        if tags & {"nightlife", "night", "neon", "bar"}:
            return time_id == "night"
        if tags & {"outdoor", "coastal", "pool", "sunny", "summer"}:
            return time_id in {"morning", "afternoon", "golden_hour"}
        return time_id in {"morning", "afternoon", "golden_hour", "night"}

    return predicate


def _lighting_for_base_space(base_space: dict[str, Any], atmosphere_cue: dict[str, Any], time_of_day: dict[str, Any]) -> Any:
    tags = set(base_space.get("tags", [])) | set(atmosphere_cue.get("tags", []))
    time_id = time_of_day["id"]

    def predicate(item: dict[str, Any]) -> bool:
        lighting_id = item["id"]
        if "studio" in tags:
            return lighting_id in {"studio_rim", "single_source_contrast"}
        if lighting_id == "neon_night":
            return time_id == "night" and bool(tags & {"neon", "urban"})
        if lighting_id == "direct_flash_clean":
            return time_id == "night" and bool(tags & {"interior", "urban", "nightlife", "bar", "hotelized_living"})
        if lighting_id == "studio_rim":
            return False
        if lighting_id == "single_source_contrast":
            return time_id in {"afternoon", "night"} and bool(tags & {"interior", "luxury", "bookish", "gallery", "hotelized_living"})
        if lighting_id == "hard_direct_light":
            return time_id in {"afternoon", "golden_hour"} and bool(tags & {"sunny", "outdoor", "rooftop", "urban", "courtyard", "pool", "coastal"})
        if lighting_id == "warm_interior":
            return time_id != "night" and "interior" in tags and not bool(tags & {"outdoor", "sunny"})
        if lighting_id == "practical_lamp":
            return time_id != "morning" and bool(tags & {"interior", "luxury", "bookish", "gallery", "hotelized_living", "grooming_bath"})
        if lighting_id == "colored_ambient":
            return time_id == "night" and bool(tags & {"nightlife", "neon", "creative", "gallery", "urban", "interior"})
        if lighting_id == "moody_darkness":
            return time_id == "night" and bool(tags & {"studio", "nightlife", "luxury", "bookish", "gallery", "interior"})
        if lighting_id == "tight_spotlight":
            return time_id in {"afternoon", "night"} and bool(tags & {"studio", "gallery", "luxury", "nightlife"})
        if lighting_id == "silhouette_edge":
            return time_id in {"golden_hour", "night"} and bool(tags & {"outdoor", "urban", "coastal", "courtyard", "rooftop", "beach"})
        if lighting_id == "soft_overcast":
            return time_id in {"morning", "afternoon"} and ("sunny" in tags or "outdoor" in tags or "interior" in tags)
        if lighting_id == "clean_daylight":
            return time_id in {"morning", "afternoon", "golden_hour"} or "sunny" in tags
        return True

    return predicate


def _is_30_plus(age_band_id: str) -> bool:
    return age_band_id in {"early_30s", "late_30s"}


def _pose_for_base_space(base_space: dict[str, Any], style_mode: str = "random") -> Any:
    tags = _scene_semantic_tags(base_space)
    support_tags = _scene_support_tags(base_space)
    base_id = base_space["id"]
    lowered = str(base_space.get("value", "")).strip().lower()

    def has_support(*required_tags: str) -> bool:
        return bool(support_tags & set(required_tags))

    def predicate(item: dict[str, Any]) -> bool:
        pose_id = item["id"]
        pose_tags = set(item.get("tags", []))
        if "mirror" in pose_tags and not has_support("mirror_support"):
            return False
        if "sink" in pose_tags and not has_support("sink_support", "counter_support"):
            return False
        if "sport_prep" in pose_tags and not bool(tags & {"sporty", "wellness"}):
            return False
        if "domestic" in pose_tags and bool(tags & {"nightlife", "bar", "night"}):
            return False
        if "counter" in pose_tags:
            counter_context = bool(tags & {"domestic", "hotelized_living", "dressing_space", "interior"})
            counter_context = counter_context and has_support("counter_support")
            awkward_context = bool(tags & {"bookish", "creative", "coastal", "sporty", "wellness", "outdoor", "travel"})
            return counter_context and not awkward_context
        if "bed" in pose_tags:
            return (base_id in {"hotel_suite_sitting_area"} or bool(tags & {"bedroom"})) and has_support("bed_support")
        if "stairs" in pose_tags:
            return ("stairs" in tags or base_id == "stair_hall_skylight") and has_support("stairs_support")
        if "chair" in pose_tags:
            seat_context = bool(tags & {"interior", "luxury", "bookish", "hotelized_living", "dressing_space", "bar"})
            return seat_context and has_support("chair_support", "bench_support", "sofa_support")
        if "lounge" in pose_tags:
            lounge_context = bool(tags & {"luxury", "pool", "coastal", "spa", "bedroom", "hotelized_living"})
            return lounge_context and has_support("bed_support", "sofa_support")
        if "floor" in pose_tags:
            public_hard_surface = bool(tags & {"travel", "urban", "public_elegant"}) or any(
                token in lowered for token in ("path", "paving", "paved", "sidewalk", "street", "road", "highway", "corridor", "lobby", "bridge", "boardwalk")
            )
            return has_support("soft_ground_support", "bed_support", "sofa_support") and not public_hard_surface
        if "perched" in pose_tags:
            perch_context = bool(tags & {"interior", "luxury", "dressing_space", "domestic", "hotelized_living", "social", "bar"})
            perch_support = has_support("counter_support", "chair_support", "bench_support", "sofa_support")
            awkward_context = bool(tags & {"sporty", "wellness", "outdoor", "coastal", "travel", "bookish"})
            return perch_context and perch_support and not awkward_context
        if pose_id in {"window_turn_teacup", "chess_piece_reach_up", "tea_pour_tray_level", "map_table_both_hands"}:
            return bool(tags & {"bookish"})
        if "cabinet" in pose_tags:
            if has_support("cabinet_support", "counter_support") and bool(tags & {"domestic", "interior", "hotelized_living", "dressing_space"}):
                return True
            return False
        if pose_id == "pottery_wheel_lift_face":
            return bool(tags & {"creative"})
        if pose_id == "umbrella_over_shoulder_turn":
            return bool(tags & {"outdoor", "coastal"})
        if item.get("group") == "kneeling":
            if tags & {"bookish", "travel", "public_elegant", "quiet"}:
                return False
            if base_id in {"hotel_suite_sitting_area", "boutique_hotel_corridor", "hotel_corridor_night", "rooftop_hotel_conservatory", "hybrid_hotel_lobby_lounge", "heritage_hotel_staircase", "airport_lounge_evening"} and style_mode not in {"luxury", "nightlife", "studio", "fantasy", "cosplay"}:
                return False
            if bool(tags & {"sporty", "wellness", "creative", "studio", "nightlife", "outdoor", "coastal", "pool", "spa", "bathroom", "dressing_space"}) and has_support("floor_support", "stairs_support", "bed_support", "sofa_support", "chair_support"):
                return True
            return False
        return True

    return predicate


def _pose_group_for_base_space(base_space: dict[str, Any], pose_group: str, style_mode: str = "random") -> Any:
    base = _pose_for_base_space(base_space, style_mode)

    def predicate(item: dict[str, Any]) -> bool:
        if item.get("group") != pose_group:
            return False
        return base(item)

    return predicate


def _framing_for_pose(pose_family: dict[str, Any], framing_group: str) -> Any:
    pose_id = pose_family["id"]

    def predicate(item: dict[str, Any]) -> bool:
        if item.get("group") != framing_group:
            return False
        framing_id = item["id"]
        if pose_id in {"reclined_one_knee_up", "side_lying_lounge", "prone_elbows_down"}:
            return framing_id in {"full_body", "ankle_up", "knee_up", "cowboy_shot", "waist_up", "bust_up", "below_chest_portrait", "face_only"}
        if pose_id == "slow_walk":
            return framing_id in {"full_body", "ankle_up", "knee_up", "cowboy_shot", "waist_up"}
        if pose_id in {"kneeling_both_knees", "one_knee_raised_floor_pose"}:
            return framing_id in {"full_body", "ankle_up", "knee_up", "cowboy_shot", "waist_up", "bust_up", "below_chest_portrait", "face_only"}
        if pose_id in {"cross_legged_seated", "one_knee_up_seated", "legs_to_side_pose", "chair_sideways_pose", "backwards_chair_pose", "seated_sideways"}:
            return framing_id in {"full_body", "ankle_up", "knee_up", "cowboy_shot", "waist_up", "bust_up", "head_and_shoulders", "below_chest_portrait", "face_only"}
        return True

    return predicate


def _capture_style_for_candidate(base_space: dict[str, Any], outfit_family: dict[str, Any]) -> Any:
    tags = set(base_space.get("tags", [])) | set(outfit_family.get("tags", []))

    def predicate(item: dict[str, Any]) -> bool:
        style_id = item["id"]
        if "studio" in tags:
            return style_id in {"fashion_photo", "editorial_photo"}
        if "nightlife" in tags or "night" in tags or "bar" in tags:
            return style_id in {"editorial_photo", "fashion_photo", "lifestyle_photo"}
        if "editorial" in tags:
            return style_id != "smartphone_photo"
        return True

    return predicate


def _compose_setting_scene(
    base_space: dict[str, Any],
    setting_material: dict[str, Any],
    detail_accent: dict[str, Any],
    atmosphere_cue: dict[str, Any],
) -> str:
    return ", ".join([
        base_space["value"],
        setting_material["value"],
        detail_accent["value"],
        atmosphere_cue["value"],
    ])


def _lookup_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return data_loader._lookup_by_id(items)


def _choose_photo_treatment(
    profiles: list[dict[str, Any]],
    rnd: random.Random,
    *,
    scene_family_id: str,
    capture_style_id: str | None = None,
    lighting_family_id: str | None = None,
    time_of_day_id: str | None = None,
    style_mode: str,
    mode: str = "women",
    previous_id: str | None = None,
    required_ids: set[str] | None = None,
    preferred_ids: set[str] | None = None,
    deprioritized_ids: set[str] | None = None,
) -> dict[str, Any]:
    required_ids = required_ids or set()
    preferred_ids = preferred_ids or set()
    deprioritized_ids = deprioritized_ids or set()
    category_weights_by_style = {
        "random": {"polished": 35.0, "stylized": 65.0},
        "nightlife": {"polished": 30.0, "stylized": 70.0},
        "studio": {"polished": 30.0, "stylized": 70.0},
        "creative_artistic": {"polished": 35.0, "stylized": 65.0},
        "luxury": {"polished": 35.0, "stylized": 65.0},
        "romantic": {"polished": 25.0, "stylized": 75.0},
        "sport": {"polished": 65.0, "stylized": 35.0},
        "fitness": {"polished": 65.0, "stylized": 35.0},
        "coastal": {"polished": 60.0, "stylized": 40.0},
        "vacation": {"polished": 60.0, "stylized": 40.0},
    }
    effective_style_mode = (style_mode or "random").strip().lower() or "random"
    effective_mode = (mode or "women").strip().lower() or "women"
    compatible_profiles: list[dict[str, Any]] = []
    compatible_weights: list[float] = []
    compatible_categories: dict[str, list[tuple[dict[str, Any], float]]] = {"polished": [], "stylized": []}
    compatible_mix_buckets: dict[str, list[tuple[dict[str, Any], float]]] = {
        "phone_snapshot": [],
        "casual_low_end": [],
        "editorial_non_phone": [],
        "polished_glam": [],
    }
    for profile in profiles:
        if required_ids and profile.get("id") not in required_ids:
            continue
        allowed_scenes = _profile_value_set(profile, "allowed_scene_families")
        banned_scenes = _profile_value_set(profile, "banned_scene_families")
        allowed_styles = _profile_value_set(profile, "allowed_style_modes")
        banned_styles = _profile_value_set(profile, "banned_style_modes")
        if allowed_scenes and scene_family_id not in allowed_scenes:
            continue
        if scene_family_id in banned_scenes:
            continue
        if effective_style_mode in banned_styles:
            continue
        if allowed_styles and effective_style_mode not in allowed_styles:
            continue
        weight = max(float(profile.get("weight", 1.0)), 0.01)
        if scene_family_id in _profile_value_set(profile, "preferred_scene_families"):
            weight *= 1.45
        if capture_style_id and capture_style_id in _profile_value_set(profile, "preferred_capture_ids"):
            weight *= 1.4
        if lighting_family_id and lighting_family_id in _profile_value_set(profile, "preferred_lighting_ids"):
            weight *= 1.35
        if time_of_day_id and time_of_day_id in _profile_value_set(profile, "preferred_time_ids"):
            weight *= 1.2
        if effective_style_mode in _profile_value_set(profile, "preferred_style_modes"):
            weight *= 1.15
        quality_tier = photo_treatment_quality_tier(str(profile.get("id", "")), str(profile.get("category", "stylized")))
        treatment_tone = photo_treatment_tone(str(profile.get("id", "")), str(profile.get("category", "stylized")))
        if effective_mode == "women" and effective_style_mode == "random":
            if quality_tier == "raw_low_end":
                weight *= 0.22
            elif quality_tier == "casual":
                weight *= 0.58
            elif quality_tier == "clean":
                weight *= 1.08
            elif quality_tier == "premium":
                weight *= 1.18
            if treatment_tone in {"documentary", "snapshot"}:
                weight *= 0.82
            if scene_family_id in {"residential_luxury", "hospitality_suite", "grooming_bath"} and quality_tier in {"casual", "raw_low_end"}:
                weight *= 0.25
        elif effective_mode == "women" and effective_style_mode in {"luxury", "romantic"}:
            if quality_tier == "raw_low_end":
                weight *= 0.08
            elif quality_tier == "casual":
                weight *= 0.30
            elif quality_tier == "premium":
                weight *= 1.15
            if treatment_tone in {"phone", "documentary", "snapshot"}:
                weight *= 0.35
            if treatment_tone in {"beauty", "editorial", "cinematic", "dramatic"}:
                weight *= 1.12
        if preferred_ids and profile.get("id") in preferred_ids:
            weight *= 1.6
        if deprioritized_ids and profile.get("id") in deprioritized_ids:
            weight *= 0.22
        if previous_id and profile.get("id") == previous_id:
            weight *= 0.78
        compatible_profiles.append(profile)
        compatible_weights.append(weight)
        category = str(profile.get("category", "stylized")).strip().lower() or "stylized"
        compatible_categories.setdefault(category, []).append((profile, weight))
        compatible_mix_buckets.setdefault(
            photo_treatment_mix_bucket(str(profile.get("id", "")), category),
            [],
        ).append((profile, weight))
    if not compatible_profiles:
        fallback = next((item for item in profiles if item.get("id") == "clean_commercial"), None)
        if fallback is not None:
            return fallback
        return profiles[0]
    if effective_mode == "women" and effective_style_mode == "random" and not required_ids:
        available_mix_buckets = [
            (bucket, weight)
            for bucket, weight in WOMEN_RANDOM_TREATMENT_MIX_TARGETS.items()
            if compatible_mix_buckets.get(bucket)
        ]
        if available_mix_buckets:
            chosen_bucket = rnd.choices(
                [item[0] for item in available_mix_buckets],
                weights=[item[1] for item in available_mix_buckets],
                k=1,
            )[0]
            bucket_profiles = compatible_mix_buckets.get(chosen_bucket, [])
            if bucket_profiles:
                return rnd.choices([item[0] for item in bucket_profiles], weights=[item[1] for item in bucket_profiles], k=1)[0]
    category_weights = category_weights_by_style.get(effective_style_mode, {"polished": 45.0, "stylized": 55.0})
    available_categories = [(category, weight) for category, weight in category_weights.items() if compatible_categories.get(category)]
    if available_categories:
        chosen_category = rnd.choices([item[0] for item in available_categories], weights=[item[1] for item in available_categories], k=1)[0]
        category_profiles = compatible_categories.get(chosen_category, [])
        if category_profiles:
            return rnd.choices([item[0] for item in category_profiles], weights=[item[1] for item in category_profiles], k=1)[0]
    return rnd.choices(compatible_profiles, weights=compatible_weights, k=1)[0]


def _normalize_candidate(
    data: dict[str, Any],
    candidate: dict[str, Any],
    *,
    style_mode: str = "random",
    user_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized = dict(candidate)
    profile = _merged_profile(_style_profile(style_mode), user_profile)
    lookups = {
        "ethnicities": _lookup_by_id(data["subjects"]["ethnicities"]),
        "hair_colors": _lookup_by_id(data["styling"]["hair_colors"]),
        "outfit_families": _lookup_by_id(data["styling"]["outfit_families"]),
        "materials": _lookup_by_id(data["styling"]["materials"]),
        "photo_treatments": _lookup_by_id(data["photo_treatments"]["profiles"]),
        "capture_styles": _lookup_by_id(data["composition"]["capture_styles"]),
        "camera_framings": _lookup_by_id(data["composition"]["camera_framings"]),
        "lighting_families": _lookup_by_id(data["composition"]["lighting_families"]),
        "pose_families": _lookup_by_id(data["pose_bank"]["pose_families"]),
        "setting_macros": _lookup_by_id(data["settings"]["setting_macros"]),
        "base_spaces": _lookup_by_id(data["setting_engine"]["base_spaces"]),
        "material_accents": _lookup_by_id(data["setting_engine"]["material_accents"]),
        "detail_accents": _lookup_by_id(data["setting_engine"]["detail_accents"]),
        "atmosphere_cues": _lookup_by_id(data["setting_engine"]["atmosphere_cues"]),
        "surface_states": _lookup_by_id(data["surface_states"]["surface_states"]),
    }
    ethnicity = lookups["ethnicities"].get(normalized.get("ethnicity_id"))
    if ethnicity is not None:
        normalized["ethnicity"] = ethnicity["value"]
        normalized["ethnicity_group"] = ethnicity["group"]
    hair_color = lookups["hair_colors"].get(normalized.get("hair_color_id"))
    if hair_color is not None:
        normalized["hair_color"] = hair_color["value"]
        normalized["hair_color_tags"] = hair_color.get("tags", [])
    outfit_family = lookups["outfit_families"].get(normalized.get("outfit_family_id"))
    if outfit_family is not None:
        normalized["outfit_family"] = outfit_family["value"]
    material = lookups["materials"].get(normalized.get("material_id"))
    if material is not None:
        normalized["material"] = material["value"]
    setting_micro = lookups["base_spaces"].get(normalized.get("setting_micro_id"))
    scene_semantic_tags: set[str] = set()
    if setting_micro is not None:
        normalized["setting_micro"] = setting_micro["value"]
        normalized["scene_family_id"] = setting_micro["scene_family_id"]
        scene_semantic_tags = _scene_semantic_tags(setting_micro)
    setting_macro = lookups["setting_macros"].get(normalized.get("setting_macro_id"))
    if setting_micro is not None:
        allowed_macro_ids = [macro_id for macro_id in setting_micro.get("macro_ids", []) if macro_id in lookups["setting_macros"]]
        if setting_macro is None or setting_macro["id"] not in allowed_macro_ids:
            setting_macro = lookups["setting_macros"].get(allowed_macro_ids[0]) if allowed_macro_ids else setting_macro
    if setting_macro is not None:
        normalized["setting_macro_id"] = setting_macro["id"]
        normalized["setting_macro"] = setting_macro["value"]
    setting_material = lookups["material_accents"].get(normalized.get("setting_material_id"))
    if setting_material is not None:
        normalized["setting_material"] = setting_material["value"]
    detail_accent = lookups["detail_accents"].get(normalized.get("detail_accent_id"))
    if detail_accent is not None:
        normalized["detail_accent"] = detail_accent["value"]
        normalized["prop_cluster_id"] = detail_accent["id"]
        normalized["prop_cluster"] = detail_accent["value"]
    atmosphere_cue = lookups["atmosphere_cues"].get(normalized.get("atmosphere_cue_id"))
    if atmosphere_cue is not None:
        normalized["atmosphere_cue"] = atmosphere_cue["value"]
    pose_family = lookups["pose_families"].get(normalized.get("pose_family_id"))
    if pose_family is not None:
        normalized["pose_family"] = pose_family["value"]
    lighting_family = lookups["lighting_families"].get(normalized.get("lighting_family_id"))
    if lighting_family is not None:
        normalized["lighting_family"] = lighting_family["value"]
    capture_style = lookups["capture_styles"].get(normalized.get("capture_style_id"))
    if capture_style is not None:
        normalized["capture_style"] = capture_style["value"]
    photo_treatment = lookups["photo_treatments"].get(normalized.get("photo_treatment_id"))
    if photo_treatment is not None:
        normalized["photo_treatment"] = photo_treatment.get("label", photo_treatment["id"])
        normalized["photo_treatment_category"] = photo_treatment.get("category", "stylized")
        normalized["capture_style_render"] = photo_treatment.get("capture_render", normalized.get("capture_style", "photo"))
        normalized["lighting_render"] = photo_treatment.get("lighting_render", normalized.get("lighting_family", ""))
        normalized["camera_vibe"] = photo_treatment.get("camera_vibe", "")
        normalized["color_grade"] = photo_treatment.get("color_grade", "")
        normalized["finish_render"] = photo_treatment.get("finish", "natural skin texture")
    camera_framing = lookups["camera_framings"].get(normalized.get("camera_framing_id"))
    if camera_framing is not None:
        normalized["camera_framing"] = camera_framing["value"]
    surface_state = lookups["surface_states"].get(normalized.get("surface_state_id"))
    if surface_state is None:
        surface_state = lookups["surface_states"].get("dry_clean")
    if surface_state is not None:
        normalized["surface_state_id"] = surface_state["id"]
        normalized["surface_state"] = surface_state["value"]
    if setting_micro is not None and setting_material is not None and detail_accent is not None and atmosphere_cue is not None:
        normalized["setting_scene_id"] = f'{setting_micro["id"]}__{setting_material["id"]}__{detail_accent["id"]}__{atmosphere_cue["id"]}'
        normalized["setting_scene"] = _compose_setting_scene(setting_micro, setting_material, detail_accent, atmosphere_cue)
    if setting_micro is not None and outfit_family is not None and pose_family is not None and lighting_family is not None:
        normalized["route"] = _infer_route(
            setting_micro,
            outfit_family,
            pose_family,
            lighting_family,
            data["routes"],
            required_route_ids=set(profile.get("required_route_ids", [])),
            preferred_route_ids=set(profile.get("preferred_route_ids", [])),
        )
    tag_sets = []
    for item in (ethnicity, capture_style, camera_framing, outfit_family, material, setting_macro, setting_micro, setting_material, detail_accent, atmosphere_cue, lighting_family, surface_state):
        if item is not None:
            tag_sets.append(set(item.get("tags", [])))
    if scene_semantic_tags:
        tag_sets.append(scene_semantic_tags)
    normalized["tags"] = sorted(set().union(*tag_sets)) if tag_sets else []
    return normalized
