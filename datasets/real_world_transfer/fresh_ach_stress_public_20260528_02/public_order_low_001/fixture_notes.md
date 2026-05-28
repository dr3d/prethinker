# Fixture Notes

## Why this source was chosen

This official or official-adjacent public source was chosen because it contains messy real-world legal, regulatory, aviation, or enforcement language with findings, exceptions, actor chains, and plausible competing explanations. It is suitable for testing ACH ranking without using synthetic prose.

## Sensitivity target

Target: **low**.

Pressure: redundant independent support for a broad consent/control remedy; narrower true provisions are off-axis

Expected behavior: No single row should materially change the winner; h1 is supported by many independent remedial provisions. Removing e4 weakens but does not flip the expected read.

## Tempting wrong hypothesis

The main tempting wrong hypothesis is **Consumer reporting agency ban only**. It is plausible from the document but should not outrank the expected best hypothesis when the ACH question axis is respected.

## Expected direct / partial / off-axis rows

- e1 (FTC violation finding context): expected partial.
- e2 (Covered driver data definition): expected direct.
- e3 (CRA disclosure ban): expected direct.
- e4 (Affirmative consent for collection/use/disclosure): expected direct.
- e5 (No coercive degradation for withholding consent): expected direct.
- e6 (Data minimization): expected direct.
- e7 (Access and deletion rights): expected direct.
- e8 (Emergency responder exception): expected off-axis.
- e9 (Misrepresentation prohibition): expected direct.

## Double-edged evidence

Some rows are intentionally double-edged where a row supports a remediation or prevention theory while also weakening an alternative responsibility theory. These are called out in the ACH payload's oracle-only relevance notes.

## Extraction quirks

The source transcription preserves official-document texture, including repeated legal labels, regulatory citations, lists, awkward line-like segmentation, monetary amounts, exceptions, and agency-style phrasing. The bracketed headings in source.md are added coordinates only and are not oracle hints.
