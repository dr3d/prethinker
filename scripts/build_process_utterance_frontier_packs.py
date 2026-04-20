from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_RUN_DIRS = {
    "error_focus": ROOT / "tmp" / "runs" / "process_utterance_forge" / "20260420_031930_forge" / "interesting_cases",
    "temporal_focus": ROOT / "tmp" / "runs" / "process_utterance_forge" / "20260420_115701_forge" / "interesting_cases",
}
OUT_DIR = ROOT / "docs" / "data" / "frontier_packs"
REPORT_PATH = ROOT / "docs" / "reports" / "PROCESS_UTTERANCE_FRONTIER_PACKS_2026-04-20.md"
CORRECTION_PACK_PATH = OUT_DIR / "process_utterance_correction_pack_v1.json"
TEMPORAL_PACK_PATH = OUT_DIR / "process_utterance_temporal_pack_v1.json"

SEVERITY_ORDER = {"fail": 0, "warn": 1, "pass": 2}
TEMPORAL_WARN_TARGET_TAGS = {
    "over_clarification",
    "over-clarification",
    "implicit_sequence",
    "brittle_parsing",
    "temporal_mismatch",
    "over_simplification",
    "temporal_conflict",
}


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", str(text).strip().lower())
    return slug.strip("_") or "case"


def _normalized_tags(raw_tags: Any) -> set[str]:
    tags: set[str] = set()
    if isinstance(raw_tags, list):
        values = raw_tags
    else:
        values = []
    for tag in values:
        text = str(tag).strip().lower().replace("-", "_").replace(" ", "_")
        if text:
            tags.add(text)
    return tags


def _load_case_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run_id, case_dir in SOURCE_RUN_DIRS.items():
        if not case_dir.exists():
            continue
        for path in sorted(case_dir.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["_source_run"] = run_id
            payload["_source_path"] = str(path)
            rows.append(payload)
    return rows


def _sort_key(case: dict[str, Any]) -> tuple[Any, ...]:
    judgment = case.get("judgment", {}) if isinstance(case.get("judgment"), dict) else {}
    result_summary = case.get("result_summary", {}) if isinstance(case.get("result_summary"), dict) else {}
    verdict = str(judgment.get("verdict", "")).strip().lower()
    status = str(result_summary.get("status", "")).strip().lower()
    return (
        SEVERITY_ORDER.get(verdict, 99),
        0 if status == "error" else 1,
        -float(case.get("interestingness", 0.0) or 0.0),
        str(case.get("utterance", "")).strip().lower(),
    )


def _distill_correction_setup_turns(utterance: str) -> list[dict[str, str]]:
    match = re.match(
        r"^actually no,\s+(.+?)\s+is with\s+(.+?)\s+not\s+(.+?)[.!?]?$",
        str(utterance).strip(),
        flags=re.IGNORECASE,
    )
    if not match:
        return []
    item = match.group(1).strip()
    old_holder = match.group(3).strip()
    return [{"utterance": f"remember that {item} is with {old_holder}"}]


def _baseline(case: dict[str, Any]) -> dict[str, Any]:
    judgment = case.get("judgment", {}) if isinstance(case.get("judgment"), dict) else {}
    result_summary = case.get("result_summary", {}) if isinstance(case.get("result_summary"), dict) else {}
    return {
        "verdict": str(judgment.get("verdict", "")).strip(),
        "status": str(result_summary.get("status", "")).strip(),
        "tags": list(judgment.get("tags", [])) if isinstance(judgment.get("tags"), list) else [],
        "interestingness": float(case.get("interestingness", 0.0) or 0.0),
        "rationale": str(judgment.get("rationale", "")).strip(),
        "logic_string": str(result_summary.get("logic_string", "")).strip(),
        "trace_overall": str(result_summary.get("trace_overall", "")).strip(),
    }


def _distilled_case(
    *,
    family: str,
    case: dict[str, Any],
    index: int,
    setup_turns: list[dict[str, str]],
) -> dict[str, Any]:
    utterance = str(case.get("utterance", "")).strip()
    source_path = Path(str(case.get("_source_path", "")))
    spec = dict(case.get("spec", {}) if isinstance(case.get("spec"), dict) else {})
    if family == "correction":
        match = re.match(
            r"^actually no,\s+(.+?)\s+is with\s+(.+?)\s+not\s+(.+?)[.!?]?$",
            utterance,
            flags=re.IGNORECASE,
        )
        if match:
            item = match.group(1).strip()
            new_holder = match.group(2).strip()
            old_holder = match.group(3).strip()
            spec = {
                "utterance": utterance,
                "hidden_intent": "assert_fact",
                "hidden_meaning": f"The previous holder is wrong. {item} is with {new_holder}, not {old_holder}.",
                "expected_behavior": "commit",
                "risk_focus": "correction",
                "uses_context": True,
                "lane": "correction",
                "style": "distilled",
                "source": "frontier_pack_distilled",
            }
    else:
        spec["source"] = "frontier_pack_distilled"
    return {
        "case_id": f"{family}_{index:02d}_{_slugify(utterance)[:48]}",
        "source_case": {
            "run_id": str(case.get("_source_run", "")).strip(),
            "file": source_path.name,
            "path": str(source_path),
        },
        "setup_turns": setup_turns,
        "utterance": utterance,
        "clarification_answer": "" if family == "correction" else str(case.get("clarification_answer", "")).strip(),
        "spec": spec,
        "baseline": _baseline(case),
    }


def _choose_correction_cases(rows: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    candidates = [
        row
        for row in rows
        if str(row.get("spec", {}).get("lane", "")).strip() == "correction"
        and _distill_correction_setup_turns(str(row.get("utterance", "")).strip())
    ]
    chosen: list[dict[str, Any]] = []
    seen: set[str] = set()
    for case in sorted(candidates, key=_sort_key):
        utterance = str(case.get("utterance", "")).strip().lower()
        if utterance in seen:
            continue
        chosen.append(case)
        seen.add(utterance)
        if len(chosen) >= limit:
            break
    return chosen


def _choose_temporal_cases(rows: list[dict[str, Any]], fail_limit: int = 6, warn_limit: int = 6) -> list[dict[str, Any]]:
    temporal = [row for row in rows if str(row.get("spec", {}).get("lane", "")).strip() == "temporal_state"]
    fails = [row for row in temporal if str(row.get("judgment", {}).get("verdict", "")).strip().lower() == "fail"]
    warns = [row for row in temporal if str(row.get("judgment", {}).get("verdict", "")).strip().lower() == "warn"]

    chosen: list[dict[str, Any]] = []
    seen: set[str] = set()
    for case in sorted(fails, key=_sort_key):
        utterance = str(case.get("utterance", "")).strip().lower()
        if utterance in seen:
            continue
        chosen.append(case)
        seen.add(utterance)
        if len(chosen) >= fail_limit:
            break

    selected_warns: list[dict[str, Any]] = []
    remaining = [case for case in warns if str(case.get("utterance", "")).strip().lower() not in seen]
    covered_tags: set[str] = set()
    while remaining and len(selected_warns) < warn_limit:
        best = max(
            remaining,
            key=lambda case: (
                len(_normalized_tags(case.get("judgment", {}).get("tags", [])) & TEMPORAL_WARN_TARGET_TAGS - covered_tags),
                float(case.get("interestingness", 0.0) or 0.0),
                -len(str(case.get("utterance", "")).strip()),
            ),
        )
        selected_warns.append(best)
        seen.add(str(best.get("utterance", "")).strip().lower())
        covered_tags |= _normalized_tags(best.get("judgment", {}).get("tags", [])) & TEMPORAL_WARN_TARGET_TAGS
        remaining = [case for case in remaining if str(case.get("utterance", "")).strip().lower() not in seen]

    chosen.extend(selected_warns)
    return chosen


def _build_pack(
    *,
    pack_id: str,
    family: str,
    description: str,
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "pack_id": pack_id,
        "family": family,
        "created_at_utc": created_at,
        "description": description,
        "source_runs": {key: str(path) for key, path in SOURCE_RUN_DIRS.items()},
        "selection_policy": (
            "Distilled from real forge interesting_cases. Correction cases preserve the failing correction utterance and "
            "inject the obvious prior-holder setup turn. Temporal cases preserve self-contained step/sequence failures and "
            "warns with tag diversity."
        ),
        "cases": cases,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_report(*, correction_pack: dict[str, Any], temporal_pack: dict[str, Any]) -> None:
    lines = [
        "# Process Utterance Frontier Packs",
        "",
        "- These packs are distilled from real forge failures and warnings.",
        "- They are meant to be durable replay targets for the hardest current `process_utterance()` families.",
        "- They intentionally keep `Freethinker` out of the loop for now so `v1` improvements remain honest.",
        "",
        "## Packs",
        "",
        f"- correction pack: `{len(correction_pack.get('cases', []))}` cases",
        f"- temporal pack: `{len(temporal_pack.get('cases', []))}` cases",
        "",
        "## Correction Pack",
        "",
    ]
    for case in correction_pack.get("cases", []):
        baseline = case.get("baseline", {})
        setup = case.get("setup_turns", [])
        setup_text = "; ".join(str(row.get("utterance", "")).strip() for row in setup)
        lines.append(
            f"- `{case.get('case_id', '')}`: setup=`{setup_text}` target=`{case.get('utterance', '')}` "
            f"baseline=`{baseline.get('verdict', '')}/{baseline.get('status', '')}`"
        )
    lines.extend(["", "## Temporal Pack", ""])
    for case in temporal_pack.get("cases", []):
        baseline = case.get("baseline", {})
        tags = ", ".join(str(tag) for tag in baseline.get("tags", []))
        lines.append(
            f"- `{case.get('case_id', '')}`: target=`{case.get('utterance', '')}` "
            f"baseline=`{baseline.get('verdict', '')}/{baseline.get('status', '')}` tags=`{tags}`"
        )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    rows = _load_case_rows()
    correction_cases = _choose_correction_cases(rows)
    temporal_cases = _choose_temporal_cases(rows)

    correction_pack = _build_pack(
        pack_id="process_utterance_correction_pack_v1",
        family="correction",
        description="Replayable correction/retraction frontier distilled from forge failures.",
        cases=[
            _distilled_case(
                family="correction",
                case=case,
                index=index,
                setup_turns=_distill_correction_setup_turns(str(case.get("utterance", "")).strip()),
            )
            for index, case in enumerate(correction_cases, start=1)
        ],
    )
    temporal_pack = _build_pack(
        pack_id="process_utterance_temporal_pack_v1",
        family="temporal_state",
        description="Replayable temporal/step-sequencing frontier distilled from forge failures and warns.",
        cases=[
            _distilled_case(
                family="temporal",
                case=case,
                index=index,
                setup_turns=[],
            )
            for index, case in enumerate(temporal_cases, start=1)
        ],
    )

    _write_json(CORRECTION_PACK_PATH, correction_pack)
    _write_json(TEMPORAL_PACK_PATH, temporal_pack)
    _write_report(correction_pack=correction_pack, temporal_pack=temporal_pack)

    print(f"Wrote correction pack: {CORRECTION_PACK_PATH}")
    print(f"Wrote temporal pack: {TEMPORAL_PACK_PATH}")
    print(f"Wrote report: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
