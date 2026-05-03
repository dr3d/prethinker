# The Ridgeline Fire

This fixture is a wildfire incident-command and policy-compliance frontier
project for Prethinker.

It combines standing orders, incident timelines, evacuation authority,
aerial-drop authorization, Red Flag Warning safety constraints, mutual aid,
witness statements, corrections, multilingual testimony with translations, and
counterfactual policy-violation questions.

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

- rule acquisition for standing orders and deadline windows;
- authority separation between IC, Air Ops, and Emergency Manager;
- temporal arithmetic around 30-minute, 2-hour, 3-hour, 4-hour, and 10-day
  windows;
- exclusion handling for non-WUI Mill District versus WUI zones;
- claim/fact separation for witness statements, disclosures, and review-board
  observations;
- multilingual statement extraction while preserving the supplied translations;
- counterfactual reasoning over a fixed set of policy violations.
