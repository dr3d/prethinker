# Festival Permit Maze Progress Journal

Fixture id: `festival_permit_maze`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## FPM-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming/festival_permit_maze.zip`

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

## FPM-001 - First Full-40 Cold Baseline

Date: 2026-05-07

Evidence lane: `cold_unseen`

Score: `18 exact / 8 partial / 14 miss`

Artifacts:

- Compile: `tmp/incoming_10_cold_runs_20260507/festival_permit_maze`
- QA: `tmp/incoming_10_cold_qa_20260507/festival_permit_maze`

Boundary: `0` write proposals and `0` runtime load errors. This is an immediate repair frontier fixture.

## FPM-002 - Permit Lifecycle Candidate

Date: 2026-05-07

Evidence lane: `candidate_compile_mode`

Candidate context: `operational_record_status_strategy_v1` with
permit/license lifecycle emphasis.

Targeted non-exact replay: `10 exact / 4 partial / 8 miss` across the `22`
baseline non-exact rows. The candidate improved `11` rows, including festival
director identity, renewed food-license expiry, sound suspension trigger and
duration, alcohol restriction reason and appeal/hearing status, authority
limits, and Holt/Burr meeting statements. It regressed one targeted partial row
about the unrenewed food-license expiry rule.

Full guardrail replay: `25 exact / 6 partial / 9 miss` across all `40` rows,
up from the baseline `18 / 8 / 14`. It improved `11` rows and regressed `4`
rows, mostly ground-use extension/public-event details and one aggregate active
permit count.

Artifacts:

- Candidate compile: `tmp/incoming_10_repair_festival_context_v1`
- Targeted QA: `tmp/incoming_10_repair_festival_context_v1_qa_nonexact`
- Full guardrail QA: `tmp/incoming_10_repair_festival_context_v1_qa_full`

Decision: strong candidate mode, not a blind global default. The lifecycle
surface earns a selector/row-gated follow-up because it captures authority,
appeal, suspension, and meeting-statement atoms that the cold compile dropped,
but it thins a few extension/status aggregate rows.

Selector follow-up:

- Structural selector:
  `tmp/incoming_10_candidate_mode_selectors/festival_structural_selector.md`
  selected `20 exact / 7 partial / 13 miss` against a perfect available upper
  bound of `28 / 5 / 7`.
- Guarded activation selector:
  `tmp/incoming_10_candidate_mode_selectors/festival_guarded_selector.md`
  selected `26 exact / 4 partial / 10 miss`, with `36/40` selected-best rows.

Decision update: guarded selection protects most of the candidate lift, but the
remaining misses on `q005`, `q006`, `q013`, and `q020` show the selector still
needs permit-extension and rule-expiry guards before this becomes a dependable
row-gated lane.

## FPM-004 - Extension/Expiry Selector Guards

Date: 2026-05-07

Evidence lane: `candidate_mode_selector`

Guard additions: public-use extension, unrenewed-expiry endpoint, explicit
violation-record suspension trigger, and approved-fireworks count surfaces.

Full selector replay:
`tmp/incoming_10_candidate_mode_selectors/festival_guarded_selector_v2.md`

Result: `28 exact / 5 partial / 7 miss`, matching the perfect available upper
bound from the baseline plus permit-lifecycle candidate modes. The selector
chose the best available mode on all `40/40` rows with `0` selector errors.

Lesson: row-gated candidate modes are working here when the guard is about the
question's semantic surface, not the fixture. The durable guards are not
"Festival" guards; they distinguish extension-purpose questions from broad
lifecycle volume, unrenewed original expiry from renewed validity rows,
suspension trigger provenance from generic suspension intervals, and approved
display counts from current-status summaries.

## FPM-005 - Baseline/Lifecycle Union Selector Lane

Date: 2026-05-07

Evidence lane: `deterministic_compile_union` plus `candidate_mode_selector`

Union compile:
`tmp/incoming_10_repair_festival_union_v1/domain_bootstrap_file_20260507T191245276285Z_festival-baseline-plus-lifecycle_qwen-qwen3-6-35b-a3b.json`

Policy: no source prose was read and no new facts were inferred. The union
deduplicated mapper-admitted clauses from the cold baseline and the permit
lifecycle candidate.

Full union replay:
`tmp/incoming_10_repair_festival_union_v1_qa_full/domain_bootstrap_qa_20260507T192923257401Z_qa_qwen-qwen3-6-35b-a3b.json`

Union alone scored `25 exact / 8 partial / 7 miss`, so it is not a global
default. It did, however, recover row-specific support for the ground-use valid
period, the October 15 failed-vendor count, failed-vendor rationale, the October
12 fireworks outcome, and the second sound-violation duration.

Three-mode selector replay:
`tmp/incoming_10_candidate_mode_selectors/festival_union_guarded_selector_v1.md`

Result: `30 exact / 6 partial / 4 miss`, matching the perfect available upper
bound across baseline, lifecycle candidate, and union modes. The selector chose
the best available mode on all `40/40` rows with `0` selector errors.

Guard additions: valid-period extension, failed-reinspection aggregate count,
failed-vendor rationale bundle, display-outcome bundle, second-violation
duration bundle, appeal-hearing status, and unrestricted-active baseline
protection.

Lesson: deterministic compile unions are useful as a bounded candidate mode
when two honest partial compiles carry complementary surfaces. They must not be
promoted as a blind default, because the same union that rescues valid-period
and failed-count rows also regresses some active-status reasoning. The durable
pattern is "union creates an evidence pool; row guards decide when its combined
surface is semantically appropriate."

## FPM-006 - Permit Rule/Time Candidate

Date: 2026-05-07

Evidence lane: `candidate_compile_mode` plus `candidate_mode_selector`

Harness/context change: expanded `operational_record_status_strategy_v1` with
permit-terms, clock-delta, event-outcome, and itemized-failure guidance. These
are operational-record surfaces, not fixture-specific facts.

Candidate compile:
`tmp/incoming_10_repair_festival_rule_time_v1/domain_bootstrap_file_20260507T222434774769Z_source_qwen-qwen3-6-35b-a3b.json`

Compile result: `127` admitted facts, `0` skipped facts/rules, rough profile
score `1.0`.

Targeted weak-row replay:
`tmp/incoming_10_repair_festival_rule_time_v1_qa_targeted/domain_bootstrap_qa_20260507T222739586445Z_qa_qwen-qwen3-6-35b-a3b.json`

Targeted result: `5 exact / 2 partial / 3 miss` over 10 probed rows. The
candidate recovered unrenewed food-license expiry, itemized failed vendors and
deficiencies, default amplified-sound hours, October 12 fireworks outcome, and
the complete suspended/restricted/pending-action list.

Full candidate replay:
`tmp/incoming_10_repair_festival_rule_time_v1_qa_full/domain_bootstrap_qa_20260507T223513323952Z_qa_qwen-qwen3-6-35b-a3b.json`

Candidate score: `32 exact / 3 partial / 5 miss`.

Four-mode selector replay:
`tmp/incoming_10_candidate_mode_selectors/festival_rule_time_guarded_selector_v2.md`

Result: `35 exact / 2 partial / 3 miss`, matching the perfect available upper
bound across baseline, lifecycle, union, and rule-time modes. The selector
chose the best available mode on all `40/40` rows with `0` selector errors.

Guard additions: festival-director identity protects direct person-role rows;
unrenewed expiry prefers deadline/requirement plus validity; failed-vendor
rationale prefers itemized vendor-deficiency support; permitted-hours questions
prefer operational-hours rule rows; display-outcome questions prefer
inspection/outcome plus status; permit-action lists prefer suspension,
restriction, status, and deadline surfaces together.

Lesson: permit type descriptions are not decorative metadata. They carry rule
terms: default hours, renewal windows, extension requirements, exemption
deadlines, inspection windows, suspension durations, appeal periods, and
violation overage clocks. Lifecycle/status lenses capture what happened; the
rule/time lens captures what the permit terms said and how clocked violations
should be measured.
