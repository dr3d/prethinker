# Multilingual Semantic IR Probe

Last updated: 2026-04-28

## Why This Probe Exists

This probe tests a central claim in the new architecture:

```text
If the LLM owns language handling, non-English input should not require Python phrase patches.
```

The goal is not to become a translation product. The goal is to see whether the
router/compiler design can preserve the same epistemic boundaries across
languages:

- medical fact versus medical advice;
- legal claim versus finding;
- contract obligation versus completed fact;
- story source fidelity;
- probate witness/rule validity;
- mixed-domain legal/medical source conflicts.

## Headline

Current result:

```text
router_ok=10/10
compiler_parsed_ok=10/10
```

This is the cleanest empirical support so far for moving language handling out
of Python. The LLM router succeeds on raw multilingual turns without a Python
translation or keyword-routing layer.

## Harness

Runner:

```powershell
python scripts\run_multilingual_semantic_ir_probe.py
```

The harness sends raw multilingual utterances to:

```text
semantic_router_v1
  -> router-selected profile/context
  -> semantic_ir_v1 compiler
  -> deterministic mapper/admission
```

No Python selector participates in this path. Python validates JSON, loads the
router-selected context package, and enforces mapper admission.

## Battery

The first battery contains 10 turns across Spanish, French, German, Portuguese,
Italian, Japanese, and code-switched English/Spanish.

It covers:

- `medical@v0`
- `legal_courtlistener@v0`
- `sec_contracts@v0`
- `story_world@v0`
- `probate@v0`

Representative cases:

```text
Priya toma warfarina desde marzo; no es una recomendacion, solo un registro.

Dans Doe c. Acme, la plainte alleguait qu'Acme avait viole le bail,
mais le tribunal a seulement constate que la plainte etait deposee a temps.

Jeder Premiumkunde muss vorrangigen Support erhalten, ausser wenn eine
unbezahlte Rechnung aelter als zehn Tage ist.

Tres lontras moravam numa casa pequena perto do rio...

契約では、借り手が期限までに支払わない場合、貸し手は返済を加速できる。
```

## First Result

Router-only:

```text
router_ok=10/10
router_score_avg=1.000
```

Full router -> compiler:

```text
router_ok=10/10
router_score_avg=1.000
compiler_parsed_ok=10/10
```

This is exactly the shape we wanted to see. The model-router chose the correct
epistemic lane across languages without Python reading the utterance for
meaning.

## What Improved After Generic Tightening

The first pass exposed downstream profile/palette issues rather than router
failure. We made generic changes, not language-specific Python patches:

- `claim_made/4` now treats `speaker_or_document` as a mixed role, so a witness
  speaker is not rejected as "not a document."
- `sec_contracts@v0` now includes `depends_on/2` and `blocked_by/2` for meeting,
  project, approval, and launch dependencies.
- `story_world@v0` now includes `lives_in/2` and `near/2`, avoiding vague
  `at/2` use for residence/proximity.
- `medical@v0` now contains declarative multilingual normalization guidance for
  obvious medication variants such as `warfarina/warfarine -> warfarin`.

The follow-up multilingual run still scored:

```text
router_ok=10/10
compiler_parsed_ok=10/10
```

and showed better concrete outputs:

```prolog
taking(priya, warfarin).
lives_in(tres_lontras, casa_pequena).
near(casa_pequena, rio).
claim_made(complaint, acme, violated_the_lease, complaint).
subject_to(acceleration_clause, non_payment_condition).
```

## What This Proves

It does not prove full multilingual robustness.

It does show that the router/SIR design can move language understanding out of
Python:

```text
LLM router: 10/10
```

The failures moved to the right place: predicate contracts, profile palette
coverage, negation policy, and query semantics. Those are architecture issues,
not "write another Spanish regex" issues.

## Remaining Edges

- Negative claim forms still collide with the lack of general negative-fact
  semantics.
- Some query operations can be syntactically admitted even when the model uses a
  vague atom such as `unknown`; this needs clearer query argument policy.
- Contract rules in non-English input are recognized, but durable rule
  admission remains intentionally conservative.
- Foreign-language legal/medical terms benefit from advisory profiles, but the
  primary lane must still own admission.
- Variance under repeated model calls may still change individual workspace
  choices even when routing stays correct.

## Architectural Takeaway

This is a strong point for the epistemic architecture:

```text
The model can understand language across languages.
The mapper can remain language-agnostic.
Profiles can provide declarative domain pressure.
Python does not need to become a multilingual NLP patch layer.
```

The next useful multilingual work is not broad translation. It is harder
cross-lingual epistemic pressure:

- non-English correction and retraction;
- non-English query plus fact in the same turn;
- non-English legal/medical mixed provenance;
- non-English contract exceptions;
- deliberately noisy spelling and grammar.
