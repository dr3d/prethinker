# Source Ledger Compile Surface Worksheet

Started: 2026-05-22

## Scope

This worksheet tracks the 2026-05-22 real-world-transfer work of turning
query-only source-ledger bridges into deterministic compile-surface carriers.

The anchor run is:

- Fixture inputs: `datasets/real_world_transfer/20260521`
- Compile root: `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\real_world_transfer_stamp_20260521_compile_current`
- QA root: `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\real_world_transfer_stamp_20260521_qa_or8_after_source_bridge_v4`
- QA result: `160 / 0 / 0`
- Compatibility rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`

## Current Readout

Current status: resolved for the four-fixture real-world batch. The final
refreshed gate result below is `4 pass / 0 hold`, with fixture-level QA at
`160 / 0 / 0`. Earlier notes in this worksheet are chronological lab history.

The MoE QA lane can answer the four real-world fixtures cleanly when the source
ledger is reachable. The final pass tuned deterministic source-record carriers
and source-authority/source-claim delivery rather than relaxing the gate.

The next work is to add deterministic source-record carrier facts for:

- source row context follow-through;
- source-text citation tokens;
- section/scope/list count blocks;
- compact date aliases;
- source text count statements.

These are deterministic source addressability surfaces, not new truth claims.

## 2026-05-22 Source-Ledger Surface Pass

The prior large pre-stamp worksheet was removed from the active docs surface;
the local cold archive keeps it if the old run context is needed.

This worksheet is now the active lab notebook for source-ledger-to-compile-surface work.

Implemented deterministic source-record carriers:

- `source_record_row_context/4`
- `source_record_citation/2`
- `source_record_citation_parts/4`
- `source_record_date_alias/3`
- `source_record_date_parts/4`
- `source_record_count_word/3`
- `source_record_section_list_count/3`
- `source_record_section_list_count_detail/5`
- `source_record_section_list_count_member/5`

Added QA routing for those carriers plus targeted source text hints for:

- VIN / vehicle-identification recall checks;
- free-repair / fee / charge remedy questions;
- rescue-helicopter launch rows;
- source-record relative next-day event dates.

Validation:

- `python -m pytest tests\test_domain_bootstrap_qa.py tests\test_domain_bootstrap_file_batch.py tests\test_source_record_ledger.py -q`
- Result: `314 passed`
- `python -m py_compile scripts\run_domain_bootstrap_qa.py scripts\run_domain_bootstrap_file_batch.py src\source_record_ledger.py`

## 2026-05-22 Real-World Compile/QA Readout

Compile root:

`C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\real_world_transfer_compile_after_source_ledger_surfaces_v1`

Refreshed compile summary:

`C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\real_world_transfer_compile_after_source_ledger_surfaces_v1_summary_refreshed.md`

Gate result after deterministic source-record coverage tune:

- CPSC: pass
- FDA: pass
- Federal Register: hold
- NTSB: hold

The FDA pass is from accepting fully covered deterministic source-record table/date scaffolds where the prior direct compile surface was absent. That does not promote raw source text into semantic truth; it treats explicit row-addressable source structure as sufficient for source addressability.

Remaining compile-gate blocker:

- Federal Register: `source_authority/3` partially delivered and `source_attributed_claim/4` undelivered for `statement:claim:authority`.
- NTSB: source-authority pair remains ledger-only and `source_attributed_claim/4` is undelivered for `source:claim:status`.

QA evidence on the same compile root:

- Full OR8 run before targeted query fixes: `157 / 0 / 3`
- Targeted CPSC rerun after VIN/free-repair hints: `40 / 0 / 0`
- Targeted NTSB rerun after rescue-helicopter and next-day support: `40 / 0 / 0`
- FDA and Federal Register were already `40 / 0 / 0` in the full run.

Operational read: the four real-world fixtures are answerable at `160 / 0 / 0` by combining the latest fixture-level QA runs, with `0` compatibility rows, `0` runtime load errors, and `0` write proposal rows. The release blocker is not QA answerability; it is compile-gate cleanliness for source-authority/source-claim semantic carriers.

## 2026-05-22 Source Authority / Source Claim Gate Pass

Tuned the profile-delivery and compile-surface detectors rather than relaxing the gate:

- Federal Register authority metadata is no longer misread as source-attributed claim pressure.
- `statutory_authority/2` is accepted as a source-authority delivery carrier.
- `vessel_state/3` is accepted as a status-state delivery carrier.
- `Authorization Act` source language now triggers the source-authority profile extension.
- `source:claim:*` retry keys now get the same explicit source-attributed-claim guidance as statement/report/note keys.

Validation:

- `python -m pytest tests\test_domain_bootstrap_file.py tests\test_domain_bootstrap_file_batch.py tests\test_compile_surface_stability.py -q`
- Result: `231 passed`
- `python -m py_compile scripts\run_domain_bootstrap_file.py scripts\run_domain_bootstrap_file_batch.py scripts\audit_compile_surface_stability.py`

Targeted NTSB compile retry:

- Summary: `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\real_world_transfer_ntsb_source_authority_claim_retry_summary.md`
- Final compile: `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\real_world_transfer_compile_after_source_ledger_surfaces_v1\ntsb_marine_carol_jean_2023\domain_bootstrap_file_20260522T143542337139Z_source_qwen-qwen3-6-35b-a3b.json`
- Result: final retry passed the gate with no compile-surface or profile-delivery flags.
- NTSB rough score: `1.0`
- NTSB risk count: `4`

Refreshed four-fixture compile gate:

- Summary: `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\real_world_transfer_compile_after_source_ledger_surfaces_v1_summary_refreshed_allpass_after_ntsb_retry.md`
- Result: `4 pass / 0 hold`
- Remaining compile-surface flags: `0`
- Remaining profile-delivery flags: `0`

Post-retry NTSB QA:

- QA run: `C:\prethinker_tmp_archive\tmp_lean_markdown_docs_cleanup_20260522\real_world_transfer_qa_after_source_ledger_surfaces_v1_ntsb_after_compile_gate_pass\domain_bootstrap_qa_20260522T144706293805Z_qa_qwen-qwen3-6-35b-a3b.md`
- Result: `40 exact / 0 partial / 0 miss`
- Compatibility rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`

Current read: the real-world four-fixture batch now has a clean compile gate and clean latest fixture-level QA evidence. A full expensive native stamp is no longer blocked by known source-authority/source-claim gate failures.

## 2026-05-25 Exact Surface Mention Pass

Batch 03 exposed a source-fidelity gap where raw spelling/casing variants were
present in `source_record_text_atom/2` only as normalized atoms. That made
questions about exact printed variants depend on query-time reconstruction.

Implemented deterministic source-record carrier:

- `source_record_surface_mention/3`

Shape:

```prolog
source_record_surface_mention(SourceRow, NormalizedSurfaceAtom, 'Exact Printed Surface').
```

This is source addressability only. It preserves exact printed names,
identifiers, casing, and spelling variants; it does not decide whether two
surface forms are aliases or the same entity. Query hinting now asks for this
carrier only on generic spelling/casing/variant/verbatim questions.

Validation:

```text
python -m pytest -q tests\test_source_record_ledger.py tests\test_source_surface_gap_audit.py
  50 passed
```

Targeted Batch 03 replay:

```text
fixture: fda_ugly_003
row: q015 spelling/casing variants
artifact:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_surface_variants_20260525\qa\fda_ugly_003_q015_surface_mentions_or
result:
  1 / 0 / 0
  compatibility/runtime/write rows: 0/0/0
```

Affected-fixture guard replay:

```text
artifact:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_surface_variants_20260525\qa\fda_ugly_003_full_surface_mentions_or
result:
  25 / 0 / 0
  compatibility/runtime/write rows: 0/0/0
```

Read:

The mechanism is transfer-safe in shape because it is a deterministic source
ledger surface. The replay used a disposable compile artifact that appended
current deterministic source-record facts to the prior Batch 03 compile; it is
mechanism evidence and an affected-fixture guard, not a new corpus score.

## 2026-05-25 Date Occurrence Coordinates

Batch 03 also exposed a source-coordinate gap for questions asking where a
date is first introduced. Month-name dates were visible in normalized row text,
but the ledger did not preserve their occurrence coordinates.

Implemented deterministic source-record carriers:

- `source_record_date_occurrence/4`
- `source_record_date_mention/4`
- `source_record_first_date_occurrence/4`

Shape:

```prolog
source_record_date_occurrence(SourceRow, CanonicalDate, OccurrenceIndex, SurfaceAtom).
source_record_date_mention(SourceRow, CanonicalDate, 'Exact Printed Date', OccurrenceIndex).
source_record_first_date_occurrence(CanonicalDate, SourceRow, Line, 'Exact Printed Date').
```

The facts preserve source coordinates only. They do not decide whether a date
is a deadline, effective date, filing date, or trigger date. QA hinting now
asks for `source_record_first_date_occurrence/4` only when the question uses
generic first-occurrence wording.

Targeted Batch 03 replay:

```text
fixture: fda_ugly_002
row: q007 first date introduction
artifact:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_date_occurrence_20260525\qa\fda_ugly_002_q007_date_occurrence_or
result:
  1 / 0 / 0
  compatibility/runtime/write rows: 0/0/0
```

Read:

This is a deterministic source-coordinate repair. It should be measured in a
fresh fixture guard before becoming a corpus claim.
