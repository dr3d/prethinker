# Fixture Notes

## Why this source was chosen

This official or official-adjacent public source was chosen because it contains messy real-world legal, regulatory, aviation, or enforcement language with findings, exceptions, actor chains, and plausible competing explanations. It is suitable for testing ACH ranking without using synthetic prose.

## Sensitivity target

Target: **high**.

Pressure: one physical finding anchors probable cause while maintenance and crew alternatives remain plausible decoys

Expected behavior: Removing e1 should not make h2 or h3 win outright, but it removes the clearest official cause statement and should sharply weaken the expected winner; e2 then becomes the next strongest support.

## Tempting wrong hypothesis

The main tempting wrong hypothesis is **Airline maintenance missed a required defect**. It is plausible from the document but should not outrank the expected best hypothesis when the ACH question axis is respected.

## Expected direct / partial / off-axis rows

- e1 (Probable cause names internal anomaly): expected direct.
- e2 (Metallurgy found discrete dirty white spot): expected direct.
- e3 (Fragment caused fuel-fed fire): expected direct.
- e4 (No prior structural or system failure): expected direct.
- e5 (Required surface inspection could not detect cracks): expected direct.
- e6 (Captain rejected takeoff properly): expected direct.
- e7 (Ultrasonic inspection would have helped): expected direct.
- e8 (Maintenance background): expected partial.

## Double-edged evidence

Some rows are intentionally double-edged where a row supports a remediation or prevention theory while also weakening an alternative responsibility theory. These are called out in the ACH payload's oracle-only relevance notes.

## Extraction quirks

The source transcription preserves official-document texture, including repeated legal labels, regulatory citations, lists, awkward line-like segmentation, monetary amounts, exceptions, and agency-style phrasing. The bracketed headings in source.md are added coordinates only and are not oracle hints.
