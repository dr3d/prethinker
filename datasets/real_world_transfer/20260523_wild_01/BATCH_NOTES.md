# Real-World Transfer Batch — 20260523_wild_01 — BATCH NOTES

This batch comprises five real-document fixtures intended as a transfer-evaluation set for Prethinker. The fixtures are drawn from five distinct regulatory and investigative domains (aviation, marine, pharmaceutical, securities, occupational safety) so that no two fixtures share named entities, vocabulary, or document structure.

## Selection criteria applied

- **Real public sources only.** No invented documents. No synthetic facts inserted into `source.md`.
- **Awkward, messy, or partial-authority content.** Preliminary status caveats, redactions, conflicting authorities, blank fields, sparse cells, non-chronological ordering, and split-attribution outcomes were all positively selected for.
- **Distinct identifier-and-numeric pressure per fixture.** Each fixture exercises a different style of identifier (NTSB case ID, MARCS-CMS / Warning Letter, SEC accession / CIK / EIN / Commission File No., MNOSHA fatality inspection number) and a different style of numeric extraction (altitudes/airspeeds in feet+knots, wind speeds in knots vs mph, dollar amounts in millions, percentages with floors, national-employee counts).
- **No shared characters or organizations with existing Prethinker fixtures.** Each entity (UPS, Granules India, Hamilton Lane, MNOSHA, Baylor J. Tregre vessel) is unique to its fixture and drawn from real-world public record.

## Documents wanted but not usable

- **Other NTSB final reports for variety:** Several NTSB final aviation reports were considered as alternatives or supplements to the UPS 2976 preliminary report (which is intentionally non-final), but the preliminary-status caveats and explicit FDR-vs-ADS-B discrepancy in DCA26MA024 made it a stronger pressure case for preliminary-status discipline than fully concluded final reports would have been. Final reports remain a candidate for future batches.
- **OSHA federal-program accident investigation summary (OSHA Form 170 narratives):** Federal OSHA used to publish detailed accident-investigation summary text on osha.gov. Recent federal OSHA pages have shifted to the Fatality and Severe Injury Dashboard and the daily-updated Fatality Inspection Data page, which is structured rather than narrative. To preserve a tabular, sparse public-record texture (and a stable URL), the Minnesota OSHA state-plan FFY 2024 summary was selected; it is OSHA-system data in the same federal/state-plan framework.
- **Forms 10-K / S-1 with longer prose disclosures:** Considered but rejected for this batch because the 8-K's tight Item-by-Item structure provides cleaner cross-reference pressure (Item 1.01 → Item 2.03 incorporation by reference, Exhibit 10.1 "qualified in its entirety" caveat) than a sprawling annual report would have within the 25-QA budget.
- **CDC MMWR outbreak reports and EPA enforcement actions:** Considered as a sixth fixture but excluded to keep the batch at exactly five.

## Retrieval environment notes

- The execution environment's egress proxy blocked some direct binary HTTP downloads to ntsb.gov and fda.gov for command-line tools (e.g., curl), with header `x-deny-reason: host_not_allowed`. In every case the `web_fetch` tool retrieved the extracted text of the page, which was then preserved in `source.md` and a copy retained as `source_original.txt`. This is documented per-fixture in each fixture's `provenance.md`. No fixture relied on private or paywalled material.
- For the SEC fixture, the EDGAR-hosted HTML 8-K renders cover-page tables as untagged layout tables; these were retained as Markdown tables to preserve the structural relationships between cell labels and values.
- For the OSHA fixture, the original PDF's wide multi-column tabular layout was converted to five Markdown table sections, each topped with the recurring "Inspection data, including citations, can be viewed at osha.gov/data." header line from the PDF.
- For the NTSB marine fixture, the source preserves the term "Gulf of America" exactly as it appears in the original NTSB report. The fixture does not editorialize on the term.

## Validation performed before zip

- Each fixture has all 12 required files.
- `qa.md` for each fixture contains exactly 25 numbered questions and no answers.
- `oracle.jsonl` for each fixture contains exactly 25 valid JSON lines with sequential q001–q025 IDs.
- Per-fixture category distribution validated: 5 direct_lookup, 3 identifier_entity, 4 temporal_sequence, 4 numeric_unit, 3 source_attribution, 3 conflict_discrepancy, 2 negative_limitation, 1 synthesis.
- For each fixture, `source.md` and `story.md` are byte-equivalent.
- `metadata.json` `source_url` populated for every fixture.
- A `source_original.*` companion file is present in every fixture.

## Notes for fixture consumers

- The `oracle.jsonl`, `qa_battery.json`, and any other answer-bearing file MUST NOT be fed into source compilation. Only `source.md` / `story.md` / `source_original.*` plus the `qa_questions.jsonl` / `qa.md` (questions only) should be presented to a system under test.
- Per-fixture `anti_leakage_manifest.md` files document compliance with this separation discipline.
