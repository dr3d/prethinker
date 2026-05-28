# ACH Stress Public Batch Worksheet

Date: 2026-05-28

Batch:

```text
datasets\real_world_transfer\fresh_ach_stress_public_20260528_01
```

Purpose:

Test Prethinker on four public, source-contained ACH stress fixtures:

- `ntsb_engine_power_001`
- `fda_warning_letter_001`
- `sec_restatement_001`
- `legal_order_chronology_001`

The batch is deliberately not just QA. It is meant to pressure whether the ACH
lane can distinguish a high-sensitivity case from a low-sensitivity control.

## Intake

Initial package issue:

- An empty extraction artifact directory named
  `{ntsb_engine_power_001,fda_warning_letter_001,sec_restatement_001,legal_order_chronology_001}`
  was present under the batch root.
- It was verified empty and removed.

Validator update:

- `scripts\validate_fresh_ugly_batch.py` now accepts `qa.md` files that contain
  bold `Q/A` blocks, when `oracle.jsonl` is complete.
- This is intake tooling only; it does not alter compile or query behavior.

Validation artifact:

```text
C:\prethinker_tmp_archive\fresh_ach_stress_public_20260528_01_validation_20260528.md
```

Result:

```text
fixtures: 4 / 4
questions: 60
issues: 0
warnings: 24
status: pass
```

The warnings mostly mark reference-answer terms that also appear in
`fixture_notes.md` or metadata. They are review signals, not hard package
failures.

## Compile R1

Command shape:

```powershell
python scripts\run_domain_bootstrap_file_batch.py `
  --dataset-root datasets\real_world_transfer\fresh_ach_stress_public_20260528_01 `
  --out-root C:\prethinker_tmp_archive\fresh_ach_stress_public_20260528_01_r1_20260528\compile_r1 `
  --fixture ntsb_engine_power_001 `
  --fixture fda_warning_letter_001 `
  --fixture sec_restatement_001 `
  --fixture legal_order_chronology_001 `
  --model qwen/qwen3.6-35b-a3b `
  --base-url https://openrouter.ai/api/v1 `
  --timeout 1200 `
  --lanes 4 `
  --compile-source `
  --compile-flat-plus-plan-passes `
  --focused-pass-ops-schema `
  --source-entity-ledger `
  --archival-identifier-ledger `
  --source-record-ledger `
  --source-record-ledger-facts `
  --profile-delivery-repair-pass `
  --intake-registry-context `
  --review-profile `
  --profile-review-retry `
  --quality-gate `
  --quality-retry-on-hold `
  --quality-retry-max-attempts 1 `
  --openrouter-allow-fallbacks false `
  --openrouter-require-parameters true
```

Summary artifact:

```text
C:\prethinker_tmp_archive\fresh_ach_stress_public_20260528_01_r1_20260528\compile_r1_summary.md
```

Result:

```text
parsed OK: 4 / 4
compile admitted / skipped: 400 / 25
diagnostic rejected flat-pass skips: 0
quality gate pass / hold: 1 / 3
runtime/write/compatibility: no compile runtime failure rows observed
```

Compile gate:

```text
fda_warning_letter_001: hold
  compile_health zero-yield planned passes despite 28 admitted facts.

legal_order_chronology_001: hold
  source-authority pair preservation ledger-only
  source-claim partial delivery
  role backbone missing with broad source_detail wrapper

ntsb_engine_power_001: hold
  source_attributed_claim/4 offered but undelivered for two source signals

sec_restatement_001: pass
```

Read:

The gate is behaving independently from QA. Three holds did not prevent strong
QA, but they remain compile-surface signals.

## QA R1

Initial QA returned zero questions because the QA runner did not parse bold
`**Q1 [tag]**` markdown. Fixed in:

```text
scripts\run_domain_bootstrap_qa.py
tests\test_domain_bootstrap_qa.py
```

QA artifact:

```text
C:\prethinker_tmp_archive\fresh_ach_stress_public_20260528_01_r1_20260528\qa_r1_fixed_summary.md
```

Result:

```text
questions: 60
exact / partial / miss: 58 / 1 / 1
exact rate: 96.67%
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
provider: OpenRouter
model: qwen/qwen3.6-35b-a3b
provider routing: allow_fallbacks=false, require_parameters=true
lanes: 4
```

Per fixture:

```text
fda_warning_letter_001: 15 / 0 / 0
legal_order_chronology_001: 15 / 0 / 0
ntsb_engine_power_001: 14 / 0 / 1
sec_restatement_001: 14 / 1 / 0
```

Residue:

```text
ntsb_engine_power_001 q012
  verdict: miss
  ordinary QA surface: compile_surface_gap
  read: this is an ACH/sensitivity counterfactual being forced through the QA
        lane, not a simple source-fact lookup.

sec_restatement_001 q003
  verdict: partial
  ordinary QA surface: query_surface_gap
  read: the compile contains the right error type, but query/rendering did not
        isolate the concise "intrasegment-vs-intersegment misclassification"
        answer cleanly.
```

QA-failure ACH triage artifact:

```text
C:\prethinker_tmp_archive\fresh_ach_stress_public_20260528_01_r1_20260528\qa_failure_ach_r1_fixed.md
```

Read:

The deterministic QA-failure ACH probe disagreed with the ordinary failure
labels on both rows. It saw nonempty direct/source-record evidence and ranked
the residues as query/join/computation shaped rather than pure compile absence.

## ACH Payload Proposer R1

New runner:

```text
scripts\run_ach_payload_proposer.py
tests\test_ach_payload_proposer.py
```

Policy:

- The LLM proposes ACH judgments only.
- It does not write KB facts.
- It does not mutate QA verdicts.
- The prompt intentionally omits `expected_read` and `expected_relevance`.
- The deterministic scorer then ranks by least disconfirmation and computes
  single-row sensitivity.

Artifact directory:

```text
C:\prethinker_tmp_archive\fresh_ach_stress_public_20260528_01_r1_20260528\ach_payload_proposals_r1
```

Result:

```text
ntsb_engine_power_001:
  matrix: complete, warnings 0
  top: h1, expected h1
  expected sensitivity: high
  observed sensitivity rows: 0
  read: winner correct, sensitivity failed

fda_warning_letter_001:
  matrix: complete, warnings 0
  top: h2,h3 tie, expected h2
  expected sensitivity: medium
  observed sensitivity rows: 0
  read: judgment proposer failed to separate quality-unit systemic framing from
        specific qualification-decision framing

sec_restatement_001:
  matrix: complete, warnings 0
  top: h1, expected h1
  expected sensitivity: low
  observed sensitivity rows: e1
  read: winner correct, low-sensitivity control failed

legal_order_chronology_001:
  matrix: complete, warnings 0
  top: h1, expected h1
  expected sensitivity: medium
  observed sensitivity rows: 0
  read: acceptable for current single-row sensitivity scorer; medium expected
        includes plausible two-row flip not modeled by current scorer
```

ACH read:

This is the main blocker surfaced by the batch. The ACH lane can populate
complete matrices and usually find the expected winner, but it does not yet
measure sensitivity reliably. Two causes are visible:

- The judgment proposer is too coarse on competing-cause contradiction. In the
  SEC fixture, it treated some material-weakness remediation rows as neutral
  rather than inconsistent with the SEC-staff-driven hypothesis, causing a false
  sensitivity row.
- The scorer's single-axis assessment model cannot represent double-edged
  evidence cleanly. In the NTSB fixture, a row like "pilot expected 10+ gallons"
  is both adverse to fuel exhaustion on its face and reframed by the report as
  faulty fuel planning. The current assessment enum forces one cell value.

Do not claim ACH sensitivity is solved from this run.

## Leakage Hygiene

During the ACH plumbing search, old narrative source-flavored examples were
found in active instrument code. They were generalized and the leakage audit was
tightened to catch the specific vocabulary class in future runs.

Files touched:

```text
scripts\run_domain_bootstrap_file.py
src\semantic_ir.py
scripts\audit_active_instrument_leakage.py
```

Audit:

```text
python scripts\audit_active_instrument_leakage.py
-> forbidden hits: 0
```

Remaining warnings are domain-token warnings (`CFR`, `CMS`, `FEI`, etc.) in
query rendering and router policy. Those are not fixture-name hits.

## Verification

```text
python -m pytest tests\test_validate_fresh_ugly_batch.py -q
-> 12 passed

python -m pytest tests\test_domain_bootstrap_qa.py::test_parse_numbered_markdown_questions_accepts_bold_q_labels tests\test_ach_payload_proposer.py tests\test_ach_overlay.py -q
-> 8 passed

python -m pytest tests\test_domain_bootstrap_file.py::test_narrative_context_guards_attributes_and_official_duties tests\test_domain_bootstrap_file.py::test_source_entity_ledger_is_scoped_to_narrative_lanes tests\test_ach_payload_proposer.py tests\test_validate_fresh_ugly_batch.py tests\test_domain_bootstrap_qa.py::test_parse_numbered_markdown_questions_accepts_bold_q_labels -q
-> 17 passed

python -m py_compile src\semantic_ir.py scripts\run_domain_bootstrap_file.py scripts\audit_active_instrument_leakage.py scripts\run_ach_payload_proposer.py scripts\run_domain_bootstrap_qa.py scripts\validate_fresh_ugly_batch.py
-> pass
```

## Next

1. Keep the 96.67% QA result as a strong but narrow ACH-stress QA signal.
2. Do not spend repair energy on NTSB q012 as ordinary QA; it belongs to the
   ACH sensitivity lane.
3. Improve ACH sensitivity before using ACH as product evidence:
   - represent double-edged evidence explicitly, or
   - allow per-judgment support and disconfirmation weights, or
   - split double-edged evidence rows into distinct pro/con rows before scoring.
4. Re-run the ACH payload proposer after the sensitivity model changes.
5. Treat the SEC q003 partial as a small query/rendering precision issue, not a
   compile blocker.
