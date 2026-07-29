from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def tool_names(calls: list[dict[str, Any]]) -> str:
    return "|".join(call.get("name", "") for call in calls)


def first_expected_tool(expect: dict[str, Any]) -> str:
    calls = expect.get("tool_calls") or []
    if not calls:
        return "no_tool" if expect.get("no_tool") else ""
    return "|".join(call.get("name", "") for call in calls)


def execution_details(tool_results: list[dict[str, Any]]) -> tuple[str, int, int, str]:
    if not tool_results:
        return "not_called", 0, 0, ""

    details: list[dict[str, Any]] = []
    success_count = 0
    error_count = 0
    for event in tool_results:
        payload = event.get("result")
        wrapper_error = event.get("error")
        payload_error = payload.get("error") if isinstance(payload, dict) else None
        error = wrapper_error or payload_error
        if error:
            error_count += 1
        else:
            success_count += 1
        details.append({
            "tool": event.get("tool"),
            "status": "error" if error else "success",
            "error": error or "",
            "message": payload.get("message", "") if isinstance(payload, dict) else "",
        })

    if error_count and success_count:
        status = "mixed"
    elif error_count:
        status = "error"
    else:
        status = "success"
    return status, success_count, error_count, json.dumps(details, ensure_ascii=False)


def row_for(run: dict[str, Any], result_item: dict[str, Any]) -> dict[str, Any]:
    result = result_item["result"]
    execution_status, execution_success_count, execution_error_count, execution_detail = execution_details(
        result_item.get("tool_results") or []
    )
    return {
        "run_id": run.get("run_id"),
        "version": run.get("version"),
        "artifact_version": run.get("artifact_version"),
        "suite": run.get("suite"),
        "case_id": result_item.get("id"),
        "is_multiturn": result_item.get("is_multiturn"),
        "case_failure_type": result.get("case_failure_type"),
        "observed_mismatch": result.get("observed_mismatch") or "",
        "expected_tool": first_expected_tool(result_item.get("expect", {})),
        "actual_tool": tool_names(result.get("actual_tool_calls") or []),
        "passed": result.get("passed"),
        "routing_correct": result.get("routing_correct"),
        "args_correct": result.get("args_correct"),
        "execution_status": execution_status,
        "execution_success_count": execution_success_count,
        "execution_error_count": execution_error_count,
        "execution_detail": execution_detail,
        "failures": "; ".join(result.get("failures") or []),
    }


def iter_run_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.glob("*.json")))
        else:
            files.append(path)
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse run JSON into a flat CSV analysis table.")
    parser.add_argument("paths", nargs="+", type=Path, help="Run JSON file(s) or directory containing run JSON files.")
    parser.add_argument("--output", type=Path, default=None, help="Output CSV path. If omitted, print to stdout.")
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    for path in iter_run_files(args.paths):
        run = json.loads(path.read_text(encoding="utf-8"))
        for item in run.get("results", []):
            rows.append(row_for(run, item))

    fieldnames = [
        "run_id", "version", "artifact_version", "suite", "case_id", "is_multiturn",
        "case_failure_type", "observed_mismatch", "expected_tool", "actual_tool",
        "passed", "routing_correct", "args_correct", "execution_status",
        "execution_success_count", "execution_error_count", "execution_detail", "failures",
    ]

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Saved {len(rows)} rows to {args.output}")
        return

    import sys

    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


if __name__ == "__main__":
    main()
