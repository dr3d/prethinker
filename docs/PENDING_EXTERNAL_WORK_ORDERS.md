# Pending External Work Order Audit

This report validates proposal-declared and standalone tmp work-order zip structure plus entry-name and template-content leak policy only.
It blocks pending packets that include filled oracle files, judged-QA manifests, model outputs, compile/run artifacts, or literal fact examples inside oracle templates.
It may read packet-control/template files, but it does not read source prose or decide expected/forbidden facts.
Standalone tmp packets are included in this run.

- Proposals scanned: `4`
- Pending work orders: `1`
- Standalone tmp work orders: `1`
- Blocking errors: `0`
- Warnings: `0`
- Status: `pass`

| Source | Proposal | Kind | Path | Fixtures | Entries | Errors | Warnings |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `tmp_zip` | `legal_authority_clean_public_filings_work_order_20260606_r8` | `standalone_external_work_order` | `tmp/legal_authority_clean_public_filings_work_order_20260606_r8.zip` | `legal_authority_clean_public_filings_work_order_20260606_r8/examples/legal_authority_verification_micro_v1, legal_authority_clean_public_filings_work_order_20260606_r8/examples/legal_authority_verification_micro_v2, legal_authority_clean_public_filings_work_order_20260606_r8/examples/legal_authority_verification_micro_v3, legal_authority_clean_public_filings_work_order_20260606_r8/examples/legal_authority_verification_micro_v4, legal_authority_clean_public_filings_work_order_20260606_r8/examples/legal_authority_verification_micro_v5, legal_authority_clean_public_filings_work_order_20260606_r8/examples/legal_authority_verification_micro_v6` | 31 | `[]` | `[]` |
