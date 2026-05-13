# Boundary Probe: Set Dedupe Aggregation Pair

## Probe A: Asset Register Reconciliation

Register R-40 lists these asset rows:

| Row | Asset token | Active in register |
| --- | --- | --- |
| A-1 | pump-alpha | yes |
| A-2 | valve-beta | yes |
| A-3 | gauge-gamma | yes |
| A-4 | pump-alpha-alt | yes |
| A-5 | relay-delta | no |

Row A-4 is an alias row for the same physical asset as row A-1. Row A-4 is not
a separate asset for unique-count purposes.

Row A-5 is retired and is excluded from the active-register set.

The register does not print the resulting unique active asset set or its count.

## Probe B: Zone Coverage Revision

Coverage revision ZR-8 begins with parcel set base-1:

| Parcel | Included in base-1 |
| --- | --- |
| P-101 | yes |
| P-102 | yes |
| P-103 | yes |
| P-104 | yes |
| P-105 | yes |

Hazard notice H-2 affects parcels P-102 and P-104. The unaffected view is
defined as base-1 minus parcels affected by H-2.

Amendment M-7 adds parcel P-106 to the covered set after the base-1 list. The
post-amendment covered view is base-1 union the M-7 additions.

The revision does not print the unaffected parcel list, the unaffected count,
the post-amendment covered list, or the post-amendment covered count.
