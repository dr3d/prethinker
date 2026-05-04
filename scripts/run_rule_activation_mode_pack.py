#!/usr/bin/env python3
"""Build a rule/evidence activation comparison pack from fixture run metrics.

This harness resolves named run ids from a fixture's committed
progress_metrics.jsonl, checks whether the referenced QA artifacts are present,
and, when possible, compares the modes and runs a selector over already-executed
query evidence.

It does not read source prose, gold KBs, answer keys outside the QA artifacts,
or strategy files. Python only resolves structured artifact paths, packages
existing query evidence, and computes after-the-fact metrics.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "rule_activation_mode_packs"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.compare_qa_mode_artifacts import build_report as build_comparison_report  # noqa: E402
from scripts.compare_qa_mode_artifacts import render_markdown as render_comparison_markdown  # noqa: E402
from scripts.select_qa_mode_without_oracle import (  # noqa: E402
    build_rows,
    call_selector,
    hybrid_selector,
    render_markdown as render_selector_markdown,
    score_selection,
    structural_selector,
    summarize as summarize_selector_rows,
)


DEFAULT_ARTIFACT_KEYS = [
    "local_artifacts.qa_json",
    "qa.artifact",
    "union_qa.artifact",
    "focused_context_qa_json",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-dir", type=Path, required=True)
    parser.add_argument(
        "--mode",
        action="append",
        required=True,
        help=(
            "Mode spec label=RUN_ID or label=RUN_ID:artifact.path. "
            "Examples: baseline=SC-001, rule_union=SC-007:qa.artifact"
        ),
    )
    parser.add_argument("--group-name", default="")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument(
        "--selector-policy",
        choices=["none", "structural", "hybrid", "direct", "completeness", "relevance", "activation"],
        default="structural",
    )
    parser.add_argument("--hybrid-llm-policy", choices=["direct", "completeness", "relevance", "activation"], default="direct")
    parser.add_argument("--hybrid-margin", type=float, default=1.5)
    parser.add_argument("--hybrid-min-score", type=float, default=3.0)
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234/v1")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument("--sample-row-limit", type=int, default=12)
    parser.add_argument("--include-self-check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixture_dir = args.fixture_dir if args.fixture_dir.is_absolute() else (REPO_ROOT / args.fixture_dir).resolve()
    group_name = str(args.group_name or fixture_dir.name)
    runs = _runs_by_id(fixture_dir / "progress_metrics.jsonl")
    modes = [_resolve_mode_spec(spec, runs=runs) for spec in args.mode]
    missing = [mode for mode in modes if not bool(mode.get("artifact_exists"))]
    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(group_name)

    manifest: dict[str, Any] = {
        "schema_version": "rule_activation_mode_pack_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fixture_dir": _display_path(fixture_dir),
        "group_name": group_name,
        "selector_policy": str(args.selector_policy),
        "status": "missing_artifacts" if missing else "ready",
        "policy": [
            "Reads progress_metrics.jsonl and existing QA artifacts only.",
            "Does not read source prose, gold KBs, oracle strategy files, or answer-shaped profile material.",
            "Does not rerun compilation, query planning, judging, or failure classification.",
            "Selector choices are over existing query evidence modes and have no write authority.",
        ],
        "modes": modes,
        "missing_artifacts": missing,
        "outputs": {},
    }

    if not missing:
        group = {
            "name": group_name,
            "artifacts": [
                {
                    "label": str(mode["label"]),
                    "path": Path(str(mode["artifact_path_abs"])),
                    "record": json.loads(Path(str(mode["artifact_path_abs"])).read_text(encoding="utf-8-sig")),
                }
                for mode in modes
            ],
        }
        comparison = build_comparison_report([group])
        comparison_json = out_dir / f"{slug}_mode_comparison.json"
        comparison_md = out_dir / f"{slug}_mode_comparison.md"
        comparison_json.write_text(json.dumps(comparison, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        comparison_md.write_text(render_comparison_markdown(comparison), encoding="utf-8")
        manifest["outputs"]["comparison_json"] = _display_path(comparison_json)
        manifest["outputs"]["comparison_md"] = _display_path(comparison_md)

        if str(args.selector_policy) != "none":
            selector = _run_selector_report(
                group={
                    "name": group_name,
                    "labels": [str(mode["label"]) for mode in modes],
                    "artifacts": group["artifacts"],
                },
                args=args,
            )
            selector_json = out_dir / f"{slug}_selector_{args.selector_policy}.json"
            selector_md = out_dir / f"{slug}_selector_{args.selector_policy}.md"
            selector_json.write_text(json.dumps(selector, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            selector_md.write_text(render_selector_markdown(selector), encoding="utf-8")
            manifest["outputs"]["selector_json"] = _display_path(selector_json)
            manifest["outputs"]["selector_md"] = _display_path(selector_md)
            manifest["selector_summary"] = selector.get("summary", {})

    manifest_json = out_dir / f"{slug}_activation_pack.json"
    manifest_md = out_dir / f"{slug}_activation_pack.md"
    manifest_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    manifest_md.write_text(_render_manifest_markdown(manifest), encoding="utf-8")
    print(f"Wrote {manifest_json}")
    print(f"Wrote {manifest_md}")
    for key, path in manifest.get("outputs", {}).items():
        print(f"{key}: {path}")
    print(json.dumps({"status": manifest["status"], "missing_artifacts": len(missing)}, sort_keys=True))
    return 0 if not missing else 2


def _run_selector_report(*, group: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    rows = build_rows(
        group,
        sample_row_limit=int(args.sample_row_limit),
        include_self_check=bool(args.include_self_check),
    )
    outputs: list[dict[str, Any]] = []
    for row in rows:
        error = ""
        selection: dict[str, Any]
        policy = str(args.selector_policy)
        if policy == "structural":
            selection = structural_selector(row=row, mode_labels=group["labels"])
        elif policy == "hybrid":
            selection = hybrid_selector(
                row=row,
                mode_labels=group["labels"],
                margin=float(args.hybrid_margin),
                min_score=float(args.hybrid_min_score),
                fallback_selector=lambda *, row, mode_labels: call_selector(
                    base_url=str(args.base_url),
                    model=str(args.model),
                    timeout=int(args.timeout),
                    temperature=float(args.temperature),
                    top_p=float(args.top_p),
                    max_tokens=int(args.max_tokens),
                    row=row,
                    mode_labels=mode_labels,
                    selection_policy=str(args.hybrid_llm_policy),
                ),
            )
        else:
            try:
                selection = call_selector(
                    base_url=str(args.base_url),
                    model=str(args.model),
                    timeout=int(args.timeout),
                    temperature=float(args.temperature),
                    top_p=float(args.top_p),
                    max_tokens=int(args.max_tokens),
                    row=row,
                    mode_labels=group["labels"],
                    selection_policy=policy,
                )
            except Exception as exc:  # pragma: no cover - live harness path
                error = str(exc)
                selection = {}
        outputs.append(score_selection(row=row, selection=selection, error=error))
    return {
        "schema_version": "qa_mode_selector_run_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Selector input excludes source prose, reference answers, judge labels, oracle fields, and failure-surface labels.",
            "Selector chooses among already-executed query evidence modes only.",
            "Python packages structured query evidence and computes after-the-fact metrics; it does not interpret source language.",
        ],
        "group": {
            "name": group["name"],
            "labels": group["labels"],
            "artifacts": [{"label": item["label"], "path": _display_path(item["path"])} for item in group["artifacts"]],
        },
        "selection_policy": str(args.selector_policy),
        "hybrid_llm_policy": str(args.hybrid_llm_policy),
        "hybrid_margin": float(args.hybrid_margin),
        "hybrid_min_score": float(args.hybrid_min_score),
        "include_self_check": bool(args.include_self_check),
        "summary": summarize_selector_rows(outputs),
        "rows": outputs,
    }


def _resolve_mode_spec(spec: str, *, runs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    label, sep, rest = str(spec).partition("=")
    if not sep or not label.strip() or not rest.strip():
        raise SystemExit(f"invalid --mode {spec!r}")
    run_id, _, key = rest.partition(":")
    run = runs.get(run_id.strip())
    if not run:
        raise SystemExit(f"unknown run id in --mode {spec!r}")
    artifact_key = key.strip()
    artifact_value = _nested_get(run, artifact_key) if artifact_key else _first_artifact(run, DEFAULT_ARTIFACT_KEYS)
    artifact_path = _resolve_repo_path(str(artifact_value or ""))
    return {
        "label": label.strip(),
        "run_id": run_id.strip(),
        "run_mode": run.get("mode", ""),
        "evidence_lane": run.get("evidence_lane", ""),
        "artifact_key": artifact_key or "auto",
        "artifact_path": _display_path(artifact_path) if artifact_path else "",
        "artifact_path_abs": str(artifact_path) if artifact_path else "",
        "artifact_exists": bool(artifact_path and artifact_path.exists()),
        "qa_summary": run.get("qa", {}) if isinstance(run.get("qa"), dict) else {},
        "selector_summary": run.get("selector", {}) if isinstance(run.get("selector"), dict) else {},
    }


def _runs_by_id(metrics_path: Path) -> dict[str, dict[str, Any]]:
    if not metrics_path.exists():
        raise SystemExit(f"missing progress metrics: {metrics_path}")
    runs: dict[str, dict[str, Any]] = {}
    for line in metrics_path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if isinstance(row, dict) and str(row.get("run_id", "")).strip():
            runs[str(row["run_id"]).strip()] = row
    return runs


def _first_artifact(run: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        value = _nested_get(run, key)
        if value:
            return value
    return ""


def _nested_get(value: dict[str, Any], dotted_key: str) -> Any:
    current: Any = value
    for part in str(dotted_key or "").split("."):
        if not part:
            continue
        if not isinstance(current, dict):
            return ""
        current = current.get(part, "")
    return current


def _resolve_repo_path(value: str) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _display_path(value: Path | str | None) -> str:
    if value is None:
        return ""
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


def _render_manifest_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# Rule Activation Mode Pack",
        "",
        f"Generated: {manifest.get('generated_at', '')}",
        "",
        f"- Fixture: `{manifest.get('fixture_dir', '')}`",
        f"- Group: `{manifest.get('group_name', '')}`",
        f"- Status: `{manifest.get('status', '')}`",
        f"- Selector policy: `{manifest.get('selector_policy', '')}`",
        "",
        "## Modes",
        "",
        "| Label | Run | Lane | Artifact | Present | Exact / Partial / Miss |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for mode in manifest.get("modes", []):
        qa = mode.get("qa_summary", {}) if isinstance(mode.get("qa_summary"), dict) else {}
        lines.append(
            f"| `{mode.get('label', '')}` | `{mode.get('run_id', '')}` | `{mode.get('evidence_lane', '')}` | `{mode.get('artifact_path', '')}` | `{mode.get('artifact_exists', False)}` | {qa.get('judge_exact', '')} / {qa.get('judge_partial', '')} / {qa.get('judge_miss', '')} |"
        )
    outputs = manifest.get("outputs", {}) if isinstance(manifest.get("outputs"), dict) else {}
    if outputs:
        lines.extend(["", "## Outputs", ""])
        for key, path in outputs.items():
            lines.append(f"- `{key}`: `{path}`")
    missing = manifest.get("missing_artifacts", []) if isinstance(manifest.get("missing_artifacts"), list) else []
    if missing:
        lines.extend(["", "## Missing Artifacts", ""])
        for mode in missing:
            lines.append(f"- `{mode.get('label', '')}` from `{mode.get('run_id', '')}` expects `{mode.get('artifact_path', '')}`")
    lines.append("")
    return "\n".join(lines)


def _slug(value: str) -> str:
    out = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(value or "").strip())
    out = "-".join(part for part in out.split("-") if part)
    return out[:80] or "rule-activation"


if __name__ == "__main__":
    raise SystemExit(main())
