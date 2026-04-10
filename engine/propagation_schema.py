"""Schema objects for known-state and domain propagation."""

from dataclasses import dataclass
from typing import Any, Optional, Set, Tuple


@dataclass(frozen=True)
class StateAtom:
    """Canonical state atom used by the propagator."""

    predicate: str
    args: Tuple[Any, ...] = ()


@dataclass
class ConstraintRuleSpec:
    """Deterministic implication rule for known-state propagation."""

    name: str
    antecedents: list[StateAtom]
    consequent: StateAtom


@dataclass
class DomainConstraintSpec:
    """Constraint over variable domains for DoF propagation."""

    kind: str
    left: str
    right: Optional[str] = None
    values: Optional[Set[Any]] = None
    when_value: Optional[Any] = None


@dataclass
class StateDomainLinkSpec:
    """Domain restriction activated by a known state."""

    trigger: StateAtom
    variable: str
    allowed_values: Set[Any]
