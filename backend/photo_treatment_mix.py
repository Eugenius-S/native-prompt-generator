from __future__ import annotations

TREATMENT_QUALITY_TIER_BY_ID = {
    "clean_commercial": "clean",
    "candid_phone_snapshot": "casual",
    "analog_35mm": "neutral",
    "low_key_dramatic": "premium",
    "direct_flash_night": "premium",
    "studio_seamless": "premium",
    "cinematic_poster_realism": "premium",
    "concept_photo_editorial": "premium",
    "direct_light_editorial": "premium",
    "mirror_selfie": "casual",
    "disposable_camera": "raw_low_end",
    "documentary_still": "raw_low_end",
    "casual_indoor_selfie": "casual",
    "vintage_flash_photo": "neutral",
    "advertising_poster_realism": "premium",
}

TREATMENT_TONE_BY_ID = {
    "clean_commercial": "beauty",
    "candid_phone_snapshot": "phone",
    "analog_35mm": "filmic",
    "low_key_dramatic": "dramatic",
    "direct_flash_night": "retro_flash",
    "studio_seamless": "beauty",
    "cinematic_poster_realism": "cinematic",
    "concept_photo_editorial": "editorial",
    "direct_light_editorial": "editorial",
    "mirror_selfie": "phone",
    "disposable_camera": "snapshot",
    "documentary_still": "documentary",
    "casual_indoor_selfie": "phone",
    "vintage_flash_photo": "retro_flash",
    "advertising_poster_realism": "beauty",
}

WOMEN_RANDOM_TREATMENT_MIX_TARGETS = {
    "phone_snapshot": 8.0,
    "casual_low_end": 8.0,
    "editorial_non_phone": 24.0,
    "polished_glam": 60.0,
}


def photo_treatment_quality_tier(treatment_id: str, category: str = "") -> str:
    normalized_id = str(treatment_id or "").strip().lower()
    normalized_category = str(category or "").strip().lower()
    if normalized_id in TREATMENT_QUALITY_TIER_BY_ID:
        return TREATMENT_QUALITY_TIER_BY_ID[normalized_id]
    if normalized_category == "polished":
        return "clean"
    return "neutral"


def photo_treatment_tone(treatment_id: str, category: str = "") -> str:
    normalized_id = str(treatment_id or "").strip().lower()
    normalized_category = str(category or "").strip().lower()
    if normalized_id in TREATMENT_TONE_BY_ID:
        return TREATMENT_TONE_BY_ID[normalized_id]
    if normalized_category == "polished":
        return "beauty"
    return "editorial"


def photo_treatment_mix_bucket(treatment_id: str, category: str = "") -> str:
    quality_tier = photo_treatment_quality_tier(treatment_id, category)
    tone = photo_treatment_tone(treatment_id, category)
    if tone == "phone":
        return "phone_snapshot"
    if quality_tier in {"raw_low_end", "casual"}:
        return "casual_low_end"
    if quality_tier in {"premium", "clean"} or tone in {"beauty", "editorial", "cinematic", "dramatic"}:
        return "polished_glam"
    return "editorial_non_phone"
