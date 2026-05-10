# Probate Storage Access Register Progress Journal

Fixture id: `probate_storage_access_register`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## PSAR-000 - Fixture Admission

Date: 2026-05-10

Evidence lane: `fixture_admission`

Source admitted from: `tmp\prethinker_transfer_fixtures_unpacked\fixtures\probate_storage_access_register`

Files admitted:

- `source.md` / `story.md`
- `fixture_notes.md`
- `qa.md`
- `qa_questions.jsonl`
- `oracle.jsonl`
- `qa_battery.json`

Benchmark discipline:

- `source.md`/`story.md` is the only cold compile source.
- `oracle.jsonl`, `qa_battery.json`, `qa.md`, and `fixture_notes.md` are scoring/review assets, not compile context.
- No Python source-prose interpretation is allowed.

## PSAR-001 - OpenRouter Cold Acquisition Baseline

Date: 2026-05-10

Evidence lane: `openrouter_cold_acquisition_baseline`

Artifacts:

- Compile: `tmp/transfer_fixtures_20260510/cold_acquisition_compile_lanes6/probate_storage_access_register/domain_bootstrap_file_20260510T093021249770Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/transfer_fixtures_20260510/cold_acquisition_qa_lanes6/probate_storage_access_register/domain_bootstrap_qa_20260510T094541044260Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `34 exact / 1 partial / 5 miss` over `40`.

Compile admitted/skipped: `109 / 15`.

Lesson: authority/custody/ownership transfer is healthy on a fresh probate
packet. The helper and archival/source-record surfaces handled most possession,
title-claim, access, and pending-status rows cold. Remaining misses are likely
procedural-deferment or exact source-addressability gaps rather than a new
authority lens.

## PSAR-002 - Current Helper Cluster Replay

Date: 2026-05-10

Evidence lane: `helper_cluster_audit`

Artifacts:

- Current live replay:
  `tmp/transfer_fixtures_20260510/probate_current_live_replay_20260510/domain_bootstrap_qa_20260510T191519633683Z_qa_qwen-qwen3-6-35b-a3b.json`
- Historical orphan-helper replay:
  `tmp/transfer_fixtures_20260510/probate_storage_helper_full_replay_20260510/domain_bootstrap_qa_20260510T144725230700Z_qa_qwen-qwen3-6-35b-a3b.json`
- Cluster row gate:
  `tmp/transfer_fixtures_20260510/authority_probate_cluster_probe_20260510/probate_row_gate.md`
- Helper class audit:
  `tmp/transfer_fixtures_20260510/authority_probate_cluster_probe_20260510/probate_helper_class_audit.md`

Results:

- cold baseline: `34 / 1 / 5`
- historical `probate_storage_support` replay: `36 / 0 / 4`
- current live replay: `29 / 3 / 8`
- current helper rows: `96 candidate-helper` from
  `archive_authority_custody_support`
- row-gate across cold, orphan, and current surfaces: `40 / 0 / 0`

Lesson: probate is the clearest helper-governance warning in the transfer set.
The old `probate_storage_support` surface rescued rows, but it is not current
implemented architecture and must be treated as orphaned historical residue.
The current live helper surface is candidate-only and regresses the standalone
cold score. Do not report the historical `36 / 0 / 4` as active architecture.
The row-gated `40 / 0 / 0` is useful diagnostic evidence that the needed answer
surfaces exist somewhere in the artifact history, but the next legitimate work
is either a generic probate storage/access helper or selector discrimination
against live, audited surfaces.
