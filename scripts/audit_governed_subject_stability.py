#!/usr/bin/env python3
"""Audit governed subject discovery stability across compile artifacts.

The audit reads only typed compile facts. It does not inspect source prose,
source-record ledgers, QA questions, or oracle answers.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.reconcile_typed_micro_compiles import (  # noqa: E402
    _governed_ground_atom,
    _governed_legal_role_atom,
    _governed_reference_atom,
    _parse_fact,
)


COMPANION_PREDICATES = {
    "claim_ground",
    "claim_range",
    "legal_citation_detail",
    "review_outcome",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-json", action="append", required=True, type=Path)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--min-support", type=int, default=2)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.compile_json, min_support=args.min_support)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def build_report(paths: list[Path], *, min_support: int = 2) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    key_support: dict[str, set[str]] = {}
    for path in paths:
        artifact_id = path.parent.name or path.name
        facts = _facts_from_compile_json(path)
        run = _summarize_run(artifact_id=artifact_id, path=path, facts=facts)
        runs.append(run)
        for key in run["claim_ground_keys"]:
            key_support.setdefault(key, set()).add(artifact_id)
    repeated_keys = {
        key: sorted(supporters)
        for key, supporters in sorted(key_support.items())
        if len(supporters) >= min_support
    }
    singleton_keys = {
        key: sorted(supporters)
        for key, supporters in sorted(key_support.items())
        if len(supporters) == 1
    }
    return {
        "schema_version": "governed_subject_stability_audit_v1",
        "authority": "typed_fact_diagnostic_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "min_support": min_support,
        "summary": {
            "run_count": len(runs),
            "distinct_claim_ground_key_count": len(key_support),
            "repeated_claim_ground_key_count": len(repeated_keys),
            "singleton_claim_ground_key_count": len(singleton_keys),
            "runs_with_keyable_subjects": sum(1 for run in runs if run["keyable_subject_count"]),
            "runs_without_keyable_subjects": sum(1 for run in runs if not run["keyable_subject_count"]),
        },
        "repeated_claim_ground_keys": repeated_keys,
        "singleton_claim_ground_keys": singleton_keys,
        "runs": runs,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Governed Subject Stability Audit",
        "",
        f"- Runs: `{summary['run_count']}`",
        f"- Min support: `{report['min_support']}`",
        f"- Distinct claim-ground keys: `{summary['distinct_claim_ground_key_count']}`",
        f"- Repeated claim-ground keys: `{summary['repeated_claim_ground_key_count']}`",
        f"- Singleton claim-ground keys: `{summary['singleton_claim_ground_key_count']}`",
        f"- Runs with keyable subjects: `{summary['runs_with_keyable_subjects']}`",
        f"- Runs without keyable subjects: `{summary['runs_without_keyable_subjects']}`",
        "",
        "## Runs",
        "",
        "| Artifact | Raw subjects | Keyable subjects | Unkeyable subjects | Claim-ground keys | Path |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for run in report["runs"]:
        lines.append(
            "| `{}` | {} | {} | {} | {} | `{}` |".format(
                run["artifact_id"],
                run["raw_subject_count"],
                run["keyable_subject_count"],
                run["unkeyable_subject_count"],
                len(run["claim_ground_keys"]),
                run["path"],
            )
        )
    lines.extend(["", "## Repeated Claim-Ground Keys", ""])
    if report["repeated_claim_ground_keys"]:
        for key, supporters in report["repeated_claim_ground_keys"].items():
            lines.append(f"- `{key}`: {', '.join(f'`{item}`' for item in supporters)}")
    else:
        lines.append("- none")
    lines.extend(["", "## Singleton Claim-Ground Keys", ""])
    if report["singleton_claim_ground_keys"]:
        for key, supporters in report["singleton_claim_ground_keys"].items():
            lines.append(f"- `{key}`: {', '.join(f'`{item}`' for item in supporters)}")
    else:
        lines.append("- none")
    lines.extend(["", "## Unkeyable Subjects", ""])
    for run in report["runs"]:
        if not run["unkeyable_subjects"]:
            continue
        lines.append(f"### {run['artifact_id']}")
        for subject in run["unkeyable_subjects"]:
            lines.append(
                "- `{}` predicates=`{}` claim_ground_keys=`{}`".format(
                    subject["subject"],
                    subject["predicates"],
                    subject["claim_ground_keys"],
                )
            )
    return "\n".join(lines) + "\n"


def _facts_from_compile_json(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    source_compile = data.get("source_compile")
    if isinstance(source_compile, dict) and isinstance(source_compile.get("facts"), list):
        return [str(fact).strip() for fact in source_compile.get("facts", []) if str(fact).strip()]
    if isinstance(data.get("facts"), list):
        return [str(fact).strip() for fact in data.get("facts", []) if str(fact).strip()]
    return []


def _summarize_run(*, artifact_id: str, path: Path, facts: list[str]) -> dict[str, Any]:
    subjects: dict[str, dict[str, Any]] = {}
    for fact in facts:
        parsed = _parse_fact(fact)
        if parsed is None:
            continue
        predicate = parsed["predicate"]
        args = [str(arg).strip() for arg in parsed["args"]]
        if predicate not in COMPANION_PREDICATES or not args:
            continue
        subject = args[0]
        row = subjects.setdefault(subject, {"subject": subject, "predicates": set(), "claim_ground_keys": set()})
        row["predicates"].add(predicate)
        if predicate == "claim_ground" and len(args) == 4:
            row["claim_ground_keys"].add(_claim_ground_key(args))
    keyable: list[dict[str, Any]] = []
    unkeyable: list[dict[str, Any]] = []
    claim_ground_keys: set[str] = set()
    for row in subjects.values():
        serialized = {
            "subject": row["subject"],
            "predicates": sorted(row["predicates"]),
            "claim_ground_keys": sorted(row["claim_ground_keys"]),
        }
        if len(row["claim_ground_keys"]) == 1:
            keyable.append(serialized)
            claim_ground_keys.update(row["claim_ground_keys"])
        else:
            unkeyable.append(serialized)
    return {
        "artifact_id": artifact_id,
        "path": str(path),
        "raw_subject_count": len(subjects),
        "keyable_subject_count": len(keyable),
        "unkeyable_subject_count": len(unkeyable),
        "claim_ground_keys": sorted(claim_ground_keys),
        "keyable_subjects": sorted(keyable, key=lambda item: item["subject"]),
        "unkeyable_subjects": sorted(unkeyable, key=lambda item: item["subject"]),
    }


def _claim_ground_key(args: list[str]) -> str:
    _subject, ground, reference, status = args
    return "|".join(
        [
            _governed_ground_atom(ground),
            _governed_reference_atom(reference),
            str(status).strip(),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
