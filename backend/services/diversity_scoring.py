from __future__ import annotations

from collections import Counter
from typing import Any

from backend.engine import generator


FRAMING_GROUP_BY_ID = {
    "waist_up": "portrait",
    "bust_up": "portrait",
    "close_portrait": "portrait",
    "head_and_shoulders": "portrait",
    "face_only": "portrait",
    "below_chest_portrait": "portrait",
    "knee_up": "mid",
    "cowboy_shot": "mid",
    "full_body": "full",
    "ankle_up": "full",
}

WOMEN_OUTFIT_SILHOUETTE_GROUP_BY_ID = {
    "mini_dress": "fitted_short",
    "blazer_mini_dress": "fitted_short",
    "crop_top_mini_skirt": "fitted_short",
    "bodysuit_trousers": "fitted_short",
    "halter_trousers": "tailored_trousers",
    "vest_trousers": "tailored_trousers",
    "shirt_trousers": "tailored_trousers",
    "blouse_trousers": "tailored_trousers",
    "knit_top_trousers": "tailored_trousers",
    "cardigan_trousers": "tailored_trousers",
    "cashmere_shell_trousers": "tailored_trousers",
    "wrap_blouse_skirt": "elevated_skirt",
    "cami_midi_skirt": "elevated_skirt",
    "silk_blouse_midi_skirt": "elevated_skirt",
    "cardigan_skirt": "elevated_skirt",
    "mockneck_knit_skirt": "elevated_skirt",
    "structured_day_dress": "longer_day_dress",
    "column_dress": "longer_day_dress",
    "sweater_jeans": "casual_denim",
    "tee_jeans": "casual_denim",
    "swimsuit": "swimwear",
    "bikini_set": "swimwear",
    "workout_top_leggings": "sporty",
    "training_jacket_trousers": "sporty",
}

WOMEN_RANDOM_COLOR_GROUP_BY_ID = {
    "slate_blue_ink": "cool_dark",
    "navy_cream": "cool_dark",
    "emerald_noir": "cool_dark",
    "oxblood_noir": "cool_dark",
    "rosewood_smoke": "cool_dark",
    "clean_neutrals": "soft_neutral",
    "earthy_soft": "soft_neutral",
    "chocolate_cream": "soft_neutral",
    "soft_camel_cream": "soft_neutral",
    "winter_neutrals": "soft_neutral",
    "champagne_taupe": "soft_neutral",
    "dusty_rose_taupe": "soft_accent",
    "powder_blue": "soft_accent",
    "plum_blush": "soft_accent",
    "lilac_smoke": "soft_accent",
    "mint_cream": "soft_accent",
    "hot_pink": "bright_pop",
    "coral_ivory": "bright_pop",
    "tangerine_cream": "bright_pop",
    "red_ivory": "bright_pop",
    "butter_denim": "bright_fresh",
    "cobalt_white": "bright_fresh",
    "aqua_white": "bright_fresh",
    "teal_cream": "fresh_clean",
    "olive_sand": "fresh_clean",
    "sage_stone": "fresh_clean",
    "terracotta_sand": "warm_earth",
    "black_ivory": "classic_bw",
    "black_gold": "classic_bw",
    "sport_clean_white": "classic_bw",
}

SOFT_REPEAT_COLOR_STORY_IDS = {"black_gold", "black_ivory", "sport_clean_white"}

_CLOSE_UP_FRAMING_IDS = frozenset({"face_only", "close_portrait", "head_and_shoulders"})
_CLOSE_UP_BUCKET_ORDER = ("front", "three_quarter", "profile", "tilt")


def _pose_group_by_id() -> dict[str, str]:
    data = generator.data_loader.load_data_bank()
    return {
        str(item.get("id", "")): str(item.get("group", "unknown") or "unknown")
        for item in data.get("pose_bank", {}).get("pose_families", [])
        if item.get("id")
    }


def _pose_tags_by_id() -> dict[str, set[str]]:
    data = generator.data_loader.load_data_bank()
    return {
        str(item.get("id", "")): set(item.get("tags", []) or [])
        for item in data.get("pose_bank", {}).get("pose_families", [])
        if item.get("id")
    }


def _same_person_visual_diversity_score(batch: list[dict[str, Any]]) -> int:
    if not batch:
        return 0
    pose_group_lookup = _pose_group_by_id()
    pose_groups = Counter(
        pose_group_lookup.get(str(candidate.get("pose_family_id", "") or ""), "unknown")
        for candidate in batch
        if candidate.get("pose_family_id")
    )
    framing_groups = Counter(
        FRAMING_GROUP_BY_ID.get(str(candidate.get("camera_framing_id", "") or ""), "unknown")
        for candidate in batch
        if candidate.get("camera_framing_id")
    )
    unique_pose_ids = len({candidate.get("pose_family_id") for candidate in batch if candidate.get("pose_family_id")})
    unique_framing_ids = len(
        {candidate.get("camera_framing_id") for candidate in batch if candidate.get("camera_framing_id")}
    )
    batch_size = len(batch)
    seated_count = pose_groups.get("seated", 0)
    lying_count = pose_groups.get("lying", 0)
    standing_count = pose_groups.get("standing", 0)
    seated_or_lying_count = seated_count + lying_count
    target_supported_posture_count = max(2, batch_size // 3)
    mid_framing_count = sum(
        1 for candidate in batch if str(candidate.get("camera_framing_id", "") or "") in {"waist_up", "cowboy_shot"}
    )
    mid_framing_cap = max(2, batch_size // 2)
    score = 0
    score += unique_pose_ids * 2
    score += unique_framing_ids * 2
    score += len({group for group, count in pose_groups.items() if group != "unknown" and count}) * 8
    score += len({group for group, count in framing_groups.items() if group != "unknown" and count}) * 6
    score += min(seated_or_lying_count, target_supported_posture_count) * 8
    if seated_or_lying_count < target_supported_posture_count:
        score -= (target_supported_posture_count - seated_or_lying_count) * 14
    if standing_count > seated_or_lying_count + 2:
        score -= (standing_count - (seated_or_lying_count + 2)) * 8
    if mid_framing_count > mid_framing_cap:
        score -= (mid_framing_count - mid_framing_cap) * 10
    if framing_groups.get("full", 0) == 0:
        score -= 10
    if framing_groups.get("portrait", 0) == 0:
        score -= 6
    return score


def _women_random_outfit_color_diversity_score(batch: list[dict[str, Any]]) -> int:
    if not batch:
        return 0
    outfit_counts = Counter(candidate.get("outfit_family_id") for candidate in batch if candidate.get("outfit_family_id"))
    color_counts = Counter(candidate.get("color_story_id") for candidate in batch if candidate.get("color_story_id"))
    batch_size = len(batch)
    fitted_lane_ids = {"mini_dress", "blazer_mini_dress", "bodysuit_trousers"}
    issue_dominant_color_ids = {
        "clean_neutrals",
        "navy_cream",
        "powder_blue",
        "earthy_soft",
        "chocolate_cream",
        "champagne_taupe",
        "hot_pink",
        "oxblood_noir",
        "rosewood_smoke",
    }
    silhouette_counts = Counter(
        WOMEN_OUTFIT_SILHOUETTE_GROUP_BY_ID.get(str(candidate.get("outfit_family_id", "") or ""), "other")
        for candidate in batch
        if candidate.get("outfit_family_id")
    )
    color_group_counts = Counter(
        WOMEN_RANDOM_COLOR_GROUP_BY_ID.get(str(candidate.get("color_story_id", "") or ""), "other")
        for candidate in batch
        if candidate.get("color_story_id")
    )
    fitted_lane_count = sum(outfit_counts.get(outfit_id, 0) for outfit_id in fitted_lane_ids)
    dominant_color_count = sum(color_counts.get(color_id, 0) for color_id in issue_dominant_color_ids)
    score = 0
    score += len(outfit_counts) * 6
    score += len(color_counts) * 7
    score += len({group for group, count in silhouette_counts.items() if group != "other" and count}) * 7
    score += len({group for group, count in color_group_counts.items() if group != "other" and count}) * 8
    score -= sum(count - 2 for count in outfit_counts.values() if count > 2) * 12
    score -= sum(
        (count - 2) * 10 if color_id in SOFT_REPEAT_COLOR_STORY_IDS else (count - 1) * 28
        for color_id, count in color_counts.items()
        if count > (2 if color_id in SOFT_REPEAT_COLOR_STORY_IDS else 1)
    )
    score -= sum(count - 3 for group, count in silhouette_counts.items() if group != "other" and count > 3) * 8
    score -= sum(count - 3 for group, count in color_group_counts.items() if group != "other" and count > 3) * 12
    fitted_lane_cap = max(2, batch_size // 4)
    if fitted_lane_count > fitted_lane_cap:
        score -= (fitted_lane_count - fitted_lane_cap) * 18
    dominant_color_cap = max(3, round(batch_size * 0.28))
    if dominant_color_count > dominant_color_cap:
        score -= (dominant_color_count - dominant_color_cap) * 20
    dark_cluster_count = color_group_counts.get("cool_dark", 0)
    soft_neutral_count = color_group_counts.get("soft_neutral", 0)
    soft_accent_count = color_group_counts.get("soft_accent", 0)
    dark_cluster_cap = max(3, round(batch_size * 0.18))
    soft_neutral_cap = max(3, round(batch_size * 0.18))
    soft_accent_cap = max(3, round(batch_size * 0.18))
    if dark_cluster_count > dark_cluster_cap:
        score -= (dark_cluster_count - dark_cluster_cap) * 22
    if soft_neutral_count > soft_neutral_cap:
        score -= (soft_neutral_count - soft_neutral_cap) * 22
    if soft_accent_count > soft_accent_cap:
        score -= (soft_accent_count - soft_accent_cap) * 18
    exact_story_cap = 2
    for color_id, count in color_counts.items():
        if color_id in SOFT_REPEAT_COLOR_STORY_IDS:
            continue
        if count > exact_story_cap:
            score -= (count - exact_story_cap) * 36
    if silhouette_counts.get("tailored_trousers", 0) == 0:
        score -= 10
    if silhouette_counts.get("elevated_skirt", 0) == 0 and silhouette_counts.get("longer_day_dress", 0) == 0:
        score -= 8
    return score


def _women_random_pose_mix_score(batch: list[dict[str, Any]]) -> int:
    if not batch:
        return 0
    pose_group_lookup = _pose_group_by_id()
    pose_tags_lookup = _pose_tags_by_id()
    pose_groups = Counter(
        pose_group_lookup.get(str(candidate.get("pose_family_id", "") or ""), "unknown")
        for candidate in batch
        if candidate.get("pose_family_id")
    )
    batch_size = len(batch)
    standing_like = pose_groups.get("standing", 0) + pose_groups.get("movement", 0)
    seated_count = pose_groups.get("seated", 0)
    lowered_count = pose_groups.get("lying", 0) + pose_groups.get("kneeling", 0)
    target_standing = round(batch_size * 0.65)
    target_seated = round(batch_size * 0.20)
    target_lowered = round(batch_size * 0.15)
    passport_like_count = sum(
        1
        for candidate in batch
        if candidate.get("pose_family_id")
        and pose_group_lookup.get(str(candidate.get("pose_family_id", "") or ""), "unknown") in {"standing", "movement"}
        and ({"default_flattering", "modest_safe"} & pose_tags_lookup.get(str(candidate.get("pose_family_id", "") or ""), set()))
    )
    score = 0
    score -= abs(standing_like - target_standing) * 10
    score -= abs(seated_count - target_seated) * 8
    score -= abs(lowered_count - target_lowered) * 8
    score += max(0, 20 - abs(standing_like - target_standing) * 3)
    score += max(0, 12 - abs(seated_count - target_seated) * 3)
    score += max(0, 10 - abs(lowered_count - target_lowered) * 3)
    if standing_like < target_standing:
        score -= (target_standing - standing_like) * 14
    seated_cap = max(4, target_seated + 1)
    if seated_count > seated_cap:
        score -= (seated_count - seated_cap) * 12
    lowered_cap = max(2, target_lowered + 1)
    if lowered_count > lowered_cap:
        score -= (lowered_count - lowered_cap) * 14
    if standing_like <= seated_count + lowered_count:
        score -= 24
    passport_like_cap = max(2, batch_size // 6)
    if passport_like_count > passport_like_cap:
        score -= (passport_like_count - passport_like_cap) * 12
    return score


def _close_up_angle_diversity_score(batch: list[dict[str, Any]]) -> int:
    close_up_candidates = [c for c in batch if str(c.get("camera_framing_id") or "").strip() in _CLOSE_UP_FRAMING_IDS]
    if len(close_up_candidates) < 2:
        return 0
    buckets = [
        _CLOSE_UP_BUCKET_ORDER[
            (candidate["_batch_index"] if candidate.get("_batch_index") is not None else index)
            % len(_CLOSE_UP_BUCKET_ORDER)
        ]
        for index, candidate in enumerate(close_up_candidates)
    ]
    bucket_counts = Counter(buckets)
    n = len(buckets)
    score = len(bucket_counts) * 6
    for count in bucket_counts.values():
        if count > n // 2:
            score -= (count - n // 2) * 8
    return score
