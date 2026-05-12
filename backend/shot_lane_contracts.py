from __future__ import annotations

from typing import Any

from backend.engine.line_bank_loader import infer_location_line_tags


SEAMLESS_STUDIO_SETTING = (
    "clean warm gray seamless studio background, clean seamless backdrop and smooth floor falloff, "
    "a clean floor shadow anchoring the frame, controlled studio air with polished separation"
)

DAYLIGHT_TOKENS = {
    "daylight",
    "bright sun",
    "bright afternoon",
    "midday",
    "noon",
    "golden hour",
    "hard white sun",
    "sunlit",
}
NIGHT_TOKENS = {
    "night",
    "after-dark",
    "after dark",
    "evening",
    "neon",
    "cocktail",
    "lamp glow",
    "dim",
    "dark",
}
CHEAP_TAIL_TAGS_BY_SCENE = {
    "hospitality_suite": {
        "institutional_like",
        "transit_like",
        "retail_like",
        "creative_like",
        "pass_through_like",
    },
    "residential_luxury": {
        "institutional_like",
        "transit_like",
        "retail_like",
        "creative_like",
        "pass_through_like",
    },
    "culture_bookish": {
        "coastal_like",
        "resort_like",
        "pool_like",
        "wet_humid_like",
    },
}


def _text(candidate: dict[str, Any], key: str) -> str:
    return str(candidate.get(key, "") or "").strip()


def _combined_setting_text(candidate: dict[str, Any]) -> str:
    return " ".join(
        part for part in (_text(candidate, "line_bank_location"), _text(candidate, "setting_scene")) if part
    ).strip()


def _has_daylight_signal(candidate: dict[str, Any]) -> bool:
    combined = " ".join(
        part
        for part in (
            _combined_setting_text(candidate),
            _text(candidate, "lighting_render"),
            _text(candidate, "time_of_day"),
        )
        if part
    ).lower()
    return any(token in combined for token in DAYLIGHT_TOKENS)


def _has_night_signal(candidate: dict[str, Any]) -> bool:
    combined = " ".join(
        part
        for part in (
            _combined_setting_text(candidate),
            _text(candidate, "lighting_render"),
            _text(candidate, "time_of_day"),
        )
        if part
    ).lower()
    return any(token in combined for token in NIGHT_TOKENS)


def _is_seamless_background(candidate: dict[str, Any]) -> bool:
    combined = " ".join(
        part for part in (_text(candidate, "setting_scene"), _text(candidate, "line_bank_location")) if part
    ).lower()
    return "seamless" in combined and "backdrop" in combined


def _location_tail_allowed(candidate: dict[str, Any], lane_id: str) -> bool:
    scene_family_id = _text(candidate, "scene_family_id")
    line_bank_location = _text(candidate, "line_bank_location")
    if not scene_family_id or not line_bank_location:
        return True
    tags = infer_location_line_tags(line_bank_location)
    if "institutional_like" in tags and scene_family_id == "studio":
        return False
    if "studio_practical_like" in tags and lane_id != "studio_practical_set":
        return False
    if lane_id == "studio_practical_set":
        return "studio_practical_like" in tags and "institutional_like" not in tags
    if scene_family_id == "garden_conservatory":
        return "garden_like" in tags
    blocked_tags = CHEAP_TAIL_TAGS_BY_SCENE.get(scene_family_id, set())
    return not bool(tags & blocked_tags)


def resolve_shot_lane_contract(candidate: dict[str, Any]) -> dict[str, str]:
    treatment_id = _text(candidate, "photo_treatment_id")
    scene_family_id = _text(candidate, "scene_family_id")

    if treatment_id == "studio_seamless":
        lane_id = "seamless_studio"
    elif treatment_id in {"direct_flash_night", "vintage_flash_photo"} or scene_family_id in {"nightlife_bar", "nightlife_neon"}:
        lane_id = "nightlife_flash"
    elif treatment_id == "low_key_dramatic":
        lane_id = "controlled_dark_interior"
    elif treatment_id == "direct_light_editorial":
        lane_id = "editorial_hard_sun"
    elif treatment_id == "concept_photo_editorial":
        lane_id = "editorial_controlled_concept"
    elif treatment_id == "clean_commercial":
        lane_id = "clean_daylight_commercial"
    elif scene_family_id == "studio":
        lane_id = "studio_practical_set"
    else:
        lane_id = "default"

    return {"lane_id": lane_id}


def apply_shot_lane_contract(candidate: dict[str, Any]) -> dict[str, Any]:
    contracted = dict(candidate)
    contract = resolve_shot_lane_contract(contracted)
    lane_id = contract["lane_id"]

    if lane_id == "seamless_studio":
        contracted["line_bank_location"] = ""
        contracted["setting_scene"] = SEAMLESS_STUDIO_SETTING
        contracted["lighting_render"] = "controlled seamless studio light"
    elif not _location_tail_allowed(contracted, lane_id):
        contracted["line_bank_location"] = ""

    time_of_day = _text(contracted, "time_of_day").lower()
    if time_of_day == "night" and (
        lane_id in {"clean_daylight_commercial", "editorial_hard_sun", "editorial_controlled_concept"}
        or _is_seamless_background(contracted)
        or _has_daylight_signal(contracted)
    ):
        contracted["time_of_day"] = "bright afternoon"
    elif time_of_day in {"morning", "bright afternoon", "golden hour", "midday", "noon"} and (
        lane_id in {"nightlife_flash", "controlled_dark_interior"} or _has_night_signal(contracted)
    ):
        contracted["time_of_day"] = "night"

    contracted["render_contract"] = contract
    return contracted
