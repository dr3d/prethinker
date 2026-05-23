# Fixture Notes

## Intake

Received as part of `prethinker_ntsb_pilot_2026_05.zip` on May 23, 2026. The incoming package contained the expected source, metadata, QA, oracle, and provenance files for this fixture, but did not include `source_original.pdf` despite naming it in the package manifest. The original PDF was fetched from the official source URL during intake normalization.

## Source

- Title: Capsizing and Sinking of Towing Vessel Baylor J. Tregre
- Source URL: https://www.ntsb.gov/investigations/AccidentReports/Reports/MIR2521.pdf
- Mode: marine

## Normalization

The canonical `qa.md` was converted from incoming `q001:` markers to numbered markdown so `scripts/run_domain_bootstrap_qa.py` can parse it. Reference answers remain isolated in scoring-only files.
