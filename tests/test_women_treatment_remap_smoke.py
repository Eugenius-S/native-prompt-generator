from backend import prompt_service
from backend.photo_treatment_mix import photo_treatment_mix_bucket, photo_treatment_quality_tier, photo_treatment_tone
from backend.services.debug_summary import _photo_treatment_lookup
from backend.services import postprocess, scoring


def _base_candidate(scene_family_id: str, outfit_family_id: str, color_story_id: str) -> dict[str, str]:
    return {
        "scene_family_id": scene_family_id,
        "setting_scene_id": "test_setting",
        "camera_framing_id": "waist_up",
        "lighting_family_id": "clean_daylight",
        "outfit_family_id": outfit_family_id,
        "color_story_id": color_story_id,
        "age_band": "22 years old",
        "photo_treatment_id": "clean_commercial",
        "photo_treatment": "Clean commercial",
        "photo_treatment_category": "polished",
        "capture_style_render": "clean commercial fashion photo",
        "lighting_render": "soft clean commercial light",
        "finish_render": "natural skin texture",
    }


class _AlwaysRemapRandom:
    def __init__(self, *_args, **_kwargs):
        pass

    def random(self) -> float:
        return 0.0


def test_women_fitness_wellness_spa_remap_finds_stylized_option():
    candidate = _base_candidate("wellness_spa", "polo_pleated_skirt", "sport_clean_white")
    remapped = prompt_service._remap_women_fitness_treatment(candidate)

    assert remapped["photo_treatment_id"] in {"candid_phone_snapshot", "analog_35mm", "documentary_still"}
    assert remapped["photo_treatment_id"] != "clean_commercial"


def test_women_nightlife_remap_replaces_clean_commercial():
    candidate = _base_candidate("nightlife_bar", "cami_midi_skirt", "black_gold")
    remapped = prompt_service._remap_women_nightlife_treatment(candidate)

    assert remapped["photo_treatment_id"] in {
        "vintage_flash_photo",
        "direct_flash_night",
        "cinematic_poster_realism",
        "low_key_dramatic",
        "disposable_camera",
    }


def test_women_luxury_remap_replaces_clean_commercial():
    candidate = _base_candidate("residential_luxury", "column_dress", "champagne_taupe")
    remapped = prompt_service._remap_women_luxury_treatment(candidate)

    assert remapped["photo_treatment_id"] in {
        "direct_light_editorial",
        "analog_35mm",
        "cinematic_poster_realism",
        "concept_photo_editorial",
        "low_key_dramatic",
    }


def test_women_romantic_coastal_remap_replaces_clean_commercial():
    candidate = _base_candidate("coastal_pool", "wrap_blouse_skirt", "powder_blue")
    remapped = prompt_service._remap_women_romantic_treatment(candidate)

    assert remapped["photo_treatment_id"] in {"analog_35mm", "direct_light_editorial", "cinematic_poster_realism", "advertising_poster_realism"}


def test_women_random_constraints_remap_clean_commercial(monkeypatch):
    monkeypatch.setattr(postprocess.random, "Random", _AlwaysRemapRandom)
    candidate = _base_candidate("residential_luxury", "column_dress", "champagne_taupe")
    form_state = dict(prompt_service.DEFAULT_FORM_STATE)
    form_state.update({"mode": "women", "styleMode": "random"})

    remapped = prompt_service._apply_prompt_constraints(candidate, form_state, spicy_level=4)

    assert remapped["photo_treatment_id"] in {
        "direct_light_editorial",
        "cinematic_poster_realism",
        "analog_35mm",
        "concept_photo_editorial",
    }
    assert remapped["photo_treatment_id"] != "clean_commercial"


def test_photo_treatment_taxonomy_separates_low_end_and_premium_lanes():
    assert photo_treatment_quality_tier("documentary_still", "stylized") == "raw_low_end"
    assert photo_treatment_tone("documentary_still", "stylized") == "documentary"
    assert photo_treatment_mix_bucket("documentary_still", "stylized") == "casual_low_end"
    assert photo_treatment_quality_tier("direct_light_editorial", "stylized") == "premium"
    assert photo_treatment_tone("direct_light_editorial", "stylized") == "editorial"
    assert photo_treatment_mix_bucket("direct_light_editorial", "stylized") == "polished_glam"
    assert photo_treatment_mix_bucket("analog_35mm", "stylized") == "editorial_non_phone"


def test_low_end_treatment_wording_avoids_explicit_cheap_language():
    lookup = _photo_treatment_lookup()
    cheapest_tokens = {
        "soft available light",
        "ordinary available light",
        "cheap-flash snapshot feel",
        "unpolished realism",
    }

    for treatment_id in {"analog_35mm", "documentary_still", "disposable_camera"}:
        profile = lookup[treatment_id]
        rendered_text = " | ".join(
            [
                str(profile.get("lighting_render", "")),
                str(profile.get("camera_vibe", "")),
                str(profile.get("color_grade", "")),
                str(profile.get("finish", "")),
            ]
        ).lower()
        for token in cheapest_tokens:
            assert token not in rendered_text


def test_women_random_batch_score_prefers_target_mix_over_low_end_heavy_batch():
    target_batch = [
        {"photo_treatment_id": "clean_commercial", "photo_treatment_category": "polished", "lighting_family_id": "clean_daylight"},
        {"photo_treatment_id": "direct_light_editorial", "photo_treatment_category": "stylized", "lighting_family_id": "hard_direct_light"},
        {"photo_treatment_id": "concept_photo_editorial", "photo_treatment_category": "stylized", "lighting_family_id": "studio_rim"},
        {"photo_treatment_id": "cinematic_poster_realism", "photo_treatment_category": "stylized", "lighting_family_id": "warm_interior"},
        {"photo_treatment_id": "advertising_poster_realism", "photo_treatment_category": "stylized", "lighting_family_id": "tight_spotlight"},
        {"photo_treatment_id": "studio_seamless", "photo_treatment_category": "stylized", "lighting_family_id": "single_source_contrast"},
        {"photo_treatment_id": "analog_35mm", "photo_treatment_category": "stylized", "lighting_family_id": "soft_overcast"},
        {"photo_treatment_id": "documentary_still", "photo_treatment_category": "stylized", "lighting_family_id": "practical_lamp"},
        {"photo_treatment_id": "low_key_dramatic", "photo_treatment_category": "stylized", "lighting_family_id": "moody_darkness"},
        {"photo_treatment_id": "candid_phone_snapshot", "photo_treatment_category": "stylized", "lighting_family_id": "clean_daylight"},
    ]
    low_end_heavy_batch = [
        {"photo_treatment_id": "candid_phone_snapshot", "photo_treatment_category": "stylized", "lighting_family_id": "clean_daylight"},
        {"photo_treatment_id": "mirror_selfie", "photo_treatment_category": "stylized", "lighting_family_id": "warm_interior"},
        {"photo_treatment_id": "casual_indoor_selfie", "photo_treatment_category": "stylized", "lighting_family_id": "practical_lamp"},
        {"photo_treatment_id": "documentary_still", "photo_treatment_category": "stylized", "lighting_family_id": "practical_lamp"},
        {"photo_treatment_id": "disposable_camera", "photo_treatment_category": "stylized", "lighting_family_id": "clean_daylight"},
        {"photo_treatment_id": "documentary_still", "photo_treatment_category": "stylized", "lighting_family_id": "soft_overcast"},
        {"photo_treatment_id": "disposable_camera", "photo_treatment_category": "stylized", "lighting_family_id": "warm_interior"},
        {"photo_treatment_id": "candid_phone_snapshot", "photo_treatment_category": "stylized", "lighting_family_id": "soft_overcast"},
        {"photo_treatment_id": "mirror_selfie", "photo_treatment_category": "stylized", "lighting_family_id": "clean_daylight"},
        {"photo_treatment_id": "clean_commercial", "photo_treatment_category": "polished", "lighting_family_id": "clean_daylight"},
        {"photo_treatment_id": "analog_35mm", "photo_treatment_category": "stylized", "lighting_family_id": "soft_overcast"},
    ]

    assert [photo_treatment_mix_bucket(item["photo_treatment_id"], item["photo_treatment_category"]) for item in target_batch].count("phone_snapshot") == 1
    assert [photo_treatment_mix_bucket(item["photo_treatment_id"], item["photo_treatment_category"]) for item in target_batch].count("casual_low_end") == 1
    assert scoring._photo_treatment_batch_score(target_batch, "random", mode="women") > scoring._photo_treatment_batch_score(low_end_heavy_batch, "random", mode="women")


def test_men_luxury_constraints_remap_clean_commercial(monkeypatch):
    monkeypatch.setattr(postprocess.random, "Random", _AlwaysRemapRandom)
    candidate = _base_candidate("residential_luxury", "male_open_collar_trousers", "champagne_taupe")
    form_state = dict(prompt_service.DEFAULT_FORM_STATE)
    form_state.update({"mode": "men", "styleMode": "luxury"})

    remapped = prompt_service._apply_prompt_constraints(candidate, form_state, spicy_level=4)

    assert remapped["photo_treatment_id"] in {
        "direct_light_editorial",
        "analog_35mm",
        "cinematic_poster_realism",
        "low_key_dramatic",
        "direct_flash_night",
    }
    assert remapped["photo_treatment_id"] != "clean_commercial"


def test_men_luxury_batch_score_rewards_lighting_variety():
    base = {
        "photo_treatment_category": "stylized",
        "photo_treatment_id": "direct_light_editorial",
    }
    flat_batch = [
        {**base, "lighting_family_id": "clean_daylight"},
        {**base, "photo_treatment_id": "analog_35mm", "lighting_family_id": "clean_daylight"},
        {**base, "photo_treatment_id": "low_key_dramatic", "lighting_family_id": "clean_daylight"},
    ]
    varied_batch = [
        {**base, "lighting_family_id": "hard_direct_light"},
        {**base, "photo_treatment_id": "analog_35mm", "lighting_family_id": "warm_interior"},
        {**base, "photo_treatment_id": "low_key_dramatic", "lighting_family_id": "moody_darkness"},
    ]

    assert scoring._photo_treatment_batch_score(varied_batch, "luxury", mode="men") > scoring._photo_treatment_batch_score(flat_batch, "luxury", mode="men")


def test_muted_color_clone_penalty_hits_repeated_neutral_batches():
    muted_heavy_batch = [
        {"color_story_id": "clean_neutrals"},
        {"color_story_id": "clean_neutrals"},
        {"color_story_id": "clean_neutrals"},
        {"color_story_id": "champagne_taupe"},
        {"color_story_id": "champagne_taupe"},
        {"color_story_id": "rosewood_smoke"},
    ]
    diverse_batch = [
        {"color_story_id": "clean_neutrals"},
        {"color_story_id": "powder_blue"},
        {"color_story_id": "navy_cream"},
        {"color_story_id": "earthy_soft"},
        {"color_story_id": "hot_pink"},
        {"color_story_id": "black_gold"},
    ]

    assert scoring._muted_color_clone_penalty(muted_heavy_batch, "random", "women") < 0
    assert scoring._muted_color_clone_penalty(diverse_batch, "random", "women") == 0
    assert scoring._muted_color_clone_penalty(muted_heavy_batch, "random", "men") == 0


def test_outfit_silhouette_clone_penalty_hits_same_look_in_different_colors():
    repeated_silhouette_batch = [
        {"outfit_family_id": "column_dress", "material_id": "soft_jersey", "color_story_id": "clean_neutrals"},
        {"outfit_family_id": "column_dress", "material_id": "soft_jersey", "color_story_id": "powder_blue"},
        {"outfit_family_id": "column_dress", "material_id": "soft_jersey", "color_story_id": "hot_pink"},
        {"outfit_family_id": "wrap_blouse_skirt", "material_id": "crepe", "color_story_id": "navy_cream"},
    ]
    varied_silhouette_batch = [
        {"outfit_family_id": "column_dress", "material_id": "soft_jersey", "color_story_id": "clean_neutrals"},
        {"outfit_family_id": "wrap_blouse_skirt", "material_id": "crepe", "color_story_id": "powder_blue"},
        {"outfit_family_id": "halter_trousers", "material_id": "satin", "color_story_id": "hot_pink"},
        {"outfit_family_id": "structured_day_dress", "material_id": "woven", "color_story_id": "navy_cream"},
    ]

    assert scoring._outfit_silhouette_clone_penalty(repeated_silhouette_batch, "random", "women") < 0
    assert scoring._outfit_silhouette_clone_penalty(varied_silhouette_batch, "random", "women") == 0
    assert scoring._outfit_silhouette_clone_penalty(repeated_silhouette_batch, "random", "men") == 0


def test_scene_outfit_clone_penalty_hits_same_look_in_same_scene_family():
    repeated_scene_outfit_batch = [
        {"scene_family_id": "residential_luxury", "outfit_family_id": "column_dress", "color_story_id": "clean_neutrals"},
        {"scene_family_id": "residential_luxury", "outfit_family_id": "column_dress", "color_story_id": "powder_blue"},
        {"scene_family_id": "residential_luxury", "outfit_family_id": "column_dress", "color_story_id": "hot_pink"},
        {"scene_family_id": "urban_daylight", "outfit_family_id": "wrap_blouse_skirt", "color_story_id": "navy_cream"},
    ]
    varied_scene_outfit_batch = [
        {"scene_family_id": "residential_luxury", "outfit_family_id": "column_dress", "color_story_id": "clean_neutrals"},
        {"scene_family_id": "residential_luxury", "outfit_family_id": "wrap_blouse_skirt", "color_story_id": "powder_blue"},
        {"scene_family_id": "urban_daylight", "outfit_family_id": "column_dress", "color_story_id": "hot_pink"},
        {"scene_family_id": "urban_daylight", "outfit_family_id": "wrap_blouse_skirt", "color_story_id": "navy_cream"},
    ]

    assert scoring._scene_outfit_clone_penalty(repeated_scene_outfit_batch, "random", "women") < 0
    assert scoring._scene_outfit_clone_penalty(varied_scene_outfit_batch, "random", "women") == 0
    assert scoring._scene_outfit_clone_penalty(repeated_scene_outfit_batch, "random", "men") == 0


def test_treatment_outfit_clone_penalty_hits_same_look_in_same_treatment():
    repeated_treatment_outfit_batch = [
        {"photo_treatment_id": "mirror_selfie", "outfit_family_id": "column_dress", "color_story_id": "clean_neutrals"},
        {"photo_treatment_id": "mirror_selfie", "outfit_family_id": "column_dress", "color_story_id": "powder_blue"},
        {"photo_treatment_id": "mirror_selfie", "outfit_family_id": "column_dress", "color_story_id": "hot_pink"},
        {"photo_treatment_id": "analog_35mm", "outfit_family_id": "wrap_blouse_skirt", "color_story_id": "navy_cream"},
    ]
    varied_treatment_outfit_batch = [
        {"photo_treatment_id": "mirror_selfie", "outfit_family_id": "column_dress", "color_story_id": "clean_neutrals"},
        {"photo_treatment_id": "mirror_selfie", "outfit_family_id": "wrap_blouse_skirt", "color_story_id": "powder_blue"},
        {"photo_treatment_id": "analog_35mm", "outfit_family_id": "column_dress", "color_story_id": "hot_pink"},
        {"photo_treatment_id": "analog_35mm", "outfit_family_id": "wrap_blouse_skirt", "color_story_id": "navy_cream"},
    ]

    assert scoring._treatment_outfit_clone_penalty(repeated_treatment_outfit_batch, "random", "women") < 0
    assert scoring._treatment_outfit_clone_penalty(varied_treatment_outfit_batch, "random", "women") == 0
    assert scoring._treatment_outfit_clone_penalty(repeated_treatment_outfit_batch, "random", "men") == 0


def test_cheap_contract_fallback_penalty_hits_flat_premium_scene_mix():
    cheap_batch = [
        {"scene_family_id": "garden_conservatory", "photo_treatment_id": "clean_commercial", "lighting_family_id": "clean_daylight"},
        {"scene_family_id": "hospitality_suite", "photo_treatment_id": "clean_commercial", "lighting_family_id": "warm_interior"},
        {"scene_family_id": "residential_luxury", "photo_treatment_id": "casual_indoor_selfie", "lighting_family_id": "soft_overcast"},
    ]
    healthy_batch = [
        {"scene_family_id": "garden_conservatory", "photo_treatment_id": "direct_light_editorial", "lighting_family_id": "hard_direct_light"},
        {"scene_family_id": "hospitality_suite", "photo_treatment_id": "concept_photo_editorial", "lighting_family_id": "tight_spotlight"},
        {"scene_family_id": "residential_luxury", "photo_treatment_id": "cinematic_poster_realism", "lighting_family_id": "warm_interior"},
    ]

    assert scoring._cheap_contract_fallback_penalty(cheap_batch, "random", "women") < 0
    assert scoring._cheap_contract_fallback_penalty(healthy_batch, "random", "women") == 0
    assert scoring._cheap_contract_fallback_penalty(cheap_batch, "sport", "women") == 0


def test_women_romantic_profile_bans_cardigan_skirt_and_prefers_refined_options():
    form_state = dict(prompt_service.DEFAULT_FORM_STATE)
    form_state.update({"mode": "women", "styleMode": "romantic"})

    profile = prompt_service._user_style_profile(form_state, spicy_level=3)

    assert "cardigan_skirt" in profile["banned_outfit_ids"]
    assert {"silk_blouse_midi_skirt", "structured_day_dress", "mockneck_knit_skirt"} <= profile["preferred_outfit_ids"]
