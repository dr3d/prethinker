# 2026-05-23 NTSB Two-Document Pilot

This batch preserves the two-document NTSB real-world pilot received on May 23, 2026.

## Fixtures

- `ntsb_001`: NTSB aviation preliminary report for Robinson Helicopter R44 II accident WPR24FA200.
- `ntsb_002`: NTSB marine final report for the capsizing and sinking of towing vessel Baylor J. Tregre, MIR-25-21 / DCA24FM038.

## Intake Assessment

The package followed the important separation discipline: each fixture included source text, metadata, provenance, questions without answers, and a separate JSONL oracle with 25 rows. The two practical misses were:

- `source_original.pdf` files were named in the manifest but not included in the archive.
- Incoming `qa.md` files used `q001:` markers, while the current QA runner expects numbered markdown.

The canonical dataset copy fixes the QA shape, preserves the incoming QA files as `qa_authored.md`, and records the missing-PDF caveat. The original PDFs were fetched from the official source URLs during intake normalization and retained as `source_original.pdf`.

## File Shape

Each fixture keeps:

- `source.md`: source document for compilation.
- `story.md`: source-compatible alias.
- `qa.md`: runner-compatible questions only.
- `qa_authored.md`: incoming q-id question file.
- `oracle.jsonl`: reference answers for after-the-fact scoring.
- `qa_questions.jsonl` and `qa_battery.json`: structured QA convenience files.
- `metadata.json`, `provenance.md`, `README.md`, and notes/progress files.

Do not feed `oracle.jsonl`, `qa_battery.json`, or other answer-bearing files into source compilation.
