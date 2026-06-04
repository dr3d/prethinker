#!/usr/bin/env python3
"""Build deterministic compile-fact judged-QA artifacts.

This is the in-repo version of the FDA judged-QA v2 package shape. It judges
whether expected Prolog facts are supported by a compile artifact's typed facts.
It does not call an LLM, read source prose, or rewrite oracle facts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_typed_micro_fixtures import (
    DEFAULT_ROOT,
    _facts_from_compile_json,
    _is_expected_variable,
    _load_fact_lines,
    _parse_fact,
)
from scripts.summarize_typed_micro_series import _apply_domain_reducers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture-root",
        type=Path,
        default=DEFAULT_ROOT,
        help="Root containing typed micro-fixture directories.",
    )
    parser.add_argument(
        "--fixture-run",
        action="append",
        default=[],
        metavar="FIXTURE_ID:RUN_ID=PATH",
        help="Compile artifact to judge. Repeat for multiple fixtures/runs.",
    )
    parser.add_argument(
        "--domain-lens-bundle",
        action="append",
        default=[],
        metavar="FIXTURE_ID=PATH",
        help="Discover union compile artifacts under PATH/unions/run*/. Repeat for multiple bundles.",
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument(
        "--created-utc",
        default="",
        help="Optional timestamp for reproducible tests; default is current UTC.",
    )
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_specs = _parse_fixture_runs(args.fixture_run)
    run_specs.extend(_parse_domain_lens_bundles(args.domain_lens_bundle))
    created_utc = str(args.created_utc).strip() or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    bundle = build_bundle(
        fixture_root=args.fixture_root,
        run_specs=run_specs,
        created_utc=created_utc,
    )
    write_bundle(bundle=bundle, out_dir=args.out_dir)
    blocked = bool(bundle["summary"]["blocking_reasons"])
    return 0 if args.exit_zero or not blocked else 1


def build_bundle(
    *,
    fixture_root: Path,
    run_specs: list[dict[str, Any]],
    created_utc: str,
) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    verdict_summary_by_file: dict[str, dict[str, int]] = {}
    forbidden_emissions_by_file: dict[str, list[dict[str, str]]] = {}
    blocking_reasons: list[str] = []
    if not run_specs:
        blocking_reasons.append("no_fixture_runs")

    for spec in run_specs:
        fixture_id = str(spec["fixture_id"])
        run_id = str(spec["run_id"])
        compile_json = Path(spec["compile_json"]).resolve()
        run_payload = build_run_payload(
            fixture_root=fixture_root,
            fixture_id=fixture_id,
            run_id=run_id,
            compile_json=compile_json,
            created_utc=created_utc,
        )
        filename = f"{fixture_id}__{run_id}__judged_qa.json"
        files.append({"filename": filename, "payload": run_payload})
        verdict_summary_by_file[filename] = dict(run_payload["verdict_summary"])
        if run_payload["forbidden_emissions"]:
            forbidden_emissions_by_file[filename] = list(run_payload["forbidden_emissions"])

    return {
        "schema": "prethinker.judged_qa_bundle.v1",
        "created_utc": created_utc,
        "fixtures": sorted({str(spec["fixture_id"]) for spec in run_specs}),
        "runs_per_fixture": dict(Counter(str(spec["fixture_id"]) for spec in run_specs)),
        "summary": {
            "file_count": len(files),
            "blocking_reasons": blocking_reasons,
        },
        "support_summary_by_fixture": _support_summary_by_fixture(files),
        "verdict_summary_by_file": verdict_summary_by_file,
        "forbidden_emissions_by_file": forbidden_emissions_by_file,
        "files": files,
    }


def build_run_payload(
    *,
    fixture_root: Path,
    fixture_id: str,
    run_id: str,
    compile_json: Path,
    created_utc: str,
) -> dict[str, Any]:
    fixture_dir = fixture_root / fixture_id
    expected_path = fixture_dir / "expected_facts.pl"
    forbidden_path = fixture_dir / "forbidden_facts.pl"
    expected_facts = _load_fact_lines(expected_path)
    forbidden_facts = _load_fact_lines(forbidden_path) if forbidden_path.exists() else []
    compile_facts, domain_reducer_reports = _compile_facts_with_domain_reducers(compile_json)
    rows: list[dict[str, Any]] = []
    verdicts: Counter[str] = Counter()
    for index, expected_fact in enumerate(expected_facts, start=1):
        row = _judge_expected_fact(
            fixture_id=fixture_id,
            run_id=run_id,
            row_index=index,
            expected_fact=expected_fact,
            compile_facts=compile_facts,
            compile_json=compile_json,
        )
        verdicts[str(row["reference_judge"]["verdict"])] += 1
        rows.append(row)
    forbidden_emissions = [
        {"forbidden_fact": forbidden_fact, "compiled_fact": match["compiled_fact"]}
        for forbidden_fact in forbidden_facts
        for match in [_exact_match(forbidden_fact, compile_facts)]
        if match is not None
    ]
    return {
        "id": f"{fixture_id}__{run_id}__judged_qa",
        "schema": "prethinker.judged_qa.v1",
        "fixture": fixture_id,
        "fixture_name": fixture_id,
        "run_id": run_id,
        "run_json": str(compile_json),
        "oracle_basis": str(expected_path),
        "forbidden_basis": str(forbidden_path) if forbidden_path.exists() else "",
        "generated_utc": created_utc,
        "domain_reducers_applied": True,
        "domain_reducer_reports": domain_reducer_reports,
        "verdict_summary": dict(sorted(verdicts.items())),
        "forbidden_emissions": forbidden_emissions,
        "rows": rows,
    }


def _compile_facts_with_domain_reducers(path: Path) -> tuple[list[str], dict[str, Any]]:
    compile_facts = _facts_from_compile_json(path)
    reduced_compile: dict[str, Any] = {"facts": compile_facts, "rules": [], "queries": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        payload = {}
    if isinstance(payload, dict):
        mode = str(payload.get("mode", "")).strip()
        if mode:
            reduced_compile["mode"] = mode
        if isinstance(payload.get("union_source_compile"), dict):
            reduced_compile["union_source_compile"] = payload["union_source_compile"]
        if isinstance(payload.get("active_profile_registry_lens"), dict):
            reduced_compile["active_profile_registry_lens"] = payload["active_profile_registry_lens"]
    reducer_reports = _apply_domain_reducers(reduced_compile)
    reduced_facts = [str(fact).strip() for fact in reduced_compile.get("facts", []) if str(fact).strip()]
    return reduced_facts, reducer_reports


def write_bundle(*, bundle: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        key: value
        for key, value in bundle.items()
        if key != "files"
    }
    manifest["files"] = [item["filename"] for item in bundle["files"]]
    for item in bundle["files"]:
        (out_dir / item["filename"]).write_text(
            json.dumps(item["payload"], indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "README.md").write_text(_readme_text(manifest), encoding="utf-8")


def _judge_expected_fact(
    *,
    fixture_id: str,
    run_id: str,
    row_index: int,
    expected_fact: str,
    compile_facts: list[str],
    compile_json: Path,
) -> dict[str, Any]:
    exact = _exact_match(expected_fact, compile_facts)
    parsed = _parse_fact(expected_fact)
    if exact is not None:
        verdict = "exact"
        label = "compile_supported"
        answer = str(exact["compiled_fact"])
        rationale = (
            f"Compile artifact emits {exact['carrier_candidate_count']} {exact['signature']} fact(s); "
            f"all {exact['total_constant_slots']} oracle constant slot(s) matched. "
            "Variable slots bound to compiled atoms."
        )
        match_detail = {
            "matched_constant_positions": exact["matched_constant_positions"],
            "total_constant_slots": exact["total_constant_slots"],
            "carrier_candidate_count": exact["carrier_candidate_count"],
        }
        query_result = _query_result(
            expected_fact=expected_fact,
            parsed=parsed,
            status="answered",
            compiled_fact=answer,
            bindings=dict(exact["bindings"]),
        )
    else:
        partial = _partial_match(expected_fact, compile_facts)
        if partial is not None:
            verdict = "partial"
            label = "compile_partial"
            answer = str(partial["compiled_fact"])
            rationale = (
                f"Compile artifact has carrier {partial['signature']} and matches the primary constant; "
                f"{len(partial['matched_constant_positions'])} of {partial['total_constant_slots']} "
                f"oracle constant slot(s) matched. Differing slot(s): {partial['difference_text']}. "
                "Partial, not exact."
            )
            match_detail = {
                "matched_constant_positions": partial["matched_constant_positions"],
                "differing_constant_positions": partial["differing_constant_positions"],
                "total_constant_slots": partial["total_constant_slots"],
                "carrier_candidate_count": partial["carrier_candidate_count"],
            }
            query_result = _query_result(
                expected_fact=expected_fact,
                parsed=parsed,
                status="answered",
                compiled_fact=answer,
                bindings=dict(partial["bindings"]),
            )
        else:
            verdict = "miss"
            label = "compile_unsupported"
            answer = ""
            miss_detail = _miss_detail(expected_fact, compile_facts)
            rationale = miss_detail["rationale"]
            match_detail = miss_detail["match_detail"]
            query_result = _query_result(
                expected_fact=expected_fact,
                parsed=parsed,
                status="unsupported",
                compiled_fact="",
                bindings={},
            )
    return {
        "id": f"{fixture_id}__{run_id}__r{row_index:03d}",
        "fixture": fixture_id,
        "fixture_name": fixture_id,
        "run_id": run_id,
        "utterance": f"Does the compile support {expected_fact}",
        "question": f"Does the compile support {expected_fact}",
        "reference_answer": expected_fact,
        "reference_answer_carrier": _signature(parsed),
        "answer": answer,
        "reference_judge": {
            "verdict": verdict,
            "label": label,
            "rationale": rationale,
        },
        "match_detail": match_detail,
        "queries": [expected_fact],
        "query_results": [{"query": expected_fact, "result": query_result}],
        "compile_run_artifact_path": str(compile_json),
    }


def _exact_match(expected_fact: str, compile_facts: list[str]) -> dict[str, Any] | None:
    parsed = _parse_fact(expected_fact)
    if parsed is None:
        return None
    constant_positions = _constant_positions(parsed)
    if not constant_positions:
        return None
    candidates = _same_signature_candidates(parsed, compile_facts)
    for compiled_fact, candidate in candidates:
        bindings = _bindings(parsed, candidate)
        if bindings is None:
            continue
        if all(parsed["args"][index] == candidate["args"][index] for index in constant_positions):
            return {
                "compiled_fact": compiled_fact,
                "signature": _signature(parsed),
                "bindings": bindings,
                "matched_constant_positions": constant_positions,
                "total_constant_slots": len(constant_positions),
                "carrier_candidate_count": len(candidates),
            }
    return None


def _partial_match(expected_fact: str, compile_facts: list[str]) -> dict[str, Any] | None:
    parsed = _parse_fact(expected_fact)
    if parsed is None:
        return None
    constant_positions = _constant_positions(parsed)
    if not constant_positions:
        return None
    primary_position = constant_positions[0]
    candidates = _same_signature_candidates(parsed, compile_facts)
    best: dict[str, Any] | None = None
    for compiled_fact, candidate in candidates:
        if parsed["args"][primary_position] != candidate["args"][primary_position]:
            continue
        matched_positions = [
            index for index in constant_positions if parsed["args"][index] == candidate["args"][index]
        ]
        if len(matched_positions) == len(constant_positions):
            continue
        bindings = _bindings(parsed, candidate) or {}
        differing = [index for index in constant_positions if index not in matched_positions]
        item = {
            "compiled_fact": compiled_fact,
            "signature": _signature(parsed),
            "bindings": bindings,
            "matched_constant_positions": matched_positions,
            "differing_constant_positions": differing,
            "difference_text": _difference_text(parsed, candidate, differing),
            "total_constant_slots": len(constant_positions),
            "carrier_candidate_count": len(candidates),
        }
        if best is None or len(item["matched_constant_positions"]) > len(best["matched_constant_positions"]):
            best = item
    return best


def _miss_detail(expected_fact: str, compile_facts: list[str]) -> dict[str, Any]:
    parsed = _parse_fact(expected_fact)
    if parsed is None:
        return {
            "rationale": "Oracle fact is not parseable as a Prolog fact.",
            "match_detail": {"carrier_candidate_count": 0, "total_constant_slots": 0},
        }
    candidates = _same_signature_candidates(parsed, compile_facts)
    constant_positions = _constant_positions(parsed)
    if not constant_positions:
        rationale = "Oracle fact has no constant slots; all-variable facts are not answer-bearing."
    elif candidates:
        primary = parsed["args"][constant_positions[0]]
        rationale = (
            f"Compile artifact has {len(candidates)} {_signature(parsed)} fact(s) but none match "
            f"the primary oracle constant '{primary}'; not compile-supported."
        )
    else:
        rationale = f"Compile artifact has no {_signature(parsed)} fact(s); not compile-supported."
    return {
        "rationale": rationale,
        "match_detail": {
            "carrier_candidate_count": len(candidates),
            "total_constant_slots": len(constant_positions),
        },
    }


def _query_result(
    *,
    expected_fact: str,
    parsed: dict[str, Any] | None,
    status: str,
    compiled_fact: str,
    bindings: dict[str, str],
) -> dict[str, Any]:
    predicate = str((parsed or {}).get("predicate") or "").strip()
    row: dict[str, str] = {}
    if compiled_fact:
        row["compiled_fact"] = compiled_fact
    row.update(bindings)
    rows = [row] if row else []
    return {
        "predicate": predicate,
        "status": status,
        "num_rows": len(rows),
        "rows": rows,
    }


def _same_signature_candidates(
    expected: dict[str, Any],
    compile_facts: list[str],
) -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []
    predicate = str(expected.get("predicate") or "")
    arity = len(expected.get("args") or [])
    for fact in compile_facts:
        parsed = _parse_fact(fact)
        if parsed is None:
            continue
        if str(parsed.get("predicate") or "") != predicate:
            continue
        if len(parsed.get("args") or []) != arity:
            continue
        out.append((fact, parsed))
    return out


def _constant_positions(parsed: dict[str, Any]) -> list[int]:
    return [
        index
        for index, arg in enumerate(parsed.get("args") or [])
        if not _is_expected_variable(str(arg).strip())
    ]


def _bindings(expected: dict[str, Any], candidate: dict[str, Any]) -> dict[str, str] | None:
    out: dict[str, str] = {}
    for expected_arg, actual_arg in zip(expected.get("args") or [], candidate.get("args") or []):
        expected_text = str(expected_arg).strip()
        actual_text = str(actual_arg).strip()
        if _is_expected_variable(expected_text):
            bound = out.get(expected_text)
            if bound is not None and bound != actual_text:
                return None
            out[expected_text] = actual_text
    return out


def _difference_text(expected: dict[str, Any], candidate: dict[str, Any], positions: list[int]) -> str:
    parts: list[str] = []
    for position in positions:
        oracle = str(expected["args"][position]).strip()
        compiled = str(candidate["args"][position]).strip()
        parts.append(f"pos{position}: oracle '{oracle}' vs compile '{compiled}'")
    return "; ".join(parts) if parts else "none"


def _signature(parsed: dict[str, Any] | None) -> str:
    if parsed is None:
        return ""
    return f"{parsed.get('predicate')}/{len(parsed.get('args') or [])}"


def _parse_fixture_runs(values: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for value in values:
        text = str(value or "").strip()
        match = re.fullmatch(r"([^:=]+):([^=]+)=(.+)", text)
        if not match:
            raise SystemExit(f"--fixture-run must be FIXTURE_ID:RUN_ID=PATH, got: {value}")
        out.append(
            {
                "fixture_id": match.group(1).strip(),
                "run_id": match.group(2).strip(),
                "compile_json": str(Path(match.group(3).strip())),
            }
        )
    return out


def _parse_domain_lens_bundles(values: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for value in values:
        text = str(value or "").strip()
        match = re.fullmatch(r"([^=]+)=(.+)", text)
        if not match:
            raise SystemExit(f"--domain-lens-bundle must be FIXTURE_ID=PATH, got: {value}")
        fixture_id = match.group(1).strip()
        bundle_root = Path(match.group(2).strip())
        union_root = bundle_root / "unions"
        if not union_root.is_dir():
            raise SystemExit(f"--domain-lens-bundle has no unions directory: {union_root}")
        seen_run_ids: set[str] = set()
        for run_dir in sorted(path for path in union_root.iterdir() if path.is_dir()):
            json_files = sorted(run_dir.glob("*.json"))
            if not json_files:
                raise SystemExit(f"No union compile JSON found under {run_dir}")
            if len(json_files) > 1:
                raise SystemExit(f"Ambiguous union compile JSONs under {run_dir}: {json_files}")
            out.append(
                {
                    "fixture_id": fixture_id,
                    "run_id": run_dir.name,
                    "compile_json": str(json_files[0]),
                }
            )
            seen_run_ids.add(run_dir.name)
        for json_file in sorted(union_root.glob("*.json")):
            run_id = _run_id_from_union_file(json_file)
            if run_id in seen_run_ids:
                raise SystemExit(f"Duplicate run id {run_id} in {union_root}")
            out.append(
                {
                    "fixture_id": fixture_id,
                    "run_id": run_id,
                    "compile_json": str(json_file),
                }
            )
            seen_run_ids.add(run_id)
    return out


def _run_id_from_union_file(path: Path) -> str:
    match = re.search(r"(?:^|[-_])run(\d+)(?:[-_.]|$)", path.name)
    if match:
        return f"run{match.group(1)}"
    return path.stem


def _support_summary_by_fixture(files: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    by_fixture: dict[str, dict[str, Counter[str]]] = defaultdict(dict)
    runs_by_fixture: dict[str, set[str]] = defaultdict(set)
    for item in files:
        payload = item["payload"]
        fixture_id = str(payload["fixture"])
        runs_by_fixture[fixture_id].add(str(payload["run_id"]))
        for row in payload["rows"]:
            reference = str(row["reference_answer"])
            verdict = str(row["reference_judge"]["verdict"])
            by_fixture[fixture_id].setdefault(reference, Counter())[verdict] += 1

    out: dict[str, dict[str, int]] = {}
    for fixture_id in sorted(by_fixture):
        counters = list(by_fixture[fixture_id].values())
        out[fixture_id] = {
            "reference_count": len(counters),
            "runs_seen": len(runs_by_fixture[fixture_id]),
            "exact_support_ge_2": sum(1 for counter in counters if counter["exact"] >= 2),
            "exact_support_ge_1": sum(1 for counter in counters if counter["exact"] >= 1),
            "zero_exact_support": sum(1 for counter in counters if counter["exact"] == 0),
            "partial_support_ge_1": sum(1 for counter in counters if counter["partial"] >= 1),
            "miss_support_ge_1": sum(1 for counter in counters if counter["miss"] >= 1),
        }
    return out


def _readme_text(manifest: dict[str, Any]) -> str:
    return (
        "# Compile-Fact Judged QA Bundle\n\n"
        "Deterministic judged-QA artifacts generated from expected Prolog facts "
        "and compile JSON typed facts.\n\n"
        "This bundle does not use source prose, model judging, or oracle "
        "rewrites. `exact` means a same-predicate/same-arity compiled fact "
        "matched every oracle constant slot. Prolog variables are wildcards and "
        "are reported as bindings. `partial` means the primary oracle constant "
        "matched but at least one other constant slot differed. `miss` means no "
        "supporting compiled fact matched the primary constant. The manifest also "
        "prints a compact support>=2 summary by fixture for N-cycle compile work.\n\n"
        f"Files: {', '.join(manifest.get('files', []))}\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
