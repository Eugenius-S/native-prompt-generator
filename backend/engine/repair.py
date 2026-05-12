from __future__ import annotations

from typing import Any

try:
    from .validator import load_rule_bank, validate_candidate
except ImportError:
    from validator import load_rule_bank, validate_candidate


def _has_finding(findings: list[dict[str, str]], finding_id: str) -> bool:
    return any(item.get("id") == finding_id for item in findings)


def repair_candidate(candidate: dict[str, Any], findings: list[dict[str, str]], rules: dict[str, Any] | None = None) -> dict[str, Any]:
    rules = rules or load_rule_bank()
    repair_rules = rules["repair"]
    repaired = dict(candidate)
    repaired["tags"] = list(repaired.get("tags", []))

    for finding in findings:
        actions = repair_rules["fix_map"].get(finding["id"], [])
        for action in actions:
            if action == "remove_small_conflicting_detail":
                repaired["surface_state_id"] = "dry_clean"
                repaired["surface_state"] = "dry clean skin"
                repaired["tags"] = [tag for tag in repaired["tags"] if tag not in {"wet", "sand", "flush"}]
                if "dry" not in repaired["tags"]:
                    repaired["tags"].append("dry")
            elif action == "swap_surface_state":
                repaired["surface_state_id"] = "dry_clean"
                repaired["surface_state"] = "dry clean skin"
                repaired["tags"] = [tag for tag in repaired["tags"] if tag not in {"wet", "sand", "flush"}]
                if "dry" not in repaired["tags"]:
                    repaired["tags"].append("dry")
            elif action == "swap_outfit_detail":
                repaired["outfit_family_id"] = "mini_dress"
                repaired["outfit_family"] = "fitted mini dress with a deep neckline"
                repaired["tags"] = [tag for tag in repaired["tags"] if tag not in {"swimwear", "sporty"}]
                for tag in ("dress", "body_hugging", "slutty"):
                    if tag not in repaired["tags"]:
                        repaired["tags"].append(tag)
            elif action == "swap_setting_micro":
                repaired["scene_family_id"] = "residential_luxury"
                repaired["setting_micro_id"] = "penthouse_living_room"
                repaired["setting_micro"] = "sunlit penthouse living room with a curved cream sofa and floor to ceiling windows"
                repaired["setting_material_id"] = "travertine_stone"
                repaired["setting_material"] = "warm travertine and pale stone detailing"
                repaired["detail_accent_id"] = "fresh_flowers"
                repaired["detail_accent"] = "fresh flowers placed as a soft focal detail"
                repaired["atmosphere_cue_id"] = "warm_afternoon_glow"
                repaired["atmosphere_cue"] = "warm afternoon glow with gentle highlights"
                repaired["setting_scene_id"] = "penthouse_living_room__travertine_stone__fresh_flowers__warm_afternoon_glow"
                repaired["setting_scene"] = (
                    "sunlit penthouse living room with a curved cream sofa and floor to ceiling windows, "
                    "warm travertine and pale stone detailing, fresh flowers placed as a soft focal detail, "
                    "warm afternoon glow with gentle highlights"
                )
                repaired["tags"] = [tag for tag in repaired["tags"] if tag not in {"outdoor", "pool", "beach", "sand"}]
                for tag in ("interior", "luxury", "sunny", "daylight"):
                    if tag not in repaired["tags"]:
                        repaired["tags"].append(tag)
            elif action == "swap_pose_family":
                repaired["pose_family_id"] = "standing_three_quarter"
                repaired["pose_family"] = "standing in a relaxed three quarter angle with one hip popped"

            remaining = validate_candidate(repaired, rules)
            if not _has_finding(remaining, finding["id"]):
                break

    return repaired
