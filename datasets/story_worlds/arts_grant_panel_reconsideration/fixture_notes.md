# arts_grant_panel_reconsideration Fixture Notes

## Author Delivery Note

Fixture 4, `arts_grant_panel_reconsideration`, was described by the author as
complete: source around 1,950 words, 40 oracle rows, and all five files in one
artifact.

## Self-Flagged Leakage / Hardness Decision

`source.md` contains worked examples of two derivable values:

- corrected average `75.4` in section 6.1;
- recusal-recomputed average `75.25` in section 9.

This makes Q15 and Q32 effectively direct lookups rather than arithmetic
derivations. The author flagged this in `anti_leakage_manifest.md`.

Possible future choices:

- Strip the worked averages from `source.md` so Q15 and Q32 become true
  arithmetic questions over per-panelist totals.
- Leave as-is and treat those rows as extraction of a stated worked example,
  which is also a legitimate row shape because institutional docs often show
  their math.

No source edit has been made yet. Preserve authored content until an explicit
benchmark-hardness decision is made.

## Fixture-Specific Notes

- Q19 and Q40 are paired. Q19 asks whether the counsel note superseded the
  rejection; Q40 asks whether the corrected score automatically wins the
  fellowship. They test the same procedural-versus-decisional distinction from
  two surface forms.
- Q36 is intentionally multi-clause. The answer chain is: not determined,
  contingent on docket grant, contingent on funding order, Fontaine first,
  contingent reserve list, Foundation Director discretion. It may be simplified
  later if a flatter "not determined" row is preferred.
- A name-collision trap was considered and removed. The author nearly named the
  panel chair "Aida Brennan" to collide with applicant "Lily Brennan," but
  chose "Marchetti" because the collision risked being a gotcha rather than a
  real semantic test. Future fixtures can deliberately include surface-level
  name collisions if that becomes a desired pressure.
