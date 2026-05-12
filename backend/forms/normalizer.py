from __future__ import annotations

import re
from typing import Any

from backend.options import DEFAULT_FORM_STATE

from .constants import (
    ALLOWED_ANTI_REPEAT_MODES,
    ALLOWED_APPEARANCE_MODES,
    ALLOWED_BEAUTY_FINISH_CONTROLS,
    ALLOWED_BREAST_SIZE_CONTROLS,
    ALLOWED_EYE_COLOR_CONTROLS,
    ALLOWED_HAIR_COLOR_CONTROLS,
    ALLOWED_HAIR_LENGTH_MODES,
    ALLOWED_HAIRSTYLE_MODES,
    ALLOWED_LOCATION_STRATEGIES,
    ALLOWED_MAKEUP_CONTROLS,
    ALLOWED_MALE_GROOMING_CONTROLS,
    ALLOWED_MALE_HAIRSTYLE_MODES,
    ALLOWED_MALE_OUTFIT_CONTROLS,
    ALLOWED_MODES,
    ALLOWED_PERSON_MODES,
    ALLOWED_PHOTO_TREATMENT_CONTROLS,
    ALLOWED_RACE_PRESETS,
    ALLOWED_SCENE_FOCUS_MODES,
    ALLOWED_POSE_FRAMING_CONTROLS,
    ALLOWED_VALIDATION_MODES,
    ALLOWED_WOMEN_SCENE_FAMILIES,
    MALE_OUTFIT_CONTROL_ALIASES,
    OUTFIT_VIBE_CONTROL_ALIASES,
    STOP_WORDS,
    SUPPORTED_STYLE_MODES,
    ALLOWED_OUTFIT_REVEAL_MODES,
    ALLOWED_OUTFIT_VIBE_CONTROLS,
    ALLOWED_PHOTO_TYPE_CONTROLS,
)


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _normalize_choice(value: Any, allowed: set[str], default: str) -> str:
    normalized = str(value or default).strip().lower()
    return normalized if normalized in allowed else default


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _clean_text(value: Any, max_length: int = 180) -> str:
    text = " ".join(str(value or "").strip().split())
    return text[:max_length].strip()


def _tokenize_text(value: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", value.lower()) if len(token) >= 3 and token not in STOP_WORDS]


def _female_appearance_mode(form_state: dict[str, Any]) -> str:
    return _normalize_choice(form_state.get("appearanceMode", "generated"), ALLOWED_APPEARANCE_MODES, "generated")


def _male_appearance_mode(form_state: dict[str, Any]) -> str:
    return _normalize_choice(form_state.get("maleAppearanceMode", "generated"), ALLOWED_APPEARANCE_MODES, "generated")


def _female_appearance_prompt(form_state: dict[str, Any]) -> str:
    if _female_appearance_mode(form_state) != "custom":
        return ""
    return _clean_text(form_state.get("appearancePrompt", ""), max_length=260)


def _male_appearance_prompt(form_state: dict[str, Any]) -> str:
    if _male_appearance_mode(form_state) != "custom":
        return ""
    return _clean_text(form_state.get("maleAppearancePrompt", ""), max_length=260)


def _male_outfit_control_value(value: Any) -> str:
    normalized = str(value or "random").strip().lower()
    normalized = MALE_OUTFIT_CONTROL_ALIASES.get(normalized, normalized)
    return _normalize_choice(normalized, ALLOWED_MALE_OUTFIT_CONTROLS, "random")


def _outfit_vibe_control_value(value: Any) -> str:
    normalized = str(value or "random").strip().lower()
    normalized = OUTFIT_VIBE_CONTROL_ALIASES.get(normalized, normalized)
    return _normalize_choice(normalized, ALLOWED_OUTFIT_VIBE_CONTROLS, "random")


def _female_custom_appearance_active(form_state: dict[str, Any]) -> bool:
    return form_state.get("mode") in {"women", "couples"} and bool(_female_appearance_prompt(form_state))


def _male_custom_appearance_active(form_state: dict[str, Any]) -> bool:
    return form_state.get("mode") in {"men", "couples"} and bool(_male_appearance_prompt(form_state))


def _merged_form_state(incoming: dict[str, Any] | None) -> dict[str, Any]:
    if isinstance(incoming, dict) and isinstance(incoming.get("formState"), dict):
        incoming = incoming["formState"]
    merged = dict(DEFAULT_FORM_STATE)
    if incoming:
        merged.update(incoming)
    merged["mode"] = _normalize_choice(merged.get("mode", "women"), ALLOWED_MODES, "women")
    merged["personMode"] = _normalize_choice(merged.get("personMode", "different_persons"), ALLOWED_PERSON_MODES, "different_persons")
    merged["appearanceMode"] = _normalize_choice(merged.get("appearanceMode", "generated"), ALLOWED_APPEARANCE_MODES, "generated")
    merged["maleAppearanceMode"] = _normalize_choice(merged.get("maleAppearanceMode", "generated"), ALLOWED_APPEARANCE_MODES, "generated")
    merged["antiRepeat"] = _normalize_choice(merged.get("antiRepeat", "normal"), ALLOWED_ANTI_REPEAT_MODES, "normal")
    merged["outfitReveal"] = _normalize_choice(merged.get("outfitReveal", "random"), ALLOWED_OUTFIT_REVEAL_MODES, "random")
    merged["outfitVibeControl"] = _outfit_vibe_control_value(merged.get("outfitVibeControl", "random"))
    merged["beautyFinishControl"] = _normalize_choice(merged.get("beautyFinishControl", "random"), ALLOWED_BEAUTY_FINISH_CONTROLS, "random")
    merged["hairLength"] = _normalize_choice(merged.get("hairLength", "random"), ALLOWED_HAIR_LENGTH_MODES, "random")
    merged["maleHairLength"] = _normalize_choice(merged.get("maleHairLength", "short"), ALLOWED_HAIR_LENGTH_MODES, "short")
    merged["maleHairstyle"] = _normalize_choice(merged.get("maleHairstyle", "random"), ALLOWED_MALE_HAIRSTYLE_MODES, "random")
    merged["maleGroomingControl"] = _normalize_choice(merged.get("maleGroomingControl", "random"), ALLOWED_MALE_GROOMING_CONTROLS, "random")
    merged["maleOutfitControl"] = _male_outfit_control_value(merged.get("maleOutfitControl", "random"))
    merged["hairstyle"] = _normalize_choice(merged.get("hairstyle", "random"), ALLOWED_HAIRSTYLE_MODES, "random")
    merged["hairColorControl"] = _normalize_choice(merged.get("hairColorControl", "random"), ALLOWED_HAIR_COLOR_CONTROLS, "random")
    merged["makeupControl"] = _normalize_choice(merged.get("makeupControl", "random"), ALLOWED_MAKEUP_CONTROLS, "random")
    merged["eyeColorControl"] = _normalize_choice(merged.get("eyeColorControl", "random"), ALLOWED_EYE_COLOR_CONTROLS, "random")
    merged["breastSizeControl"] = _normalize_choice(merged.get("breastSizeControl", "random"), ALLOWED_BREAST_SIZE_CONTROLS, "random")
    merged["styleMode"] = _normalize_choice(merged.get("styleMode", "random"), SUPPORTED_STYLE_MODES, "random")
    merged["photoTypeControl"] = _normalize_choice(merged.get("photoTypeControl", "balanced"), ALLOWED_PHOTO_TYPE_CONTROLS, "balanced")
    merged["photoTreatmentControl"] = _normalize_choice(merged.get("photoTreatmentControl", "random"), ALLOWED_PHOTO_TREATMENT_CONTROLS, "random")
    if merged["photoTypeControl"] != "custom":
        merged["photoTreatmentControl"] = "random"
    merged["sceneFocus"] = _normalize_choice(merged.get("sceneFocus", "random"), ALLOWED_SCENE_FOCUS_MODES, "random")
    merged["womenSceneFamily"] = _normalize_choice(merged.get("womenSceneFamily", "random"), ALLOWED_WOMEN_SCENE_FAMILIES, "random")
    merged["poseFramingControl"] = _normalize_choice(merged.get("poseFramingControl", "mixed"), ALLOWED_POSE_FRAMING_CONTROLS, "mixed")
    merged["validationMode"] = _normalize_choice(merged.get("validationMode", "normal"), ALLOWED_VALIDATION_MODES, "normal")
    merged["locationStrategy"] = _normalize_choice(merged.get("locationStrategy", "fresh_only"), ALLOWED_LOCATION_STRATEGIES, "fresh_only")
    merged["batchSize"] = max(1, min(_safe_int(merged.get("batchSize", 10), 10), 100))
    merged["debugMode"] = _parse_bool(merged.get("debugMode", False))
    merged["useCoreIdentityPrompt"] = _parse_bool(merged.get("useCoreIdentityPrompt", False))
    merged["spicyLevel"] = str(merged.get("spicyLevel", "random"))
    for key in (
        "coreIdentityPrompt",
        "appearancePrompt",
        "maleAppearancePrompt",
        "name",
        "maleName",
        "customRace",
        "maleCustomRace",
        "maleCustomHair",
        "customHair",
        "customHairColor",
        "exactTheme",
        "characterConstraint",
    ):
        merged[key] = _clean_text(merged.get(key, ""))
    merged["maleAge"] = _clean_text(merged.get("maleAge", "Random"), max_length=40) or "Random"
    merged["racePreset"] = _normalize_choice(merged.get("racePreset", "random_default_split"), ALLOWED_RACE_PRESETS, "random_default_split")
    merged["maleRacePreset"] = _normalize_choice(merged.get("maleRacePreset", "random_default_split"), ALLOWED_RACE_PRESETS, "random_default_split")
    if merged["racePreset"] == "black_british":
        merged["racePreset"] = "other"
    if merged["maleRacePreset"] == "black_british":
        merged["maleRacePreset"] = "other"
    if merged["racePreset"] != "other":
        merged["customRace"] = ""
    if merged["maleRacePreset"] != "other":
        merged["maleCustomRace"] = ""
    if merged["appearanceMode"] != "custom":
        merged["appearancePrompt"] = ""
    if merged["maleAppearanceMode"] != "custom":
        merged["maleAppearancePrompt"] = ""
    if merged["hairstyle"] != "custom":
        merged["customHair"] = ""
    if merged["maleHairstyle"] != "custom":
        merged["maleCustomHair"] = ""
    if merged["hairColorControl"] != "custom":
        merged["customHairColor"] = ""
    if not _parse_bool(merged.get("allowDyedNaturalHairColors", False)):
        merged["allowDyedNaturalHairColors"] = False
    if merged["personMode"] != "same_person":
        merged["useCoreIdentityPrompt"] = False
    if merged["mode"] == "men":
        merged["useCoreIdentityPrompt"] = False
        merged["coreIdentityPrompt"] = ""
        merged["appearanceMode"] = "generated"
        merged["appearancePrompt"] = ""
        merged["outfitReveal"] = "random"
        merged["outfitVibeControl"] = "random"
        merged["beautyFinishControl"] = "random"
        merged["hairstyle"] = "random"
        merged["customHair"] = ""
        merged["hairColorControl"] = "random"
        merged["customHairColor"] = ""
        merged["makeupControl"] = "random"
        if merged["maleHairLength"] == "random":
            merged["maleHairLength"] = "short"
    if merged["mode"] in {"women", "couples"}:
        merged["maleAppearanceMode"] = "generated"
        merged["maleAppearancePrompt"] = ""
        merged["allowDyedNaturalHairColors"] = bool(merged.get("allowDyedNaturalHairColors", False)) and merged["hairColorControl"] == "random"
    else:
        merged["allowDyedNaturalHairColors"] = False
    return merged
