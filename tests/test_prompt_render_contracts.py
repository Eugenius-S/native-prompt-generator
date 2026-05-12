from __future__ import annotations

from backend.engine.render import prompt_renderer


def _candidate(**overrides: str) -> dict[str, str]:
    candidate = {
        "beauty_level": "beautified with polished glam appeal",
        "age_band": "20 years old",
        "ethnicity": "Polish",
        "body_type": "slim toned body",
        "breast_size": "medium breasts",
        "hair_color": "medium brown hair",
        "hair_structure": "soft loose waves",
        "eye_color": "gray eyes",
        "makeup_style": "night out glam makeup",
        "photo_treatment_id": "studio_seamless",
        "capture_style_render": "fashion photo",
        "camera_angle": "eye level angle",
        "lighting_render": "hard direct light with crisp shadow edges",
        "time_of_day": "golden hour",
        "camera_vibe": "fashion campaign camera feel",
        "color_grade": "high-contrast fashion color",
        "lens_look": "35mm lens look",
        "finish_render": "natural skin texture with crisp contrast",
        "scene_family_id": "studio",
        "setting_scene": "school portrait setup with blue muslin backdrop, stool and direct flash feel",
        "line_bank_location": "school portrait setup with blue muslin backdrop, stool and direct flash feel",
        "mood_energy": "soft flirty energy",
        "line_bank_expression": "hungry stare, chin slightly down, direct eye contact",
        "outfit_family_id": "mini_dress",
        "outfit_family": "side laced dress",
        "color_story_id": "clean_neutrals",
        "color_story": "clean neutrals palette",
        "material": "",
        "pose_family": "upper-body pose with a slight torso angle",
        "hand_action": "one hand lightly touching the strap near her collarbone",
        "person_mode": "different_persons",
        "camera_framing_id": "waist_up",
        "camera_framing": "waist-up portrait framing",
    }
    candidate.update(overrides)
    return candidate


def test_render_candidate_prompt_uses_clean_seamless_studio_contract() -> None:
    prompt = prompt_renderer.render_candidate_prompt(_candidate())

    assert "school portrait setup" not in prompt
    assert "stool" not in prompt
    assert "blue muslin backdrop" not in prompt
    assert "clean seamless backdrop" in prompt


def test_render_candidate_prompt_blocks_night_plus_daylight_combo() -> None:
    prompt = prompt_renderer.render_candidate_prompt(
        _candidate(
            photo_treatment_id="clean_commercial",
            scene_family_id="urban_daylight",
            lighting_render="soft clean commercial light",
            time_of_day="night",
            line_bank_location="fish market edge with wet stone floor, metal tables and cold daylight",
            setting_scene="fish market edge with wet stone floor, metal tables and cold daylight",
        )
    )

    assert "night, DSLR beauty editorial feel" not in prompt
    assert "bright afternoon" in prompt


def test_render_candidate_prompt_drops_cheap_location_tail_for_hospitality_suite() -> None:
    prompt = prompt_renderer.render_candidate_prompt(
        _candidate(
            photo_treatment_id="concept_photo_editorial",
            scene_family_id="hospitality_suite",
            line_bank_location="record store corner with poster wall and narrow aisle",
            setting_scene="luxury suite with lacquered wood, marble vanity and city glow",
        )
    )

    assert "record store corner" not in prompt
    assert "luxury suite with lacquered wood" in prompt


def test_render_candidate_prompt_normalizes_dark_lane_out_of_bright_afternoon() -> None:
    prompt = prompt_renderer.render_candidate_prompt(
        _candidate(
            photo_treatment_id="low_key_dramatic",
            scene_family_id="nightlife_bar",
            line_bank_location="private cocktail booth with dim amber spill and velvet seating",
            setting_scene="private cocktail booth with dim amber spill and velvet seating",
            lighting_render="low-key dramatic light with strong shadow falloff",
            time_of_day="bright afternoon",
        )
    )

    assert "bright afternoon" not in prompt
    assert "night" in prompt
