# Provenance — ntsb_marine_investigation_001

## Source URL

`https://www.ntsb.gov/investigations/AccidentReports/Reports/MIR2521.pdf`

CAROL case reference (per the document itself):
`NTSB accident ID DCA24FM038`.

## Retrieval date

2026-05-23.

## How the original was obtained

Retrieved via the `web_fetch` tool against the canonical NTSB report PDF URL.
The fetched representation contained the text-extracted contents of the
issued PDF, including the running page footer
"Capsizing and Sinking of Towing Vessel Baylor J. Tregre MIR-25-21" and the
section numbering.

A direct `curl` download of the PDF binary was attempted but was rejected by
the egress proxy (`x-deny-reason: host_not_allowed`). The verbatim text
extraction is preserved as `source_original.txt`, and `source.md` is the same
text re-rendered as Markdown.

## How source.md was converted

- Numbered sections "1 Factual Information", "1.1 Background", "1.2 Event
  Sequence", "1.3 Additional Information", "1.3.1 Damage", "1.3.2 Vessel
  Inspections and Survey", "1.3.3 Environmental Information", "1.3.3.1
  Reported Weather", "1.3.3.2 Weather Forecasts", "2 Analysis", "3
  Conclusions", and "3.1 Probable Cause" were prefixed with corresponding
  Markdown heading levels (`##`, `###`, `####`, `#####`).
- The Casualty Summary block and the Vessel Particulars block at the end of
  the document were rendered as Markdown tables. Field/value alignment from
  the PDF was preserved.
- Footnotes 1 through 8 were preserved verbatim, inline-set as Markdown
  blockquotes near their referencing prose.
- Figure captions ("Figure 1." through "Figure 8.") were preserved as inline
  text since the figure imagery itself is not part of the text extraction.
- One paragraph in the trailing legal/jurisdictional boilerplate ("The
  National Transportation Safety Board (NTSB) is an independent federal
  agency …") was abbreviated with `[…]` because it is generic agency
  description and not investigation-specific. The mission language about
  fault and 49 U.S.C. § 1154(b) was kept because the Prethinker pipeline
  may test whether the system distinguishes "the NTSB does not assign
  fault" from probable cause language.
- The colloquial phrase "Gulf of America" appears in the source verbatim
  (e.g., Casualty Summary "Gulf of America, 23 nm south of Galveston" and
  Section 2 Analysis). It has been preserved as written; no terminology
  was substituted or modernized.
- No content was paraphrased or added.

## Known extraction issues

- Direct PDF binary cannot be redistributed from this build environment;
  only the verbatim text is preserved.
- A number of "Figure N." labels appear without accompanying images in the
  text representation; this is expected behavior for a text-only
  extraction of an illustrated PDF.
- Wind/speed values in the source mix knots, mph, and kts in various
  passages; the source spellings (e.g., "23 kts", "85-100 mph (about 74-87
  knots)") were preserved without normalization.

## Format of the retained original

`source_original.txt` — UTF-8 plain text mirroring `source.md`.
