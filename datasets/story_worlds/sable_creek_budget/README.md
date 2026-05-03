# The Sable Creek Budget Amendment

This fixture is a cold/no-oracle frontier project for Prethinker.

It focuses on municipal budget amendment votes, charter thresholds, reserve restrictions, public comments, and post-vote analysis.

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

- vote arithmetic and quorum-like threshold reasoning;
- budget-category and reserve-use constraints;
- public-comment claim versus council action separation;
- counterfactual budget-governance questions;

