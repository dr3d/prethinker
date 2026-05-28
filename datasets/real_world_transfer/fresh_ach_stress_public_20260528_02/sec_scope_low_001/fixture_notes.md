# Fixture Notes

## Why this source was chosen

This official or official-adjacent public source was chosen because it contains messy real-world legal, regulatory, aviation, or enforcement language with findings, exceptions, actor chains, and plausible competing explanations. It is suitable for testing ACH ranking without using synthetic prose.

## Sensitivity target

Target: **low**.

Pressure: distinguish cause/driver from scope/consequence and concurrent filing items

Expected behavior: No single row should materially change the winner because e1, e2, e3, and e5 independently support h1. The scope row e4 should not be misread as the causal explanation.

## Tempting wrong hypothesis

The main tempting wrong hypothesis is **No material financial-statement impact**. It is plausible from the document but should not outrank the expected best hypothesis when the ACH question axis is respected.

## Expected direct / partial / off-axis rows

- e1 (No-reliance and restatement because of presentation error): expected direct.
- e2 (Error identified in 2027 Notes presentation): expected direct.
- e3 (Current versus long-term liability classification): expected direct.
- e4 (No total/cash-flow impact): expected off-axis.
- e5 (Control weakness around conversion provisions): expected direct.
- e6 (Revenue weakness is separate): expected direct.
- e7 (PwC ICFR opinion no longer reliable): expected direct.
- e8 (Shareholder letter item): expected off-axis.

## Double-edged evidence

Some rows are intentionally double-edged where a row supports a remediation or prevention theory while also weakening an alternative responsibility theory. These are called out in the ACH payload's oracle-only relevance notes.

## Extraction quirks

The source transcription preserves official-document texture, including repeated legal labels, regulatory citations, lists, awkward line-like segmentation, monetary amounts, exceptions, and agency-style phrasing. The bracketed headings in source.md are added coordinates only and are not oracle hints.
