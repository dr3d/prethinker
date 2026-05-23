# Provenance — ntsb_aviation_investigation_001

## Source URL

Primary document (PDF):
`https://www.ntsb.gov/investigations/Documents/Preliminary%20Report%20DCA26MA024.pdf`

Companion NTSB investigation landing page:
`https://www.ntsb.gov/investigations/Pages/DCA26MA024.aspx`

## Retrieval date

2026-05-23.

## How the original was obtained

Retrieved via the `web_fetch` tool against the canonical NTSB PDF URL. The
fetched representation contained the page-by-page text extracted from the
NTSB-issued PDF, including the recurring page footer
`This information is preliminary and subject to change` and the
"Aviation Investigation Preliminary Report" header layout.

A direct `curl` download of the PDF binary was attempted but was rejected by
the egress proxy (`x-deny-reason: host_not_allowed`). Because direct PDF
retention was not possible in this build environment, the verbatim text
extraction is preserved as `source_original.txt`, and `source.md` is the
same text minimally re-rendered as Markdown (headings, tables, and the
preliminary-status caveats kept intact). No content was paraphrased or
summarized.

## How source.md was converted

Markdown conversion steps applied to the fetched text:

- Page-break sentinels `Page N of 12 DCA26MA024` and the
  `This information is preliminary and subject to change` caveat lines were
  preserved verbatim, not stripped.
- Section headings such as "History of Flight", "Crew Experience",
  "Recorders", "Airplane and Operator Information", "MD-11 Engine
  Pylon-to-Wing Connection", "Recovery Operations and Wreckage Examination",
  "NTSB Materials Laboratory Examination", "Maintenance and Inspections",
  "Safety Actions", "Similar Events", "Aircraft and Owner/Operator
  Information", "Meteorological Information and Flight Plan", "Wreckage and
  Impact Information", and "Administrative Information" were prefixed with
  Markdown `##` markers.
- Two key/value tables at the end (Aircraft and Owner/Operator Information,
  Meteorological Information and Flight Plan, Wreckage and Impact
  Information, Administrative Information) were rendered as Markdown tables.
  The Passenger Injuries field was intentionally left blank to mirror the
  source, which leaves it blank (this is itself a fixture pressure point).
- Figure captions ("Figure 1." through "Figure 10.") were preserved as
  inline text since the figure images themselves are not part of the text
  extraction.
- No content was added, removed, or rewritten.

## Known extraction issues

- The PDF cannot be redistributed alongside this fixture from the build
  environment; only the text content is preserved. Anyone wanting the
  binary PDF can fetch it from the source URL above.
- The "Amateur Built" and "Operator Designator Code" fields in the Aircraft
  and Owner/Operator Information table render blank in the extraction; that
  matches the visible state of the source PDF.
- The "Passenger Injuries" cell in the Wreckage and Impact Information
  table is blank in the source; this is preserved.
- Diacritics, degree signs, and lat/long minutes-seconds notation were
  preserved as Unicode characters where the original used them.

## Format of the retained original

`source_original.txt` — UTF-8 plain text (mirroring `source.md`). No PDF
binary is retained because the build environment cannot reach `ntsb.gov`
directly.
