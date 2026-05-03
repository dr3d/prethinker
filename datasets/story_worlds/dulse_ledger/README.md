# The Dulse Ledger

This fixture is a cold/no-oracle frontier project for Prethinker.

It focuses on trade, debt, witness rules, family custom, and ledger-validity reasoning.

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

- customary rule application over ledger entries;
- witness and family-membership constraints;
- debt, offset, and validity state tracking;
- source-local trade records without imported assumptions;

