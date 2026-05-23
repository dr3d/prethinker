# Fixture Notes

## Intake

Received as part of `prethinker_ntsb_pilot_2026_05.zip` on May 23, 2026. The incoming package contained the expected source, metadata, QA, oracle, and provenance files for this fixture, but did not include `source_original.pdf` despite naming it in the package manifest. The original PDF was fetched from the official source URL during intake normalization.

## Source

- Title: Robinson Helicopter R44 II Accident, Bluestem, Washington
- Source URL: https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/194501/pdf
- Mode: aviation

## Normalization

The canonical `qa.md` was converted from incoming `q001:` markers to numbered markdown so `scripts/run_domain_bootstrap_qa.py` can parse it. Reference answers remain isolated in scoring-only files.

## 2026-05-23 Spotcheck Lesson

q009 pressured duration answers whose endpoints survive as source-record clock
tokens but not as a complete typed event pair. The general repair is
query-only source-record clock-duration support; this fixture should not teach
the harness any NTSB-specific vocabulary.
