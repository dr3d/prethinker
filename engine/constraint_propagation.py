"""Constraint propagation utilities.

Provides two capabilities:
1. Known-state propagation via deterministic implication rules.
2. Degree-of-freedom (DoF) propagation via domain constraints.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from .propagation_schema import (
    ConstraintRuleSpec,
    DomainConstraintSpec,
    StateAtom,
    StateDomainLinkSpec,
)


def _is_var(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("?")


def _merge_bindings(base: Dict[str, Any], key: str, value: Any) -> Optional[Dict[str, Any]]:
    existing = base.get(key)
    if existing is not None and existing != value:
        return None
    merged = dict(base)
    merged[key] = value
    return merged


def _match_pattern(pattern: StateAtom, fact: StateAtom, bindings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if pattern.predicate != fact.predicate or len(pattern.args) != len(fact.args):
        return None

    current = dict(bindings)
    for p_arg, f_arg in zip(pattern.args, fact.args):
        if _is_var(p_arg):
            maybe = _merge_bindings(current, p_arg, f_arg)
            if maybe is None:
                return None
            current = maybe
        elif p_arg != f_arg:
            return None
    return current


def _apply_bindings(atom: StateAtom, bindings: Dict[str, Any]) -> StateAtom:
    applied = []
    for arg in atom.args:
        if _is_var(arg):
            applied.append(bindings.get(arg, arg))
        else:
            applied.append(arg)
    return StateAtom(atom.predicate, tuple(applied))


def _ordered_key(value: Any) -> tuple[str, tuple[int, ...] | float] | None:
    """Return a comparable key for numbers and date/time atoms.

    Date atoms use the same conservative shape as the rest of the harness:
    ``2026_04_28``, ``2026_04_28_08_00``, ISO-ish dashes, optional ``v`` prefix,
    and optional UTC/Z suffixes. The propagator does not interpret prose dates.
    """

    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return ("number", float(value))
    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None
    try:
        return ("number", float(text))
    except ValueError:
        pass

    normalized = text
    if normalized.startswith("v_"):
        normalized = normalized[2:]
    elif normalized.startswith("v") and re.match(r"^v\d{4}[_-]\d{2}[_-]\d{2}", normalized):
        normalized = normalized[1:]
    normalized = re.sub(r"(?:_utc|z)$", "", normalized, flags=re.IGNORECASE)
    normalized = normalized.replace("T", "_").replace("t", "_")
    match = re.fullmatch(
        r"(?P<year>\d{4})[_-](?P<month>\d{2})[_-](?P<day>\d{2})"
        r"(?:[_-](?P<hour>\d{2})(?:[_:](?P<minute>\d{2})(?:[_:](?P<second>\d{2}))?)?)?",
        normalized,
    )
    if not match:
        return None
    parts = [
        int(match.group("year")),
        int(match.group("month")),
        int(match.group("day")),
        int(match.group("hour") or 0),
        int(match.group("minute") or 0),
        int(match.group("second") or 0),
    ]
    return ("temporal", tuple(parts))


def _ordered_relation_holds(left: Any, right: Any, kind: str) -> bool | None:
    left_key = _ordered_key(left)
    right_key = _ordered_key(right)
    if left_key is None or right_key is None or left_key[0] != right_key[0]:
        return None

    left_value = left_key[1]
    right_value = right_key[1]
    if kind in {"less_than", "before"}:
        return left_value < right_value
    if kind in {"less_equal", "before_or_equal", "at_or_before"}:
        return left_value <= right_value
    if kind in {"greater_than", "after"}:
        return left_value > right_value
    if kind in {"greater_equal", "after_or_equal", "at_or_after"}:
        return left_value >= right_value
    return None


def _filter_ordered_domain(
    values: Set[Any],
    other_values: Set[Any],
    *,
    kind: str,
    is_left: bool,
) -> Set[Any]:
    kept: Set[Any] = set()
    for value in values:
        for other_value in other_values:
            left = value if is_left else other_value
            right = other_value if is_left else value
            holds = _ordered_relation_holds(left, right, kind)
            if holds is True:
                kept.add(value)
                break
            if holds is None:
                # Incomparable values are kept; this propagator narrows only
                # domains whose values have deterministic numeric/date order.
                kept.add(value)
                break
    return kept


@dataclass
class PropagationProblem:
    initial_states: Set[StateAtom] = field(default_factory=set)
    rules: List[ConstraintRuleSpec] = field(default_factory=list)
    initial_domains: Dict[str, Set[Any]] = field(default_factory=dict)
    domain_constraints: List[DomainConstraintSpec] = field(default_factory=list)
    state_domain_links: List[StateDomainLinkSpec] = field(default_factory=list)


@dataclass
class PropagationResult:
    known_states: Set[StateAtom]
    domains: Dict[str, Set[Any]]
    degrees_of_freedom: Dict[str, int]
    total_degrees_of_freedom: int
    contradictions: List[str]
    iterations: int


class ConstraintPropagator:
    """Run fixed-point propagation over states and variable domains."""

    def __init__(self, max_iterations: int = 100):
        self.max_iterations = max_iterations

    def propagate(self, problem: PropagationProblem) -> PropagationResult:
        known_states = set(problem.initial_states)
        domains = {var: set(values) for var, values in problem.initial_domains.items()}
        contradictions: List[str] = []

        iteration = 0
        changed = True
        while changed and iteration < self.max_iterations:
            iteration += 1
            changed = False

            new_states = self._derive_states(known_states, problem.rules)
            if not new_states.issubset(known_states):
                known_states.update(new_states)
                changed = True

            domains_changed = self._apply_state_links(
                known_states, domains, problem.state_domain_links, contradictions
            )
            if domains_changed:
                changed = True

            domain_changed = self._propagate_domains(
                domains, problem.domain_constraints, contradictions
            )
            if domain_changed:
                changed = True

        if iteration == self.max_iterations and changed:
            contradictions.append(
                f"Propagation hit max_iterations={self.max_iterations} before convergence"
            )

        dof = {var: len(values) for var, values in domains.items()}
        total_dof = sum(max(0, size - 1) for size in dof.values())

        return PropagationResult(
            known_states=known_states,
            domains=domains,
            degrees_of_freedom=dof,
            total_degrees_of_freedom=total_dof,
            contradictions=contradictions,
            iterations=iteration,
        )

    def _derive_states(
        self,
        known_states: Set[StateAtom],
        rules: List[ConstraintRuleSpec],
    ) -> Set[StateAtom]:
        derived: Set[StateAtom] = set()

        for rule in rules:
            bindings_list = [dict()]
            for antecedent in rule.antecedents:
                next_bindings: List[Dict[str, Any]] = []
                for binding in bindings_list:
                    for fact in known_states:
                        merged = _match_pattern(antecedent, fact, binding)
                        if merged is not None:
                            next_bindings.append(merged)
                bindings_list = next_bindings
                if not bindings_list:
                    break

            for binding in bindings_list:
                derived.add(_apply_bindings(rule.consequent, binding))

        return derived

    def _apply_state_links(
        self,
        known_states: Set[StateAtom],
        domains: Dict[str, Set[Any]],
        links: List[StateDomainLinkSpec],
        contradictions: List[str],
    ) -> bool:
        changed = False
        for link in links:
            if link.trigger not in known_states:
                continue

            if link.variable not in domains:
                domains[link.variable] = set(link.allowed_values)
                changed = True
                continue

            before = set(domains[link.variable])
            domains[link.variable].intersection_update(link.allowed_values)
            if domains[link.variable] != before:
                changed = True

            if not domains[link.variable]:
                contradictions.append(
                    f"Domain wiped by state link: {link.variable} after trigger {link.trigger}"
                )

        return changed

    def _propagate_domains(
        self,
        domains: Dict[str, Set[Any]],
        constraints: List[DomainConstraintSpec],
        contradictions: List[str],
    ) -> bool:
        changed = False

        for constraint in constraints:
            kind = constraint.kind
            left = constraint.left
            right = constraint.right
            values = constraint.values or set()

            if left not in domains:
                continue

            if kind == "allowed_values":
                before = set(domains[left])
                domains[left].intersection_update(values)
                changed |= domains[left] != before

            elif kind == "forbidden_values":
                before = set(domains[left])
                domains[left].difference_update(values)
                changed |= domains[left] != before

            elif kind == "equal" and right and right in domains:
                intersection = domains[left].intersection(domains[right])
                if domains[left] != intersection:
                    domains[left] = set(intersection)
                    changed = True
                if domains[right] != intersection:
                    domains[right] = set(intersection)
                    changed = True

            elif kind == "not_equal" and right and right in domains:
                if len(domains[left]) == 1:
                    value = next(iter(domains[left]))
                    if value in domains[right]:
                        domains[right].remove(value)
                        changed = True
                if len(domains[right]) == 1:
                    value = next(iter(domains[right]))
                    if value in domains[left]:
                        domains[left].remove(value)
                        changed = True

            elif kind == "implication" and right and right in domains:
                if len(domains[left]) == 1 and constraint.when_value in domains[left]:
                    before = set(domains[right])
                    domains[right].intersection_update(values)
                    changed |= domains[right] != before

            elif kind in {
                "less_than",
                "less_equal",
                "greater_than",
                "greater_equal",
                "before",
                "before_or_equal",
                "after",
                "after_or_equal",
                "at_or_before",
                "at_or_after",
            }:
                if right and right in domains:
                    left_before = set(domains[left])
                    right_before = set(domains[right])
                    domains[left] = _filter_ordered_domain(
                        domains[left],
                        domains[right],
                        kind=kind,
                        is_left=True,
                    )
                    domains[right] = _filter_ordered_domain(
                        domains[right],
                        domains[left],
                        kind=kind,
                        is_left=False,
                    )
                    changed |= domains[left] != left_before or domains[right] != right_before
                elif values:
                    before = set(domains[left])
                    domains[left] = _filter_ordered_domain(
                        domains[left],
                        values,
                        kind=kind,
                        is_left=True,
                    )
                    changed |= domains[left] != before

            if not domains[left]:
                contradictions.append(f"Domain contradiction: {left} has no feasible values")
            if right and right in domains and not domains[right]:
                contradictions.append(f"Domain contradiction: {right} has no feasible values")

        return changed
