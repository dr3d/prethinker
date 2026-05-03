# The Black Lantern Maze

This fixture is a maximal confusion frontier project for Prethinker.

It is designed to hurt the current architecture on identity, source status,
rule priority, correction safety, overloaded approval language, multilingual
notes, helper-supported executable rules, and clarification eagerness.

## Files

- `story.md`: source fixture to compile.
- `source.md`: preserved copy of the supplied source under its original name.
- `gold_kb.pl`: source-provided reference Prolog KB. Oracle for scoring only.
- `gold_kb_notes.md`: source-provided strategy notes. Oracle/training notes,
  not cold-run context.
- `intake_plan.md`: same strategy notes under the standard planning filename.
- `ambiguity_and_chaos_overlay.md`: focused ingestion/query CE challenge cases.
- `qa_source.md`: original 40-question QA battery.
- `qa.md`: script-compatible QA file for post-ingestion QA experiments.
- `failure_buckets.json`: compact failure taxonomy for review and graphing.
- `progress_journal.md`: running mini-journal of benchmark attempts and lessons.
- `progress_metrics.jsonl`: append-only metrics rows for progress graphs.

## Evidence-Lane Discipline

Cold runs must keep `gold_kb.pl`, `gold_kb_notes.md`, `qa.md`,
`qa_source.md`, and `ambiguity_and_chaos_overlay.md` out of source-compilation
model context. The reference KB and QA files exist to score behavior after a
run, not to guide compilation.

No non-oracle starter ontology registry is currently included. If one is added
later, it should be authored as a generic product-mode profile and clearly
labeled as assisted context, not cold discovery evidence.

## Why It Matters

Black Lantern combines several current hard frontiers in one hostile fixture:

- claim/finding/fact separation;
- source-status discipline;
- unclear proposition handling;
- ambiguous pronouns and overloaded "approved" language;
- same title held by different people at different times;
- near-duplicate names and spelling variants;
- multilingual notes and translation status;
- correction/retraction safety;
- helper-supported rule acquisition;
- priority and anti-rule behavior;
- CE over-eagerness and under-eagerness.

No benchmark run has been recorded yet.
