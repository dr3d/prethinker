# Counterfactual Arithmetic Pair

Pressure:

The source gives a current accepted total and a proposed or excluded increment.
Questions ask for the hypothetical total if the increment were adopted, while
also asking for the current total and the excluded increment separately.

Expected boundary class:

`counterfactual_arithmetic_join`

Repair rule:

Do not add fixture names, local identifiers, question ids, answer strings, or
domain-specific vocabulary to the harness. A repair is valid only if it can be
phrased as a reusable join over admitted current-total and excluded/proposed
increment surfaces.
