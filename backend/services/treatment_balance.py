from __future__ import annotations

from collections import Counter
from typing import Any

from backend.photo_treatment_mix import (
    WOMEN_RANDOM_TREATMENT_MIX_TARGETS,
    photo_treatment_mix_bucket,
    photo_treatment_quality_tier,
    photo_treatment_tone,
)
from backend.services.photo_treatment_lookup import _photo_treatment_lookup


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
    if tags & {"outdoor", "rooftop", "sunny", "daylight", "sunlit", "summer"}:
        return "urban_outdoor"
    return "indoor"


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


def _random_flat_light_candidate(candidate: dict[str, Any]) -> bool:
    scene_family_id = candidate.get("scene_family_id")
    treatment_id = candidate.get("photo_treatment_id")
    lighting_id = candidate.get("lighting_family_id")
    if scene_family_id not in {"residential_luxury", "hospitality_suite", "culture_bookish", "garden_conservatory"}:
        return False
    if treatment_id == "casual_indoor_selfie" and lighting_id in {"clean_daylight", "soft_overcast", "warm_interior"}:
        return True
    if treatment_id == "clean_commercial" and lighting_id in {"soft_overcast", "warm_interior"}:
        return True
    return False


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


def _random_light_scene_balance_score(batch: list[dict[str, Any]]) -> int:
    if not batch:
        return 0
    total = len(batch)
    scene_groups = Counter(_random_scene_group(candidate) for candidate in batch)
    outdoor_count = sum(scene_groups.get(group, 0) for group in ("urban_outdoor", "water", "nature", "outdoor"))
    water_count = scene_groups.get("water", 0)
    nature_count = scene_groups.get("nature", 0)
    bright_count = sum(1 for candidate in batch if _is_random_bright_candidate(candidate))
    target_outdoor = round(total * 0.6)
    target_bright = round(total * 0.7)
    target_water = round(total * 0.2)
    target_nature = round(total * 0.2)
    score = 0
    score -= abs(outdoor_count - target_outdoor) * 10
    score -= abs(bright_count - target_bright) * 8
    score -= abs(water_count - target_water) * 14
    score -= abs(nature_count - target_nature) * 14
    score += max(0, 16 - abs(outdoor_count - target_outdoor) * 4)
    score += max(0, 16 - abs(bright_count - target_bright) * 4)
    score += max(0, 20 - abs(water_count - target_water) * 5)
    score += max(0, 20 - abs(nature_count - target_nature) * 5)
    muted_lighting_count = sum(1 for candidate in batch if candidate.get("lighting_family_id") in RANDOM_MUTED_LIGHTING_IDS)
    muted_treatment_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in RANDOM_MUTED_TREATMENT_IDS)
    muted_lighting_cap = max(7, round(total * 0.35))
    muted_treatment_cap = max(7, round(total * 0.35))
    cheap_flat_light_count = sum(1 for candidate in batch if _random_flat_light_candidate(candidate))
    if muted_lighting_count > muted_lighting_cap:
        score -= (muted_lighting_count - muted_lighting_cap) * 8
    if muted_treatment_count > muted_treatment_cap:
        score -= (muted_treatment_count - muted_treatment_cap) * 6
    if cheap_flat_light_count:
        score -= cheap_flat_light_count * 24
    if water_count < target_water:
        score -= (target_water - water_count) * 24
    if nature_count < target_nature:
        score -= (target_nature - nature_count) * 24
    return score


def _photo_treatment_candidate_score(candidate: dict[str, Any], style_mode: str, mode: str = "women") -> int:
    treatment_id = candidate.get("photo_treatment_id")
    if not treatment_id:
        return 0
    profile = _photo_treatment_lookup().get(treatment_id)
    if not profile:
        return 0
    score = 0
    harder_lanes = {"concept_photo_editorial", "direct_light_editorial"}
    casual_stylized_lanes = {
        "mirror_selfie",
        "disposable_camera",
        "documentary_still",
        "casual_indoor_selfie",
        "vintage_flash_photo",
        "advertising_poster_realism",
    }
    scene_family = candidate.get("scene_family_id", "")
    capture_id = candidate.get("capture_style_id", "")
    lighting_id = candidate.get("lighting_family_id", "")
    time_id = candidate.get("time_of_day_id", "")
    allowed_scenes = {str(value) for value in profile.get("allowed_scene_families", [])}
    banned_scenes = {str(value) for value in profile.get("banned_scene_families", [])}
    allowed_styles = {str(value) for value in profile.get("allowed_style_modes", [])}
    banned_styles = {str(value) for value in profile.get("banned_style_modes", [])}
    preferred_scenes = {str(value) for value in profile.get("preferred_scene_families", [])}
    preferred_styles = {str(value) for value in profile.get("preferred_style_modes", [])}
    preferred_captures = {str(value) for value in profile.get("preferred_capture_ids", [])}
    preferred_lighting = {str(value) for value in profile.get("preferred_lighting_ids", [])}
    preferred_times = {str(value) for value in profile.get("preferred_time_ids", [])}
    if allowed_scenes and scene_family not in allowed_scenes:
        score -= 24
    if scene_family in banned_scenes:
        score -= 28
    if allowed_styles and style_mode not in allowed_styles and style_mode != "random":
        score -= 18
    if style_mode in banned_styles:
        score -= 24
    if scene_family in preferred_scenes:
        score += 12
    if style_mode in preferred_styles:
        score += 9
    if capture_id in preferred_captures:
        score += 8
    if lighting_id in preferred_lighting:
        score += 8
    if time_id in preferred_times:
        score += 6
    category = candidate.get("photo_treatment_category", "")
    mix_bucket = photo_treatment_mix_bucket(str(treatment_id or ""), str(category or ""))
    quality_tier = photo_treatment_quality_tier(str(treatment_id or ""), str(category or ""))
    treatment_tone = photo_treatment_tone(str(treatment_id or ""), str(category or ""))
    if style_mode == "random":
        score += 3 if category == "stylized" else 2
        if treatment_id in harder_lanes:
            score += 8
        if treatment_id in casual_stylized_lanes:
            score += 6
        if treatment_id == "clean_commercial":
            score += 2
        if _random_flat_light_candidate(candidate):
            score -= 30
        if mode == "women":
            if mix_bucket == "phone_snapshot":
                score -= 10
            elif mix_bucket == "casual_low_end":
                score -= 18
            elif mix_bucket == "editorial_non_phone":
                score += 8
            elif mix_bucket == "polished_glam":
                score += 14
            if quality_tier == "raw_low_end":
                score -= 14
            elif quality_tier == "casual":
                score -= 6
            elif quality_tier == "clean":
                score += 4
            elif quality_tier == "premium":
                score += 6
            if treatment_tone in {"documentary", "snapshot"}:
                score -= 6
            if treatment_tone in {"beauty", "editorial", "cinematic", "dramatic"}:
                score += 4
            if treatment_id in {"direct_light_editorial", "concept_photo_editorial", "cinematic_poster_realism", "advertising_poster_realism", "studio_seamless"}:
                score += 5
            if treatment_id == "clean_commercial":
                score += 1
        if mode == "couples" and treatment_id == "clean_commercial":
            score += 3
    elif style_mode in {"nightlife", "studio", "creative_artistic"}:
        score += 8 if category == "stylized" else -3
        if treatment_id in harder_lanes:
            score += 14
        if style_mode == "nightlife" and treatment_id == "vintage_flash_photo":
            score += 10
        if style_mode == "nightlife" and treatment_id in {"direct_flash_night", "low_key_dramatic", "cinematic_poster_realism"}:
            score += 8
        if style_mode == "nightlife" and treatment_id == "clean_commercial":
            score -= 10
        if mode == "women" and style_mode == "nightlife":
            if treatment_id in {"vintage_flash_photo", "direct_flash_night", "low_key_dramatic", "cinematic_poster_realism", "disposable_camera", "concept_photo_editorial"}:
                score += 8
            if treatment_id == "clean_commercial":
                score -= 10
        if mode == "men" and style_mode == "nightlife":
            if treatment_id in {"direct_flash_night", "low_key_dramatic", "cinematic_poster_realism", "vintage_flash_photo", "direct_light_editorial", "analog_35mm"}:
                score += 12
            if treatment_id == "clean_commercial":
                score -= 18
        if style_mode == "studio" and treatment_id == "advertising_poster_realism":
            score += 10
        if style_mode == "creative_artistic" and treatment_id in {"vintage_flash_photo", "advertising_poster_realism"}:
            score += 8
        if mode == "women" and style_mode == "creative_artistic":
            if treatment_id in {"concept_photo_editorial", "direct_light_editorial", "advertising_poster_realism", "vintage_flash_photo", "documentary_still"}:
                score += 8
            if treatment_id == "clean_commercial":
                score -= 10
    elif style_mode in {"luxury", "romantic"}:
        score += 9 if category == "stylized" else -4
        if treatment_id in harder_lanes:
            score += 15 if style_mode == "luxury" else 11
        if mode == "men" and style_mode == "luxury":
            score += 12 if category == "stylized" else -10
            if treatment_id in {"direct_flash_night", "cinematic_poster_realism", "direct_light_editorial", "analog_35mm", "low_key_dramatic", "documentary_still"}:
                score += 8
            if treatment_id == "clean_commercial":
                score -= 28
        if mode == "men" and style_mode == "romantic":
            score += 16 if category == "stylized" else -14
            if treatment_id in {"analog_35mm", "documentary_still", "disposable_camera", "candid_phone_snapshot", "low_key_dramatic", "direct_light_editorial"}:
                score += 12
            if treatment_id == "clean_commercial":
                score -= 22
        if mode == "women" and style_mode == "luxury":
            if quality_tier == "raw_low_end":
                score -= 24
            elif quality_tier == "casual":
                score -= 18
            if treatment_tone in {"phone", "documentary", "snapshot"}:
                score -= 16
            if treatment_tone in {"beauty", "editorial", "cinematic", "dramatic"}:
                score += 8
            if treatment_id in {"direct_light_editorial", "concept_photo_editorial", "cinematic_poster_realism", "advertising_poster_realism", "vintage_flash_photo"}:
                score += 10
            if treatment_id == "clean_commercial":
                score -= 14
        if mode == "women" and style_mode == "romantic":
            if quality_tier == "raw_low_end":
                score -= 18
            elif quality_tier == "casual":
                score -= 12
            if treatment_tone in {"phone", "documentary", "snapshot"}:
                score -= 10
            if treatment_tone in {"beauty", "editorial", "cinematic", "filmic"}:
                score += 6
            if treatment_id in {"analog_35mm", "documentary_still", "candid_phone_snapshot", "disposable_camera", "direct_light_editorial", "cinematic_poster_realism"}:
                score += 10
            if treatment_id == "clean_commercial":
                score -= 18
        if style_mode == "luxury" and treatment_id in {"casual_indoor_selfie", "advertising_poster_realism", "vintage_flash_photo"}:
            score += 8
    elif style_mode in {"lifestyle", "urban_day"}:
        score += 7 if category == "stylized" else -2
        if treatment_id == "direct_light_editorial":
            score += 8
        if treatment_id in casual_stylized_lanes:
            score += 12
        if mode == "women" and treatment_id in {"candid_phone_snapshot", "analog_35mm", "documentary_still", "casual_indoor_selfie"}:
            score += 10
        if treatment_id == "clean_commercial":
            score -= 10
    elif style_mode in {"cultural_bookish", "creative_artistic"}:
        score += 8 if category == "stylized" else -2
        if treatment_id in casual_stylized_lanes:
            score += 10
        if style_mode == "creative_artistic" and treatment_id in {"concept_photo_editorial", "direct_light_editorial", "advertising_poster_realism"}:
            score += 8
        if style_mode == "creative_artistic" and treatment_id == "clean_commercial":
            score -= 8
    elif style_mode in {"sport", "fitness", "coastal", "vacation"}:
        score += 4 if category == "polished" else -1
        if style_mode == "fitness":
            if mode == "women":
                if category == "stylized":
                    score += 12
                if category == "polished":
                    score -= 6
                if treatment_id in {"candid_phone_snapshot", "analog_35mm", "documentary_still", "direct_light_editorial", "disposable_camera"}:
                    score += 16
                if scene_family == "wellness_spa" and treatment_id in {"candid_phone_snapshot", "analog_35mm", "documentary_still"}:
                    score += 8
                if treatment_id == "clean_commercial":
                    score -= 24
            else:
                if category == "stylized":
                    score += 5
                if treatment_id in {"candid_phone_snapshot", "analog_35mm", "documentary_still", "direct_light_editorial"}:
                    score += 10
                if treatment_id == "clean_commercial":
                    score -= 8
    if mode == "couples" and style_mode == "random":
        if category == "polished":
            score -= 12
        if category == "stylized":
            score += 16
        if treatment_id in {
            "candid_phone_snapshot",
            "casual_indoor_selfie",
            "mirror_selfie",
            "disposable_camera",
            "analog_35mm",
            "cinematic_poster_realism",
            "direct_light_editorial",
            "documentary_still",
            "concept_photo_editorial",
            "vintage_flash_photo",
            "advertising_poster_realism",
        }:
            score += 18
        if treatment_id == "clean_commercial":
            score -= 80
    return score


def _photo_treatment_batch_score(batch: list[dict[str, Any]], style_mode: str, mode: str = "women") -> int:
    if not batch:
        return 0
    if mode == "women" and style_mode == "random":
        bucket_counts = {key: 0 for key in WOMEN_RANDOM_TREATMENT_MIX_TARGETS}
        unique_buckets: dict[str, set[str]] = {key: set() for key in WOMEN_RANDOM_TREATMENT_MIX_TARGETS}
        for candidate in batch:
            treatment_id = str(candidate.get("photo_treatment_id", "") or "")
            bucket = photo_treatment_mix_bucket(treatment_id, str(candidate.get("photo_treatment_category", "") or ""))
            bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
            if treatment_id:
                unique_buckets.setdefault(bucket, set()).add(treatment_id)
        batch_size = len(batch)
        phone_count = bucket_counts.get("phone_snapshot", 0)
        casual_low_end_count = bucket_counts.get("casual_low_end", 0)
        editorial_non_phone_count = bucket_counts.get("editorial_non_phone", 0)
        polished_glam_count = bucket_counts.get("polished_glam", 0)
        target_phone = batch_size * (WOMEN_RANDOM_TREATMENT_MIX_TARGETS["phone_snapshot"] / 100.0)
        target_casual_low_end = batch_size * (WOMEN_RANDOM_TREATMENT_MIX_TARGETS["casual_low_end"] / 100.0)
        target_editorial = batch_size * (WOMEN_RANDOM_TREATMENT_MIX_TARGETS["editorial_non_phone"] / 100.0)
        target_polished = batch_size * (WOMEN_RANDOM_TREATMENT_MIX_TARGETS["polished_glam"] / 100.0)
        unique_lighting_count = len({candidate.get("lighting_family_id") for candidate in batch if candidate.get("lighting_family_id")})
        phone_excess = max(0.0, phone_count - target_phone)
        casual_low_end_excess = max(0.0, casual_low_end_count - target_casual_low_end)
        score = 84
        score -= abs(phone_count - target_phone) * 24
        score -= abs(casual_low_end_count - target_casual_low_end) * 22
        score -= abs(editorial_non_phone_count - target_editorial) * 10
        score -= abs(polished_glam_count - target_polished) * 10
        score -= phone_excess * 18
        score -= casual_low_end_excess * 22
        score += len(unique_buckets.get("editorial_non_phone", set())) * 4
        score += len(unique_buckets.get("polished_glam", set())) * 5
        score += min(len(unique_buckets.get("phone_snapshot", set())), 1) * 2
        score += min(unique_lighting_count, 5) * 3
        return int(round(score))
    targets = {
        "random": 0.65,
        "nightlife": 0.70,
        "studio": 0.65,
        "creative_artistic": 0.72,
        "luxury": 0.62,
        "romantic": 0.68,
        "old_money": 0.45,
        "lifestyle": 0.50,
        "urban_day": 0.50,
        "cultural_bookish": 0.50,
        "coastal": 0.40,
        "vacation": 0.40,
        "sport": 0.35,
        "fitness": 0.35,
    }
    target = targets.get(style_mode)
    if target is None:
        return 0
    if mode == "men" and style_mode == "luxury":
        target = 0.72
    if mode == "men" and style_mode == "romantic":
        target = 0.80
    if mode == "couples" and style_mode == "random":
        target = 0.62
    if mode == "women" and style_mode == "random":
        target = 0.62
    if mode == "women" and style_mode == "lifestyle":
        target = 0.68
    if mode == "women" and style_mode == "luxury":
        target = 0.70
    if mode == "women" and style_mode == "romantic":
        target = 0.82
    if mode == "women" and style_mode == "nightlife":
        target = 0.82
    if mode == "women" and style_mode == "creative_artistic":
        target = 0.80
    if mode == "women" and style_mode == "fitness":
        target = 0.78
    if mode == "men" and style_mode == "luxury":
        target = 0.70
    stylized_count = sum(1 for candidate in batch if candidate.get("photo_treatment_category") == "stylized")
    polished_count = sum(1 for candidate in batch if candidate.get("photo_treatment_category") == "polished")
    harder_lane_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in {"concept_photo_editorial", "direct_light_editorial"})
    casual_lane_ids = {"mirror_selfie", "disposable_camera", "documentary_still", "casual_indoor_selfie", "vintage_flash_photo", "advertising_poster_realism"}
    casual_lane_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in casual_lane_ids)
    unique_casual_lanes = len({candidate.get("photo_treatment_id") for candidate in batch if candidate.get("photo_treatment_id") in casual_lane_ids})
    unique_harder_lanes = len({candidate.get("photo_treatment_id") for candidate in batch if candidate.get("photo_treatment_id") in {"concept_photo_editorial", "direct_light_editorial"}})
    unique_lighting_count = len({candidate.get("lighting_family_id") for candidate in batch if candidate.get("lighting_family_id")})
    clean_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") == "clean_commercial")
    ratio = stylized_count / len(batch)
    diff = abs(ratio - target)
    expected_polished = len(batch) * (1 - target)
    polished_excess = max(0.0, polished_count - expected_polished)
    score = 52 - diff * 150 - polished_excess * 12
    score += min(unique_lighting_count, 5) * 3
    if style_mode == "random":
        score += min(harder_lane_count, 5) * 4
        score += unique_harder_lanes * 3
        score += min(casual_lane_count, 5) * 4
        score += unique_casual_lanes * 3
        if mode == "women":
            women_favored = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in {"disposable_camera", "documentary_still", "mirror_selfie", "candid_phone_snapshot", "vintage_flash_photo", "advertising_poster_realism"})
            score += women_favored * 4
    elif style_mode == "luxury":
        score += min(harder_lane_count, 6) * 7
        score += unique_harder_lanes * 6
        score += min(unique_lighting_count, 5) * 4
        if mode == "men":
            score += unique_lighting_count * 3
            score += stylized_count * 2
            score -= polished_count
    elif style_mode in {"studio", "creative_artistic"}:
        score += min(harder_lane_count, 6) * 8
        score += unique_harder_lanes * 6
        score += min(casual_lane_count, 3) * 3
        if style_mode == "studio":
            poster_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") == "advertising_poster_realism")
            score += poster_count * 5
        if style_mode == "creative_artistic":
            vintage_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") == "vintage_flash_photo")
            score += vintage_count * 4
    elif style_mode in {"lifestyle", "urban_day"}:
        score += min(harder_lane_count, 3) * 4
        score += unique_harder_lanes * 3
        score += min(casual_lane_count, 5) * 5
        score += unique_casual_lanes * 4
        if mode == "women" and style_mode == "lifestyle":
            lifestyle_favored = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in {"candid_phone_snapshot", "analog_35mm", "documentary_still", "disposable_camera", "casual_indoor_selfie", "direct_light_editorial"})
            score += lifestyle_favored * 4
    elif style_mode == "cultural_bookish":
        score += min(casual_lane_count, 5) * 5
        score += unique_casual_lanes * 5
    elif style_mode == "nightlife":
        vintage_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") == "vintage_flash_photo")
        score += vintage_count * 6
        if mode == "women":
            nightlife_favored = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in {"vintage_flash_photo", "direct_flash_night", "low_key_dramatic", "cinematic_poster_realism", "disposable_camera", "concept_photo_editorial"})
            score += nightlife_favored * 5
    elif style_mode == "fitness":
        if mode == "women":
            fitness_favored = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in {"candid_phone_snapshot", "analog_35mm", "documentary_still", "direct_light_editorial"})
            score += fitness_favored * 8
            score += min(casual_lane_count, 5) * 5
    if mode == "women" and style_mode == "romantic":
        romantic_favored = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in {"analog_35mm", "documentary_still", "candid_phone_snapshot", "disposable_camera", "direct_light_editorial", "cinematic_poster_realism"})
        score += romantic_favored * 5
    if mode == "men" and style_mode == "romantic":
        documentary_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in {"documentary_still", "analog_35mm", "disposable_camera", "direct_light_editorial"})
        score += documentary_count * 6
    if mode == "couples" and style_mode == "random":
        couples_favored_ids = {"candid_phone_snapshot", "casual_indoor_selfie", "mirror_selfie", "disposable_camera", "analog_35mm", "cinematic_poster_realism", "direct_light_editorial", "documentary_still", "concept_photo_editorial", "vintage_flash_photo", "advertising_poster_realism"}
        couples_favored = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in couples_favored_ids)
        unique_couples_favored = len({candidate.get("photo_treatment_id") for candidate in batch if candidate.get("photo_treatment_id") in couples_favored_ids})
        score += couples_favored * 5
        score += unique_couples_favored * 3
    clean_caps: dict[tuple[str, str], int] = {
        ("women", "random"): 4,
        ("women", "luxury"): 4,
        ("women", "nightlife"): 2,
        ("women", "creative_artistic"): 3,
        ("women", "lifestyle"): 6,
        ("women", "fitness"): 3,
        ("women", "romantic"): 2,
        ("men", "luxury"): 2,
        ("men", "romantic"): 3,
        ("couples", "random"): 4,
    }
    clean_cap = clean_caps.get((mode, style_mode))
    if clean_cap is not None and clean_count > clean_cap:
        score -= (clean_count - clean_cap) * (18 if mode == "couples" and style_mode == "random" else 12)
    if style_mode == "random":
        polished_bonus = min(polished_count, 4)
        if polished_bonus:
            score += polished_bonus * (12 if mode == "couples" else 8)
    return int(round(score))
