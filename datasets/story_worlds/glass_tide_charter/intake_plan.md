# Artifact 4 - Methodology and Training Guidance

# How the Gold KB Was Derived

This document explains the reasoning strategy used to transform the source fixture into the gold Prolog KB. It is intended as training guidance for Prethinker prompt, schema, mapper, and rule-admission work.

---

## 1. First, separate source-layer types

The source document contains several epistemic shapes. They should not all become the same kind of Prolog row.

### A. Direct source facts

These are explicit claims made by the narrative source as authoritative facts inside the fixture:

```prolog
role(mara_vale, harbor_warden).
vessel_arrival(sunless_heron, t1820).
cargo_value(sapphire_figs, 130).
```

### B. Observations and records

Some facts are important because of their evidence type:

```prolog
observed(owl_faces_sea_at_dawn(azure17)).
instrument_record(tideheart_pressure(t1740, 84)).
certified_log(arrival_time(amber_finch, t1910)).
```

This matters because the fixture contains an evidence rule: watch logs, instrument records, and certified logs can support findings.

### C. Claims

Captain Orra's alleged clearance is deliberately not admitted as a signed-clearance fact:

```prolog
claim(captain_orra_pike, signed_clearance(sunless_heron), t1821).
observed(no_signed_clearance_found(sunless_heron)).
```

The correct representation is **claim**, not:

```prolog
signed_clearance(sunless_heron).
```

That distinction tests whether Prethinker prevents unsupported state changes from entering durable truth.

### D. Source-stated rules

Rules explicitly read from the Charter become executable rules when the conditions and actions are clear:

```prolog
owes_harbor_tax(Owner, Cargo) :-
    cargo_owner(Cargo, Owner),
    cargo_value(Cargo, Value),
    Value > 100,
    \+ relief_cargo(Cargo).
```

### E. Derived helper rules

Some rules are not new domain knowledge; they are utility or summary projections that make querying easier:

```prolog
cargo_tax_status(Cargo, owes_tax) :-
    cargo_owner(Cargo, Owner),
    owes_harbor_tax(Owner, Cargo).
```

Prethinker should label these differently from source-stated rules when possible.

---

## 2. Normalize entities into stable atoms

Names were normalized to lowercase snake_case atoms:

```text
Mara Vale       -> mara_vale
Sunless Heron   -> sunless_heron
Archive Vault   -> archive_vault
blue-salt C17   -> blue_salt_crate_c17
```

Guidance for Prethinker:

- Preserve proper names as stable atoms.
- Avoid inventing shorter aliases unless the source uses them repeatedly.
- Keep object identity distinct from category identity.

For example:

```prolog
cargo(blue_salt_crate_c17).
abandoned(blue_salt_crate_c17).
```

is better than collapsing the crate into a generic `blue_salt` concept.

---

## 3. Represent time as comparable symbols

The story uses times heavily. I represented each source time as an atom and added minute values:

```prolog
time_min(t1740, 1060).
time_min(t2230, 1350).
```

This allows rules such as:

```prolog
between_inclusive(T, S, E) :-
    at_or_after(T, S),
    at_or_before(T, E).
```

Why this matters:

- The glass tide is a temporal window.
- The storm alarm is a temporal window.
- The harbor closure is a temporal window.
- Patient test clearance depends on elapsed time.
- Key revocation depends on a temporal interval.

Prethinker should avoid storing only English phrases like `during_evening`; it should create enough structure to reason.

---

## 4. Convert explicit condition/action language into rules

The Charter rules often have the shape:

```text
If condition C, then action/status A, unless exception E.
```

Example:

```text
A cargo owner owes harbor tax when the cargo value is greater than 100 crowns and the cargo is not relief cargo.
```

Gold rule:

```prolog
owes_harbor_tax(Owner, Cargo) :-
    cargo_owner(Cargo, Owner),
    cargo_value(Cargo, Value),
    Value > 100,
    \+ relief_cargo(Cargo).
```

Important training point:

- Do not compile a universal rule as a fact.
- Do not compile a recommendation or permission as an already-executed event.
- Preserve exceptions explicitly.

---

## 5. Preserve negative conditions carefully

The KB uses negation-as-failure for closed-world fixture conditions, such as no emergency signal or no signed clearance.

Example:

```prolog
must_wait_offshore(Vessel) :-
    vessel_arrival(Vessel, Time),
    harbor_closed_at(Time),
    \+ emergency_signal(Vessel, Time).
```

This is acceptable in a bounded fixture because the source document is treated as the closed evidence set.

Training caution:

In real deployments, `\+ emergency_signal(Vessel, Time)` should often be admitted only when the profile treats the available records as complete enough for that predicate.

---

## 6. Model exceptions and override rules explicitly

The copper-rails vote is a good test because four supporters are not enough when a Treasurer veto applies to a budget matter.

Gold rule:

```prolog
proposal_passes(Proposal) :-
    support_count(Proposal, Count),
    Count >= 3,
    \+ (budget_matter(Proposal), treasurer_veto(Proposal, _), \+ emergency_override(Proposal)).
```

Gold failure rule:

```prolog
proposal_fails(Proposal) :-
    support_count(Proposal, Count),
    Count >= 3,
    budget_matter(Proposal),
    treasurer_veto(Proposal, _),
    \+ emergency_override(Proposal).
```

This tests whether Prethinker handles:

- normal rule;
- exception;
- exception-to-exception.

---

## 7. Keep permissions distinct from events

The source says that certain vessels **may** dock under conditions. That does not mean every vessel did dock.

Correct pattern:

```prolog
may_dock_at_west_sluice(Vessel) :-
    vessel_arrival(Vessel, Time),
    harbor_closed_at(Time),
    emergency_signal(Vessel, Time).
```

Separate event fact:

```prolog
docked_at(sunless_heron, west_sluice, t1825).
```

Prethinker should not transform permission into occurrence.

---

## 8. Keep claims from becoming operational state

The source includes Captain Orra's clearance claim, but no signed clearance exists.

Correct:

```prolog
claim(captain_orra_pike, signed_clearance(sunless_heron), t1821).
claim_only(signed_clearance(sunless_heron)).
```

Incorrect:

```prolog
signed_clearance(sunless_heron).
```

This distinction is central to Prethinker's epistemic architecture. A claim can be recorded as a claim. It cannot become a fact merely because a source character said it.

---

## 9. Represent corrections as precedence rules, not duplicate facts

The Amber Finch arrival time deliberately includes a conflict:

```prolog
uncertified_arrival_note(amber_finch, t1850).
certified_arrival_time(amber_finch, t1910).
```

The effective arrival rule chooses the certified time:

```prolog
effective_arrival_time(V, T) :- certified_arrival_time(V, T).
effective_arrival_time(V, T) :-
    uncertified_arrival_note(V, T),
    \+ certified_arrival_time(V, _).
```

Training guidance:

- Do not erase the weaker note unless the task is mutation/retraction.
- Preserve both source rows and add a rule for which controls.

---

## 10. Rule admission should require support links

For a real Prethinker rule-acquisition pass, every executable rule should carry support metadata outside raw Prolog, such as:

```json
{
  "rule_id": "rule_tax_001",
  "prolog_clause": "owes_harbor_tax(Owner, Cargo) :- cargo_owner(Cargo, Owner), cargo_value(Cargo, Value), Value > 100, \\+ relief_cargo(Cargo).",
  "source_rule": "Tax rule",
  "source_span": "A cargo owner owes harbor tax when...",
  "risk": "low",
  "admission_status": "candidate"
}
```

The gold KB shows the desired executable result, but Prethinker should admit such rules only through a stricter path than ordinary facts.

---

## 11. Candidate rule-acquisition checklist

A candidate executable rule should pass these checks before durable admission:

1. The source states a clear condition/effect or condition/permission relation.
2. All predicates in the rule are already allowed by the profile or admitted predicate registry.
3. Every variable in the head appears safely in the body.
4. The rule does not promote a claim into a finding.
5. The rule does not convert a permission into an event.
6. The rule preserves exceptions.
7. The rule has a source/support link.
8. The rule does not rely on broad world knowledge outside the fixture.
9. The rule is tested in query-only mode before durable admission.

---

## 12. How I reasoned through the fixture

The process was:

1. **Segment the source** into setting, Charter rules, event facts, claims/corrections, and end-state notes.
2. **Extract entities**: people, roles, places, vessels, cargo, events, times.
3. **Normalize atoms** using lowercase snake_case.
4. **Mark epistemic source type**: direct source fact, observation, instrument record, certified log, uncertified note, claim.
5. **Identify source-stated rules** by looking for condition/effect language: "if", "when", "unless", "only if", "may", "must", "does not waive".
6. **Separate permission from occurrence**.
7. **Separate claim from finding**.
8. **Convert temporal windows** into comparable time facts and interval rules.
9. **Add executable rules** only where the source rule was explicit and bounded.
10. **Add derived summary predicates** only to support common QA without changing the truth model.
11. **Design questions** to force reasoning across facts and rules.

---

## 13. Failure modes this fixture is designed to reveal

### A. Claim promotion

Bad systems will assert:

```prolog
signed_clearance(sunless_heron).
```

Correct systems will keep it as a claim.

### B. Rule-to-fact collapse

Bad systems will assert:

```prolog
owes_harbor_tax(basil_crow, sapphire_figs).
```

A better system may derive it from:

```prolog
owes_harbor_tax(Owner, Cargo) :- ...
```

It is acceptable to store both source facts and derived facts in different layers, but they should be labeled.

### C. Permission/event confusion

Bad systems will infer that every vessel with permission actually docked.

### D. Exception loss

Bad systems will say copper rails passed because four people supported it.

### E. Temporal flattening

Bad systems will miss that the harbor reopened at 22:30 while the storm alarm remained active until midnight.

### F. Correction mishandling

Bad systems will keep both Amber Finch arrival times as equally true.

### G. Insufficient variable safety

Bad rule output may contain variables in the head that do not occur in the body.

### H. Over-specific rules

A weak compiler may produce:

```prolog
owes_harbor_tax(basil_crow, sapphire_figs).
```

but fail to produce the general tax rule.

### I. Over-general rules

A risky compiler may invent rules such as:

```prolog
all_captain_claims_are_false(X) :- captain(X).
```

The source does not support that. It only says unsupported claims are not findings.

---

## 14. Recommended Prethinker evaluation modes

Run the fixture in at least four modes:

### Mode 1: Fact-only cold compile

Measures whether the system can extract entities, events, and source facts without rules.

### Mode 2: Rule-candidate pass

The model proposes executable rules, but the mapper only records candidates and diagnostics.

### Mode 3: Query-only rule trial

Load candidate rules in an isolated runtime and run the QA battery without durable admission.

### Mode 4: Admitted rules + facts

Only after rule safety checks pass, run the full KB with durable admitted rules.

---

## 15. Scoring guidance

Suggested scoring categories:

```text
fact_exact
rule_exact
rule_partial
claim_fact_boundary_error
permission_event_error
temporal_window_error
exception_error
correction_precedence_error
query_surface_gap
answer_surface_gap
```

High-value questions are not just those that retrieve facts. The best questions require at least one rule plus at least one fact, for example:

- Why did copper rails fail despite four supporters?
- Was repair order 72 authorized?
- Was Mira cleared from quarantine?
- Could the Sunless Heron dock at West Sluice?
- Did Orra's clearance claim become a finding?

---

## 16. Summary

This fixture is designed to move Prethinker beyond a queryable fact ledger toward safe executable rule ingestion. The correct architecture is not "let the LLM write Prolog rules directly into the KB." The correct architecture is:

```text
source document
  -> backbone facts
  -> support facts
  -> rule candidates
  -> deterministic rule admission
  -> query-only trial
  -> durable executable rules
```

The story is intentionally whimsical, but the logic pressures are serious: admission boundaries, source support, rule safety, exceptions, temporal reasoning, claims, corrections, and derived consequences.
