#!/usr/bin/env python3
"""
Differential validation for vendored Prolog engine behavior.

Compares a curated behavior suite against:
- vendored engine in this repo (`engine/core.py`)
- reference engine from prior repo baseline (`../prolog-reasoning/src/engine/core.py` by default)

Publishes agreement rates across categories:
- unification
- recursion
- negation
- backtracking
- findall
- retraction_behavior
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE_REPO = (ROOT.parent / "prolog-reasoning").resolve()

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.core import Clause, PrologEngine, Term


@dataclass(frozen=True)
class DifferentialCase:
    name: str
    category: str
    steps: list[dict[str, str]]


def _utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _normalize_clause(clause: str) -> str:
    text = (clause or "").strip()
    if not text:
        return ""
    if not text.endswith("."):
        text += "."
    return text


def _split_top_level(text: str, delimiter: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    paren_depth = 0
    bracket_depth = 0
    for ch in text:
        if ch == "(":
            paren_depth += 1
            current.append(ch)
            continue
        if ch == ")":
            paren_depth = max(0, paren_depth - 1)
            current.append(ch)
            continue
        if ch == "[":
            bracket_depth += 1
            current.append(ch)
            continue
        if ch == "]":
            bracket_depth = max(0, bracket_depth - 1)
            current.append(ch)
            continue
        if ch == delimiter and paren_depth == 0 and bracket_depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue
        current.append(ch)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _contains_variable(term: Any) -> bool:
    if getattr(term, "is_variable", False):
        return True
    return any(_contains_variable(arg) for arg in getattr(term, "args", []))


def _collect_query_variables(term: Any) -> list[str]:
    names: list[str] = []

    def walk(node: Any) -> None:
        if getattr(node, "is_variable", False):
            name = str(getattr(node, "name", ""))
            if name and name not in names:
                names.append(name)
        for arg in getattr(node, "args", []):
            walk(arg)

    walk(term)
    return names


def _canonical_rows(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    cleaned: list[dict[str, str]] = []
    for row in rows:
        normalized_row = {str(k): str(v) for k, v in row.items()}
        cleaned.append(normalized_row)
    cleaned.sort(key=lambda r: json.dumps(r, sort_keys=True))
    return cleaned


class RuntimeAdapter:
    def __init__(self, *, engine_cls: Any, clause_cls: Any, term_cls: Any, max_depth: int = 500) -> None:
        self.engine = engine_cls(max_depth=max_depth)
        self._Clause = clause_cls
        self._Term = term_cls

    def _parse_term(self, text: str) -> Any:
        normalized = _normalize_clause(text)
        if normalized.endswith("."):
            normalized = normalized[:-1].strip()
        if not normalized:
            raise ValueError("Empty term.")
        return self.engine.parse_term(normalized)

    def assert_fact(self, clause: str) -> dict[str, Any]:
        normalized = _normalize_clause(clause)
        if not normalized:
            return {"status": "validation_error", "message": "Empty fact clause."}
        if ":-" in normalized:
            return {"status": "validation_error", "message": "Fact clause contains rule operator."}
        try:
            fact_term = self._parse_term(normalized)
        except Exception as error:  # pragma: no cover - defensive
            return {"status": "validation_error", "message": f"Fact parse failed: {error}"}
        if _contains_variable(fact_term):
            return {"status": "validation_error", "message": "Fact must be ground (no variables)."}
        for existing in self.engine.clauses:
            if existing.head == fact_term and not existing.body:
                return {"status": "success", "result_type": "fact_asserted", "fact": normalized}
        self.engine.add_clause(self._Clause(fact_term))
        return {"status": "success", "result_type": "fact_asserted", "fact": normalized}

    def assert_rule(self, clause: str) -> dict[str, Any]:
        normalized = _normalize_clause(clause)
        if not normalized:
            return {"status": "validation_error", "message": "Empty rule clause."}
        raw = normalized[:-1].strip() if normalized.endswith(".") else normalized
        if ":-" not in raw:
            return {"status": "validation_error", "message": "Rule clause missing ':-'."}
        try:
            head_text, body_text = raw.split(":-", 1)
            head_term = self._parse_term(head_text)
            body_terms = [self._parse_term(part) for part in _split_top_level(body_text.strip(), ",")]
            if not body_terms:
                return {"status": "validation_error", "message": "Rule body is empty."}
        except Exception as error:  # pragma: no cover - defensive
            return {"status": "validation_error", "message": f"Rule parse failed: {error}"}
        rule_clause = self._Clause(head_term, body_terms)
        for existing in self.engine.clauses:
            if existing.head == rule_clause.head and (existing.body or []) == rule_clause.body:
                return {"status": "success", "result_type": "rule_asserted", "rule": normalized}
        self.engine.add_clause(rule_clause)
        return {"status": "success", "result_type": "rule_asserted", "rule": normalized}

    def retract_fact(self, clause: str) -> dict[str, Any]:
        normalized = _normalize_clause(clause)
        if not normalized:
            return {"status": "validation_error", "message": "Empty retract clause."}
        if ":-" in normalized:
            return {"status": "validation_error", "message": "Retract target cannot be a rule."}
        try:
            fact_term = self._parse_term(normalized)
        except Exception as error:  # pragma: no cover - defensive
            return {"status": "validation_error", "message": f"Retract parse failed: {error}"}
        if _contains_variable(fact_term):
            return {"status": "validation_error", "message": "Retract target must be ground (no variables)."}
        for idx, existing in enumerate(self.engine.clauses):
            if existing.head == fact_term and not existing.body:
                del self.engine.clauses[idx]
                return {"status": "success", "result_type": "fact_retracted", "fact": normalized}
        return {"status": "no_results", "result_type": "no_result", "fact": normalized}

    def query_rows(self, query: str) -> dict[str, Any]:
        normalized = _normalize_clause(query)
        try:
            query_term = self._parse_term(normalized)
            variable_names = _collect_query_variables(query_term)
            solutions = self.engine.resolve(query_term)
        except Exception as error:
            return {
                "status": "error",
                "message": str(error),
                "rows": [],
                "num_rows": 0,
                "variables": [],
            }
        if not solutions:
            return {
                "status": "no_results",
                "rows": [],
                "num_rows": 0,
                "variables": variable_names,
            }
        rows: list[dict[str, str]] = []
        seen: set[str] = set()
        if variable_names:
            for solution in solutions:
                row: dict[str, str] = {}
                for var_name in variable_names:
                    bound = solution.apply(self._Term(var_name, is_variable=True))
                    row[var_name] = str(bound)
                key = json.dumps(row, sort_keys=True)
                if key in seen:
                    continue
                seen.add(key)
                rows.append(row)
        else:
            rows.append({})
        rows = _canonical_rows(rows)
        return {
            "status": "success",
            "rows": rows,
            "num_rows": len(rows),
            "variables": variable_names,
        }


def _load_reference_core_module(reference_repo: Path) -> Any:
    path = (reference_repo / "src" / "engine" / "core.py").resolve()
    if not path.exists():
        raise FileNotFoundError(f"Reference engine not found: {path}")
    spec = importlib.util.spec_from_file_location("reference_engine_core", str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module spec from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build_cases() -> list[DifferentialCase]:
    return [
        DifferentialCase(
            name="unification_var_atom",
            category="unification",
            steps=[{"op": "query", "query": "=(X, alice)."}],
        ),
        DifferentialCase(
            name="unification_compound",
            category="unification",
            steps=[{"op": "query", "query": "=(parent(X, bob), parent(alice, Y))."}],
        ),
        DifferentialCase(
            name="recursion_transitive_closure",
            category="recursion",
            steps=[
                {"op": "assert_fact", "clause": "parent(alice, bob)."},
                {"op": "assert_fact", "clause": "parent(bob, carol)."},
                {"op": "assert_rule", "clause": "ancestor(X, Y) :- parent(X, Y)."},
                {"op": "assert_rule", "clause": "ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z)."},
                {"op": "query", "query": "ancestor(alice, carol)."},
            ],
        ),
        DifferentialCase(
            name="backtracking_multiple_bindings",
            category="backtracking",
            steps=[
                {"op": "assert_fact", "clause": "parent(john, alice)."},
                {"op": "assert_fact", "clause": "parent(john, bob)."},
                {"op": "query", "query": "parent(john, X)."},
            ],
        ),
        DifferentialCase(
            name="negation_as_failure_allows_non_penguin",
            category="negation",
            steps=[
                {"op": "assert_fact", "clause": "bird(tweety)."},
                {"op": "assert_fact", "clause": "bird(polly)."},
                {"op": "assert_fact", "clause": "penguin(polly)."},
                {"op": "assert_rule", "clause": "can_fly(X) :- bird(X), \\+(penguin(X))."},
                {"op": "query", "query": "can_fly(tweety)."},
            ],
        ),
        DifferentialCase(
            name="negation_as_failure_blocks_penguin",
            category="negation",
            steps=[
                {"op": "assert_fact", "clause": "bird(polly)."},
                {"op": "assert_fact", "clause": "penguin(polly)."},
                {"op": "assert_rule", "clause": "can_fly(X) :- bird(X), \\+(penguin(X))."},
                {"op": "query", "query": "can_fly(polly)."},
            ],
        ),
        DifferentialCase(
            name="findall_collects_bindings",
            category="findall",
            steps=[
                {"op": "assert_fact", "clause": "parent(john, alice)."},
                {"op": "assert_fact", "clause": "parent(john, bob)."},
                {"op": "query", "query": "findall(X, parent(john, X), L)."},
            ],
        ),
        DifferentialCase(
            name="findall_matches_ground_list",
            category="findall",
            steps=[
                {"op": "assert_fact", "clause": "parent(john, alice)."},
                {"op": "assert_fact", "clause": "parent(john, bob)."},
                {"op": "query", "query": "findall(X, parent(john, X), [alice, bob])."},
            ],
        ),
        DifferentialCase(
            name="retract_existing_fact",
            category="retraction_behavior",
            steps=[
                {"op": "assert_fact", "clause": "parent(alice, bob)."},
                {"op": "query", "query": "parent(alice, bob)."},
                {"op": "retract_fact", "clause": "parent(alice, bob)."},
                {"op": "query", "query": "parent(alice, bob)."},
            ],
        ),
        DifferentialCase(
            name="retract_missing_fact_no_results",
            category="retraction_behavior",
            steps=[
                {"op": "retract_fact", "clause": "parent(nope, ghost)."},
                {"op": "query", "query": "parent(nope, ghost)."},
            ],
        ),
    ]


def _execute_case(runtime: RuntimeAdapter, case: DifferentialCase) -> list[dict[str, Any]]:
    steps_out: list[dict[str, Any]] = []
    for idx, step in enumerate(case.steps, start=1):
        op = str(step.get("op", "")).strip()
        if op == "assert_fact":
            result = runtime.assert_fact(step["clause"])
            steps_out.append(
                {
                    "idx": idx,
                    "op": op,
                    "status": str(result.get("status", "")),
                    "result_type": str(result.get("result_type", "")),
                }
            )
            continue
        if op == "assert_rule":
            result = runtime.assert_rule(step["clause"])
            steps_out.append(
                {
                    "idx": idx,
                    "op": op,
                    "status": str(result.get("status", "")),
                    "result_type": str(result.get("result_type", "")),
                }
            )
            continue
        if op == "retract_fact":
            result = runtime.retract_fact(step["clause"])
            steps_out.append(
                {
                    "idx": idx,
                    "op": op,
                    "status": str(result.get("status", "")),
                    "result_type": str(result.get("result_type", "")),
                }
            )
            continue
        if op == "query":
            result = runtime.query_rows(step["query"])
            rows = _canonical_rows(result.get("rows", []) if isinstance(result.get("rows"), list) else [])
            steps_out.append(
                {
                    "idx": idx,
                    "op": op,
                    "status": str(result.get("status", "")),
                    "num_rows": int(result.get("num_rows", 0) or 0),
                    "rows": rows,
                    "variables": list(result.get("variables", [])) if isinstance(result.get("variables"), list) else [],
                }
            )
            continue
        raise ValueError(f"Unsupported case op: {op}")
    return steps_out


def _first_difference(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> str:
    if len(left) != len(right):
        return f"step_count_mismatch: left={len(left)} right={len(right)}"
    for idx, (l_step, r_step) in enumerate(zip(left, right), start=1):
        if l_step != r_step:
            return (
                f"step_{idx}_mismatch: left={json.dumps(l_step, sort_keys=True)} "
                f"right={json.dumps(r_step, sort_keys=True)}"
            )
    return ""


def _compute_category_rates(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, dict[str, int]] = {}
    for row in rows:
        category = str(row.get("category", "uncategorized"))
        bucket = grouped.setdefault(category, {"total": 0, "agreed": 0})
        bucket["total"] += 1
        if bool(row.get("agreement")):
            bucket["agreed"] += 1
    out: dict[str, Any] = {}
    for category, values in sorted(grouped.items()):
        total = values["total"]
        agreed = values["agreed"]
        rate = (agreed / total) if total else 0.0
        out[category] = {
            "total_cases": total,
            "agreed_cases": agreed,
            "agreement_rate": round(rate, 4),
        }
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run differential validation against reference Prolog engine.")
    parser.add_argument(
        "--reference-repo",
        default=str(DEFAULT_REFERENCE_REPO),
        help="Path to prior-repo baseline (expects src/engine/core.py).",
    )
    parser.add_argument(
        "--out",
        default="",
        help="Output JSON report path (default tmp/runs/differential_validation_<utc>.json).",
    )
    parser.add_argument(
        "--fail-on-disagreement",
        action="store_true",
        help="Return non-zero if any case disagrees with reference.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reference_repo = Path(args.reference_repo).resolve()

    try:
        ref_module = _load_reference_core_module(reference_repo)
    except Exception as error:
        print(f"Reference load failed: {error}")
        return 2

    cases = _build_cases()
    case_rows: list[dict[str, Any]] = []
    agreed_total = 0
    for case in cases:
        vendored_steps = _execute_case(
            RuntimeAdapter(engine_cls=PrologEngine, clause_cls=Clause, term_cls=Term),
            case,
        )
        reference_steps = _execute_case(
            RuntimeAdapter(
                engine_cls=ref_module.PrologEngine,
                clause_cls=ref_module.Clause,
                term_cls=ref_module.Term,
            ),
            case,
        )
        agreement = vendored_steps == reference_steps
        if agreement:
            agreed_total += 1
        case_rows.append(
            {
                "name": case.name,
                "category": case.category,
                "agreement": agreement,
                "difference": "" if agreement else _first_difference(vendored_steps, reference_steps),
                "vendored": vendored_steps,
                "reference": reference_steps,
            }
        )

    total = len(case_rows)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "reference_repo": str(reference_repo),
        "reference_engine_path": str((reference_repo / "src" / "engine" / "core.py").resolve()),
        "cases_total": total,
        "agreed_total": agreed_total,
        "agreement_rate": round((agreed_total / total) if total else 0.0, 4),
        "category_rates": _compute_category_rates(case_rows),
        "cases": case_rows,
    }

    if args.out:
        out_path = Path(args.out).resolve()
    else:
        out_path = (ROOT / "tmp" / "runs" / f"differential_validation_{_utc_now_compact()}.json").resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        "Differential validation: "
        f"{agreed_total}/{total} agreed "
        f"({report['agreement_rate']*100:.1f}%) -> {out_path}"
    )
    for category, values in report["category_rates"].items():
        pct = float(values["agreement_rate"]) * 100.0
        print(f"  {category}: {values['agreed_cases']}/{values['total_cases']} ({pct:.1f}%)")

    if args.fail_on_disagreement and agreed_total != total:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
