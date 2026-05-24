# fresh_ugly_public_20260524_01

A Prethinker test-corpus batch of 8 fixtures, 25 QA pairs each (200 questions total), built exclusively from real, official, public U.S. government documents. None of the source documents were drawn from prior Prethinker fixture batches, and no Prethinker internals were inspected while constructing the QA. See each fixture's `anti_leakage_manifest.md` for the per-fixture statement.

## Domains covered

| # | fixture_id                       | issuer / source                                                  | document type                                                                                                  |
|---|----------------------------------|------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| 1 | `ntsb_aviation_ugly_001`         | NTSB                                                             | Preliminary Report DCA26MA024 — UPS Flight 2976 MD-11F crash, Louisville (SDF), 04 Nov 2025                    |
| 2 | `ntsb_marine_ugly_001`           | NTSB                                                             | MIR-25-21 — Towing vessel *Baylor J. Tregre* capsizing, Gulf of America, 13 May 2024                           |
| 3 | `fda_warning_ugly_001`           | FDA                                                              | Warning Letter MARCS-CMS 721916 to Medical Products Laboratories Inc, 09 Apr 2026                              |
| 4 | `fda_warning_ugly_002`           | FDA                                                              | Warning Letter MARCS-CMS 722113 to Nupack Inc, 20 Mar 2026                                                     |
| 5 | `osha_incident_ugly_001`         | OSHA IMIS                                                        | Accident 180500.015 + Inspection 1814187.015 — Premier Fence LLC, 3 fatalities on I-91 W. Springfield MA, 03/28/2025 (OPEN case, contested) |
| 6 | `osha_incident_ugly_002`         | OSHA IMIS                                                        | Accident 123160.015 + Inspection 1455758.015 — Centimark Corporation, 1 fatality fall through deteriorated roof, Plant City FL, 01/13/2020 (CLOSED case, informal settlement) |
| 7 | `sec_material_event_ugly_001`    | SEC EDGAR                                                        | 1606 Corp. — Form 8-K Item 1.01, First Amendment to Purchase and Sale Agreement with Jefferson Enterprise Energy LLC, 13 Apr 2026 |
| 8 | `sec_material_event_ugly_002`    | SEC EDGAR                                                        | Pool Corporation — Form 8-K Item 5.02 + 7.01, CEO transition (Arvan → Watwood), Executive Chair appointment (Stokely), 04 May 2026 |

## Per-fixture file layout

Every fixture directory contains these files:

| file                       | role                                                                                  |
|----------------------------|---------------------------------------------------------------------------------------|
| `source_original.txt`      | plain-text capture of the official source                                              |
| `source.md`                | Markdown rendering preserving tables, dates, identifiers, and narrative                |
| `metadata.json`            | fixture ID, source URLs, issuer, event date, retrieval date, pressure tags             |
| `provenance.md`            | source URLs, retrieval method, transformations performed, caveats                      |
| `fixture_notes.md`         | why this document was chosen, messy features, Prethinker design pressure               |
| `qa.md`                    | 25 human-readable questions in five categories of five                                 |
| `qa_authored_with_answers.md` | preserved incoming QA file with authored reference answers; scoring-only, not runner input |
| `qa_questions.jsonl`       | the same 25 questions, JSONL with `id` and `question` fields                           |
| `oracle.jsonl`             | reference answers, JSONL with `id` and `reference_answer` fields                       |
| `anti_leakage_manifest.md` | per-fixture statement of independence from Prethinker internals and prior fixtures     |

## QA composition (every fixture)

- **5 direct lookup** (q001–q005)
- **5 timeline / date / order** (q006–q010)
- **5 table / source-record** (q011–q015)
- **5 reasoning / join** (q016–q020)
- **5 negative / exception / contrast** (q021–q025)

## Sources

Every source URL is recorded in the per-fixture `provenance.md` and `metadata.json`. Origin domains used:

- `ntsb.gov` (Accident reports and Marine Incident Reports, PDF)
- `fda.gov` (Warning Letters, HTML)
- `osha.gov` and `osha.prod.pace.dol.gov` (IMIS Accident Report Detail / Inspection Detail pages, HTML)
- `sec.gov` (EDGAR 8-K filings, HTML)

## Retrieval date

All sources retrieved 2026-05-24.

## How to use

1. Read each `source.md` as the system-under-test's input.
2. Score the system's answers against `oracle.jsonl`, keyed by question `id`.
3. Use `fixture_notes.md` and the `pressure_tags` array in `metadata.json` to bucket per-fixture failure modes when reporting.

## Notes

- Some source documents contain real, in-the-original inconsistencies (e.g., osha_incident_ugly_002 lists the fall height as 22.8 ft in the narrative and 23 ft in three structured fields). These are preserved verbatim; the oracle reports both values. Questions are written so that "both" is the correct answer, not one or the other.
- Some source documents contain heavy redactions (b)(4) in the FDA fixtures. The oracle treats redacted content as redacted; questions are not written to require the redacted content.
- Some source documents (the Pool Corporation 8-K) had cover-page registrant tables that did not survive HTML extraction. Where this occurs, `provenance.md` discloses the gap and `source.md` notes the missing element rather than fabricating substitute content.
