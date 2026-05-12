from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.stress_combination_audit import run_audit


def _merge_counter_dicts(reports: list[dict[str, object]], field: str) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for report in reports:
        counter.update({str(key): int(value) for key, value in (report.get(field) or {}).items()})
    return dict(counter.most_common())


def _merge_nested_counter_dicts(reports: list[dict[str, object]], field: str) -> dict[str, dict[str, int]]:
    merged: dict[str, Counter[str]] = {}
    for report in reports:
        raw = report.get(field) or {}
        if not isinstance(raw, dict):
            continue
        for outer_key, inner_map in raw.items():
            if not isinstance(inner_map, dict):
                continue
            counter = merged.setdefault(str(outer_key), Counter())
            counter.update({str(key): int(value) for key, value in inner_map.items()})
    return {outer_key: dict(counter.most_common()) for outer_key, counter in sorted(merged.items())}


def _aggregate_reports(reports: list[dict[str, object]]) -> dict[str, object]:
    if len(reports) == 1:
        result = dict(reports[0])
        result["calibration_runs"] = 1
        result["run_series_violations_per_100"] = [float(result.get("violations_per_100_candidates", 0.0))]
        result["run_series_max_violations_per_100"] = float(result.get("violations_per_100_candidates", 0.0))
        result["run_series_avg_violations_per_100"] = float(result.get("violations_per_100_candidates", 0.0))
        return result

    run_series = [float(report.get("violations_per_100_candidates", 0.0)) for report in reports]
    runs_total = sum(int(report.get("runs_total", 0)) for report in reports)
    runs_successful = sum(int(report.get("runs_successful", 0)) for report in reports)
    runs_failed = sum(int(report.get("runs_failed", 0)) for report in reports)
    candidates_total = sum(int(report.get("candidates_total", 0)) for report in reports)
    violations_total = sum(int(report.get("violations_total", 0)) for report in reports)
    violations_per_100 = round((violations_total / candidates_total) * 100, 2) if candidates_total else 0.0

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "calibration_runs": len(reports),
        "runs_per_case": int(reports[-1].get("runs_per_case", 0)),
        "batch_size": int(reports[-1].get("batch_size", 0)),
        "max_cases": int(reports[-1].get("max_cases", 0)),
        "cases_full_total": int(reports[-1].get("cases_full_total", reports[-1].get("cases_total", 0))),
        "cases_total": int(reports[-1].get("cases_total", 0)),
        "runs_total": runs_total,
        "runs_successful": runs_successful,
        "runs_failed": runs_failed,
        "candidates_total": candidates_total,
        "violations_total": violations_total,
        "violations_per_100_candidates": violations_per_100,
        "run_series_violations_per_100": run_series,
        "run_series_max_violations_per_100": round(max(run_series), 2) if run_series else 0.0,
        "run_series_avg_violations_per_100": round(sum(run_series) / len(run_series), 2) if run_series else 0.0,
        "violation_counts": _merge_counter_dicts(reports, "violation_counts"),
        "violation_counts_by_mode": _merge_nested_counter_dicts(reports, "violation_counts_by_mode"),
        "violation_counts_by_scene": _merge_nested_counter_dicts(reports, "violation_counts_by_scene"),
        "failure_counts_by_case": _merge_counter_dicts(reports, "failure_counts_by_case"),
        "failure_counts_by_mode": _merge_counter_dicts(reports, "failure_counts_by_mode"),
        "failure_counts_by_message": _merge_counter_dicts(reports, "failure_counts_by_message"),
        "per_run": [
            {
                "run": index + 1,
                "runs_total": int(report.get("runs_total", 0)),
                "runs_successful": int(report.get("runs_successful", 0)),
                "runs_failed": int(report.get("runs_failed", 0)),
                "candidates_total": int(report.get("candidates_total", 0)),
                "violations_total": int(report.get("violations_total", 0)),
                "violations_per_100_candidates": float(report.get("violations_per_100_candidates", 0.0)),
            }
            for index, report in enumerate(reports)
        ],
    }


def _summary_markdown(report: dict[str, object], threshold: float, output_path: Path, hard_fail: bool) -> str:
    violations_per_100 = float(report.get("violations_per_100_candidates", 0.0))
    max_violations_per_100 = float(report.get("run_series_max_violations_per_100", violations_per_100))
    avg_violations_per_100 = float(report.get("run_series_avg_violations_per_100", violations_per_100))
    calibration_runs = int(report.get("calibration_runs", 1))
    runs_total = int(report.get("runs_total", 0))
    runs_successful = int(report.get("runs_successful", 0))
    runs_failed = int(report.get("runs_failed", 0))
    cases_total = int(report.get("cases_total", 0))
    cases_full_total = int(report.get("cases_full_total", cases_total))
    candidates_total = int(report.get("candidates_total", 0))
    violations_total = int(report.get("violations_total", 0))
    status = "PASS" if max_violations_per_100 <= threshold and runs_failed == 0 else "WARN"

    lines = [
        "## Coherence Threshold Report",
        "",
        f"- Status: **{status}**",
        f"- Calibration runs: **{calibration_runs}**",
        f"- Threshold (violations per 100): **{threshold}**",
        f"- Actual average (violations per 100): **{avg_violations_per_100}**",
        f"- Actual max (violations per 100): **{max_violations_per_100}**",
        f"- Actual aggregate (violations per 100): **{violations_per_100}**",
        f"- Cases covered: **{cases_total}/{cases_full_total}**",
        f"- Runs: **{runs_successful}/{runs_total}** successful",
        f"- Failed runs: **{runs_failed}**",
        f"- Candidates: **{candidates_total}**",
        f"- Violations: **{violations_total}**",
        f"- Report file: `{output_path}`",
        f"- Hard fail mode: **{'on' if hard_fail else 'off'}**",
        "",
    ]

    top_violations = list((report.get("violation_counts") or {}).items())[:8]
    if top_violations:
        lines.append("### Top violations")
        lines.append("")
        lines.append("| Rule | Count |")
        lines.append("|---|---:|")
        for rule_id, count in top_violations:
            lines.append(f"| {rule_id} | {count} |")
        lines.append("")

    top_failures = list((report.get("failure_counts_by_message") or {}).items())[:5]
    if top_failures:
        lines.append("### Top failures")
        lines.append("")
        lines.append("| Error | Count |")
        lines.append("|---|---:|")
        for message, count in top_failures:
            lines.append(f"| {message} | {count} |")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run coherence audit and emit CI threshold report (non-blocking by default)."
    )
    parser.add_argument("--runs-per-case", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--progress-every", type=int, default=0)
    parser.add_argument("--threshold", type=float, default=2.5)
    parser.add_argument(
        "--calibration-runs",
        type=int,
        default=1,
        help="How many full audits to run before computing threshold checks.",
    )
    parser.add_argument("--output", type=str, default="")
    parser.add_argument(
        "--hard-fail",
        action="store_true",
        help="Fail with exit code 1 when threshold is exceeded or failed runs are present.",
    )
    args = parser.parse_args()

    calibration_runs = max(1, int(args.calibration_runs))
    reports = [
        run_audit(
            runs_per_case=args.runs_per_case,
            batch_size=args.batch_size,
            max_cases=args.max_cases,
            progress_every=args.progress_every,
        )
        for _ in range(calibration_runs)
    ]
    report = _aggregate_reports(reports)

    if args.output:
        output_path = Path(args.output)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = ROOT / "data" / "audits" / f"coherence_ci_report_{stamp}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    violations_per_100 = float(report.get("violations_per_100_candidates", 0.0))
    max_violations_per_100 = float(report.get("run_series_max_violations_per_100", violations_per_100))
    runs_failed = int(report.get("runs_failed", 0))
    threshold_exceeded = max_violations_per_100 > args.threshold
    has_run_failures = runs_failed > 0

    print(f"COHERENCE_REPORT={output_path}")
    print(
        "COHERENCE_SUMMARY "
        f"calibration_runs={calibration_runs} "
        f"cases={report.get('cases_total', 0)}/{report.get('cases_full_total', report.get('cases_total', 0))} "
        f"runs={report.get('runs_total', 0)} "
        f"success={report.get('runs_successful', 0)} "
        f"failed={runs_failed} "
        f"candidates={report.get('candidates_total', 0)} "
        f"violations={report.get('violations_total', 0)} "
        f"viol_per_100={violations_per_100} "
        f"viol_per_100_max={max_violations_per_100} "
        f"threshold={args.threshold}"
    )

    if threshold_exceeded:
        print(
            "::warning::Coherence threshold exceeded: "
            f"viol_per_100_max={max_violations_per_100} > threshold={args.threshold}"
        )
    if has_run_failures:
        print(
            "::warning::Coherence audit had failed runs: "
            f"failed_runs={runs_failed}"
        )

    summary = _summary_markdown(report, args.threshold, output_path, args.hard_fail)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write(summary)
            handle.write("\n")

    if args.hard_fail and (threshold_exceeded or has_run_failures):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
