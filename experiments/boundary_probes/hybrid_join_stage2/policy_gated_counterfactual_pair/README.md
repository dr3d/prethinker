# Policy-Gated Counterfactual Pair

Boundary class: `policy_gated_counterfactual_total`

This probe tests whether the QA layer can answer a hypothetical total when a
source gives a current/base total plus a gated addition that is explicitly not
part of the current total.

Prediction:

- The compiler should preserve the current total and the gated numeric delta as
  grounded components.
- QA may derive the hypothetical total only for counterfactual questions.
- Withdrawn or rejected historical estimates must not be treated as deltas.
