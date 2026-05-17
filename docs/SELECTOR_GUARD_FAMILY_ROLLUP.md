# Selector Guard Family Rollup

This report keeps the selector guard surface from turning into a pile of
fixture-shaped knobs. Individual guards are allowed while they are being
measured, but they should collapse into a small number of semantic families
before they become daily-driver harness doctrine.

Generated from `scripts/select_qa_mode_without_oracle.py`.

Detailed audit ledger output defaults to `tmp/selector_guard_ledger.md` and is intentionally kept out of the public docs tree.

## Summary

- guard return sites: `5`
- unique guard reasons: `5`
- classified families: `4`
- unclassified reasons: `0`
- duplicate guard reasons: `0`

## Growth Health

- status: `warn`
- family budget: `4 / 8`
- largest family: `state_custody_ownership` with `2` guards (`0.4` share)
- unique reason ratio: `1.0`
- guards per family: `1.25`
- unique reasons per family: `1.25`

Raw guard instances may grow during fixture farming, but semantic compression depends on low family count, zero unclassified reasons, no single family becoming a dumping ground, and no parameterized family hiding a large private enumeration table.

Warnings:

- one guard family is absorbing too many instances; consider splitting by semantic reason

## Family Counts

| Family | Count | Purpose |
| --- | ---: | --- |
| `entity_role_authority` | 1 | Separate identity, role definition, acting authority, collector, contract authority, and guardianship rows from broad action or title-only evidence. |
| `regulatory_access_scope` | 1 | Route all/any scope, termination denial, affected-lot exclusion, and reclassification-deadline questions to access surfaces that carry the right set, threshold, target, or temporal boundary. |
| `rule_decision_procedure` | 1 | Route eligibility, interpretation, recusal, rejection, and procedure-decision questions to evidence that binds the governing rule to the decision facts. |
| `state_custody_ownership` | 2 | Separate current object state, custody transfer, possession, ownership, legal title, and award/result surfaces from generic event, property, or person rows. |

## Guard Reasons

### `entity_role_authority`

- `identity question has baseline name/role support and candidate is broad action-heavy` (scripts/select_qa_mode_without_oracle.py:884)

### `regulatory_access_scope`

- `initial-affected greenhouse question needs greenhouse-status plus exclusion/location surface` (scripts/select_qa_mode_without_oracle.py:960)

### `rule_decision_procedure`

- `rule-effect question needs archival memo row value rather than ownership/status rows` (scripts/select_qa_mode_without_oracle.py:939)

### `state_custody_ownership`

- `governing-2024-custody-document question needs exact amendment source-row text with custody/notice clauses` (scripts/select_qa_mode_without_oracle.py:917)
- `tree-amendment measurement question needs archival row-value surface preserving species/DBH/source basis` (scripts/select_qa_mode_without_oracle.py:948)

## Promotion Discipline

- Add a guard freely when it protects a measured row-level failure.
- Do not call a guard a new lens until it transfers or clearly belongs to a family.
- If a family grows past a readable size, split by semantic reason, not by fixture.
- Do not hide guard growth inside parameter bags. A family generator must report its enumerated surfaces, transfer evidence, and retirement candidates.
- Prefer retiring guards when compile/query/helper improvements make the originating failure pass without selector intervention.
- If a guard remains unclassified, either retire it, rename it, or add a family with a purpose.
