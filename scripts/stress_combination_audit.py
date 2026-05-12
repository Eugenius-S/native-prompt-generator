from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend import prompt_service
from backend.engine import generator

SPORT_SCENE_TAGS = {"sporty", "wellness", "outdoor"}
WATER_SCENE_TAGS = {"pool", "coastal", "beach", "spa", "wellness", "humid"}
QUIET_SCENE_TAGS = {"bookish", "quiet", "public_elegant", "domestic"}
CREATIVE_SCENE_TAGS = {"creative", "maker"}


@dataclass(frozen=True)
class AuditCase:
    label: str
    form_state: dict[str, Any]


def _scene_tags_by_family() -> dict[str, set[str]]:
    data = generator.load_data_bank()
    mapping: dict[str, set[str]] = defaultdict(set)
    for item in data["setting_engine"]["base_spaces"]:
        mapping[item["scene_family_id"]].update(item.get("tags", []))
    return {family_id: set(tags) for family_id, tags in mapping.items()}


def _pose_meta() -> tuple[dict[str, set[str]], dict[str, str]]:
    data = generator.load_data_bank()
    tags: dict[str, set[str]] = {}
    groups: dict[str, str] = {}
    for item in data["pose_bank"]["pose_families"]:
        pose_id = str(item["id"])
        tags[pose_id] = set(item.get("tags", []))
        groups[pose_id] = str(item.get("group", ""))
    return tags, groups


def _outfit_tags() -> dict[str, set[str]]:
    data = generator.load_data_bank()
    tags: dict[str, set[str]] = {}
    for item in data["styling"]["outfit_families"]:
        tags[str(item["id"])] = set(item.get("tags", []))
    return tags


def _women_native_style(scene_family_id: str) -> str:
    if scene_family_id in {"coastal_pool", "coastal_boardwalk"}:
        return "coastal"
    if scene_family_id in {"nightlife_bar", "nightlife_neon"}:
        return "nightlife"
    if scene_family_id in {"residential_luxury", "hospitality_suite", "grooming_bath"}:
        return "luxury"
    if scene_family_id == "culture_bookish":
        return "cultural_bookish"
    if scene_family_id in {"creative_gallery", "studio"}:
        return "creative_artistic"
    if scene_family_id == "wellness_spa":
        return "fitness"
    return "lifestyle"


def _build_cases(batch_size: int) -> list[AuditCase]:
    base = deepcopy(prompt_service.DEFAULT_FORM_STATE)
    cases: list[AuditCase] = []

    women_scene_families = sorted(
        family for family in prompt_service.ALLOWED_WOMEN_SCENE_FAMILIES if family != "random"
    )
    validations = ["normal", "strict"]
    breast_controls = ["random", "small_breasts"]

    for scene_family in women_scene_families:
        style_probe = _women_native_style(scene_family)
        styles = ["random", style_probe]
        if scene_family in {"nightlife_bar", "nightlife_neon"} and "nightlife" not in styles:
            styles.append("nightlife")
        if scene_family == "wellness_spa" and "fitness" not in styles:
            styles.append("fitness")
        for style_mode in styles:
            for validation_mode in validations:
                for breast_control in breast_controls:
                    state = deepcopy(base)
                    state.update(
                        {
                            "mode": "women",
                            "batchSize": batch_size,
                            "debugMode": True,
                            "styleMode": style_mode,
                            "sceneFocus": "random",
                            "womenSceneFamily": scene_family,
                            "antiRepeat": "hard",
                            "validationMode": validation_mode,
                            "breastSizeControl": breast_control,
                        }
                    )
                    cases.append(
                        AuditCase(
                            label=(
                                f"women|scene={scene_family}|style={style_mode}|"
                                f"validation={validation_mode}|breast={breast_control}"
                            ),
                            form_state=state,
                        )
                    )

    style_sweep = [
        "random",
        "lifestyle",
        "luxury",
        "nightlife",
        "cultural_bookish",
        "creative_artistic",
        "coastal",
        "fitness",
        "sport",
        "romantic",
    ]

    for mode in ("women", "couples", "men"):
        for style_mode in style_sweep:
            for validation_mode in validations:
                state = deepcopy(base)
                state.update(
                    {
                        "mode": mode,
                        "batchSize": batch_size,
                        "debugMode": True,
                        "styleMode": style_mode,
                        "sceneFocus": "random",
                        "antiRepeat": "hard",
                        "validationMode": validation_mode,
                    }
                )
                if mode == "women":
                    state["womenSceneFamily"] = "random"
                    state["breastSizeControl"] = "small_breasts"
                if mode == "couples":
                    state["personMode"] = "different_persons"
                    state["breastSizeControl"] = "small_breasts"
                cases.append(
                    AuditCase(
                        label=f"{mode}|style={style_mode}|validation={validation_mode}|sweep",
                        form_state=state,
                    )
                )

    return cases


def _select_cases(cases: list[AuditCase], max_cases: int) -> list[AuditCase]:
    if max_cases <= 0 or max_cases >= len(cases):
        return cases

    by_mode: dict[str, list[AuditCase]] = defaultdict(list)
    for case in cases:
        by_mode[str(case.form_state.get("mode", "unknown"))].append(case)

    mode_order = ["women", "couples", "men"]
    for mode in sorted(by_mode):
        if mode not in mode_order:
            mode_order.append(mode)

    selected: list[AuditCase] = []
    index_by_mode = {mode: 0 for mode in mode_order}
    while len(selected) < max_cases:
        made_progress = False
        for mode in mode_order:
            bucket = by_mode.get(mode, [])
            index = index_by_mode.get(mode, 0)
            if index >= len(bucket):
                continue
            selected.append(bucket[index])
            index_by_mode[mode] = index + 1
            made_progress = True
            if len(selected) >= max_cases:
                break
        if not made_progress:
            break

    return selected


def _detect_violations(
    candidate: dict[str, Any],
    scene_tags: set[str],
    outfit_tag_map: dict[str, set[str]],
    pose_tag_map: dict[str, set[str]],
    pose_group_map: dict[str, str],
) -> list[str]:
    violations: list[str] = []

    outfit_id = str(candidate.get("outfit_family_id", ""))
    pose_id = str(candidate.get("pose_family_id", ""))
    outfit_tags = outfit_tag_map.get(outfit_id, set())
    pose_tags = pose_tag_map.get(pose_id, set())
    pose_group = pose_group_map.get(pose_id, "")

    if "swimwear" in outfit_tags and not (scene_tags & WATER_SCENE_TAGS):
        violations.append("swimwear_without_water_context")

    if "sporty" in outfit_tags and not (scene_tags & SPORT_SCENE_TAGS):
        violations.append("sporty_outfit_without_sport_context")

    if ("night" in outfit_tags or "editorial" in outfit_tags) and (scene_tags & QUIET_SCENE_TAGS) and "night" not in scene_tags:
        violations.append("night_editorial_outfit_in_quiet_day_scene")

    if "sport_prep" in pose_tags and not (scene_tags & SPORT_SCENE_TAGS):
        violations.append("sport_prep_pose_without_sport_context")

    if "bookish" in pose_tags and "bookish" not in scene_tags:
        violations.append("bookish_task_pose_without_bookish_scene")

    if "creative" in pose_tags and not (scene_tags & CREATIVE_SCENE_TAGS):
        violations.append("creative_task_pose_without_creative_scene")

    if "domestic" in pose_tags and "domestic" not in scene_tags:
        violations.append("domestic_task_pose_without_domestic_scene")

    if "outdoor" in pose_tags and "outdoor" not in scene_tags:
        violations.append("outdoor_pose_inside_scene")

    if pose_group == "kneeling" and (scene_tags & QUIET_SCENE_TAGS) and not (scene_tags & {"sporty", "wellness"}):
        violations.append("kneeling_pose_in_quiet_formal_scene")

    return violations


def run_audit(
    runs_per_case: int,
    batch_size: int,
    max_cases: int = 0,
    progress_every: int = 0,
) -> dict[str, Any]:
    scene_tag_map = _scene_tags_by_family()
    pose_tag_map, pose_group_map = _pose_meta()
    outfit_tag_map = _outfit_tags()

    all_cases = _build_cases(batch_size)
    cases = _select_cases(all_cases, max_cases=max_cases)

    violation_counter: Counter[str] = Counter()
    violation_by_mode: dict[str, Counter[str]] = defaultdict(Counter)
    violation_by_scene: dict[str, Counter[str]] = defaultdict(Counter)
    violation_by_case: Counter[str] = Counter()
    violation_by_breast: dict[str, Counter[str]] = defaultdict(Counter)
    violation_by_validation: dict[str, Counter[str]] = defaultdict(Counter)
    failure_by_case: Counter[str] = Counter()
    failure_by_mode: Counter[str] = Counter()
    failure_by_message: Counter[str] = Counter()
    failure_by_breast: Counter[str] = Counter()
    failure_by_validation: Counter[str] = Counter()
    runs_by_breast: Counter[str] = Counter()
    runs_by_validation: Counter[str] = Counter()
    examples: dict[str, list[dict[str, Any]]] = defaultdict(list)

    total_runs = 0
    successful_runs = 0
    failed_runs = 0
    total_candidates = 0

    original_append_history = prompt_service.append_history
    original_save_memory = generator._save_memory

    prompt_service.append_history = lambda entry, limit=40: {"id": "audit", **entry}
    generator._save_memory = lambda memory: None

    try:
        expected_runs = len(cases) * runs_per_case
        for case in cases:
            for _ in range(runs_per_case):
                total_runs += 1
                if progress_every > 0 and total_runs % progress_every == 0:
                    print(
                        f"AUDIT_PROGRESS runs={total_runs}/{expected_runs} "
                        f"mode={case.form_state.get('mode', 'unknown')}",
                        flush=True,
                    )
                breast_control = str(case.form_state.get("breastSizeControl", "n/a"))
                validation_mode = str(case.form_state.get("validationMode", "normal"))
                runs_by_breast[breast_control] += 1
                runs_by_validation[validation_mode] += 1
                try:
                    result = prompt_service.generate_run(case.form_state)
                except Exception as exc:
                    failed_runs += 1
                    failure_by_case[case.label] += 1
                    failure_by_mode[str(case.form_state.get("mode", "unknown"))] += 1
                    failure_by_message[str(exc)] += 1
                    failure_by_breast[breast_control] += 1
                    failure_by_validation[validation_mode] += 1
                    continue

                successful_runs += 1
                prompts = result.get("prompts", [])
                total_candidates += len(prompts)

                for item in prompts:
                    candidate = item.get("candidate", {})
                    scene_family_id = str(candidate.get("scene_family_id", ""))
                    mode = str(case.form_state.get("mode", "unknown"))
                    scene_tags = scene_tag_map.get(scene_family_id, set())

                    violations = _detect_violations(
                        candidate,
                        scene_tags,
                        outfit_tag_map,
                        pose_tag_map,
                        pose_group_map,
                    )
                    for violation_id in violations:
                        violation_counter[violation_id] += 1
                        violation_by_mode[mode][violation_id] += 1
                        violation_by_scene[scene_family_id][violation_id] += 1
                        violation_by_case[case.label] += 1
                        violation_by_breast[breast_control][violation_id] += 1
                        violation_by_validation[validation_mode][violation_id] += 1
                        if len(examples[violation_id]) < 8:
                            examples[violation_id].append(
                                {
                                    "case": case.label,
                                    "scene_family_id": scene_family_id,
                                    "setting_micro_id": candidate.get("setting_micro_id"),
                                    "outfit_family_id": candidate.get("outfit_family_id"),
                                    "pose_family_id": candidate.get("pose_family_id"),
                                    "tags": sorted(candidate.get("tags", [])),
                                }
                            )
    finally:
        prompt_service.append_history = original_append_history
        generator._save_memory = original_save_memory

    violations_per_100 = 0.0
    if total_candidates:
        violations_per_100 = round((sum(violation_counter.values()) / total_candidates) * 100, 2)

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "runs_per_case": runs_per_case,
        "batch_size": batch_size,
        "max_cases": max_cases,
        "cases_full_total": len(all_cases),
        "cases_total": len(cases),
        "runs_total": total_runs,
        "runs_successful": successful_runs,
        "runs_failed": failed_runs,
        "candidates_total": total_candidates,
        "violations_total": sum(violation_counter.values()),
        "violations_per_100_candidates": violations_per_100,
        "violation_counts": dict(violation_counter.most_common()),
        "violation_counts_by_mode": {
            mode: dict(counter.most_common())
            for mode, counter in sorted(violation_by_mode.items())
        },
        "violation_counts_by_scene": {
            scene: dict(counter.most_common())
            for scene, counter in sorted(violation_by_scene.items())
            if counter
        },
        "violation_counts_by_case": dict(violation_by_case.most_common()),
        "violation_counts_by_breast_control": {
            control: dict(counter.most_common())
            for control, counter in sorted(violation_by_breast.items())
        },
        "violation_counts_by_validation_mode": {
            mode: dict(counter.most_common())
            for mode, counter in sorted(violation_by_validation.items())
        },
        "failure_counts_by_case": dict(failure_by_case.most_common()),
        "failure_counts_by_mode": dict(failure_by_mode.most_common()),
        "failure_counts_by_message": dict(failure_by_message.most_common()),
        "failure_counts_by_breast_control": dict(failure_by_breast.most_common()),
        "failure_counts_by_validation_mode": dict(failure_by_validation.most_common()),
        "runs_by_breast_control": dict(runs_by_breast.most_common()),
        "runs_by_validation_mode": dict(runs_by_validation.most_common()),
        "examples": dict(examples),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run a broad generation stress audit and report systematic outfit/pose/scene mismatch patterns."
        )
    )
    parser.add_argument("--runs-per-case", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--progress-every", type=int, default=0)
    parser.add_argument("--output", type=str, default="")
    args = parser.parse_args()

    report = run_audit(
        runs_per_case=args.runs_per_case,
        batch_size=args.batch_size,
        max_cases=args.max_cases,
        progress_every=args.progress_every,
    )

    if args.output:
        output_path = Path(args.output)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = ROOT / "data" / "audits" / f"combination_audit_{stamp}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"AUDIT_REPORT={output_path}")
    print(
        "AUDIT_SUMMARY "
        f"runs={report['runs_total']} success={report['runs_successful']} failed={report['runs_failed']} "
        f"candidates={report['candidates_total']} violations={report['violations_total']} "
        f"viol_per_100={report['violations_per_100_candidates']}"
    )
    top_violations = list(report["violation_counts"].items())[:10]
    if top_violations:
        print("TOP_VIOLATIONS")
        for rule_id, count in top_violations:
            print(f"- {rule_id}: {count}")
    top_failures = list(report["failure_counts_by_message"].items())[:5]
    if top_failures:
        print("TOP_FAILURES")
        for message, count in top_failures:
            print(f"- {message}: {count}")


if __name__ == "__main__":
    main()
