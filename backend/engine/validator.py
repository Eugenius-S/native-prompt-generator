from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_rule_bank() -> dict[str, Any]:
    return {
        "compatibility": _read_json(ROOT / "rules" / "compatibility_rules.json"),
        "repair": _read_json(ROOT / "rules" / "repair_rules.json"),
        "anti_repeat": _read_json(ROOT / "rules" / "anti_repeat_rules.json"),
        "batch_balance": _read_json(ROOT / "rules" / "batch_balance_rules.json"),
    }


def _has_any(tags: set[str], values: list[str]) -> bool:
    return any(value in tags for value in values)


def validate_candidate(candidate: dict[str, Any], rules: dict[str, Any] | None = None) -> list[dict[str, str]]:
    rules = rules or load_rule_bank()
    tags = set(candidate.get("tags", []))
    findings: list[dict[str, str]] = []

    for rule in rules["compatibility"]["hard_conflicts"]:
        if _has_any(tags, rule.get("if_any_tags", [])):
            if _has_any(tags, rule.get("and_any_tags", [])):
                findings.append({"type": "hard_conflict", "id": rule["id"], "message": rule["message"]})
            if rule.get("and_not_any_tags") and not _has_any(tags, rule["and_not_any_tags"]):
                findings.append({"type": "hard_conflict", "id": rule["id"], "message": rule["message"]})

    for rule in rules["compatibility"]["required_context"]:
        if _has_any(tags, rule.get("trigger_tags", [])) and not _has_any(tags, rule.get("requires_any_tags", [])):
            findings.append(
                {
                    "type": f'{rule["severity"]}_conflict',
                    "id": rule["id"],
                    "message": f'Missing required context for {rule["id"]}.',
                }
            )

    if not candidate.get("beauty_level"):
        findings.append(
            {
                "type": "hard_conflict",
                "id": "women_must_read_beautified",
                "message": "Beauty control is missing.",
            }
        )

    vivid_rules = rules["batch_balance"]["vivid_colored_hair"]
    age_rules = rules["batch_balance"].get("age_rules", {})
    hair_tags = set(candidate.get("hair_color_tags", []))
    if "vivid_colored_hair" in hair_tags and candidate.get("age_band_id") not in vivid_rules["allowed_age_bands"]:
        findings.append(
            {
                "type": "hard_conflict",
                "id": "vivid_colored_hair_age_mismatch",
                "message": "Vivid colored hair is only allowed on the configured younger age band.",
            }
        )

    breast_size_id = candidate.get("breast_size_id")
    age_band_id = candidate.get("age_band_id")
    if breast_size_id == "big_breasts" and age_band_id not in age_rules.get("big_breasts_age_bands", []):
        findings.append(
            {
                "type": "hard_conflict",
                "id": "big_breasts_age_mismatch",
                "message": "Big breasts should stay in the configured younger age bands.",
            }
        )
    if breast_size_id in {"very_big_breasts", "extra_large_breasts"} and age_band_id not in age_rules.get("very_big_breasts_age_bands", []):
        findings.append(
            {
                "type": "hard_conflict",
                "id": "very_big_breasts_age_mismatch" if breast_size_id == "very_big_breasts" else "extra_large_breasts_age_mismatch",
                "message": "Very big breasts should stay in the configured younger age bands." if breast_size_id == "very_big_breasts" else "Extra large breasts should stay in the configured younger age bands.",
            }
        )

    return findings
