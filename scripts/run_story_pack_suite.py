#!/usr/bin/env python3
"""
Run an end-to-end story-pack suite for markdown packs that contain:
- a fenced raw story section (```text ... ```)
- suggested staged gulp percentages
- a recommended split mode

This script establishes repeatable runners for new story packs by:
1) extracting raw story text into tmp/story_inputs/*.txt
2) running stress cycles via scripts/run_story_stress_cycle.py
3) running progressive cycles via scripts/run_story_progressive_gulp.py
4) emitting consolidated suite summaries (json + md)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STRESS = ROOT / "scripts" / "run_story_stress_cycle.py"
PROGRESSIVE = ROOT / "scripts" / "run_story_progressive_gulp.py"


def _utc_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _slug(text: str, *, max_len: int = 60) -> str:
    clean = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text or ""))
    while "__" in clean:
        clean = clean.replace("__", "_")
    clean = clean.strip("_") or "pack"
    return clean[:max_len].strip("_") or "pack"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _extract_story(pack_markdown: str) -> str:
    match = re.search(
        r"##\s*Raw Story Text\s*```text\s*(.*?)\s*```",
        pack_markdown,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        match = re.search(r"```text\s*(.*?)\s*```", pack_markdown, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()


def _extract_split_mode(pack_markdown: str, *, default: str) -> str:
    match = re.search(
        r"Recommended primary split mode:\s*`(full|paragraph|line)`",
        pack_markdown,
        flags=re.IGNORECASE,
    )
    if not match:
        return default
    return str(match.group(1)).strip().lower()


def _extract_percentages(pack_markdown: str, *, default: list[int]) -> list[int]:
    found: list[int] = []
    for raw in re.findall(r"`(\d+)%`", pack_markdown):
        try:
            pct = int(raw)
        except Exception:
            continue
        if 1 <= pct <= 100 and pct not in found:
            found.append(pct)
    if not found:
        found = list(default)
    if 100 not in found:
        found.append(100)
    return sorted(found)


def _run(cmd: list[str]) -> int:
    print("\n$ " + " ".join(cmd))
    completed = subprocess.run(cmd, cwd=ROOT)
    return int(completed.returncode or 0)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _build_markdown(summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Story Pack Suite")
    lines.append("")
    lines.append(f"- Generated UTC: `{summary.get('generated_at_utc', '')}`")
    lines.append(f"- Backend: `{summary.get('settings', {}).get('backend', '')}`")
    lines.append(f"- Model: `{summary.get('settings', {}).get('model', '')}`")
    lines.append("")
    packs = summary.get("packs", [])
    if not isinstance(packs, list):
        packs = []
    for pack in packs:
        if not isinstance(pack, dict):
            continue
        lines.append(f"## {pack.get('pack_name', 'pack')}")
        lines.append("")
        lines.append(f"- Story file: `{pack.get('story_file', '')}`")
        lines.append(f"- Stress exit code: `{pack.get('stress_exit_code', '')}`")
        lines.append(f"- Progressive exit code: `{pack.get('progressive_exit_code', '')}`")
        stress = pack.get("stress_summary", {})
        if isinstance(stress, dict):
            lines.append(
                "- Stress metrics: "
                f"pipeline `{stress.get('pipeline_pass_count', '?')}/{stress.get('run_count', '?')}`, "
                f"coverage `{stress.get('avg_coverage', '?')}`, "
                f"precision `{stress.get('avg_precision', '?')}`, "
                f"exam `{stress.get('avg_exam_pass_rate', '?')}`"
            )
        prog = pack.get("progressive_summary", {})
        if isinstance(prog, dict):
            stage_rows = prog.get("stages", [])
            hard_gate_pass = 0
            total = 0
            if isinstance(stage_rows, list):
                total = len(stage_rows)
                for row in stage_rows:
                    if not isinstance(row, dict):
                        continue
                    if bool(row.get("hard_gate_pass", False)) or bool(row.get("gate_passed", False)):
                        hard_gate_pass += 1
            lines.append(f"- Progressive gates: `{hard_gate_pass}/{total}` passed")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run stress+progressive suite for story packs.")
    parser.add_argument(
        "--packs",
        default="tmp/story_pack_mid.md,tmp/story_pack_upper_mid.md",
        help="Comma-separated markdown pack paths.",
    )
    parser.add_argument("--backend", default="ollama")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--model", default="qwen3.5:9b")
    parser.add_argument("--prompt-file", default="modelfiles/semantic_parser_system_prompt.md")
    parser.add_argument("--context-length", type=int, default=8192)
    parser.add_argument("--predicate-registry", default="")
    parser.add_argument("--strict-registry", action="store_true")
    parser.add_argument("--type-schema", default="")
    parser.add_argument("--exam-style", default="detective", choices=["general", "detective", "medical"])
    parser.add_argument("--exam-question-count", type=int, default=20)
    parser.add_argument("--exam-min-temporal-questions", type=int, default=4)
    parser.add_argument("--stress-modes", default="full,paragraph,line")
    parser.add_argument("--stress-temporal", default="off,on")
    parser.add_argument("--default-progressive-split", default="paragraph", choices=["full", "paragraph", "line"])
    parser.add_argument("--default-progressive-percentages", default="25,50,75,100")
    parser.add_argument("--summary-json", default="tmp/story_pack_suite_latest.summary.json")
    parser.add_argument("--summary-md", default="tmp/story_pack_suite_latest.summary.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    default_pcts: list[int] = []
    for raw in str(args.default_progressive_percentages).split(","):
        token = raw.strip()
        if not token:
            continue
        try:
            pct = int(token)
        except Exception:
            continue
        if 1 <= pct <= 100 and pct not in default_pcts:
            default_pcts.append(pct)
    if not default_pcts:
        default_pcts = [25, 50, 75, 100]
    if 100 not in default_pcts:
        default_pcts.append(100)

    pack_paths: list[Path] = []
    for raw in str(args.packs).split(","):
        token = raw.strip()
        if not token:
            continue
        p = Path(token)
        if not p.is_absolute():
            p = (ROOT / p).resolve()
        pack_paths.append(p)

    summary: dict[str, Any] = {
        "generated_at_utc": _utc_iso(),
        "settings": {
            "backend": args.backend,
            "base_url": args.base_url,
            "model": args.model,
            "prompt_file": args.prompt_file,
            "context_length": int(args.context_length),
            "predicate_registry": str(args.predicate_registry),
            "strict_registry": bool(args.strict_registry),
            "type_schema": str(args.type_schema),
            "exam_style": args.exam_style,
            "exam_question_count": int(args.exam_question_count),
            "exam_min_temporal_questions": int(args.exam_min_temporal_questions),
            "stress_modes": args.stress_modes,
            "stress_temporal": args.stress_temporal,
            "default_progressive_split": args.default_progressive_split,
            "default_progressive_percentages": default_pcts,
        },
        "packs": [],
    }

    inputs_dir = ROOT / "tmp" / "story_inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)

    for pack_path in pack_paths:
        pack_entry: dict[str, Any] = {
            "pack_path": str(pack_path),
        }
        if not pack_path.exists():
            pack_entry["error"] = "pack_not_found"
            summary["packs"].append(pack_entry)
            continue

        pack_text = _read_text(pack_path)
        story_text = _extract_story(pack_text)
        if not story_text:
            pack_entry["error"] = "story_not_found"
            summary["packs"].append(pack_entry)
            continue

        base_name = _slug(pack_path.stem.replace("story_pack_", ""))
        pack_name = f"{base_name}_pack"
        story_file = inputs_dir / f"{base_name}.txt"
        story_file.write_text(story_text.strip() + "\n", encoding="utf-8")

        split_mode = _extract_split_mode(pack_text, default=str(args.default_progressive_split))
        percentages = _extract_percentages(pack_text, default=default_pcts)
        pct_csv = ",".join(str(p) for p in percentages)

        stress_summary_json = ROOT / "tmp" / f"{pack_name}_stress.summary.json"
        stress_summary_md = ROOT / "tmp" / f"{pack_name}_stress.summary.md"
        stress_report_html = ROOT / "docs" / "reports" / f"{pack_name}-stress.html"

        progressive_summary_json = ROOT / "tmp" / f"{pack_name}_progressive.summary.json"
        progressive_summary_md = ROOT / "tmp" / f"{pack_name}_progressive.summary.md"
        progressive_report_html = ROOT / "docs" / "reports" / f"{pack_name}-progressive.html"

        stress_cmd = [
            sys.executable,
            str(STRESS),
            "--story-file",
            str(story_file),
            "--label",
            pack_name,
            "--modes",
            str(args.stress_modes),
            "--temporal",
            str(args.stress_temporal),
            "--backend",
            str(args.backend),
            "--base-url",
            str(args.base_url),
            "--model",
            str(args.model),
            "--prompt-file",
            str(args.prompt_file),
            "--context-length",
            str(int(args.context_length)),
            "--exam-style",
            str(args.exam_style),
            "--exam-question-count",
            str(int(args.exam_question_count)),
            "--exam-min-temporal-questions",
            str(int(args.exam_min_temporal_questions)),
            "--summary-json",
            str(stress_summary_json),
            "--summary-md",
            str(stress_summary_md),
            "--report-html",
            str(stress_report_html),
            "--write-latest-alias",
        ]
        if str(args.predicate_registry).strip():
            stress_cmd.extend(["--predicate-registry", str(args.predicate_registry)])
        if bool(args.strict_registry):
            stress_cmd.append("--strict-registry")
        if str(args.type_schema).strip():
            stress_cmd.extend(["--type-schema", str(args.type_schema)])
        stress_code = _run(stress_cmd)

        progressive_cmd = [
            sys.executable,
            str(PROGRESSIVE),
            "--story-file",
            str(story_file),
            "--label",
            pack_name,
            "--percentages",
            pct_csv,
            "--split-mode",
            split_mode,
            "--auto-fallback-split",
            "--backend",
            str(args.backend),
            "--base-url",
            str(args.base_url),
            "--model",
            str(args.model),
            "--prompt-file",
            str(args.prompt_file),
            "--context-length",
            str(int(args.context_length)),
            "--temporal-dual-write",
            "--exam-style",
            str(args.exam_style),
            "--exam-question-count",
            str(int(args.exam_question_count)),
            "--exam-min-temporal-questions",
            str(int(args.exam_min_temporal_questions)),
            "--pack-markdown",
            str(pack_path),
            "--summary-json",
            str(progressive_summary_json),
            "--summary-md",
            str(progressive_summary_md),
            "--report-html",
            str(progressive_report_html),
        ]
        if str(args.predicate_registry).strip():
            progressive_cmd.extend(["--predicate-registry", str(args.predicate_registry)])
        if bool(args.strict_registry):
            progressive_cmd.append("--strict-registry")
        if str(args.type_schema).strip():
            progressive_cmd.extend(["--type-schema", str(args.type_schema)])
        progressive_code = _run(progressive_cmd)

        pack_entry.update(
            {
                "pack_name": pack_name,
                "story_file": str(story_file),
                "story_char_count": len(story_text),
                "recommended_split_mode": split_mode,
                "recommended_percentages": percentages,
                "stress_exit_code": stress_code,
                "stress_summary_json": str(stress_summary_json),
                "stress_summary_md": str(stress_summary_md),
                "stress_report_html": str(stress_report_html),
                "progressive_exit_code": progressive_code,
                "progressive_summary_json": str(progressive_summary_json),
                "progressive_summary_md": str(progressive_summary_md),
                "progressive_report_html": str(progressive_report_html),
                "stress_summary": _load_json(stress_summary_json),
                "progressive_summary": _load_json(progressive_summary_json),
            }
        )
        summary["packs"].append(pack_entry)

    out_json = Path(str(args.summary_json))
    if not out_json.is_absolute():
        out_json = (ROOT / out_json).resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    out_md = Path(str(args.summary_md))
    if not out_md.is_absolute():
        out_md = (ROOT / out_md).resolve()
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(_build_markdown(summary), encoding="utf-8")

    print(f"[story-pack-suite] summary_json={out_json}")
    print(f"[story-pack-suite] summary_md={out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
