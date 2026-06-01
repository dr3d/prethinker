#!/usr/bin/env python3
"""Run adversarial null controls against the reference judge.

The reference judge is allowed to see the human reference answer because it is a
scorer, not a query path. That still leaves a governance question: does it bless
weak or irrelevant evidence too easily?

This audit samples product-exact QA rows and rejudges two null variants:

- empty_evidence: the true reference answer with no query results.
- wrong_reference: the row's redacted typed evidence with a different reference
  answer from the same fixture.

Any exact verdict in either control is a blocker for score confidence.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.audit_redaction_replay import _iter_qa_files, _redacted_row  # noqa: E402
from scripts.run_domain_bootstrap_qa import SemanticIRCallConfig, judge_reference_answer  # noqa: E402
from src.model_path import openrouter_api_key  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="QA JSON files or directories containing QA JSON files.")
    parser.add_argument("--sample-per-fixture", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20260601)
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="https://openrouter.ai/api/v1")
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.82)
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--api-key", default=openrouter_api_key())
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--exit-zero", action="store_true", help="Report without failing. Do not use for gates.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    qa_files = sorted({file.resolve() for path in args.paths for file in _iter_qa_files(path)})
    config = SemanticIRCallConfig(
        backend="lmstudio",
        base_url=str(args.base_url),
        model=str(args.model),
        timeout=int(args.timeout),
        temperature=float(args.temperature),
        top_p=float(args.top_p),
        max_tokens=int(args.max_tokens),
        api_key=str(args.api_key or ""),
        think_enabled=False,
        reasoning_effort="none",
    )
    report = build_report(
        qa_files=qa_files,
        config=config,
        sample_per_fixture=max(1, int(args.sample_per_fixture)),
        seed=int(args.seed),
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    blocked = report["summary"]["exact_null_verdicts"] > 0
    return 0 if args.exit_zero or not blocked else 1


def build_report(
    *,
    qa_files: list[Path],
    config: SemanticIRCallConfig,
    sample_per_fixture: int,
    seed: int,
) -> dict[str, Any]:
    rng = random.Random(seed)
    rows_by_fixture: dict[str, list[dict[str, Any]]] = defaultdict(list)
    all_reference_rows_by_fixture: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for qa_file in qa_files:
        payload = json.loads(qa_file.read_text(encoding="utf-8"))
        fixture_hint = qa_file.parent.name
        for row in payload.get("rows", []) or []:
            if not isinstance(row, dict):
                continue
            fixture = str(row.get("fixture") or row.get("fixture_name") or fixture_hint)
            reference = str(row.get("reference_answer", "")).strip()
            if reference:
                all_reference_rows_by_fixture[fixture].append(row)
            verdict = str((row.get("reference_judge") or {}).get("verdict", "")).strip()
            if verdict == "exact" and reference:
                rows_by_fixture[fixture].append(row)

    sampled: list[tuple[str, dict[str, Any]]] = []
    for fixture, rows in sorted(rows_by_fixture.items()):
        rows = list(rows)
        rng.shuffle(rows)
        for row in rows[:sample_per_fixture]:
            sampled.append((fixture, row))

    controls: list[dict[str, Any]] = []
    unclassified_fields: set[str] = set()
    for fixture, row in sampled:
        row_id = str(row.get("id", "")).strip()
        reference = str(row.get("reference_answer", "")).strip()
        empty_row = {
            **row,
            "query_results": [],
            "reference_answer": reference,
        }
        empty_judge = judge_reference_answer(row=empty_row, config=config, sign_clean_strict=True)
        controls.append(
            _control_row(
                fixture=fixture,
                row_id=row_id,
                control="empty_evidence",
                reference_answer=reference,
                judge=empty_judge,
            )
        )

        wrong_reference = _wrong_reference_for_row(
            fixture_rows=all_reference_rows_by_fixture.get(fixture, []),
            row=row,
        )
        redacted_row, _redaction = _redacted_row(row, unclassified_fields=unclassified_fields)
        wrong_row = {
            **redacted_row,
            "reference_answer": wrong_reference,
        }
        wrong_judge = judge_reference_answer(row=wrong_row, config=config, sign_clean_strict=True)
        controls.append(
            _control_row(
                fixture=fixture,
                row_id=row_id,
                control="wrong_reference",
                reference_answer=wrong_reference,
                judge=wrong_judge,
            )
        )

    counts = Counter(str(row["verdict"]) for row in controls)
    exact_controls = [row for row in controls if row["verdict"] == "exact"]
    return {
        "schema_version": "reference_judge_null_control_audit_v1",
        "qa_file_count": len(qa_files),
        "sample_per_fixture": sample_per_fixture,
        "seed": seed,
        "summary": {
            "sampled_product_exact_rows": len(sampled),
            "control_judgments": len(controls),
            "exact_null_verdicts": len(exact_controls),
            "verdict_counts": dict(sorted(counts.items())),
            "unclassified_redaction_fields": sorted(unclassified_fields),
        },
        "exact_null_rows": exact_controls,
        "controls": controls,
    }


def _wrong_reference_for_row(*, fixture_rows: list[dict[str, Any]], row: dict[str, Any]) -> str:
    own_id = str(row.get("id", "")).strip()
    own_reference = str(row.get("reference_answer", "")).strip()
    for candidate in fixture_rows:
        candidate_id = str(candidate.get("id", "")).strip()
        candidate_reference = str(candidate.get("reference_answer", "")).strip()
        if candidate_id != own_id and candidate_reference and candidate_reference != own_reference:
            return candidate_reference
    return "__null_control_reference_should_not_be_supported__"


def _control_row(
    *,
    fixture: str,
    row_id: str,
    control: str,
    reference_answer: str,
    judge: dict[str, Any],
) -> dict[str, Any]:
    return {
        "fixture": fixture,
        "id": row_id,
        "control": control,
        "reference_answer": reference_answer,
        "verdict": str(judge.get("verdict", "")).strip() or "missing",
        "answer_supported": bool(judge.get("answer_supported")),
        "concise_answer": str(judge.get("concise_answer", "")).strip(),
        "issues": judge.get("issues", []),
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Reference Judge Null-Control Audit",
        "",
        f"- Schema: `{report['schema_version']}`",
        f"- QA files: `{report['qa_file_count']}`",
        f"- Sample per fixture: `{report['sample_per_fixture']}`",
        f"- Sampled product-exact rows: `{summary['sampled_product_exact_rows']}`",
        f"- Control judgments: `{summary['control_judgments']}`",
        f"- Exact null verdicts: `{summary['exact_null_verdicts']}`",
        f"- Verdict counts: `{summary['verdict_counts']}`",
    ]
    if summary["unclassified_redaction_fields"]:
        lines.extend(["", "## Unclassified Redaction Fields", ""])
        for field in summary["unclassified_redaction_fields"]:
            lines.append(f"- `{field}`")
    if report["exact_null_rows"]:
        lines.extend(["", "## Exact Null Rows", "", "| Fixture | Row | Control | Concise Answer |", "| --- | --- | --- | --- |"])
        for row in report["exact_null_rows"]:
            lines.append(
                f"| `{row['fixture']}` | `{row['id']}` | `{row['control']}` | {_md_cell(row['concise_answer'])} |"
            )
    lines.extend(["", "## Controls", "", "| Fixture | Row | Control | Verdict |", "| --- | --- | --- | --- |"])
    for row in report["controls"]:
        lines.append(f"| `{row['fixture']}` | `{row['id']}` | `{row['control']}` | `{row['verdict']}` |")
    return "\n".join(lines).rstrip() + "\n"


def _md_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())
