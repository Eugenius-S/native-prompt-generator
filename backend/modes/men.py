from __future__ import annotations

from typing import Any

from backend.legacy_bridge import render_batch as render_mode_batch
from backend.engine import generator
from backend.engine.repair import repair_candidate
from backend.engine.validator import load_rule_bank, validate_candidate
from backend.prompt_service import _apply_prompt_constraints, _diversify_women_outfit_colors, _user_style_profile


class MenModeHandler:
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
        rules = load_rule_bank()
        data = generator.load_data_bank()
        scaffolds: list[dict[str, Any]] = []
        for index, candidate in enumerate(batch):
            findings = findings_map[index]
            repaired = repair_candidate(candidate, findings, rules) if findings else candidate
            normalized_candidate = generator._normalize_candidate(data, repaired, style_mode=effective_style_mode, user_profile=user_profile)
            rendered_candidate = _apply_prompt_constraints(normalized_candidate, form_state, spicy_level)
            rendered_findings = validate_candidate(normalized_candidate, rules)
            repair_applied = normalized_candidate != candidate
            scaffolds.append(
                {
                    "candidate": rendered_candidate,
                    "findings": rendered_findings,
                    "repairApplied": repair_applied,
                }
            )
        mode_prompts = render_mode_batch("men", [item["candidate"] for item in scaffolds], form_state, effective_style_mode, chosen_seed, spicy_level)
        return [
            {
                "prompt": mode_prompt["prompt"],
                "segments": mode_prompt["segments"],
                "candidate": scaffold["candidate"],
                "findings": scaffold["findings"],
                "repairApplied": scaffold["repairApplied"],
                "debugMeta": mode_prompt.get("debugMeta"),
            }
            for scaffold, mode_prompt in zip(scaffolds, mode_prompts)
        ]

    def post_render_batch(self, prompts: list[dict[str, Any]], form_state: dict[str, Any], spicy_level: int) -> list[dict[str, Any]]:
        return _diversify_women_outfit_colors(prompts, form_state, spicy_level)


MEN_HANDLER = MenModeHandler()
