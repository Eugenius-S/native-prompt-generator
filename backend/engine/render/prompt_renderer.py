from __future__ import annotations

import functools
import random
import re
from typing import Any

from ...character_constraints import resolve_character_constraint_segment
from ...shot_lane_contracts import apply_shot_lane_contract
from ..line_bank_loader import infer_pose_line_tags
from ..data_loader import _load_static_data_bank, _lookup_by_id


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
    "butter_denim": {"primary": "butter yellow", "secondary": "soft denim blue"},
    "teal_cream": {"primary": "teal", "secondary": "cream"},
    "olive_sand": {"primary": "olive", "secondary": "sand"},
    "cobalt_white": {"primary": "cobalt", "secondary": "white"},
    "coral_ivory": {"primary": "coral", "secondary": "ivory"},
    "plum_blush": {"primary": "plum", "secondary": "blush"},
    "sage_stone": {"primary": "sage", "secondary": "stone"},
    "aqua_white": {"primary": "aqua", "secondary": "white"},
    "terracotta_sand": {"primary": "terracotta", "secondary": "sand"},
    "mint_cream": {"primary": "mint", "secondary": "cream"},
    "lilac_smoke": {"primary": "lilac", "secondary": "smoke"},
    "tangerine_cream": {"primary": "tangerine", "secondary": "cream"},
    "red_ivory": {"primary": "true red", "secondary": "ivory"},
    "black_ivory": {"primary": "black", "secondary": "ivory"},
}

PORTRAIT_FRAMING_IDS = {"waist_up", "bust_up", "close_portrait", "head_and_shoulders", "face_only", "below_chest_portrait"}
TIGHT_PORTRAIT_FRAMING_IDS = {"close_portrait", "head_and_shoulders", "face_only"}
LOWER_BODY_ACTION_TOKENS = ("thigh", "hip", "hips", "leg", "legs", "knee", "knees", "ankle", "ankles", "waist", "waistband", "waistline")
TIGHT_PORTRAIT_BLOCKED_ACTION_TOKENS = LOWER_BODY_ACTION_TOKENS + ("midriff",)
LOWER_BODY_OUTFIT_TOKENS = ("skirt", "trousers", "pants", "jeans", "shorts", "leggings", "bottoms")
CLOSE_UP_ANGLE_BUCKETS: dict[str, tuple[str, ...]] = {
    "front": (
        "tight beauty headshot with her head level and eyes locked directly into camera",
        "tight beauty headshot facing forward with a soft direct gaze",
        "tight beauty headshot straight-on with parted lips and eyes into camera",
    ),
    "three_quarter": (
        "tight beauty headshot with a subtle three-quarter turn and direct eye contact",
        "tight beauty headshot with a strong three-quarter turn and the jaw still visible",
        "tight beauty headshot turned slightly off-axis with eyes still into camera",
    ),
    "profile": (
        "tight beauty headshot in a clean side-profile with the chin level and jaw visible",
        "tight beauty headshot in a stronger side-profile with the eye-line toward camera",
        "tight beauty headshot turned close to profile with a subtle over-shoulder eye contact",
    ),
    "chin_up": (
        "tight beauty headshot with the chin gently lifted and eyes into camera",
        "tight beauty headshot with a chin-up angle and soft direct gaze",
        "tight beauty headshot with the chin slightly raised and the jaw line open",
    ),
    "chin_down": (
        "tight beauty headshot with chin slightly lowered and a cool direct gaze",
        "tight beauty headshot with a gentle head tilt and a chin-down close-up",
        "tight beauty headshot with the head tipped softly down and direct eye contact",
    ),
    "strong_turn": (
        "tight beauty headshot with a strong head turn and over-shoulder eye contact",
        "tight beauty headshot in a decisive strong-turn profile with the jaw still visible",
        "tight beauty headshot turned sharply off-axis with one eye cutting back to camera",
    ),
}
CLOSE_UP_BUCKET_ORDER = ("front", "three_quarter", "profile", "chin_up", "chin_down", "strong_turn")

TIGHT_PORTRAIT_ANGLE_BUCKETS: dict[str, tuple[str, ...]] = {
    "front": (
        "portrait crop facing camera with relaxed shoulders and direct eye contact",
        "portrait crop with a centered forward stance and chin level",
    ),
    "three_quarter": (
        "portrait crop with shoulders angled slightly toward camera",
        "portrait crop with a stronger three-quarter head turn toward camera",
        "portrait crop with one shoulder leading and a direct gaze",
    ),
    "profile": (
        "portrait crop with the head turned close to profile and eyes cutting back to camera",
        "portrait crop in a side-profile stance with the jaw line clean and one eye toward camera",
        "portrait crop in a side-profile with the chin level and the shoulder line soft",
    ),
    "chin_up": (
        "portrait crop with the chin gently lifted and a clean eye-line toward camera",
        "portrait crop with a chin-up angle and relaxed shoulders",
        "portrait crop with the chin slightly raised and the neck line open",
    ),
    "chin_down": (
        "portrait crop with chin slightly lowered and shoulders relaxed",
        "portrait crop with a subtle chin-down tilt and direct eye contact",
        "portrait crop with the head tipped gently down and a soft gaze back to camera",
    ),
    "strong_turn": (
        "portrait crop with a strong turn through the shoulders and a back-to-camera glance",
        "portrait crop with a decisive strong-turn profile and one eye toward camera",
        "portrait crop with the body turned sharply off-axis and the jaw line clean",
    ),
}
TIGHT_PORTRAIT_BUCKET_ORDER = ("front", "three_quarter", "profile", "chin_up", "chin_down", "strong_turn")
ACTIVE_OUTFIT_FAMILY_IDS = {
    "workout_top_leggings",
    "zip_jacket_leggings",
    "training_jacket_trousers",
    "zip_front_training_set",
    "cross_strap_keyhole_active_set",
    "polo_pleated_skirt",
}
ACTIVE_FOOTWEAR_TOKENS = ("trainer", "trainers", "sneaker", "sneakers", "tennis shoes", "running shoes", "keds")


@functools.lru_cache(maxsize=1)
def _render_styling_lookups() -> dict[str, dict[str, dict[str, Any]]]:
    styling = _load_static_data_bank()["styling"]
    return {
        "outfit_families": _lookup_by_id(styling["outfit_families"]),
        "color_stories": _lookup_by_id(styling["color_stories"]),
    }


def _article_for(value: str) -> str:
    return "an" if value[:1].lower() in {"a", "e", "i", "o", "u"} else "a"


def _seeded_random(*parts: Any) -> random.Random:
    seed = "|".join(str(part or "") for part in parts)
    return random.Random(seed)


def _color_story_components(color_story_id: str, color_story: str) -> tuple[str, str | None]:
    override = COLOR_STORY_RENDER_OVERRIDES.get(color_story_id)
    if override is not None:
        return override["primary"], override.get("secondary")

    base = (color_story or "").strip()
    for suffix in (" accent story", " palette", " story", " accent"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    if " and " in base:
        primary, secondary = base.split(" and ", 1)
        return primary.strip(), secondary.strip()
    return base.strip(), None


def _outfit_color_layout(outfit_id: str, outfit_text: str, outfit_tags: set[str]) -> str:
    text = outfit_text.lower()
    if outfit_id in {"thigh_high_bodysuit_robe", "robe_layered_slip_set"} or "robe layer" in text:
        return "layered_robe"
    if outfit_tags & {"shirt_layer", "layered"} or any(token in text for token in (" over ", " under ", " trench coat", "overshirt", "blazer")):
        return "layered_outer"
    if "trousers" in text or "trouser" in text or "joggers" in text or outfit_tags & {"trousers"}:
        return "top_trousers"
    if "skirt" in text:
        return "top_skirt"
    if any(token in text for token in ("leggings", "shorts", "bottoms")):
        return "top_bottoms"
    return "single_piece"


def _pattern_pool(scene_family_id: str, outfit_tags: set[str]) -> list[str]:
    if scene_family_id in {"coastal_pool", "coastal_boardwalk"}:
        return ["subtle palm print", "soft resort stripe", "washed cabana stripe"]
    if scene_family_id in {"courtyard_garden", "garden_conservatory"}:
        return ["small floral print", "tonal botanical pattern", "soft leaf motif"]
    if outfit_tags & {"sporty", "activewear"}:
        return ["clean racing stripe", "tonal geometric paneling", "subtle track stripe"]
    if outfit_tags & {"editorial", "night", "clubwear"}:
        return ["tonal geometric pattern", "subtle abstract pattern", "quiet animal-jacquard pattern"]
    if outfit_tags & {"reserved", "quiet_luxury", "tailored", "modest_safe"}:
        return ["fine pinstripe", "quiet geometric jacquard", "small windowpane check"]
    return ["subtle floral print", "fine stripe", "quiet geometric pattern"]


def _layout_targets(layout: str) -> tuple[str, str]:
    if layout == "layered_robe":
        return "base piece", "robe layer"
    if layout == "layered_outer":
        return "base piece", "outer layer"
    if layout == "top_trousers":
        return "top", "trousers"
    if layout == "top_skirt":
        return "top", "skirt"
    if layout == "top_bottoms":
        return "top", "bottoms"
    return "piece", "piece"


def _colors_are_visually_close(primary: str, secondary: str | None) -> bool:
    if not primary or not secondary:
        return False
    neutral_tokens = {
        "cream",
        "taupe",
        "smoke",
        "stone",
        "camel",
        "brown",
        "champagne",
        "rosewood",
        "dusty",
        "soft",
        "earthy",
        "winter",
        "noir",
        "ink",
        "chocolate",
    }
    primary_tokens = set(primary.lower().split())
    secondary_tokens = set(secondary.lower().split())
    if primary_tokens == secondary_tokens:
        return True
    return bool(primary_tokens & neutral_tokens and secondary_tokens & neutral_tokens)


def _pick_outfit_color_mode(
    chooser: random.Random,
    *,
    primary: str,
    secondary: str | None,
    has_secondary: bool,
    allow_pattern: bool,
    layout: str,
    boost_split_for_close_colors: bool = False,
) -> str:
    if not has_secondary:
        if allow_pattern:
            return chooser.choices(["single", "pattern"], weights=[90, 10], k=1)[0]
        return "single"

    if layout in {"layered_robe", "layered_outer", "top_trousers", "top_skirt", "top_bottoms"}:
        modes = ["single", "split", "dual"]
        weights = [55, 35, 10]
        if _colors_are_visually_close(primary, secondary):
            weights = [35, 50, 5]
            if boost_split_for_close_colors:
                weights = [20, 65, 5]
        if allow_pattern:
            modes.insert(2, "pattern")
            if _colors_are_visually_close(primary, secondary):
                weights = [30, 45, 15, 10]
                if boost_split_for_close_colors:
                    weights = [18, 57, 15, 10]
            else:
                weights = [50, 30, 10, 10]
        return chooser.choices(modes, weights=weights, k=1)[0]

    if allow_pattern:
        return chooser.choices(["single", "pattern", "dual"], weights=[80, 10, 10], k=1)[0]
    return chooser.choices(["single", "dual"], weights=[90, 10], k=1)[0]


def _pattern_friendly_outfit(outfit_text: str, outfit_tags: set[str]) -> bool:
    text = outfit_text.lower()
    if outfit_tags & {"dress", "layered", "shirt_layer", "separates", "tailored", "sporty", "activewear"}:
        return True
    return any(token in text for token in ("shirt", "dress", "skirt", "robe", "overshirt", "blazer", "polo", "tee", "swim"))


def _append_material(outfit_text: str, material: str) -> str:
    if not material:
        return outfit_text
    if "finish" in material:
        return f"{outfit_text} with {material}"
    return f"{outfit_text} in {material}"


def _without_leading_article(value: str) -> str:
    lowered = value.lower()
    for article in ("a ", "an ", "the "):
        if lowered.startswith(article):
            return value[len(article) :].strip()
    return value


def _candidate_needs_active_footwear(candidate: dict[str, Any]) -> bool:
    outfit_family_id = str(candidate.get("outfit_family_id", "") or "")
    route = str(candidate.get("route", "") or "")
    tags = set(candidate.get("tags", [])) | set(candidate.get("setting_tags", []))
    if outfit_family_id in ACTIVE_OUTFIT_FAMILY_IDS:
        return True
    if route == "sports_flirt":
        return True
    return bool(tags & {"sporty", "active", "activewear", "gym", "track", "stadium"})


def _append_active_footwear(block: str, candidate: dict[str, Any]) -> str:
    if not block or not _candidate_needs_active_footwear(candidate):
        return block
    lowered = block.lower()
    if any(token in lowered for token in ACTIVE_FOOTWEAR_TOKENS):
        return block
    return f"{block} with clean trainers"


def render_outfit_phrase_from_parts(
    *,
    outfit_family_id: str,
    outfit_family: str,
    color_story_id: str,
    color_story: str,
    material: str,
    scene_family_id: str = "",
    seed_parts: tuple[Any, ...] = (),
    boost_split_for_close_colors: bool = False,
    render_mode_override: str = "",
) -> str:
    lookups = _render_styling_lookups()
    outfit_record = lookups["outfit_families"].get(outfit_family_id, {})
    outfit_tags = set(outfit_record.get("tags", []))
    layout = _outfit_color_layout(outfit_family_id, outfit_family, outfit_tags)
    primary, secondary = _color_story_components(color_story_id, color_story)
    base = _append_material(outfit_family, material)
    if not primary:
        phrase = base
        return f"{_article_for(phrase)} {phrase}"

    chooser = _seeded_random(
        "outfit_render",
        outfit_family_id,
        color_story_id,
        material,
        scene_family_id,
        *seed_parts,
    )
    allow_pattern = _pattern_friendly_outfit(outfit_family, outfit_tags)
    if render_mode_override in {"single", "dual", "pattern", "split"} and (render_mode_override != "pattern" or allow_pattern):
        mode = render_mode_override
    else:
        mode = _pick_outfit_color_mode(
            chooser,
            primary=primary,
            secondary=secondary,
            has_secondary=bool(secondary),
            allow_pattern=allow_pattern,
            layout=layout,
            boost_split_for_close_colors=boost_split_for_close_colors,
        )
    pattern = chooser.choice(_pattern_pool(scene_family_id, outfit_tags)) if mode == "pattern" else ""

    if mode == "single":
        color_clause = f"rendered in {primary}"
    elif mode == "dual" and secondary:
        color_clause = f"using a {primary} and {secondary} palette"
    elif mode == "pattern":
        if layout == "single_piece":
            color_clause = f"rendered in {primary} with a {pattern}"
        else:
            base_target, accent_target = _layout_targets(layout)
            accent_color = secondary or primary
            color_clause = f"with {primary} on the {base_target} and a {pattern} in {accent_color} on the {accent_target}"
    elif secondary:
        base_target, accent_target = _layout_targets(layout)
        color_clause = f"with {primary} on the {base_target} and {secondary} on the {accent_target}"
    else:
        color_clause = f"rendered in {primary}"

    phrase = f"{base}, {color_clause}"
    return f"{_article_for(phrase)} {phrase}"


def render_outfit_phrase(candidate: dict[str, Any]) -> str:
    return render_outfit_phrase_from_parts(
        outfit_family_id=str(candidate.get("outfit_family_id", "") or ""),
        outfit_family=str(candidate.get("outfit_family", "") or ""),
        color_story_id=str(candidate.get("color_story_id", "") or ""),
        color_story=str(candidate.get("color_story", "") or ""),
        material=str(candidate.get("material", "") or ""),
        scene_family_id=str(candidate.get("scene_family_id", "") or ""),
        seed_parts=(
            candidate.get("setting_scene_id", ""),
            candidate.get("setting_micro_id", ""),
            candidate.get("photo_treatment_id", ""),
            candidate.get("time_of_day_id", ""),
        ),
        render_mode_override=str(candidate.get("outfit_render_mode_override", "") or ""),
    )


def render_male_outfit_phrase(
    color: str,
    outfit_text: str,
    *,
    scene_family_id: str = "",
    seed_parts: tuple[Any, ...] = (),
) -> str:
    lowered = outfit_text.lower()
    embedded_color_tokens = {
        "black",
        "dark",
        "white",
        "cream",
        "charcoal",
        "navy",
        "stone",
        "sand",
        "espresso",
        "graphite",
        "taupe",
    }
    has_embedded_color = any(f" {token} " in f" {lowered} " for token in embedded_color_tokens)
    phrase = outfit_text.strip() if has_embedded_color or not color else f"{color} {outfit_text}".strip()
    chooser = _seeded_random("male_outfit_render", color, outfit_text, scene_family_id, *seed_parts)
    pattern_friendly = any(token in outfit_text.lower() for token in ("shirt", "overshirt", "polo", "tee", "blazer", "camp-collar"))
    if pattern_friendly and chooser.random() < 0.10:
        pattern = chooser.choice(_pattern_pool(scene_family_id, {"tailored" if "blazer" in outfit_text.lower() else "clean"}))
        if "overshirt" in outfit_text.lower() or "blazer" in outfit_text.lower():
            phrase = f"{phrase} with a {pattern} on the outer layer"
        elif "polo" in outfit_text.lower():
            phrase = f"{phrase} with a {pattern} on the polo"
        elif "tee" in outfit_text.lower() or "t-shirt" in outfit_text.lower():
            phrase = f"{phrase} with a {pattern} on the tee"
        else:
            phrase = f"{phrase} with a {pattern} on the shirt"
    return f"{_article_for(phrase)} {phrase}"


def _effective_capture_text(candidate: dict[str, Any]) -> str:
    return str(candidate.get("capture_style_render") or candidate.get("capture_style") or "photo").strip()


def _effective_lighting_text(candidate: dict[str, Any]) -> str:
    return str(candidate.get("lighting_render") or candidate.get("lighting_family") or "").strip()


def _effective_camera_framing_text(candidate: dict[str, Any]) -> str:
    framing_id = str(candidate.get("camera_framing_id") or "").strip()
    overrides = {
        "close_portrait": "close portrait with full head and hair visible, breathing room above the head, framed around the upper chest, no top-of-head crop",
        "head_and_shoulders": "head-and-shoulders portrait with full head and hair visible, breathing room above the head, cropped above the chest, no top-of-head crop",
        "face_only": "tight beauty headshot with full face and hair visible, a little breathing room above the head, a hint of neck or upper shoulders visible, avoid ultra-tight face-only crop",
        "bust_up": "bust-up portrait with full head and hair visible, breathing room above the head, cropped slightly below the chest, no top-of-head crop",
        "below_chest_portrait": "portrait with full head and hair visible, breathing room above the head, framed to slightly below the chest, no top-of-head crop",
        "waist_up": "waist-up portrait with full head and hair visible, breathing room above the head, no top-of-head crop",
        "knee_up": "knee-up fashion framing",
        "cowboy_shot": "cowboy-shot framing, cropped around mid-thigh",
        "full_body": "full-length framing, camera far enough from the subject to keep the whole standing figure in frame, centered as a full-height composition with ankles or feet visible when the pose allows, avoid waist-up, mid-shot, and portrait crop",
        "ankle_up": "full-length figure framing, camera far enough from the subject to keep the whole figure in frame, centered as a full-height composition with the crop landing near the ankles, avoid waist-up, mid-shot, and portrait crop",
    }
    return overrides.get(framing_id, str(candidate.get("camera_framing") or "").strip())


def _portrait_visible_outfit_text(outfit_text: str) -> str:
    visible_text = str(outfit_text or "").strip()
    cropped_text = visible_text
    lowered = cropped_text.lower()
    for separator in (" paired with ", " with "):
        index = lowered.find(separator)
        if index > 0:
            cropped_text = cropped_text[:index].strip()
            lowered = cropped_text.lower()
            break
    for separator in (", ",):
        index = lowered.find(separator)
        if index > 0:
            trailing_text = cropped_text[index + len(separator) :].strip()
            if any(token in trailing_text.lower() for token in LOWER_BODY_OUTFIT_TOKENS):
                cropped_text = cropped_text[:index].strip()
                lowered = cropped_text.lower()
                break
    for separator in (" and ",):
        index = lowered.find(separator)
        if index > 0:
            trailing_text = cropped_text[index + len(separator) :].strip()
            if any(token in trailing_text.lower() for token in LOWER_BODY_OUTFIT_TOKENS):
                cropped_text = cropped_text[:index].strip()
                lowered = cropped_text.lower()
                break
    sanitized_text = re.sub(r"\b(micro mini|micro|mini|midi|maxi|short)\s+((?:shirt\s+)?dress)\b", r"\2", cropped_text, flags=re.IGNORECASE)
    sanitized_text = re.sub(r"\s{2,}", " ", sanitized_text).strip()
    if sanitized_text:
        return sanitized_text
    return visible_text


def _portrait_safe_hand_action(hand_action: str, *, tight_crop: bool) -> str:
    normalized_action = str(hand_action or "").strip()
    lowered = normalized_action.lower()
    blocked_tokens = TIGHT_PORTRAIT_BLOCKED_ACTION_TOKENS if tight_crop else LOWER_BODY_ACTION_TOKENS
    if any(token in lowered for token in blocked_tokens):
        return ""
    return normalized_action


def _women_pose_needs_underarm_grooming(candidate: dict[str, Any], pose_text: str) -> bool:
    pose_id_tokens = {
        str(candidate.get("pose_family_id") or "").strip().lower(),
        str(candidate.get("line_bank_pose_id") or "").strip().lower(),
    }
    if {"hands_up_fixing_hair", "arms_above_head_stand"} & pose_id_tokens:
        return True

    lowered = str(pose_text or "").strip().lower()
    return any(
        token in lowered
        for token in (
            "both hands lifted",
            "both arms extended above the head",
            "arms extended above the head",
            "arms raised straight above head",
            "arms above the head",
            "as if fixing her hair",
            "one hand lifted to the hairline",
        )
    )


def _close_up_angle_bucket(pose_seed: tuple[Any, ...], bucket_order: tuple[str, ...], batch_index: int | None) -> str:
    """Pick an angle bucket deterministically, cycling through all buckets when batch_index is available."""
    if batch_index is not None:
        return bucket_order[batch_index % len(bucket_order)]
    chooser = _seeded_random(*pose_seed)
    return chooser.choice(bucket_order)


def _framing_aware_pose_text(candidate: dict[str, Any]) -> tuple[str, str]:
    framing_id = str(candidate.get("camera_framing_id") or "").strip()
    pose_text = str(candidate.get("pose_render") or candidate.get("line_bank_pose") or candidate["pose_family"]).strip()
    hand_action = str(candidate.get("hand_action", "")).strip()
    pose_seed = (
        framing_id,
        str(candidate.get("pose_family_id") or ""),
        str(candidate.get("line_bank_pose_id") or ""),
        str(candidate.get("setting_scene_id") or ""),
        str(candidate.get("photo_treatment_id") or ""),
    )
    batch_index: int | None = candidate.get("_batch_index")
    if framing_id == "face_only":
        bucket = _close_up_angle_bucket(pose_seed, CLOSE_UP_BUCKET_ORDER, batch_index)
        phrases = CLOSE_UP_ANGLE_BUCKETS[bucket]
        chooser = _seeded_random("face_only_pose_phrase", bucket, *pose_seed)
        return chooser.choice(phrases), ""
    if framing_id in TIGHT_PORTRAIT_FRAMING_IDS:
        bucket = _close_up_angle_bucket(pose_seed, TIGHT_PORTRAIT_BUCKET_ORDER, batch_index)
        phrases = TIGHT_PORTRAIT_ANGLE_BUCKETS[bucket]
        chooser = _seeded_random("tight_portrait_pose_phrase", bucket, *pose_seed)
        return chooser.choice(phrases), _portrait_safe_hand_action(hand_action, tight_crop=True)
    if framing_id in PORTRAIT_FRAMING_IDS:
        return "upper-body pose with a slight torso angle", _portrait_safe_hand_action(hand_action, tight_crop=False)
    return pose_text, hand_action


@functools.lru_cache(maxsize=1)
def _render_prompt_opener_lookups() -> dict[str, dict[str, dict[str, Any]]]:
    prompt_openers = _load_static_data_bank()["prompt_openers"]
    return {
        "framings": _lookup_by_id(prompt_openers["framings"]),
        "treatments": _lookup_by_id(prompt_openers["treatments"]),
    }


def _framing_opener_label(candidate: dict[str, Any]) -> str:
    framing_id = str(candidate.get("camera_framing_id") or "").strip()
    record = _render_prompt_opener_lookups()["framings"].get(framing_id, {})
    return str(record.get("lead") or "framed").strip()


def _treatment_opener_noun(candidate: dict[str, Any]) -> str:
    treatment_id = str(candidate.get("photo_treatment_id") or "").strip()
    record = _render_prompt_opener_lookups()["treatments"].get(treatment_id, {})
    return str(record.get("noun") or _effective_capture_text(candidate) or "photo").strip()


def _render_prompt_opener(candidate: dict[str, Any]) -> str:
    opener = f'{_framing_opener_label(candidate)} {_treatment_opener_noun(candidate)}'.strip()
    return opener.capitalize()


def _render_technical_block(
    candidate: dict[str, Any],
    *,
    lighting_override: str | None = None,
    time_override: str | None = None,
) -> str:
    framing_id = str(candidate.get("camera_framing_id") or "").strip()
    framing_term = "" if framing_id in {"full_body", "ankle_up"} else "headroom"
    parts = [
        candidate.get("camera_angle", ""),
        lighting_override or _effective_lighting_text(candidate),
        time_override or candidate.get("time_of_day", ""),
        candidate.get("camera_vibe", ""),
        candidate.get("color_grade", ""),
        candidate.get("lens_look", ""),
        "shallow depth",
        "crisp detail",
        candidate.get("finish_render") or "natural skin texture",
        framing_term,
    ]
    return ", ".join(part for part in parts if part)


def _format_subject_identity_block(candidate: dict[str, Any]) -> str:
    beauty_phrase = {
        "beautified and flattering": "flattering read",
        "beautified with polished glam appeal": "polished glam read",
    }.get(candidate["beauty_level"], f'{candidate["beauty_level"]} read')
    ethnicity = candidate.get("ethnicity_override") or candidate["ethnicity"]
    hair_color = candidate.get("hair_color_override") or candidate["hair_color"]
    hair_structure = candidate.get("hair_structure_override") or candidate["hair_structure"]
    appearance_prompt = str(candidate.get("appearance_prompt", "")).strip()
    subject_name = candidate.get("subject_name", "").strip()
    lowered_ethnicity = ethnicity.lower()
    if lowered_ethnicity.endswith((" woman", " women", " girl")):
        base_identity = ethnicity
    else:
        base_identity = f"{ethnicity} woman"
    if subject_name:
        subject_identity = f"{base_identity} named {subject_name}"
    else:
        subject_identity = base_identity
    if subject_name:
        locked_identity = f"the same woman named {subject_name}"
    else:
        locked_identity = "the same woman in every prompt"
    suffix_parts: list[str] = []
    if candidate.get("core_identity_prompt"):
        suffix_parts.append(f'core identity notes: {candidate["core_identity_prompt"]}')
    age_phrase = str(candidate["age_band"]).replace(" years old", "-year-old")
    framing_id = str(candidate.get("camera_framing_id") or "").strip()
    compact_face_only = framing_id == "face_only"
    if appearance_prompt and candidate.get("person_mode") == "same_person":
        if compact_face_only:
            return f'{locked_identity} with a {beauty_phrase}{", " + ", ".join(suffix_parts) if suffix_parts else ""}'
        return f'{locked_identity} with a {beauty_phrase}, {candidate["body_type"]}, {candidate["breast_size"]}{", " + ", ".join(suffix_parts) if suffix_parts else ""}'
    if appearance_prompt:
        if compact_face_only:
            return f'a {age_phrase} {subject_identity} with a {beauty_phrase}{", " + ", ".join(suffix_parts) if suffix_parts else ""}'
        return f'a {age_phrase} {subject_identity} with a {beauty_phrase}, {candidate["body_type"]}, {candidate["breast_size"]}{", " + ", ".join(suffix_parts) if suffix_parts else ""}'
    if candidate.get("core_identity_prompt") and candidate.get("person_mode") == "same_person":
        if compact_face_only:
            return f'{locked_identity} with a {beauty_phrase}, {hair_color} in {hair_structure}, {candidate["eye_color"]}, and {candidate["makeup_style"]}{", " + ", ".join(suffix_parts) if suffix_parts else ""}'
        return f'{locked_identity} with a {beauty_phrase}, {candidate["body_type"]}, {candidate["breast_size"]}, {hair_color} in {hair_structure}, {candidate["eye_color"]}, and {candidate["makeup_style"]}{", " + ", ".join(suffix_parts) if suffix_parts else ""}'
    if compact_face_only:
        return f'a {age_phrase} {subject_identity} with a {beauty_phrase}, {hair_color} in {hair_structure}, {candidate["eye_color"]}, and {candidate["makeup_style"]}{", " + ", ".join(suffix_parts) if suffix_parts else ""}'
    return f'a {age_phrase} {subject_identity} with a {beauty_phrase}, {candidate["body_type"]}, {candidate["breast_size"]}, {hair_color} in {hair_structure}, {candidate["eye_color"]}, and {candidate["makeup_style"]}{", " + ", ".join(suffix_parts) if suffix_parts else ""}'


def _format_subject_block(candidate: dict[str, Any]) -> str:
    return f'{_render_prompt_opener(candidate)} of {_format_subject_identity_block(candidate)}'


def _format_outfit_block(candidate: dict[str, Any]) -> str:
    if candidate.get("appearance_prompt"):
        return f'Appearance: {candidate["appearance_prompt"]}'
    framing_id = str(candidate.get("camera_framing_id") or "").strip()
    if framing_id == "face_only":
        return ""
    line_bank_outfit = str(candidate.get("line_bank_outfit", "")).strip()
    if line_bank_outfit:
        outfit_text = _portrait_visible_outfit_text(line_bank_outfit) if framing_id in PORTRAIT_FRAMING_IDS else line_bank_outfit
        line_bank_phrase = render_outfit_phrase_from_parts(
            outfit_family_id=str(candidate.get("outfit_family_id", "") or ""),
            outfit_family=_without_leading_article(outfit_text),
            color_story_id=str(candidate.get("color_story_id", "") or ""),
            color_story=str(candidate.get("color_story", "") or ""),
            material="",
            scene_family_id=str(candidate.get("scene_family_id", "") or ""),
            seed_parts=(
                candidate.get("setting_scene_id", ""),
                candidate.get("setting_micro_id", ""),
                candidate.get("photo_treatment_id", ""),
                candidate.get("time_of_day_id", ""),
                candidate.get("line_bank_outfit_id", ""),
            ),
            boost_split_for_close_colors=True,
            render_mode_override=str(candidate.get("outfit_render_mode_override", "") or ""),
        )
        return _append_active_footwear(f"Wearing {line_bank_phrase}", candidate)
    if framing_id in PORTRAIT_FRAMING_IDS:
        upper_visible_outfit = _portrait_visible_outfit_text(str(candidate.get("outfit_family", "") or ""))
        return _append_active_footwear("Wearing " + render_outfit_phrase_from_parts(
            outfit_family_id=str(candidate.get("outfit_family_id", "") or ""),
            outfit_family=upper_visible_outfit,
            color_story_id=str(candidate.get("color_story_id", "") or ""),
            color_story=str(candidate.get("color_story", "") or ""),
            material=str(candidate.get("material", "") or ""),
            scene_family_id=str(candidate.get("scene_family_id", "") or ""),
            seed_parts=(
                candidate.get("setting_scene_id", ""),
                candidate.get("setting_micro_id", ""),
                candidate.get("photo_treatment_id", ""),
                candidate.get("time_of_day_id", ""),
                "portrait_visible_outfit",
            ),
        ), candidate)
    return _append_active_footwear(f'Wearing {render_outfit_phrase(candidate)}', candidate)


def _format_character_block(candidate: dict[str, Any]) -> str:
    return resolve_character_constraint_segment(candidate=candidate)


def _format_pose_block(candidate: dict[str, Any]) -> str:
    pose_text, hand_action = _framing_aware_pose_text(candidate)
    details: list[str] = []
    if hand_action:
        details.append(hand_action)
    if _women_pose_needs_underarm_grooming(candidate, pose_text):
        details.append("clean-shaven underarms")
    if details:
        return f'Pose: {pose_text}, {", ".join(details)}'
    return f'Pose: {pose_text}'


def _format_mood_block(candidate: dict[str, Any]) -> str:
    line_bank_expression = str(candidate.get("line_bank_expression", "")).strip()
    if line_bank_expression:
        return f'{candidate["mood_energy"]}, expression: {line_bank_expression}, direct eye contact'
    return f'{candidate["mood_energy"]}, direct eye contact'


def _format_setting_block(candidate: dict[str, Any]) -> str:
    line_bank_location = str(candidate.get("line_bank_location", "")).strip()
    if line_bank_location:
        setting_scene = line_bank_location
    else:
        setting_scene = str(candidate.get("setting_scene", "")).strip()
    setting = f'Set in {setting_scene}'
    if candidate.get("exact_theme"):
        setting += f', theme: {candidate["exact_theme"]}'
    return setting


def _format_framing_block(candidate: dict[str, Any]) -> str:
    framing_id = str(candidate.get("camera_framing_id") or "").strip()
    pose_source = str(candidate.get("line_bank_pose") or candidate.get("pose_render") or candidate.get("pose_family") or "")
    pose_tags = infer_pose_line_tags(pose_source)
    if framing_id == "full_body":
        if "standing_like" in pose_tags:
            return "Framing: true full-length standing shot, camera pulled back to keep her whole standing figure visible in frame, centered as a full-height composition, feet visible when the pose allows, no waist-up crop, no mid-shot crop, no portrait crop"
        return "Framing: true full-length figure shot, camera pulled back to keep the whole figure visible in frame, centered as a full-height composition, no waist-up crop, no mid-shot crop, no portrait crop"
    if framing_id == "ankle_up":
        if "standing_like" in pose_tags:
            return "Framing: true full-length standing shot, camera pulled back to keep her whole standing figure visible in frame, centered as a full-height composition, framing lands near the ankles, no waist-up crop, no mid-shot crop, no portrait crop"
        return "Framing: true full-length figure shot, camera pulled back to keep the whole figure visible in frame, centered as a full-height composition, framing lands near the ankles, no waist-up crop, no mid-shot crop, no portrait crop"
    if framing_id == "close_portrait":
        return "Framing: close portrait with full head and hair visible, a little breathing room above the head, the crop landing around the upper chest, and no top-of-head crop"
    if framing_id == "head_and_shoulders":
        return "Framing: head-and-shoulders portrait with full head and hair visible, a little breathing room above the head, cropped above the chest, and no top-of-head crop"
    if framing_id == "face_only":
        return "Framing: tight beauty headshot with full face and hair visible, a little breathing room above the head, a hint of neck or upper shoulders visible, and no ultra-tight face-only crop"
    if framing_id in {"waist_up", "bust_up", "below_chest_portrait"}:
        return "Framing: chest-up portrait with full head and hair visible, a little breathing room above the head, and no top-of-head crop"
    return ""


def render_candidate_segments(candidate: dict[str, Any]) -> dict[str, str]:
    contracted = apply_shot_lane_contract(candidate)
    return {
        "capture_style": _effective_capture_text(contracted).capitalize(),
        "subject": _format_subject_block(contracted),
        "character": _format_character_block(contracted),
        "outfit": _format_outfit_block(contracted),
        "pose": _format_pose_block(contracted),
        "setting": _format_setting_block(contracted),
        "framing": _format_framing_block(contracted),
        "mood": _format_mood_block(contracted),
        "technical": _render_technical_block(contracted),
    }


def render_candidate_prompt(candidate: dict[str, Any]) -> str:
    segments = render_candidate_segments(candidate)
    ordered_parts = [segments["subject"], segments["technical"]]
    if segments.get("character"):
        ordered_parts.append(segments["character"])
    ordered_parts.extend([segments["outfit"], segments["pose"], segments["setting"], segments.get("framing", ""), segments["mood"]])
    return ". ".join(part for part in ordered_parts if part) + "."
