from __future__ import annotations

from typing import Any

from backend.engine import generator
from backend.engine.repair import repair_candidate
from backend.engine.validator import load_rule_bank, validate_candidate
from backend.prompt_service import _apply_prompt_constraints, _diversify_women_outfit_colors, _user_style_profile


def _women_debug_meta(candidate: dict[str, Any], repair_applied: bool, findings_count: int, index: int) -> dict[str, Any]:
    return {
        "index": index + 1,
        "route": candidate.get("route", ""),
        "sceneFamily": candidate.get("scene_family_id", ""),
        "setting": candidate.get("setting_micro", ""),
        "lineBankLocation": candidate.get("line_bank_location", ""),
        "outfit": candidate.get("outfit_family", ""),
        "material": candidate.get("material", ""),
        "color": candidate.get("color_story", ""),
        "pose": candidate.get("pose_family", ""),
        "hand": candidate.get("hand_action", ""),
        "framing": candidate.get("camera_framing", ""),
        "lighting": candidate.get("lighting_family", ""),
        "time": candidate.get("time_of_day", ""),
        "mood": candidate.get("mood_energy", ""),
        "photoTreatment": candidate.get("photo_treatment", ""),
        "photoTreatmentCategory": candidate.get("photo_treatment_category", ""),
        "cameraVibe": candidate.get("camera_vibe", ""),
        "colorGrade": candidate.get("color_grade", ""),
        "finish": candidate.get("finish_render", ""),
        "hair": candidate.get("hair_structure_override") or candidate.get("hair_structure", ""),
        "hairColor": candidate.get("hair_color_override") or candidate.get("hair_color", ""),
        "makeup": candidate.get("makeup_style", ""),
        "capture": candidate.get("capture_style", ""),
        "captureRender": candidate.get("capture_style_render") or candidate.get("capture_style", ""),
        "lineBankPose": candidate.get("line_bank_pose", ""),
        "lineBankOutfit": candidate.get("line_bank_outfit", ""),
        "lineBankExpression": candidate.get("line_bank_expression", ""),
        "lineBankLocation": candidate.get("line_bank_location", ""),
        "repairApplied": repair_applied,
        "findingsCount": findings_count,
    }


class WomenModeHandler:
    def build_profile(self, form_state: dict[str, Any], spicy_level: int, effective_style_mode: str) -> dict[str, Any]:
        scoring_form_state = dict(form_state)
        scoring_form_state["styleMode"] = effective_style_mode
        return _user_style_profile(scoring_form_state, spicy_level)

    def render_prompt_batch(
        self,
        batch: list[dict[str, Any]],
        findings_map: dict[int, list[dict[str, Any]]],
        form_state: dict[str, Any],
        spicy_level: int,
        effective_style_mode: str,
        chosen_seed: int,
        user_profile: dict[str, Any],
    ) -> list[dict[str, Any]]:
        del chosen_seed
        rules = load_rule_bank()
        data = generator.load_data_bank()
        prompts: list[dict[str, Any]] = []
        for index, candidate in enumerate(batch):
            findings = findings_map[index]
            repaired = repair_candidate(candidate, findings, rules) if findings else candidate
            normalized_candidate = generator._normalize_candidate(data, repaired, style_mode=effective_style_mode, user_profile=user_profile)
            rendered_candidate = _apply_prompt_constraints(normalized_candidate, form_state, spicy_level)
            rendered_candidate["_batch_index"] = index
            rendered_findings = validate_candidate(normalized_candidate, rules)
            repair_applied = normalized_candidate != candidate
            prompts.append(
                {
                    "prompt": generator.render_candidate_prompt(rendered_candidate),
                    "segments": generator.render_candidate_segments(rendered_candidate),
                    "candidate": rendered_candidate,
                    "findings": rendered_findings,
                    "repairApplied": repair_applied,
                    "debugMeta": _women_debug_meta(rendered_candidate, repair_applied, len(rendered_findings), index),
                }
            )
        return prompts

    def post_render_batch(self, prompts: list[dict[str, Any]], form_state: dict[str, Any], spicy_level: int) -> list[dict[str, Any]]:
        return _diversify_women_outfit_colors(prompts, form_state, spicy_level)


WOMEN_HANDLER = WomenModeHandler()
