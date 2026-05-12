from __future__ import annotations

import random
from typing import Any

from .constants import ANTI_REPEAT_PROFILES, THEME_HINTS, WOMEN_SCENE_FAMILY_OUTFIT_REVEAL
from .normalizer import _tokenize_text


FANTASY_LOCATION_DOMAIN_TOKENS = {
    "fantasy",
    "castle",
    "wizard",
    "arcane",
    "dragon",
    "elven",
    "dwarven",
    "throne",
    "medieval",
    "witch",
    "temple",
    "catacomb",
    "chapel",
    "tavern",
    "enchanted",
    "haunted",
}
SCI_FI_LOCATION_DOMAIN_TOKENS = {
    "cyberpunk",
    "starship",
    "spaceport",
    "spaceship",
    "space",
    "station",
    "orbital",
    "android",
    "robotics",
    "reactor",
    "cryo",
    "alien",
    "mars",
    "future",
    "futuristic",
    "sci",
    "scifi",
}


def _effective_spicy_level(form_state: dict[str, Any]) -> int:
    normalized = str(form_state.get("spicyLevel", "random")).strip().lower()
    if normalized == "random":
        return random.randint(3, 8)
    try:
        return int(normalized)
    except (TypeError, ValueError):
        return random.randint(3, 8)


def _location_strategy_flags(form_state: dict[str, Any]) -> str:
    strategy = str(form_state.get("locationStrategy", "fresh_only") or "fresh_only").strip().lower()
    if strategy == "random":
        strategy = random.choice(["fresh_only", "allow_repeats"])
    if strategy == "exact_theme" and not form_state.get("exactTheme"):
        return "fresh_only"
    return strategy


def _anti_repeat_profile(form_state: dict[str, Any]) -> dict[str, Any]:
    return ANTI_REPEAT_PROFILES[form_state["antiRepeat"]]


def _resolve_runtime_controls(form_state: dict[str, Any]) -> tuple[int, bool, bool, str, str]:
    spicy_level = _effective_spicy_level(form_state)
    effective_location_strategy = _location_strategy_flags(form_state)
    anti_repeat_profile = _anti_repeat_profile(form_state)
    if effective_location_strategy in {"allow_repeats", "exact_theme"}:
        return spicy_level, False, False, effective_location_strategy, form_state["antiRepeat"]
    return (
        spicy_level,
        anti_repeat_profile["use_recent_batch_rules"],
        anti_repeat_profile["use_memory_rules"],
        effective_location_strategy,
        form_state["antiRepeat"],
    )


def _infer_theme_style_mode(form_state: dict[str, Any]) -> str:
    if form_state["styleMode"] != "random" or not form_state.get("exactTheme"):
        return form_state["styleMode"]
    tokens = set(_tokenize_text(form_state["exactTheme"]))
    style_map = [
        ({"night", "nightlife", "bar", "cocktail", "wine", "club", "neon", "arcade", "karaoke", "lounge"}, "nightlife"),
        ({"studio", "seamless", "backdrop", "portrait"}, "studio"),
        ({"beach", "coastal", "pool", "resort", "marina", "boardwalk", "sea"}, "coastal"),
        ({"book", "library", "bookish", "piano", "record", "salon", "museum"}, "cultural_bookish"),
        ({"garden", "courtyard", "greenhouse", "conservatory", "floral", "botanical"}, "romantic"),
        ({"spa", "wellness", "bath", "bathroom", "shower", "luxury", "penthouse", "hotel", "suite"}, "luxury"),
        ({"city", "urban", "rooftop", "office", "apartment"}, "urban_day"),
        ({"art", "artist", "atelier", "gallery", "creative", "loft"}, "creative_artistic"),
        ({"fantasy", "cosplay", "elf", "warrior", "arcane"}, "fantasy"),
        ({"sport", "fitness", "athletic", "tennis", "workout", "gym"}, "fitness"),
    ]
    for keywords, style_mode in style_map:
        if tokens & keywords:
            return style_mode
    return form_state["styleMode"]


def _matched_theme_hints(exact_theme: str) -> list[dict[str, Any]]:
    if not exact_theme:
        return []
    tokens = set(_tokenize_text(exact_theme))
    if not tokens:
        return []
    matched_hints = [hint for hint in THEME_HINTS if tokens & hint["keywords"]]
    if not matched_hints:
        return []
    best_priority = max(int(hint.get("priority", 0)) for hint in matched_hints)
    return [hint for hint in matched_hints if int(hint.get("priority", 0)) == best_priority]


def _exact_theme_scene_constraints(form_state: dict[str, Any]) -> tuple[set[str], set[str]]:
    if form_state.get("locationStrategy") != "exact_theme" or not form_state.get("exactTheme"):
        return set(), set()
    matched_hints = _matched_theme_hints(form_state["exactTheme"])
    if not matched_hints:
        return set(), set()
    scene_families = set().union(*(set(hint.get("scene_families", set())) for hint in matched_hints))
    routes = set().union(*(set(hint.get("routes", set())) for hint in matched_hints))
    return scene_families, routes


def _exact_theme_location_keywords(form_state: dict[str, Any]) -> set[str]:
    if form_state.get("locationStrategy") != "exact_theme" or not form_state.get("exactTheme"):
        return set()
    generic_location_tokens = {"landing", "stair", "stairs", "corner", "room", "lounge", "hallway", "window", "terrace"}
    specific_tokens = [token for token in _tokenize_text(form_state["exactTheme"]) if token not in generic_location_tokens]
    if not specific_tokens:
        return set()
    return {specific_tokens[-1]}


def _requested_location_domain(form_state: dict[str, Any]) -> str:
    style_mode = str(form_state.get("styleMode", "random") or "random").strip().lower()
    if style_mode in {"fantasy", "cosplay"}:
        return "fantasy_sci_fi"
    exact_theme = str(form_state.get("exactTheme", "") or "").strip()
    if exact_theme:
        tokens = set(_tokenize_text(exact_theme))
        if tokens & (FANTASY_LOCATION_DOMAIN_TOKENS | SCI_FI_LOCATION_DOMAIN_TOKENS):
            return "fantasy_sci_fi"
    return "realism"


def _effective_outfit_reveal(form_state: dict[str, Any], spicy_level: int) -> str:
    if form_state["outfitReveal"] != "random":
        return form_state["outfitReveal"]
    if form_state["mode"] == "women":
        women_scene_family = form_state.get("womenSceneFamily", "random")
        scene_reveal = WOMEN_SCENE_FAMILY_OUTFIT_REVEAL.get(women_scene_family)
        if scene_reveal:
            return scene_reveal
    style_mode = form_state["styleMode"]
    if style_mode in {"cultural_bookish", "old_money"} or form_state["styleVibe"] in {"soft", "clean"}:
        return "reserved"
    if style_mode in {"sport", "fitness"}:
        if spicy_level <= 3:
            return "reserved"
        if spicy_level <= 5:
            return "balanced"
        return "revealing"
    if style_mode in {"lifestyle", "urban_day", "creative_artistic"}:
        if spicy_level <= 3:
            return "reserved"
        return "balanced"
    if spicy_level <= 3:
        return "reserved"
    if spicy_level in {4, 5}:
        return "balanced"
    if spicy_level == 6:
        return "revealing"
    if style_mode in {"random", "luxury", "romantic"}:
        return "revealing"
    return "pushing_it"


def _effective_makeup_control(form_state: dict[str, Any], spicy_level: int) -> str:
    if form_state["makeupControl"] != "random":
        return form_state["makeupControl"]
    if form_state["mode"] == "women":
        women_scene_family = form_state.get("womenSceneFamily", "random")
        if women_scene_family in {"culture_bookish", "urban_daylight"}:
            return "natural_pretty"
        if women_scene_family in {"residential_luxury", "hospitality_suite"}:
            return "soft_glam_clean"
        if women_scene_family in {"grooming_bath", "wellness_spa"}:
            return "clean_minimal"
        if women_scene_family in {"courtyard_garden", "garden_conservatory", "coastal_pool", "coastal_boardwalk"}:
            return "natural_pretty"
        if women_scene_family in {"nightlife_bar", "nightlife_neon"}:
            return "night_out_glam"
        if women_scene_family in {"studio", "creative_gallery"}:
            return "soft_glam_clean"
    if spicy_level <= 3:
        if form_state["styleVibe"] == "clean":
            return "fresh_barely_there"
        if form_state["styleVibe"] in {"soft", "casual"}:
            return "groomed_daylight_soft"
        return "clean_minimal"
    if spicy_level == 4:
        if form_state["styleVibe"] in {"soft", "clean"}:
            return "rosy_polished_minimal"
        return "natural_pretty"
    if form_state["styleVibe"] in {"soft", "casual", "clean"}:
        if form_state["styleVibe"] == "clean":
            return "fresh_barely_there"
        if form_state["styleVibe"] == "soft":
            return "rosy_polished_minimal"
        return "natural_pretty"
    if form_state["styleMode"] == "nightlife" or form_state["styleVibe"] in {"glam", "cinematic", "editorial"} or spicy_level >= 7:
        return "night_out_glam"
    if spicy_level >= 5:
        return "soft_glam_clean"
    return "natural_pretty"
