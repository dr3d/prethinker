# ACH Overlay Probe

**Status: parked exploratory overlay, not a current claim-bearing lane.**

This note is retained as a disciplined overlay experiment. It is not a product
claim, not a QA-score path, and not evidence that ACH can yet discriminate
genuinely contested real-world explanations.

Started: 2026-05-22

This note explores an Analysis of Competing Hypotheses overlay for Prethinker.
The goal is to test competing explanations against admitted evidence without
turning the exercise into an essay generator.

Current status: ACH is an exploratory overlay, not a product-ready claim and
not a QA-score improvement path. The existing probes show that the deterministic
scorer runs and preserves the model-proposes/code-decides boundary. They do not
yet show that ACH can discriminate genuinely contested explanations or identify
pivotal evidence in the wild.

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
  -> admitted typed facts, claims, dates, statuses, quantities, source coordinates
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
intentional for the first research step: a reviewer or later planner chooses the
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
from typed admitted predicates such as source-claim, status, event, date,
quantity, authority, and source-coordinate facts. It may carry source
coordinates for review, but it must not parse source-record/display prose as the
evidence route. The proposer remains separate from the scorer.

## Guardrails

- ACH is query-only over admitted typed evidence and source coordinates.
- ACH does not write truth into the KB.
- The overlay ranks by least inconsistent evidence, not by the biggest pile of
  supporting evidence.
- Missing matrix cells are warnings, not silent defaults.
- Sensitivity rows are explicit: if removing one evidence item changes the top
  hypothesis set, the report names it.
- QA exact-rate lifts from ACH-guided support surfaces are not claim-bearing
  unless they pass the current redaction, typed-plan, atom-shape, and judge-null
  controls.
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
      "source": {"kind": "compiled_query", "query": "access_condition(door_7, lock_untouched, SourceCoord)."}
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
3. Build one compiled-artifact probe, manually selecting evidence rows from
   admitted typed facts and reviewable source coordinates. Done:
   `experiments/ach_overlay/ntsb_marine_weather_v1`.
4. Only after the deterministic matrix behaves well, add an optional planner
   that proposes hypotheses and evidence-query templates.
5. Keep the planner separate from the scorer: model proposes, deterministic ACH
   code audits the matrix.

## Research Discipline

ACH should be treated as a sibling research overlay, not a scoring shortcut. Its
job is to test whether Prethinker's typed evidence substrate can support
reviewable competing-hypothesis reasoning without weakening the core gates.
Future product value may exist in legal, regulatory, clinical, financial,
insurance, safety, and investigation workflows, but current ACH evidence is not
a product-readiness result.

ACH must not be allowed to inflate QA exact-rate claims, write durable KB facts,
or introduce fixture-shaped language into the core instrument. A useful ACH
result means the matrix is complete, the judgments are auditable, the evidence
rows trace to admitted typed facts and source coordinates, and the ranking says
something clearer than a direct QA answer would have said.

Optimization target:

```text
make competing-explanation analysis understandable and reviewable
without weakening audit-grammar discipline
```

Near-term calibration should prefer documents with genuine disagreement or
alternative explanations. Overdetermined NTSB probable-cause reports are good
arithmetic sanity checks, but contested enforcement, claims, incident, and
litigation-like records are better tests of whether ACH can do the thing it is
for: distinguish real competing explanations and identify pivotal evidence.

Matrix population also needs independence discipline. A matrix hand-populated
by someone who already knows the answer can easily reproduce that answer by
construction. The next meaningful ACH test should use either independent matrix
population or a blinded review protocol where the matrix author does not shape
judgments after seeing the target conclusion.

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

Read: this is a real-document arithmetic sanity check, not validation of
contested ACH reasoning. The deterministic overlay ranks the NTSB
weather/towline-force explanation by least disconfirmation without turning that
ranking into a KB fact or contaminating QA metrics. But the case is
overdetermined, has one survivor, and reports zero sensitivity rows. It does
not yet show that ACH can discriminate balanced alternatives or identify
pivotal evidence.

The next ACH automation step, if pursued, is a small payload proposer that
suggests candidate evidence rows from typed admitted predicates and source
coordinates while leaving judgments to review/audit.

## Open Questions

- Should ACH judgments be proposed by an LLM, a user, or both?
- Should evidence diagnosticity live on the evidence row, the judgment, or both?
- How should absence evidence be represented so it is explicit rather than an
  accidental empty query?
- What makes an ACH result research-ready: matrix completeness, contested-case
  behavior, independent matrix population, or domain-specific reviewer approval?

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

Read: the scorer remained internally consistent on a fresh public NTSB surface
report. It ranked the unsafe-passing/evasive-action hypothesis as the single
least-disconfirmed explanation, matching the report's probable-cause theory,
while keeping hazmat-response, PPE, decontamination, and classification evidence
in a severity lane rather than confusing it with initiating crash cause.

This is still an overdetermined single-survivor case with zero sensitivity
rows. It is useful as a sanity check and boundary-preservation example, not as a
claim that ACH has been validated on contested evidence.

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

Read: the ACH scorer can also run over a compliance-style evidence matrix. On a
fresh FDA warning letter, the deterministic scorer ranked systemic
data-integrity failure as the least-disconfirmed explanation. The quality-unit
hypothesis remained plausible but lower-ranked, while narrower computer-control
and import-alert-status explanations were disconfirmed by broader inspection
findings and remediation demands.

This is not yet proof that ACH works as a compliance decision aid. The matrix
was hand-populated, the outcome collapsed to one survivor, and sensitivity rows
were zero. The result shows the overlay can preserve discipline on a compliance
payload; it does not yet exercise the hard ACH problem.

## 2026-05-25 QA Failure Triage Probe

Question:

Can ACH classify QA failure surfaces without letting the LLM mutate answers,
KB state, verdicts, or score claims?

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
query density, nonempty direct rows, historical source-record telemetry,
support-surface presence, query error counts, and generic question-shape tags.
The default run does not use the existing failure-surface classifier as
evidence. A second run includes that classifier label as one caged evidence row.

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
of those rows already had substantial direct evidence or historical
source-record telemetry and looked more like ordering, grouping, joining, or
route-selection failures.

Both readings can be true at different layers: the direct compile surface may
be too thin while the old source-record substrate contained enough prose to
recover the answer through now-disallowed routes. The research question is
which failure surface is real after the prose route is removed. ACH helps by
forcing that into a ranked, reviewable hypothesis rather than a single label.

Near-term implication:

Do not let ACH change QA scores. Use it as a diagnostic lens to decide whether
the next research probe should target direct compile preservation, query
routing, source-coordinate joins, or answer assessment. On Batch 03, the next
experiment should inspect the ACH-disagreement rows, especially rows labeled
`compile_surface_gap` but ranked `h_join_computation`, before assuming a
compile-side repair is the right first patch.

Follow-up, now historical:

The ACH read produced a useful intervention path at the time. A narrow
source-coordinate pass added query-only support for preceding headings, named
section windows, quote-to-heading location, elapsed date differences, and public
`.gov` contact emails. Targeted replay recovered intended rows without runtime,
write, or compatibility pressure, and the full Batch 03 R2 rerun reported
`273 / 11 / 16 = 91.0%` on 300 rows, up from `270 / 14 / 16 = 90.0%`.

Under the current sign-clean reset, that 91.0% is not claim-bearing. Some of
the added surfaces are typed computations, but named section windows and
quote-to-heading location are prose-adjacent in the exact way the reset warns
about. The result remains useful as a diagnostic example of ACH pointing at a
patch location, but no QA lift from this path should be cited unless it passes
redaction replay, typed-plan replay, atom-shape gates, and answer-judge null
controls.

The guard still matters: row-level comparison showed `7` baseline-exact
regressions, and `0` of those regressions had an added support surface. ACH was
therefore useful as a patch-location lens, but not as a scoring shortcut.

## 2026-05-28 Stress-Batch Read

The detailed ACH stress worksheet has been retired from `docs` to the local
archive to keep the public tree lean:

```text
C:\prethinker_tmp_archive\docs_worksheet_archive_20260601\ACH_STRESS_PUBLIC_20260528_WORKSHEET.md
```

Current read:

- ACH ranking is research-plausible as a deterministic overlay.
- The existing real-document probes mostly collapse to one survivor and zero
  sensitivity rows, so they do not yet validate the pivotal-evidence use case.
- High/low sensitivity discrimination looked promising under the locked scorer
  on one stress line, but medium sensitivity required a deterministic
  family-level pass on the same batch.
- This is not a solved-product or solved-research claim. The next meaningful
  test is a fresh heldout, genuinely contested ACH batch with independent or
  blinded matrix population, followed by the same no-KB-write, no-QA-mutation,
  typed-evidence-only discipline.

The original May 2026 fixture request has been aged out of the public tree.
Current fixture requests should be written from the active research question
rather than resurrecting the old work order.
