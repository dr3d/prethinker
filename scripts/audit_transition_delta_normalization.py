#!/usr/bin/env python3
"""Audit deterministic transition/delta observations from compile JSON files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.transition_delta_normalizer import (  # noqa: E402
    normalize_transition_delta_facts,
    summarize_observations,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("compile_json", nargs="+", type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    args = parser.parse_args()

    results = []
    for path in args.compile_json:
        payload = json.loads(path.read_text(encoding="utf-8"))
        facts = payload.get("source_compile", {}).get("facts", [])
        if not isinstance(facts, list):
            facts = []
        observations = normalize_transition_delta_facts([str(fact) for fact in facts])
        results.append(
            {
                "compile_json": str(path),
                "summary": summarize_observations(observations),
                "observations": observations,
            }
        )

    report = {
        "file_count": len(results),
        "results": results,
        "summary": _merge_summaries([item["summary"] for item in results]),
    }

    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(_to_markdown(report), encoding="utf-8")

    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def _merge_summaries(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    total = 0
    for summary in summaries:
        total += int(summary.get("observation_count") or 0)
        for key, value in dict(summary.get("kind_counts") or {}).items():
            counts[str(key)] = counts.get(str(key), 0) + int(value or 0)
    return {
        "observation_count": total,
        "kind_counts": dict(sorted(counts.items())),
    }


def _to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Transition/Delta Normalization Audit",
        "",
        f"- Files: `{report['file_count']}`",
        f"- Observations: `{report['summary']['observation_count']}`",
        f"- Kind counts: `{report['summary']['kind_counts']}`",
        "",
    ]
    for result in report["results"]:
        lines.extend(
            [
                f"## `{Path(result['compile_json']).name}`",
                "",
                f"- Observations: `{result['summary']['observation_count']}`",
                f"- Kind counts: `{result['summary']['kind_counts']}`",
                "",
            ]
        )
        for observation in result["observations"]:
            lines.append(f"- `{observation['kind']}`: `{_compact_observation(observation)}`")
        lines.append("")
    return "\n".join(lines)


def _compact_observation(observation: dict[str, Any]) -> str:
    return ", ".join(
        f"{key}={value}"
        for key, value in observation.items()
        if key not in {"kind"} and value is not None and value != ""
    )


if __name__ == "__main__":
    raise SystemExit(main())
