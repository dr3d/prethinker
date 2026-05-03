# The Sable Creek Budget Amendment Progress Journal

This journal records cold, diagnostic, assisted, and oracle-calibration runs for
this fixture. Keep evidence lanes separate.

## Fixture Admission

- Timestamp: `2026-05-03`
- Evidence lane: `fixture_admission`
- Source files admitted from: `tmp/sable_creek_budget`
- Initial status: source and 40-question QA battery installed; no compile or QA
  run has been executed.

## First Baseline Plan

Use the current source-only semantic-parallax cold baseline recipe:

```text
story.md
  -> source-only profile bootstrap
  -> flat-plus-focused semantic-parallax compile
  -> mapper admission
  -> QA over admitted KB
```

No gold KB, starter registry, strategy document, or QA answer key should be used
for source compilation in the cold lane.

