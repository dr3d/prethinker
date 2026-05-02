# The Glass Tide Charter

This fixture is a rule-ingestion frontier project for Prethinker. It is a dense charter/source-record narrative for Lumenfall Harbor with source-stated rules, exceptions, overrides, temporal windows, bounded negation, evidence ranking, claims, corrections, permissions, and executable-rule expectations.

## Files

- `story.md`: source fixture.
- `gold_kb.pl`: source-provided reference Prolog KB. Oracle for scoring only.
- `gold_kb_notes.md`: source-provided methodology/training guidance. Oracle/training notes, not cold-run context.
- `intake_plan.md`: same methodology notes under the standard planning filename.
- `qa_source.md`: original table-form QA battery.
- `qa.md`: script-compatible numbered QA file for `scripts/run_domain_bootstrap_qa.py`.
- `qa_battery.jsonl`: machine-friendly 100-question QA rows.
- `qa_support_map.jsonl`: first-20 oracle support-accounting scaffold for failure attribution.
- `failure_buckets.json`: compact failure taxonomy.
- `ontology_registry.json`: non-oracle generic starter profile for assisted product-mode experiments only; not a cold-run claim.
- `progress_journal.md`: running mini-journal of benchmark attempts and lessons.
- `progress_metrics.jsonl`: append-only metrics rows for progress graphs.

## Evidence-Lane Discipline

Cold runs must keep `gold_kb.pl`, `gold_kb_notes.md`, `qa.md`, `qa_battery.jsonl`, and `qa_support_map.jsonl` out of model context. The reference KB and support map exist to score behavior after a run, not to guide compilation.

The starter `ontology_registry.json` is deliberately generic. Profile-guided runs may use it, but their journal entries must say so explicitly. A profile-guided result is product-mode evidence, not cold ontology discovery.

## Why It Matters

Glass Tide targets the next hard frontier: safe executable rule ingestion. A good run should preserve facts and support rows, but also pressure the architecture toward source-supported executable rules for:

- living-cargo quarantine with emergency docking that does not waive quarantine;
- Tideheart critical-state harbor closure;
- Archive access with blue-key revocation and storm-alarm exceptions;
- Council voting with Treasurer veto and emergency override;
- cargo tax thresholds and relief-cargo exceptions;
- acting-warden authority limited to permits;
- salvage reward with sacred-cargo exception;
- patient clearance with two negative tests at least six hours apart;
- evidence ranking where claims do not become findings without support.
