#!/usr/bin/env python3
"""
Run raw story ingestion directly from a text/markdown file.

This is the production-like path where Prethinker receives raw prose as-is.
By default this tool does not normalize, clean, or rewrite source text.
It wraps raw source text into a scenario, runs kb_pipeline, and optionally
runs kb_interrogator.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "kb_pipeline.py"
INTERROGATOR = ROOT / "scripts" / "kb_interrogator.py"


def _slug(text: str, *, max_len: int = 72) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text or ""))
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    cleaned = cleaned.strip("_") or "story"
    return cleaned[:max_len].strip("_") or "story"


def _read_story_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _to_utterances(raw_text: str, *, split_mode: str) -> list[str]:
    source = str(raw_text or "")
    if split_mode == "full":
        return [source] if source.strip() else []
    if split_mode == "paragraph":
        blocks = source.replace("\r\n", "\n").replace("\r", "\n").split("\n\n")
        return [b for b in blocks if b.strip()]
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return [ln for ln in lines if ln.strip()]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run(cmd: list[str]) -> int:
    proc = subprocess.run(cmd, cwd=str(ROOT))
    return int(proc.returncode)


def _resolve_kb_path(report: dict[str, Any], kb_name: str) -> Path:
    ns = report.get("kb_namespace")
    if isinstance(ns, dict):
        corpus_path = ns.get("corpus_path")
        if isinstance(corpus_path, str) and corpus_path.strip():
            path = Path(corpus_path.strip())
            return path if path.is_absolute() else (ROOT / path).resolve()
        kb_dir = ns.get("kb_dir")
        if isinstance(kb_dir, str) and kb_dir.strip():
            base = Path(kb_dir.strip())
            base = base if base.is_absolute() else (ROOT / base).resolve()
            return base / "kb.pl"
    ontology_kb_name = report.get("ontology_kb_name")
    if isinstance(ontology_kb_name, str) and ontology_kb_name.strip():
        return ROOT / "kb_store" / ontology_kb_name.strip() / "kb.pl"
    return ROOT / "kb_store" / kb_name / "kb.pl"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run raw story ingestion through kb_pipeline.")
    parser.add_argument("--story-file", required=True, help="Raw story text/markdown path.")
    parser.add_argument("--scenario-name", default="", help="Optional scenario/ontology name override.")
    parser.add_argument(
        "--scenario-out",
        default="",
        help="Optional output path for generated scenario JSON. Default: tmp/scenarios/<name>.json",
    )
    parser.add_argument("--kb-name", default="", help="Optional KB namespace name. Default: scenario name.")
    parser.add_argument(
        "--pipeline-out",
        default="",
        help="Optional output path for pipeline run JSON. Default: tmp/<name>.pipeline.json",
    )
    parser.add_argument("--backend", default="ollama")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--model", default="qwen3.5:9b")
    parser.add_argument("--runtime", default="core")
    parser.add_argument("--prompt-file", default="modelfiles/semantic_parser_system_prompt.md")
    parser.add_argument("--context-length", type=int, default=8192)
    parser.add_argument("--clarification-eagerness", type=float, default=0.2)
    parser.add_argument("--max-clarification-rounds", type=int, default=1)
    parser.add_argument("--clarification-answer-model", default="qwen3.5:9b")
    parser.add_argument("--clarification-answer-backend", default="ollama")
    parser.add_argument("--clarification-answer-base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--clarification-answer-context-length", type=int, default=8192)
    parser.add_argument("--clarification-answer-min-confidence", type=float, default=0.55)
    parser.add_argument("--frontend-proposal-mode", default="off")
    parser.add_argument(
        "--write-corpus-on-fail",
        action="store_true",
        help="Pass through to kb_pipeline so kb.pl/progress/profile are persisted even when run fails.",
    )
    parser.add_argument(
        "--split-mode",
        default="full",
        choices=["full", "paragraph", "line"],
        help="How to package source text into utterances. Default 'full' is raw-as-is.",
    )
    parser.add_argument("--run-interrogator", action="store_true", help="Also run kb_interrogator after pipeline pass.")
    parser.add_argument(
        "--run-interrogator-on-fail",
        action="store_true",
        help="When pipeline fails, still run interrogator if candidate kb.pl exists.",
    )
    parser.add_argument("--exam-style", default="detective", choices=["general", "detective", "medical"])
    parser.add_argument("--exam-question-count", type=int, default=14)
    parser.add_argument("--exam-min-temporal-questions", type=int, default=2)
    args = parser.parse_args()

    story_path = Path(args.story_file)
    if not story_path.is_absolute():
        story_path = (ROOT / story_path).resolve()
    if not story_path.exists():
        print(f"[raw-story] missing file: {story_path}", file=sys.stderr)
        return 2

    base_name = args.scenario_name.strip() or f"story_{_slug(story_path.stem)}_raw"
    kb_name = args.kb_name.strip() or base_name

    scenario_path = Path(args.scenario_out).resolve() if args.scenario_out else ROOT / "tmp" / "scenarios" / f"{base_name}.json"
    pipeline_out = Path(args.pipeline_out).resolve() if args.pipeline_out else ROOT / "tmp" / f"{base_name}.pipeline.json"

    raw_story_text = _read_story_text(story_path)
    utterances = _to_utterances(raw_story_text, split_mode=str(args.split_mode))
    if not utterances:
        print(f"[raw-story] no utterances extracted from: {story_path}", file=sys.stderr)
        return 3

    scenario = {
        "name": base_name,
        "ontology_name": base_name,
        "utterances": utterances,
        "validations": [],
    }
    _write_json(scenario_path, scenario)
    print(f"[raw-story] scenario written: {scenario_path}")
    print(f"[raw-story] split_mode={args.split_mode} (default full = no-preprocess pass-through)")
    print(f"[raw-story] utterance_count={len(utterances)}")

    cmd = [
        sys.executable,
        str(PIPELINE),
        "--backend",
        args.backend,
        "--base-url",
        args.base_url,
        "--model",
        args.model,
        "--runtime",
        args.runtime,
        "--scenario",
        str(scenario_path),
        "--kb-name",
        kb_name,
        "--out",
        str(pipeline_out),
        "--prompt-file",
        str((ROOT / args.prompt_file).resolve()),
        "--context-length",
        str(int(args.context_length)),
        "--clarification-eagerness",
        str(float(args.clarification_eagerness)),
        "--max-clarification-rounds",
        str(int(args.max_clarification_rounds)),
        "--clarification-answer-model",
        args.clarification_answer_model,
        "--clarification-answer-backend",
        args.clarification_answer_backend,
        "--clarification-answer-base-url",
        args.clarification_answer_base_url,
        "--clarification-answer-context-length",
        str(int(args.clarification_answer_context_length)),
        "--clarification-answer-min-confidence",
        str(float(args.clarification_answer_min_confidence)),
        "--frontend-proposal-mode",
        args.frontend_proposal_mode,
    ]
    if args.write_corpus_on_fail:
        cmd.append("--write-corpus-on-fail")
    rc = _run(cmd)

    report: dict[str, Any] = {}
    if pipeline_out.exists():
        report = _load_json(pipeline_out)
        print(
            "[raw-story] pipeline",
            f"status={report.get('overall_status')}",
            f"parse_failures={report.get('turn_parse_failures')}",
            f"apply_failures={report.get('turn_apply_failures')}",
            f"clarification_requests={report.get('turns_clarification_requested')}",
        )
    else:
        print(f"[raw-story] pipeline report missing: {pipeline_out}", file=sys.stderr)

    if rc != 0:
        print(f"[raw-story] pipeline failed (rc={rc})")
        if not args.run_interrogator_on_fail:
            return rc

    if not args.run_interrogator:
        return 0 if rc == 0 else rc

    kb_path = _resolve_kb_path(report, kb_name)
    if not kb_path.exists():
        print(f"[raw-story] kb.pl missing; cannot run interrogator: {kb_path}", file=sys.stderr)
        return 0 if rc == 0 else rc
    print(f"[raw-story] interrogator target kb={kb_path}")
    interrogator_json = ROOT / "tmp" / f"{base_name}.interrogator.json"
    interrogator_md = ROOT / "tmp" / f"{base_name}.interrogator.md"

    icmd = [
        sys.executable,
        str(INTERROGATOR),
        "--source-text-file",
        str(story_path),
        "--candidate-kb",
        str(kb_path),
        "--backend",
        args.backend,
        "--base-url",
        args.base_url,
        "--model",
        args.model,
        "--context-length",
        str(int(args.context_length)),
        "--exam-style",
        args.exam_style,
        "--exam-question-count",
        str(int(args.exam_question_count)),
        "--exam-min-temporal-questions",
        str(int(args.exam_min_temporal_questions)),
        "--out-json",
        str(interrogator_json),
        "--out-md",
        str(interrogator_md),
    ]
    irc = _run(icmd)
    if irc != 0:
        print(f"[raw-story] interrogator failed (rc={irc})")
        return irc

    ireport = _load_json(interrogator_json)
    fact_audit = ireport.get("fact_audit", {}) if isinstance(ireport.get("fact_audit"), dict) else {}
    exam = ireport.get("exam", {}) if isinstance(ireport.get("exam"), dict) else {}
    print(
        "[raw-story] interrogator",
        f"coverage={fact_audit.get('coverage_score')}",
        f"precision={fact_audit.get('precision_score')}",
        f"exam={exam.get('pass_count')}/{exam.get('question_count')}",
    )
    return 0 if rc == 0 else rc


if __name__ == "__main__":
    raise SystemExit(main())
