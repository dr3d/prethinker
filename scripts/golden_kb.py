#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

VARIABLE_RE = re.compile(r"\b[A-Z_][A-Za-z0-9_]*\b")
QUOTE_RE = re.compile(r"'[^']*'")


def _resolve(path_text: str) -> Path:
    p = Path(path_text)
    return p.resolve() if p.is_absolute() else (ROOT / p).resolve()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _strip_line_comments(text: str) -> str:
    out_lines: list[str] = []
    for raw in text.splitlines():
        line = raw
        in_quote = False
        kept: list[str] = []
        for i, ch in enumerate(line):
            if ch == "'":
                in_quote = not in_quote
                kept.append(ch)
                continue
            if ch == "%" and not in_quote:
                break
            kept.append(ch)
        out_lines.append("".join(kept))
    return "\n".join(out_lines)


def _iter_clauses(text: str) -> list[str]:
    cleaned = _strip_line_comments(text)
    clauses: list[str] = []
    cur: list[str] = []
    paren = 0
    bracket = 0
    in_quote = False
    for ch in cleaned:
        cur.append(ch)
        if ch == "'":
            in_quote = not in_quote
            continue
        if in_quote:
            continue
        if ch == "(":
            paren += 1
            continue
        if ch == ")":
            paren = max(0, paren - 1)
            continue
        if ch == "[":
            bracket += 1
            continue
        if ch == "]":
            bracket = max(0, bracket - 1)
            continue
        if ch == "." and paren == 0 and bracket == 0:
            raw = "".join(cur).strip()
            cur = []
            if not raw:
                continue
            raw = raw[:-1].strip() if raw.endswith(".") else raw
            if raw:
                clauses.append(raw)
    tail = "".join(cur).strip()
    if tail:
        clauses.append(tail)
    return clauses


def _normalize_whitespace(clause: str) -> str:
    c = " ".join(clause.split())
    c = re.sub(r"\s*\(\s*", "(", c)
    c = re.sub(r"\s*\)\s*", ")", c)
    c = re.sub(r"\s*,\s*", ", ", c)
    c = re.sub(r"\s*:-\s*", " :- ", c)
    c = re.sub(r"\s+", " ", c).strip()
    return c


def _normalize_vars_segment(segment: str, mapping: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        token = match.group(0)
        if token == "_":
            return "_"
        mapped = mapping.get(token)
        if mapped:
            return mapped
        mapped = f"V{len(mapping) + 1}"
        mapping[token] = mapped
        return mapped

    return VARIABLE_RE.sub(repl, segment)


def _normalize_variable_names(clause: str) -> str:
    mapping: dict[str, str] = {}
    out: list[str] = []
    last = 0
    for m in QUOTE_RE.finditer(clause):
        out.append(_normalize_vars_segment(clause[last : m.start()], mapping))
        out.append(m.group(0))
        last = m.end()
    out.append(_normalize_vars_segment(clause[last:], mapping))
    return "".join(out)


def canonicalize_clause(raw_clause: str) -> str:
    c = raw_clause.strip()
    if not c:
        return ""
    c = _normalize_whitespace(c)
    c = _normalize_variable_names(c)
    c = _normalize_whitespace(c)
    if not c.endswith("."):
        c += "."
    return c


def canonicalize_clauses(clauses: list[str]) -> list[str]:
    normalized = {canonicalize_clause(item) for item in clauses if canonicalize_clause(item)}
    return sorted(normalized)


def load_canonical_clauses(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"KB file not found: {path}")
    text = path.read_text(encoding="utf-8-sig")
    clauses = _iter_clauses(text)
    return canonicalize_clauses(clauses)


def write_canonical_file(path: Path, clauses: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(clauses)
    if body:
        body += "\n"
    path.write_text(body, encoding="utf-8")


def compare_kbs(golden_path: Path, candidate_path: Path) -> dict[str, Any]:
    golden = load_canonical_clauses(golden_path)
    candidate = load_canonical_clauses(candidate_path)
    golden_set = set(golden)
    candidate_set = set(candidate)

    missing = sorted(golden_set - candidate_set)
    extra = sorted(candidate_set - golden_set)
    matched = sorted(golden_set & candidate_set)

    golden_text = "\n".join(golden) + ("\n" if golden else "")
    candidate_text = "\n".join(candidate) + ("\n" if candidate else "")

    return {
        "match": len(missing) == 0 and len(extra) == 0,
        "golden_clause_count": len(golden),
        "candidate_clause_count": len(candidate),
        "matched_clause_count": len(matched),
        "missing_clause_count": len(missing),
        "extra_clause_count": len(extra),
        "missing_clauses": missing,
        "extra_clauses": extra,
        "golden_sha256": _sha256_text(golden_text),
        "candidate_sha256": _sha256_text(candidate_text),
    }


def _load_report(report_path: Path) -> dict[str, Any]:
    if not report_path.exists():
        raise FileNotFoundError(f"Run report not found: {report_path}")
    payload = json.loads(report_path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("Run report payload is not a JSON object.")
    return payload


def _freeze_from_report(report_path: Path, output_path: Path, source_kb_path: Path | None) -> dict[str, Any]:
    report = _load_report(report_path)
    kb_namespace = report.get("kb_namespace", {}) if isinstance(report.get("kb_namespace"), dict) else {}
    corpus_path_text = str(kb_namespace.get("corpus_path", "")).strip()
    resolved_source = source_kb_path or (Path(corpus_path_text).resolve() if corpus_path_text else None)
    if resolved_source is None:
        raise ValueError("Could not determine corpus path from report; use --source-kb.")
    clauses = load_canonical_clauses(resolved_source)
    write_canonical_file(output_path, clauses)
    return {
        "status": "ok",
        "report": str(report_path),
        "source_kb": str(resolved_source),
        "golden_kb": str(output_path),
        "clause_count": len(clauses),
        "golden_sha256": _sha256_text(("\n".join(clauses) + ("\n" if clauses else ""))),
        "prompt_id": (
            str(report.get("prompt_provenance", {}).get("prompt_id", ""))
            if isinstance(report.get("prompt_provenance"), dict)
            else ""
        ),
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
    }


def _run_kb_pipeline(command: list[str]) -> int:
    proc = subprocess.run(command, cwd=str(ROOT), check=False)
    return int(proc.returncode)


def _benchmark_once(
    *,
    scenario_path: Path,
    golden_kb_path: Path,
    backend: str,
    model: str,
    prompt_file: Path | None,
    base_url: str,
    context_length: int,
    clarification_eagerness: float,
    max_clarification_rounds: int,
    clarification_answer_model: str,
    clarification_answer_backend: str,
    clarification_answer_base_url: str,
    clarification_answer_context_length: int,
    force_empty_kb: bool,
    out_report: Path,
    kb_root: Path,
    prompt_history_dir: Path,
) -> dict[str, Any]:
    out_report.parent.mkdir(parents=True, exist_ok=True)
    kb_root.mkdir(parents=True, exist_ok=True)
    prompt_history_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "kb_pipeline.py",
        "--scenario",
        str(scenario_path),
        "--backend",
        backend,
        "--base-url",
        base_url,
        "--model",
        model,
        "--context-length",
        str(int(context_length)),
        "--runtime",
        "core",
        "--kb-root",
        str(kb_root),
        "--prompt-history-dir",
        str(prompt_history_dir),
        "--clarification-eagerness",
        str(float(clarification_eagerness)),
        "--max-clarification-rounds",
        str(int(max_clarification_rounds)),
        "--clarification-answer-model",
        clarification_answer_model,
        "--clarification-answer-backend",
        clarification_answer_backend,
        "--clarification-answer-base-url",
        clarification_answer_base_url,
        "--clarification-answer-context-length",
        str(int(clarification_answer_context_length)),
        "--out",
        str(out_report),
    ]
    if prompt_file:
        cmd.extend(["--prompt-file", str(prompt_file)])
    if force_empty_kb:
        cmd.append("--force-empty-kb")

    run_exit_code = _run_kb_pipeline(cmd)
    report = _load_report(out_report)
    kb_namespace = report.get("kb_namespace", {}) if isinstance(report.get("kb_namespace"), dict) else {}
    corpus_path_text = str(kb_namespace.get("corpus_path", "")).strip()
    candidate_kb_path = Path(corpus_path_text).resolve() if corpus_path_text else None

    compare: dict[str, Any]
    if candidate_kb_path and candidate_kb_path.exists():
        compare = compare_kbs(golden_kb_path, candidate_kb_path)
    else:
        compare = {
            "match": False,
            "golden_clause_count": len(load_canonical_clauses(golden_kb_path)),
            "candidate_clause_count": 0,
            "matched_clause_count": 0,
            "missing_clause_count": 0,
            "extra_clause_count": 0,
            "missing_clauses": [],
            "extra_clauses": [],
            "golden_sha256": "",
            "candidate_sha256": "",
            "error": "Candidate corpus path not found in report output.",
        }

    overall_status = str(report.get("overall_status", "unknown"))
    return {
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "scenario_path": str(scenario_path),
        "golden_kb_path": str(golden_kb_path),
        "candidate_kb_path": str(candidate_kb_path) if candidate_kb_path else "",
        "run_report_path": str(out_report),
        "run_exit_code": run_exit_code,
        "run_overall_status": overall_status,
        "kb_match": bool(compare.get("match", False)),
        "comparison": compare,
    }


def _parse_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("Manifest must be a JSON object.")
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Golden KB tooling for story->KB benchmarking.")
    sub = parser.add_subparsers(dest="command", required=True)

    freeze = sub.add_parser("freeze", help="Freeze a canonical golden KB from a rigorous run report.")
    freeze.add_argument("--report", required=True, help="Path to kb_pipeline run JSON report.")
    freeze.add_argument("--output", required=True, help="Output golden KB .pl path.")
    freeze.add_argument("--source-kb", default="", help="Optional explicit source kb.pl path.")
    freeze.add_argument("--meta-out", default="", help="Optional metadata JSON path.")

    compare = sub.add_parser("compare", help="Compare a candidate KB against golden KB.")
    compare.add_argument("--golden", required=True, help="Golden KB .pl path.")
    compare.add_argument("--candidate", required=True, help="Candidate KB .pl path.")
    compare.add_argument("--out", default="", help="Optional JSON diff output path.")

    bench = sub.add_parser("benchmark", help="Run scenario and compare generated KB to golden.")
    bench.add_argument("--scenario", required=True, help="Scenario JSON path.")
    bench.add_argument("--golden", required=True, help="Golden KB .pl path.")
    bench.add_argument("--backend", default="ollama")
    bench.add_argument("--base-url", default="http://127.0.0.1:11434")
    bench.add_argument("--model", default="qwen3.5:9b")
    bench.add_argument("--prompt-file", default="")
    bench.add_argument("--context-length", type=int, default=8192)
    bench.add_argument("--clarification-eagerness", type=float, default=0.0)
    bench.add_argument("--max-clarification-rounds", type=int, default=0)
    bench.add_argument("--clarification-answer-model", default="qwen3.5:9b")
    bench.add_argument("--clarification-answer-backend", default="ollama")
    bench.add_argument("--clarification-answer-base-url", default="http://127.0.0.1:11434")
    bench.add_argument("--clarification-answer-context-length", type=int, default=16384)
    bench.add_argument("--force-empty-kb", action="store_true", help="Always clear KB before benchmark run.")
    bench.add_argument("--kb-root", default="tmp/golden_bench/kb_store")
    bench.add_argument("--prompt-history-dir", default="tmp/golden_bench/prompt_history")
    bench.add_argument("--out-report", default="", help="Optional run report output path.")
    bench.add_argument("--out-summary", default="", help="Optional benchmark summary JSON path.")

    manifest = sub.add_parser("benchmark-manifest", help="Run benchmark across every manifest entry.")
    manifest.add_argument("--manifest", default="goldens/manifest.json")
    manifest.add_argument("--backend", default="")
    manifest.add_argument("--base-url", default="")
    manifest.add_argument("--model", default="")
    manifest.add_argument("--prompt-file", default="")
    manifest.add_argument("--context-length", type=int, default=0)
    manifest.add_argument("--clarification-eagerness", type=float, default=-1.0)
    manifest.add_argument("--max-clarification-rounds", type=int, default=-1)
    manifest.add_argument("--clarification-answer-model", default="")
    manifest.add_argument("--clarification-answer-backend", default="")
    manifest.add_argument("--clarification-answer-base-url", default="")
    manifest.add_argument("--clarification-answer-context-length", type=int, default=0)
    manifest.add_argument("--force-empty-kb", action="store_true", help="Always clear KB before each manifest benchmark entry.")
    manifest.add_argument("--kb-root", default="tmp/golden_bench_manifest/kb_store")
    manifest.add_argument("--prompt-history-dir", default="tmp/golden_bench_manifest/prompt_history")
    manifest.add_argument("--out-dir", default="tmp/golden_bench_manifest")
    manifest.add_argument("--out-summary", default="")

    return parser


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _run_manifest(args: argparse.Namespace) -> int:
    manifest_path = _resolve(args.manifest)
    payload = _parse_manifest(manifest_path)
    defaults = payload.get("defaults", {}) if isinstance(payload.get("defaults"), dict) else {}
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("Manifest entries must be a list.")

    out_dir = _resolve(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for idx, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            continue
        sid = str(entry.get("id", f"entry_{idx:03d}")).strip() or f"entry_{idx:03d}"
        scenario = _resolve(str(entry.get("scenario_path", "")).strip())
        golden = _resolve(str(entry.get("golden_kb_path", "")).strip())
        if not scenario.exists() or not golden.exists():
            rows.append(
                {
                    "id": sid,
                    "status": "error",
                    "error": "scenario or golden path missing",
                    "scenario_path": str(scenario),
                    "golden_kb_path": str(golden),
                }
            )
            continue

        backend = args.backend or str(entry.get("backend", defaults.get("backend", "ollama")))
        base_url = args.base_url or str(entry.get("base_url", defaults.get("base_url", "http://127.0.0.1:11434")))
        model = args.model or str(entry.get("model", defaults.get("model", "qwen3.5:9b")))
        prompt_file_text = args.prompt_file or str(entry.get("prompt_file", defaults.get("prompt_file", "")))
        prompt_file = _resolve(prompt_file_text) if prompt_file_text.strip() else None

        context_length = int(
            args.context_length
            if args.context_length > 0
            else entry.get("context_length", defaults.get("context_length", 8192))
        )
        clarification_eagerness = float(
            args.clarification_eagerness
            if args.clarification_eagerness >= 0.0
            else entry.get("clarification_eagerness", defaults.get("clarification_eagerness", 0.0))
        )
        max_clarification_rounds = int(
            args.max_clarification_rounds
            if args.max_clarification_rounds >= 0
            else entry.get("max_clarification_rounds", defaults.get("max_clarification_rounds", 0))
        )
        ca_model = args.clarification_answer_model or str(
            entry.get("clarification_answer_model", defaults.get("clarification_answer_model", "qwen3.5:9b"))
        )
        ca_backend = args.clarification_answer_backend or str(
            entry.get("clarification_answer_backend", defaults.get("clarification_answer_backend", "ollama"))
        )
        ca_base = args.clarification_answer_base_url or str(
            entry.get("clarification_answer_base_url", defaults.get("clarification_answer_base_url", "http://127.0.0.1:11434"))
        )
        ca_ctx = int(
            args.clarification_answer_context_length
            if args.clarification_answer_context_length > 0
            else entry.get("clarification_answer_context_length", defaults.get("clarification_answer_context_length", 16384))
        )
        force_empty_kb = bool(
            args.force_empty_kb
            or entry.get("force_empty_kb", defaults.get("force_empty_kb", True))
        )

        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_report = out_dir / f"{sid}_{stamp}.json"

        row = _benchmark_once(
            scenario_path=scenario,
            golden_kb_path=golden,
            backend=backend,
            model=model,
            prompt_file=prompt_file,
            base_url=base_url,
            context_length=context_length,
            clarification_eagerness=clarification_eagerness,
            max_clarification_rounds=max_clarification_rounds,
            clarification_answer_model=ca_model,
            clarification_answer_backend=ca_backend,
            clarification_answer_base_url=ca_base,
            clarification_answer_context_length=ca_ctx,
            force_empty_kb=force_empty_kb,
            out_report=out_report,
            kb_root=_resolve(args.kb_root),
            prompt_history_dir=_resolve(args.prompt_history_dir),
        )
        row["id"] = sid
        rows.append(row)
        print(
            f"[{sid}] run_status={row['run_overall_status']} kb_match={row['kb_match']} "
            f"missing={row['comparison'].get('missing_clause_count', 0)} extra={row['comparison'].get('extra_clause_count', 0)}"
        )

    passed = sum(
        1
        for item in rows
        if isinstance(item, dict)
        and item.get("run_overall_status") == "passed"
        and bool(item.get("kb_match"))
    )
    total = len(rows)
    summary = {
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "manifest_path": str(manifest_path),
        "total_entries": total,
        "passed_entries": passed,
        "pass_rate": round((passed / total), 3) if total else 0.0,
        "results": rows,
    }

    out_summary = _resolve(args.out_summary) if str(args.out_summary).strip() else (out_dir / "summary.json")
    _write_json(out_summary, summary)
    print(f"Wrote {out_summary}")
    return 0 if passed == total else 2


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "freeze":
        report_path = _resolve(args.report)
        output_path = _resolve(args.output)
        source_kb = _resolve(args.source_kb) if str(args.source_kb).strip() else None
        result = _freeze_from_report(report_path, output_path, source_kb)
        if str(args.meta_out).strip():
            _write_json(_resolve(args.meta_out), result)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "compare":
        golden = _resolve(args.golden)
        candidate = _resolve(args.candidate)
        diff = compare_kbs(golden, candidate)
        payload = {
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
            "golden": str(golden),
            "candidate": str(candidate),
            "comparison": diff,
        }
        if str(args.out).strip():
            _write_json(_resolve(args.out), payload)
        print(json.dumps(payload, indent=2))
        return 0 if bool(diff.get("match")) else 2

    if args.command == "benchmark":
        scenario = _resolve(args.scenario)
        golden = _resolve(args.golden)
        prompt_file = _resolve(args.prompt_file) if str(args.prompt_file).strip() else None
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_report = (
            _resolve(args.out_report)
            if str(args.out_report).strip()
            else _resolve(f"tmp/golden_bench/run_{scenario.stem}_{stamp}.json")
        )
        result = _benchmark_once(
            scenario_path=scenario,
            golden_kb_path=golden,
            backend=str(args.backend),
            model=str(args.model),
            prompt_file=prompt_file,
            base_url=str(args.base_url),
            context_length=int(args.context_length),
            clarification_eagerness=float(args.clarification_eagerness),
            max_clarification_rounds=int(args.max_clarification_rounds),
            clarification_answer_model=str(args.clarification_answer_model),
            clarification_answer_backend=str(args.clarification_answer_backend),
            clarification_answer_base_url=str(args.clarification_answer_base_url),
            clarification_answer_context_length=int(args.clarification_answer_context_length),
            force_empty_kb=bool(args.force_empty_kb),
            out_report=out_report,
            kb_root=_resolve(args.kb_root),
            prompt_history_dir=_resolve(args.prompt_history_dir),
        )
        if str(args.out_summary).strip():
            _write_json(_resolve(args.out_summary), result)
        print(json.dumps(result, indent=2))
        return 0 if result["run_overall_status"] == "passed" and result["kb_match"] else 2

    if args.command == "benchmark-manifest":
        return _run_manifest(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
