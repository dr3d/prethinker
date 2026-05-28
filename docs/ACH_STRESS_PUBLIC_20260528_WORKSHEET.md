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

## ACH Sensitivity R2: Axis Fit, Dependencies, Support Drop

Intervention:

- Added `question_axis` to the ACH proposer output.
- Added `hypothesis_axis_fit` (`direct`, `partial`, `off_axis`) so a true but
  compatible scope/consequence claim does not outrank a direct answer to the
  ACH question.
- Added per-cell judgment weights.
- Added `judgment_dependencies` / `omission_effects` for conditional evidence
  interpretation.
- Added proposal-contract retry: if a rationale cites another evidence id
  without declaring the dependency, the runner asks for a corrected complete
  matrix.
- Added deterministic support-drop sensitivity: a row can be sensitive even
  when the top hypothesis does not flip, if declared omission effects collapse
  the top hypothesis's support.

Artifact directory:

```text
C:\prethinker_tmp_archive\fresh_ach_stress_public_20260528_01_r10_20260528\ach_axis_dependency_support_r10
```

R10 emitted summaries:

```text
ntsb_engine_power_001:
  top: h1, expected h1
  sensitivity rows: e1
  read: high-sensitivity pivotal physical row now detected

sec_restatement_001:
  top: h1, expected h1
  sensitivity rows: 0
  read: low-sensitivity control now clean; h2 correctly treated as partial
        axis fit (scope/consequence), not the causal explanation

fda_warning_letter_001:
  top: h2, expected h2
  sensitivity rows: 0
  read: ranking fixed; medium sensitivity still under-detected

legal_order_chronology_001:
  top: h1, expected h1
  sensitivity rows: 0 in emitted R10 summary
  proposal contract: 1 residual violation after 2 retries
  read: ranking fixed; medium sensitivity still not clean in emitted summary
```

After calibrating support-drop sensitivity to `0.30`, rescoring the same R10
scorer payloads gives:

```text
ntsb_engine_power_001: e1
sec_restatement_001: 0
fda_warning_letter_001: 0
legal_order_chronology_001: e2, e3
```

Current read:

- ACH ranking is materially better: R10 selected the expected winner on all
  four stress fixtures.
- The axis-fit addition fixed the SEC failure mode: compatible
  scope/consequence hypotheses are visible as partial-axis claims instead of
  winning by accumulated support.
- High sensitivity is now detected on the NTSB control without requiring a fake
  winner flip; support-collapse is the right product signal there.
- Low sensitivity stays clean on the SEC control at the `0.30` support-drop
  threshold.
- Medium sensitivity remains immature. Legal now shows medium-ish support-drop
  rows under rescoring, but FDA is still quiet, and exact expected pivotal-row
  matching is not reliable enough to claim.
- The dependency-contract retry is useful but incomplete: it catches explicit
  evidence-id leakage in rationales, but the model can still describe another
  row indirectly. Treat this as a cage, not a solved dependency parser.

Do not claim ACH sensitivity is solved. The honest claim is narrower and
stronger: ACH ranking now looks product-plausible on this batch; sensitivity has
clear high/low discrimination and a partially working dependency story, with
medium sensitivity still the next blocker.

## Fresh ACH Stress Batch 02

Dataset:

```text
datasets\real_world_transfer\fresh_ach_stress_public_20260528_02
```

Intake:

- 6 fixtures present.
- Sensitivity distribution: 2 high, 2 medium, 2 low.
- Required ACH files present for each fixture:
  `source.md`, `source_original.txt`, `source_url.txt`, `metadata.json`,
  `fixture_notes.md`, `qa.md`, `oracle.jsonl`, `ach_payload.json`.
- `batch_manifest.json` present.
- `ach_payload.json` parses for all fixtures.
- `oracle.jsonl` parses for all fixtures.
- Evidence anchors appear in `source.md`.
- Evidence coordinates map to bracketed source headings.
- No `expected_read` / `expected_relevance` leakage in `source.md`.
- No source URL duplicates found against maintained `datasets\real_world_transfer`
  batches.

Note: `scripts\validate_fresh_ugly_batch.py` fails this batch because that
validator is shaped for 25-row ordinary QA batches with
`qa_authored_with_answers.md`. This ACH stress batch intentionally has 13-14 QA
rows plus `ach_payload.json`, so the validator failure is not treated as an ACH
intake failure.

ACH locked R1:

```text
C:\prethinker_tmp_archive\fresh_ach_stress_public_20260528_02_r1_20260528\ach_locked_r1
```

Runner settings:

```text
model: qwen/qwen3.6-35b-a3b
base_url: https://openrouter.ai/api/v1
provider fallbacks: false
require parameters: true
temperature: 0
proposal contract retries: 2
support-drop threshold: locked at 0.30
```

Aggregate:

```text
ranking: 6/6 expected winners
matrix completeness: 6/6 complete
warnings: 0/6
low-sensitivity controls: 2/2 clean
high-sensitivity expected pivotal rows: 0/2 exact
medium-sensitivity rows: 0/2 detected
proposal contract residual violations: 2 fixtures
```

Per fixture:

```text
enforcement_single_document_hook_001 (high):
  top: h1, expected h1
  sensitivity: 0
  expected pivotal: e4
  proposal contract: 1 residual violation after 2 retries
  read: ranking works; high sensitivity missed

ntsb_pivotal_physical_001 (high):
  top: h1, expected h1
  sensitivity: e5
  expected pivotal: e1
  proposal contract: 1 residual violation after 2 retries
  read: sensitivity exists, but the wrong row is flagged; the proposer made the
        inspection-detectability row load-bearing instead of the official
        cause / physical-anomaly row

legal_controls_medium_001 (medium):
  top: h1, expected h1
  sensitivity: 0
  read: medium sensitivity missed

regulatory_quality_medium_001 (medium):
  top: h1, expected h1
  sensitivity: 0
  read: medium sensitivity missed

public_order_low_001 (low):
  top: h1, expected h1
  sensitivity: 0
  read: low control clean

sec_scope_low_001 (low):
  top: h1, expected h1
  sensitivity: 0
  read: low control clean
```

Current read:

- The ranking story generalized strongly: all six unseen fixtures selected the
  expected winner with complete matrices and zero scorer warnings.
- The axis-fit change transferred: both low controls stayed quiet, including
  the SEC scope/consequence trap.
- Sensitivity did not generalize yet. The decisive failure is not threshold
  calibration; it is dependency declaration. The proposer often reaches the
  correct winner but does not emit the dependency rows needed for deterministic
  sensitivity, even after retries.
- The most useful blocker is now narrow: improve dependency extraction or add a
  deterministic post-pass that detects cross-row dependence from structured
  rationales without using fixture/source vocabulary.

Do not use batch 02 to claim solved ACH sensitivity. Use it to claim that ACH
ranking is robust on unseen official documents, and that sensitivity remains
the active product blocker.

## ACH Stress Summarizer

Added a dedicated ACH stress-run summarizer so future ACH batches are scored
against ACH expectations rather than ordinary QA fixture assumptions.

Tool:

```text
scripts\summarize_ach_stress_run.py
```

Batch 02 R1 summary artifacts:

```text
C:\prethinker_tmp_archive\fresh_ach_stress_public_20260528_02_r1_20260528\ach_locked_r1_summary.json
C:\prethinker_tmp_archive\fresh_ach_stress_public_20260528_02_r1_20260528\ach_locked_r1_summary.md
```

Generated aggregate:

```text
fixtures: 6
ranking correct: 6
matrix complete: 6
warnings: 0
contract residual fixtures: 2
high pivotal detected: 0
medium detected: 0
low clean: 2
alignment: clean 2, missed 3, wrong_or_partial_sensitivity 1
```

This confirms the worksheet read with a repeatable scorecard: ranking and low
controls are stable; high/medium sensitivity remains blocked on dependency
capture and contract adherence.

## Batch 02 R2 Dependency-Audit Prompt

Change tested:

- The ACH payload proposer now explicitly audits every evidence row as a
  possible interpretation anchor after filling the matrix.
- The audit is fixture-free and structural: if removing one row would change
  any other evidence-hypothesis assessment or weight, the proposer should emit
  matching `judgment_dependencies` and `omission_effects`.
- Reports now preserve `proposal_contract_violations` so residual contract
  failures are inspectable, not only counted.

R2 artifact directory:

```text
C:\prethinker_tmp_archive\fresh_ach_stress_public_20260528_02_r2_dependency_prompt_20260528\ach_high_probe
```

R2 summary artifacts:

```text
C:\prethinker_tmp_archive\fresh_ach_stress_public_20260528_02_r2_dependency_prompt_20260528\ach_dependency_prompt_r2_summary.json
C:\prethinker_tmp_archive\fresh_ach_stress_public_20260528_02_r2_dependency_prompt_20260528\ach_dependency_prompt_r2_summary.md
```

R1 -> R2:

```text
ranking correct: 6/6 -> 6/6
matrix complete: 6/6 -> 6/6
warnings: 0 -> 0
contract residual fixtures: 2 -> 0
high pivotal detected: 0/2 -> 1/2
medium detected: 0/2 -> 0/2
low clean: 2/2 -> 2/2
```

Per-fixture R2:

```text
enforcement_single_document_hook_001: high, top h1, no sensitivity rows
ntsb_pivotal_physical_001: high, top h1, sensitivity e1/e3/e5/e6, expected e1 found
legal_controls_medium_001: medium, top h1, no sensitivity rows
regulatory_quality_medium_001: medium, top h1, no sensitivity rows
public_order_low_001: low, top h1, no sensitivity rows
sec_scope_low_001: low, top h1, no sensitivity rows
```

Read:

- The dependency-audit prompt is a real improvement: it removed residual
  contract violations, preserved the low controls, and recovered one high
  pivotal case.
- It is not a complete sensitivity solution. The remaining high miss is not an
  explicit row-dependency failure; it is an evidence-role failure where a row is
  expected to matter because it is the only concrete occurrence/outcome hook for
  an otherwise well-supported responsibility theory.
- Medium sensitivity remains immature. Current scoring detects single-row
  flips and support drops, but not multi-row weakening or family-level
  dependence.
- Do not tune thresholds on this batch. The next ACH mechanism should be
  evaluated against a fresh heldout ACH set.

Follow-up instrumentation:

- The deterministic ACH report now includes `top_support_contributions`, a
  per-evidence breakdown of support weight and support share for the single
  top hypothesis.
- The proposer harness summary now records the leading `top_support_evidence_ids`.
- This does not change ranking or sensitivity. It is a diagnostic surface for
  separating missed dependency capture from underweighted direct-support or
  concrete-hook evidence.

Regenerated R2 summary with support diagnostics:

```text
enforcement expected pivotal support: rank 5, share 0.1154
ntsb expected pivotal support: rank 1, share 0.1923
```

This supports the current blocker read: the remaining high miss is not a
classic dependency failure. The proposer treated the expected pivotal row as a
low-share consequence/hook row, while the recovered NTSB pivotal row was the
top direct support row and also generated omission effects.

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
