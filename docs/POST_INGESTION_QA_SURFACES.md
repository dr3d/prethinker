# Post-Ingestion QA Surfaces

Prethinker has three distinct post-ingestion surfaces:

```text
compile surface -> query surface -> answer surface
```

This matters because a good KB does not automatically produce a good answer.

## Compile Surface

The compile surface is what the source-ingestion pipeline admitted into the KB.

It answers:

- What facts, rules, claims, events, priorities, tradeoffs, and source records survived mapper admission?
- Did the compiler preserve the right row classes?
- Did deterministic admission block unsafe or unsupported writes?

Failures here are `compile_surface_gap` failures. A smarter query planner cannot recover a row the KB never admitted.

## Query Surface

The query surface is how a question is translated into Prolog queries over the admitted KB.

It answers:

- Did the QA planner ask the right predicate family?
- Did it use variables instead of over-bound constants?
- Did it gather the whole support bundle instead of one nearby row?
- Did it include temporal helpers, source-status rows, rationale rows, or companion table predicates when needed?

Failures here are `query_surface_gap` failures. The KB may already contain the support, but the planner does not retrieve it.

## Answer Surface

The answer surface is how query rows are compared or synthesized into the expected explanation.

It answers:

- Did the evidence bundle support the reference answer?
- Did the final answer preserve uncertainty, source attribution, and claim/fact boundaries?
- Did it combine rows correctly without inventing missing support?

Failures here are `answer_surface_gap` or `hybrid_join_gap` failures. `answer_surface_gap` means the rows are essentially there but the answer/judge did not recognize the support. `hybrid_join_gap` means the rows exist but need a join, count, temporal comparison, set difference, or arithmetic helper that the current query surface did not assemble.

## Evidence-Bundle Planning

`scripts/run_domain_bootstrap_qa.py` has optional `--evidence-bundle-plan`, `--execute-evidence-bundle-plan`, and `--evidence-bundle-context-filter` modes.

That mode adds an LLM-owned control-plane pass:

```text
question + compiled KB inventory + admitted clauses
  -> evidence_bundle_plan_v1
  -> Semantic IR query compiler
  -> mapper-admitted query operations
  -> Prolog runtime
```

The evidence-bundle planner:

- sees only the compiled KB surface and the question
- does not see the raw source document
- does not see the answer key
- cannot authorize writes
- cannot bypass mapper admission

`--execute-evidence-bundle-plan` is stricter and still query-only: it executes only plan templates whose predicate and arity already appear in the compiled KB inventory or the virtual temporal helper inventory. It is useful as a diagnostic, but APR-011 showed it should not be a default scoring path yet because extra query evidence can add answer-surface noise.

`--evidence-bundle-context-filter` uses predicates from the LLM-owned plan to compact `relevant_clauses` before the normal Semantic IR QA compiler runs. BTC-026 showed the idea can rescue focused hard rows, but replacing the broad clause view too aggressively can lose partial support elsewhere. The likely next version should keep a small broad-context floor and add focused clauses on top.

## Evidence-Mode Selection

Avalon AG-007 adds a row-level selector over already-executed evidence modes.
This is different from rerunning compilation and different from a diagnostic
perfect selector.

The selector sees:

- the question;
- the mode labels;
- planned queries;
- executed query results;
- bounded structured row samples.

The selector does **not** see:

- source prose;
- answer keys;
- reference answers;
- judge labels;
- failure-surface labels;
- gold KBs.

The first Avalon run compared three evidence modes:

```text
baseline:             25 exact / 12 partial / 3 miss
postgate_rule_union:  27 exact / 10 partial / 3 miss
focused_context:      29 exact /  7 partial / 4 miss
```

The non-oracle selector produced:

```text
31 exact / 7 partial / 2 miss
selected best available mode on 38/40 rows
perfect-selector upper bound: 32 exact / 7 partial / 1 miss
```

This is the first strong evidence that safe accumulated surfaces can be
activated row-by-row instead of globally. The model owns evidence-mode choice,
but it only chooses among already admitted/query-only evidence bundles. It
cannot write, read the answer key, or bypass the mapper.

One important operational lesson: selector evidence must include enough
structured result rows. A five-row sample hid decisive support in wide result
tables and scored `28 exact / 9 partial / 3 miss`; increasing the sample to
sixteen rows produced the `31 exact` result.

The next Black Lantern replay is the caution sign. The same selector mechanism
ran cleanly over baseline, narrow evidence filtering, and broad evidence
filtering, but selected only `28 exact / 9 partial / 3 miss` against a
`33 exact / 4 partial / 3 miss` upper bound. Adding each mode's QA self-check
notes moved exact count to `29` but increased misses to `4`.

That negative transfer is useful: row-level activation is now a real mechanism,
but the selector must learn evidence completeness, not merely evidence
directness. It should not become the default until calibrated across fixture
types.

The first calibration check split that posture into explicit harness dials:

```powershell
python scripts/select_qa_mode_without_oracle.py `
  --selection-policy direct `
  --sample-row-limit 16 `
  ...
```

Available selector policies:

- `direct`: stable default; prefer direct, specific, non-empty evidence over
  broad relaxed fallbacks when modes are close.
- `completeness`: experimental; prefer broader evidence when it covers more
  entities, statuses, contrasts, conditions, timestamps, or rule consequences
  named by the question.
- `relevance`: experimental; penalize non-empty rows centered on a different
  named person, organization, rule, event, deadline, correction, or decision
  than the question asks about.

`--include-self-check` optionally adds bounded QA self-check notes to selector
evidence. It is not baseline input.

Current calibration:

```text
Avalon direct replay:              30 exact / 9 partial / 1 miss
Avalon completeness+self-check:    27 exact / 9 partial / 2 miss, 2 selector errors
Black Lantern direct:              28 exact / 9 partial / 3 miss
Black Lantern self-check:          29 exact / 7 partial / 4 miss
Black Lantern completeness+self-check:
                                   31 exact / 6 partial / 3 miss
Avalon relevance:                  30 exact / 8 partial / 2 miss
Black Lantern relevance:           28 exact / 8 partial / 3 miss, 1 selector error
```

The research lesson is that evidence-mode selection is itself a query-surface
control problem. Completeness pressure helps broad multi-part questions but can
overrule simpler direct-support rows. Relevance pressure names the wrong-subject
failure mode but did not beat the other policies in this replay. The safe
default remains direct; alternate policies must be reported as diagnostic
variants.

`--classify-failure-surfaces` adds a structured diagnostic pass after judging non-exact rows. It sees the reference answer, compiled KB inventory, admitted clauses, emitted queries, and query results. It does not see the raw source document and it cannot write. Its labels are:

- `compile_surface_gap`
- `query_surface_gap`
- `hybrid_join_gap`
- `answer_surface_gap`
- `judge_uncertain`

Existing QA artifacts can be classified without rerunning the QA pass:

```powershell
python scripts/classify_domain_bootstrap_qa_failures.py `
  --qa-json tmp/domain_bootstrap_qa/<run>.json
```

That is the preferred efficiency path when a run already has judged rows. It spends model time only on the remaining non-exacts.

This follows the project rule: no Python NLP over raw prose.

## Support-Row Acquisition

APR exposed a fourth practical move that still belongs to the compile surface:

```text
safe backbone compile
  -> support-row acquisition pass
  -> deterministic safe union
  -> QA over the accumulated surface
```

`scripts/run_support_acquisition_pass.py` implements this as an experimental
separate pass. It receives:

- the raw source document as direct evidence;
- an already-admitted compile surface as structured anchor context;
- a support-only predicate palette.

It may propose rows such as:

- `support_reason/2`
- `support_effect/2`
- `support_tradeoff/3`
- `support_exception/2`
- `support_positive_counterpart/2`

Those rows still go through the normal Semantic IR mapper. Python does not read
the source prose to derive the support rows; it only supplies the raw source,
structured admitted anchors, and predicate contracts.

APR-016 is the current proof point: the default enterprise-guidance profile was
not widened, but two independent support-only passes plus deterministic safe
union moved the fixture from APR-010's `37 exact / 4 partial / 2 miss` to `42
exact / 1 partial / 0 miss`.

The lesson is:

```text
Do not widen the default profile to chase rationale rows.
Acquire support rows in a separate pass and union only mapper-admitted clauses.
Multiple independently admitted support views may be better than any one view.
```

## Current Lesson

APR showed a clean distinction:

```text
Ingestion got the enterprise guidance fixture to useful.
Query strategy got it to strong.
Profile widening and generic rationale predicates regressed.
Support-row acquisition plus safe union got it stronger.
```

The current design principle is:

```text
Specialize passes before widening the default predicate menu.
```

Adding broad or answer-shaped predicates can make the compiler less useful by pulling it away from the durable backbone. The better frontier is to preserve a balanced compile surface and improve how questions retrieve support from it.
