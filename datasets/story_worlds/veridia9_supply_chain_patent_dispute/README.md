# The Veridia-9 Supply Chain & Patent Integrity Dispute

This fixture is a dense dispute-document frontier project for Prethinker.

It combines pharmaceutical liability, cold-chain compliance, disputed lab
findings, distribution after regulatory hold, patent-stay warranty arguments,
reinsurance notice, corrections, and financial-layer arithmetic. It should be
useful for testing whether the system can keep facts, claims, corrected values,
legal positions, and threshold calculations separate without importing oracle
predicate clues.

## Files

- `story.md`: source document to compile.
- `source.md`: preserved copy of the source under the generic source name.
- `qa_source.md`: original supplied 40-question QA table.
- `qa.md`: script-compatible numbered QA file for post-ingestion QA.
- `progress_journal.md`: running mini-journal of benchmark attempts and lessons.
- `progress_metrics.jsonl`: append-only metrics rows for progress graphs.

## Evidence-Lane Discipline

This fixture intentionally has no `gold_kb.pl`, no `ontology_registry.json`, no
`intake_plan.md`, and no `failure_buckets.json` at admission time. Do not add a
starter profile or reference KB unless a later experiment explicitly creates a
separate assisted lane and labels it as such.

Cold runs should use only `story.md` as the source document. `qa.md` and
`qa_source.md` exist for post-ingestion scoring, not source-compilation context.

No benchmark run has been recorded yet.

## Why It Matters

The fixture pressures:

- source-boundary discipline across policy, audit, legal, and regulatory text;
- correction handling for superseded times and degradation percentages;
- claim/fact separation between Biogenix, Helix, Zenith, FDR, and GRV;
- temporal arithmetic around breach duration, late notice, and sequence order;
- financial arithmetic across deductible, underwriter lines, and reinsurance;
- legal-status reasoning around patent stays and trading-warranty discharge;
- meta-epistemic restraint where the document records disputes but no final
  safety or reinsurance determination.
