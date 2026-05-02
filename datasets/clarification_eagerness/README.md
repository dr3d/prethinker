# Clarification Eagerness Datasets

These fixtures test when Prethinker should ask a clarification question instead
of guessing, over-asking, or silently committing an unsafe row.

Clarification eagerness is evaluated as two related surfaces:

- **ingestion CE**: ambiguity blocks safe symbolic admission while a source or
  utterance is being compiled;
- **query CE**: a user question cannot be safely answered from the admitted KB
  without choosing scope, identity, deadline, stage, or epistemic status for
  the user.

The fixture files are hand-authored calibration assets. Python harnesses may
validate JSON shape, compare declared expected behavior, and log metrics. Python
must not derive entities, predicates, facts, rules, or answers from raw prose.

Current fixtures:

- `clarification_eagerness_trap/`: a small charter/procedure/case-file hybrid
  with 20 ingestion CE cases, 20 query CE cases, and 10 baseline QA probes.
