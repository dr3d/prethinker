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
