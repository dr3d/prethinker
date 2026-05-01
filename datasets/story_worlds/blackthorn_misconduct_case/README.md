# The Blackthorn Misconduct Case

This fixture is a hostile source-document benchmark for Prethinker.

It is a university research-misconduct proceeding assembled from policy extracts,
procedural timelines, witness statements, financial traces, corrections, and
appeal records. It is designed to hurt the system in places Iron Harbor only
started to touch: procedural state, business-day and calendar-day deadlines,
authority shifts, findings vs sanctions, advisory opinions that are not
determinations, unresolved questions, and financial dependencies.

## Files

- `story.md` - the source document to compile.
- `gold_kb.pl` - reference Prolog KB for deterministic oracle work.
- `ontology_registry.json` - fixture-owned predicate vocabulary only, not facts.
- `qa.md` - 100 human-readable QA probes with answer key.
- `qa_battery.jsonl` - machine-readable QA battery.
- `qa_support_map.jsonl` - first-20 support expectations for root-cause scoring.
- `failure_buckets.json` - expected failure classes.
- `intake_plan.md` / `gold_kb_notes.md` - strategy notes from the fixture author.
- `progress_journal.md` / `progress_metrics.jsonl` - live research record.

## Core Traps

- Do not collapse witness claims into findings.
- Do not treat FSRB sanction modification as overturning the finding.
- Do not answer explicitly unresolved Tanaka reporting-obligation questions as settled.
- Do not use corrected-away committee rosters or publication dates as current truth.
- Do not confuse inquiry-extension authority with investigation-extension authority.
- Do not treat General Counsel's fund-return opinion as a university determination.
- Preserve multilingual witness statements as source-owned claims.
