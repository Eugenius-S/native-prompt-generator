from __future__ import annotations

import functools
import math
import random
import re
from typing import Any

from backend.engine import generator, line_bank_loader


WHITE_GROUP = "white"
RACE_PRESET_TO_GROUP = {
    "mostly_whites": "white",
    "mostly_blacks": "black",
    "mostly_asian": "asian",
    "mostly_latina": "latina",
}

MALE_BODY_BY_PRESET = {
    "random_balanced": ["lean athletic build", "athletic build", "broad-shouldered build", "solid build"],
    "slim_lean": ["lean build", "lean athletic build"],
    "toned": ["toned build", "defined athletic build"],
    "athletic": ["athletic build", "muscular athletic build"],
    "curvy": ["solid broad build", "thick solid build"],
    "mixed_curvy_accent": ["solid athletic build", "broad-shouldered build", "solid build"],
    "mixed_athletic_accent": ["athletic build", "lean athletic build", "defined athletic build"],
}

MALE_HAIR_BY_LENGTH = {
    "short": ["textured crop", "messy short hair", "clean side-part hair", "short tapered hair"],
    "medium": ["medium textured hair", "slightly longer swept hair", "medium side-part hair"],
    "long": ["shoulder-length hair", "long loose hair", "long tied-back hair"],
}

MALE_GROOMING_BY_STYLE = {
    "random": ["clean-shaven", "light stubble", "trimmed beard"],
    "studio": ["clean-shaven", "light stubble"],
    "luxury": ["light stubble", "trimmed beard"],
    "old_money": ["light stubble", "trimmed beard"],
    "sport": ["clean-shaven", "light stubble"],
    "fitness": ["clean-shaven", "light stubble"],
    "nightlife": ["light stubble", "trimmed beard"],
    "fantasy": ["light stubble", "trimmed beard"],
}

MALE_GROOMING_LABELS = {
    "clean_shaven": "clean-shaven",
    "light_stubble": "light stubble",
    "trimmed_beard": "trimmed beard",
}

MALE_OUTFITS = {
    "random": [
        "fitted t-shirt with relaxed trousers",
        "open collar shirt with tailored trousers",
        "clean knit polo with dark trousers",
    ],
    "studio": [
        "fitted black t-shirt with tailored trousers",
        "clean white tank with dark trousers",
    ],
    "lifestyle": [
        "clean t-shirt with straight jeans",
        "light overshirt over a fitted tee with relaxed trousers",
    ],
    "luxury": [
        "open collar shirt with tailored trousers",
        "fine knit polo with pleated trousers",
        "dark silk shirt with sharply tailored trousers",
        "lightweight blazer over a fine knit top with tailored trousers",
    ],
    "old_money": [
        "light linen shirt with pleated trousers",
        "fine gauge knit polo with cream trousers",
    ],
    "romantic": [
        "soft open shirt with tailored trousers",
        "clean henley with dark trousers",
        "fine knit sweater with dark tailored trousers",
        "soft linen shirt with relaxed pleated trousers",
        "fitted merino crewneck with slim dark trousers",
    ],
    "vacation": [
        "light resort shirt with relaxed shorts",
        "linen shirt with drawstring trousers",
    ],
    "sport": [
        "fitted athletic t-shirt with training shorts",
        "clean performance tank with track pants",
    ],
    "fitness": [
        "fitted compression tee with gym shorts",
        "sleeveless training top with performance shorts",
    ],
    "cosplay": [
        "stylized leather-look jacket over a fitted base layer",
        "cinematic costume-inspired shirt with dark trousers",
    ],
    "fantasy": [
        "cinematic fantasy tunic with fitted dark trousers",
        "layered hero-style shirt with a leather belt detail",
    ],
    "nightlife": [
        "dark fitted shirt with slim trousers",
        "black knit polo with sharp dark trousers",
    ],
    "cultural_bookish": [
        "fine knit sweater with tailored trousers",
        "soft collared shirt with dark wool trousers",
    ],
    "creative_artistic": [
        "relaxed artist shirt with dark trousers",
        "washed tee under a cropped jacket with loose trousers",
    ],
    "urban_day": [
        "fitted tee with straight trousers",
        "clean zip jacket over a t-shirt with jeans",
    ],
    "coastal": [
        "light linen shirt with resort shorts",
        "open resort shirt with easy trousers",
    ],
}

MALE_OUTFIT_CONTROL_ALIASES = {
    "male_open_collar_trousers": "luxury",
    "male_fineknit_trousers": "old_money",
    "male_track_jacket_joggers": "sport",
    "male_relaxed_overshirt_trousers": "lifestyle",
    "male_dark_shirt_trousers": "nightlife",
    "male_black_polo_trousers": "nightlife",
    "male_linen_pleated_trousers": "coastal",
    "male_blazer_knit_trousers": "old_money",
}

MALE_RANDOM_OUTFIT_VIBES_BY_SCENE = {
    "culture_bookish": "cultural_bookish",
    "residential_luxury": "luxury",
    "hospitality_suite": "luxury",
    "grooming_bath": "lifestyle",
    "courtyard_garden": "romantic",
    "garden_conservatory": "romantic",
    "coastal_pool": "coastal",
    "coastal_boardwalk": "coastal",
    "nightlife_bar": "nightlife",
    "nightlife_neon": "nightlife",
    "studio": "studio",
    "creative_gallery": "creative_artistic",
    "wellness_spa": "lifestyle",
    "urban_daylight": "urban_day",
}

MALE_POSES = {
    "random": [
        "standing with a slight torso turn, one hand near his pocket and eyes on camera",
        "leaning in with relaxed shoulders and an easy half-smile",
        "casual stance with a slight head tilt and a confident smile",
        "one hand resting on a ledge with relaxed shoulders and a calm look",
    ],
    "studio": [
        "standing with one shoulder forward and calm direct eye contact",
        "seated slightly sideways with relaxed hands and a steady gaze",
        "relaxed lean with a slight head tilt and quiet direct eye contact",
    ],
    "lifestyle": [
        "casual stance with a slight head tilt and a confident smile",
        "relaxed lean with one shoulder forward and easy direct eye contact",
    ],
    "luxury": [
        "one hand resting on a ledge with calm direct eye contact",
        "standing tall with relaxed shoulders and a composed half-smile",
        "seated in a lounge chair with one forearm resting lightly and a composed stare",
        "adjusting one cuff with relaxed shoulders and calm direct eye contact",
        "standing near the window with one hand in his pocket and a quiet confident look",
        "leaning lightly against a polished bar with squared shoulders and an easy composed expression",
        "standing in a slight quarter turn with carved window light and a composed editorial gaze",
        "resting one hand at his jacket hem with still posture and a controlled campaign look",
    ],
    "old_money": [
        "relaxed lean with a mild smile and tidy composed posture",
        "standing near a chair with one hand resting lightly on the backrest",
    ],
    "romantic": [
        "leaning slightly in with softened shoulders and a warm look",
        "standing relaxed with an easy smile and steady eye contact",
        "seated slightly turned with softened shoulders and a quiet affectionate gaze",
        "standing close to the camera with one hand near his pocket and a warm half-smile",
        "leaning lightly on a doorway with relaxed posture and a gentle direct look",
        "resting one hand on the back of a chair with softened shoulders and an easy romantic smile",
        "standing with one hand in his pocket and a quiet softened smile",
        "leaning with one elbow against the set and a warm reflective gaze",
        "seated with relaxed shoulders and a gentle half-smile",
    ],
    "vacation": [
        "easy resort stance with one hand near his pocket and a sunlit squint",
        "leaning on a terrace rail with relaxed shoulders and a calm look",
    ],
    "sport": [
        "mid-step with one shoulder forward and an athletic ready posture",
        "standing in a relaxed post-workout stance with hands busy and weight shifted",
    ],
    "fitness": [
        "mid-step with an athletic ready posture and squared shoulders",
        "resting after a workout with a relaxed chest-forward stance and focused eye contact",
    ],
    "nightlife": [
        "leaning slightly closer with one shoulder forward and a confident nightlife read",
        "standing angled to camera with one hand low and a controlled flirt read",
    ],
    "cultural_bookish": [
        "seated with one forearm on the table and a calm reading-room gaze",
        "standing beside a shelf with one hand on a book spine and eyes on camera",
    ],
    "creative_artistic": [
        "one hand resting on a workbench with a composed look",
        "standing near an easel with a slight head tilt and easy focus",
    ],
    "urban_day": [
        "casual stance with head tilt and a confident smile",
        "one hand resting on a rail with relaxed shoulders and eyes on camera",
    ],
    "coastal": [
        "easy resort stance with one shoulder forward and a calm sunlit look",
        "leaning lightly on a terrace rail with relaxed posture and direct eye contact",
    ],
    "cosplay": [
        "standing with squared shoulders and a composed heroic stare",
        "one hand near his belt and the other resting on a ledge with a confident half-smile",
    ],
    "fantasy": [
        "standing with squared shoulders and a composed heroic stare",
        "one hand near his belt and the other resting on a ledge with a confident half-smile",
    ],
}

COUPLE_INTERACTIONS = {
    "random": [
        "standing close with his hand at her waist and her body angled slightly toward him",
        "holding each other lightly with their shoulders turned off-axis toward camera",
        "standing side by side holding hands with relaxed shoulders and an easy shared look",
        "walking slowly together with their bodies angled slightly toward each other",
        "standing close with her leaning lightly into his shoulder and both looking toward camera",
        "seated together on the edge of a bench with their knees turned slightly toward each other",
        "standing with one of her arms looped through his while both keep an easy shared posture",
    ],
    "lifestyle": [
        "standing side by side holding hands with relaxed shoulders and an easy shared look",
        "walking slowly together with their shoulders lightly brushing and an easy shared smile",
        "standing close with her leaning lightly into him and both bodies turned gently toward camera",
        "seated together on the edge of a bench with calm body language and an easy shared look",
        "standing close with one of her arms looped through his and relaxed everyday chemistry",
    ],
    "luxury": [
        "standing close with his hand at her waist and her shoulder turned elegantly toward him",
        "holding hands with composed posture and a quiet luxury-campaign chemistry",
        "seated together in a lounge setting with her body angled toward him and calm intimate posture",
        "standing with her resting lightly against him and both holding a composed editorial gaze",
        "woman seated lightly on his lap with elegant posture and restrained intimate chemistry",
    ],
    "old_money": [
        "standing side by side with linked arms and quiet elegant chemistry",
        "walking together with calm posture and understated close body language",
        "seated together with relaxed shoulders and a quiet shared look",
    ],
    "romantic": [
        "leaning into each other with his hand at her waist and a soft cheek-near-cheek closeness",
        "holding each other close with intimate body language and a slight camera angle",
        "standing forehead-near-forehead with soft body language and quiet romantic closeness",
        "seated close together with her leaning into his shoulder and a warm shared look",
        "holding hands with their bodies turned gently toward each other and soft romantic chemistry",
        "woman seated lightly on his lap with softened shoulders and intimate relaxed closeness",
    ],
    "nightlife": [
        "standing close in a charged nightlife pose with his hand at her waist and her shoulder turned toward him",
        "holding each other in a confident late-night pose with their bodies angled off-axis",
        "standing close with one hand low at her waist and a confident late-night shoulder-to-shoulder pose",
        "walking together through the scene with charged nightlife chemistry and an off-axis fashion read",
        "seated together in a banquette pose with her leaning into him and a confident after-dark read",
    ],
    "sport": [
        "moving together in a sporty flirt pose with his hand brushing her waist and both bodies angled dynamically",
        "standing close in an athletic couple pose with easy touch and active weight shift",
        "walking together mid-step with playful athletic chemistry and light hand contact",
        "standing shoulder to shoulder with one of his hands near her waist and a shared post-workout grin",
    ],
    "fitness": [
        "moving together in a toned athletic pose with close body language and a slight camera angle",
        "standing close after a workout with one hand at her waist and a playful shared look",
        "walking side by side after a workout with relaxed shoulders and easy couple chemistry",
        "seated together on a recovery bench with their knees turned toward each other and a shared calm look",
        "standing shoulder to shoulder with a water-break closeness and light hand contact",
    ],
}

MALE_MOODS = {
    "random": "easy confident energy, direct eye contact",
    "studio": "calm studio confidence, direct eye contact",
    "lifestyle": "easy confident energy, direct eye contact",
    "luxury": "composed confident energy, direct eye contact",
    "old_money": "quiet composed energy, direct eye contact",
    "romantic": "warm composed energy, direct eye contact",
    "vacation": "relaxed resort confidence, direct eye contact",
    "sport": "athletic confident energy, direct eye contact",
    "fitness": "athletic focused energy, direct eye contact",
    "cosplay": "controlled cinematic confidence, direct eye contact",
    "fantasy": "controlled heroic energy, direct eye contact",
    "nightlife": "controlled late-night confidence, direct eye contact",
    "cultural_bookish": "quiet intelligent energy, direct eye contact",
    "creative_artistic": "creative composed energy, direct eye contact",
    "urban_day": "easy city confidence, direct eye contact",
    "coastal": "relaxed coastal confidence, direct eye contact",
}

COUPLE_MOODS = {
    "random": "easy couple chemistry, attention on each other",
    "studio": "clean editorial chemistry, sharing a locked-in frame",
    "lifestyle": "easy close chemistry, drawn toward each other",
    "luxury": "composed intimate chemistry, absorbed in each other",
    "old_money": "quiet elegant chemistry, held between them",
    "romantic": "soft romantic chemistry, attention on each other",
    "vacation": "relaxed getaway chemistry, bodies angled together",
    "sport": "playful athletic chemistry, moving with each other",
    "fitness": "playful athletic chemistry, moving with each other",
    "cosplay": "cinematic duo energy, locked into each other",
    "fantasy": "cinematic duo energy, locked into each other",
    "nightlife": "charged nightlife chemistry, pulled into each other",
    "cultural_bookish": "quiet close chemistry, attention on each other",
    "creative_artistic": "creative couple chemistry, absorbed in each other",
    "urban_day": "easy city chemistry, bodies angled together",
    "coastal": "relaxed coastal chemistry, drawn toward each other",
}

COUPLE_MALE_COLOR_CHOICES = {
    "random": ["charcoal", "deep navy", "stone", "espresso", "soft black"],
    "lifestyle": ["charcoal", "deep navy", "stone", "soft black"],
    "luxury": ["charcoal", "espresso", "deep navy", "stone", "cream"],
    "old_money": ["cream", "stone", "deep navy", "taupe", "soft black"],
    "romantic": ["charcoal", "deep navy", "stone", "cream", "espresso"],
    "vacation": ["white", "stone", "sand", "deep navy", "cream"],
    "sport": ["charcoal", "white", "deep navy", "graphite", "black"],
    "fitness": ["charcoal", "white", "deep navy", "graphite", "black"],
    "nightlife": ["soft black", "charcoal", "deep navy", "espresso", "graphite"],
    "cultural_bookish": ["charcoal", "deep navy", "stone", "espresso"],
    "creative_artistic": ["charcoal", "deep navy", "stone", "washed black"],
    "urban_day": ["charcoal", "deep navy", "stone", "soft black"],
    "coastal": ["white", "stone", "sand", "deep navy", "cream"],
}

FEMALE_COLOR_TO_AVOID_MALE = {
    "clean_neutrals": {"stone", "cream", "white"},
    "hot_pink": {"rose", "pink"},
    "powder_blue": {"sky blue", "powder blue", "light blue"},
    "lime_pop": {"lime", "green"},
    "navy_cream": {"navy", "cream"},
    "earthy_soft": {"olive", "tan", "brown"},
    "winter_neutrals": {"stone", "cream", "white"},
    "sport_clean_white": {"white"},
    "black_gold": {"black", "gold"},
    "oxblood_noir": {"oxblood", "burgundy", "black"},
    "emerald_noir": {"emerald", "green", "black"},
}


def _beauty_phrase(beauty_level: str) -> str:
    return {
        "beautified and flattering": "flattering read",
        "beautified with polished glam appeal": "polished glam read",
    }.get(beauty_level, f"{beauty_level} read")


def _age_phrase(value: str) -> str:
    return str(value).replace(" years old", "-year-old")


def _article_for(value: str) -> str:
    return "an" if (value or "").strip().lower()[:1] in {"a", "e", "i", "o", "u"} else "a"


def _coerce_spicy_level(value: Any, default: int = 3) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _normalize_group(race_preset: str) -> str | None:
    return RACE_PRESET_TO_GROUP.get(race_preset)


def _masculinize_ethnicity(value: str) -> str:
    replacements = {
        "Latina": "Latino",
        "Filipina": "Filipino",
    }
    cleaned = value.strip()
    for source, target in replacements.items():
        if cleaned.endswith(source):
            return cleaned[: -len(source)] + target
    return cleaned


def _extract_age_number(value: str) -> int | None:
    match = re.search(r"(\d{2})", value or "")
    return int(match.group(1)) if match else None


def _pick_age_text(rnd: random.Random, requested: str, *, floor: int = 18) -> str:
    normalized = str(requested or "random").strip().lower()
    age_map = {
        "18": ["18 years old"],
        "young 18": ["18 years old"],
        "18-20": ["18 years old", "19 years old", "20 years old"],
        "19": ["19 years old"],
        "young 19": ["19 years old"],
        "20": ["20 years old"],
        "young 20": ["20 years old"],
        "21": ["21 years old"],
        "young 21": ["young 21 years old"],
        "21-23": ["21 years old", "22 years old", "23 years old"],
        "22": ["22 years old"],
        "young 22": ["22 years old"],
        "23": ["23 years old"],
        "young 23": ["23 years old"],
        "25": ["25 years old"],
        "26": ["26 years old"],
        "27": ["27 years old"],
        "28": ["28 years old"],
        "29": ["29 years old"],
        "25-30": ["25 years old", "27 years old", "29 years old", "30 years old"],
        "30+": ["32 years old", "38 years old"],
        "random": ["18 years old", "19 years old", "20 years old", "21 years old", "22 years old", "23 years old", "25 years old", "27 years old", "32 years old"],
    }
    choices = age_map.get(normalized, age_map["random"])
    chosen = rnd.choice(choices)
    age_number = _extract_age_number(chosen)
    if age_number is not None and age_number < floor:
        return f"{floor} years old"
    return chosen


def _pick_ethnicity_entry(
    rnd: random.Random,
    data: dict[str, Any],
    race_preset: str,
    *,
    preferred_group: str | None = None,
    exclude_value: str | None = None,
) -> dict[str, Any]:
    ethnicities = list(data["subjects"]["ethnicities"])
    exact_match = next((item for item in ethnicities if item.get("id") == race_preset), None)
    if exact_match:
        return exact_match
    group = preferred_group or _normalize_group(race_preset)
    pool = ethnicities
    if group:
        pool = [item for item in pool if item.get("group") == group] or ethnicities
    elif race_preset == "random_default_split":
        filtered = [item for item in pool if item.get("group") not in {"middle_eastern", "south_asian"}]
        if filtered:
            pool = filtered
    if exclude_value:
        filtered = [item for item in pool if item["value"] != exclude_value]
        if filtered:
            pool = filtered
    weights = [max(float(item.get("weight", 0.01)), 0.01) for item in pool]
    return rnd.choices(pool, weights=weights, k=1)[0]


def _custom_identity_text(custom_race: str, target: str) -> str:
    cleaned = " ".join((custom_race or "").strip().split())
    if not cleaned:
        return f"{target}"
    lowered = cleaned.lower()
    if any(word in lowered for word in ("woman", "women", "girl", "man", "men", "boy", "couple")):
        return cleaned
    suffix = {"woman": "woman", "man": "man", "couple": "couple"}[target]
    return f"{cleaned} {suffix}"


def _choose_male_body(rnd: random.Random, preset: str) -> str:
    return rnd.choice(MALE_BODY_BY_PRESET.get(preset, MALE_BODY_BY_PRESET["random_balanced"]))


@functools.lru_cache(maxsize=1)
def _male_styling_bank() -> dict[str, list[dict[str, Any]]]:
    styling = generator.load_data_bank().get("styling", {})
    return {
        "hair_structures": [item for item in styling.get("hair_structures", []) if "male" in item.get("tags", [])],
        "outfit_families": [item for item in styling.get("outfit_families", []) if "male" in item.get("tags", [])],
    }


def _style_item_by_id(items: list[dict[str, Any]], item_id: str) -> dict[str, Any] | None:
    for item in items:
        if item.get("id") == item_id:
            return item
    return None


def _weighted_style_value(rnd: random.Random, items: list[dict[str, Any]]) -> str:
    weights = [max(float(item.get("weight", 0.0)), 0.01) for item in items]
    return rnd.choices(items, weights=weights, k=1)[0]["value"]


def _male_length_tag(length: str) -> str:
    return {"short": "short_hair", "medium": "medium_hair", "long": "long_hair"}.get(length, "short_hair")


def _male_style_tags(style_mode: str) -> set[str]:
    return {
        "random": {"lifestyle", "creative_artistic", "nightlife", "coastal", "vacation"},
        "lifestyle": {"lifestyle"},
        "luxury": {"luxury", "romantic", "old_money"},
        "old_money": {"old_money", "coastal", "luxury"},
        "romantic": {"romantic", "lifestyle", "old_money", "coastal"},
        "vacation": {"vacation", "coastal", "old_money"},
        "sport": {"sport", "fitness", "urban_day"},
        "fitness": {"fitness", "sport", "urban_day"},
        "nightlife": {"nightlife", "luxury"},
        "cultural_bookish": {"cultural_bookish", "old_money", "lifestyle"},
        "creative_artistic": {"creative_artistic", "urban_day", "lifestyle"},
        "urban_day": {"urban_day", "lifestyle", "creative_artistic"},
        "coastal": {"coastal", "vacation", "old_money"},
    }.get(style_mode, set())


def _male_style_items(items: list[dict[str, Any]], style_mode: str) -> list[dict[str, Any]]:
    style_tags = _male_style_tags(style_mode)
    if not style_tags:
        return []
    return [item for item in items if style_tags & set(item.get("tags", []))]


def _normalize_male_outfit_control(outfit_control: str) -> str:
    normalized = str(outfit_control or "random").strip().lower()
    return MALE_OUTFIT_CONTROL_ALIASES.get(normalized, normalized)


def _male_outfit_vibe_for_scene(scene_family_id: str, fallback_style_mode: str) -> str:
    scene_key = str(scene_family_id or "").strip().lower()
    if scene_key in MALE_RANDOM_OUTFIT_VIBES_BY_SCENE:
        return MALE_RANDOM_OUTFIT_VIBES_BY_SCENE[scene_key]
    if "nightlife" in scene_key or any(token in scene_key for token in {"bar", "club", "neon", "cocktail", "lounge"}):
        return "nightlife"
    if any(token in scene_key for token in {"coastal", "beach", "pool", "resort", "boardwalk", "marina", "sea"}):
        return "coastal"
    if any(token in scene_key for token in {"book", "library", "culture", "bookish", "salon"}):
        return "cultural_bookish"
    if any(token in scene_key for token in {"luxury", "hotel", "suite", "penthouse"}):
        return "luxury"
    if any(token in scene_key for token in {"garden", "courtyard", "greenhouse", "conservatory"}):
        return "romantic"
    if any(token in scene_key for token in {"creative", "gallery", "artist", "atelier", "loft"}):
        return "creative_artistic"
    if any(token in scene_key for token in {"studio", "backdrop", "portrait"}):
        return "studio"
    if any(token in scene_key for token in {"sport", "fitness", "gym", "athletic", "workout"}):
        return "sport" if "sport" in scene_key else "fitness"
    if any(token in scene_key for token in {"urban", "city", "apartment", "daylight", "street"}):
        return "urban_day"
    if any(token in scene_key for token in {"wellness", "spa", "bath", "grooming"}):
        return "lifestyle"
    if fallback_style_mode in MALE_OUTFITS and fallback_style_mode != "random":
        return fallback_style_mode
    return "lifestyle"


def _choose_male_hair(rnd: random.Random, length: str, hairstyle_control: str = "random", custom_hair: str = "") -> str:
    if custom_hair:
        return custom_hair
    hair_entries = _male_styling_bank()["hair_structures"]
    if hairstyle_control != "random":
        chosen = _style_item_by_id(hair_entries, hairstyle_control)
        if chosen:
            return chosen["value"]
    effective = length if length in MALE_HAIR_BY_LENGTH else "short"
    tagged_entries = [item for item in hair_entries if _male_length_tag(effective) in item.get("tags", [])]
    if tagged_entries:
        return _weighted_style_value(rnd, tagged_entries)
    return rnd.choice(MALE_HAIR_BY_LENGTH[effective])


def _choose_male_grooming(rnd: random.Random, style_mode: str, grooming_control: str = "random") -> str:
    if grooming_control != "random":
        return MALE_GROOMING_LABELS.get(grooming_control, "light stubble")
    return rnd.choice(MALE_GROOMING_BY_STYLE.get(style_mode, MALE_GROOMING_BY_STYLE["random"]))


def _choose_male_outfit(rnd: random.Random, style_mode: str, outfit_control: str = "random", scene_family_id: str = "") -> tuple[str, str]:
    outfit_entries = _male_styling_bank()["outfit_families"]
    effective_vibe = _normalize_male_outfit_control(outfit_control)
    if effective_vibe == "random":
        effective_vibe = _male_outfit_vibe_for_scene(scene_family_id, style_mode)
    style_entries = _male_style_items(outfit_entries, effective_vibe)
    if style_entries:
        if effective_vibe in {"romantic", "luxury", "nightlife"}:
            softened_weights = [max(math.sqrt(max(float(item.get("weight", 0.0)), 0.01)), 0.01) for item in style_entries]
            return rnd.choices(style_entries, weights=softened_weights, k=1)[0]["value"], effective_vibe
        return _weighted_style_value(rnd, style_entries), effective_vibe
    return rnd.choice(MALE_OUTFITS.get(effective_vibe, MALE_OUTFITS["random"])), effective_vibe


def _choose_male_pose(rnd: random.Random, style_mode: str) -> str:
    return rnd.choice(MALE_POSES.get(style_mode, MALE_POSES["random"]))


def _choose_men_line_bank_value(
    data: dict[str, Any],
    *,
    domain: str,
    spicy_level: int,
    seed_parts: tuple[Any, ...],
    scene_family_id: str = "",
    style_mode: str = "random",
    scene_tags: set[str] | None = None,
    setting_value: str = "",
    camera_framing_id: str = "",
) -> str:
    records = line_bank_loader.records_for_level(
        data.get("line_banks", {}),
        gender="men",
        domain=domain,
        spicy_level=spicy_level,
    )
    if domain == "outfits":
        records = [
            record
            for record in records
            if line_bank_loader.line_bank_outfit_matches_scene(
                record,
                scene_family_id=scene_family_id,
                style_mode=style_mode,
                scene_tags=scene_tags,
                setting_value=setting_value,
            )
        ]
    if domain == "poses":
        records = [
            record
            for record in records
            if line_bank_loader.line_bank_pose_matches_scene(
                record,
                scene_family_id=scene_family_id,
                scene_tags=scene_tags,
                setting_value=setting_value,
                framing_id=camera_framing_id,
            )
        ]
    if not records:
        return ""
    chooser = random.Random(hash(("men_line_bank", domain, spicy_level, *seed_parts)))
    chosen = chooser.choice(records)
    return str(chosen.get("value", "") or "").strip()


def _apply_men_line_bank_identity_overrides(
    identity: dict[str, str],
    data: dict[str, Any],
    *,
    candidate: dict[str, Any],
    style_mode: str,
    spicy_level: int,
) -> dict[str, str]:
    updated = dict(identity)
    seed_parts = (
        str(candidate.get("setting_scene_id", "") or ""),
        str(candidate.get("scene_family_id", "") or ""),
        str(candidate.get("photo_treatment_id", "") or ""),
        str(candidate.get("camera_framing_id", "") or ""),
        str(candidate.get("color_story_id", "") or ""),
        str(candidate.get("outfit_family_id", "") or ""),
        style_mode,
        updated.get("_ethnicity_id", ""),
        updated.get("age", ""),
    )
    if not updated.get("appearance_prompt"):
        line_bank_outfit = _choose_men_line_bank_value(
            data,
            domain="outfits",
            spicy_level=spicy_level,
            seed_parts=seed_parts + ("outfit",),
            scene_family_id=str(candidate.get("scene_family_id", "") or ""),
            style_mode=style_mode,
            scene_tags=set(candidate.get("setting_tags", []) or []),
            setting_value=str(candidate.get("setting", "") or candidate.get("setting_scene", "") or ""),
        )
        if line_bank_outfit:
            updated["outfit"] = line_bank_outfit
            updated["_line_bank_outfit"] = line_bank_outfit
    line_bank_pose = _choose_men_line_bank_value(
        data,
        domain="poses",
        spicy_level=spicy_level,
        seed_parts=seed_parts + ("pose",),
        scene_family_id=str(candidate.get("scene_family_id", "") or ""),
        style_mode=style_mode,
        scene_tags=set(candidate.get("setting_tags", []) or []),
        setting_value=str(candidate.get("setting", "") or candidate.get("setting_scene", "") or ""),
        camera_framing_id=str(candidate.get("camera_framing_id", "") or ""),
    )
    if line_bank_pose:
        updated["pose"] = line_bank_pose
        updated["_line_bank_pose"] = line_bank_pose
    line_bank_expression = _choose_men_line_bank_value(
        data,
        domain="expressions",
        spicy_level=spicy_level,
        seed_parts=seed_parts + ("expression",),
    )
    if line_bank_expression:
        updated["_line_bank_expression"] = line_bank_expression
    return updated


def _fallback_couple_interaction_records(style_mode: str) -> list[dict[str, Any]]:
    values = COUPLE_INTERACTIONS.get(style_mode, COUPLE_INTERACTIONS["random"])
    return [
        {
            "id": f"legacy_{style_mode}_{index}",
            "value": value,
            "lane": "moderate_safe",
            "weight": 1.0,
            "recommended_min_spicy": 1,
            "high_spicy_only": False,
            "block_low_spicy": False,
        }
        for index, value in enumerate(values, start=1)
    ]


@functools.lru_cache(maxsize=1)
def _couple_interaction_bank() -> list[dict[str, Any]]:
    pose_bank = generator.load_data_bank().get("pose_bank", {})
    interactions = pose_bank.get("couple_interactions", [])
    return [dict(item) for item in interactions if isinstance(item, dict) and item.get("id") and item.get("value")]


def _weighted_record_choice(rnd: random.Random, records: list[dict[str, Any]]) -> dict[str, Any]:
    weights = [max(float(record.get("weight", 0.0)), 0.01) for record in records]
    return dict(rnd.choices(records, weights=weights, k=1)[0])


def _high_spicy_interaction_matches(
    record: dict[str, Any],
    style_mode: str,
    scene_family_id: str,
    spicy_level: int,
) -> bool:
    if spicy_level <= 4:
        return False
    lane = str(record.get("lane", "moderate_safe") or "moderate_safe")
    if lane == "moderate_safe":
        return False
    if lane == "pushing_it" and spicy_level <= 6:
        return False
    if spicy_level < int(record.get("recommended_min_spicy", 1) or 1):
        return False
    style_modes = {str(value) for value in record.get("style_modes", [])}
    if style_modes and style_mode not in style_modes and "random" not in style_modes:
        return False
    allowed_scene_families = {str(value) for value in record.get("allowed_scene_families", [])}
    if allowed_scene_families and scene_family_id not in allowed_scene_families:
        return False
    if record.get("high_spicy_only") and spicy_level < 5:
        return False
    if record.get("block_low_spicy") and spicy_level <= 4:
        return False
    return True


def _choose_couple_interaction(
    rnd: random.Random,
    style_mode: str,
    scene_family_id: str,
    spicy_level: int,
) -> dict[str, Any]:
    records = _couple_interaction_bank()
    high_spicy_records = [
        record
        for record in records
        if _high_spicy_interaction_matches(record, style_mode, scene_family_id, spicy_level)
    ]
    if not high_spicy_records and style_mode == "random" and spicy_level >= 6:
        high_spicy_records = [
            record
            for record in records
            if _high_spicy_interaction_matches(record, "romantic", scene_family_id, spicy_level)
            or _high_spicy_interaction_matches(record, "nightlife", scene_family_id, spicy_level)
            or _high_spicy_interaction_matches(record, "luxury", scene_family_id, spicy_level)
        ]
    if high_spicy_records:
        return _weighted_record_choice(rnd, high_spicy_records)
    return _weighted_record_choice(rnd, _fallback_couple_interaction_records(style_mode))


def _male_mood(style_mode: str, spicy_level: int | None = None) -> str:
    if spicy_level is not None and spicy_level >= 7:
        high_spicy = {
            "random": "heated masculine energy, direct eye contact",
            "luxury": "smoldering luxury confidence, direct eye contact",
            "romantic": "heated romantic confidence, direct eye contact",
            "nightlife": "after-dark magnetic confidence, direct eye contact",
            "coastal": "sunlit seductive confidence, direct eye contact",
        }
        if style_mode in high_spicy:
            return high_spicy[style_mode]
    if spicy_level is not None and spicy_level >= 6:
        mid_high_spicy = {
            "random": "charged confident energy, direct eye contact",
            "luxury": "smoldering composed confidence, direct eye contact",
            "romantic": "warm magnetic confidence, direct eye contact",
            "nightlife": "charged late-night confidence, direct eye contact",
            "coastal": "sun-warmed confident energy, direct eye contact",
        }
        if style_mode in mid_high_spicy:
            return mid_high_spicy[style_mode]
    return MALE_MOODS.get(style_mode, MALE_MOODS["random"])


def _couple_mood(style_mode: str, spicy_level: int | None = None) -> str:
    if spicy_level is not None and spicy_level >= 7:
        high_spicy = {
            "random": "heated close chemistry, eyes locked on each other",
            "lifestyle": "heated everyday chemistry, pulled tight together",
            "luxury": "smoldering intimate chemistry, fully absorbed in each other",
            "romantic": "smoldering romantic chemistry, lost in each other",
            "nightlife": "after-dark magnetic chemistry, locked into each other",
            "coastal": "heated getaway chemistry, bodies drawn tight together",
        }
        if style_mode in high_spicy:
            return high_spicy[style_mode]
    if spicy_level is not None and spicy_level >= 6:
        mid_high_spicy = {
            "random": "charged close chemistry, drawn tight together",
            "lifestyle": "charged everyday chemistry, leaning into each other",
            "luxury": "charged intimate chemistry, attention fixed on each other",
            "romantic": "heated romantic chemistry, pulled into each other",
            "nightlife": "charged late-night chemistry, circling each other",
            "coastal": "charged getaway chemistry, bodies angled together",
        }
        if style_mode in mid_high_spicy:
            return mid_high_spicy[style_mode]
    return COUPLE_MOODS.get(style_mode, COUPLE_MOODS["random"])


def _legacy_debug_meta(
    mode: str,
    candidate: dict[str, Any],
    male_identity: dict[str, str],
    segments: dict[str, str],
    style_mode: str,
    index: int,
) -> dict[str, Any]:
    debug = {
        "index": index,
        "route": candidate.get("route", ""),
        "sceneFamily": candidate.get("scene_family_id", ""),
        "setting": candidate.get("setting_micro", ""),
        "outfit": candidate.get("outfit_family", ""),
        "material": candidate.get("material", ""),
        "color": candidate.get("color_story", ""),
        "pose": candidate.get("pose_family", ""),
        "framing": candidate.get("camera_framing", ""),
        "lighting": candidate.get("lighting_family", ""),
        "time": candidate.get("time_of_day", ""),
        "capture": candidate.get("capture_style", ""),
        "captureRender": candidate.get("capture_style_render") or candidate.get("capture_style", ""),
        "photoTreatment": candidate.get("photo_treatment", ""),
        "photoTreatmentCategory": candidate.get("photo_treatment_category", ""),
        "cameraVibe": candidate.get("camera_vibe", ""),
        "colorGrade": candidate.get("color_grade", ""),
        "finish": candidate.get("finish_render", ""),
        "mode": mode,
        "styleMode": style_mode,
        "maleOutfitVibe": male_identity.get("_outfit_vibe", ""),
        "maleOutfit": male_identity.get("outfit", ""),
        "malePose": male_identity.get("pose", ""),
        "maleExpression": male_identity.get("_line_bank_expression", ""),
        "maleHair": male_identity.get("hair", ""),
        "maleGrooming": male_identity.get("grooming", ""),
        "maleAge": male_identity.get("age", ""),
        "maleEthnicity": male_identity.get("ethnicity", ""),
        "maleEthnicityId": male_identity.get("_ethnicity_id", ""),
        "maleEthnicityGroup": male_identity.get("ethnicity_group", ""),
        "maleAppearanceMode": "custom" if male_identity.get("appearance_prompt") else "generated",
        "mood": segments.get("mood", ""),
    }
    if mode == "men":
        debug["outfit"] = male_identity.get("outfit", "")
        debug["pose"] = male_identity.get("pose", "")
        debug["hair"] = male_identity.get("hair", "")
        debug["hairColor"] = ""
        debug["makeup"] = ""
    if mode == "couples":
        debug["femaleOutfit"] = candidate.get("outfit_family", "")
        debug["femaleColorStory"] = candidate.get("color_story", "")
        debug["femaleHair"] = candidate.get("hair_structure_override") or candidate.get("hair_structure", "")
        debug["femaleEyeColor"] = candidate.get("eye_color", "")
        debug["femaleMakeup"] = candidate.get("makeup_style", "")
        debug["maleColorStory"] = male_identity.get("_color", "")
        debug["pose"] = segments.get("pose", "")
        debug["coupleInteraction"] = segments.get("pose", "")
        debug["coupleInteractionId"] = segments.get("_couple_interaction_id", "")
        debug["coupleInteractionLane"] = segments.get("_couple_interaction_lane", "")
        debug["coupleLineBankPose"] = segments.get("_couple_line_bank_pose", "")
    return debug


def _soft_female_appearance_prompt(text: str) -> bool:
    tokens = set(re.findall(r"[a-z0-9]+", (text or "").lower()))
    return bool(tokens & {"soft", "clean", "polished", "blouse", "midi", "tailored", "trousers", "cardigan", "knit", "ivory", "minimal"})


def _female_identity_bits(candidate: dict[str, Any]) -> dict[str, str]:
    ethnicity = candidate.get("ethnicity_override") or candidate["ethnicity"]
    hair_color = candidate.get("hair_color_override") or candidate["hair_color"]
    hair_structure = candidate.get("hair_structure_override") or candidate["hair_structure"]
    return {
        "age": candidate["age_band"],
        "ethnicity": ethnicity,
        "body": candidate["body_type"],
        "breasts": candidate["breast_size"],
        "hair_color": hair_color,
        "eye_color": candidate.get("eye_color", ""),
        "hair_structure": hair_structure,
        "makeup": candidate["makeup_style"],
        "beauty": _beauty_phrase(candidate["beauty_level"]),
    }


def _couple_female_outfit_text(candidate: dict[str, Any], style_mode: str) -> str:
    outfit_id = candidate.get("outfit_family_id", "")
    scene_family = candidate.get("scene_family_id", "")
    color_story_id = candidate.get("color_story_id", "")
    color_story = candidate.get("color_story", "")
    material = candidate.get("material", "")
    outfit_family = candidate.get("outfit_family", "")

    def render_variant(variant_id: str, variant_outfit: str, variant_material: str, variant_seed: str) -> str:
        return generator.render_outfit_phrase_from_parts(
            outfit_family_id=variant_id,
            outfit_family=variant_outfit,
            color_story_id=color_story_id,
            color_story=color_story,
            material=variant_material,
            scene_family_id=scene_family,
            seed_parts=(candidate.get("setting_scene_id", ""), style_mode, variant_seed),
        )

    is_swimwear = outfit_id in {"swimsuit", "bikini_set"}
    is_coastal_scene = scene_family in {"coastal_pool", "coastal_boardwalk"}
    if style_mode == "random" and outfit_id in {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt"}:
        fallback_variants = [
            ("blouse_trousers", "silk blouse tucked into tailored wide trousers", "tailored woven fabric"),
            ("cardigan_skirt", "buttoned cardigan over a fitted top with a pleated midi skirt", "ribbed knit texture"),
            ("shirt_trousers", "lightweight resort shirt with relaxed linen trousers", "crisp cotton fabric"),
        ]
        chooser = random.Random(hash((candidate.get("setting_scene_id", ""), candidate.get("color_story_id", ""), outfit_id, style_mode, "random_soften")))
        chosen = chooser.choice(fallback_variants)
        return render_variant(chosen[0], chosen[1], chosen[2], "random_soften")
    if style_mode in {"lifestyle", "urban_day", "cultural_bookish"} and outfit_id in {
        "swimsuit",
        "bikini_set",
        "crop_top_mini_skirt",
        "latex_editorial",
        "corset_trousers",
    }:
        fallback_variants = [
            ("blouse_trousers", "silk blouse tucked into tailored wide trousers", "tailored woven fabric"),
            ("cardigan_skirt", "buttoned cardigan over a fitted top with a pleated midi skirt", "ribbed knit texture"),
            ("cami_midi_skirt", "silk cami with a bias cut midi skirt", "satin finish"),
        ]
        chooser = random.Random(hash((candidate.get("setting_scene_id", ""), candidate.get("color_story_id", ""), outfit_id, style_mode, "lifestyle_soften")))
        chosen = chooser.choice(fallback_variants)
        return render_variant(chosen[0], chosen[1], chosen[2], "lifestyle_soften")
    if style_mode == "romantic" and outfit_id in {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt"}:
        fallback_variants = [
            ("cami_midi_skirt", "silk cami with a bias cut midi skirt", "satin finish"),
            ("cardigan_skirt", "buttoned cardigan over a fitted top with a pleated midi skirt", "ribbed knit texture"),
            ("blouse_trousers", "silk blouse tucked into tailored wide trousers", "tailored woven fabric"),
        ]
        chooser = random.Random(hash((candidate.get("setting_scene_id", ""), candidate.get("color_story_id", ""), outfit_id, style_mode, "romantic_soften")))
        chosen = chooser.choice(fallback_variants)
        return render_variant(chosen[0], chosen[1], chosen[2], "romantic_soften")
    if style_mode == "luxury" and outfit_id in {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt"}:
        fallback_variants = [
            ("blazer_mini_dress", "tailored blazer mini dress with a clean open neckline", "tailored woven fabric"),
            ("cami_midi_skirt", "silk cami with a bias cut midi skirt", "satin finish"),
            ("bodysuit_trousers", "sleek square neck bodysuit with high waisted tailored trousers", "tailored woven fabric"),
        ]
        chooser = random.Random(hash((candidate.get("setting_scene_id", ""), candidate.get("color_story_id", ""), outfit_id, style_mode, "luxury_soften")))
        chosen = chooser.choice(fallback_variants)
        return render_variant(chosen[0], chosen[1], chosen[2], "luxury_soften")
    if style_mode == "nightlife" and outfit_id in {
        "swimsuit",
        "bikini_set",
        "crop_top_mini_skirt",
        "latex_editorial",
        "polo_pleated_skirt",
        "workout_top_leggings",
        "zip_jacket_leggings",
        "training_jacket_trousers",
        "shirt_trousers",
        "cardigan_skirt",
        "cardigan_trousers",
        "sweater_jeans",
    }:
        fallback_variants = [
            ("blazer_mini_dress", "tailored blazer mini dress", "satin finish"),
            ("cami_midi_skirt", "silk cami with a bias cut midi skirt", "satin finish"),
            ("bodysuit_trousers", "sleek square neck bodysuit with high waisted tailored trousers", "tailored woven fabric"),
        ]
        chooser = random.Random(hash((candidate.get("setting_scene_id", ""), candidate.get("color_story_id", ""), outfit_id, style_mode)))
        chosen = chooser.choice(fallback_variants)
        return render_variant(chosen[0], chosen[1], chosen[2], "nightlife_soften")
    if outfit_id == "latex_editorial" and style_mode not in {"nightlife", "studio", "fantasy", "cosplay"}:
        return render_variant("blouse_trousers", "silk blouse tucked into tailored wide trousers", "tailored woven fabric", "latex_soften")
    if is_swimwear and not is_coastal_scene and style_mode not in {"coastal", "vacation"}:
        return render_variant("bodysuit_trousers", "sleek square neck bodysuit with high waisted tailored trousers", "tailored woven fabric", "swim_soften")
    return generator.render_outfit_phrase(candidate)


def _choose_couple_male_color(style_mode: str, female_color_story_id: str, candidate: dict[str, Any]) -> str:
    palette = list(COUPLE_MALE_COLOR_CHOICES.get(style_mode, COUPLE_MALE_COLOR_CHOICES["random"]))
    avoided = FEMALE_COLOR_TO_AVOID_MALE.get(female_color_story_id, set())
    filtered = [color for color in palette if color not in avoided] or palette
    chooser = random.Random(hash((candidate.get("setting_scene_id", ""), candidate.get("age_band", ""), style_mode, female_color_story_id)))
    return chooser.choice(filtered)


def _build_male_identity(
    rnd: random.Random,
    data: dict[str, Any],
    form_state: dict[str, Any],
    *,
    style_mode: str,
    mode: str,
    scene_family_id: str = "",
    female_age_number: int | None = None,
    female_ethnicity: str | None = None,
    female_group: str | None = None,
    seed_material: tuple[str, ...] | None = None,
) -> dict[str, str]:
    male_age_value = form_state.get("maleAge", form_state.get("age", "random"))
    male_race_preset = form_state.get("maleRacePreset", form_state.get("racePreset", "random_default_split")) if mode == "couples" else form_state.get("racePreset", "random_default_split")
    custom_race = form_state.get("maleCustomRace", "") if mode == "couples" else form_state.get("customRace", "")
    ethnicity_id = ""
    if male_race_preset == "other" and custom_race:
        ethnicity = _custom_identity_text(custom_race, "man")
        ethnicity_group = "custom"
    else:
        preferred_group = _normalize_group(male_race_preset)
        if preferred_group is None and female_group == WHITE_GROUP:
            preferred_group = WHITE_GROUP
        entry = _pick_ethnicity_entry(
            rnd,
            data,
            male_race_preset,
            preferred_group=preferred_group or female_group,
            exclude_value=female_ethnicity if female_group == WHITE_GROUP else None,
        )
        ethnicity_id = str(entry.get("id", "") or "")
        ethnicity = f'{_masculinize_ethnicity(entry["value"])} man'
        ethnicity_group = entry.get("group", "")
    if str(male_age_value or "").strip().lower() not in {"", "random"}:
        age = _pick_age_text(rnd, male_age_value)
    elif female_age_number is not None:
        male_age_number = max(21, female_age_number + rnd.randint(2, 5))
        age = f"{male_age_number} years old"
    else:
        age = _pick_age_text(rnd, form_state.get("age", "random"))
    hair_length = form_state.get("maleHairLength", "short")
    hairstyle_control = str(form_state.get("maleHairstyle", "random") or "random").strip().lower()
    custom_hair = ""
    if hairstyle_control == "custom":
        custom_hair = " ".join(str(form_state.get("maleCustomHair", "") or "").strip().split())[:180]
    grooming_control = str(form_state.get("maleGroomingControl", "random") or "random").strip().lower()
    outfit_control = str(form_state.get("maleOutfitControl", "random") or "random").strip().lower()
    appearance_prompt = ""
    if str(form_state.get("maleAppearanceMode", "generated")).strip().lower() == "custom":
        appearance_prompt = " ".join(str(form_state.get("maleAppearancePrompt", "") or "").strip().split())[:260]
    selection_seed = (
        style_mode,
        scene_family_id,
        male_age_value,
        male_race_preset,
        tuple(seed_material or ()),
    )
    outfit_rng = random.Random(hash((selection_seed, "male_outfit")))
    pose_rng = random.Random(hash((selection_seed, "male_pose")))
    outfit, outfit_vibe = _choose_male_outfit(outfit_rng, style_mode, outfit_control=outfit_control, scene_family_id=scene_family_id)
    identity = {
        "name": form_state.get("maleName", "").strip() if mode == "couples" else "",
        "age": age,
        "ethnicity": ethnicity,
        "_ethnicity_id": ethnicity_id,
        "ethnicity_group": ethnicity_group,
        "body": _choose_male_body(rnd, form_state.get("bodyMixPreset", "random_balanced")),
        "hair": _choose_male_hair(rnd, hair_length, hairstyle_control=hairstyle_control, custom_hair=custom_hair),
        "grooming": _choose_male_grooming(rnd, style_mode, grooming_control=grooming_control),
        "outfit": outfit,
        "pose": _choose_male_pose(pose_rng, style_mode),
        "beauty": rnd.choice(["handsome", "good-looking", "ruggedly handsome"]),
        "appearance_prompt": appearance_prompt,
        "_outfit_locked": outfit_control != "random",
        "_outfit_vibe": outfit_vibe,
    }
    return identity


def preview_male_identities(
    mode: str,
    candidates: list[dict[str, Any]],
    form_state: dict[str, Any],
    effective_style_mode: str,
    seed: int,
) -> list[dict[str, str]]:
    rnd = random.Random(seed)
    data = generator.load_data_bank()
    spicy_level = _coerce_spicy_level(form_state.get("spicyLevel", 3))
    locked_male_identity: dict[str, str] | None = None
    identities: list[dict[str, str]] = []
    for candidate in candidates:
        female_age_number = _extract_age_number(candidate.get("age_band", ""))
        female_ethnicity = candidate.get("ethnicity_override") or candidate.get("ethnicity")
        female_group = candidate.get("ethnicity_group")
        male_identity = locked_male_identity or _build_male_identity(
            rnd,
            data,
            form_state,
            style_mode=effective_style_mode,
            mode=mode,
            scene_family_id=candidate.get("scene_family_id", ""),
            female_age_number=female_age_number if mode == "couples" else None,
            female_ethnicity=female_ethnicity if mode == "couples" else None,
            female_group=female_group if mode == "couples" else None,
            seed_material=(
                str(candidate.get("setting_scene_id", "") or ""),
                str(candidate.get("photo_treatment_id", "") or ""),
                str(candidate.get("camera_framing_id", "") or ""),
                str(candidate.get("color_story_id", "") or ""),
                str(candidate.get("outfit_family_id", "") or ""),
            ),
        )
        if mode == "men":
            male_identity = _apply_men_line_bank_identity_overrides(
                male_identity,
                data,
                candidate=candidate,
                style_mode=effective_style_mode,
                spicy_level=spicy_level,
            )
        if form_state.get("personMode") == "same_person":
            locked_male_identity = dict(male_identity)
        identities.append(dict(male_identity))
    return identities


def _stylize_male_identity_for_treatment(
    candidate: dict[str, Any],
    male_identity: dict[str, str],
    style_mode: str,
    spicy_level: int | None = None,
) -> dict[str, str]:
    if male_identity.get("appearance_prompt"):
        return dict(male_identity)
    treatment_id = str(candidate.get("photo_treatment_id", "") or "")
    if style_mode not in {"luxury", "romantic"}:
        return dict(male_identity)
    # Use a deterministic index for pose/outfit variety within a batch without collapsing to one dominant template.
    _pose_seed = (
        str(candidate.get("setting_scene_id", "") or ""),
        str(candidate.get("scene_family_id", "") or ""),
        str(candidate.get("photo_treatment_id", "") or ""),
        str(candidate.get("camera_framing_id", "") or ""),
        str(candidate.get("color_story_id", "") or ""),
        str(candidate.get("outfit_family_id", "") or ""),
    )
    _pose_idx = abs(hash(_pose_seed))
    low_spicy = spicy_level is not None and spicy_level <= 3
    stylized_map = {
        "concept_photo_editorial": {
            "outfit": "open collar silk shirt with sharply tailored trousers",
            "pose": "standing tall with one shoulder carved by the light and a composed editorial stare",
            "mood": "controlled editorial luxury energy, direct eye contact",
        },
        "direct_light_editorial": {
            "outfit": "fine knit polo with sharply tailored trousers",
            "pose": "standing in hard light with a slight quarter turn and a composed fashion-campaign stare",
            "mood": "hard-light luxury confidence, direct eye contact",
        },
        "cinematic_poster_realism": {
            "outfit": "dark open collar shirt with tailored trousers",
            "pose": "leaning lightly against the set with sculpted posture and a cinematic steady gaze",
            "mood": "cinematic luxury confidence, direct eye contact",
        },
        "direct_flash_night": {
            "outfit": "dark silk shirt with tailored trousers",
            "pose": "standing close to camera with relaxed shoulders and a controlled late-night stare",
            "mood": "late-night luxury confidence, direct eye contact",
        },
        "analog_35mm": {
            "outfit": "soft open shirt with pleated trousers",
            "outfits_romantic": [
                "soft open shirt with pleated trousers",
                "fine knit crewneck sweater with dark tailored trousers",
                "soft linen shirt with relaxed pleated trousers",
                "textured knit polo with tailored dark trousers",
            ],
            "poses": [
                "standing relaxed with one shoulder forward and an understated film-portrait gaze",
                "seated slightly forward with elbows resting lightly and a quiet 35mm romantic look",
                "leaning lightly against a wall with relaxed posture and a warm understated film gaze",
                "standing by the window with relaxed shoulders and a warm reflective film gaze",
            ],
            "mood": "quiet filmic romantic confidence, direct eye contact",
        },
        "documentary_still": {
            "outfit": "soft open shirt with tailored trousers",
            "outfits_romantic": [
                "soft open shirt with tailored trousers",
                "lightweight blazer over a fine knit top with tailored trousers",
                "fine knit crewneck sweater with dark tailored trousers",
                "soft collar shirt with pleated dark trousers",
            ],
            "poses": [
                "leaning lightly on a doorway with relaxed posture and a quietly cinematic romantic look",
                "standing still with one hand resting at his side and a quietly present documentary gaze",
                "seated with quiet attentive posture and an understated documentary romantic look",
                "standing in a slight quarter turn with relaxed shoulders and a soft documentary gaze",
            ],
            "mood": "documentary romantic calm, direct eye contact",
        },
        "disposable_camera": {
            "outfit": "clean henley with dark trousers",
            "pose": "standing relaxed with one shoulder forward and an easy imperfect film-snapshot look",
            "mood": "film-snapshot romantic ease, direct eye contact",
        },
        "candid_phone_snapshot": {
            "outfit": "soft open shirt with dark trousers",
            "poses": [
                "standing close to the camera with relaxed shoulders and a warm candid half-smile",
                "leaning slightly toward the camera with easy posture and a natural candid romantic look",
                "seated with one arm resting forward and a warm candid smile",
                "standing angled with one hand near his pocket and an easy candid smile",
            ],
            "mood": "candid romantic warmth, direct eye contact",
        },
    }
    override = stylized_map.get(treatment_id)
    if not override:
        return dict(male_identity)
    identity = dict(male_identity)
    if not identity.get("_line_bank_outfit") and not identity.get("_outfit_locked"):
        if style_mode == "romantic" and "outfits_romantic" in override:
            identity["outfit"] = override["outfits_romantic"][_pose_idx % len(override["outfits_romantic"])]
        else:
            identity["outfit"] = override["outfit"]
    if not identity.get("_line_bank_pose"):
        if "poses" in override:
            identity["pose"] = override["poses"][_pose_idx % len(override["poses"])]
        else:
            identity["pose"] = override["pose"]
    low_spicy_mood_overrides = {
        "concept_photo_editorial": "quiet editorial confidence, direct eye contact",
        "direct_light_editorial": "calm editorial confidence, direct eye contact",
        "cinematic_poster_realism": "quiet cinematic confidence, direct eye contact",
        "direct_flash_night": "calm late-night confidence, direct eye contact",
        "analog_35mm": "quiet filmic confidence, direct eye contact",
        "documentary_still": "quiet documentary calm, direct eye contact",
        "disposable_camera": "easy film-snapshot energy, direct eye contact",
        "candid_phone_snapshot": "soft candid warmth, direct eye contact",
    }
    identity["_mood_override"] = low_spicy_mood_overrides.get(treatment_id, override["mood"]) if low_spicy else override["mood"]
    return identity


def _setting_mood_technical(
    candidate: dict[str, Any],
    mode: str,
    style_mode: str,
    exact_theme: str,
    spicy_level: int | None = None,
) -> tuple[str, str, str]:
    segments = generator.render_candidate_segments(candidate)
    if mode == "men":
        segments["mood"] = _male_mood(style_mode, spicy_level)
    elif mode == "couples":
        segments["mood"] = _couple_mood(style_mode, spicy_level)
    if not exact_theme and style_mode in {"sport", "fitness"}:
        if mode == "couples":
            segments["setting"] = "Set in a bright boutique gym corner with clean training equipment, pale rubber flooring and crisp daylight"
            segments["mood"] = "playful athletic chemistry, moving with each other"
        else:
            segments["setting"] = "Set in a bright boutique gym corner with clean training equipment, pale rubber flooring and crisp daylight"
            segments["mood"] = "athletic confident energy, direct eye contact"
        segments["technical"] = generator._render_technical_block(
            candidate,
            lighting_override="clean natural daylight",
            time_override="bright afternoon",
        )
    if not exact_theme and style_mode == "nightlife":
        if mode == "couples":
            segments["setting"] = "Set in a moody cocktail bar with amber lamps, mirrored shelving, deep banquettes and restrained neon reflections"
            if spicy_level is not None and spicy_level >= 7:
                segments["mood"] = "after-dark magnetic chemistry, locked into each other"
            elif spicy_level is not None and spicy_level >= 6:
                segments["mood"] = "charged late-night chemistry, circling each other"
            else:
                segments["mood"] = "charged nightlife chemistry, pulled into each other"
        else:
            segments["setting"] = "Set in a moody cocktail bar with amber lamps, mirrored shelving, deep banquettes and restrained neon reflections"
            if spicy_level is not None and spicy_level >= 7:
                segments["mood"] = "after-dark magnetic confidence, direct eye contact"
            elif spicy_level is not None and spicy_level >= 6:
                segments["mood"] = "charged late-night confidence, direct eye contact"
            else:
                segments["mood"] = "controlled late-night confidence, direct eye contact"
        segments["technical"] = generator._render_technical_block(
            candidate,
            lighting_override="clean neon ambience without colored spots on skin",
            time_override="night",
        )
    if mode == "men" and spicy_level is not None and spicy_level <= 3 and style_mode in {"luxury", "nightlife", "romantic"}:
        low_spicy_moods = {
            "luxury": "quiet composed energy, direct eye contact",
            "nightlife": "calm late-night confidence, direct eye contact",
            "romantic": "soft composed energy, direct eye contact",
        }
        segments["mood"] = low_spicy_moods.get(style_mode, segments["mood"])
    return segments["setting"], segments["mood"], segments["technical"]


def _render_men_mood(mood: str, expression: str) -> str:
    normalized_expression = str(expression or "").strip()
    if not normalized_expression:
        return mood
    direct_eye_contact_suffix = ", direct eye contact"
    if mood.endswith(direct_eye_contact_suffix):
        return f'{mood[: -len(direct_eye_contact_suffix)]}, expression: {normalized_expression}{direct_eye_contact_suffix}'
    return f'{mood}, expression: {normalized_expression}'


def _build_men_prompt(candidate: dict[str, Any], male_identity: dict[str, str], style_mode: str, spicy_level: int) -> tuple[str, dict[str, str]]:
    male_identity = _stylize_male_identity_for_treatment(candidate, male_identity, style_mode, spicy_level)
    setting, mood, technical = _setting_mood_technical(candidate, "men", style_mode, candidate.get("exact_theme", ""), spicy_level)
    mood = male_identity.get("_mood_override", mood)
    mood = _render_men_mood(mood, male_identity.get("_line_bank_expression", ""))
    age_phrase = _age_phrase(male_identity["age"])
    name_prefix = f'{male_identity["name"]}, ' if male_identity.get("name") else ""
    if male_identity.get("appearance_prompt"):
        subject = (
            f'{generator._effective_capture_text(candidate).capitalize()} of {name_prefix}a {age_phrase} '
            f'{male_identity["ethnicity"]} with a {male_identity["beauty"]} read and {male_identity["body"]}'
        )
        outfit = f'Appearance: {male_identity["appearance_prompt"]}'
    elif male_identity.get("_line_bank_outfit"):
        subject = (
            f'{generator._effective_capture_text(candidate).capitalize()} of {name_prefix}a {age_phrase} '
            f'{male_identity["ethnicity"]} with a {male_identity["beauty"]} read, {male_identity["body"]}, '
            f'{male_identity["hair"]} and {male_identity["grooming"]}'
        )
        line_bank_outfit = str(male_identity.get("_line_bank_outfit", "")).strip()
        if line_bank_outfit.lower().startswith(("a ", "an ", "the ")):
            outfit = f'Wearing {line_bank_outfit}'
        else:
            outfit = f'Wearing {_article_for(line_bank_outfit)} {line_bank_outfit}'
    else:
        subject = (
            f'{generator._effective_capture_text(candidate).capitalize()} of {name_prefix}a {age_phrase} '
            f'{male_identity["ethnicity"]} with a {male_identity["beauty"]} read, {male_identity["body"]}, '
            f'{male_identity["hair"]} and {male_identity["grooming"]}'
        )
        outfit_phrase = generator.render_male_outfit_phrase(
            male_identity.get("_color", ""),
            male_identity["outfit"],
            scene_family_id=str(candidate.get("scene_family_id", "") or ""),
            seed_parts=(candidate.get("setting_scene_id", ""), style_mode, candidate.get("photo_treatment_id", "")),
        )
        outfit = f'Wearing {outfit_phrase}'
    pose = f'Pose: {male_identity["pose"]}'
    segments = {
        "subject": subject,
        "outfit": outfit,
        "pose": pose,
        "setting": setting,
        "mood": mood,
        "technical": technical,
    }
    prompt = ". ".join(segments[key] for key in ("subject", "outfit", "pose", "setting", "mood", "technical")) + "."
    return prompt, segments


def _build_couples_prompt(
    candidate: dict[str, Any],
    male_identity: dict[str, str],
    style_mode: str,
    spicy_level: int,
) -> tuple[str, dict[str, str]]:
    male_identity = _stylize_male_identity_for_treatment(candidate, male_identity, style_mode)
    setting, mood, technical = _setting_mood_technical(candidate, "couples", style_mode, candidate.get("exact_theme", ""), spicy_level)
    if style_mode == "luxury" and candidate.get("photo_treatment_id") in {"concept_photo_editorial", "direct_light_editorial", "cinematic_poster_realism", "direct_flash_night"}:
        mood = male_identity.get("_mood_override", mood)
    female = _female_identity_bits(candidate)
    interaction_seed = (
        candidate.get("setting_scene_id", ""),
        candidate.get("camera_framing_id", ""),
        candidate.get("photo_treatment_id", ""),
        candidate.get("age_band", ""),
        style_mode,
    )
    interaction_record = _choose_couple_interaction(
        random.Random(hash(interaction_seed)),
        style_mode,
        str(candidate.get("scene_family_id", "") or ""),
        spicy_level,
    )
    interaction = interaction_record["value"]
    interaction_lane = str(interaction_record.get("lane", "moderate_safe") or "moderate_safe")
    line_bank_couple_pose = str(candidate.get("line_bank_pose", "") or "").strip()
    female_age_phrase = _age_phrase(female["age"])
    male_age_phrase = _age_phrase(male_identity["age"])
    female_appearance_prompt = str(candidate.get("appearance_prompt", "")).strip()
    soft_female_appearance = _soft_female_appearance_prompt(female_appearance_prompt)
    female_name = candidate.get("subject_name", "").strip()
    female_prefix = f"{female_name}, " if female_name else ""
    male_prefix = f'{male_identity["name"]}, ' if male_identity.get("name") else ""
    female_outfit = _couple_female_outfit_text(candidate, style_mode)
    if female_appearance_prompt:
        female_subject = (
            f'{female_prefix}a {female_age_phrase} {female["ethnicity"]} woman '
            f'with a {female["beauty"]}, {female["body"]}, {female["breasts"]}'
        )
        female_outfit = female_appearance_prompt
    else:
        female_subject = (
            f'{female_prefix}a {female_age_phrase} {female["ethnicity"]} woman '
            f'with a {female["beauty"]}, {female["body"]}, {female["breasts"]}, {female["hair_color"]} in {female["hair_structure"]}, '
            f'{female["eye_color"]}, and {female["makeup"]}'
        )
    if soft_female_appearance and style_mode != "nightlife":
        if mood in {"slow seductive energy, direct eye contact", "bratty playful energy, direct eye contact"}:
            mood = "soft close chemistry, direct eye contact"
        interaction_record = random.Random(hash((candidate["setting_scene_id"], candidate["camera_framing_id"], candidate["age_band"]))).choice([
            {
                "id": "soft_appearance_light_touch",
                "lane": "moderate_safe",
                "value": "standing close with light touch and relaxed shoulders turned gently toward camera",
            },
            {
                "id": "soft_appearance_easy_hold",
                "lane": "moderate_safe",
                "value": "holding each other lightly with calm body language and an easy shared look",
            },
        ])
        interaction = interaction_record["value"]
        interaction_lane = str(interaction_record.get("lane", "moderate_safe") or "moderate_safe")
    elif spicy_level >= 7:
        if interaction_lane == "pushing_it":
            if style_mode == "nightlife":
                mood = "dangerously close nightlife chemistry, locked into each other"
            elif style_mode == "romantic":
                mood = "hungry romantic chemistry, lost in each other"
            else:
                mood = "hungry close chemistry, fully absorbed in each other"
        elif interaction_lane == "revealing":
            if style_mode == "nightlife":
                mood = "after-dark magnetic chemistry, locked into each other"
            elif style_mode == "romantic":
                mood = "smoldering romantic chemistry, lost in each other"
            else:
                mood = "heated close chemistry, eyes locked on each other"
    elif spicy_level >= 6 and interaction_lane == "revealing":
        if style_mode == "nightlife":
            mood = "charged late-night chemistry, circling each other"
        elif style_mode == "romantic":
            mood = "heated romantic chemistry, pulled into each other"
        else:
            mood = "charged close chemistry, drawn tight together"
    if male_identity.get("appearance_prompt"):
        male_subject = (
            f'{male_prefix}a {male_age_phrase} {male_identity["ethnicity"]} '
            f'with a {male_identity["beauty"]} read and {male_identity["body"]}'
        )
        male_outfit = f'male appearance: {male_identity["appearance_prompt"]}'
    else:
        male_color = _choose_couple_male_color(style_mode, candidate.get("color_story_id", ""), candidate)
        male_identity["_color"] = male_color
        male_subject = (
            f'{male_prefix}a {male_age_phrase} {male_identity["ethnicity"]} '
            f'with a {male_identity["beauty"]} read, {male_identity["body"]}, {male_identity["hair"]} and {male_identity["grooming"]}'
        )
        male_outfit_phrase = generator.render_male_outfit_phrase(
            male_color,
            male_identity["outfit"],
            scene_family_id=str(candidate.get("scene_family_id", "") or ""),
            seed_parts=(candidate.get("setting_scene_id", ""), style_mode, candidate.get("photo_treatment_id", "")),
        )
        male_outfit = f'he wears {male_outfit_phrase}'
    subject = f'{generator._effective_capture_text(candidate).capitalize()} of {female_subject}, together with {male_subject}'
    female_outfit_prefix = "Female appearance:" if female_appearance_prompt else "She wears"
    outfit = f'{female_outfit_prefix} {female_outfit}, while {male_outfit}'
    pose_value = interaction
    if line_bank_couple_pose:
        pose_value = f"{line_bank_couple_pose}, {interaction}"
    pose = f'Pose: {pose_value}'
    segments = {
        "subject": subject,
        "outfit": outfit,
        "pose": pose,
        "setting": setting,
        "mood": mood,
        "technical": technical,
        "_couple_interaction_id": interaction_record.get("id", ""),
        "_couple_interaction_lane": interaction_record.get("lane", "moderate_safe"),
        "_couple_line_bank_pose": line_bank_couple_pose,
    }
    prompt = ". ".join(segments[key] for key in ("subject", "outfit", "pose", "setting", "mood", "technical")) + "."
    return prompt, segments


def render_batch(
    mode: str,
    candidates: list[dict[str, Any]],
    form_state: dict[str, Any],
    effective_style_mode: str,
    seed: int,
    spicy_level: int,
) -> list[dict[str, Any]]:
    rnd = random.Random(seed)
    data = generator.load_data_bank()
    prompts: list[dict[str, Any]] = []
    locked_male_identity: dict[str, str] | None = None
    for index, candidate in enumerate(candidates, start=1):
        female_age_number = _extract_age_number(candidate.get("age_band", ""))
        female_ethnicity = candidate.get("ethnicity_override") or candidate.get("ethnicity")
        female_group = candidate.get("ethnicity_group")
        male_identity = locked_male_identity or _build_male_identity(
            rnd,
            data,
            form_state,
            style_mode=effective_style_mode,
            mode=mode,
            scene_family_id=candidate.get("scene_family_id", ""),
            female_age_number=female_age_number if mode == "couples" else None,
            female_ethnicity=female_ethnicity if mode == "couples" else None,
            female_group=female_group if mode == "couples" else None,
            seed_material=(
                str(candidate.get("setting_scene_id", "") or ""),
                str(candidate.get("photo_treatment_id", "") or ""),
                str(candidate.get("camera_framing_id", "") or ""),
                str(candidate.get("color_story_id", "") or ""),
                str(candidate.get("outfit_family_id", "") or ""),
            ),
        )
        if mode == "men":
            male_identity = _apply_men_line_bank_identity_overrides(
                male_identity,
                data,
                candidate=candidate,
                style_mode=effective_style_mode,
                spicy_level=spicy_level,
            )
        if form_state.get("personMode") == "same_person":
            locked_male_identity = dict(male_identity)
        if mode == "men":
            prompt, segments = _build_men_prompt(candidate, male_identity, effective_style_mode, spicy_level)
        else:
            prompt, segments = _build_couples_prompt(candidate, male_identity, effective_style_mode, spicy_level)
        prompts.append(
            {
                "prompt": prompt,
                "segments": segments,
                "debugMeta": _legacy_debug_meta(mode, candidate, male_identity, segments, effective_style_mode, index),
            }
        )
    return prompts
