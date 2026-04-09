#!/usr/bin/env python3
"""
Render kb_pipeline run reports into themed chat-style HTML transcripts.

This wraps the shared dialog renderer (ported from prolog-reasoning) by:
1) converting kb_run JSON report -> renderer-compatible "steps" payload
2) invoking scripts/render_dialog_json_html.py with selected theme
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RENDERER = ROOT / "scripts" / "render_dialog_json_html.py"


def _coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, indent=2, ensure_ascii=False)


def _safe_stem_label(path: Path) -> str:
    return path.stem.replace("_", " ").strip() or "run"


def _heuristic_route(text: str) -> str:
    lowered = text.strip().lower()
    if re.search(r"\b(retract|remove|delete|undo|correction|actually)\b", lowered):
        return "retract"
    if re.search(r"\b(if|whenever|then)\b", lowered):
        return "assert_rule"
    if lowered.endswith("?") or re.search(r"^\s*(who|what|where|when|why|how)\b", lowered):
        return "query"
    if re.search(r"\b(translate|summarize|rewrite|format|explain)\b", lowered):
        return "other"
    return "assert_fact"


def _route_rationale(route: str) -> str:
    if route == "assert_fact":
        return "Seed grounded terms/constants as facts for later inference."
    if route == "assert_rule":
        return "Introduce an inference rule so downstream queries can derive new truths."
    if route == "query":
        return "Probe current KB state and variable bindings."
    if route == "retract":
        return "Revise KB by retracting prior assertions and testing correction behavior."
    return "Out-of-scope turn used to verify parser abstains from KB mutation."


def _load_scenario_payload(report: dict[str, Any], source: Path) -> dict[str, Any] | None:
    raw = str(report.get("scenario_path", "")).strip()
    candidate_paths: list[Path] = []
    if raw:
        candidate_paths.append(Path(raw))
    candidate_paths.append(source)
    for candidate in candidate_paths:
        if candidate.is_file():
            try:
                parsed = json.loads(candidate.read_text(encoding="utf-8-sig"))
            except Exception:
                continue
            if isinstance(parsed, dict) and isinstance(parsed.get("utterances"), list):
                return parsed
    return None


def _normalized_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _collect_kb_elements(parsed: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(parsed, dict):
        return {
            "intent": "unknown",
            "logic_string": "",
            "facts": [],
            "rules": [],
            "queries": [],
            "atoms": [],
            "variables": [],
            "predicates": [],
        }
    components = parsed.get("components", {})
    if not isinstance(components, dict):
        components = {}
    return {
        "intent": str(parsed.get("intent", "unknown")),
        "logic_string": str(parsed.get("logic_string", "")),
        "facts": parsed.get("facts", []) if isinstance(parsed.get("facts"), list) else [],
        "rules": parsed.get("rules", []) if isinstance(parsed.get("rules"), list) else [],
        "queries": parsed.get("queries", []) if isinstance(parsed.get("queries"), list) else [],
        "uncertainty_score": parsed.get("uncertainty_score"),
        "uncertainty_label": parsed.get("uncertainty_label"),
        "needs_clarification": parsed.get("needs_clarification"),
        "clarification_question": parsed.get("clarification_question"),
        "clarification_reason": parsed.get("clarification_reason"),
        "atoms": components.get("atoms", []) if isinstance(components.get("atoms"), list) else [],
        "variables": components.get("variables", []) if isinstance(components.get("variables"), list) else [],
        "predicates": components.get("predicates", []) if isinstance(components.get("predicates"), list) else [],
    }


def _coerce_utterance_text(raw: Any) -> str:
    if isinstance(raw, str):
        return raw
    if isinstance(raw, dict):
        return str(raw.get("utterance", "") or raw.get("text", "") or raw.get("input", ""))
    return str(raw)


def _summarize_kb_action(
    *,
    apply_tool: str,
    apply_status: str,
    apply_input: Any,
    apply_result: dict[str, Any],
    kb_elements: dict[str, Any],
) -> str:
    input_text = _coerce_text(apply_input).strip()
    intent = str(kb_elements.get("intent", "unknown"))
    lines = [f"intent={intent} apply_tool={apply_tool} apply_status={apply_status}"]

    if apply_tool in {"assert_fact", "assert_rule"}:
        lines.append("effect=mutation(write)")
    elif apply_tool in {"retract_fact", "retract_rule"}:
        lines.append("effect=mutation(retract)")
    elif apply_tool in {"query_kb", "query"}:
        lines.append("effect=read(query)")
    else:
        lines.append("effect=none")

    if input_text:
        lines.append(f"submitted={input_text}")
    result_type = _coerce_text(apply_result.get("result_type")).strip()
    if result_type:
        lines.append(f"result_type={result_type}")
    for key in ("fact", "rule", "query", "message"):
        value = _coerce_text(apply_result.get(key)).strip()
        if value:
            lines.append(f"{key}={value}")
    return "\n".join(lines)


def _build_turn_step(
    turn: dict[str, Any],
    index: int,
    *,
    expected_utterance: str,
) -> dict[str, Any]:
    route = str(turn.get("route", "unknown"))
    apply_row = turn.get("apply", {})
    if not isinstance(apply_row, dict):
        apply_row = {}
    apply_result = apply_row.get("result", {})
    if not isinstance(apply_result, dict):
        apply_result = {"raw": apply_result}
    apply_status = str(turn.get("apply_status", apply_result.get("status", "unknown")))
    apply_tool = str(apply_row.get("tool", "none"))
    parsed = turn.get("parsed")
    kb_elements = _collect_kb_elements(parsed if isinstance(parsed, dict) else None)
    observed_utterance = str(turn.get("utterance", ""))
    expected_route = _heuristic_route(expected_utterance) if expected_utterance else _heuristic_route(observed_utterance)
    parse_ok = 1.0 if not turn.get("validation_errors") else 0.0
    route_ok = 1.0 if route == expected_route else 0.0
    apply_ok = 1.0 if apply_status in {"success", "skipped", "no_results", "clarification_requested"} else 0.0
    utterance_ok = (
        1.0
        if (not expected_utterance or _normalized_text(expected_utterance) == _normalized_text(observed_utterance))
        else 0.0
    )
    turn_score = round((parse_ok + route_ok + apply_ok + utterance_ok) / 4.0, 3)
    kb_action_summary = _summarize_kb_action(
        apply_tool=apply_tool,
        apply_status=apply_status,
        apply_input=apply_row.get("input"),
        apply_result=apply_result,
        kb_elements=kb_elements,
    )

    assistant_payload = {
        "expected_utterance": expected_utterance or None,
        "observed_utterance": observed_utterance,
        "route": route,
        "expected_route": expected_route,
        "route_source": turn.get("route_source"),
        "repaired": bool(turn.get("repaired", False)),
        "fallback_used": bool(turn.get("fallback_used", False)),
        "parsed": parsed,
        "validation_errors": turn.get("validation_errors", []),
        "apply_status": apply_status,
        "utterance_ok": utterance_ok,
        "turn_score": turn_score,
        "clarification_rounds": turn.get("clarification_rounds", []),
        "clarification_pending": bool(turn.get("clarification_pending", False)),
        "clarification_question": turn.get("clarification_question"),
        "clarification_policy": turn.get("clarification_policy", {}),
    }

    tool_calls = [
        {
            "tool": f"kb_apply::{apply_tool}",
            "arguments": {
                "turn_index": index,
                "input": apply_row.get("input"),
            },
            "output": apply_result,
        }
    ]
    annotations = [
        {
            "kind": "info",
            "title": "Prethinker Annotation",
            "text": (
                f"Why asked: {_route_rationale(expected_route)}\n"
                f"Utterance expected/observed: {expected_utterance or '(none)'} / {observed_utterance}\n"
                f"Route expected/observed: {expected_route} / {route}\n"
                f"Parser path: source={turn.get('route_source')} repaired={bool(turn.get('repaired', False))} "
                f"fallback={bool(turn.get('fallback_used', False))}"
            ),
        },
        {
            "kind": "info",
            "title": "KB Action",
            "text": kb_action_summary,
        },
        {
            "kind": "info",
            "title": "KB Elements",
            "text": (
                f"intent={kb_elements['intent']}\n"
                f"logic={kb_elements['logic_string']}\n"
                f"facts={kb_elements['facts']}\n"
                f"rules={kb_elements['rules']}\n"
                f"queries={kb_elements['queries']}\n"
                f"uncertainty_score={kb_elements['uncertainty_score']} uncertainty_label={kb_elements['uncertainty_label']}\n"
                f"needs_clarification={kb_elements['needs_clarification']}\n"
                f"clarification_question={kb_elements['clarification_question']}\n"
                f"clarification_reason={kb_elements['clarification_reason']}\n"
                f"predicates={kb_elements['predicates']}\n"
                f"atoms={kb_elements['atoms']} variables={kb_elements['variables']}"
            ),
        },
        {
            "kind": "warning" if bool(turn.get("clarification_pending", False)) else "info",
            "title": "Clarification Policy",
            "text": (
                f"pending={bool(turn.get('clarification_pending', False))}\n"
                f"question={turn.get('clarification_question')}\n"
                f"rounds_used={turn.get('clarification_rounds_used', 0)} "
                f"max_rounds={turn.get('clarification_max_rounds', 0)}\n"
                f"policy={turn.get('clarification_policy', {})}"
            ),
        },
        {
            "kind": "score",
            "title": "Turn Score",
            "text": (
                f"score={turn_score} (parse_ok={parse_ok}, route_ok={route_ok}, apply_ok={apply_ok}, utterance_ok={utterance_ok})\n"
                f"apply_tool={apply_tool} apply_status={apply_status}"
            ),
        },
    ]

    return {
        "step": f"turn_{index:02d}: {route} [{apply_status}]",
        "prompt": _coerce_text(turn.get("utterance")).strip() or "(empty utterance)",
        "assistant_message": json.dumps(assistant_payload, indent=2, ensure_ascii=False),
        "tool_calls": tool_calls,
        "annotations": annotations,
    }


def _build_validation_step(report: dict[str, Any]) -> dict[str, Any]:
    validations = report.get("validations", [])
    if not isinstance(validations, list):
        validations = []

    summary = {
        "validation_total": report.get("validation_total", 0),
        "validation_passed": report.get("validation_passed", 0),
        "overall_status": report.get("overall_status", "unknown"),
        "turn_parse_failures": report.get("turn_parse_failures", 0),
        "turn_apply_failures": report.get("turn_apply_failures", 0),
    }

    tool_calls: list[dict[str, Any]] = []
    pass_count = 0
    annotation_lines: list[str] = []
    row_annotations: list[dict[str, str]] = []
    for idx, row in enumerate(validations, start=1):
        if not isinstance(row, dict):
            continue
        passed = bool(row.get("passed"))
        if passed:
            pass_count += 1
        reasons = row.get("reasons", [])
        if not isinstance(reasons, list):
            reasons = []
        annotation_lines.append(
            f"{row.get('id', f'validation_{idx:02d}')}: {'PASS' if passed else 'FAIL'} "
            f"(query={row.get('query')}, expected={row.get('expected_status')}, "
            f"observed={((row.get('result') or {}) if isinstance(row.get('result'), dict) else {}).get('status')})"
        )
        if reasons:
            annotation_lines.append("  reasons: " + "; ".join(str(item) for item in reasons))
        row_annotations.append(
            {
                "kind": "pass" if passed else "fail",
                "title": str(row.get("id", f"validation_{idx:02d}")),
                "text": (
                    f"query={row.get('query')}\n"
                    f"expected={row.get('expected_status')} observed={((row.get('result') or {}) if isinstance(row.get('result'), dict) else {}).get('status')}\n"
                    f"reasons={'; '.join(str(item) for item in reasons) if reasons else 'none'}"
                ),
            }
        )
        tool_calls.append(
            {
                "tool": "validation::query_rows",
                "arguments": {
                    "id": row.get("id", f"validation_{idx:02d}"),
                    "query": row.get("query"),
                    "expected_status": row.get("expected_status"),
                },
                "output": row.get("result"),
            }
        )
    validation_score = round(pass_count / len(validations), 3) if validations else 0.0

    return {
        "step": "validation_summary",
        "prompt": "Run deterministic KB validations and compare against expectations.",
        "assistant_message": json.dumps(summary, indent=2, ensure_ascii=False),
        "tool_calls": tool_calls,
        "annotations": [
            {
                "kind": "score",
                "title": "Validation Score",
                "text": f"score={validation_score} ({pass_count}/{len(validations)} passed)",
            },
            {
                "kind": "info",
                "title": "Validation Notes",
                "text": "\n".join(annotation_lines) if annotation_lines else "No validations captured.",
            },
        ]
        + row_annotations,
    }


def _build_run_context_step(report: dict[str, Any]) -> dict[str, Any]:
    prompt_provenance = report.get("prompt_provenance", {})
    if not isinstance(prompt_provenance, dict):
        prompt_provenance = {}
    summary = {
        "run_id": report.get("run_id"),
        "run_started_utc": report.get("run_started_utc"),
        "run_finished_utc": report.get("run_finished_utc"),
        "scenario": report.get("scenario"),
        "ontology_kb_name": report.get("ontology_kb_name"),
        "backend": report.get("backend"),
        "model": report.get("model"),
        "model_settings": report.get("model_settings", {}),
        "prompt_provenance": prompt_provenance,
    }
    prompt_preview = _coerce_text(prompt_provenance.get("preview")).strip() or "(none)"
    prompt_id = _coerce_text(prompt_provenance.get("prompt_id")).strip() or "(none)"
    prompt_sha = _coerce_text(prompt_provenance.get("prompt_sha256")).strip() or "(none)"
    snapshot_path = _coerce_text(prompt_provenance.get("snapshot_path")).strip() or "(none)"

    return {
        "step": "run_context",
        "prompt": "Capture run provenance and prompt/version settings for reproducibility.",
        "assistant_message": json.dumps(summary, indent=2, ensure_ascii=False),
        "tool_calls": [],
        "annotations": [
            {
                "kind": "info",
                "title": "Prompt Provenance",
                "text": (
                    f"prompt_id={prompt_id}\n"
                    f"prompt_sha256={prompt_sha}\n"
                    f"snapshot_path={snapshot_path}\n"
                    f"preview:\n{prompt_preview}"
                ),
            }
        ],
    }


def _convert_report_to_dialog_payload(report: dict[str, Any], source: Path) -> dict[str, Any]:
    scenario_payload = _load_scenario_payload(report, source=source)
    expected_utterances: list[str] = []
    if isinstance(scenario_payload, dict):
        utterances = scenario_payload.get("utterances", [])
        if isinstance(utterances, list):
            expected_utterances = [_coerce_utterance_text(item) for item in utterances]

    turns = report.get("turns", [])
    if not isinstance(turns, list):
        turns = []

    steps = [_build_run_context_step(report)]
    for idx, turn in enumerate(turns, start=1):
        if isinstance(turn, dict):
            expected_utterance = expected_utterances[idx - 1] if idx - 1 < len(expected_utterances) else ""
            steps.append(_build_turn_step(turn, idx, expected_utterance=expected_utterance))

    steps.append(_build_validation_step(report))

    scenario = str(report.get("scenario", _safe_stem_label(source)))
    kb_name = str(report.get("ontology_kb_name", "default"))
    title = f"Semantic Parser Run: {scenario} ({kb_name})"
    generated = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    return {
        "title": title,
        "captured_at": generated,
        "model": report.get("model", "unknown"),
        "integration": report.get("backend", "kb_pipeline"),
        "scenario": scenario,
        "ontology_kb_name": kb_name,
        "steps": steps,
    }


def _collect_sources(path: Path, pattern: str, recursive: bool) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        raise FileNotFoundError(f"Input path does not exist: {path}")
    if recursive:
        found = sorted(p for p in path.rglob(pattern) if p.is_file())
    else:
        found = sorted(p for p in path.glob(pattern) if p.is_file())
    return [p for p in found if not p.name.endswith(".dialog.json")]


def _resolve_output_path(
    source: Path,
    *,
    output_arg: str,
    source_root: Path | None,
) -> Path:
    if output_arg:
        out = Path(output_arg).resolve()
        if source_root is None and out.suffix.lower() == ".html":
            return out
        if source_root is not None:
            return (out / source.relative_to(source_root)).with_suffix(".html")
        return out / f"{source.stem}.html"
    if source_root is not None:
        return source.with_suffix(".html")
    return source.with_suffix(".html")


def _render_with_shared_renderer(
    *,
    renderer_path: Path,
    input_json_path: Path,
    output_html_path: Path,
    theme: str,
    title: str,
    docs_hub_link: str,
    repo_link: str,
) -> None:
    cmd = [
        sys.executable,
        str(renderer_path),
        "--input",
        str(input_json_path),
        "--output",
        str(output_html_path),
        "--theme",
        theme,
        "--title",
        title,
        "--docs-hub-link",
        docs_hub_link,
        "--repo-link",
        repo_link,
    ]
    subprocess.run(cmd, cwd=str(ROOT), check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render kb_pipeline run JSON into themed chat-style HTML.")
    parser.add_argument("--input", required=True, help="KB run JSON file or directory.")
    parser.add_argument("--output", default="", help="HTML output file (single input) or output directory.")
    parser.add_argument("--pattern", default="*.json", help="Glob pattern for directory input.")
    parser.add_argument("--recursive", action="store_true", help="Search directory input recursively.")
    parser.add_argument(
        "--theme",
        default="standard",
        choices=["standard", "telegram", "imessage"],
        help="Renderer skin (light/dark appearance toggle is built into HTML).",
    )
    parser.add_argument("--title", default="", help="Optional title override for single-file input.")
    parser.add_argument(
        "--renderer",
        default=str(DEFAULT_RENDERER),
        help="Path to shared dialog renderer script.",
    )
    parser.add_argument(
        "--docs-hub-link",
        default="/docs",
        help="Top-nav docs link inside rendered page.",
    )
    parser.add_argument(
        "--repo-link",
        default="./README.md",
        help="Top-nav repo link inside rendered page.",
    )
    parser.add_argument(
        "--keep-dialog-json",
        action="store_true",
        help="Keep converted intermediate JSON next to output HTML for inspection.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    renderer_path = Path(args.renderer).resolve()
    if not renderer_path.exists():
        raise FileNotFoundError(f"Renderer not found: {renderer_path}")

    sources = _collect_sources(input_path, pattern=args.pattern, recursive=args.recursive)
    if not sources:
        raise FileNotFoundError(f"No input reports found under: {input_path}")
    if len(sources) > 1 and args.title.strip():
        raise ValueError("--title is only supported for single-file input.")

    source_root = input_path if input_path.is_dir() else None
    for source in sources:
        report = json.loads(source.read_text(encoding="utf-8-sig"))
        dialog_payload = _convert_report_to_dialog_payload(report, source=source)
        output_html = _resolve_output_path(source, output_arg=args.output, source_root=source_root)
        output_html.parent.mkdir(parents=True, exist_ok=True)

        title = args.title.strip() if args.title.strip() else str(dialog_payload.get("title", source.stem))

        if args.keep_dialog_json:
            dialog_json_path = output_html.with_suffix(".dialog.json")
            dialog_json_path.write_text(json.dumps(dialog_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            temp_handle = tempfile.NamedTemporaryFile(prefix="dialog_", suffix=".json", delete=False)
            dialog_json_path = Path(temp_handle.name).resolve()
            temp_handle.close()
            dialog_json_path.write_text(json.dumps(dialog_payload, indent=2, ensure_ascii=False), encoding="utf-8")

        try:
            _render_with_shared_renderer(
                renderer_path=renderer_path,
                input_json_path=dialog_json_path,
                output_html_path=output_html,
                theme=args.theme,
                title=title,
                docs_hub_link=args.docs_hub_link,
                repo_link=args.repo_link,
            )
        finally:
            if not args.keep_dialog_json and dialog_json_path.exists():
                dialog_json_path.unlink()

        print(f"Wrote {output_html}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())



