# The Avalon Grant Committee

This fixture is a grant-eligibility, committee-governance, and rule-composition
frontier project for Prethinker.

It combines eligibility rules, fiscal-year windows, grant waiting periods,
formal interpretations, committee quorum, conflict-of-interest recusals,
temporary replacement authority, conditional approvals, corrections, appeals,
counterfactuals, and unresolved rule questions.

## Files

- `story.md`: source document to compile.
- `source.md`: preserved copy of the source under the generic source name.
- `qa_battery_40.json`: original supplied 40-question QA battery.
- `qa.md`: script-compatible numbered QA file for post-ingestion QA.
- `progress_journal.md`: running mini-journal of benchmark attempts and lessons.
- `progress_metrics.jsonl`: append-only metrics rows for progress graphs.

## Evidence-Lane Discipline

This fixture intentionally has no `gold_kb.pl`, no `ontology_registry.json`, no
`intake_plan.md`, and no `failure_buckets.json` at admission time. Do not add a
starter profile or reference KB unless a later experiment explicitly creates a
separate assisted lane and labels it as such.

Cold runs should use only `story.md` as the source document. `qa.md` and
`qa_battery_40.json` exist for post-ingestion scoring, not source-compilation
context.

No benchmark run has been recorded yet.

## Why It Matters

The fixture pressures:

- executable rule composition across eligibility, exceptions, formal
  interpretations, and conditional approvals;
- fiscal-year and business-day temporal arithmetic;
- committee authority separation between Grant Committee, Foundation Director,
  and Review Panel;
- quorum and recusal arithmetic;
- correction handling where the correction does or does not change the outcome;
- unresolved-rule preservation for questions the committee explicitly did not
  decide;
- counterfactual reasoning without turning hypothetical facts into durable
  state.
