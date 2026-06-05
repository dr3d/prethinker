#!/usr/bin/env python3
"""Validate compile-only typed micro-fixtures.

Micro-fixtures are tiny source snippets paired with expected typed facts. They
exercise compile recall without QA wording, source-ledger retrieval, or a judge.
This script can run as a static manifest/fact sanity check, and can optionally
compare expected facts against a supplied compile artifact.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.carrier_contract_registry import carrier_contract  # noqa: E402


FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")
DEFAULT_ROOT = REPO_ROOT / "datasets" / "compile_micro_fixtures"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument(
        "--compile-json",
        action="append",
        default=[],
        metavar="FIXTURE_ID=PATH",
        help="Optional compile artifact to compare against one micro-fixture.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    compile_map = _parse_compile_map(args.compile_json)
    report = build_report(root=args.root, compile_map=compile_map)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if args.exit_zero or not report["summary"]["blocking_errors"] else 1


def build_report(*, root: Path = DEFAULT_ROOT, compile_map: dict[str, Path] | None = None) -> dict[str, Any]:
    compile_map = compile_map or {}
    rows: list[dict[str, Any]] = []
    for manifest_path in sorted(root.glob("*/manifest.json")):
        fixture_dir = manifest_path.parent
        manifest = _load_json(manifest_path)
        fixture_id = str(manifest.get("fixture_id") or fixture_dir.name).strip()
        source_path = fixture_dir / _manifest_file(manifest, "source", default="source.md")
        expected_path = fixture_dir / _manifest_file(manifest, "expected_facts", default="expected_facts.pl")
        alternatives_file = _manifest_file(manifest, "expected_alternatives", default="")
        forbidden_file = _manifest_file(manifest, "forbidden_facts", default="")
        alternatives_path = fixture_dir / alternatives_file
        forbidden_path = fixture_dir / forbidden_file
        expected_facts = _load_fact_lines(expected_path)
        expected_alternatives = _load_alternative_groups(alternatives_path) if alternatives_file.strip() else []
        forbidden_facts = _load_fact_lines(forbidden_path) if forbidden_file.strip() else []
        errors: list[str] = []
        if not source_path.exists():
            errors.append("missing_source")
        if not expected_path.exists():
            errors.append("missing_expected_facts")
        for fact in expected_facts:
            parsed = _parse_fact(fact)
            if parsed is None:
                errors.append(f"invalid_fact:{fact}")
                continue
            signature = f"{parsed['predicate']}/{len(parsed['args'])}"
            if carrier_contract(signature) is None:
                errors.append(f"unregistered_signature:{signature}")
        for group in expected_alternatives:
            for alternative in group.get("any_of", []):
                for fact in alternative.get("facts", []):
                    parsed = _parse_fact(str(fact))
                    if parsed is None:
                        errors.append(f"invalid_alternative_fact:{group.get('id', '')}:{fact}")
                        continue
                    signature = f"{parsed['predicate']}/{len(parsed['args'])}"
                    if carrier_contract(signature) is None:
                        errors.append(f"unregistered_alternative_signature:{group.get('id', '')}:{signature}")
        for fact in forbidden_facts:
            parsed = _parse_fact(fact)
            if parsed is None:
                errors.append(f"invalid_forbidden_fact:{fact}")
                continue
            signature = f"{parsed['predicate']}/{len(parsed['args'])}"
            if carrier_contract(signature) is None:
                errors.append(f"unregistered_forbidden_signature:{signature}")
        compile_path = compile_map.get(fixture_id)
        compile_result: dict[str, Any] = {}
        if compile_path is not None:
            compile_facts = _facts_from_compile_json(compile_path)
            match_report = _match_expected_facts(expected_facts, compile_facts)
            missing = list(match_report["missing_expected_facts"])
            alternatives_report = _match_alternative_groups(
                expected_alternatives,
                compile_facts,
                match_report["variable_bindings"],
            )
            forbidden_report = _match_expected_facts(
                _apply_bindings_to_facts(forbidden_facts, alternatives_report["variable_bindings"]),
                compile_facts,
            )
            forbidden_matches = [
                fact
                for fact in _apply_bindings_to_facts(forbidden_facts, alternatives_report["variable_bindings"])
                if fact not in forbidden_report["missing_expected_facts"]
            ]
            compile_result = {
                "compile_json": str(compile_path),
                "expected_fact_count": len(expected_facts),
                "matched_fact_count": int(match_report["matched_fact_count"]),
                "missing_expected_facts": missing,
                "expected_alternative_group_count": len(expected_alternatives),
                "matched_alternative_group_count": int(alternatives_report["matched_group_count"]),
                "missing_expected_alternatives": alternatives_report["missing_expected_alternatives"],
                "selected_alternatives": alternatives_report["selected_alternatives"],
                "forbidden_fact_count": len(forbidden_facts),
                "matched_forbidden_facts": forbidden_matches,
                "variable_bindings": alternatives_report["variable_bindings"],
                "passed": not missing and not alternatives_report["missing_expected_alternatives"] and not forbidden_matches,
            }
            if missing:
                errors.append("compile_missing_expected_facts")
            if alternatives_report["missing_expected_alternatives"]:
                errors.append("compile_missing_expected_alternatives")
            if forbidden_matches:
                errors.append("compile_emitted_forbidden_facts")
        rows.append(
            {
                "fixture_id": fixture_id,
                "path": str(fixture_dir),
                "source": str(source_path),
                "expected_facts": str(expected_path),
                "expected_fact_count": len(expected_facts),
                "expected_alternative_group_count": len(expected_alternatives),
                "forbidden_fact_count": len(forbidden_facts),
                "errors": errors,
                "compile_result": compile_result,
            }
        )
    blocking = [row for row in rows if row["errors"]]
    return {
        "schema_version": "typed_micro_fixture_validation_v1",
        "root": str(root),
        "summary": {
            "fixture_count": len(rows),
            "blocking_errors": len(blocking),
            "fixtures_with_compile_artifacts": sum(1 for row in rows if row["compile_result"]),
        },
        "rows": rows,
    }


def _manifest_file(manifest: dict[str, Any], key: str, *, default: str) -> str:
    value = manifest.get(key)
    if str(value or "").strip():
        return str(value).strip()
    files = manifest.get("files")
    if isinstance(files, dict) and str(files.get(key) or "").strip():
        return str(files[key]).strip()
    return default


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Typed Micro-Fixture Validation",
        "",
        f"- Root: `{report.get('root', '')}`",
        f"- Fixtures: `{report['summary']['fixture_count']}`",
        f"- Blocking errors: `{report['summary']['blocking_errors']}`",
        f"- Fixtures with compile artifacts: `{report['summary']['fixtures_with_compile_artifacts']}`",
        "",
        "| Fixture | Expected facts | Forbidden facts | Errors | Compile result |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for row in report.get("rows", []):
        compile_result = row.get("compile_result") or {}
        if compile_result:
            fact_count = int(compile_result.get("expected_fact_count", 0))
            group_count = int(compile_result.get("expected_alternative_group_count", 0))
            matched = int(compile_result.get("matched_fact_count", 0)) + int(
                compile_result.get("matched_alternative_group_count", 0)
            )
            result = f"{matched}/{fact_count + group_count}"
        else:
            result = ""
        forbidden = compile_result.get("matched_forbidden_facts", []) if compile_result else []
        if result and forbidden:
            result = f"{result}; forbidden={len(forbidden)}"
        lines.append(
            "| `{}` | {} | {} | `{}` | `{}` |".format(
                row.get("fixture_id", ""),
                row.get("expected_fact_count", 0),
                row.get("forbidden_fact_count", 0),
                row.get("errors", []),
                result,
            )
        )
    return "\n".join(lines) + "\n"


def _parse_compile_map(values: list[str]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for value in values:
        if "=" not in str(value):
            raise SystemExit(f"--compile-json must be FIXTURE_ID=PATH, got: {value}")
        fixture_id, path = str(value).split("=", 1)
        out[fixture_id.strip()] = Path(path.strip())
    return out


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_fact_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith("%")]


def _load_alternative_groups(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = _load_json(path)
    groups = data.get("groups", []) if isinstance(data, dict) else []
    out: list[dict[str, Any]] = []
    for index, group in enumerate(groups):
        if not isinstance(group, dict):
            continue
        group_id = str(group.get("id") or f"group_{index + 1}").strip()
        alternatives: list[dict[str, Any]] = []
        for alt_index, alternative in enumerate(group.get("any_of", [])):
            if isinstance(alternative, dict):
                facts = [
                    str(fact).strip()
                    for fact in alternative.get("facts", [])
                    if str(fact).strip()
                ]
                alt_id = str(alternative.get("id") or f"alternative_{alt_index + 1}").strip()
            elif isinstance(alternative, list):
                facts = [str(fact).strip() for fact in alternative if str(fact).strip()]
                alt_id = f"alternative_{alt_index + 1}"
            else:
                continue
            alternatives.append({"id": alt_id, "facts": facts})
        out.append({"id": group_id, "any_of": alternatives})
    return out


def _facts_from_compile_json(path: Path) -> list[str]:
    data = _load_json(path)
    source_compile = data.get("source_compile")
    if isinstance(source_compile, dict) and isinstance(source_compile.get("facts"), list):
        return [str(fact).strip() for fact in source_compile.get("facts", []) if str(fact).strip()]
    if isinstance(data.get("facts"), list):
        return [str(fact).strip() for fact in data.get("facts", []) if str(fact).strip()]
    return []


def _parse_fact(fact: str) -> dict[str, Any] | None:
    match = FACT_RE.match(fact)
    if not match:
        return None
    args = _split_args(match.group(2))
    return {"predicate": match.group(1), "args": args}


def _match_expected_facts(
    expected_facts: list[str],
    compile_facts: list[str],
    initial_bindings: dict[str, str] | None = None,
) -> dict[str, Any]:
    expected = [(fact, _parse_fact(fact)) for fact in expected_facts]
    actual = [(fact, _parse_fact(fact)) for fact in dict.fromkeys(compile_facts)]
    actual_index = _actual_fact_index(actual)
    matched, bindings = _match_expected_backtrack(
        expected,
        actual,
        0,
        dict(initial_bindings or {}),
        actual_index=actual_index,
        memo={},
    )
    missing = [fact for fact, parsed in expected if fact not in matched]
    return {
        "matched_fact_count": len(matched),
        "missing_expected_facts": missing,
        "variable_bindings": bindings,
    }


def _match_alternative_groups(
    groups: list[dict[str, Any]],
    compile_facts: list[str],
    initial_bindings: dict[str, str],
) -> dict[str, Any]:
    matched, bindings, selected = _match_alternative_groups_backtrack(groups, compile_facts, 0, dict(initial_bindings), [])
    matched_ids = {item["group_id"] for item in selected}
    missing = [str(group.get("id") or "") for group in groups if str(group.get("id") or "") not in matched_ids]
    return {
        "matched_group_count": matched,
        "missing_expected_alternatives": missing,
        "selected_alternatives": selected,
        "variable_bindings": bindings,
    }


def _match_alternative_groups_backtrack(
    groups: list[dict[str, Any]],
    compile_facts: list[str],
    index: int,
    bindings: dict[str, str],
    selected: list[dict[str, str]],
) -> tuple[int, dict[str, str], list[dict[str, str]]]:
    if index >= len(groups):
        return len(selected), dict(bindings), list(selected)
    group = groups[index]
    group_id = str(group.get("id") or f"group_{index + 1}").strip()
    best_count, best_bindings, best_selected = _match_alternative_groups_backtrack(
        groups,
        compile_facts,
        index + 1,
        bindings,
        selected,
    )
    for alternative in group.get("any_of", []):
        alt_id = str(alternative.get("id") or "").strip()
        facts = [str(fact).strip() for fact in alternative.get("facts", []) if str(fact).strip()]
        if not facts:
            continue
        report = _match_expected_facts(facts, compile_facts, bindings)
        if report["matched_fact_count"] != len(facts):
            continue
        alt_selected = [
            *selected,
            {"group_id": group_id, "alternative_id": alt_id},
        ]
        count, next_bindings, next_selected = _match_alternative_groups_backtrack(
            groups,
            compile_facts,
            index + 1,
            report["variable_bindings"],
            alt_selected,
        )
        if count > best_count:
            best_count = count
            best_bindings = next_bindings
            best_selected = next_selected
            if best_count == len(groups) - index:
                return best_count, best_bindings, best_selected
    return best_count, best_bindings, best_selected


def _apply_bindings_to_facts(facts: list[str], bindings: dict[str, str]) -> list[str]:
    rendered: list[str] = []
    for fact in facts:
        parsed = _parse_fact(fact)
        if parsed is None:
            rendered.append(fact)
            continue
        args = [bindings.get(str(arg).strip(), str(arg).strip()) for arg in parsed["args"]]
        rendered.append(f"{parsed['predicate']}({', '.join(args)}).")
    return rendered


def _match_expected_backtrack(
    expected: list[tuple[str, dict[str, Any] | None]],
    actual: list[tuple[str, dict[str, Any] | None]],
    index: int,
    bindings: dict[str, str],
    *,
    actual_index: dict[tuple[str, int], list[tuple[str, dict[str, Any] | None]]] | None = None,
    memo: dict[tuple[int, tuple[tuple[str, str], ...]], tuple[set[str], dict[str, str]]] | None = None,
) -> tuple[set[str], dict[str, str]]:
    if index >= len(expected):
        return set(), dict(bindings)
    memo_key = (index, tuple(sorted(bindings.items())))
    if memo is not None and memo_key in memo:
        cached_matched, cached_bindings = memo[memo_key]
        return set(cached_matched), dict(cached_bindings)
    fact_text, pattern = expected[index]
    if pattern is None:
        matched_tail, tail_bindings = _match_expected_backtrack(
            expected,
            actual,
            index + 1,
            bindings,
            actual_index=actual_index,
            memo=memo,
        )
        result = (matched_tail, tail_bindings)
        if memo is not None:
            memo[memo_key] = (set(result[0]), dict(result[1]))
        return result
    best_matched: set[str] = set()
    best_bindings = dict(bindings)
    candidates = actual
    if actual_index is not None:
        key = (str(pattern.get("predicate") or ""), len(pattern.get("args") or []))
        candidates = actual_index.get(key, [])
    for _actual_text, candidate in candidates:
        trial = _unify_fact_pattern(pattern, candidate, bindings)
        if trial is None:
            continue
        tail_matched, tail_bindings = _match_expected_backtrack(
            expected,
            actual,
            index + 1,
            trial,
            actual_index=actual_index,
            memo=memo,
        )
        current = {fact_text, *tail_matched}
        if len(current) > len(best_matched):
            best_matched = current
            best_bindings = tail_bindings
            if len(best_matched) == len(expected) - index:
                result = (best_matched, best_bindings)
                if memo is not None:
                    memo[memo_key] = (set(result[0]), dict(result[1]))
                return result
    tail_matched, tail_bindings = _match_expected_backtrack(
        expected,
        actual,
        index + 1,
        bindings,
        actual_index=actual_index,
        memo=memo,
    )
    if len(tail_matched) > len(best_matched):
        result = (tail_matched, tail_bindings)
    else:
        result = (best_matched, best_bindings)
    if memo is not None:
        memo[memo_key] = (set(result[0]), dict(result[1]))
    return result


def _actual_fact_index(
    actual: list[tuple[str, dict[str, Any] | None]],
) -> dict[tuple[str, int], list[tuple[str, dict[str, Any] | None]]]:
    out: dict[tuple[str, int], list[tuple[str, dict[str, Any] | None]]] = {}
    for fact_text, parsed in actual:
        if parsed is None:
            continue
        key = (str(parsed.get("predicate") or ""), len(parsed.get("args") or []))
        out.setdefault(key, []).append((fact_text, parsed))
    return out


def _unify_fact_pattern(
    pattern: dict[str, Any],
    candidate: dict[str, Any] | None,
    bindings: dict[str, str],
) -> dict[str, str] | None:
    if candidate is None:
        return None
    if pattern.get("predicate") != candidate.get("predicate"):
        return None
    pattern_args = list(pattern.get("args") or [])
    candidate_args = list(candidate.get("args") or [])
    if len(pattern_args) != len(candidate_args):
        return None
    out = dict(bindings)
    for expected_arg, actual_arg in zip(pattern_args, candidate_args):
        expected_text = str(expected_arg).strip()
        actual_text = str(actual_arg).strip()
        if _is_expected_variable(expected_text):
            if expected_text == "_":
                continue
            bound = out.get(expected_text)
            if bound is not None and bound != actual_text:
                return None
            out[expected_text] = actual_text
            continue
        if expected_text != actual_text:
            return None
    return out


def _is_expected_variable(value: str) -> bool:
    return bool(re.fullmatch(r"(?:[A-Z][A-Za-z0-9_]*|_[A-Za-z0-9_]*)", str(value or "").strip()))


def _split_args(raw: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escape = False
    depth = 0
    for char in raw:
        if quote:
            current.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char == "(":
            depth += 1
            current.append(char)
            continue
        if char == ")":
            depth = max(0, depth - 1)
            current.append(char)
            continue
        if char == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if current or raw.strip():
        args.append("".join(current).strip())
    return args


if __name__ == "__main__":
    raise SystemExit(main())
