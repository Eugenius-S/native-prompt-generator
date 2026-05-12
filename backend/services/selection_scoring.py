from __future__ import annotations

import re
from collections import Counter
from typing import Any

from backend.legacy_bridge import preview_male_identities
from backend.engine import generator
from backend.forms.normalizer import _clean_text, _tokenize_text


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
    data = generator.load_data_bank()
    available = {item["id"] for item in data["subjects"]["ethnicities"]}
    return {
        item_id
        for item_id in MOSTLY_MIXED_ETHNICITY_IDS
        if item_id in available
    }


def _random_default_ethnicity_ids() -> set[str]:
    data = generator.load_data_bank()
    return {
        str(item.get("id"))
        for item in data["subjects"]["ethnicities"]
        if str(item.get("group", "")) not in RANDOM_DEFAULT_EXCLUDED_ETHNICITY_GROUPS
    }


def _women_active_high_spicy_pose_ids(spicy_level: int) -> set[str]:
    from backend.services.scoring import HIGH_SPICY_WOMEN_POSE_IDS, HIGH_SPICY_WOMEN_REVEALING_POSE_IDS

    if spicy_level <= 5:
        return set()
    if spicy_level == 6:
        return HIGH_SPICY_WOMEN_REVEALING_POSE_IDS
    return HIGH_SPICY_WOMEN_POSE_IDS


def _women_active_high_spicy_outfit_ids(spicy_level: int) -> set[str]:
    from backend.services.scoring import HIGH_SPICY_WOMEN_OUTFIT_IDS, HIGH_SPICY_WOMEN_REVEALING_OUTFIT_IDS

    if spicy_level <= 5:
        return set()
    if spicy_level == 6:
        return HIGH_SPICY_WOMEN_REVEALING_OUTFIT_IDS
    return HIGH_SPICY_WOMEN_OUTFIT_IDS


def _normalize_age_filter(value: str) -> set[str] | None:
    normalized = value.strip().lower()
    if not normalized or normalized == "random":
        return None
    return AGE_MAP.get(normalized)


def _custom_race_group(custom_race: str) -> str | None:
    lowered = custom_race.lower()
    for group, hints in RACE_GROUP_HINTS.items():
        if any(hint in lowered for hint in hints):
            return group
    return None


def _custom_race_preferences(custom_race: str) -> tuple[str | None, set[str]]:
    cleaned = _clean_text(custom_race)
    if not cleaned:
        return None, set()
    group = _custom_race_group(cleaned)
    data = generator.load_data_bank()
    preferred_ids: set[str] = set()
    lowered = cleaned.lower()
    tokens = set(_tokenize_text(cleaned))
    for ethnicity in data["subjects"]["ethnicities"]:
        value = ethnicity["value"].lower()
        score = 0
        if lowered == value:
            score += 100
        elif lowered in value or value in lowered:
            score += 35
        score += 8 * len(tokens & set(_tokenize_text(value)))
        if group and ethnicity.get("group") == group:
            score += 10
        if score >= 20:
            preferred_ids.add(ethnicity["id"])
    return group, preferred_ids


def _custom_race_candidate_score(candidate: dict[str, Any], custom_race: str) -> int:
    if not custom_race:
        return 0
    lowered = custom_race.lower()
    ethnicity = candidate["ethnicity"].lower()
    tags = {str(tag).lower() for tag in candidate.get("tags", [])}
    score = 0
    if lowered == ethnicity:
        score += 40
    elif lowered in ethnicity or ethnicity in lowered:
        score += 24
    for token in _tokenize_text(custom_race):
        if token in ethnicity:
            score += 10
        if token in tags:
            score += 4
    group = _custom_race_group(custom_race)
    if group and candidate.get("ethnicity_group") == group:
        score += 20
    return score


def _couples_different_persons_identity_constraints(form_state: dict[str, Any]) -> dict[str, set[str]]:
    if form_state.get("mode") != "couples" or form_state.get("personMode") != "different_persons":
        return {}
    constraints: dict[str, set[str]] = {}
    allowed_ages = _normalize_age_filter(form_state.get("age", "Random"))
    if allowed_ages:
        constraints["required_age_band_ids"] = set(allowed_ages)
    if form_state.get("racePreset") == "other" and form_state.get("customRace"):
        _, preferred_ethnicity_ids = _custom_race_preferences(form_state["customRace"])
        if preferred_ethnicity_ids:
            constraints["required_ethnicity_ids"] = set(preferred_ethnicity_ids)
            constraints["preferred_ethnicity_ids"] = set(preferred_ethnicity_ids)
    elif form_state.get("racePreset") in SAME_PERSON_ETHNICITY_IDS:
        constraints["required_ethnicity_ids"] = {form_state["racePreset"]}
        constraints["preferred_ethnicity_ids"] = {form_state["racePreset"]}
    return constraints


def _male_age_matches_request(age_text: str, requested: str) -> bool:
    normalized = str(requested or "random").strip().lower()
    if normalized in {"", "random"}:
        return True
    match = re.search(r"(\d{2})", age_text or "")
    if not match:
        return False
    age_number = int(match.group(1))
    if normalized.startswith("young "):
        return age_number == int(normalized.split()[-1])
    if normalized == "18-20":
        return 18 <= age_number <= 20
    if normalized == "21-23":
        return 21 <= age_number <= 23
    if normalized == "25-30":
        return 25 <= age_number <= 30
    if normalized == "30+":
        return age_number >= 30
    return age_number == int(normalized) if normalized.isdigit() else False


def _custom_race_matches_identity_text(custom_race: str, identity: dict[str, Any]) -> bool:
    cleaned_custom_race = _clean_text(custom_race).lower()
    if not cleaned_custom_race:
        return False
    identity_ethnicity = _clean_text(identity.get("ethnicity", "")).lower()
    if identity_ethnicity and (
        cleaned_custom_race == identity_ethnicity
        or cleaned_custom_race in identity_ethnicity
        or identity_ethnicity in cleaned_custom_race
    ):
        return True
    custom_tokens = set(_tokenize_text(cleaned_custom_race))
    identity_tokens = set(_tokenize_text(identity_ethnicity))
    if custom_tokens and len(custom_tokens & identity_tokens) >= max(1, min(2, len(custom_tokens))):
        return True
    custom_group = _custom_race_group(cleaned_custom_race)
    return bool(custom_group) and str(identity.get("ethnicity_group", "") or "").lower() == custom_group


def _male_race_matches_request(male_identity: dict[str, Any], race_preset: str, custom_race: str = "") -> bool:
    if race_preset == "random_default_split":
        return True
    if race_preset == "other":
        if not custom_race:
            return True
        group, preferred_ethnicity_ids = _custom_race_preferences(custom_race)
        if preferred_ethnicity_ids and male_identity.get("_ethnicity_id") in preferred_ethnicity_ids:
            return True
        if _custom_race_matches_identity_text(custom_race, male_identity):
            return True
        return bool(group) and male_identity.get("ethnicity_group") == group
    if race_preset in SAME_PERSON_ETHNICITY_IDS:
        return male_identity.get("_ethnicity_id") == race_preset
    target_group = SAME_PERSON_RACE_GROUPS.get(race_preset)
    if target_group:
        return male_identity.get("ethnicity_group") == target_group
    return True


def _explicit_male_identity_constraints_active(form_state: dict[str, Any]) -> bool:
    if form_state.get("mode") != "couples":
        return False
    male_age = str(form_state.get("maleAge", "Random") or "Random").strip().lower()
    male_race = str(form_state.get("maleRacePreset", "random_default_split") or "random_default_split").strip()
    male_custom_race = str(form_state.get("maleCustomRace", "") or "").strip()
    return male_age not in {"", "random"} or male_race != "random_default_split" or bool(male_custom_race)


def _couples_male_identity_score(
    batch: list[dict[str, Any]],
    form_state: dict[str, Any],
    style_mode: str,
    seed: int,
) -> tuple[int, bool]:
    if form_state.get("mode") != "couples" or not _explicit_male_identity_constraints_active(form_state):
        return 0, False
    male_age_value = str(form_state.get("maleAge", "Random") or "Random")
    male_race_preset = str(form_state.get("maleRacePreset", "random_default_split") or "random_default_split")
    male_custom_race = str(form_state.get("maleCustomRace", "") or "")
    male_identities = preview_male_identities("couples", batch, form_state, style_mode, seed)
    score = 0
    hard_fail = False
    if male_age_value.strip().lower() not in {"", "random"}:
        age_matches = sum(1 for male_identity in male_identities if _male_age_matches_request(str(male_identity.get("age", "")), male_age_value))
        age_misses = len(male_identities) - age_matches
        score += age_matches * 12 - age_misses * 24
        if age_misses:
            hard_fail = True
    if male_race_preset != "random_default_split" or male_custom_race:
        race_matches = sum(1 for male_identity in male_identities if _male_race_matches_request(male_identity, male_race_preset, male_custom_race))
        race_misses = len(male_identities) - race_matches
        score += race_matches * 12 - race_misses * 24
        if race_misses:
            hard_fail = True
    return score, hard_fail


def _race_score(batch: list[dict[str, Any]], race_preset: str, custom_race: str = "") -> int:
    if race_preset == "random_default_split":
        return 0
    if race_preset == "other":
        return sum(_custom_race_candidate_score(candidate, custom_race) for candidate in batch)
    if race_preset in SAME_PERSON_ETHNICITY_IDS:
        return sum(24 if candidate["ethnicity_id"] == race_preset else -24 for candidate in batch)
    groups = [candidate["ethnicity_group"] for candidate in batch]
    counts = Counter(groups)
    size = len(batch)
    if race_preset == "mostly_mixed":
        unique_ids = {candidate.get("ethnicity_id") for candidate in batch}
        mixed_hits = sum(1 for candidate in batch if candidate.get("ethnicity_group") in MIXED_ETHNICITY_GROUPS)
        return min(80, len(unique_ids) * 4 + len(counts) * 8 + mixed_hits)
    target_map = {
        "mostly_whites": "white",
        "mostly_blacks": "black",
        "mostly_asian": "asian",
        "mostly_latina": "latina",
    }
    target = target_map.get(race_preset)
    if not target:
        return 0
    return counts.get(target, 0) * 18 - (size - counts.get(target, 0)) * 12


def _body_score(batch: list[dict[str, Any]], preset: str) -> int:
    if preset == "random_balanced":
        return 0
    groups = [candidate["body_group"] for candidate in batch]
    counts = Counter(groups)
    if preset == "slim_lean":
        return counts.get("lean", 0) * 10
    if preset == "toned":
        return counts.get("toned", 0) * 10
    if preset == "athletic":
        return counts.get("athletic", 0) * 10
    if preset == "curvy":
        return counts.get("curvy", 0) * 10
    if preset == "mixed_curvy_accent":
        return counts.get("curvy", 0) * 8 + (len(counts) > 1) * 10
    if preset == "mixed_athletic_accent":
        return counts.get("athletic", 0) * 8 + (len(counts) > 1) * 10
    return 0


def _style_score(candidate: dict[str, Any], style_mode: str) -> int:
    if style_mode == "random":
        return 0
    scene = candidate["scene_family_id"]
    route = candidate["route"]
    capture = candidate["capture_style_id"]
    tags = set(candidate.get("tags", []))
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
    score = 0
    if scene in scenes:
        score += 10
    if route in routes:
        score += 8
    if capture in captures:
        score += 6
    if style_mode in {"sport", "fitness"} and {"sporty", "athletic"} & tags:
        score += 8
    if style_mode == "sport":
        score += 12 if candidate["outfit_family_id"] == "crop_top_mini_skirt" else -18
        score += 12 if candidate["material_id"] == "athletic_jersey" else -10
        score += 10 if candidate["scene_family_id"] == "urban_daylight" else -16
        score += 8 if candidate["route"] == "sports_flirt" else -14
        score += 4 if candidate["hair_structure_id"] == "high_ponytail" else 0
    if style_mode == "fitness":
        fitness_safe_outfits = {"polo_pleated_skirt", "workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"}
        fitness_safe_colors = {"sport_clean_white", "navy_cream", "earthy_soft", "powder_blue", "clean_neutrals"}
        score += 14 if candidate["outfit_family_id"] in fitness_safe_outfits else -20
        score -= 26 if candidate["outfit_family_id"] == "crop_top_mini_skirt" else 0
        score += 12 if candidate["material_id"] == "athletic_jersey" else -8
        score += 12 if candidate["scene_family_id"] in {"urban_daylight", "wellness_spa"} else -16
        score += 10 if candidate["route"] in {"sports_flirt", "luxury_interior"} else -14
        score += 6 if candidate["hair_structure_id"] == "high_ponytail" else 0
        score += 8 if candidate.get("color_story_id") in fitness_safe_colors else -6
        score += 6 if candidate["scene_family_id"] == "wellness_spa" else 0
        score += 4 if {"wellness", "sporty"} & tags else 0
    if style_mode in {"old_money", "luxury"} and "luxury" in tags:
        score += 6
    if style_mode == "nightlife" and candidate.get("material_id") == "vinyl_latex":
        score -= 28
    if style_mode == "nightlife":
        if candidate.get("outfit_family_id") == "mini_dress":
            score -= 4
        if candidate.get("outfit_family_id") in {"cami_midi_skirt", "wrap_blouse_skirt", "column_dress", "halter_trousers", "silk_blouse_midi_skirt"}:
            score += 6
    if style_mode == "lifestyle":
        if candidate.get("outfit_family_id") == "mini_dress":
            score -= 8
        if candidate.get("outfit_family_id") in {"blazer_mini_dress", "bodysuit_trousers", "corset_trousers"}:
            score -= 12
        if candidate.get("color_story_id") in {"black_gold", "oxblood_noir", "emerald_noir", "hot_pink"}:
            score -= 10
    if style_mode == "random":
        if candidate.get("outfit_family_id") == "mini_dress":
            score -= 8
        if candidate.get("outfit_family_id") in {"column_dress", "wrap_blouse_skirt", "vest_trousers", "blouse_trousers", "shirt_trousers", "cami_midi_skirt", "silk_blouse_midi_skirt", "mockneck_knit_skirt", "cashmere_shell_trousers", "structured_day_dress"}:
            score += 6
        if candidate.get("color_story_id") == "clean_neutrals":
            score -= 4
    if style_mode == "romantic":
        if candidate.get("scene_family_id") == "coastal_pool":
            score -= 10
        if candidate.get("outfit_family_id") in {"cami_midi_skirt", "wrap_blouse_skirt", "column_dress", "halter_trousers", "silk_blouse_midi_skirt", "structured_day_dress", "mockneck_knit_skirt"}:
            score += 8
        if candidate.get("outfit_family_id") in {"corset_trousers", "bodysuit_trousers", "blazer_mini_dress", "cardigan_skirt"}:
            score -= 10
        if candidate.get("outfit_family_id") in {"blouse_trousers", "knit_top_trousers", "cardigan_trousers", "sweater_jeans"}:
            score -= 6
    if style_mode == "luxury":
        if candidate.get("outfit_family_id") == "mini_dress":
            score -= 12
        if candidate.get("outfit_family_id") in {"column_dress", "wrap_blouse_skirt", "vest_trousers", "blouse_trousers", "cami_midi_skirt", "halter_trousers", "cashmere_shell_trousers", "structured_day_dress", "silk_blouse_midi_skirt"}:
            score += 8
        if candidate.get("color_story_id") == "clean_neutrals":
            score -= 6
    if style_mode == "creative_artistic":
        if candidate.get("outfit_family_id") in {"vest_trousers", "column_dress", "wrap_blouse_skirt", "halter_trousers", "apron_workshop_trousers", "silk_blouse_midi_skirt"}:
            score += 10
        if candidate.get("color_story_id") in {"slate_blue_ink", "rosewood_smoke", "black_gold", "emerald_noir"}:
            score += 6
        if candidate.get("outfit_family_id") in {"polo_pleated_skirt", "workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"}:
            score -= 18
        if candidate.get("outfit_family_id") == "mini_dress":
            score -= 8
    return score
