# Pending External Work Order Audit

This report validates proposal-declared work-order zip structure plus entry-name and template-content leak policy only.
It blocks pending packets that include filled oracle files, judged-QA manifests, model outputs, compile/run artifacts, or literal fact examples inside oracle templates.
It may read packet-control/template files, but it does not read source prose or decide expected/forbidden facts.

- Proposals scanned: `4`
- Pending work orders: `0`
- Standalone tmp work orders: `0`
- Blocking errors: `0`
- Warnings: `0`
- Status: `pass`

| Source | Proposal | Kind | Path | Fixtures | Entries | Errors | Warnings |
| --- | --- | --- | --- | --- | ---: | --- | --- |
