from __future__ import annotations

from collections import Counter
from typing import Any


CLONE_PRONE_MUTED_COLOR_IDS = {"clean_neutrals", "champagne_taupe", "rosewood_smoke"}


def _scene_family_clone_penalty(batch: list[dict[str, Any]], style_mode: str, mode: str) -> int:
    if style_mode not in {"random", "lifestyle", "luxury"}:
        return 0
    scene_counts = Counter(
        str(candidate.get("scene_family_id", "") or "")
        for candidate in batch
        if candidate.get("scene_family_id")
    )
    if not scene_counts:
        return 0
    caps_by_style = {
        "random": {"cap": 3, "penalty": 10, "focus_caps": {"garden_conservatory": 1, "residential_luxury": 5}, "focus_penalty": 24},
        "lifestyle": {"cap": 3, "penalty": 10, "focus_caps": {"garden_conservatory": 1, "residential_luxury": 5}, "focus_penalty": 20},
        "luxury": {"cap": 4, "penalty": 10, "focus_caps": {"garden_conservatory": 2}, "focus_penalty": 18},
    }
    caps = caps_by_style[style_mode]
    penalty = sum(count - caps["cap"] for count in scene_counts.values() if count > caps["cap"]) * caps["penalty"]
    for scene_family_id, cap in caps["focus_caps"].items():
        count = scene_counts.get(scene_family_id, 0)
        if count > cap:
            penalty += (count - cap) * caps["focus_penalty"]
    if mode == "women":
        penalty += max(0, scene_counts.get("garden_conservatory", 0) - caps["focus_caps"]["garden_conservatory"]) * 2
    return -penalty


def _muted_color_clone_penalty(batch: list[dict[str, Any]], style_mode: str, mode: str) -> int:
    if mode not in {"women", "couples"}:
        return 0
    style_caps = {
        "random": {"combined": 4, "per_color": 2, "combined_penalty": 14, "per_color_penalty": 12},
        "lifestyle": {"combined": 4, "per_color": 2, "combined_penalty": 14, "per_color_penalty": 12},
        "luxury": {"combined": 3, "per_color": 2, "combined_penalty": 16, "per_color_penalty": 14},
    }
    caps = style_caps.get(style_mode)
    if not caps:
        return 0
    muted_counts = Counter(
        candidate.get("color_story_id")
        for candidate in batch
        if candidate.get("color_story_id") in CLONE_PRONE_MUTED_COLOR_IDS
    )
    total_muted = sum(muted_counts.values())
    penalty = 0
    if total_muted > caps["combined"]:
        penalty += (total_muted - caps["combined"]) * caps["combined_penalty"]
    penalty += sum(count - caps["per_color"] for count in muted_counts.values() if count > caps["per_color"]) * caps["per_color_penalty"]
    return -penalty


def _outfit_silhouette_clone_penalty(batch: list[dict[str, Any]], style_mode: str, mode: str) -> int:
    if mode not in {"women", "couples"}:
        return 0
    style_caps = {
        "random": {"cap": 2, "penalty": 10},
        "lifestyle": {"cap": 2, "penalty": 10},
        "luxury": {"cap": 2, "penalty": 12},
    }
    caps = style_caps.get(style_mode)
    if not caps:
        return 0
    silhouette_counts = Counter(
        (candidate.get("outfit_family_id"), candidate.get("material_id"))
        for candidate in batch
        if candidate.get("outfit_family_id") and candidate.get("material_id")
    )
    penalty = sum(count - caps["cap"] for count in silhouette_counts.values() if count > caps["cap"]) * caps["penalty"]
    return -penalty


def _scene_outfit_clone_penalty(batch: list[dict[str, Any]], style_mode: str, mode: str) -> int:
    if mode not in {"women", "couples"}:
        return 0
    style_caps = {
        "random": {"cap": 2, "penalty": 8},
        "lifestyle": {"cap": 2, "penalty": 8},
        "luxury": {"cap": 2, "penalty": 10},
    }
    caps = style_caps.get(style_mode)
    if not caps:
        return 0
    scene_outfit_counts = Counter(
        (candidate.get("scene_family_id"), candidate.get("outfit_family_id"))
        for candidate in batch
        if candidate.get("scene_family_id") and candidate.get("outfit_family_id")
    )
    penalty = sum(count - caps["cap"] for count in scene_outfit_counts.values() if count > caps["cap"]) * caps["penalty"]
    return -penalty


def _treatment_outfit_clone_penalty(batch: list[dict[str, Any]], style_mode: str, mode: str) -> int:
    if mode not in {"women", "couples"}:
        return 0
    style_caps = {
        "random": {"cap": 2, "penalty": 8},
        "lifestyle": {"cap": 2, "penalty": 8},
        "luxury": {"cap": 2, "penalty": 10},
    }
    caps = style_caps.get(style_mode)
    if not caps:
        return 0
    treatment_outfit_counts = Counter(
        (candidate.get("photo_treatment_id"), candidate.get("outfit_family_id"))
        for candidate in batch
        if candidate.get("photo_treatment_id") and candidate.get("outfit_family_id")
    )
    penalty = sum(count - caps["cap"] for count in treatment_outfit_counts.values() if count > caps["cap"]) * caps["penalty"]
    return -penalty


def _cheap_contract_fallback_candidate(candidate: dict[str, Any]) -> bool:
    scene_family_id = str(candidate.get("scene_family_id", "") or "")
    treatment_id = str(candidate.get("photo_treatment_id", "") or "")
    lighting_id = str(candidate.get("lighting_family_id", "") or "")
    if scene_family_id in {"culture_bookish", "garden_conservatory"}:
        if treatment_id == "clean_commercial" and lighting_id in {"clean_daylight", "soft_overcast", "warm_interior"}:
            return True
    if scene_family_id in {"residential_luxury", "hospitality_suite"}:
        if treatment_id == "clean_commercial" and lighting_id in {"clean_daylight", "soft_overcast", "warm_interior"}:
            return True
        if treatment_id == "casual_indoor_selfie" and lighting_id in {"clean_daylight", "soft_overcast", "warm_interior"}:
            return True
    return False


def _cheap_contract_fallback_penalty(batch: list[dict[str, Any]], style_mode: str, mode: str) -> int:
    style_penalties = {
        "random": 18,
        "lifestyle": 16,
        "luxury": 20,
        "romantic": 16,
        "creative_artistic": 16,
        "cultural_bookish": 18,
    }
    per_candidate_penalty = style_penalties.get(style_mode)
    if per_candidate_penalty is None:
        return 0
    cheap_count = sum(1 for candidate in batch if _cheap_contract_fallback_candidate(candidate))
    if not cheap_count:
        return 0
    if mode == "women":
        per_candidate_penalty += 4
    elif mode == "couples":
        per_candidate_penalty += 2
    return -(cheap_count * per_candidate_penalty)


def _location_motif_for_candidate(candidate: dict[str, Any]) -> str:
    text = " ".join(
        str(candidate.get(field, "") or "")
        for field in ("line_bank_location", "setting_scene", "setting_micro")
    ).lower()
    if any(token in text for token in ("greenhouse", "conservatory")):
        return "conservatory_greenhouse"
    if any(token in text for token in ("citrus", "orange", "lemon", "orchard", "grove")):
        return "orchard_citrus"
    if any(token in text for token in ("pool", "lagoon", "beach", "shore", "boardwalk", "marina", "cabana", "coastal")):
        return "waterside"
    if any(token in text for token in ("garden", "park", "greenhouse", "conservatory", "courtyard", "lawn", "meadow", "field")):
        return "garden_nature"
    if any(token in text for token in ("cafe", "street", "terrace", "city", "tram", "harbor", "riverwalk", "restaurant")):
        return "urban_social"
    if any(token in text for token in ("suite", "hotel", "lounge", "living room", "apartment", "window", "kitchen")):
        return "interior_lounge"
    if any(token in text for token in ("spa", "bath", "shower", "vanity", "wellness")):
        return "wellness_private"
    if any(token in text for token in ("bar", "night", "neon", "after-dark", "cocktail")):
        return "nightlife"
    scene_family = str(candidate.get("scene_family_id", "") or "").strip()
    if scene_family:
        return f"scene::{scene_family}"
    return "unspecified"


def _location_motif_clone_penalty(batch: list[dict[str, Any]], style_mode: str, location_strategy: str) -> int:
    if style_mode not in {"random", "lifestyle", "coastal", "vacation"}:
        return 0
    if location_strategy == "exact_theme":
        return 0
    caps_by_style = {
        "random": {"cap": 4, "penalty": 7, "focus_caps": {"waterside": 4, "orchard_citrus": 2, "conservatory_greenhouse": 1}, "focus_penalty": 20},
        "lifestyle": {"cap": 4, "penalty": 7, "focus_caps": {"waterside": 4, "orchard_citrus": 2, "conservatory_greenhouse": 1}, "focus_penalty": 18},
        "coastal": {"cap": 7, "penalty": 4, "focus_caps": {"waterside": 6, "orchard_citrus": 3, "conservatory_greenhouse": 2}, "focus_penalty": 8},
        "vacation": {"cap": 6, "penalty": 5, "focus_caps": {"waterside": 5, "orchard_citrus": 3, "conservatory_greenhouse": 2}, "focus_penalty": 10},
    }
    caps = caps_by_style[style_mode]
    motif_counts = Counter(_location_motif_for_candidate(candidate) for candidate in batch)
    penalty = sum(count - caps["cap"] for count in motif_counts.values() if count > caps["cap"]) * caps["penalty"]
    for motif, motif_cap in caps["focus_caps"].items():
        count = motif_counts.get(motif, 0)
        if count > motif_cap:
            penalty += (count - motif_cap) * caps["focus_penalty"]
    return -penalty
