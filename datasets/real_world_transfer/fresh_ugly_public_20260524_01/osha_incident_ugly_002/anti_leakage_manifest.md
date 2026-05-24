# Anti-Leakage Manifest — osha_incident_ugly_002

- The collector did not inspect Prethinker internals while building this fixture. No Prethinker source files, schemas, rubric files, or evaluation code were read.
- This document — the OSHA IMIS Accident Report Detail for Accident Summary Nr 123160.015 (Centimark Corporation) and the matched Inspection Detail for Inspection Nr 1455758.015 — is not from any prior Prethinker fixture batch. It was identified by browsing the public OSHA IMIS accident search interface for this batch only.
- The QA in `qa.md`, `qa_questions.jsonl`, and `oracle.jsonl` was written exclusively from the content of `source.md`. No outside facts about Centimark Corporation, the Plant City FL incident, the OSHA investigation, or any related litigation were used to construct or answer the questions.
- No synthetic source text was created. `source_original.txt` and `source.md` are derived only from the two public OSHA IMIS pages cited in `provenance.md`; site chrome and navigation were stripped but the substantive content (tables, dates, identifiers, narrative, settlement record) is preserved from the official source — including the internal 22.8 ft vs 23 ft inconsistency.

## Local runner hygiene

The canonical `qa.md` in this repository is questions-only. The answer-bearing incoming QA file is retained as `qa_authored_with_answers.md` and must be treated like `oracle.jsonl`: scoring-only, never compile or answer context.
