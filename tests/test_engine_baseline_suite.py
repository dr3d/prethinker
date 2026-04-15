"""
Baseline Prolog engine core suite ported from the legacy repository.

Run: pytest tests/test_engine_baseline_suite.py -v
"""

from engine.core import Term, Clause, Substitution, PrologEngine
import pytest


class TestTerm:
    """Test Term representation."""
    
    def test_atom_creation(self):
        t = Term("john")
        assert t.name == "john"
        assert not t.args
        assert not t.is_variable
    
    def test_variable_creation(self):
        t = Term("X", is_variable=True)
        assert t.name == "X"
        assert t.is_variable
    
    def test_compound_term(self):
        args = [Term("john"), Term("alice")]
        t = Term("parent", args)
        assert t.name == "parent"
        assert len(t.args) == 2
        assert str(t) == "parent(john, alice)"
    
    def test_term_equality(self):
        t1 = Term("parent", [Term("john"), Term("alice")])
        t2 = Term("parent", [Term("john"), Term("alice")])
        assert t1 == t2
    
    def test_term_copy(self):
        original = Term("f", [Term("a"), Term("X", is_variable=True)])
        copied = original.copy()
        assert copied == original
        assert copied is not original


class TestSubstitution:
    """Test variable substitution."""
    
    def test_bind(self):
        subst = Substitution()
        subst2 = subst.bind("X", Term("john"))
        assert subst2.get("X").name == "john"
    
    def test_apply_to_variable(self):
        subst = Substitution({"X": Term("john")})
        result = subst.apply(Term("X", is_variable=True))
        assert result.name == "john"
    
    def test_apply_to_compound(self):
        subst = Substitution({"X": Term("john")})
        compound = Term("parent", [Term("X", is_variable=True), Term("alice")])
        result = subst.apply(compound)
        assert result.args[0].name == "john"
        assert result.args[1].name == "alice"
    
    def test_apply_follows_chains(self):
        """X -> Y, Y -> john should give X -> john."""
        subst = Substitution({"X": Term("Y", is_variable=True), "Y": Term("john")})
        result = subst.apply(Term("X", is_variable=True))
        assert result.name == "john"


class TestParser:
    """Test parser behavior for nested args and list syntax."""

    def test_parse_nested_compound(self):
        engine = PrologEngine()
        term = engine.parse_term("f(a, g(b, c))")
        assert term.name == "f"
        assert len(term.args) == 2
        assert term.args[1].name == "g"
        assert [arg.name for arg in term.args[1].args] == ["b", "c"]

    def test_parse_list_with_tail(self):
        engine = PrologEngine()
        term = engine.parse_term("[H|T]")
        assert term.name == "."
        assert term.args[0].is_variable
        assert term.args[0].name == "H"
        assert term.args[1].is_variable
        assert term.args[1].name == "T"


class TestUnification:
    """Test unification algorithm."""
    
    def test_unify_same_atoms(self):
        engine = PrologEngine()
        t1 = Term("john")
        t2 = Term("john")
        result = engine.unify(t1, t2)
        assert result is not None
        assert not result.bindings
    
    def test_unify_different_atoms_fails(self):
        engine = PrologEngine()
        t1 = Term("john")
        t2 = Term("mary")
        result = engine.unify(t1, t2)
        assert result is None
    
    def test_unify_variable_with_atom(self):
        engine = PrologEngine()
        t1 = Term("X", is_variable=True)
        t2 = Term("john")
        result = engine.unify(t1, t2)
        assert result is not None
        assert result.get("X").name == "john"
    
    def test_unify_compounds(self):
        engine = PrologEngine()
        t1 = Term("parent", [Term("X", is_variable=True), Term("alice")])
        t2 = Term("parent", [Term("john"), Term("alice")])
        result = engine.unify(t1, t2)
        assert result is not None
        assert result.get("X").name == "john"
    
    def test_unify_fails_on_arity_mismatch(self):
        engine = PrologEngine()
        t1 = Term("f", [Term("a")])
        t2 = Term("f", [Term("a"), Term("b")])
        result = engine.unify(t1, t2)
        assert result is None
    
    def test_occurs_check(self):
        """X = f(X) should fail (infinite structure)."""
        engine = PrologEngine()
        t1 = Term("X", is_variable=True)
        t2 = Term("f", [Term("X", is_variable=True)])
        result = engine.unify(t1, t2)
        assert result is None


class TestResolution:
    """Test backward-chaining resolution."""
    
    def test_facts_only(self):
        engine = PrologEngine()
        engine.add_clause(Clause(Term("parent", [Term("john"), Term("alice")])))
        engine.add_clause(Clause(Term("parent", [Term("alice"), Term("bob")])))
        
        query = Term("parent", [Term("john"), Term("X", is_variable=True)])
        solutions = engine.resolve(query)
        
        assert len(solutions) == 1
        assert solutions[0].get("X").name == "alice"
    
    def test_backtracking_multiple_solutions(self):
        engine = PrologEngine()
        engine.add_clause(Clause(Term("parent", [Term("john"), Term("alice")])))
        engine.add_clause(Clause(Term("parent", [Term("john"), Term("bob")])))
        
        query = Term("parent", [Term("john"), Term("X", is_variable=True)])
        solutions = engine.resolve(query)
        
        assert len(solutions) == 2
        names = {sol.get("X").name for sol in solutions}
        assert names == {"alice", "bob"}
    
    def test_simple_rule(self):
        """Test: grandfather(X, Z) :- father(X, Y), father(Y, Z)."""
        engine = PrologEngine()
        
        # Add facts
        engine.add_clause(Clause(Term("father", [Term("john"), Term("alice")])))
        engine.add_clause(Clause(Term("father", [Term("alice"), Term("bob")])))
        
        # Add rule
        engine.add_clause(
            Clause(
                Term("grandfather", [Term("X", is_variable=True), Term("Z", is_variable=True)]),
                [
                    Term("father", [Term("X", is_variable=True), Term("Y", is_variable=True)]),
                    Term("father", [Term("Y", is_variable=True), Term("Z", is_variable=True)])
                ]
            )
        )
        
        query = Term("grandfather", [Term("john", is_variable=False), Term("X", is_variable=True)])
        solutions = engine.resolve(query)
        
        assert len(solutions) == 1
        # Check that we got a solution (variable names may be renamed)
        assert solutions[0].bindings
        
        # Add facts
        engine.add_clause(Clause(Term("parent", [Term("john"), Term("alice")])))
        engine.add_clause(Clause(Term("parent", [Term("alice"), Term("bob")])))
        engine.add_clause(Clause(Term("parent", [Term("bob"), Term("charlie")])))
        
        # Direct ancestor
        engine.add_clause(
            Clause(
                Term("ancestor", [Term("X", is_variable=True), Term("Y", is_variable=True)]),
                [Term("parent", [Term("X", is_variable=True), Term("Y", is_variable=True)])]
            )
        )
        
        # Transitive ancestor
        engine.add_clause(
            Clause(
                Term("ancestor", [Term("X", is_variable=True), Term("Y", is_variable=True)]),
                [
                    Term("parent", [Term("X", is_variable=True), Term("Z", is_variable=True)]),
                    Term("ancestor", [Term("Z", is_variable=True), Term("Y", is_variable=True)])
                ]
            )
        )
        
        # Test direct
        query1 = Term("ancestor", [Term("john"), Term("X", is_variable=True)])
        solutions1 = engine.resolve(query1)
        assert len(solutions1) > 0
        
        # Test transitive
        query2 = Term("ancestor", [Term("john"), Term("charlie")])
        solutions2 = engine.resolve(query2)
        assert len(solutions2) > 0


class TestBuiltins:
    """Test built-in predicates."""
    
    def test_is_arithmetic(self):
        engine = PrologEngine()
        
        # X is 2 + 3
        query = Term("is", [Term("X", is_variable=True), Term("+", [Term("2", is_number=True), Term("3", is_number=True)])])
        solutions = engine.resolve(query)
        
        assert len(solutions) == 1
        # Note: simplified - actual result depends on eval_expr
    
    def test_comparison(self):
        engine = PrologEngine()
        
        # 5 > 3
        query = Term(">", [Term("5", is_number=True), Term("3", is_number=True)])
        solutions = engine.resolve(query)
        
        assert len(solutions) == 1
    
    def test_negation_as_failure(self):
        engine = PrologEngine()
        engine.add_clause(Clause(Term("bird", [Term("tweety")])))
        engine.add_clause(Clause(Term("penguin", [Term("polly")])))
        
        # Can fly if bird and not penguin
        engine.add_clause(
            Clause(
                Term("can_fly", [Term("X", is_variable=True)]),
                [
                    Term("bird", [Term("X", is_variable=True)]),
                    Term("\\+", [Term("penguin", [Term("X", is_variable=True)])])
                ]
            )
        )
        
        # Test
        query = Term("can_fly", [Term("tweety")])
        solutions = engine.resolve(query)
        
        assert len(solutions) == 1

    def test_cut_commits_clause(self):
        """Cut should commit to the selected clause and prevent fallthrough."""
        engine = PrologEngine()

        # max(X, Y, X) :- X >= Y, !.
        engine.add_clause(
            Clause(
                Term("max", [Term("X", is_variable=True), Term("Y", is_variable=True), Term("X", is_variable=True)]),
                [
                    Term(">=", [Term("X", is_variable=True), Term("Y", is_variable=True)]),
                    Term("!"),
                ],
            )
        )
        # max(X, Y, Y).
        engine.add_clause(
            Clause(
                Term("max", [Term("X", is_variable=True), Term("Y", is_variable=True), Term("Y", is_variable=True)])
            )
        )

        solutions = engine.resolve(
            Term("max", [Term("5", is_number=True), Term("3", is_number=True), Term("R", is_variable=True)])
        )
        assert len(solutions) == 1
        assert solutions[0].apply(Term("R", is_variable=True)).name == "5"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
