# Anti-leakage manifest — osha_incident_ugly_003

## Principles
1. `source.md` and `source_original.txt` contain only the document text (and its faithful Markdown rendering). They contain no QA hints, no editorial commentary, and no answer-bearing annotations.
2. `qa.md` and `qa_questions.jsonl` contain only questions and category labels. No reference answers, no oracle text, no spoilers.
3. `oracle.jsonl` contains reference answers. It is excluded from any prompt that includes `qa.md` or `qa_questions.jsonl` in the same context window during evaluation.
4. `qa_authored_with_answers.md` is a human-review artifact only. It pairs questions with answers and must not be supplied to the model under test.
5. `metadata.json`, `provenance.md`, and `fixture_notes.md` describe the fixture and its pressure points. They contain factual descriptions of what the source says (e.g. that the report embeds contributing-factor language in the probable-cause paragraph rather than in a separate subsection) and may be visible to humans during review, but are not supplied to the model under test during QA evaluation.

## File roles
| File | Purpose | Visible to model under test? |
| --- | --- | --- |
| `source.md` | Document text (Markdown extract) | Yes (always) |
| `source_original.txt` | Original-format snapshot (text-equivalent to `source.md`) | Optional (alternative encoding) |
| `qa.md` | Questions only, human-readable | Yes (when prompting questions) |
| `qa_questions.jsonl` | Questions only, machine-readable | Yes (when prompting questions) |
| `oracle.jsonl` | Reference answers | No |
| `qa_authored_with_answers.md` | Human review artifact | No |
| `metadata.json` | Fixture metadata | No |
| `provenance.md` | Source provenance | No |
| `fixture_notes.md` | Pressure-point notes (for graders) | No |
| `anti_leakage_manifest.md` | This file | No |

## Verification checklist (run at fixture-build time)
- [x] Question IDs in `qa.md`, `qa_questions.jsonl`, `oracle.jsonl`, and `qa_authored_with_answers.md` match (q001…q025).
- [x] No reference answer text appears in `qa.md` or `qa_questions.jsonl`.
- [x] No QA hint or editorial annotation appears inside `source.md`.
- [x] All category counts match the spec (5/5/5/5/5).
- [x] All elapsed-time arithmetic in oracle answers is shown work, not just final numbers.
