# QA Instrument

Prethinker QA is not a deterministic-only replay over a compiled KB. It is a
governed semantic pass over frozen artifacts.

That phrase is the important unit. A governed semantic pass has the same shape
whether it happens during compile or QA:

```text
LLM proposal
  inside deterministic constraints
  measured by deterministic artifacts
  sometimes checked by LLM judging
```

The current thirteen facets are measurement surfaces over these passes. Some
facets pressure compile-stage behavior. Query, selector, and answer facets
pressure QA-stage behavior. The number is calibration telemetry for the current
vocabulary, not a permanent architectural fact.

The model may help interpret a natural-language question and may help judge or
classify an answer row. Deterministic code still controls what evidence can be
queried, what query shapes are legal, whether any proposed operation can run,
whether writes are blocked, and how the row is recorded.

Current language boundary: messy human query language should enter the
deterministic QA layer through Semantic IR / structured `query_intents[]` or
structured query templates. Python query support may consume typed atoms,
registered predicates, source coordinates, and explicit structural fields. It
must not parse source-record prose, display strings, model-authored prose
fields, or raw user questions to recover meaning.

## The Shape

```text
compiled KB artifact
+ natural-language question
  -> LLM proposes structured query-plan / evidence-plan candidates
  -> deterministic mapper validates predicates, arity, variables, and policy
  -> deterministic Prolog/runtime executes admitted queries
  -> deterministic ledgers, selectors, and guards shape candidate support
  -> LLM may judge reference-answer match, compose notes, or classify failure
  -> deterministic summary records exact/partial/miss and cleanliness pressure
```

The authority boundary is different from compile. During QA, the model is not
allowed to create durable source truth. It can propose query operations, answer
comparisons, evidence bundles, and failure labels. The compiled KB, deterministic
ledgers, runtime query engine, and harness policy decide what is executable and
what gets counted.

The discipline is not "the LLM did well." The discipline is that the audit
summary can say what path was used and whether the run stayed clean.

## Response Envelope

The QA row can also carry a product-facing `qa_response_envelope_v1`.

This envelope is deliberately downstream of scoring. It does not change
exact/partial/miss counts, compatibility accounting, failure-surface labels, or
compile gates. It renders the current row as a support reading:

```text
reference answer supplied by the evaluation set
  + admitted query evidence
  + reference judge verdict
  + clarification and missing-slot signals
  + failure-surface label when present
  -> established / partially_established / not_established
     / clarification_required / coverage_gap / ambiguous
```

The key boundary is that this is `reference_answer_support`, not an autonomous
final-answer renderer. It can say that the admitted evidence establishes the
supplied reference answer, or that the row needs clarification or has a coverage
gap. It should not be described as "Prethinker answered the user's question" in
a product demo unless a separate final-answer renderer has actually composed
that answer from the envelope.

The separate `qa_rendered_response_v1` layer consumes the envelope and produces
user-facing text for demos or workstation surfaces. That renderer is not part of
QA scoring. It does not query, judge, mutate, or repair the KB; it only presents
the current support reading.

## What Is LLM-Mediated

The QA stage can involve model calls for:

- interpreting the natural-language question into structured query candidates;
- emitting structured `query_intents[]` for answer shape and target terms;
- proposing compact evidence-bundle plans over the compiled artifact;
- comparing returned support with reference answers;
- classifying a non-exact row as compile-surface, query-surface, hybrid-join,
  answer-surface, or uncertain;
- composing diagnostic notes used by researchers.

Those model outputs are proposal and measurement material. They do not become
durable KB facts.

## What Is Deterministic

The harness controls:

- loading admitted facts and rules from the frozen compile artifact;
- exposing the compiled predicate inventory and query templates;
- validating query predicates, arity, variable use, and adapter policy;
- executing Prolog/runtime queries;
- preserving source coordinates through deterministic ledgers;
- blocking QA-time writes and counting write proposals if they appear;
- disabling retired compatibility adapters unless explicitly requested;
- counting compatibility rows, runtime load errors, exact/partial/miss rows,
  and failure-surface labels.

This is why `0 compatibility rows`, `0 runtime load errors`, and `0 write
proposal rows` matter. They show the QA run stayed inside the intended
governed path even though LLM calls participated in planning and judging.

`compatibility rows = 0` is specifically a cleanliness signal: no answer row had
to be rescued by a retired or non-clean compatibility path. That does not mean
the LLM was absent. It means the deterministic summary found no compatibility
rescue pressure.

## Reference Judge Null Controls

Any LLM-judged QA exact-rate metric must pass adversarial null controls before
it can become claim-bearing:

```text
empty_evidence:
  true reference answer, no query evidence
wrong_reference:
  redacted typed evidence, different same-fixture reference answer
```

The wrong-reference control must also neutralize the original question text.
Otherwise the judge can follow the original question, bless the original answer
path, and ignore that the reference answer was swapped. The 2026-06-04 FDA v2
diagnostic exposed exactly that failure: sample3 produced one exact null verdict
before the control question was neutralized, and zero exact null verdicts after
the harness fix.

Older internal JSON keys may still contain the word `helper` for backward
compatibility with archived comparison artifacts. New reports and product prose
should prefer `support surface`, `query-only support`, or `compatibility row`
depending on the actual path. A support surface is allowed to be current and
clean; a compatibility row is the cleanliness pressure being counted.

## The Audit Grammar

The deterministic summary is the audit grammar for a QA run. It records:

- exact / partial / miss counts;
- compatibility rows;
- runtime load errors;
- QA-time write proposals;
- failure-surface labels;
- cache/provider/run metadata where available.

Comparison reports also carry `qa_regression_guard_v1`. The guard fails when a
row that was previously exact becomes non-exact in the candidate run. That
turns row churn into a promotion blocker instead of leaving it as a narrative
note after the fact.

This is what makes a run comparable and replayable. LLM proposals, evidence
bundles, answer comparisons, and failure classifications are governed by this
accounting, but they do not replace it.

That distinction matters when a gate change passes more rows. The release
question is not "did the threshold get looser?" It is whether the newly passing
rows are admitted by principled criteria and the deterministic summary still
shows clean evidence paths, zero compatibility rescue, zero runtime load
errors, and zero QA writes.

## The Three QA Facets

The query, selector, and answer facets are measurement surfaces over this
pipeline. They are not three pure-deterministic subsystems.

| Facet | Question It Asks | Typical Failure |
| --- | --- | --- |
| Query surface | Did the question planner ask for the right admitted predicates with the right joins and variables? | The KB contains the fact, but the query asks the wrong predicate or binds the wrong slot. |
| Selector surface | Did the harness choose the right evidence surface for this row? | A broader support bundle beats a narrower direct surface even though it answers the wrong question. |
| Answer surface | Did the final answer shape match the admitted epistemic state? | The evidence supports a qualified answer, but the row is answered too crisply, too vaguely, or with the wrong uncertainty. |

These facets explain where a row failed. They do not imply that QA itself is
model-free.

## Failure Surface Labels

The usual non-exact labels mean:

- `compile_surface_gap`: the compiled artifact did not preserve the needed
  answer-bearing surface.
- `query_surface_gap`: the artifact had enough information, but query planning
  or query execution did not reach it.
- `hybrid_join_gap`: pieces existed, but the necessary join across surfaces was
  missing or mis-bound.
- `answer_surface_gap`: support was close enough, but the answer/verdict shape
  did not match the expected epistemic answer.
- `judge_uncertain`: the scorer could not cleanly assign the failure.

These labels are diagnostics. A clean repair should improve the underlying
surface and then transfer to unlike documents.

## Why This Matters

In legal, clinical, compliance, safety, and enterprise-record settings, a
plausible answer is not enough. The system has to show what evidence path it
used, whether that path was admitted by policy, and whether any hidden rescue
mechanism was needed to make the answer work.

That is why cleanliness metrics are product metrics, not just lab counters.
`0 compatibility rows` means the row did not depend on a retired or non-clean
adapter rescue. `0 runtime load errors` means the admitted state could actually
load and execute. `0 write proposal rows` means QA did not try to mutate truth
while answering. Together, those numbers distinguish governed QA from an
answer-shaped model response.

## Practical Rule

When describing QA, avoid saying "deterministic QA" unless the claim is scoped
to a specific substep such as Prolog query execution or ledger extraction.

The safer phrases are:

```text
governed QA over admitted state
governed semantic pass
multi-lens semantic compile + governed QA
```

Those phrases preserve the core truth: QA uses LLM-mediated planning and
judging, but deterministic code constrains what evidence is available, what may
execute, and what counts as an answer.
