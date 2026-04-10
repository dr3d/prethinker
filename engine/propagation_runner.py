"""Helpers and CLI for state/domain propagation experiments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from .constraint_propagation import ConstraintPropagator, PropagationProblem
from .propagation_schema import (
    ConstraintRuleSpec,
    DomainConstraintSpec,
    StateAtom,
    StateDomainLinkSpec,
)


def _parse_state_atom(raw: Any) -> StateAtom:
    """Parse a state atom from dict or list form."""
    if isinstance(raw, dict):
        predicate = raw.get("predicate")
        args = tuple(raw.get("args", []))
        return StateAtom(predicate=predicate, args=args)

    if isinstance(raw, list) and raw:
        predicate = raw[0]
        args = tuple(raw[1:])
        return StateAtom(predicate=predicate, args=args)

    raise ValueError(f"Invalid state atom format: {raw}")


def _parse_rule(raw: Dict[str, Any]) -> ConstraintRuleSpec:
    """Parse deterministic rule spec from JSON dict."""
    return ConstraintRuleSpec(
        name=raw.get("name", "rule"),
        antecedents=[_parse_state_atom(a) for a in raw.get("antecedents", [])],
        consequent=_parse_state_atom(raw["consequent"]),
    )


def _parse_domain_constraint(raw: Dict[str, Any]) -> DomainConstraintSpec:
    """Parse domain constraint spec from JSON dict."""
    values = raw.get("values")
    return DomainConstraintSpec(
        kind=raw["kind"],
        left=raw["left"],
        right=raw.get("right"),
        values=set(values) if values is not None else None,
        when_value=raw.get("when_value"),
    )


def _parse_state_domain_link(raw: Dict[str, Any]) -> StateDomainLinkSpec:
    """Parse state-triggered domain narrowing link from JSON dict."""
    return StateDomainLinkSpec(
        trigger=_parse_state_atom(raw["trigger"]),
        variable=raw["variable"],
        allowed_values=set(raw.get("allowed_values", [])),
    )


def build_propagation_problem(spec: Dict[str, Any]) -> PropagationProblem:
    """Build PropagationProblem from a JSON-compatible dict."""
    return PropagationProblem(
        initial_states={_parse_state_atom(s) for s in spec.get("initial_states", [])},
        rules=[_parse_rule(r) for r in spec.get("rules", [])],
        initial_domains={
            var: set(values) for var, values in spec.get("initial_domains", {}).items()
        },
        domain_constraints=[
            _parse_domain_constraint(c) for c in spec.get("domain_constraints", [])
        ],
        state_domain_links=[
            _parse_state_domain_link(link)
            for link in spec.get("state_domain_links", [])
        ],
    )


def execute_propagation(spec: Dict[str, Any], max_iterations: int = 100) -> Dict[str, Any]:
    """Execute propagation from a dict spec and return JSON-serializable result."""
    problem = build_propagation_problem(spec)
    result = ConstraintPropagator(max_iterations=max_iterations).propagate(problem)

    known_states = [
        {"predicate": atom.predicate, "args": list(atom.args)}
        for atom in sorted(result.known_states, key=lambda a: (a.predicate, a.args))
    ]
    domains = {
        var: sorted(list(values)) for var, values in sorted(result.domains.items())
    }

    return {
        "known_states": known_states,
        "domains": domains,
        "degrees_of_freedom": result.degrees_of_freedom,
        "total_degrees_of_freedom": result.total_degrees_of_freedom,
        "contradictions": result.contradictions,
        "iterations": result.iterations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run known-state and domain propagation from a JSON spec."
    )
    parser.add_argument(
        "--problem-json",
        required=True,
        help="Path to propagation problem JSON file",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=100,
        help="Max propagation iterations (default: 100)",
    )
    args = parser.parse_args()

    problem_path = Path(args.problem_json)
    if not problem_path.exists():
        raise FileNotFoundError(f"Propagation problem not found: {args.problem_json}")

    with open(problem_path, "r", encoding="utf-8") as handle:
        spec = json.load(handle)

    result = execute_propagation(spec, max_iterations=args.max_iterations)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
