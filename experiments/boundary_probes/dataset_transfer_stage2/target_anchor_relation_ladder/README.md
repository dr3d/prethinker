# Target Anchor Relation Ladder

Purpose: isolate compile-surface misses where a clause contains both a target
relation and a temporal or causal anchor, and the compile preserves the anchor
as if it were the target.

Forbidden fix: do not add selectors, helpers, predicates, or prompts for this
packet's names, teams, objects, or answer strings. A useful repair must be a
generic source-fidelity principle:

- target relation and anchor relation are separate coordinates;
- after/before/following/during clauses attach temporal context;
- the object of joined/assigned/appointed/attached/enrolled remains the target;
- the anchor event remains a qualifier, not a replacement target.
