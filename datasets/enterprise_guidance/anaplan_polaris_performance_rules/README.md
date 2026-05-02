# Anaplan Polaris Performance Rules

This fixture is an enterprise technical-guidance frontier project for Prethinker. It pressures rule extraction, conditional recommendation handling, prioritization, optimization tactics, procedure/checklist structure, tradeoffs, and performance-metric normalization.

The source is intentionally not a story-world narrative. It should be treated as operational guidance: many statements are recommendations, warnings, conditions, or prioritization rules, not durable facts about a particular model.

## Files

- `source.md`: source guidance document.
- `gold_kb.pl`: oracle-only reference Prolog surface for scoring and review.
- `ontology_registry.json`: non-oracle starter enterprise-guidance profile for profile-guided experiments.
- `qa.md`: script-compatible numbered QA file for `scripts/run_domain_bootstrap_qa.py`.
- `qa_battery.jsonl`: machine-friendly QA rows with id, phase, question, expected answer, and likely mistake.
- `failure_buckets.json`: compact failure taxonomy for review.
- `progress_journal.md`: running mini-journal of benchmark attempts and lessons.
- `progress_metrics.jsonl`: append-only metrics rows for progress graphs.

## Benchmark Discipline

Cold runs must keep `gold_kb.pl` and `qa_battery.jsonl` out of model context. The reference KB and answer key exist to score emitted signatures, QA support, and oracle behavior after the run.

Profile-guided runs may use `ontology_registry.json`, but journal entries must say so explicitly. This registry is a generic enterprise-guidance/policy profile derived from the fixture brief, not from expected answers.

## Why It Matters

This fixture exposes failures that document/story fixtures do not:

- turning recommendations into already-true facts;
- losing priority order;
- collapsing distinct metrics such as Calculation Effort, Complexity, GB, Memory, and Populated Cell Count;
- missing exceptions and tradeoffs;
- treating "SUM is fast" as "always use SUM";
- collapsing procedure/checklist chains into vague recommendations;
- losing conditions such as "when possible", "if performance degrades", or "when cell counts are high".

