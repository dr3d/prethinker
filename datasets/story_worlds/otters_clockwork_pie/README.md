# Three Otters And The Clockwork Pie

This fixture is a story-world frontier project for Prethinker. It is intentionally
Goldilocks-shaped, but all durable facts must come from the local source story:
otters, mugs, boots, boats, clockwork pie, mint, Tilly Tumbletop, and the later
repair arc. Any bears, porridge, chairs, beds, or familiar-template facts are
failures unless they appear in the source.

## Files

- `story.md`: source story.
- `gold_kb.pl`: human-authored reference Prolog KB.
- `gold_kb_notes.md`: explanation of the document-to-logic strategy behind the
  reference KB.
- `qa_source.md`: original 100-question battery with expected answers and likely
  failure notes.
- `qa.md`: script-compatible numbered QA file for
  `scripts/run_domain_bootstrap_qa.py`.
- `qa_battery.jsonl`: machine-friendly QA rows with id, phase, question,
  expected answer, and likely mistake.
- `intake_plan.md`: proposed benchmark/game-plan and failure buckets.
- `failure_buckets.json`: compact story-world failure taxonomy for fixture
  scoring and review.
- `ontology_registry.json`: predicate/signature inventory scaffold derived from
  `gold_kb.pl`.
- `progress_journal.md`: running mini-journal of benchmark attempts and lessons.
- `progress_metrics.jsonl`: append-only metrics rows for progress graphs.

Generate a local graph-friendly table with:

```bash
python scripts/summarize_story_world_progress.py
```

## Why It Matters

This is a high-pressure story-world test for the current Semantic IR direction:

- source fidelity over famous-story priors;
- entity grounding without replacing local names with familiar aliases;
- narrative chronology and event ordering;
- subjective judgment versus objective fact;
- narrator truth versus character speech;
- final-state updates after repair/remedy events;
- norm and responsibility extraction without smuggling moral conclusions into
  unsupported facts.

The fixture should be used as a staged benchmark:

1. Load `gold_kb.pl` and test whether the deterministic Prolog layer can answer
   the QA battery when the KB is already good.
2. Ask Prethinker to compile `story.md` without target-Prolog hints, then compare
   admitted predicate signatures and QA support against the reference.
3. Use failure buckets from `intake_plan.md` to improve profile/context pressure,
   not Python-side language patches.

## Current Lesson

The local UI segmented-ingestion path needs exact prior source spans in context.
Without that, later segments such as "They had each..." or "While they were
gone..." are too easy for the model to under-extract or over-clarify. With exact
source-span context, the model is much less likely to import Goldilocks-style
template facts.
