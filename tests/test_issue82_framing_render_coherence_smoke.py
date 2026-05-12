from __future__ import annotations

from backend.engine.render import prompt_renderer


def _candidate(**overrides: str) -> dict[str, str]:
    candidate = {
        "beauty_level": "beautified and flattering",
        "age_band": "25 years old",
        "ethnicity": "Chinese",
        "body_type": "slim body",
        "breast_size": "medium breasts",
        "hair_color": "medium brown hair",
        "hair_structure": "loose side braid",
        "eye_color": "green eyes",
        "makeup_style": "night out glam makeup",
        "photo_treatment_id": "clean_commercial",
        "capture_style_render": "fashion photo",
        "camera_angle": "slight three quarter view",
        "lighting_render": "soft clean commercial light",
        "time_of_day": "night",
        "camera_vibe": "DSLR beauty editorial feel",
        "color_grade": "clean airy commercial color",
        "lens_look": "50mm lens look",
        "finish_render": "natural skin texture",
        "scene_family_id": "urban_daylight",
        "setting_scene": "dusty highway shoulder with road sign, dry grass and low golden sun",
        "mood_energy": "bratty playful energy",
        "line_bank_expression": "intense teasing look, chin lowered",
        "outfit_family_id": "halter_top_mini_skirt",
        "outfit_family": "satin halter top with a low rise micro skirt",
        "color_story_id": "slate_blue_ink",
        "color_story": "slate blue and ink palette",
        "material": "",
        "pose_family": "leaning on the counter with her hips angled back",
        "hand_action": "one hand resting low along her thigh",
        "person_mode": "different_persons",
        "camera_framing_id": "close_portrait",
        "camera_framing": "close portrait framing",
    }
    candidate.update(overrides)
    return candidate


def test_portrait_prompt_drops_lower_body_outfit_and_pose_conflicts() -> None:
    prompt = prompt_renderer.render_candidate_prompt(_candidate())

    assert prompt.startswith("Tight close-up fashion photo")
    assert "micro skirt" not in prompt
    assert "thigh" not in prompt
    assert "hips angled back" not in prompt


def test_tight_portrait_keeps_upper_visible_outfit_and_safe_pose_detail() -> None:
    prompt = prompt_renderer.render_candidate_prompt(
        _candidate(
            outfit_family="open cardigan over a lace trim camisole",
            hand_action="one hand lightly touching the strap near her collarbone",
            camera_framing_id="head_and_shoulders",
            camera_framing="head and shoulders portrait framing",
        )
    )

    assert "cardigan over a lace trim camisole" in prompt
    assert "collarbone" in prompt
    assert "thigh" not in prompt


def test_portrait_prompt_drops_lower_body_outfit_after_and_separator() -> None:
    prompt = prompt_renderer.render_candidate_prompt(
        _candidate(
            outfit_family="oversized blazer over a fitted top and mini skirt",
            camera_framing_id="waist_up",
            camera_framing="waist-up portrait framing",
        )
    )

    assert "mini skirt" not in prompt
    assert "oversized blazer over a fitted top" in prompt


def test_portrait_prompt_sanitizes_one_piece_mini_dress_wording() -> None:
    prompt = prompt_renderer.render_candidate_prompt(
        _candidate(
            outfit_family="fitted beach mini dress",
            line_bank_outfit="leather mini dress with a deep neckline",
            camera_framing_id="waist_up",
            camera_framing="waist-up portrait framing",
        )
    )

    assert "mini dress" not in prompt
    assert "leather dress" in prompt


def test_portrait_prompt_drops_comma_split_lower_body_outfit_tail() -> None:
    prompt = prompt_renderer.render_candidate_prompt(
        _candidate(
            line_bank_outfit="tight-fitting silk blouse, a latex mini skirt and fishnet tights",
            camera_framing_id="close_portrait",
            camera_framing="tight close-up portrait framing",
        )
    )

    assert "mini skirt" not in prompt
    assert "fishnet" not in prompt
    assert "silk blouse" in prompt


def test_portrait_prompt_drops_waistband_hand_action() -> None:
    prompt = prompt_renderer.render_candidate_prompt(
        _candidate(
            hand_action="one hand hooked lightly at the waistband",
            camera_framing_id="bust_up",
            camera_framing="bust-up portrait framing",
        )
    )

    assert "waistband" not in prompt


def test_full_body_prompt_keeps_lower_body_outfit_and_pose_detail() -> None:
    prompt = prompt_renderer.render_candidate_prompt(_candidate(camera_framing_id="full_body", camera_framing="full body framing"))

    assert "micro skirt" in prompt
    assert "thigh" in prompt
    assert "hips angled back" in prompt
    assert "true full-length standing shot" in prompt
    assert "whole standing figure visible in frame" in prompt
    assert "headroom" not in prompt


def test_ankle_up_prompt_adds_explicit_full_figure_clause() -> None:
    prompt = prompt_renderer.render_candidate_prompt(
        _candidate(camera_framing_id="ankle_up", camera_framing="ankle-up full figure framing")
    )

    assert "true full-length" in prompt
    assert "centered as a full-height composition" in prompt
    assert "framing lands near the ankles" in prompt
    assert "headroom" not in prompt


def test_head_and_shoulders_prompt_keeps_safe_headroom_language() -> None:
    prompt = prompt_renderer.render_candidate_prompt(
        _candidate(
            camera_framing_id="head_and_shoulders",
            camera_framing="head and shoulders portrait framing",
            hand_action="one hand lightly touching the strap near her collarbone",
        )
    )

    assert "breathing room above the head" in prompt
    assert "cropped above the chest" in prompt
    assert "no top-of-head crop" in prompt
    assert "collarbone" in prompt


def test_close_portrait_prompt_explicitly_blocks_top_crop() -> None:
    prompt = prompt_renderer.render_candidate_prompt(_candidate())

    assert "upper chest" in prompt
    assert "no top-of-head crop" in prompt


def test_face_only_prompt_drops_body_and_outfit_noise() -> None:
    prompt = prompt_renderer.render_candidate_prompt(
        _candidate(
            camera_framing_id="face_only",
            camera_framing="face-only portrait framing",
            outfit_family="open cardigan over a fitted camisole",
            line_bank_outfit="open cardigan over a fitted camisole",
            hand_action="one hand lightly touching the strap near her collarbone",
        )
    )

    assert prompt.startswith("Face close-up fashion photo")
    assert "medium breasts" not in prompt
    assert "slim body" not in prompt
    assert "Wearing" not in prompt
    assert "shoulders angled" not in prompt
    assert "tight beauty headshot" in prompt
    assert "hint of neck or upper shoulders visible" in prompt
    assert "no ultra-tight face-only crop" in prompt
