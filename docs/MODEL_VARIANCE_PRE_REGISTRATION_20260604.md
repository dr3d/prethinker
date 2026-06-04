# Model Variance Pre-Registration - 2026-06-04

This protocol freezes the next model/runtime variance excursion before any new
Gemma, Qwen, seed, or temperature result can influence the plan.

The purpose is robustness measurement, not model shopping. The deliverable is a
spread of outcomes with row-level churn and gate status. The deliverable is not
the best score observed in any arm.

## Research Question

```text
Are the current closed-domain transfer cells a property of the governed
predicate-pack method, or are they materially dependent on one local Qwen
serving path and decoding bundle?
```

This protocol can change confidence in the current claim. It does not expand
the claim to new families, broad QA, product readiness, or arbitrary document
understanding.

## Primary Anchors

The first variance cell is SEC Form 8-K because it was the strongest current
skeleton-pack transfer example and already had a seed plus three unlike
transfers. Later on 2026-06-04, a SEC value-axis audit found item/exhibit
role-axis mixing in the expected facts themselves, so this protocol is now read
as a variance/model-sensitivity diagnostic rather than a pristine methods-anchor
confirmation.

Compile-fact anchors:

```text
sec_form_8k_skeleton_v1
sec_form_8k_skeleton_transfer_001
sec_form_8k_skeleton_transfer_002
sec_form_8k_skeleton_transfer_003
```

Current reference measurement:

```text
support>=2: 50 / 50
per-run exact: 144 / 150
forbidden support: 0
redaction replay: 144 / 144 exact rows survive
typed-plan replay: 144 / 144 exact rows replay through registered carriers
```

Query anchor:

```text
SEC transfer_003 five-row atom-library query smoke
```

Current reference measurement after mapper variable preservation:

```text
5 / 5 judged exact
typed-plan replay: 5 / 5
redacted rejudge: 5 / 5
prose-dependent exact rows: 0
compatibility/runtime/write rows: 0
```

Do not add or remove anchor cells after seeing a result. If an anchor cannot run
because a runtime is unavailable, mark that cell as unavailable or deferred.
Do not silently substitute a friendlier cell.

## Arms

### Arm A - Reference Local Qwen, Temperature 0

Use the current local LM Studio Qwen lane exactly as loaded and record all
available metadata.

Required metadata:

```text
provider: lmstudio
model id: as returned by /v1/models or /api/v0/models
model file / quantization: as shown by LM Studio
architecture: as returned or observed
loaded context length: as returned or observed
temperature: 0.0
top_p: 1.0 unless the run explicitly records otherwise
seed: recorded if supplied, but not treated as proof of determinism
```

Run count:

```text
N=5 same-condition draws for the SEC compile-fact anchors
N=5 same-condition draws for the SEC atom-library query anchor if practical
```

If N=5 is too expensive, stop at N=3 and record the truncation as a protocol
deviation. Do not replace missing draws with another model/provider.

### Arm B - Reference Local Qwen, Temperature Sweep

This arm is diagnostic only. It does not change the default claim setting.

Run:

```text
temperature=0.2, N=3
temperature=0.5, N=3
```

Use the same SEC anchors and all other settings from Arm A. Report all churn.
Expect scores to wobble. Do not chase the wobble with prompt or schema changes.

### Arm C - Dense Gemma Control

Gemma is a control, not a candidate replacement. Use the exact locally loaded or
hosted Gemma model id if and only if it is available.

First run only:

```text
temperature=0.0
N=5 if practical, otherwise N=3 with deviation recorded
same SEC anchors
same gates
```

If Gemma holds clean, the result hardens the claim by showing that the SEC
skeleton result is not only a Qwen/MoE artifact. If Gemma degrades, that is a
finding, not a reason to discard the cell.

Do not tune predicate contracts, prompts, post-processors, query retry logic, or
oracles between the Qwen and Gemma arms.

### Deferred Arms

OpenRouter Qwen, local dense models, alternate quants, and thinking/reasoning
lanes are not part of this pre-registration unless a later dated protocol adds
them.

Do not mix OpenRouter and local LM Studio results as interchangeable. If
OpenRouter enters a later protocol, provider/backend metadata is part of the
cell identity.

## Gates

Every compile-fact anchor must report:

```text
support>=2 expected facts
per-run exact / partial / miss if a per-run QA view is available
supported forbidden facts
registered signatures
atom-shape findings
lens-scope findings
carrier value-domain findings where applicable
redaction replay for exact rows
typed-plan replay for exact rows
compatibility/runtime/write rows
metadata completeness
```

Every atom-library query anchor must report:

```text
exact / partial / miss
blocked atom constants
blocked source-record plans
typed-plan replay
redacted rejudge
prose-dependent exact rows
compatibility/runtime/write rows
metadata completeness
```

A cell that fails hygiene is reported as failed. It is not repaired inside this
protocol.

## Reporting Rules

Report all cells, including bad ones.

For each arm, report:

```text
mean and range, when a numeric summary is appropriate
row-level churn against the reference cell
which rows are stable exact, unstable, or stable miss
which gates pass or fail
metadata gaps
latency and cost when available
```

Do not report "best model per row" or "best model per fixture" as a claim. That
would be model-shopping.

Do not treat a higher score at a nonzero temperature as a new default. Nonzero
temperature arms are variance probes unless a later pre-registered protocol
turns them into a claim lane.

## Stop Conditions

Stop the protocol and write the result, rather than repairing, when any of these
happen:

- an anchor cell fails a hard governance gate;
- the model/runtime is unavailable;
- metadata cannot identify the model/provider/settings bundle;
- a run hits rate limits or local runtime instability repeatedly;
- row churn is broad enough that the cell no longer tests the same method.

The correct output of a failed arm is a negative or unavailable result, not an
adjacent code-hardening project.

## Non-Goals

This protocol does not:

- choose a production model;
- prove broad Prethinker QA;
- rescue query planning outside typed atom libraries;
- justify prompt/schema edits between arms;
- tune for the maximum observed score;
- revisit old contaminated scores;
- promote Gemma, Qwen, OpenRouter, or LM Studio as generally equivalent.

## Next Action After Completion

Update:

```text
docs/DOMAIN_PACK_RESEARCH_EVIDENCE.md
docs/PROVIDER_RUNTIME_DISCIPLINE_NOTE.md
PROJECT_STATE.md
```

The update should state the measured variance band and whether the SEC methods
example appears stable across the tested runtime/model arms. If the result is
negative, say so plainly and narrow the current research claim accordingly.

## Addendum - Gemma Q4 Query Control

Added before execution on 2026-06-04 after the local runtime was switched from
Gemma Q8 to Gemma Q4.

Arm D:

```text
model: google/gemma-4-12b
provider: local LM Studio
observed quantization before run: GGUF Q4_K_M
loaded context before run: 65536
temperature: 0.0
seed: local GUI set to random; harness does not request a seed
anchor: SEC transfer_003 five-row atom-library query smoke
draws: N=5
```

This is a query-control arm only. It does not replace the Q8 Gemma control and
does not test fresh compile stability. Report product exact, typed-plan replay,
redacted rejudge, prose-dependent rows, latency, and metadata completeness. If
Q4 is faster or cleaner than Q8 on this small anchor, treat that as a candidate
follow-up hypothesis, not as a promoted model migration.

Completed result:

```text
product exact: 25 / 25
typed-plan replay: 25 / 25, pass
redacted rejudge: 25 / 25, 0 prose-dependent, pass
latency: about 74-76 seconds per five-row draw
metadata: arch=gemma4, compatibility_type=gguf, quantization=Q4_K_M,
  loaded_context_length=65536
artifact:
  C:\prethinker_tmp_archive\model_variance_prereg_20260604\sec_t003_atom_query_variance_20260604\sec_t003_atom_query_armD_gemma12b_q4_temp0_N5
```

Read: cleanest query-control arm so far, but still only a tiny query-anchor
result over a Qwen-compiled typed artifact.

## Addendum - Gemma Q4 SEC Compile Substitution

Added and executed on 2026-06-04 after the query-control surface saturated.

Arm E:

```text
model: google/gemma-4-12b
provider: local LM Studio
observed quantization in artifacts: GGUF Q4_K_M
loaded context in artifacts: 65536
temperature: 0.0
top_p: 1.0
top_k: 20 requested by harness
seed: local GUI set to random; harness does not request a seed
fixture: sec_form_8k_skeleton_transfer_003
profile registry: datasets/domain_profiles/sec_form_8k_v1/ontology_registry.json
lenses: wrapper, items, exhibits, signature
draws: N=3 same-condition lens-bundle compiles
support rule: support>=2 with constant-slot matcher
```

This is the first compile-substitution control. It tests whether the SEC
transfer_003 skeleton compile result survives a model swap, not merely whether
Gemma can query over Qwen-emitted atoms.

Completed result:

```text
expected supported: 10 / 12 in two same-condition roots
forbidden supported: 0 / 10 in both roots
registered signatures: pass in both roots
atom-shape: pass in both roots
lens-scope: pass in both roots
unexpected same-signature facts: 7 in the early root, 6 in r1
metadata: arch=gemma4, compatibility_type=gguf, quantization=Q4_K_M,
  loaded_context_length=65536
artifacts:
  C:\prethinker_tmp_archive\model_variance_prereg_20260604\sec_compile_substitution_20260604\sec_compile_substitution_early_10of12_7unexpected\sec8k-t003-gemma4-q4-temp0-r1
  C:\prethinker_tmp_archive\model_variance_prereg_20260604\sec_compile_substitution_20260604\compile_substitution_sec\sec8k-t003-gemma4-q4-temp0-r1
```

Unsupported expected rows:

```text
sec_exhibit(... exhibit_104, cover_page_ixbrl, embedded_ixbrl, ...)
sec_filing_item(... item_2_02, results_of_operations_financial_condition,
  furnished, ...)
```

The emitted same-signature variants stayed registered and atom-shape clean, but
used different role/key semantics: Exhibit 104 was emitted as `filed`, Item
2.02 was emitted as `substantive`, and filing/source identifiers varied across
runs. The Qwen reference cell for the same fixture remained `12/12` support>=2
with `0/10` forbidden and one unexpected fact.

Read: Gemma Q4 did not reproduce the SEC compile cell cleanly in either
same-condition root. The SEC skeleton methods example remains a local-Qwen
result; cross-model compile robustness is not established. Because this is a
dirty Q4 compile-substitution cell, do not tune prompts or contracts inside
this protocol. A Gemma Q8 compile-substitution rerun may be a later diagnostic,
but only as a new reported arm, not a repair of this one.

## Addendum - Planned Qwen 27B Dense Same-Family Control

Added before execution on 2026-06-04 after Gemma Q4 compile substitution came
back dirty.

Arm F:

```text
model: qwen/qwen3.6-27b
provider: local LM Studio
observed metadata before run attempt: arch=qwen35, compatibility_type=gguf,
  quantization=Q4_K_M, max_context_length=262144
observed state before run attempt: not-loaded
intended loaded context: 65536 if confirmed by artifacts
temperature: 0.0
top_p: 1.0
top_k: 20 requested by harness
seed: local GUI setting only; harness does not request a seed
fixture: sec_form_8k_skeleton_transfer_003
profile registry: datasets/domain_profiles/sec_form_8k_v1/ontology_registry.json
lenses: wrapper, items, exhibits, signature
draws: N=3 same-condition lens-bundle compiles
support rule: support>=2 with constant-slot matcher
```

Reason for the arm:

```text
Gemma Q4 is dense but outside the Qwen family. Qwen 27B is dense and closer to
the current Qwen MoE reference, so it tests whether the SEC compile drift is
mostly MoE/runtime behavior, Qwen-family behavior, or broader model
sensitivity.
```

Run condition:

```text
Do not run until LM Studio reports qwen/qwen3.6-27b as loaded. If it is
unavailable or too slow, record the arm as unavailable rather than substituting
a different model.
```

Completed result:

```text
loaded metadata: arch=qwen35, compatibility_type=gguf, quantization=Q4_K_M,
  loaded_context_length=65536
expected supported: 10 / 12
forbidden supported: 0 / 10
registered signatures: pass
atom-shape: pass
lens-scope: pass
unexpected same-signature facts: 3
artifact:
  C:\prethinker_tmp_archive\model_variance_prereg_20260604\sec_compile_substitution_20260604\qwen27b_compile_substitution_sec\sec8k-t003-qwen27b-q4-temp0-r1
```

Unsupported expected rows:

```text
sec_exhibit(... exhibit_104, cover_page_ixbrl, embedded_ixbrl, ...)
sec_filing_item(... item_2_02, results_of_operations_financial_condition,
  furnished, ...)
```

The emitted same-signature variants were stable across all three runs but used
different role semantics: Exhibit 104 as `filed` and Item 2.02 as
`substantive`. Qwen 27B also emitted a repeated
`domain_omission(... 'sec_signatory/5' ... none_found ...)` while also emitting
the expected signer row, an accountability inconsistency rather than a
forbidden-fact leak.

Read: same-family dense Qwen did not recover the Qwen MoE reference cell. The
result narrows the hypothesis: the SEC transfer_003 compile substitution problem
is not only Gemma-family mismatch, and not only MoE-vs-dense routing. It is a
model/path-sensitive SEC role-semantics boundary under the current closed pack.

## Addendum - SEC Value-Axis Diagnostic

Added after Arms E/F on 2026-06-04.

The dense compile controls pointed at the same two rows, but the follow-up audit
showed that the problem is not only model choice: the SEC expected facts
themselves use mixed value axes.

Retained artifact:

```text
C:\prethinker_tmp_archive\sec_value_axis_audit_20260604
```

Result:

```text
SEC expected facts:
  checked SEC item/exhibit facts: 17
  issues: 5

SEC transfer_003 Qwen MoE artifact:
  checked SEC item/exhibit facts: 24
  issues: 10
```

Read: `sec_filing_item/5.item_role` mixes structural item role with legal
treatment (`furnished`), and `sec_exhibit/5.exhibit_role` mixes legal treatment
with content format (`embedded_ixbrl`). The right next step is schema repair
under the Qwen MoE reference path, not another model substitution arm.
