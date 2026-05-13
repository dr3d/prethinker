# Counterfactual Arithmetic Dense Pair

Boundary class: `counterfactual_arithmetic_join`

This probe tests whether the compiler and QA path can keep current totals,
candidate adjustments, dispositions, and hypothetical totals separate when
several adjustment records are present.

The intended geometry is fixture-free:

- a stated current total;
- one or more adjustment records;
- dispositions that mark an adjustment as already included, excluded, withdrawn,
  superseded, or rejected;
- a hypothetical question that requires applying only the relevant excluded
  adjustment to the current total.

This probe should not justify domain-specific predicate names, local ids, or
story vocabulary in harness architecture.

