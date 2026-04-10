"""Constraint propagation utilities.

Provides two capabilities:
1. Known-state propagation via deterministic implication rules.
2. Degree-of-freedom (DoF) propagation via domain constraints.
"""

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

            if not domains[left]:
                contradictions.append(f"Domain contradiction: {left} has no feasible values")
            if right and right in domains and not domains[right]:
                contradictions.append(f"Domain contradiction: {right} has no feasible values")

        return changed
