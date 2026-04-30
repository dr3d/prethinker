# The Iron Harbor Water Crisis

This fixture is a challenging story-world exploration for Prethinker. It is a municipal water incident with standing policy rules, corrected records, multilingual witness statements, temporal deadlines, joint authorization requirements, and compliance traps.

## Files

- `story.md`: ASCII-normalized source document.
- `gold_kb.pl`: source-provided reference Prolog KB, normalized to ASCII.
- `gold_kb_notes.md`: source-provided strategy notes describing intended pressure points.
- `qa_source.md`: source-provided 100-question battery with answers and notes.
- `qa.md`: script-compatible numbered QA file for `scripts/run_domain_bootstrap_qa.py`.
- `qa_battery.jsonl`: machine-friendly QA rows with id, source id, phase, question, expected answer, and likely mistake.
- `intake_plan.md`: same source strategy notes, placed under the Otters-style planning filename.
- `failure_buckets.json`: compact failure taxonomy for fixture scoring and review.
- `ontology_registry.json`: predicate/signature inventory scaffold derived from `gold_kb.pl`.
- `progress_journal.md`: running mini-journal of benchmark attempts and lessons.
- `progress_metrics.jsonl`: append-only metrics rows for progress graphs.

Generate a local graph-friendly table with:

```bash
python scripts/summarize_story_world_progress.py
```

## Source Fidelity

The source folder contained `source_story.md`, `qa_battery_100.json`, `reference_kb.pl`, and `strategy_notes.md`. The QA answers and reference KB are treated as source-provided benchmark assets. No additional benchmark answers were invented during integration.

The normalized dataset is ASCII-stable. Names with diacritics are transliterated, punctuation is normalized, and the Hindi witness statement is represented by its supplied English translation with an explicit normalization note.

## Why It Matters

This fixture pressures:

- policy scope and exclusion handling;
- correction and retraction handling;
- claim versus established-fact separation;
- temporal deadline arithmetic;
- joint authorization and validity prerequisites;
- multilingual witness extraction through supplied translations;
- false-positive violation avoidance;
- predicate canonicalization under a new domain.

## Current Lesson

The fixture should reward systems that preserve source authority and uncertainty. Foundry Row's notification is compliant, Cheng's pump-awareness disclosure is not a review-board finding, and missing tests or bypass deactivation times must stay missing rather than being filled in by plausible inference.
