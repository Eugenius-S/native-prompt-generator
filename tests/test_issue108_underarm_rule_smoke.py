from __future__ import annotations

from backend.engine.render import prompt_renderer


def _candidate(**overrides: str) -> dict[str, str]:
    candidate = {
        "beauty_level": "beautified and flattering",
        "age_band": "21 years old",
        "ethnicity": "Polish",
        "body_type": "slim toned body",
        "breast_size": "medium breasts",
        "hair_color": "dark brown hair",
        "hair_structure": "soft loose waves",
        "eye_color": "green eyes",
        "makeup_style": "soft glam makeup",
        "photo_treatment_id": "clean_commercial",
        "capture_style_render": "fashion photo",
        "camera_angle": "slight three quarter view",
        "lighting_render": "soft clean commercial light",
        "time_of_day": "bright afternoon",
        "camera_vibe": "DSLR beauty editorial feel",
        "color_grade": "clean airy commercial color",
        "lens_look": "50mm lens look",
        "finish_render": "natural skin texture",
        "scene_family_id": "urban_daylight",
        "setting_scene": "sunlit rooftop with pale walls and warm sky",
        "mood_energy": "soft flirty energy",
        "line_bank_expression": "playful half smile",
        "outfit_family_id": "column_dress",
        "outfit_family": "fitted ribbed dress",
        "color_story_id": "powder_blue",
        "color_story": "powder blue palette",
        "material": "",
        "pose_family_id": "hands_up_fixing_hair",
        "pose_family": "standing with both hands lifted as if fixing her hair, keeping the shoulders open and the hips softly offset",
        "hand_action": "one hand lightly touching the strap near her collarbone",
        "person_mode": "different_persons",
        "camera_framing_id": "waist_up",
        "camera_framing": "waist-up portrait framing",
    }
    candidate.update(overrides)
    return candidate


def test_issue108_adds_clean_shaven_underarms_for_arms_up_pose() -> None:
    prompt = prompt_renderer.render_candidate_prompt(_candidate())
    assert "clean-shaven underarms" in prompt


def test_issue108_does_not_touch_non_arms_up_pose() -> None:
    prompt = prompt_renderer.render_candidate_prompt(
        _candidate(
            pose_family_id="standing_three_quarter",
            pose_family="standing in a relaxed three quarter angle with one hip popped",
        )
    )
    assert "clean-shaven underarms" not in prompt
