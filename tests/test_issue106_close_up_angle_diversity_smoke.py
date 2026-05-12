"""Smoke tests for close-up angle bucket diversity (issue #106).

Checks:
- face_only prompts use angle bucket language, not "only the face visible" (anti-regression)
- Rendering with different _batch_index values produces different angle buckets
- A synthetic batch of close-up candidates covers multiple angle buckets
- The scoring helper rewards bucket diversity correctly
"""
from __future__ import annotations

from backend.engine.render import prompt_renderer
from backend.services.scoring import _close_up_angle_diversity_score

_CLOSE_UP_BUCKET_MARKERS = (
    # front
    "facing forward",
    "straight-on",
    "eyes locked directly into camera",
    # three_quarter
    "three-quarter",
    "off-axis",
    "one ear drawn back",
    # profile
    "side-profile",
    "turned close to profile",
    # chin_up
    "chin-up",
    "chin gently lifted",
    "chin slightly raised",
    # chin_down
    "chin-down",
    "chin slightly lowered",
    "head tipped softly down",
    # strong_turn
    "strong turn",
    "strong-turn",
    "turned sharply off-axis",
)


def _face_only_candidate(batch_index: int | None = None, **overrides: object) -> dict:
    c: dict = {
        "beauty_level": "beautified",
        "age_band": "25 years old",
        "ethnicity": "Chinese",
        "body_type": "slim body",
        "breast_size": "medium breasts",
        "hair_color": "dark brown hair",
        "hair_structure": "loose waves",
        "eye_color": "brown eyes",
        "makeup_style": "soft glam makeup",
        "photo_treatment_id": "clean_commercial",
        "capture_style_render": "beauty photo",
        "camera_angle": "eye level",
        "lighting_render": "soft studio light",
        "time_of_day": "day",
        "camera_vibe": "DSLR beauty editorial feel",
        "color_grade": "clean natural color",
        "lens_look": "85mm lens look",
        "finish_render": "natural skin texture",
        "scene_family_id": "studio_neutral",
        "setting_scene": "plain light studio backdrop",
        "mood_energy": "calm confident energy",
        "line_bank_expression": "relaxed direct gaze",
        "outfit_family_id": "cami_midi_skirt",
        "outfit_family": "silk cami with a midi skirt",
        "color_story_id": "clean_neutrals",
        "color_story": "clean neutral palette",
        "material": "",
        "pose_family": "standing relaxed",
        "hand_action": "",
        "person_mode": "different_persons",
        "camera_framing_id": "face_only",
        "camera_framing": "face-only portrait framing",
    }
    if batch_index is not None:
        c["_batch_index"] = batch_index
    c.update(overrides)
    return c


def test_face_only_no_extreme_crop_language() -> None:
    """Anti-regression: face_only should not produce 'only the face visible'."""
    for i in range(4):
        prompt = prompt_renderer.render_candidate_prompt(_face_only_candidate(batch_index=i))
        assert "only the face visible" not in prompt, f"batch_index={i}: got 'only the face visible'"


def test_face_only_prompt_contains_tight_beauty_headshot() -> None:
    for i in range(4):
        prompt = prompt_renderer.render_candidate_prompt(_face_only_candidate(batch_index=i))
        assert "tight beauty headshot" in prompt, f"batch_index={i}: missing 'tight beauty headshot'"


def test_face_only_prompt_contains_angle_bucket_language() -> None:
    """Each face_only prompt with a known batch_index must contain one of the expected bucket markers."""
    for i in range(4):
        prompt = prompt_renderer.render_candidate_prompt(_face_only_candidate(batch_index=i))
        found = any(marker in prompt for marker in _CLOSE_UP_BUCKET_MARKERS)
        assert found, f"batch_index={i}: no angle bucket marker found in: {prompt[:200]}"


def test_face_only_six_prompts_cover_all_buckets() -> None:
    """With 6 sequential batch_index values, each explicit close-up bucket should appear once."""
    prompts = [prompt_renderer.render_candidate_prompt(_face_only_candidate(batch_index=i)) for i in range(6)]

    # each bucket has a distinct set of primary markers
    bucket_front_markers = ("facing forward", "straight-on", "eyes locked directly into camera")
    bucket_three_q_markers = ("three-quarter", "off-axis", "one ear drawn back")
    bucket_profile_markers = ("side-profile", "turned close to profile")
    bucket_chin_up_markers = ("chin-up", "chin gently lifted", "chin slightly raised")
    bucket_chin_down_markers = ("chin-down", "chin slightly lowered", "head tipped softly down")
    bucket_strong_turn_markers = ("strong turn", "strong-turn", "turned sharply off-axis")

    def detect_bucket(p: str) -> str:
        if any(m in p for m in bucket_strong_turn_markers):
            return "strong_turn"
        if any(m in p for m in bucket_chin_down_markers):
            return "chin_down"
        if any(m in p for m in bucket_chin_up_markers):
            return "chin_up"
        if any(m in p for m in bucket_profile_markers):
            return "profile"
        if any(m in p for m in bucket_three_q_markers):
            return "three_quarter"
        if any(m in p for m in bucket_front_markers):
            return "front"
        return "unknown"

    detected = [detect_bucket(p) for p in prompts]
    unique_buckets = set(detected)
    assert unique_buckets == {"front", "three_quarter", "profile", "chin_up", "chin_down", "strong_turn"}, (
        f"Expected all 6 close-up buckets in 6 sequential prompts, got: {detected}"
    )


def test_face_only_twelve_prompts_repeat_all_buckets() -> None:
    """With 12 sequential prompts, all buckets should repeat cleanly across two cycles."""
    prompts = [prompt_renderer.render_candidate_prompt(_face_only_candidate(batch_index=i)) for i in range(12)]

    bucket_front_markers = ("facing forward", "straight-on", "eyes locked directly into camera")
    bucket_three_q_markers = ("three-quarter", "off-axis", "one ear drawn back")
    bucket_profile_markers = ("side-profile", "turned close to profile")
    bucket_chin_up_markers = ("chin-up", "chin gently lifted", "chin slightly raised")
    bucket_chin_down_markers = ("chin-down", "chin slightly lowered", "head tipped softly down")
    bucket_strong_turn_markers = ("strong turn", "strong-turn", "turned sharply off-axis")

    def detect_bucket(p: str) -> str:
        if any(m in p for m in bucket_strong_turn_markers):
            return "strong_turn"
        if any(m in p for m in bucket_chin_down_markers):
            return "chin_down"
        if any(m in p for m in bucket_chin_up_markers):
            return "chin_up"
        if any(m in p for m in bucket_profile_markers):
            return "profile"
        if any(m in p for m in bucket_three_q_markers):
            return "three_quarter"
        if any(m in p for m in bucket_front_markers):
            return "front"
        return "unknown"

    detected = [detect_bucket(p) for p in prompts]
    unique_buckets = set(detected) - {"unknown"}
    assert unique_buckets == {"front", "three_quarter", "profile", "chin_up", "chin_down", "strong_turn"}, (
        f"Expected all 6 close-up buckets in 12 sequential prompts, got: {detected}"
    )


def test_close_up_diversity_score_rewards_variety() -> None:
    """_close_up_angle_diversity_score must return a higher score for a diverse close-up batch."""
    all_same = [
        {"camera_framing_id": "face_only", "_batch_index": 0},
        {"camera_framing_id": "face_only", "_batch_index": 4},
        {"camera_framing_id": "face_only", "_batch_index": 8},
        {"camera_framing_id": "face_only", "_batch_index": 12},
    ]
    diverse = [
        {"camera_framing_id": "face_only", "_batch_index": 0},
        {"camera_framing_id": "face_only", "_batch_index": 1},
        {"camera_framing_id": "face_only", "_batch_index": 2},
        {"camera_framing_id": "face_only", "_batch_index": 3},
    ]
    score_same = _close_up_angle_diversity_score(all_same)
    score_diverse = _close_up_angle_diversity_score(diverse)
    assert score_diverse > score_same, (
        f"Diverse batch score ({score_diverse}) should exceed all-same-bucket score ({score_same})"
    )


def test_close_up_diversity_score_empty_batch() -> None:
    assert _close_up_angle_diversity_score([]) == 0


def test_close_up_diversity_score_no_close_up_candidates() -> None:
    batch = [{"camera_framing_id": "full_body"}, {"camera_framing_id": "waist_up"}]
    assert _close_up_angle_diversity_score(batch) == 0
