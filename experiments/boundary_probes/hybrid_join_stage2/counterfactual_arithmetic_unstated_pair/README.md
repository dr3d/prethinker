# Counterfactual Arithmetic Unstated Pair

Boundary class: `counterfactual_arithmetic_join`

This probe removes the explicitly stated hypothetical outcome. The source gives
the current total, candidate adjustment amount, and disposition, then states
the arithmetic instruction without naming the final computed value.

The fixture-free geometry is:

- current total is stated;
- candidate adjustment amount is stated;
- candidate is excluded from the current total;
- question asks for the hypothetical total if that candidate were included;
- the final value must be assembled from the pieces rather than copied from an
  emitted outcome row.

No repair should name this fixture, its identifiers, or its domains.

