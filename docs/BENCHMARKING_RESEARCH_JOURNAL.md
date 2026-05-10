# Benchmarking Research Journal

This journal records the continuing benchmarking lane: frontier comparison,
Axis-2 probes, fixture mutation labs, local 35B factory runs, and follow-on
research decisions. It is written for two audiences:

- a documentarian reconstructing what happened day by day
- future Codex instances learning the project history without relying on chat
  memory

Fixture-specific lessons still belong in fixture `progress_journal.md` files
when a result changes how that fixture should be understood. This journal is for
cross-fixture method, benchmark instrumentation, and exploratory mutation work.

## Journaling Policy

Every meaningful benchmarking work session should leave a short entry with:

- **Date/time and operator**: who ran the work and when.
- **Intent**: what question the work was trying to answer.
- **Lane label**: sealed benchmark, mutation fixture, A/B semantic perturbation,
  lens sensitivity probe, Axis-2 assembly, dynamic KB-update turnstream, or
  platform calibration.
- **Platform**: POWER, OpenRouter, NITRO, or other named execution lane.
- **Inputs**: source fixtures, plans, recipes, prompts, model ids, and scripts.
- **Outputs**: generated artifacts, scorecards, drift summaries, and tests.
- **Finding**: what the run showed, including negative or ambiguous results.
- **Next action**: the smallest useful follow-up.

Generated JSON/JSONL/CSV artifacts can live under `tmp/public_benchmark/...`.
Durable scripts and tests live under `scripts/benchmarking/` and
`tests/benchmarking/`. Durable interpretations that outgrow this journal can be
promoted into focused docs.

## CTO Coordination Protocol

Benchmarking owns:

- scripts and tests under `scripts/benchmarking/` and `tests/benchmarking/`
- generated exploratory artifacts under `tmp/public_benchmark/`
- benchmark/mutation plans, recipes, rollups, and drift summaries
- journal entries that identify likely architecture edges

Benchmarking should not casually rewrite architecture-lane code when a finding
points at lenses, guards, helpers, selector behavior, mapper admission, runtime
mutation semantics, or domain profiles. Those findings should first be captured
as CTO handoff notes.

A handoff note should include:

- the observed row or mutation pattern
- artifact links
- why this looks architectural rather than just model variance
- the suspected component: lens, guard, helper, selector, mapper, profile, or
  runtime state update
- the smallest proposed experiment or code change
- whether benchmarking can prototype safely inside `scripts/benchmarking/`

If the fix is purely benchmark instrumentation, Codex can implement it directly
inside the benchmarking lane. If the fix changes Prethinker behavior outside
that lane, journal it and hand it to CTO unless explicitly asked to patch it.

This is not bureaucracy. It is toe protection.

## Lane Vocabulary

- **Sealed benchmark fixture**: blind or semi-blind evaluation; use for
  publication-grade score evidence.
- **Mutation fixture**: known-source research tool after sealed value is spent.
- **A/B semantic perturbation**: controlled pair where one meaning-bearing
  feature changes and the expected answer must change with it.
- **Lens sensitivity probe**: mutation aimed at a specific lens, guard, helper,
  or selector behavior.
- **Axis-2 assembly**: context recipe combining target and filler fixtures to
  measure retention under load.
- **Dynamic KB-update turnstream**: turn sequence where a query or update changes
  runtime state and later queries must observe the mutation.
- **Platform calibration**: comparing POWER, OpenRouter, NITRO, or another
  execution environment.

## 2026-05-09 - Frontier Pilot And First Axis-2 Probe

**Intent.** Establish a fair direct-frontier baseline and test whether
stuffed-context assemblies create early Axis-2 signal.

**Lane.** Frontier direct QA; Axis-2 assembly.

**Platform.** OpenRouter with `anthropic/claude-opus-4.7`,
`openai/gpt-5.5`, and `google/gemini-3.1-pro-preview`.

**Inputs.**

- 10-fixture direct frontier pilot plan.
- Target fixture for Axis 2: `contradictory_evidence_packet`.
- Stuffed fillers: `rule_activation_exception_matrix`,
  `hospital_shift_exception_log`, `authority_possession_custody_packet`,
  `count_composition_roster`.

**Outputs.**

- `scripts/benchmarking/run_frontier_direct_qa.py`
- `scripts/benchmarking/run_frontier_battery_qa.py`
- `scripts/benchmarking/score_frontier_direct_qa.py`
- `scripts/benchmarking/plan_axis2_context_probe.py`
- `scripts/benchmarking/summarize_axis2_context_probe.py`
- `tmp/public_benchmark/axis2_probe/axis2_context_probe_rollup.md`
- `tmp/public_benchmark/axis2_probe/axis2_context_probe_interpretation.md`

**Finding.** Frontier models were strong on fresh-source direct QA. The
stuffed-context probe did not show collapse at roughly 15k source tokens, but it
did show structured exactness loss: source-scope confusion, qualifier loss, and
row-specific jaggedness. Claude showed the clearest aggregate context-position
drop; GPT was aggregate-stable but jagged; Gemini had weaker baseline exactness
and many row flips.

**Next action.** Add meta-recall and larger dilution later, but shift daily
factory work to local 35B mutation probes.

## 2026-05-09 - Mutation Lab And Platform Vocabulary

**Intent.** Turn spent fixtures into ore for controlled semantic stress testing
without spending frontier-model money.

**Lane.** Mutation fixture; platform calibration.

**Platform.** POWER local 35B first; OpenRouter only for calibration; NITRO
reserved as sidecar/annex lane.

**Inputs.**

- Source fixtures: `contradictory_evidence_packet`,
  `rule_activation_exception_matrix`, `temporal_state_ledger`,
  `thornfield_variance`.
- Deterministic mutations: control, heading stripping, top-section reversal,
  question reversal, qualifier questions last.

**Outputs.**

- `scripts/benchmarking/plan_fixture_mutation_lab.py`
- `scripts/benchmarking/summarize_mutation_lab_drift.py`
- `tmp/public_benchmark/mutation_lab/fixture_mutation_lab_plan.md`
- `tmp/public_benchmark/mutation_lab/mutation_lab_drift_power_pilot.md`

**Finding.** Local POWER answer generation through
`qwen/qwen3.6-35b-a3b` worked cleanly for a 200-row one-look battery pilot.
The same local model did not work as a reliable strict judge, even with plain
JSON extraction. The factory therefore needs cheap deterministic triage first:
answer drift against control, followed by selective judge calibration.

**Next action.** Extend mutation families toward perception stress: grammar
damage, typo ranges, multilingual wrappers/headings, and date/number format
pressure.

## 2026-05-09 - Perception-Stress Direction

**Intent.** Probe the perceiving LLM rather than only the reasoning layer by
damaging the surface form while preserving source commitments.

**Lane.** Mutation fixture; lens sensitivity probe candidate.

**Platform.** POWER first.

**Planned mutation families.**

- light and heavier typo injection
- telegraphic grammar with articles/connectors removed
- multilingual section labels and question wrappers
- ISO date conversion to more international date forms
- punctuation/whitespace degradation

**Finding.** Not yet run at the time this entry was opened. The design rule is
that perception-stress mutations may reuse the original oracle only when the
meaning stays constant. If a mutation changes a source commitment, it becomes an
A/B semantic perturbation and must carry an oracle delta before scoring.

**Next action.** Implement deterministic perception-stress mutations in the
mutation lab planner, regenerate the plan, and run a small POWER pilot.

## 2026-05-09 - First Perception-Stress POWER Pilot

**Intent.** Start using old fixture ore to probe surface perception: grammar,
typos, multilingual labels, date formatting, punctuation, and question wrapper
effects.

**Lane.** Mutation fixture; perception-surface mangle.

**Platform.** POWER, LM Studio, `qwen/qwen3.6-35b-a3b`.

**Inputs.**

- Plan: `tmp/public_benchmark/mutation_lab/fixture_mutation_lab_plan.md`
- Source family run in this pilot: `contradictory_evidence_packet`
- Variants: control plus 12 mutations:
  `strip_headings`, `reverse_top_sections`, `punctuation_flattened`,
  `typo_light_source`, `typo_heavy_source`, `telegraphic_grammar_source`,
  `multilingual_headings`, `international_dates`, `reverse_questions`,
  `qualifier_questions_last`, `question_wrapper_es`,
  `question_wrapper_fr_de`.

**Outputs.**

- Raw local battery answers:
  `tmp/public_benchmark/mutation_lab/perception_power_pilot/frontier_battery_qa_qwen-qwen3.6-35b-a3b.jsonl`
- Drift summary:
  `tmp/public_benchmark/mutation_lab/perception_power_pilot_drift.md`
- CSV:
  `tmp/public_benchmark/mutation_lab/perception_power_pilot_drift.csv`

**Finding.**

The run produced `520` answers with zero missing rows. The drift summarizer
compared `480` non-control rows against the control answers:

- drift rows: `68 / 480`
- mean token-F1 similarity: `0.9176`
- largest mutation-level drift count: `international_dates`, `11 / 40`
- next highest: `reverse_top_sections`, `typo_light_source`,
  `multilingual_headings`, each `7 / 40`

This is not an accuracy score. Several largest drift rows are answer-shape
changes such as terse `No` versus qualified `No`. The useful finding is that
the local model's answer surface is sensitive to perception mangles, and
international date formatting is the first standout pressure point.

**CTO handoff status.**

No architecture patch requested yet. This is a benchmarking triage result. If
date-format drift survives selective judging, likely component candidates are:

- temporal normalization / temporal lens
- source-record date addressability
- answer normalization for semantically equivalent date forms

Benchmarking can continue probing inside `scripts/benchmarking/` before asking
CTO to alter architecture-lane behavior.

**Next action.**

Run selective judging or manual review on the `international_dates` drift rows,
then add a dynamic KB-update turnstream fixture to test update retention rather
than source perception.

## 2026-05-09 - CTO Ack On Date-Format Drift

**Intent.** Record architecture-lane response to the first benchmarking handoff.

**Lane.** CTO coordination; mutation fixture triage.

**Platform.** File handoff under `tmp/public_benchmark/mutation_lab/`.

**Inputs.**

- Benchmarking handoff:
  `tmp/public_benchmark/mutation_lab/cto_handoff_20260509_perception_date_format.md`
- CTO ack:
  `tmp/public_benchmark/mutation_lab/cto_ack_20260509_perception_date_format.md`

**CTO read.**

Accepted as benchmarking-lane triage, not an architecture patch request.
Token-F1 drift is a perception signal, not proof of correctness loss. No
compiler, lens, helper, or architecture change should happen until drift rows
are selectively judged or manually reviewed.

**CTO recommended next step.**

Review `international_dates` drift rows first, but include repeated `q025` and
`q030` cross-mutation drifts as controls. If the same row drifts under many
unrelated mutations, the issue may be answer-normalization or scorer sensitivity
rather than date parsing.

Suggested triage labels:

- harmless answer-shape drift
- semantically equivalent date formatting
- source retrieval focus change
- true correctness loss
- scorer normalization defect

**Architecture boundary.**

No architecture patch. If true correctness loss is later confirmed, likely
architecture-side target is date/address normalization or answer normalization
around temporal/source-record evidence, not necessarily a new lens.

**Next action.**

Build a selective triage table for `international_dates` drift rows plus q025
and q030 cross-mutation controls.

## 2026-05-09 - Date Mangle Correction And V2 Rerun

**Intent.** Correct the `international_dates` perception mangle after CTO's
control-row advice exposed that the mutator was changing identifier strings,
not just date surface forms.

**Lane.** Mutation fixture; benchmarking instrumentation fix.

**Platform.** POWER, LM Studio, `qwen/qwen3.6-35b-a3b`.

**Issue.**

The first `international_dates` mutation rewrote ISO-looking substrings inside
identifiers. Example:

```text
BAS-MAINT-2026-04-28-003
-> BAS-MAINT-28 Apr 2026-003
```

That is not an oracle-preserving perception mangle. It changes the identifier,
so rows like `q012` were contaminated by the mutation itself.

**Fix.**

Updated `scripts/benchmarking/plan_fixture_mutation_lab.py` so
`_international_dates` rewrites only standalone dates, leaving dates embedded in
alphanumeric/hyphenated identifiers unchanged. Added a regression test in
`tests/benchmarking/test_fixture_mutation_lab.py`.

**Outputs.**

- Corrected raw run:
  `tmp/public_benchmark/mutation_lab/perception_power_pilot_v2/frontier_battery_qa_qwen-qwen3.6-35b-a3b.jsonl`
- Corrected drift summary:
  `tmp/public_benchmark/mutation_lab/perception_power_pilot_v2_drift.md`
- Corrected triage table:
  `tmp/public_benchmark/mutation_lab/perception_power_pilot_v2_triage.md`

**Finding.**

The corrected v2 run produced `520` answers with zero missing rows. Drift
changed materially:

- v1 drift rows: `68 / 480`, mean similarity `0.9176`
- v2 drift rows: `48 / 480`, mean similarity `0.9333`
- v1 `international_dates`: `11 / 40` drift rows, mean similarity `0.8480`
- v2 `international_dates`: `6 / 40` drift rows, mean similarity `0.8966`

The reduction confirms that part of the first signal was mutator-induced, not
model-induced.

**CTO handoff status.**

No architecture request. The correct lesson is methodological: perception
mangles must preserve identifiers unless the lane is explicitly an A/B semantic
perturbation with an oracle delta.

**Next action.**

Use v2 artifacts for future review. Treat v1 as contaminated for
identifier-embedded date rows.

## 2026-05-09 - V2 Perception Drift Manual Review

**Intent.** Follow CTO's ack by reviewing the corrected v2
`international_dates` rows plus q025/q030 cross-mutation controls before
requesting any architecture work.

**Lane.** Mutation fixture; benchmarking instrumentation fix.

**Platform.** POWER output reviewed manually, no additional model calls.

**Inputs.**

- `tmp/public_benchmark/mutation_lab/perception_power_pilot_v2_drift.md`
- `tmp/public_benchmark/mutation_lab/perception_power_pilot_v2_triage.md`
- Fixture oracle for `contradictory_evidence_packet`
- CTO ack labels from
  `tmp/public_benchmark/mutation_lab/cto_ack_20260509_perception_date_format.md`

**Outputs.**

- `tmp/public_benchmark/mutation_lab/perception_power_pilot_v2_triage_review.md`
- Updated `scripts/benchmarking/extract_mutation_drift_triage.py` so triage
  tables include the oracle `reference_answer`, not only control and mutated
  answers.

**Finding.**

The corrected date-format signal is mostly normalization noise. The obvious
date rows are semantically equivalent, and the q025/q030 controls show a
repeatable scoring-instrument issue: token-F1 drift flags terse `No` controls
versus longer oracle-like denials as if they were regressions.

One row, `q029`, remains useful. The model shifts from a phone-tower
transaction-gap reading toward the nearby "no Pemberton pings" source sentence.
That is a source-retrieval focus change, not clear evidence of a date-parser
failure. No architecture request was opened.

**Next action.**

Run the perception-stress pilot over `rule_activation_exception_matrix` and
`temporal_state_ledger` on POWER to see whether this is a general
answer-normalization pattern or whether other fixtures expose real source-focus
losses.

## 2026-05-09 - Rule/Temporal Perception POWER Pass

**Intent.** Extend the perception-stress factory beyond
`contradictory_evidence_packet` to see whether date, grammar, wrapper, and
layout mangles create stable patterns across rule and temporal fixtures.

**Lane.** Mutation fixture; perception-surface mangle; lens sensitivity probe
candidate.

**Platform.** POWER, LM Studio, `qwen/qwen3.6-35b-a3b`.

**Inputs.**

- `rule_activation_exception_matrix`
- `temporal_state_ledger`
- 13 mutation variants per fixture: control plus the 12 current
  perception/layout/question-order mangles.

**Outputs.**

- Raw battery answers:
  `tmp/public_benchmark/mutation_lab/perception_power_pilot_rule_temporal/frontier_battery_qa_qwen-qwen3.6-35b-a3b.jsonl`
- Drift summary:
  `tmp/public_benchmark/mutation_lab/perception_power_pilot_rule_temporal_drift.md`
- Triage table:
  `tmp/public_benchmark/mutation_lab/perception_power_pilot_rule_temporal_triage.md`
- Interpretation:
  `tmp/public_benchmark/mutation_lab/perception_power_pilot_rule_temporal_interpretation.md`
- CTO handoff:
  `tmp/public_benchmark/mutation_lab/cto_handoff_20260509_rule_temporal_edges.md`

**Instrumentation fixes.**

- `run_frontier_battery_qa.py` now accepts repeatable `--fixture` filters, so
  factory runs can target named synthetic fixtures without throwaway plans.
- `summarize_mutation_lab_drift.py` now includes fixture-level rollups.
- The drift metric now normalizes common English number words through twenty,
  so `13` versus `Thirteen` is not treated as zero-overlap drift.
- `largest_drifts` sorting now handles `0.0` similarity correctly.
- `extract_mutation_drift_triage.py` now includes fixture name and oracle
  reference answer in markdown tables.

**Finding.**

The run produced `26` battery calls and `1040` row answers with no missing
answers. After number-word normalization:

- Compared non-control rows: `960`
- Drift rows: `177`
- Mean similarity: `0.8980`
- `rule_activation_exception_matrix`: `167 / 480` drift rows, mean `0.8156`
- `temporal_state_ledger`: `10 / 480` drift rows, mean `0.9805`

Most `rule_activation_exception_matrix` drift is answer-shape noise: terse
controls versus rule-cited mutated answers. Two useful candidate edges remain:

- `rule_activation_exception_matrix` `q040`: absence of relocation should be
  negative evidence for ineligibility, but some mangles turn it into unresolved
  status.
- `temporal_state_ledger` `q014`: date-format mutation shifts the answer from
  logged satisfaction time to underlying threshold time.

**Next action.**

Convert these into explicit A/B semantic probes: one for
absence-as-negative-evidence versus absence-as-unresolved, and one for competing
temporal milestones in a single event chain.

## 2026-05-09 - CTO Ack And Probe Label Adoption

**Intent.** Process Architecture's ack of the rule/temporal handoff and turn it
into benchmark-lane next work.

**Lane.** CTO coordination; A/B semantic perturbation design.

**Platform.** File mailbox under `tmp/public_benchmark/mutation_lab/`.

**Inputs.**

- `tmp/public_benchmark/mutation_lab/cto_ack_20260509_rule_temporal_edges.md`
- `tmp/public_benchmark/mutation_lab/cto_note_20260509_mailbox_protocol.md`
- `tmp/public_benchmark/mutation_lab/MAILBOX_PROTOCOL.md`

**Outputs.**

- `tmp/public_benchmark/mutation_lab/semantic_probe_design_20260509.md`

**Finding.**

Architecture accepted the two candidate edge patterns as useful
architecture-adjacent semantics, but still not patch requests. The durable probe
labels are:

- `absence_negative_evidence_vs_unresolved`
- `condition_time_vs_certification_time`

The mailbox protocol is now explicit: benchmark handoffs use
`cto_handoff_YYYYMMDD_topic.md`, architecture acks use
`cto_ack_YYYYMMDD_topic.md`, and distilled lessons move to docs only after the
evidence stabilizes.

**Next action.**

Build small synthetic probe fixtures for the two labels under the mutation lab:
8-12 questions per variant, POWER first, then optional OpenRouter calibration
once the oracle deltas are stable.

## 2026-05-09 - First Semantic A/B Probe POWER Pilot

**Intent.** Make the CTO-accepted edge labels runnable as explicit A/B probes
instead of leaving them as notes from mutation drift.

**Lane.** A/B semantic perturbation; platform calibration.

**Platform.** POWER, LM Studio, `qwen/qwen3.6-35b-a3b`.

**Inputs.**

- Probe labels:
  `absence_negative_evidence_vs_unresolved`,
  `condition_time_vs_certification_time`
- Planner:
  `scripts/benchmarking/plan_semantic_ab_probes.py`

**Outputs.**

- Probe plan:
  `tmp/public_benchmark/mutation_lab/semantic_probes/semantic_ab_probe_plan.md`
- Raw POWER pilot:
  `tmp/public_benchmark/mutation_lab/semantic_probes/power_pilot_v2/frontier_battery_qa_qwen-qwen3.6-35b-a3b.jsonl`
- Interpretation:
  `tmp/public_benchmark/mutation_lab/semantic_probes/power_pilot_v2_interpretation.md`

**Finding.**

The planner created `4` synthetic fixtures, `32` total rows. The first POWER
run exposed one ambiguous absence-probe question about whether the applicant
could supplement the record; the source actually described later Records Office
confirmation. The question was corrected and the probe regenerated.

In the v2 run, local 35B preserved both distinctions:

- pending missing relocation file stayed pending/unresolved
- final missing relocation documentation became disqualifying
- condition-clock variant used `2026-05-01 17:00`
- certification-clock variant used `2026-05-01 17:30`

This means the labels are calibrated probe fixtures, not yet demonstrated model
failures. They are ready for selective Prethinker/frontier comparison or for
harder follow-on perturbations.

**Next action.**

Add longer/noisier variants later, or run this small pack through the
compile-once Prethinker path once the benchmarking lane has a clean harness for
that comparison.

## 2026-05-09 - Semantic A/B Probe Summary Check

**Intent.** Add a cheap sanity checker for the first semantic A/B probe pack so
the POWER pilot has an explicit distinction-pass summary, not only a manual
read.

**Lane.** A/B semantic perturbation; benchmarking instrumentation.

**Platform.** POWER output, deterministic local summary.

**Inputs.**

- `tmp/public_benchmark/mutation_lab/semantic_probes/power_pilot_v2/frontier_battery_qa_qwen-qwen3.6-35b-a3b.jsonl`

**Outputs.**

- `scripts/benchmarking/summarize_semantic_ab_probe_pilot.py`
- `tests/benchmarking/test_summarize_semantic_ab_probe_pilot.py`
- `tmp/public_benchmark/mutation_lab/semantic_probes/power_pilot_v2_summary.md`

**Finding.**

The summary checker evaluated the core distinction rows:

- checked rows: `14`
- passed rows: `14`
- failed rows: `0`

This supports the manual v2 read: the explicit A/B probes are calibrated and
the local 35B model preserves the two initial distinctions when they are stated
cleanly.

**Next action.**

Use the summary checker as a gate before adding harder probe variants. The next
useful probe work is adding mild distractor records and less direct wording
without changing the oracle.

## 2026-05-09 - Semantic A/B Probe Distractor Layer

**Intent.** Add mild irrelevant-record pressure to the calibrated A/B semantic
probes without changing their oracle commitments.

**Lane.** A/B semantic perturbation; platform calibration.

**Platform.** POWER, LM Studio, `qwen/qwen3.6-35b-a3b`.

**Inputs.**

- `scripts/benchmarking/plan_semantic_ab_probes.py`
- Probe labels:
  `absence_negative_evidence_vs_unresolved`,
  `condition_time_vs_certification_time`

**Outputs.**

- Updated probe plan:
  `tmp/public_benchmark/mutation_lab/semantic_probes/semantic_ab_probe_plan.md`
- Raw POWER run:
  `tmp/public_benchmark/mutation_lab/semantic_probes/power_pilot_distractor/frontier_battery_qa_qwen-qwen3.6-35b-a3b.jsonl`
- Summary:
  `tmp/public_benchmark/mutation_lab/semantic_probes/power_pilot_distractor_summary.md`
- Interpretation:
  `tmp/public_benchmark/mutation_lab/semantic_probes/power_pilot_distractor_interpretation.md`

**Finding.**

The plan now has `8` fixtures and `64` rows. The added variants include:

- an unrelated approved relocation applicant as a distractor in the absence
  probe
- an unrelated drill timeline with nearby times in the milestone probe

POWER preserved the distinctions across the base and distractor variants:

- checked rows: `28`
- passed rows: `28`
- failed rows: `0`

This is useful calibration but not a failure. The first distractor layer is too
easy for the local 35B model.

**Next action.**

Build a harder second layer for one probe only, likely
`absence_negative_evidence_vs_unresolved`, using near-collision applicant names,
same-rule opposite outcomes, and question order that places the tempting wrong
case immediately before the target.

## 2026-05-09 - Semantic A/B Probe Hard Absence Layer

**Intent.** Push the absence probe past obvious distractors by adding
near-collision applicant names, same-rule opposite outcomes, a wrong-file
correction, and question order pressure.

**Lane.** A/B semantic perturbation; platform calibration.

**Platform.** POWER, LM Studio, `qwen/qwen3.6-35b-a3b`.

**Inputs.**

- Updated `scripts/benchmarking/plan_semantic_ab_probes.py`
- Hard absence variants:
  `unresolved_absence_hard`, `negative_absence_hard`

**Outputs.**

- Updated plan:
  `tmp/public_benchmark/mutation_lab/semantic_probes/semantic_ab_probe_plan.md`
- Raw POWER run:
  `tmp/public_benchmark/mutation_lab/semantic_probes/power_pilot_hard/frontier_battery_qa_qwen-qwen3.6-35b-a3b.jsonl`
- Summary:
  `tmp/public_benchmark/mutation_lab/semantic_probes/power_pilot_hard_summary.md`
- Interpretation:
  `tmp/public_benchmark/mutation_lab/semantic_probes/power_pilot_hard_interpretation.md`

**Finding.**

The plan now has `10` fixtures and `82` rows. The hard absence variants add:

- `North Pier Glass` as target
- `North Pier Glazing` as an approved same-rule near-collision applicant
- `North Pine Glass` as a wrong-file correction distractor
- `q000` about the approved near-collision applicant immediately before `q001`
  about the target

POWER still preserved the distinctions:

- checked rows: `36`
- passed rows: `36`
- failed rows: `0`

This is still calibration, not a demonstrated failure. The local 35B handles
explicit near-collision pressure when the source is short and clean.

**Next action.**

Create an Axis-2 style assembly around the hard absence probe: target plus
filler fixtures, same 9-question battery. That tests retention under load
rather than short-source comprehension.

## 2026-05-09 - Semantic Axis-2 Hard Absence POWER Pilot

**Intent.** Test whether the hard absence distinction survives context load,
not just short-source comprehension.

**Lane.** Axis-2 assembly; A/B semantic perturbation; platform calibration.

**Platform.** POWER, LM Studio, `qwen/qwen3.6-35b-a3b`.

**Inputs.**

- `scripts/benchmarking/plan_semantic_axis2_probe.py`
- Hard absence semantic variants:
  `unresolved_absence_hard`, `negative_absence_hard`
- Fillers:
  `rule_activation_exception_matrix`, `temporal_state_ledger`,
  `contradictory_evidence_packet`, `count_composition_roster`

**Outputs.**

- Axis-2 plan:
  `tmp/public_benchmark/mutation_lab/semantic_probes/axis2_hard_absence/semantic_axis2_probe_plan.md`
- Raw POWER output:
  `tmp/public_benchmark/mutation_lab/semantic_probes/axis2_hard_absence/power_pilot/frontier_battery_qa_qwen-qwen3.6-35b-a3b.jsonl`
- Retry output:
  `tmp/public_benchmark/mutation_lab/semantic_probes/axis2_hard_absence/power_pilot_retry_unresolved_first/frontier_battery_qa_qwen-qwen3.6-35b-a3b.jsonl`
- Interpretation:
  `tmp/public_benchmark/mutation_lab/semantic_probes/axis2_hard_absence/power_pilot_interpretation.md`

**Finding.**

The first run produced `8` calls and `72` rows, but one call
(`unresolved_absence_hard__axis2_first`) returned no parseable JSON. Rerunning
that condition by itself produced answers.

After retry, the remaining meaningful failure is `q003`: the model preserved
the pending/unresolved status but answered using the near-collision applicant
`North Pine Glass` instead of target applicant `North Pier Glass`.

This is not an absence-vs-unresolved collapse. It is an entity/addressability
failure under assembly load and near-collision pressure. Because it appeared in
one retry condition, it needs replication before a CTO handoff.

**Instrumentation fix.**

`summarize_semantic_ab_probe_pilot.py` now checks `q003` for near-collision
entity confusion and accepts `denied` as a valid disqualifying negative-absence
answer.

**Next action.**

Run `unresolved_absence_hard__axis2_first` for three POWER repetitions. If the
entity/addressability drift repeats, create a CTO handoff as an
entity-addressability probe candidate.

## 2026-05-09 - Axis-2 Entity Addressability Replication

**Intent.** Replicate the single meaningful Axis-2 hard absence failure before
deciding whether it deserves CTO attention.

**Lane.** Axis-2 assembly; lens sensitivity probe candidate; CTO coordination.

**Platform.** POWER, LM Studio, `qwen/qwen3.6-35b-a3b`.

**Inputs.**

- Target fixture:
  `absence_negative_evidence_vs_unresolved__unresolved_absence_hard__axis2_first`
- Three POWER repetitions using
  `scripts/benchmarking/run_frontier_battery_qa.py`

**Outputs.**

- Raw replication output:
  `tmp/public_benchmark/mutation_lab/semantic_probes/axis2_hard_absence/power_replicate_unresolved_first/frontier_battery_qa_qwen-qwen3.6-35b-a3b.jsonl`
- Summary:
  `tmp/public_benchmark/mutation_lab/semantic_probes/axis2_hard_absence/power_replicate_unresolved_first_summary.md`
- CTO handoff:
  `tmp/public_benchmark/mutation_lab/cto_handoff_20260509_axis2_entity_addressability.md`

**Finding.**

The entity/addressability failure replicated in `3 / 3` POWER runs. For `q003`,
the question asks:

```text
Does the packet establish a prior-county operating date for North Pier Glass?
```

All three runs answered with `North Pine Glass`, a near-collision distractor:

```text
No, the packet states North Pine Glass has no confirmed relocation file and the case remains pending.
```

This is not an absence-vs-unresolved collapse. The model kept the broad
pending/no-file status but attached it to the wrong entity. The candidate label
sent to CTO is `near_collision_entity_addressability_under_load`.

**Next action.**

Wait for CTO classification. Benchmarking can continue by testing whether this
same probe fails on target-middle/target-last with more repetitions or by
running one hosted calibration model.

## 2026-05-09 - Axis-2 Entity Addressability Position Check

**Intent.** Determine whether the replicated `q003` near-collision entity
failure was isolated to target-first assembly or tied to target position under
context load.

**Lane.** Axis-2 assembly; lens sensitivity probe candidate; CTO coordination.

**Platform.** POWER, LM Studio, `qwen/qwen3.6-35b-a3b`.

**Inputs.**

- `unresolved_absence_hard__axis2_standalone`
- `unresolved_absence_hard__axis2_middle`
- `unresolved_absence_hard__axis2_last`
- Three POWER repetitions per condition.

**Outputs.**

- Raw output:
  `tmp/public_benchmark/mutation_lab/semantic_probes/axis2_hard_absence/power_replicate_unresolved_other_positions/frontier_battery_qa_qwen-qwen3.6-35b-a3b.jsonl`
- Summary:
  `tmp/public_benchmark/mutation_lab/semantic_probes/axis2_hard_absence/power_replicate_unresolved_other_positions_summary.md`
- Interpretation:
  `tmp/public_benchmark/mutation_lab/semantic_probes/axis2_hard_absence/power_replicate_position_interpretation.md`
- CTO reply:
  `tmp/public_benchmark/mutation_lab/cto_reply_20260509_axis2_entity_addressability.md`

**Finding.**

The failure is position-sensitive:

- standalone: `0 / 3` q003 entity drifts
- stuffed first: `3 / 3` q003 entity drifts
- stuffed middle: `3 / 3` q003 entity drifts
- stuffed last: `0 / 3` q003 entity drifts

The model preserves the broad pending/no-file status but answers with the
near-collision distractor `North Pine Glass` instead of target `North Pier
Glass` when the target source must survive later filler context.

**Next action.**

Wait for CTO classification. This is now strong enough to include as a
candidate meaning-depth resolution finding under
`near_collision_entity_addressability_under_load`.

## 2026-05-09 - Meaning-Depth Signal Map Draft

**Intent.** Distill the current probe evidence into a compact research map
without promoting it to publication prose too early.

**Lane.** Meaning-depth resolution synthesis; mutation-lab interpretation.

**Platform.** No model calls; synthesis from POWER artifacts.

**Inputs.**

- `tmp/public_benchmark/mutation_lab/semantic_probes/axis2_hard_absence/power_replicate_unresolved_first_summary.md`
- `tmp/public_benchmark/mutation_lab/semantic_probes/axis2_hard_absence/power_replicate_unresolved_other_positions_summary.md`
- `tmp/public_benchmark/mutation_lab/semantic_probes/axis2_hard_absence/power_replicate_position_interpretation.md`

**Outputs.**

- `tmp/public_benchmark/mutation_lab/meaning_depth_signal_map_20260509.md`

**Finding.**

The current strongest signal is
`near_collision_entity_addressability_under_load`: the local 35B model
preserves the right broad semantic status but binds it to the wrong
near-collision applicant when the target appears before later filler context.

This supports the meaning-depth resolution frame: the failure is not simply
"does not understand the rule." It is a finer failure to preserve which entity a
structural status belongs to under load.

**Next action.**

Wait for CTO classification and avoid turning this into publication prose until
there is hosted/frontier or Prethinker comparison evidence.

## 2026-05-09 - CTO Ack On Entity Addressability

**Intent.** Record Architecture's classification of the replicated Axis-2
entity-addressability probe.

**Lane.** CTO coordination; meaning-depth resolution synthesis.

**Platform.** File mailbox under `tmp/public_benchmark/mutation_lab/`.

**Inputs.**

- `tmp/public_benchmark/mutation_lab/cto_ack_20260509_axis2_entity_addressability.md`
- `tmp/public_benchmark/mutation_lab/meaning_depth_signal_map_20260509.md`

**Finding.**

CTO accepted the label `near_collision_entity_addressability_under_load` as
architecture-adjacent probe evidence. No Prethinker architecture patch is
requested or taken.

Architecture classification: this maps to deterministic source addressability
and entity identity preservation, not to epistemic-state machinery. Relevant
future architecture surfaces include near-name entity separation, query target
binding under context load, source-addressed entity ledgers, and assembly-order
sensitivity.

**Next action.**

Benchmarking keeps owning the probe. Only ask Architecture to evaluate helpers
or ledger checks if the pattern appears in Prethinker rows or a
publication-relevant comparison. The signal map was updated with the accepted
classification.
