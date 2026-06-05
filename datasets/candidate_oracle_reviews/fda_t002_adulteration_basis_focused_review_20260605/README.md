# FDA T002 Adulteration-Basis Focused Review

Source-only focused review returned on 2026-06-05 from the cleaned work-order
packet. The reviewer did not receive model outputs, prior oracle files, or
judged-QA manifests.

Decision: `forbidden_addition`.

Candidate:

```prolog
fda_adulteration_basis(fda_warning_letter_320_25_68, adulteration_insanitary_conditions, fdca_501_a_2_a, drug_products, direct).
```

Source-only rationale: the Rechon warning letter states adulteration under
FDCA section `501(a)(2)(B)` for CGMP, and does not state a section
`501(a)(2)(A)` insanitary-conditions adulteration basis. Import refusal under
section `801(a)(3)` is not an adulteration-basis row.

Oracle action:

```prolog
fda_adulteration_basis(_, adulteration_insanitary_conditions, fdca_501_a_2_a, _, _).
```
