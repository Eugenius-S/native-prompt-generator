from __future__ import annotations

import argparse
import functools
import json
import math
import os
import random
import tempfile
import time
from pathlib import Path
from typing import Any

try:
    from . import candidate_builder, data_loader, selectors
    from .render import prompt_renderer
    from .repair import repair_candidate
    from .validator import load_rule_bank, validate_candidate
except ImportError:
    import candidate_builder
    import data_loader
    import selectors
    from render import prompt_renderer
    from repair import repair_candidate
    from validator import load_rule_bank, validate_candidate


ROOT = data_loader.ROOT
DATA_ROOT = data_loader.DATA_ROOT
CONTENT_BANK_CONFIG_PATH = data_loader.CONTENT_BANK_CONFIG_PATH
MEMORY_PATH = data_loader.MEMORY_PATH
STATIC_BANK_FILES = data_loader.STATIC_BANK_FILES


STYLE_PROFILES = selectors.STYLE_PROFILES


def _read_json(path: Path) -> dict[str, Any]:
    return data_loader._read_json(path)


def _retry_file_access(operation: Any, attempts: int = 50, delay: float = 0.01) -> Any:
    return data_loader._retry_file_access(operation, attempts=attempts, delay=delay)


def _write_json_atomic(path: Path, payload: Any) -> None:
    data_loader._write_json_atomic(path, payload)


def _load_runtime_memory() -> dict[str, Any]:
    return data_loader._load_runtime_memory()


def _merge_data(base: Any, overlay: Any) -> Any:
    return data_loader._merge_data(base, overlay)


def _content_bank_config() -> dict[str, bool]:
    return data_loader._content_bank_config()


def _layer_fragment_paths(layer_name: str, bank_name: str) -> list[Path]:
    return data_loader._layer_fragment_paths(layer_name, bank_name)


@functools.lru_cache(maxsize=1)
def _load_static_data_bank() -> dict[str, Any]:
    return data_loader._load_static_data_bank()


def _weighted_pick(items: list[dict[str, Any]], rnd: random.Random) -> dict[str, Any]:
    return selectors._weighted_pick(items, rnd)


def _weighted_pick_filtered(
    items: list[dict[str, Any]],
    rnd: random.Random,
    predicate: Any | None = None,
    avoid_id: str | None = None,
    avoid_ids: set[str] | None = None,
    preferred_predicate: Any | None = None,
) -> dict[str, Any]:
    return selectors._weighted_pick_filtered(
        items,
        rnd,
        predicate=predicate,
        avoid_id=avoid_id,
        avoid_ids=avoid_ids,
        preferred_predicate=preferred_predicate,
    )


def _style_profile(style_mode: str | None) -> dict[str, Any]:
    return selectors._style_profile(style_mode)


def _merged_profile(base_profile: dict[str, Any], user_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    return selectors._merged_profile(base_profile, user_profile)


def _photo_treatment_profile(profile: dict[str, Any] | None) -> dict[str, Any]:
    return selectors._photo_treatment_profile(profile)


def _style_preference_predicate(
    profile: dict[str, Any],
    *,
    ids_key: str | None = None,
    tags_key: str | None = None,
    field_name: str = "id",
) -> Any | None:
    return selectors._style_preference_predicate(profile, ids_key=ids_key, tags_key=tags_key, field_name=field_name)


def _infer_route(
    base_space: dict[str, Any],
    outfit_family: dict[str, Any],
    pose_family: dict[str, Any],
    lighting_family: dict[str, Any],
    routes_bank: dict[str, Any],
    required_route_ids: set[str] | None = None,
    preferred_route_ids: set[str] | None = None,
) -> str:
    return selectors._infer_route(
        base_space,
        outfit_family,
        pose_family,
        lighting_family,
        routes_bank,
        required_route_ids=required_route_ids,
        preferred_route_ids=preferred_route_ids,
    )


def load_data_bank() -> dict[str, Any]:
    return data_loader.load_data_bank()


@functools.lru_cache(maxsize=1)
def _render_styling_lookups() -> dict[str, dict[str, dict[str, Any]]]:
    return prompt_renderer._render_styling_lookups()


COLOR_STORY_RENDER_OVERRIDES: dict[str, dict[str, str]] = {
    "clean_neutrals": {"primary": "soft stone"},
    "hot_pink": {"primary": "hot pink"},
    "powder_blue": {"primary": "powder blue"},
    "lime_pop": {"primary": "lime"},
    "navy_cream": {"primary": "navy", "secondary": "cream"},
    "earthy_soft": {"primary": "earthy brown"},
    "winter_neutrals": {"primary": "winter cream"},
    "sport_clean_white": {"primary": "clean white"},
    "black_gold": {"primary": "black", "secondary": "gold"},
    "oxblood_noir": {"primary": "oxblood", "secondary": "noir"},
    "emerald_noir": {"primary": "emerald", "secondary": "noir"},
    "chocolate_cream": {"primary": "chocolate", "secondary": "cream"},
    "champagne_taupe": {"primary": "champagne", "secondary": "taupe"},
    "slate_blue_ink": {"primary": "slate blue", "secondary": "ink"},
    "rosewood_smoke": {"primary": "rosewood", "secondary": "smoke"},
    "soft_camel_cream": {"primary": "soft camel", "secondary": "cream"},
    "dusty_rose_taupe": {"primary": "dusty rose", "secondary": "taupe"},
}


def _article_for(value: str) -> str:
    return prompt_renderer._article_for(value)


def _seeded_random(*parts: Any) -> random.Random:
    return prompt_renderer._seeded_random(*parts)


def _color_story_components(color_story_id: str, color_story: str) -> tuple[str, str | None]:
    return prompt_renderer._color_story_components(color_story_id, color_story)


def _outfit_color_layout(outfit_id: str, outfit_text: str, outfit_tags: set[str]) -> str:
    return prompt_renderer._outfit_color_layout(outfit_id, outfit_text, outfit_tags)


def _pattern_pool(scene_family_id: str, outfit_tags: set[str]) -> list[str]:
    return prompt_renderer._pattern_pool(scene_family_id, outfit_tags)


def _layout_targets(layout: str) -> tuple[str, str]:
    return prompt_renderer._layout_targets(layout)


def _pick_outfit_color_mode(
    chooser: random.Random,
    *,
    has_secondary: bool,
    allow_pattern: bool,
    layout: str,
) -> str:
    return prompt_renderer._pick_outfit_color_mode(
        chooser,
        has_secondary=has_secondary,
        allow_pattern=allow_pattern,
        layout=layout,
    )


def _pattern_friendly_outfit(outfit_text: str, outfit_tags: set[str]) -> bool:
    return prompt_renderer._pattern_friendly_outfit(outfit_text, outfit_tags)


def _append_material(outfit_text: str, material: str) -> str:
    return prompt_renderer._append_material(outfit_text, material)


def render_outfit_phrase_from_parts(
    *,
    outfit_family_id: str,
    outfit_family: str,
    color_story_id: str,
    color_story: str,
    material: str,
    scene_family_id: str = "",
    seed_parts: tuple[Any, ...] = (),
) -> str:
    return prompt_renderer.render_outfit_phrase_from_parts(
        outfit_family_id=outfit_family_id,
        outfit_family=outfit_family,
        color_story_id=color_story_id,
        color_story=color_story,
        material=material,
        scene_family_id=scene_family_id,
        seed_parts=seed_parts,
    )


def render_outfit_phrase(candidate: dict[str, Any]) -> str:
    return prompt_renderer.render_outfit_phrase(candidate)


def render_male_outfit_phrase(
    color: str,
    outfit_text: str,
    *,
    scene_family_id: str = "",
    seed_parts: tuple[Any, ...] = (),
) -> str:
    return prompt_renderer.render_male_outfit_phrase(
        color,
        outfit_text,
        scene_family_id=scene_family_id,
        seed_parts=seed_parts,
    )


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


def _age_predicate(
    batch_rules: dict[str, Any],
    breast_size_id: str,
    vivid_hair: bool,
) -> Any | None:
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


def _scene_support_tags(base_space: dict[str, Any]) -> set[str]:
    lowered = str(base_space.get("value", "")).strip().lower()
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
    if any(token in lowered for token in ("cabinet", "cupboard", "wardrobe", "shelves", "pantry")):
        support_tags.add("cabinet_support")
    if any(token in lowered for token in ("floor", "ground", "mat", "deck", "patio", "sand", "grass")):
        support_tags.add("floor_support")
    return support_tags


def _scene_semantic_tags(base_space: dict[str, Any]) -> set[str]:
    tags = set(base_space.get("tags", []))
    scene_family_id = str(base_space.get("scene_family_id", ""))
    normalized = set(tags)
    normalized |= _scene_support_tags(base_space)

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

    return normalized


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


def _compose_predicates(*predicates: Any | None) -> Any | None:
    active = [predicate for predicate in predicates if predicate is not None]
    if not active:
        return None

    def predicate(item: dict[str, Any]) -> bool:
        return all(check(item) for check in active)

    return predicate


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
        if "swimwear" in outfit_tags and not (tags & _wet_context_tags()):
            return False
        if "sporty" in outfit_tags and not (tags & {"sporty", "wellness"}):
            return False
        if style_mode in active_training_styles and "sporty" in outfit_tags:
            if outfit_id not in active_training_outfit_ids:
                return False
            if item.get("id") not in active_training_space_ids:
                return False
            if not (tags & {"sporty", "outdoor", "coastal", "nature"}):
                return False
        if style_mode not in relaxed_editorial_styles and is_quiet_day_scene(tags):
            if outfit_tags & {"night", "pushing_it"} and not (outfit_tags & {"reserved", "quiet_luxury", "modest_safe"}):
                return False
            if outfit_id in quiet_day_residential_luxury_block_ids and item.get("scene_family_id") == "residential_luxury":
                return False
        if tags & {"pool", "coastal"}:
            allowed_pool_tags = {"swimwear", "dress", "feminine", "balanced_reveal", "dressy", "summer", "coastal"}
            if style_mode in active_training_styles and "sporty" in outfit_tags:
                allowed_pool_tags |= {"sporty", "athletic", "activewear", "wellness"}
            if not (outfit_tags & allowed_pool_tags):
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
    eligible_base_spaces = [
        item
        for item in data["setting_engine"]["base_spaces"]
        if _base_space_outfit_predicate(outfit_family, style_mode)(item)
    ]
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
    memory_avoid_ids = _recent_memory_set(data["memory"], "setting_scene_families", avoid_recent_memory_count)

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


def _engine_item_predicate(required_tags: set[str], forbidden_tags: set[str] | None = None) -> Any:
    forbidden_tags = forbidden_tags or set()

    def predicate(item: dict[str, Any]) -> bool:
        item_tags = set(item.get("tags", []))
        if required_tags and not item_tags.intersection(required_tags):
            return False
        if forbidden_tags and item_tags.intersection(forbidden_tags):
            return False
        return True

    return predicate


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


def _setting_micro_predicate(setting_macro: dict[str, Any], outfit_family: dict[str, Any]) -> Any:
    macro_tags = set(setting_macro.get("tags", []))
    outfit_tags = set(outfit_family.get("tags", []))

    def predicate(item: dict[str, Any]) -> bool:
        tags = set(item.get("tags", []))
        required = item.get("requires_any_tags", [])
        forbidden = item.get("forbids_any_tags", [])
        if required:
            if setting_macro["id"] == "city_lifestyle":
                if not any(tag in macro_tags for tag in required) and not any(tag in {"interior", "outdoor"} for tag in required):
                    return False
            elif setting_macro["id"] == "fantasy_location":
                pass
            elif not any(tag in macro_tags for tag in required):
                return False
        if forbidden and any(tag in macro_tags for tag in forbidden):
            return False
        if "swimwear" in outfit_tags and not (tags & _wet_context_tags()):
            return False
        if setting_macro["id"] == "nightlife" and "nightlife" not in tags and "neon" not in tags:
            return False
        if setting_macro["id"] == "studio_clean" and "outdoor" in tags:
            return False
        if setting_macro["id"] == "beach_resort" and "coastal" not in tags and "pool" not in tags:
            return False
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


def _prop_cluster_predicate(setting_micro: dict[str, Any]) -> Any:
    setting_tags = set(setting_micro.get("tags", []))

    def predicate(item: dict[str, Any]) -> bool:
        prop_tags = set(item.get("tags", []))
        if not prop_tags:
            return True
        if "pool" in prop_tags or "beach" in prop_tags or "summer" in prop_tags:
            return bool(setting_tags & {"pool", "coastal", "summer"})
        if "bathroom" in prop_tags or "dressing_space" in prop_tags:
            return bool(setting_tags & {"bathroom", "dressing_space"})
        if "bookish" in prop_tags:
            return "bookish" in setting_tags
        if "nightlife" in prop_tags or "arcade" in prop_tags or "neon" in prop_tags:
            return bool(setting_tags & {"nightlife", "neon"})
        if "hotelized_living" in prop_tags:
            return "hotelized_living" in setting_tags
        if "luxury" in prop_tags:
            return "luxury" in setting_tags
        return True

    return predicate


def _time_of_day_predicate(setting_macro: dict[str, Any], setting_micro: dict[str, Any]) -> Any:
    tags = set(setting_macro.get("tags", [])) | set(setting_micro.get("tags", []))

    def predicate(item: dict[str, Any]) -> bool:
        time_id = item["id"]
        if "nightlife" in tags or "neon" in tags or setting_macro["id"] == "nightlife":
            return time_id == "night"
        if "outdoor" in tags or "coastal" in tags or "pool" in tags:
            return time_id in {"morning", "afternoon", "golden_hour"}
        return time_id in {"morning", "afternoon", "night"}

    return predicate


def _lighting_predicate(setting_macro: dict[str, Any], setting_micro: dict[str, Any], time_of_day: dict[str, Any]) -> Any:
    tags = set(setting_macro.get("tags", [])) | set(setting_micro.get("tags", []))
    time_id = time_of_day["id"]

    def predicate(item: dict[str, Any]) -> bool:
        lighting_id = item["id"]
        if lighting_id == "neon_night":
            return time_id == "night" and bool(tags & {"nightlife", "neon"})
        if lighting_id == "direct_flash_clean":
            return time_id == "night" and bool(tags & {"nightlife", "urban", "interior", "luxury"})
        if lighting_id == "studio_rim":
            return setting_macro["id"] == "studio_clean"
        if lighting_id == "single_source_contrast":
            return setting_macro["id"] == "studio_clean" or (time_id in {"afternoon", "night"} and bool(tags & {"interior", "luxury", "bookish", "gallery"}))
        if lighting_id == "hard_direct_light":
            return time_id in {"afternoon", "golden_hour"} and bool(tags & {"outdoor", "sunny", "urban", "courtyard", "coastal"})
        if lighting_id == "warm_interior":
            return time_id != "night" and "interior" in tags
        if lighting_id == "practical_lamp":
            return time_id != "morning" and bool(tags & {"interior", "luxury", "bookish", "gallery", "hospitality", "grooming_bath"})
        if lighting_id == "colored_ambient":
            return time_id == "night" and bool(tags & {"nightlife", "neon", "creative", "gallery", "urban", "interior"})
        if lighting_id == "moody_darkness":
            return time_id == "night" and bool(tags & {"studio", "nightlife", "luxury", "bookish", "gallery", "interior"})
        if lighting_id == "tight_spotlight":
            return time_id in {"afternoon", "night"} and bool(tags & {"studio", "gallery", "luxury", "nightlife"})
        if lighting_id == "silhouette_edge":
            return time_id in {"golden_hour", "night"} and bool(tags & {"outdoor", "urban", "coastal", "courtyard", "rooftop", "beach"})
        if lighting_id in {"clean_daylight", "soft_overcast"}:
            return time_id in {"morning", "afternoon", "golden_hour"}
        return True

    return predicate


def _is_30_plus(age_band_id: str) -> bool:
    return age_band_id in {"early_30s", "late_30s"}


def _pose_predicate(setting_micro: dict[str, Any]) -> Any:
    setting_id = setting_micro["id"]
    tags = set(setting_micro.get("tags", []))

    def predicate(item: dict[str, Any]) -> bool:
        pose_id = item["id"]
        pose_tags = set(item.get("tags", []))
        if "sport_prep" in pose_tags and not bool(tags & {"sporty", "wellness"}):
            return False
        if pose_id == "stairs_seated":
            return "stairs" in tags or setting_id in {"stairwell_steps", "stone_stairs"}
        if pose_id in {"chair_sideways_pose", "backwards_chair_pose"}:
            return "interior" in tags or setting_id in {"hotel_suite_sitting_area", "bookstore_corner", "walk_in_closet"}
        if pose_id == "side_lying_lounge":
            return setting_id in {"hotel_suite_sitting_area", "marble_primary_bathroom", "poolside_steps"} or "luxury" in tags
        return True

    return predicate


def _pose_for_base_space(base_space: dict[str, Any], style_mode: str = "random") -> Any:
    tags = _scene_semantic_tags(base_space)
    support_tags = _scene_support_tags(base_space)
    base_id = base_space["id"]

    def has_support(*required_tags: str) -> bool:
        return bool(support_tags & set(required_tags))

    def predicate(item: dict[str, Any]) -> bool:
        pose_id = item["id"]
        pose_tags = set(item.get("tags", []))
        if "sport_prep" in pose_tags and not bool(tags & {"sporty", "wellness"}):
            return False
        if "domestic" in pose_tags and bool(tags & {"nightlife", "bar", "night"}):
            return False
        if pose_id == "counter_hip_lean_collar_touch":
            counter_context = bool(tags & {"domestic", "hotelized_living", "dressing_space", "interior"})
            counter_context = counter_context and has_support("counter_support")
            awkward_context = bool(tags & {"bookish", "creative", "coastal", "sporty", "wellness", "outdoor", "travel"})
            return counter_context and not awkward_context
        if pose_id == "bed_kneel_sheet_grip":
            return (base_id in {"hotel_suite_sitting_area"} or bool(tags & {"bedroom"})) and has_support("bed_support")
        if pose_id == "stairs_seated":
            return ("stairs" in tags or base_id == "stair_hall_skylight") and has_support("stairs_support")
        if pose_id in {"chair_sideways_pose", "backwards_chair_pose"}:
            seat_context = bool(tags & {"interior", "luxury", "bookish", "hotelized_living", "dressing_space", "bar"})
            return seat_context and has_support("chair_support", "bench_support", "sofa_support")
        if pose_id == "side_lying_lounge":
            lounge_context = bool(tags & {"luxury", "pool", "coastal", "spa", "bedroom", "hotelized_living"})
            return lounge_context and has_support("bed_support", "sofa_support")
        if pose_id in {"window_turn_teacup", "chess_piece_reach_up", "tea_pour_tray_level", "map_table_both_hands"}:
            return bool(tags & {"bookish"})
        if pose_id == "cabinet_reach_inside":
            if has_support("cabinet_support", "counter_support") and bool(tags & {"domestic", "interior", "hotelized_living", "dressing_space"}):
                return True
            return False
        if pose_id == "pottery_wheel_lift_face":
            return bool(tags & {"creative"})
        if pose_id == "umbrella_over_shoulder_turn":
            return bool(tags & {"outdoor", "coastal"})
        if item.get("group") == "kneeling":
            if base_id in {
                "hotel_suite_sitting_area",
                "boutique_hotel_corridor",
                "hotel_corridor_night",
                "rooftop_hotel_conservatory",
                "hybrid_hotel_lobby_lounge",
                "heritage_hotel_staircase",
                "airport_lounge_evening",
            } and style_mode not in {"luxury", "nightlife", "studio", "fantasy", "cosplay"}:
                return False
            if bool(tags & {"sporty", "wellness", "creative", "studio", "night", "outdoor", "coastal", "pool", "spa", "bathroom", "dressing_space"}) and has_support("floor_support", "stairs_support", "bed_support", "sofa_support", "chair_support"):
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


def _pose_group_predicate(setting_micro: dict[str, Any], pose_group: str) -> Any:
    base = _pose_predicate(setting_micro)

    def predicate(item: dict[str, Any]) -> bool:
        if item.get("group") != pose_group:
            return False
        return base(item)

    return predicate


def _framing_group_predicate(framing_group: str) -> Any:
    return lambda item: item.get("group") == framing_group


def _framing_for_pose(pose_family: dict[str, Any], framing_group: str) -> Any:
    pose_id = pose_family["id"]

    def predicate(item: dict[str, Any]) -> bool:
        if item.get("group") != framing_group:
            return False
        framing_id = item["id"]
        if pose_id in {"reclined_one_knee_up", "side_lying_lounge", "prone_elbows_down"}:
            return framing_id in {"full_body", "knee_up", "cowboy_shot", "waist_up", "bust_up"}
        if pose_id == "slow_walk":
            return framing_id in {"full_body", "knee_up", "cowboy_shot", "waist_up"}
        if pose_id in {"kneeling_both_knees", "one_knee_raised_floor_pose"}:
            return framing_id in {"full_body", "knee_up", "cowboy_shot", "waist_up", "bust_up"}
        if pose_id in {"cross_legged_seated", "one_knee_up_seated", "legs_to_side_pose", "chair_sideways_pose", "backwards_chair_pose", "seated_sideways"}:
            return framing_id in {"full_body", "knee_up", "cowboy_shot", "waist_up", "bust_up", "head_and_shoulders"}
        if pose_id in {"slow_walk", "standing_three_quarter", "wall_lean", "cowboy_shot_stance"}:
            return True
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
    return ", ".join(
        [
            base_space["value"],
            setting_material["value"],
            detail_accent["value"],
            atmosphere_cue["value"],
        ]
    )


def _lookup_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return selectors._lookup_by_id(items)


def _profile_value_set(profile: dict[str, Any], key: str) -> set[str]:
    return selectors._profile_value_set(profile, key)


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
    return selectors._choose_photo_treatment(
        profiles,
        rnd,
        scene_family_id=scene_family_id,
        capture_style_id=capture_style_id,
        lighting_family_id=lighting_family_id,
        time_of_day_id=time_of_day_id,
        style_mode=style_mode,
        mode=mode,
        previous_id=previous_id,
        required_ids=required_ids,
        preferred_ids=preferred_ids,
        deprioritized_ids=deprioritized_ids,
    )


def _normalize_candidate(
    data: dict[str, Any],
    candidate: dict[str, Any],
    *,
    style_mode: str = "random",
    user_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return selectors._normalize_candidate(data, candidate, style_mode=style_mode, user_profile=user_profile)


def _recent_memory_set(memory: dict[str, Any], key: str, count: int) -> set[str]:
    return candidate_builder._recent_memory_set(memory, key, count)


def _push_memory(memory: dict[str, Any], key: str, value: str, max_len: int) -> None:
    candidate_builder._push_memory(memory, key, value, max_len)


def _save_memory(memory: dict[str, Any]) -> None:
    data_loader._save_memory(memory)


def _setting_micro_cap(setting_micro_id: str, setting_micro_rules: dict[str, Any], default_cap: int) -> int:
    return candidate_builder._setting_micro_cap(setting_micro_id, setting_micro_rules, default_cap)


def build_candidate(
    data: dict[str, Any],
    rules: dict[str, Any],
    rnd: random.Random,
    ethnicity_group: str,
    body_group: str,
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
    breast_size_id: str | None = None,
) -> dict[str, Any]:
    return candidate_builder.build_candidate(
        data,
        rules,
        rnd,
        ethnicity_group,
        body_group,
        pose_group,
        framing_group,
        vivid_hair,
        identity_core=identity_core,
        recent_batch=recent_batch,
        previous=previous,
        avoid_setting_micro_ids=avoid_setting_micro_ids,
        scene_family_counts=scene_family_counts,
        style_mode=style_mode,
        preferred_ethnicity_ids=preferred_ethnicity_ids,
        user_profile=user_profile,
        breast_size_id=breast_size_id,
    )


def _effective_capture_text(candidate: dict[str, Any]) -> str:
    return prompt_renderer._effective_capture_text(candidate)


def _effective_lighting_text(candidate: dict[str, Any]) -> str:
    return prompt_renderer._effective_lighting_text(candidate)


def _render_technical_block(
    candidate: dict[str, Any],
    *,
    lighting_override: str | None = None,
    time_override: str | None = None,
) -> str:
    return prompt_renderer._render_technical_block(
        candidate,
        lighting_override=lighting_override,
        time_override=time_override,
    )


def _format_subject_block(candidate: dict[str, Any]) -> str:
    return prompt_renderer._format_subject_block(candidate)


def _format_outfit_block(candidate: dict[str, Any]) -> str:
    return prompt_renderer._format_outfit_block(candidate)


def _format_pose_block(candidate: dict[str, Any]) -> str:
    return prompt_renderer._format_pose_block(candidate)


def render_candidate_segments(candidate: dict[str, Any]) -> dict[str, str]:
    return prompt_renderer.render_candidate_segments(candidate)


def render_candidate_prompt(candidate: dict[str, Any]) -> str:
    return prompt_renderer.render_candidate_prompt(candidate)


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
    return candidate_builder.generate_batch(
        count,
        seed=seed,
        identity_lock=identity_lock,
        persist_memory=persist_memory,
        use_recent_batch_rules=use_recent_batch_rules,
        use_memory_rules=use_memory_rules,
        style_mode=style_mode,
        ethnicity_group_override=ethnicity_group_override,
        preferred_ethnicity_ids=preferred_ethnicity_ids,
        ethnicity_id_pool=ethnicity_id_pool,
        user_profile=user_profile,
        mode=mode,
        spicy_level=spicy_level,
        photo_type_control=photo_type_control,
    )


def persist_batch_memory(batch: list[dict[str, Any]]) -> None:
    candidate_builder.persist_batch_memory(batch)


def generate_candidate(seed: int = 42) -> tuple[dict[str, Any], list[dict[str, str]], dict[str, Any]]:
    return candidate_builder.generate_candidate(seed=seed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--identity-lock", action="store_true")
    parser.add_argument("--render-prompts", action="store_true")
    args = parser.parse_args()

    batch = generate_batch(args.count, seed=args.seed, identity_lock=args.identity_lock)
    if args.render_prompts:
        for item in batch:
            print(render_candidate_prompt(item))
    else:
        print(json.dumps(batch if args.count > 1 else batch[0], indent=2))
