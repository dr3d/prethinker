import unittest

from engine.constraint_propagation import ConstraintPropagator, PropagationProblem
from engine.propagation_runner import execute_propagation
from engine.propagation_schema import (
    ConstraintRuleSpec,
    DomainConstraintSpec,
    StateAtom,
    StateDomainLinkSpec,
)


class ConstraintPropagationTests(unittest.TestCase):
    def test_known_state_rule_derivation(self) -> None:
        problem = PropagationProblem(
            initial_states={
                StateAtom("parent", ("alice", "bob")),
                StateAtom("parent", ("bob", "carol")),
            },
            rules=[
                ConstraintRuleSpec(
                    name="parent_implies_ancestor",
                    antecedents=[StateAtom("parent", ("?X", "?Y"))],
                    consequent=StateAtom("ancestor", ("?X", "?Y")),
                ),
                ConstraintRuleSpec(
                    name="ancestor_chain",
                    antecedents=[
                        StateAtom("parent", ("?X", "?Y")),
                        StateAtom("ancestor", ("?Y", "?Z")),
                    ],
                    consequent=StateAtom("ancestor", ("?X", "?Z")),
                ),
            ],
        )
        result = ConstraintPropagator().propagate(problem)
        self.assertIn(StateAtom("ancestor", ("alice", "bob")), result.known_states)
        self.assertIn(StateAtom("ancestor", ("alice", "carol")), result.known_states)

    def test_domain_constraints_reduce_dof(self) -> None:
        problem = PropagationProblem(
            initial_domains={
                "X": {"alice", "bob", "carol"},
                "Y": {"bob", "carol"},
            },
            domain_constraints=[
                DomainConstraintSpec(kind="allowed_values", left="X", values={"alice", "bob"}),
                DomainConstraintSpec(kind="not_equal", left="X", right="Y"),
            ],
        )
        result = ConstraintPropagator().propagate(problem)
        self.assertEqual(result.domains["X"], {"alice", "bob"})
        self.assertEqual(result.degrees_of_freedom["X"], 2)
        self.assertGreaterEqual(result.total_degrees_of_freedom, 1)

    def test_state_link_narrows_domain(self) -> None:
        problem = PropagationProblem(
            initial_states={StateAtom("machine_ready", ("line_1",))},
            initial_domains={"task": {"inspect", "ship", "repair"}},
            state_domain_links=[
                StateDomainLinkSpec(
                    trigger=StateAtom("machine_ready", ("line_1",)),
                    variable="task",
                    allowed_values={"inspect", "ship"},
                )
            ],
        )
        result = ConstraintPropagator().propagate(problem)
        self.assertEqual(result.domains["task"], {"inspect", "ship"})

    def test_runner_returns_serializable_shape(self) -> None:
        spec = {
            "initial_states": [{"predicate": "ready", "args": ["line_1"]}],
            "rules": [
                {
                    "name": "ready_implies_open",
                    "antecedents": [{"predicate": "ready", "args": ["?L"]}],
                    "consequent": {"predicate": "open", "args": ["?L"]},
                }
            ],
            "initial_domains": {"mode": ["auto", "manual"]},
            "domain_constraints": [
                {"kind": "allowed_values", "left": "mode", "values": ["auto"]}
            ],
        }
        result = execute_propagation(spec)
        self.assertIn("known_states", result)
        self.assertIn("domains", result)
        self.assertEqual(result["domains"]["mode"], ["auto"])


if __name__ == "__main__":
    unittest.main()
