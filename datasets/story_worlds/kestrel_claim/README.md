# The Kestrel Claim

This fixture is a maritime-insurance dispute frontier project for Prethinker. It pressures source-attributed competing accounts, layered financial arithmetic, dual-role entities, cover-suspension windows, reinsurance thresholds, salvage-security status, multilingual witness statements, legal citations, and temporal corrections.

## Files

- `story.md`: source dispute narrative.
- `gold_kb.pl`: source-provided reference Prolog KB. This is an oracle for scoring only.
- `gold_kb_notes.md`: source-provided strategy notes describing intended pressure points.
- `qa_source.md`: human-readable conversion of the supplied 100-question battery.
- `qa.md`: script-compatible numbered QA file for `scripts/run_domain_bootstrap_qa.py`.
- `qa_battery.jsonl`: machine-friendly QA rows with id, source id, phase, question, expected answer, and likely mistake.
- `qa_support_map.jsonl`: first-20 support-accounting scaffold for failure attribution.
- `failure_buckets.json`: compact failure taxonomy for review.
- `ontology_registry.json`: non-oracle starter maritime-insurance profile for profile-guided experiments. It is not derived from `gold_kb.pl` and should not be used for cold-score claims.
- `intake_plan.md`: same source strategy notes under the standard planning filename.
- `progress_journal.md`: running mini-journal of benchmark attempts and lessons.
- `progress_metrics.jsonl`: append-only metrics rows for progress graphs.

## Benchmark Discipline

Cold runs must keep `gold_kb.pl` out of the model context. The reference KB exists to score emitted signatures, QA support, and oracle behavior after the run. Profile-guided runs may use `ontology_registry.json`, but their journal entries must say so explicitly.

## Why It Matters

Kestrel is designed to expose failures that simpler story worlds do not:

- collapsing competing survey accounts into one fact;
- confusing one entity's separate H&M and P&I roles;
- treating salvage security as payment;
- applying reinsurance late notice to the assured's claim;
- resolving an unresolved navigation dispute;
- treating legal citations as findings;
- losing corrected timestamps, measurements, or financial amounts;
- mixing H&M, P&I, reinsurance, retrocession, salvage, and regulatory authority.
