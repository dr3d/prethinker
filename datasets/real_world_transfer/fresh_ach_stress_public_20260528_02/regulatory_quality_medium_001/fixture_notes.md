# Fixture Notes

## Why this source was chosen

This official or official-adjacent public source was chosen because it contains messy real-world legal, regulatory, aviation, or enforcement language with findings, exceptions, actor chains, and plausible competing explanations. It is suitable for testing ACH ranking without using synthetic prose.

## Sensitivity target

Target: **medium**.

Pressure: systemic quality/process failure versus specific bad decision or data-integrity-only reading

Expected behavior: Removing e4 or e5 should weaken the systemic reading, but h1 should survive because e1 and e2 still supply direct support. Removing several systemic rows could make h2 or h3 appear more competitive.

## Tempting wrong hypothesis

The main tempting wrong hypothesis is **Isolated scanning error**. It is plausible from the document but should not outrank the expected best hypothesis when the ACH question axis is respected.

## Expected direct / partial / off-axis rows

- e1 (QU failed CGMP responsibility): expected direct.
- e2 (Rejected product distributed): expected direct.
- e3 (Scanning procedure explanation): expected direct.
- e4 (Fundamental QU deficiencies): expected direct.
- e5 (Quality systems inadequate): expected direct.
- e6 (Failure to thoroughly investigate): expected partial.
- e7 (Released based on passing retest): expected partial.
- e8 (Microbial contamination not uniform): expected direct.
- e9 (Computer system vulnerabilities): expected off-axis.

## Double-edged evidence

Some rows are intentionally double-edged where a row supports a remediation or prevention theory while also weakening an alternative responsibility theory. These are called out in the ACH payload's oracle-only relevance notes.

## Extraction quirks

The source transcription preserves official-document texture, including repeated legal labels, regulatory citations, lists, awkward line-like segmentation, monetary amounts, exceptions, and agency-style phrasing. The bracketed headings in source.md are added coordinates only and are not oracle hints.
