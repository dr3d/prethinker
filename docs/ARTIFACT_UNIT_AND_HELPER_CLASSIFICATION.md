# Artifact Unit And Legacy Helper Classification

Last updated: 2026-05-16

This note is a historical boundary marker from the helper-retirement migration.
It records why helper rows had to become visible in reports, and why the current
instrument moved away from them as a default answer surface.

The current helper retirement audit lives in
`docs/HELPER_RESIDUE_AUDIT_WORKSHEET.md`.

## Current Artifact Unit

The live no-helper artifact under evaluation is:

```text
source + lens set + deterministic ledgers + admitted predicates + query policy
```

The default query policy is:

```text
--helper-companion-row-limit 0
```

That means native helper companion assembly is skipped upstream. Legacy native
helper adapters remain available only for forensic replay, old artifact
compatibility, and migration audits.

## Historical Helper Unit

Older reports may describe the artifact as:

```text
source + lens set + deterministic ledgers + admitted predicates + helper set
```

That formula is still useful when reading historical May 2026 scorecards because
helper rows were part of what those runs measured. It is no longer the active
default. When a historical result mentions `candidate-helper`, `clean-helper`,
or `transfer-proven-helper`, read it as helper-era evidence that must be either:

- retired as archaeology,
- replaced by direct admitted predicates,
- replaced by deterministic ledger surfaces, or
- kept only behind an explicit forensic/compatibility flag.

## Leakage Test

The helper-era leakage test remains valuable because the same failure mode can
appear in predicates, lenses, query policies, and audit classifiers.

A support surface is legitimate when it performs a general operation over
admitted KB state, deterministic source-record rows, identifiers, dates,
intervals, counts, or generic table/field structure.

A support surface is suspicious when it knows a fixture's proper nouns, exact
row payloads, row ids, answer strings, local organizations, or oracle targets
before it runs.

Examples of legitimate operations:

- count distinct entities by stable identifier
- compute intervals from admitted timestamps
- preserve normalized source-record atoms as exact display strings
- enumerate table rows with a requested identifier
- join custody, authority, access, and title predicates by item id
- expose deterministic source-record fields for a bound query constant

Examples of suspicious operations:

- hard-code a fixture item such as `ex_010`
- hard-code a person, organization, or document id unique to one fixture
- return a prose answer copied from a reference answer rather than derived from
  admitted rows
- trigger only on one fixture's signature names

The current application of this test is broader than helpers: public predicate
names, slot contracts, lens vocabularies, trigger conditions, and audit
classifiers all need the same fixture-free transfer discipline.

## Migration Rule

```text
historical helper result
  -> classify leakage risk
  -> identify the reusable distinction it exposed
  -> replay no-helper
  -> add direct compile/ledger/query surface only if transfer evidence supports it
  -> leave the helper-era row in history
```

The promotion question is not "did the helper rescue rows?" The question is:

```text
What general operation did this expose?
Can that operation transfer without fixture-specific constants?
What upstream compile, ledger, or query-policy surface retires the helper?
```

## Reading Old Labels

Use these labels only when interpreting historical or forensic runs:

| Label | Meaning |
| --- | --- |
| `candidate-helper` | Used a helper with fixture-family constants or unproven transfer behavior. |
| `transfer-proven-helper` | Used a former candidate that passed sibling-fixture replay without new fixture constants. |
| `clean-helper` | Used a generic helper over predicates, ledgers, identifiers, dates, intervals, or counts. |

For current runs, prefer reporting `no-helper`, `direct compile surface`,
`deterministic ledger`, `query policy`, and `selector/guard` behavior.

## Doctrine

Historical helpers made durable state more retrievable without changing what the
KB believed. That was useful, but it was also dangerous: fixture vocabulary can
become architecture unless the support surface is audited.

The current doctrine is stricter:

```text
language proposes
admission governs
state records
direct surfaces answer
legacy adapters compare only when explicitly requested
```
