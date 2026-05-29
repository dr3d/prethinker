# Fixture notes — osha_incident_ugly_007

## Why this document is "ugly"
The decision contains a dense intermix of party-identifier metadata (docket number 23-0180; recently substituted Acting Secretary in footnote 1; non-standard "the Court" usage for an ALJ tribunal), date and sequence pressure (Sept 7 2022 inspection, Dec 15 2022 citation, March 18 2025 decision; the 14-minute drive-to-worksite gap; the time-stamped 12:16 p.m. first photograph; the 2-day trial), evidentiary-list pressure (three discrete photo ranges Ex. P-1 pp. 1-12, 13-16, 17-18; the four-element prima facie test from Jake's Fireworks; multiple case-law citations including a quoted-citation parenthetical), absence/exception pressure (Irwin's series of admissions about what she did NOT do; the D-ring's visibility in the photographs taken from inside the restaurant), and cross-section pressure (the D-ring placement in the worksite section vs. its non-visibility in the photographs analyzed in a different section; the two-pronged failure-of-prima-facie-case in the Order tying back to two separate analysis sections).

## QA pressure structures (per fresh_ugly_public_batch_v2 spec)
- metadata/id/party (>=5): q001 (docket+ALJ), q002 (counsel), q003 (DISH personnel), q004 (OSHA officers), q005 (footnote 1 substitution), q006 (employee counts), q007 (statutory framework Rule 90(a)(1))
- date/deadline/sequence (>=5): q008 (inspection date), q009 (citation+decision dates), q010 (event ordering), q011 (timestamp + 14-minute gap), q012 (trial duration/location), q013 (Footnote 8 source-of-timing)
- table/list/citation/coord (>=5): q014 (4-element prima facie test from Jake's Fireworks), q015 (three exhibit ranges), q016 (regulatory citation + threshold), q017 (two cited cases for imputed knowledge), q018 (rope+D-ring physical list), q019 (penalty+statutory citation)
- source-state/exception/absence (>=4): q020 (Irwin's admissions of omission), q021 (Barrett's comment characterization), q022 (D-ring not visible in restaurant photos), q023 (DISH safety program; reasonable diligence; foreseeability)
- cross-section (>=4): q003 (parties cross worksite+OSHA-inspection sections), q010 (sequence spans Background + Inspection), q014 (Legal Standard quote + Analysis structure), q024 (D-ring placement in worksite vs visibility in analysis), q025 (Introduction + Order combine)
- exact-wording (>=3): q013 (Footnote 8 wording), q018 (rope/D-ring precise dimensions), q021 (verbatim "fired employees for less"-style characterization)

## What the QA does NOT do
The QA does not ask the model to second-guess the ALJ's credibility findings or to predict appellate disposition. All questions are answerable from the reproduced text.
