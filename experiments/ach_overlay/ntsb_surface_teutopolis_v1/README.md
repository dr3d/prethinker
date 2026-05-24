# NTSB Surface Teutopolis ACH Probe

Purpose:

Probe whether the deterministic ACH overlay can separate crash-cause hypotheses
from injury-severity hypotheses on a genuinely fresh Batch 02 public document.

Source:

`datasets/real_world_transfer/fresh_ugly_public_20260524_02/ntsb_surface_ugly_001`

Hypothesis pressure:

- unsafe passing / evasive loss of control as probable cause;
- mechanical or cargo-tank defect as alternative cause;
- driver impairment, fatigue, or distraction as alternative cause;
- HOS exemption or carrier safety management as alternative cause;
- hazmat classification/PPE/decontamination as a severity explanation rather
  than initiating crash cause.

Discipline:

The payload is manually constructed from the source report and references the
compiled source-record substrate. It is not part of QA scoring and does not
write durable KB facts.
