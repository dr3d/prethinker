"""
Core Prolog Engine Implementation.

Pure Python Prolog interpreter with:
- Unification
- Backward-chaining inference
- Backtracking
- Built-in predicates (is, findall, negation, cut, etc.)
- Depth filtering (prevent infinite loops)
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from copy import deepcopy
from datetime import datetime
import re


@dataclass
class Term:
    """
    Prolog term representation.
    
    Types:
    - Atom: "john", "mary" (lowercase)
    - Number: 42, 3.14
    - Variable: X, Y (uppercase or _)
    - Compound: f(a, b) or parent(john, mary)
    - List: [1, 2, 3] or [H|T]
    """
    name: str
    args: List["Term"] = None
    is_variable: bool = False
    is_number: bool = False
    
    def __init__(self, name: str, args=None, is_variable=False, is_number=False):
        self.name = name
        self.args = args or []
        self.is_variable = is_variable
        self.is_number = is_number
    
    def __repr__(self):
        if self.args:
            args_str = ", ".join(str(arg) for arg in self.args)
            return f"{self.name}({args_str})"
        return self.name
    
    def __eq__(self, other):
        if not isinstance(other, Term):
            return False
        return (self.name == other.name and 
                self.args == other.args and 
                self.is_variable == other.is_variable)
    
    def __hash__(self):
        return hash((self.name, tuple(self.args)))
    
    def copy(self):
        """Deep copy this term."""
        return deepcopy(self)


@dataclass
class Clause:
    """
    Prolog clause: head :- body.
    
    If body is None, it's a fact.
    """
    head: Term
    body: Optional[List[Term]] = None  # Goals in the body
    
    def __repr__(self):
        if self.body:
            body_str = ", ".join(str(t) for t in self.body)
            return f"{self.head} :- {body_str}."
        return f"{self.head}."


class Substitution:
    """Variable substitution/binding."""
    
    def __init__(self, bindings=None):
        self.bindings = bindings or {}
    
    def bind(self, var: str, term: Term) -> "Substitution":
        """Create new substitution with additional binding."""
        new_bindings = self.bindings.copy()
        new_bindings[var] = term
        return Substitution(new_bindings)
    
    def get(self, var: str) -> Optional[Term]:
        """Get binding for variable."""
        return self.bindings.get(var)
    
    def apply(self, term: Term) -> Term:
        """Apply substitution to a term."""
        if term.is_variable:
            binding = self.get(term.name)
            if binding:
                return self.apply(binding)  # Follow chains
            return term
        
        if term.args:
            new_args = [self.apply(arg) for arg in term.args]
            new_term = Term(term.name, new_args)
            return new_term
        
        return term
    
    def compose(self, other: "Substitution") -> "Substitution":
        """Compose two substitutions."""
        # Apply other to all bindings in self
        new_bindings = {}
        for var, term in self.bindings.items():
            new_bindings[var] = other.apply(term)
        
        # Add bindings from other
        for var, term in other.bindings.items():
            if var not in new_bindings:
                new_bindings[var] = term
        
        return Substitution(new_bindings)
    
    def __repr__(self):
        items = [f"{k}: {v}" for k, v in self.bindings.items()]
        return "{" + ", ".join(items) + "}"
    
    def __bool__(self):
        return bool(self.bindings)


class PrologEngine:
    """Pure Python Prolog interpreter."""
    
    def __init__(self, max_depth=500):
        self.clauses: List[Clause] = []
        self.max_depth = max_depth
        self._rename_counter = 0
        self._anonymous_counter = 0
        self.builtins = {
            "is": self._builtin_is,
            ">": self._builtin_gt,
            "<": self._builtin_lt,
            ">=": self._builtin_gte,
            "=<": self._builtin_lte,
            "=:=": self._builtin_arith_eq,
            "=\\=": self._builtin_arith_neq,
            "\\+": self._builtin_not,
            "!": self._builtin_cut,
            "findall": self._builtin_findall,
            "=": self._builtin_unify,
            "\\=": self._builtin_not_unify,
            "value_greater_than": self._builtin_value_greater_than,
            "value_at_most": self._builtin_value_at_most,
            "number_greater_than": self._builtin_number_greater_than,
            "number_at_most": self._builtin_number_at_most,
            "hours_at_least": self._builtin_hours_at_least,
            "support_count_at_least": self._builtin_support_count_at_least,
            "percent_at_least": self._builtin_percent_at_least,
            "percent_below": self._builtin_percent_below,
        }
    
    def add_clause(self, clause: Clause):
        """Add a fact or rule to the KB."""
        self.clauses.append(clause)
    
    def parse_term(self, s: str) -> Term:
        """Parse a string into a Term."""
        s = s.strip()
        if not s:
            raise ValueError("Cannot parse empty term")

        # List syntax: [a, b, c] and [H|T]
        if s.startswith("[") and s.endswith("]"):
            return self._parse_list_term(s)

        # Compound term: f(a, b, g(c))
        open_paren = s.find("(")
        if open_paren > 0 and s.endswith(")") and self._is_outer_wrapped_parens(s, open_paren):
            name = s[:open_paren].strip()
            raw_args = s[open_paren + 1 : -1].strip()
            if not raw_args:
                return Term(name, [])
            args = [self.parse_term(part.strip()) for part in self._split_top_level(raw_args, ",")]
            return Term(name, args)

        if s == "_":
            self._anonymous_counter += 1
            return Term(f"_Anon{self._anonymous_counter}", is_variable=True)

        if s[0].isupper() or s.startswith("_"):
            return Term(s, is_variable=True)

        if re.fullmatch(r"-?\d+(?:\.\d+)?", s):
            if "." in s:
                return Term(s, is_number=True)
            return Term(str(int(s)), is_number=True)

        if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
            return Term(s[1:-1])

        return Term(s)

    def _parse_list_term(self, s: str) -> Term:
        """Parse bracket list syntax into ./2 terms."""
        inner = s[1:-1].strip()
        if not inner:
            return Term("[]")

        list_parts = self._split_top_level(inner, "|")
        if len(list_parts) > 2:
            raise ValueError(f"Invalid list syntax: {s}")

        elements_part = list_parts[0].strip()
        elements: List[Term] = []
        if elements_part:
            elements = [self.parse_term(piece.strip()) for piece in self._split_top_level(elements_part, ",")]

        tail = Term("[]")
        if len(list_parts) == 2:
            tail = self.parse_term(list_parts[1].strip())

        result = tail
        for elem in reversed(elements):
            result = Term(".", [elem, result])
        return result

    def _split_top_level(self, text: str, delimiter: str) -> List[str]:
        """Split by delimiter while respecting nested (), [] structures."""
        parts: List[str] = []
        current: List[str] = []
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
                parts.append("".join(current).strip())
                current = []
                continue

            current.append(ch)

        tail = "".join(current).strip()
        if tail:
            parts.append(tail)
        return parts

    def _is_outer_wrapped_parens(self, text: str, first_open_idx: int) -> bool:
        """True if first '(' is closed by the final ')' in the string."""
        depth = 0
        for idx in range(first_open_idx, len(text)):
            ch = text[idx]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0 and idx != len(text) - 1:
                    return False
        return depth == 0
    
    def unify(self, t1: Term, t2: Term, subst: Substitution = None) -> Optional[Substitution]:
        """Unify two terms, returning substitution if successful."""
        if subst is None:
            subst = Substitution()
        
        t1 = subst.apply(t1)
        t2 = subst.apply(t2)
        
        # Same term
        if t1 == t2:
            return subst
        
        # Variable unification
        if t1.is_variable:
            if self._occurs_check(t1.name, t2):
                return None
            return subst.bind(t1.name, t2)
        
        if t2.is_variable:
            if self._occurs_check(t2.name, t1):
                return None
            return subst.bind(t2.name, t1)
        
        # Compound unification
        if t1.name != t2.name or len(t1.args) != len(t2.args):
            return None
        
        for arg1, arg2 in zip(t1.args, t2.args):
            subst = self.unify(arg1, arg2, subst)
            if subst is None:
                return None
        
        return subst
    
    def _occurs_check(self, var: str, term: Term) -> bool:
        """Check if variable occurs in term (prevent infinite structures)."""
        if term.is_variable:
            return term.name == var
        return any(self._occurs_check(var, arg) for arg in term.args)
    
    def resolve(self, goal: Term, subst: Substitution = None, depth: int = 0) -> List[Substitution]:
        """
        Resolve a goal, returning all solutions.
        
        Uses depth-first search with backtracking.
        """
        if subst is None:
            subst = Substitution()
        
        if depth > self.max_depth:
            return []
        
        goal = subst.apply(goal)
        
        # Check if builtin
        if goal.name in self.builtins:
            return self.builtins[goal.name](goal, subst, depth)
        
        solutions = []
        
        # Try to unify with each clause head
        for clause in self.clauses:
            # Rename variables in clause to avoid conflicts
            renamed_clause = self._rename_clause(clause, depth)
            
            # Try to unify goal with clause head
            new_subst = self.unify(goal, renamed_clause.head, subst)
            if new_subst is None:
                continue
            
            # If clause has no body, we found a solution
            if not renamed_clause.body:
                solutions.append(new_subst)
            else:
                # Resolve body goals
                body_solutions, did_cut = self._resolve_goals(renamed_clause.body, new_subst, depth + 1)
                solutions.extend(body_solutions)
                if did_cut:
                    break
        
        return solutions
    
    def _resolve_goals(self, goals: List[Term], subst: Substitution, depth: int) -> Tuple[List[Substitution], bool]:
        """
        Resolve a list of goals.

        Returns:
        - solutions
        - did_cut: whether a cut occurred in this goal sequence scope
        """
        if depth > self.max_depth:
            return [], False

        if not goals:
            return [subst], False
        
        first_goal = goals[0]
        rest_goals = goals[1:]

        # Handle cut as a structural control operator in the current clause scope.
        if first_goal.name == "!" and not first_goal.args:
            rest_solutions, _ = self._resolve_goals(rest_goals, subst, depth + 1)
            return rest_solutions, True
        
        solutions = []
        
        # Resolve first goal
        first_solutions = self.resolve(first_goal, subst, depth + 1)

        cut_triggered = False
        
        # For each solution to first goal, resolve rest
        for sol in first_solutions:
            rest_solutions, branch_cut = self._resolve_goals(rest_goals, sol, depth + 1)
            solutions.extend(rest_solutions)
            if branch_cut:
                cut_triggered = True
                break
        
        return solutions, cut_triggered
    
    def _rename_clause(self, clause: Clause, depth: int) -> Clause:
        """Rename variables in clause to avoid conflicts.

        Uses a global counter so that every clause instantiation gets a unique
        suffix, preventing variable collisions when the same clause is used
        multiple times at the same depth level.
        """
        self._rename_counter += 1
        suffix = f"_{self._rename_counter}"
        renamed_head = self._rename_term(clause.head, suffix)
        renamed_body = [self._rename_term(t, suffix) for t in clause.body] if clause.body else None
        return Clause(renamed_head, renamed_body)
    
    def _rename_term(self, term: Term, suffix: str) -> Term:
        """Rename all variables in a term."""
        if term.is_variable:
            return Term(term.name + suffix, is_variable=True)
        if term.args:
            new_args = [self._rename_term(arg, suffix) for arg in term.args]
            return Term(term.name, new_args)
        return term
    
    # =============================================================================
    # BUILT-IN PREDICATES
    # =============================================================================
    
    def _builtin_is(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """X is Expr — arithmetic evaluation."""
        if len(goal.args) != 2:
            return []
        
        lhs = subst.apply(goal.args[0])
        rhs = subst.apply(goal.args[1])
        
        try:
            value = self._eval_expr(rhs)
            result_term = Term(str(value), is_number=True)
            new_subst = self.unify(lhs, result_term, subst)
            return [new_subst] if new_subst else []
        except:
            return []
    
    def _eval_expr(self, expr: Term) -> float:
        """Evaluate arithmetic expression."""
        if expr.is_variable:
            raise ValueError("Unbound variable in arithmetic expression")

        if expr.is_number:
            return float(expr.name)
        
        if expr.name == "+":
            return self._eval_expr(expr.args[0]) + self._eval_expr(expr.args[1])
        elif expr.name == "-" and len(expr.args) == 2:
            return self._eval_expr(expr.args[0]) - self._eval_expr(expr.args[1])
        elif expr.name == "-" and len(expr.args) == 1:
            return -self._eval_expr(expr.args[0])
        elif expr.name == "*":
            return self._eval_expr(expr.args[0]) * self._eval_expr(expr.args[1])
        elif expr.name == "/":
            return self._eval_expr(expr.args[0]) / self._eval_expr(expr.args[1])
        elif expr.name == "//":
            return float(int(self._eval_expr(expr.args[0]) // self._eval_expr(expr.args[1])))
        elif expr.name == "mod":
            return float(int(self._eval_expr(expr.args[0])) % int(self._eval_expr(expr.args[1])))
        elif expr.name == "**":
            return self._eval_expr(expr.args[0]) ** self._eval_expr(expr.args[1])
        elif expr.name == "abs" and len(expr.args) == 1:
            return abs(self._eval_expr(expr.args[0]))
        else:
            raise ValueError(f"Unknown operator: {expr.name}")
    
    def _builtin_gt(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """X > Y."""
        if len(goal.args) != 2:
            return []
        try:
            left = self._eval_expr(subst.apply(goal.args[0]))
            right = self._eval_expr(subst.apply(goal.args[1]))
            return [subst] if left > right else []
        except:
            return []
    
    def _builtin_lt(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """X < Y."""
        if len(goal.args) != 2:
            return []
        try:
            left = self._eval_expr(subst.apply(goal.args[0]))
            right = self._eval_expr(subst.apply(goal.args[1]))
            return [subst] if left < right else []
        except:
            return []
    
    def _builtin_gte(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """X >= Y."""
        if len(goal.args) != 2:
            return []
        try:
            left = self._eval_expr(subst.apply(goal.args[0]))
            right = self._eval_expr(subst.apply(goal.args[1]))
            return [subst] if left >= right else []
        except:
            return []
    
    def _builtin_lte(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """X =< Y."""
        if len(goal.args) != 2:
            return []
        try:
            left = self._eval_expr(subst.apply(goal.args[0]))
            right = self._eval_expr(subst.apply(goal.args[1]))
            return [subst] if left <= right else []
        except:
            return []
    
    def _builtin_arith_eq(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """X =:= Y — arithmetic equality."""
        if len(goal.args) != 2:
            return []
        try:
            left = self._eval_expr(subst.apply(goal.args[0]))
            right = self._eval_expr(subst.apply(goal.args[1]))
            return [subst] if left == right else []
        except:
            return []
    
    def _builtin_arith_neq(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """X =\\= Y — arithmetic inequality."""
        if len(goal.args) != 2:
            return []
        try:
            left = self._eval_expr(subst.apply(goal.args[0]))
            right = self._eval_expr(subst.apply(goal.args[1]))
            return [subst] if left != right else []
        except:
            return []
    
    def _builtin_not(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """\\+ Goal — negation as failure."""
        if len(goal.args) != 1:
            return []
        
        inner_goal = goal.args[0]
        solutions = self.resolve(inner_goal, subst, depth + 1)
        
        # Succeeds if inner goal fails
        return [subst] if not solutions else []
    
    def _builtin_cut(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """! cut marker. Clause-level pruning is handled in _resolve_goals."""
        return [subst]
    
    def _builtin_findall(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """findall(Template, Goal, List) — collect all solutions."""
        if len(goal.args) != 3:
            return []

        template = subst.apply(goal.args[0])
        query_goal = subst.apply(goal.args[1])
        result_slot = goal.args[2]

        # Collect all solutions for the goal
        inner_solutions = self.resolve(query_goal, subst, depth + 1)

        # Apply template to each solution to build the collected list
        collected = [sol.apply(template) for sol in inner_solutions]

        prolog_list = self._build_prolog_list(collected)
        new_subst = self.unify(result_slot, prolog_list, subst)
        return [new_subst] if new_subst is not None else []

    def _build_prolog_list(self, terms: List["Term"]) -> "Term":
        """Build a Prolog list term ./2 from a Python list of Terms."""
        result: Term = Term("[]")
        for term in reversed(terms):
            result = Term(".", [term, result])
        return result
    
    def _builtin_unify(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """X = Y — unify."""
        if len(goal.args) != 2:
            return []
        new_subst = self.unify(goal.args[0], goal.args[1], subst)
        return [new_subst] if new_subst else []
    
    def _builtin_not_unify(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """X \\= Y — not unifiable."""
        if len(goal.args) != 2:
            return []
        new_subst = self.unify(goal.args[0], goal.args[1], subst)
        return [subst] if not new_subst else []

    def _builtin_value_greater_than(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """value_greater_than(Entity, Threshold) via entity_property(Entity, value, Value)."""
        return self._builtin_entity_value_threshold(goal, subst, depth, mode="greater_than")

    def _builtin_value_at_most(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """value_at_most(Entity, Threshold) via entity_property(Entity, value, Value)."""
        return self._builtin_entity_value_threshold(goal, subst, depth, mode="at_most")

    def _builtin_number_greater_than(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """number_greater_than(Value, Threshold) for already-bound numeric terms."""
        return self._builtin_number_threshold(goal, subst, mode="greater_than")

    def _builtin_number_at_most(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """number_at_most(Value, Threshold) for already-bound numeric terms."""
        return self._builtin_number_threshold(goal, subst, mode="at_most")

    def _builtin_hours_at_least(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """hours_at_least(Start, End, Threshold) for canonical time atoms."""
        if len(goal.args) != 3:
            return []
        start_time = self._time_term_value(subst.apply(goal.args[0]))
        end_time = self._time_term_value(subst.apply(goal.args[1]))
        threshold = self._numeric_term_value(subst.apply(goal.args[2]))
        if start_time is None or end_time is None or threshold is None:
            return []
        delta_hours = int((end_time - start_time).total_seconds() // 3600)
        return [subst] if delta_hours >= threshold else []

    def _builtin_support_count_at_least(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """support_count_at_least(Proposal, Threshold) via supported(Proposal, Officer)."""
        if len(goal.args) != 2:
            return []
        proposal_arg = subst.apply(goal.args[0])
        threshold = self._numeric_term_value(subst.apply(goal.args[1]))
        if threshold is None:
            return []
        proposals: List[Term] = []
        if proposal_arg.is_variable:
            proposal_var = Term("_SupportCountProposal", is_variable=True)
            officer_var = Term("_SupportCountOfficer", is_variable=True)
            for next_subst in self.resolve(Term("supported", [proposal_var, officer_var]), subst, depth + 1):
                proposal = next_subst.apply(proposal_var)
                if proposal not in proposals:
                    proposals.append(proposal)
        else:
            proposals = [proposal_arg]
        out: List[Substitution] = []
        for proposal in proposals:
            officer_var = Term("_SupportCountOfficer", is_variable=True)
            support_goal = Term("supported", [proposal, officer_var])
            supporters = {
                str(next_subst.apply(officer_var))
                for next_subst in self.resolve(support_goal, subst, depth + 1)
            }
            if len(supporters) < threshold:
                continue
            new_subst = self.unify(goal.args[0], proposal, subst)
            if new_subst is not None:
                out.append(new_subst)
        return out

    def _builtin_percent_at_least(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """percent_at_least(Part, Whole, Percent) for already-bound numeric terms."""
        return self._builtin_percent_threshold(goal, subst, mode="at_least")

    def _builtin_percent_below(self, goal: Term, subst: Substitution, depth: int) -> List[Substitution]:
        """percent_below(Part, Whole, Percent) for already-bound numeric terms."""
        return self._builtin_percent_threshold(goal, subst, mode="below")

    def _builtin_number_threshold(
        self,
        goal: Term,
        subst: Substitution,
        *,
        mode: str,
    ) -> List[Substitution]:
        if len(goal.args) != 2:
            return []
        value = self._numeric_term_value(subst.apply(goal.args[0]))
        threshold = self._numeric_term_value(subst.apply(goal.args[1]))
        if value is None or threshold is None:
            return []
        if mode == "greater_than" and value > threshold:
            return [subst]
        if mode == "at_most" and value <= threshold:
            return [subst]
        return []

    def _builtin_percent_threshold(
        self,
        goal: Term,
        subst: Substitution,
        *,
        mode: str,
    ) -> List[Substitution]:
        if len(goal.args) != 3:
            return []
        part = self._numeric_term_value(subst.apply(goal.args[0]))
        whole = self._numeric_term_value(subst.apply(goal.args[1]))
        percent = self._numeric_term_value(subst.apply(goal.args[2]))
        if part is None or whole is None or percent is None or whole == 0:
            return []
        actual = (part / whole) * 100
        if mode == "at_least" and actual >= percent:
            return [subst]
        if mode == "below" and actual < percent:
            return [subst]
        return []

    def _builtin_entity_value_threshold(
        self,
        goal: Term,
        subst: Substitution,
        depth: int,
        *,
        mode: str,
    ) -> List[Substitution]:
        if len(goal.args) != 2:
            return []
        entity = subst.apply(goal.args[0])
        threshold = self._numeric_term_value(subst.apply(goal.args[1]))
        if threshold is None:
            return []
        value_var = Term("_ValueThreshold", is_variable=True)
        property_goal = Term("entity_property", [entity, Term("value"), value_var])
        out: List[Substitution] = []
        for next_subst in self.resolve(property_goal, subst, depth + 1):
            value = self._numeric_term_value(next_subst.apply(value_var))
            if value is None:
                continue
            if mode == "greater_than" and value > threshold:
                out.append(next_subst)
            elif mode == "at_most" and value <= threshold:
                out.append(next_subst)
        return out

    @staticmethod
    def _numeric_term_value(term: Term) -> Optional[float]:
        if term.is_variable or term.args:
            return None
        if not term.is_number and not re.fullmatch(r"-?\d+(?:\.\d+)?", str(term.name)):
            return None
        try:
            return float(term.name)
        except Exception:
            return None

    @staticmethod
    def _time_term_value(term: Term) -> Optional[datetime]:
        if term.is_variable or term.args:
            return None
        value = str(term.name).strip().lower()
        match = re.fullmatch(r"t?(\d{1,2})[_:]?(\d{2})", value)
        if not match:
            return None
        hour, minute = match.groups()
        if int(hour) > 23 or int(minute) > 59:
            return None
        return datetime(2000, 1, 1, int(hour), int(minute))


if __name__ == "__main__":
    # Test engine
    engine = PrologEngine()
    
    # Add facts
    engine.add_clause(Clause(Term("parent", [Term("john"), Term("alice")])))
    engine.add_clause(Clause(Term("parent", [Term("alice"), Term("bob")])))
    
    # Add rule: ancestor(X, Y) :- parent(X, Y).
    engine.add_clause(
        Clause(
            Term("ancestor", [Term("X", is_variable=True), Term("Y", is_variable=True)]),
            [Term("parent", [Term("X", is_variable=True), Term("Y", is_variable=True)])]
        )
    )
    
    # Query
    query = Term("ancestor", [Term("john", is_variable=False), Term("X", is_variable=True)])
    solutions = engine.resolve(query)
    
    print(f"Query: {query}")
    print(f"Solutions: {solutions}")
