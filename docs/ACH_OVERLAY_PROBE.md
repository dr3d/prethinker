# ACH Overlay Probe

Started: 2026-05-22

This note explores an Analysis of Competing Hypotheses overlay for Prethinker.
The goal is to test competing explanations against admitted evidence without
turning the exercise into an essay generator.

## Shape

The first implementation is deterministic and local:

- `src/ach_overlay.py`
- `scripts/run_ach_overlay.py`
- `tests/test_ach_overlay.py`

It does not call an LLM, compile documents, query OpenRouter, mutate KB state,
or write durable facts. It scores a populated ACH matrix and writes harness-style
JSON/Markdown artifacts reporting whether the matrix is complete, which
hypotheses survive by least disconfirmation, and which evidence rows are most
diagnostic or sensitivity-critical.

## Why This Fits Prethinker

ACH is useful where the answer is not just a fact lookup but a disciplined
choice among plausible explanations. That includes legal disputes, incident
reports, clinical uncertainty, compliance interpretation, source credibility,
and root-cause analysis.

Prethinker's existing compile path can provide the evidence substrate:

```text
compiled KB artifact
  -> admitted facts, source rows, claims, dates, statuses, quantities
  -> ACH evidence rows
  -> hypotheses
  -> consistency / inconsistency / neutral / not-applicable matrix
  -> least-disconfirmed hypothesis ranking
```

## Harness Slipstream

ACH should enter the harness as a sibling stage, not as a compile or QA scoring
mutation:

```text
domain compile
  -> QA / evidence inspection
  -> ACH payload JSON
  -> scripts/run_ach_overlay.py
  -> ACH report JSON/Markdown
```

The current seam is manual payload construction from admitted evidence. That is
intentional for the first product step: a reviewer or later planner chooses the
hypotheses, evidence rows, and judgments; the deterministic scorer audits the
matrix. This lets ACH pilots sit beside existing compile/QA artifacts without
changing exact/partial/miss metrics.

Example:

```powershell
python scripts\run_ach_overlay.py `
  --payload experiments\ach_overlay\synthetic_root_cause_v1\ach_payload.json `
  --out-dir tmp\ach_overlay_runs
```

The next safe automation layer is a payload builder that proposes evidence rows
from admitted `source_record_*`, source-claim, status, event, date, quantity, and
authority predicates. The proposer remains separate from the scorer.

## Guardrails

- ACH is query-only over admitted evidence.
- ACH does not write truth into the KB.
- The overlay ranks by least inconsistent evidence, not by the biggest pile of
  supporting evidence.
- Missing matrix cells are warnings, not silent defaults.
- Sensitivity rows are explicit: if removing one evidence item changes the top
  hypothesis set, the report names it.
- Motivation, bias, incentives, and source interest are treated only as
  documented evidentiary pressures. They may affect claim weight or
  corroboration requirements, but they do not prove a claim false by
  themselves.

## Motivation And Bias Boundary

ACH is a useful place to explore theory-of-mind-adjacent evidence without
letting it leak into the base truth model. The overlay may represent facts such
as a source's financial stake, adversarial posture, authority role, prior
inconsistent statement, lack of firsthand access, or documented interest in an
outcome.

The safe claim is not "the person secretly wanted X, so the claim is false."
The safe claim is "the record documents an interest or bias pressure, so this
claim should be annotated and may require corroboration before it receives full
weight."

This keeps ACH aligned with Prethinker: disciplined evidentiary reasoning over
source-grounded records, not free-floating psychological inference.

## Payload Sketch

```json
{
  "schema_version": "ach_overlay_v1",
  "hypotheses": [
    {"id": "h_accident", "label": "Accidental failure"},
    {"id": "h_sabotage", "label": "Sabotage"}
  ],
  "evidence": [
    {
      "id": "e_lock",
      "label": "Lock was untouched",
      "diagnosticity": "critical",
      "source": {"kind": "compiled_query", "query": "source_record_text_atom(Row, Text)."}
    },
    {
      "id": "e_interest",
      "label": "Source had a documented financial interest in the outcome",
      "diagnosticity": "moderate",
      "source": {"kind": "compiled_query", "query": "source_interest(Source, Interest, Target)."}
    }
  ],
  "judgments": [
    {
      "evidence_id": "e_lock",
      "hypothesis_id": "h_accident",
      "assessment": "consistent",
      "rationale": "An untouched lock is compatible with accidental failure."
    },
    {
      "evidence_id": "e_lock",
      "hypothesis_id": "h_sabotage",
      "assessment": "inconsistent",
      "rationale": "Sabotage would usually require access or bypass evidence."
    },
    {
      "evidence_id": "e_interest",
      "hypothesis_id": "h_sabotage",
      "assessment": "consistent",
      "rationale": "A documented interest can create bias pressure, but it is not direct proof."
    }
  ]
}
```

The deterministic report shape is:

```text
matrix_complete
warnings
hypothesis_scores
diagnostic_evidence
sensitivity
surviving_hypotheses
```

## Probe Plan

1. Keep the initial overlay deterministic and unit-tested. Done.
2. Build one tiny synthetic fixture with three hypotheses and five evidence
   rows where the intended disconfirming evidence is obvious. Done.
3. Build one source-record probe from an existing compiled artifact, manually
   selecting evidence rows from admitted source facts. Done:
   `experiments/ach_overlay/ntsb_marine_weather_v1`.
4. Only after the deterministic matrix behaves well, add an optional planner
   that proposes hypotheses and evidence-query templates.
5. Keep the planner separate from the scorer: model proposes, deterministic ACH
   code audits the matrix.

## Product Discipline

ACH should be treated as a sibling product surface, not a scoring shortcut. Its
job is to make Prethinker's source-grounded substrate legible to domains that
already think in evidence matrices, competing hypotheses, disconfirmation, and
reviewable reasoning. That is useful for market reception in legal, regulatory,
clinical, financial, insurance, safety, and investigation workflows.

ACH must not be allowed to inflate QA exact-rate claims, write durable KB facts,
or introduce fixture-shaped language into the core instrument. A useful ACH
result means the matrix is complete, the judgments are auditable, the evidence
rows trace to admitted source/claim surfaces, and the ranking says something
clearer than a direct QA answer would have said.

Optimization target:

```text
make competing-explanation analysis understandable and reviewable
without weakening audit-grammar discipline
```

Near-term calibration should prefer documents with genuine disagreement or
alternative explanations. Overdetermined NTSB probable-cause reports are good
sanity checks, but contested enforcement, claims, incident, and litigation-like
records are better tests of whether ACH is product-ready.

## 2026-05-23 Real-Document Probe

Payload:

```text
experiments/ach_overlay/ntsb_marine_weather_v1/ach_payload.json
```

Run artifact:

```text
C:\prethinker_tmp_archive\work_20260523_record_narrative_ach\ach_overlay_runs\ntsb_marine_weather_v1
```

Result:

```text
hypotheses: 4
evidence rows: 6
judgments: 24
matrix complete: true
warnings: 0
top hypothesis: h_weather_towline_force
surviving hypotheses: 1
sensitivity rows: 0
```

Read: the deterministic overlay behaves well on a real incident-report payload.
It ranks the NTSB weather/towline-force explanation by least disconfirmation
without turning that ranking into a KB fact or contaminating QA metrics. The
next ACH step is a small payload-proposer that suggests candidate evidence rows
from admitted source-record and claim surfaces while leaving final judgments to
review/audit.

## Open Questions

- Should ACH judgments be proposed by an LLM, a user, or both?
- Should evidence diagnosticity live on the evidence row, the judgment, or both?
- How should absence evidence be represented so it is explicit rather than an
  accidental empty query?
- What makes an ACH result product-ready: matrix completeness, transfer probe
  behavior, or domain-specific reviewer approval?

## 2026-05-24 Fresh Ugly Batch 02 Probe

Payload:

```text
experiments/ach_overlay/ntsb_surface_teutopolis_v1/ach_payload.json
```

Run artifact:

```text
C:\prethinker_tmp_archive\fresh_ugly_public_20260524_02_r1_20260524\ntsb_surface_teutopolis_v1
```

Result:

```text
hypotheses: 5
evidence rows: 6
judgments: 30
matrix complete: true
warnings: 0
top hypothesis: h_teen_unsafe_passing_evasive_loss_control
surviving hypotheses: 1
sensitivity rows: 0
```

Read: ACH remained useful on a fresh public NTSB surface report. The overlay
ranked the unsafe-passing/evasive-action hypothesis as the single least
disconfirmed explanation, matching the report's probable-cause theory, while
keeping hazmat-response, PPE, decontamination, and classification evidence in a
severity lane rather than confusing it with initiating crash cause.

## 2026-05-24 FDA Warning Letter Probe

Payload:

```text
experiments/ach_overlay/fda_warning_data_integrity_v1/ach_payload.json
```

Run artifact:

```text
C:\prethinker_tmp_archive\ach_overlay_runs_20260524\fda-warning-data-integrity-v1_ach_report.md
```

Result:

```text
hypotheses: 4
evidence rows: 6
judgments: 24
matrix complete: true
warnings: 0
top hypothesis: h_data_integrity_systemic_primary
surviving hypotheses: 1
sensitivity rows: 0
```

Read: ACH also works as a compliance evidence matrix, not only as an incident
root-cause lens. On a fresh FDA warning letter, the deterministic scorer ranked
systemic data-integrity failure as the least-disconfirmed explanation. The
quality-unit hypothesis remained plausible but lower-ranked, while narrower
computer-control and import-alert-status explanations were disconfirmed by the
broader inspection findings and remediation demands.

## 2026-05-25 QA Failure Triage Probe

Question:

Can ACH improve QA without letting the LLM mutate answers, KB state, or
verdicts?

Probe:

```text
script:
  scripts/run_qa_failure_ach_probe.py

module:
  src/qa_failure_ach.py

baseline artifact:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_r1_20260524\fresh_ugly_public_20260524_03_qa_r1_summary.json

ACH artifacts:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_r1_20260524\fresh_ugly_public_20260524_03_qa_failure_ach_probe.md
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_r1_20260524\fresh_ugly_public_20260524_03_qa_failure_ach_probe_with_label.md
```

Shape:

The probe builds a fixed ACH matrix for each non-exact QA row. The competing
hypotheses are patch locations:

```text
h_compile_preservation
h_query_route
h_join_computation
h_answer_assessment
```

Evidence comes only from archived row telemetry: response envelope status,
query density, nonempty direct/source-record rows, support-surface presence,
query error counts, and generic question-shape tags. The default run does not
use the existing failure-surface classifier as evidence. A second run includes
that classifier label as one caged evidence row.

Result on Batch 03:

```text
rows:
  30 non-exact

default, not using existing failure label:
  h_compile_preservation: 2
  h_join_computation: 20
  h_join_computation,h_query_route: 8
  agreement with existing failure-surface classifier: 6 / 30

with existing failure label as caged evidence:
  h_compile_preservation: 1
  h_query_route: 1
  h_join_computation: 20
  h_join_computation,h_query_route: 8
  agreement with existing failure-surface classifier: 9 / 30
```

Read:

This is a useful discomfort signal. The existing failure-surface classifier
called `22 / 30` non-exact rows compile-surface gaps. The ACH triage says many
of those rows already have substantial source-record or direct query evidence
and look more like ordering, grouping, joining, or route-selection failures.

Both readings can be true at different layers: the direct compile surface may
be too thin while the source-record substrate still contains enough evidence to
recover the answer. The product question is which patch location is most useful
next. ACH helps by forcing that into a ranked, reviewable hypothesis rather
than a single label.

Near-term implication:

Do not let ACH change QA scores. Use it as a diagnostic lens to decide whether
the next repair should target direct compile preservation, query routing,
source-coordinate joins, or answer assessment. On Batch 03, the next experiment
should inspect the ACH-disagreement rows, especially rows labeled
`compile_surface_gap` but ranked `h_join_computation`, before assuming a
compile-side repair is the right first patch.

Follow-up:

The ACH read produced a useful intervention path. A narrow source-coordinate
pass added query-only support for preceding headings, named section windows,
quote-to-heading location, elapsed date differences, and public `.gov` contact
emails. Targeted replay recovered the intended rows without runtime, write, or
compatibility pressure. The full Batch 03 R2 rerun reached `273 / 11 / 16 =
91.0%` on 300 rows, up from `270 / 14 / 16 = 90.0%`.

The guard still matters: row-level comparison showed `7` baseline-exact
regressions, and `0` of those regressions had an added support surface. ACH was
therefore useful as a patch-location lens, but the next blocker is not just
more support breadth. It is dense-document stability over SEC-style biography,
exhibit, dollar/percentage, covenant, signature-block, and conditional-term
rows.

## 2026-05-28 Stress-Batch Read

The detailed ACH stress worksheet has been retired from `docs` to the local
archive to keep the public tree lean:

```text
C:\prethinker_tmp_archive\docs_worksheet_archive_20260601\ACH_STRESS_PUBLIC_20260528_WORKSHEET.md
```

Current read:

- ACH ranking is product-plausible across recent stress batches.
- High/low sensitivity discrimination is promising under the locked scorer.
- Medium sensitivity required a deterministic family-level pass. That pass
  recovered the previously missed medium case on the same batch without
  reintroducing low-control false positives.
- This is still not a solved-product claim. The family threshold and locked
  scorer need a fresh heldout ACH batch before we say Prethinker can reliably
  identify pivotal evidence.

The original May 2026 fixture request has been aged out of the public tree.
Current fixture requests should be written from the active research question
rather than resurrecting the old work order.
