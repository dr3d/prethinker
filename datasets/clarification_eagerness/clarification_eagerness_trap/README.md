# The Clarification Eagerness Trap

Fixture id: `clarification_eagerness_trap_v1`

This fixture targets clarification eagerness as knowledge-acquisition behavior.
It is intentionally modest: the point is not broad domain coverage, but
measurable ask/no-ask behavior when facts, claims, rules, corrections, titles,
and queries collide.

## Files

- `source.md`: compact source case file for Lantern Bridge Ferry Landing.
- `clear_answer_key.md`: compact source-support key and baseline expected
  symbolic surface.
- `ambiguity_cases.md`: hand-authored ingestion CE cases.
- `qa.md`: hand-authored query CE cases plus baseline QA.
- `expected_ce_behavior.md`: aggregate expected CE behavior and scoring notes.
- `ingestion_cases.jsonl`: machine-readable ingestion CE cases derived from the
  authored table.
- `query_cases.jsonl`: machine-readable query CE cases derived from the
  authored table.
- `baseline_qa.jsonl`: machine-readable baseline QA rows derived from the
  authored table.
- `progress_journal.md`: run history and lessons.
- `progress_metrics.jsonl`: compact metrics for progress graphs.

## Expected Shape

Ingestion CE:

- `20` cases total.
- `10` should ask or partial-ask.
- `10` should not ask.
- Safe partials are expected in mixed clear/ambiguous rows.

Query CE:

- `20` cases total.
- `7` should ask.
- `13` should answer without asking, including one multiple-binding answer and
  one broad answer that preserves distinctions.

## Research Rule

Clarification is not failure. A good clarification is an admission-control
success: the system noticed that durable truth would require a choice it was
not authorized to make.
