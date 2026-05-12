from __future__ import annotations

from collections import Counter
from functools import lru_cache

from backend.engine.render import prompt_renderer
from backend.prompt_service import _merged_form_state, generate_run


FRAMING_GROUPS = {
    "portrait": {"waist_up", "bust_up", "close_portrait", "head_and_shoulders", "face_only", "below_chest_portrait"},
    "mid": {"knee_up", "cowboy_shot"},
    "full": {"full_body", "ankle_up"},
}

NEW_RANDOM_VARIANT_IDS = {"below_chest_portrait", "ankle_up"}
LEGACY_RANDOM_BASE_IDS = {"waist_up", "bust_up", "close_portrait", "head_and_shoulders", "full_body"}


def _render_candidate(**overrides: str) -> dict[str, str]:
    candidate = {
        "beauty_level": "beautified and flattering",
        "age_band": "22 years old",
        "ethnicity": "Spanish",
        "body_type": "athletic build",
        "breast_size": "medium breasts",
        "hair_color": "dark brown hair",
        "hair_structure": "loose waves",
        "eye_color": "brown eyes",
        "makeup_style": "fresh natural makeup",
        "camera_framing_id": "full_body",
        "camera_framing": "full body framing",
        "photo_treatment_id": "clean_commercial",
        "capture_style_render": "clean commercial fashion photo",
        "camera_angle": "eye-level angle",
        "lighting_render": "soft clean commercial light",
        "time_of_day": "afternoon",
        "camera_vibe": "DSLR beauty editorial feel",
        "color_grade": "clean airy commercial color",
        "lens_look": "85mm lens look",
        "finish_render": "natural skin texture",
        "outfit_family_id": "column_dress",
        "outfit_family": "column dress",
        "color_story_id": "champagne_taupe",
        "color_story": "champagne and taupe palette",
        "material": "soft satin",
        "scene_family_id": "residential_luxury",
        "setting_scene": "sunlit hotel suite",
        "pose_family": "standing with one hip slightly angled",
        "hand_action": "one hand at her waist",
        "mood_energy": "soft flirty energy",
        "person_mode": "different_persons",
    }
    candidate.update(overrides)
    return candidate


@lru_cache(maxsize=None)
def _group_counts(control: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for seed in range(6):
        form = _merged_form_state(
            {
                "mode": "women",
                "batchSize": 8,
                "styleMode": "random",
                "poseFramingControl": control,
                "seed": str(seed),
                "debugMode": "on",
                "antiRepeat": "hard",
                "validationMode": "strict",
            }
        )
        run = generate_run(form)
        for item in run["prompts"]:
            framing_id = item["candidate"]["camera_framing_id"]
            for group, framing_ids in FRAMING_GROUPS.items():
                if framing_id in framing_ids:
                    counts[group] += 1
                    break
    return counts


@lru_cache(maxsize=None)
def _framing_counts(control: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for seed in range(12):
        form = _merged_form_state(
            {
                "mode": "women",
                "batchSize": 8,
                "styleMode": "random",
                "poseFramingControl": control,
                "seed": str(seed),
                "debugMode": "on",
                "antiRepeat": "hard",
                "validationMode": "strict",
            }
        )
        run = generate_run(form)
        for item in run["prompts"]:
            counts[item["candidate"]["camera_framing_id"]] += 1
    return counts


def test_more_portraits_control_pushes_batch_toward_portrait_groups() -> None:
    mixed = _group_counts("mixed")
    portraits = _group_counts("more_portraits")

    assert portraits["portrait"] >= mixed["portrait"] + 10
    assert portraits["portrait"] > portraits["mid"]
    assert portraits["portrait"] > portraits["full"]
    assert portraits["mid"] == 0
    assert portraits["full"] == 0


def test_more_full_body_control_pushes_batch_toward_full_body_group() -> None:
    mixed = _group_counts("mixed")
    full_body = _group_counts("more_full_body")

    assert full_body["full"] >= mixed["full"] + 10
    assert full_body["full"] > full_body["mid"]
    assert full_body["full"] > full_body["portrait"]
    assert full_body["mid"] == 0
    assert full_body["portrait"] == 0


def test_medium_shots_control_keeps_only_mid_group() -> None:
    mixed = _group_counts("mixed")
    medium = _group_counts("medium_shots")

    assert medium["mid"] >= mixed["mid"] + 10
    assert medium["mid"] > medium["portrait"]
    assert medium["mid"] > medium["full"]
    assert medium["portrait"] == 0
    assert medium["full"] == 0


def test_random_control_mixes_new_framing_variants_with_legacy_base() -> None:
    random_counts = _framing_counts("random")

    assert sum(random_counts[item_id] for item_id in NEW_RANDOM_VARIANT_IDS) >= 6
    assert sum(random_counts[item_id] for item_id in LEGACY_RANDOM_BASE_IDS) >= 12
    assert random_counts["ankle_up"] >= 2
    assert random_counts["full_body"] >= 2
    assert random_counts["face_only"] == 0


def test_more_portraits_control_removes_face_only_variant() -> None:
    portrait_counts = _framing_counts("more_portraits")

    assert portrait_counts["face_only"] == 0
    assert portrait_counts["head_and_shoulders"] >= 1
    assert portrait_counts["below_chest_portrait"] >= 1


def test_camera_framing_render_uses_stronger_full_body_and_portrait_language() -> None:
    assert prompt_renderer._effective_camera_framing_text(
        {"camera_framing_id": "full_body", "camera_framing": "full body framing"}
    ) == "full-length framing, camera far enough from the subject to keep the whole standing figure in frame, centered as a full-height composition with ankles or feet visible when the pose allows, avoid waist-up, mid-shot, and portrait crop"
    assert prompt_renderer._effective_camera_framing_text(
        {"camera_framing_id": "head_and_shoulders", "camera_framing": "head and shoulders portrait framing"}
    ) == "head-and-shoulders portrait with full head and hair visible, breathing room above the head, cropped above the chest, no top-of-head crop"
    assert prompt_renderer._effective_camera_framing_text(
        {"camera_framing_id": "face_only", "camera_framing": "face-only portrait framing"}
    ) == "tight beauty headshot with full face and hair visible, a little breathing room above the head, a hint of neck or upper shoulders visible, avoid ultra-tight face-only crop"
    assert prompt_renderer._effective_camera_framing_text(
        {"camera_framing_id": "ankle_up", "camera_framing": "ankle-up full figure framing"}
    ) == "full-length figure framing, camera far enough from the subject to keep the whole figure in frame, centered as a full-height composition with the crop landing near the ankles, avoid waist-up, mid-shot, and portrait crop"


def test_full_body_framing_block_adds_camera_pullback_for_standing_pose() -> None:
    block = prompt_renderer._format_framing_block(
        {
            "camera_framing_id": "full_body",
            "pose_family": "standing in a relaxed three quarter angle with one hip popped",
        }
    )

    assert "true full-length standing shot" in block
    assert "camera pulled back" in block
    assert "whole standing figure visible in frame" in block
    assert "centered as a full-height composition" in block
    assert "no waist-up crop" in block


def test_portrait_framing_block_keeps_breathing_room_above_head() -> None:
    block = prompt_renderer._format_framing_block(
        {
            "camera_framing_id": "head_and_shoulders",
            "pose_family": "standing with one shoulder forward and a soft direct gaze",
        }
    )

    assert "head-and-shoulders portrait" in block
    assert "breathing room above the head" in block
    assert "no top-of-head crop" in block
    assert "above the chest" in prompt_renderer._effective_camera_framing_text(
        {"camera_framing_id": "head_and_shoulders", "camera_framing": "head and shoulders portrait framing"}
    )


def test_rendered_prompt_opener_leads_with_framing_and_treatment_text() -> None:
    prompt = prompt_renderer.render_candidate_prompt(_render_candidate())

    assert prompt.startswith("Full-body fashion photo of a 22-year-old Spanish woman")
    assert "true full-length standing shot" in prompt
    assert "whole standing figure visible in frame" in prompt
    assert "no portrait crop" in prompt


def test_explicit_mirror_selfie_control_keeps_selfie_opener_in_live_generation() -> None:
    form = _merged_form_state(
        {
            "mode": "women",
            "batchSize": 4,
            "styleMode": "luxury",
            "poseFramingControl": "more_full_body",
            "photoTypeControl": "custom",
            "photoTreatmentControl": "mirror_selfie",
            "seed": "2",
            "debugMode": "on",
            "antiRepeat": "hard",
            "validationMode": "strict",
        }
    )

    run = generate_run(form)
    framing_first_selfie_prefixes = (
        "close-up mirror selfie",
        "tight close-up mirror selfie",
        "head-and-shoulders mirror selfie",
        "bust-up mirror selfie",
        "upper-body mirror selfie",
        "waist-up mirror selfie",
        "knee-up mirror selfie",
        "cowboy-shot mirror selfie",
        "full-body mirror selfie",
        "full-figure mirror selfie",
    )

    assert run["prompts"]
    assert all(item["candidate"]["photo_treatment_id"] == "mirror_selfie" for item in run["prompts"])
    assert all(item["prompt"].lower().startswith(framing_first_selfie_prefixes) for item in run["prompts"])
