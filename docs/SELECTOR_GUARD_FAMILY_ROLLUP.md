# Selector Guard Family Rollup

Last updated: 2026-05-18

This report keeps selector guards from becoming fixture-shaped knobs.
Individual guards are allowed while measured, but public doctrine should name
small semantic families rather than row-specific stories.

Detailed generated ledgers belong under `tmp` during active work and in the
cold archive afterward, not in the public docs tree.

## Current Summary

- active guard return sites: `5`
- unique guard reasons: `5`
- classified semantic families: `4`
- unclassified reasons: `0`
- duplicate guard reasons: `0`

This is a healthy terminal-audit state: the family count is small, raw reasons
are classified, and guard compression is no longer the main research lane.

## Guard Families

| Family | Count | Purpose |
| --- | ---: | --- |
| `entity_role_authority` | 1 | Separate identity, role definition, acting authority, collector, contract authority, and guardianship rows from broad action or title-only evidence. |
| `regulatory_access_scope` | 1 | Route all/any scope, affected-set, exclusion, threshold, and deadline questions to access surfaces that bind the correct set and temporal boundary. |
| `rule_decision_procedure` | 1 | Route eligibility, interpretation, recusal, rejection, and procedure-decision questions to evidence that binds the governing rule to the decision facts. |
| `state_custody_ownership` | 2 | Separate current object state, custody transfer, possession, ownership, legal title, and award/result surfaces from generic event, property, or person rows. |

## Promotion Discipline

- Add a guard when it protects a measured semantic mismatch.
- Do not add a guard that only remembers a fixture, row id, answer string,
  local person, or local organization.
- Do not hide guard growth inside parameter bags.
- Merge or split by semantic reason, not by source story.
- Prefer retiring guards when direct compile surfaces, deterministic ledgers,
  or predicate contracts make the originating failure pass upstream.

Guard details are still available through generated local ledgers when needed,
but the public face should expose the family shape and discipline, not the
birth rows.
