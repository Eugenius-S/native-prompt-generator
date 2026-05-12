from __future__ import annotations

from backend.prompt_service import _merged_form_state, _user_style_profile, generate_run


def test_non_custom_photo_type_resets_manual_treatment_lock() -> None:
    merged = _merged_form_state(
        {
            "mode": "women",
            "photoTypeControl": "glossy",
            "photoTreatmentControl": "mirror_selfie",
        }
    )

    assert merged["photoTypeControl"] == "glossy"
    assert merged["photoTreatmentControl"] == "random"


def test_custom_photo_type_keeps_manual_treatment_lock() -> None:
    merged = _merged_form_state(
        {
            "mode": "women",
            "photoTypeControl": "custom",
            "photoTreatmentControl": "mirror_selfie",
        }
    )

    assert merged["photoTypeControl"] == "custom"
    assert merged["photoTreatmentControl"] == "mirror_selfie"


def test_balanced_photo_type_biases_healthy_default_lane() -> None:
    merged = _merged_form_state(
        {
            "mode": "women",
            "styleMode": "random",
            "photoTypeControl": "balanced",
        }
    )
    profile = _user_style_profile(merged, spicy_level=5)

    assert {"clean_commercial", "direct_light_editorial", "concept_photo_editorial", "advertising_poster_realism"} <= set(profile.get("preferred_photo_treatment_ids", set()))
    assert {"studio_seamless", "direct_flash_night", "analog_35mm", "documentary_still"} <= set(profile.get("deprioritized_photo_treatment_ids", set()))
    assert {"studio", "nightlife_neon"} <= set(profile.get("banned_scene_families", set()))


def test_glossy_photo_type_biases_premium_non_phone_lanes() -> None:
    merged = _merged_form_state(
        {
            "mode": "women",
            "styleMode": "random",
            "photoTypeControl": "glossy",
        }
    )
    profile = _user_style_profile(merged, spicy_level=5)

    assert {"clean_commercial", "direct_light_editorial", "concept_photo_editorial"} <= set(profile.get("preferred_photo_treatment_ids", set()))
    assert {"candid_phone_snapshot", "mirror_selfie", "casual_indoor_selfie"} <= set(profile.get("deprioritized_photo_treatment_ids", set()))
    assert "studio_seamless" in set(profile.get("deprioritized_photo_treatment_ids", set()))
    assert {"creative_gallery", "studio", "nightlife_neon", "wellness_spa"} <= set(profile.get("banned_scene_families", set()))


def test_studio_photo_type_requests_studio_scene_family() -> None:
    merged = _merged_form_state(
        {
            "mode": "women",
            "styleMode": "random",
            "photoTypeControl": "studio",
        }
    )
    profile = _user_style_profile(merged, spicy_level=5)

    assert profile.get("required_scene_families") == {"studio"}
    assert "studio_seamless" in set(profile.get("preferred_photo_treatment_ids", set()))
    assert "clean_commercial" not in set(profile.get("preferred_photo_treatment_ids", set()))
    assert "clean_commercial" in set(profile.get("deprioritized_photo_treatment_ids", set()))


def test_stylized_photo_type_biases_art_direction_lane() -> None:
    merged = _merged_form_state(
        {
            "mode": "women",
            "styleMode": "random",
            "photoTypeControl": "stylized",
        }
    )
    profile = _user_style_profile(merged, spicy_level=5)

    assert {"concept_photo_editorial", "cinematic_poster_realism", "direct_flash_night", "vintage_flash_photo"} <= set(profile.get("preferred_photo_treatment_ids", set()))
    assert {"direct_light_editorial", "studio_seamless", "clean_commercial"} <= set(profile.get("deprioritized_photo_treatment_ids", set()))
    assert {"urban_daylight", "grooming_bath", "wellness_spa"} <= set(profile.get("banned_scene_families", set()))


def test_glossy_photo_type_runtime_stays_inside_curated_treatment_lane() -> None:
    allowed_ids = {
        "clean_commercial",
        "direct_light_editorial",
        "concept_photo_editorial",
        "advertising_poster_realism",
        "cinematic_poster_realism",
        "low_key_dramatic",
    }
    form = _merged_form_state(
        {
            "mode": "women",
            "batchSize": 6,
            "styleMode": "random",
            "photoTypeControl": "glossy",
            "debugMode": "on",
            "antiRepeat": "hard",
            "validationMode": "strict",
        }
    )

    run = generate_run(form)
    treatment_ids = {item["candidate"]["photo_treatment_id"] for item in run["prompts"]}

    assert treatment_ids <= allowed_ids


def test_balanced_photo_type_runtime_avoids_extreme_scene_and_treatment_tails() -> None:
    banned_scene_ids = {"studio", "nightlife_neon"}
    banned_treatment_ids = {"studio_seamless", "direct_flash_night", "mirror_selfie", "casual_indoor_selfie", "candid_phone_snapshot", "disposable_camera", "analog_35mm", "documentary_still", "vintage_flash_photo"}
    for seed in range(4):
        form = _merged_form_state(
            {
                "mode": "women",
                "batchSize": 6,
                "styleMode": "random",
                "photoTypeControl": "balanced",
                "debugMode": "on",
                "antiRepeat": "hard",
                "validationMode": "strict",
                "seed": str(seed),
            }
        )

        run = generate_run(form)
        treatment_ids = {item["candidate"]["photo_treatment_id"] for item in run["prompts"]}
        scene_ids = {item["candidate"]["scene_family_id"] for item in run["prompts"]}

        assert not treatment_ids & banned_treatment_ids
        assert not scene_ids & banned_scene_ids


def test_glossy_photo_type_runtime_avoids_arty_and_studio_scene_tails() -> None:
    banned_scene_ids = {"creative_gallery", "studio", "nightlife_neon", "wellness_spa"}
    for seed in range(4):
        form = _merged_form_state(
            {
                "mode": "women",
                "batchSize": 6,
                "styleMode": "random",
                "photoTypeControl": "glossy",
                "debugMode": "on",
                "antiRepeat": "hard",
                "validationMode": "strict",
                "seed": str(seed),
            }
        )

        run = generate_run(form)
        scene_ids = {item["candidate"]["scene_family_id"] for item in run["prompts"]}

        assert not scene_ids & banned_scene_ids


def test_studio_photo_type_runtime_stays_on_studio_scenes() -> None:
    form = _merged_form_state(
        {
            "mode": "women",
            "batchSize": 6,
            "styleMode": "random",
            "photoTypeControl": "studio",
            "debugMode": "on",
            "antiRepeat": "hard",
            "validationMode": "strict",
        }
    )

    run = generate_run(form)
    scene_ids = {item["candidate"]["scene_family_id"] for item in run["prompts"]}

    assert scene_ids == {"studio"}


def test_stylized_photo_type_runtime_avoids_naturalistic_scene_tails() -> None:
    allowed_ids = {
        "concept_photo_editorial",
        "cinematic_poster_realism",
        "low_key_dramatic",
        "direct_flash_night",
        "vintage_flash_photo",
        "advertising_poster_realism",
    }
    banned_scene_ids = {"urban_daylight", "grooming_bath", "wellness_spa", "courtyard_garden", "garden_conservatory", "coastal_boardwalk", "coastal_pool"}
    for seed in range(4):
        form = _merged_form_state(
            {
                "mode": "women",
                "batchSize": 6,
                "styleMode": "random",
                "photoTypeControl": "stylized",
                "debugMode": "on",
                "antiRepeat": "hard",
                "validationMode": "strict",
                "seed": str(seed),
            }
        )

        run = generate_run(form)
        treatment_ids = {item["candidate"]["photo_treatment_id"] for item in run["prompts"]}
        scene_ids = {item["candidate"]["scene_family_id"] for item in run["prompts"]}

        assert treatment_ids <= allowed_ids
        assert not scene_ids & banned_scene_ids


def test_stylized_photo_type_runtime_keeps_large_random_batches_generatable() -> None:
    for payload in (
        {
            "mode": "women",
            "batchSize": 10,
            "styleMode": "random",
            "photoTypeControl": "stylized",
            "debugMode": "on",
            "antiRepeat": "hard",
            "validationMode": "strict",
            "seed": "101",
        },
        {
            "mode": "couples",
            "batchSize": 10,
            "styleMode": "random",
            "photoTypeControl": "stylized",
            "debugMode": "on",
            "antiRepeat": "hard",
            "validationMode": "strict",
            "seed": "101",
        },
    ):
        run = generate_run(_merged_form_state(payload))
        assert len(run["prompts"]) == 10


def test_amateur_photo_type_runtime_stays_inside_casual_capture_lane() -> None:
    allowed_ids = {
        "candid_phone_snapshot",
        "mirror_selfie",
        "casual_indoor_selfie",
        "disposable_camera",
        "documentary_still",
        "analog_35mm",
        "direct_light_editorial",
    }
    form = _merged_form_state(
        {
            "mode": "women",
            "batchSize": 6,
            "styleMode": "random",
            "photoTypeControl": "amateur",
            "debugMode": "on",
            "antiRepeat": "hard",
            "validationMode": "strict",
        }
    )

    run = generate_run(form)
    treatment_ids = {item["candidate"]["photo_treatment_id"] for item in run["prompts"]}

    assert treatment_ids <= allowed_ids


def test_photo_type_debug_exposes_effective_mode_and_mix_distribution() -> None:
    form = _merged_form_state(
        {
            "mode": "women",
            "batchSize": 6,
            "styleMode": "random",
            "photoTypeControl": "amateur",
            "debugMode": "on",
            "antiRepeat": "hard",
            "validationMode": "strict",
        }
    )

    run = generate_run(form)
    debug = run["debug"]

    assert debug["effectivePhotoType"] == "amateur"
    assert sum(debug["photoTreatmentMixBucketDistribution"].values()) == len(run["prompts"])
    assert sum(debug["photoTreatmentQualityTierDistribution"].values()) == len(run["prompts"])
    assert sum(debug["photoTreatmentToneDistribution"].values()) == len(run["prompts"])
