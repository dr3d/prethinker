# Strategy for Solving the Black Lantern Maze

Fixture id: `black_lantern_maze_v1`

This is not a normal extraction test. Treat it as a black-hole confusion fixture. The goal is to make Prethinker stronger by forcing it to decide what it is allowed to know, what it must preserve as a claim, what it must ask about, and which rules are safe to promote.

## 1. Do not run this as one giant pass

The source intentionally mixes:
- identity resolution;
- aliases;
- source claims;
- tribunal findings;
- corrections;
- rules;
- anti-rules;
- temporal windows;
- numeric thresholds;
- exceptions;
- priority rules;
- messy translations;
- ambiguous follow-up utterances.

A single pass will either over-compress the ontology or over-commit unsafe rows.

Recommended pass structure:

```text
source backbone pass
  -> entities, roles, documents, aliases, direct timeline rows

source-status pass
  -> source_claim, translated_claim, tribunal_finding, not_tribunal_finding

correction pass
  -> adopted_correction, held_for_clarification, same_entity, unresolved_name

body-fact lenses
  -> cargo values, tests, fever windows, signatures, safety holds, crate statuses

rule lenses by family
  -> filing rule
  -> cargo tax threshold/exception rules
  -> quarantine temporal rule
  -> repair payment authorization / safety priority
  -> salvage reward exception
  -> evidence boundary rule

deterministic union
  -> mapper-admitted facts and promotion-ready rules only

query/probe pass
  -> run QA and CE questions
```

## 2. Preserve epistemic source status

The biggest trap is claim/finding collapse.

These must stay distinct:

```prolog
source_claim(ivo_kest_staff_memo, ivo_kest, caused(kai_morano, mooring_alarm_confusion)).
source_claim(eli_kest_witness_statement, eli_kest, caused(harbor_office, mooring_alarm_confusion)).
source_claim(kai_morano_contractor_letter, kai_morano, caused(kai_moreno, mooring_alarm_confusion)).
tribunal_finding(dock_tribunal, overwritten(alarm_log, before_review)).
not_tribunal_finding(dock_tribunal, caused(kai_morano, mooring_alarm_confusion)).
```

Never derive `caused(kai_morano, mooring_alarm_confusion)` as a fact from a memo.

## 3. Use Clarification Eagerness as admission control

The fixture is designed so CE should fire on:
- "She approved it."
- "Lena approved it."
- "The Acting Watch Captain signed it."
- "The rule says it was valid."
- "No, it was Orin."
- "The blue crate was not abandoned."
- "Kai caused the confusion."
- "Was it late?"

But CE should not fire on:
- source-attributed claims;
- multiple-binding answers;
- broad safe answers;
- direct date-resolved titles;
- clear written corrections.

Target CE behavior:

```text
commit clear partials;
block only ambiguous rows;
ask one compact question targeting the blocked slot;
do not ask when quarantine or claim attribution is sufficient.
```

## 4. Treat "approved" as an overloaded verb

In this fixture, "approved" may mean:
- approved packet as Tide Engineer;
- released funds as Treasurer;
- certified relief cargo;
- verified receipt;
- translated "aprobó";
- claimed approval in damaged text;
- full payment authorization.

Do not canonicalize all of these to `approved/2`.

Recommended normalized surfaces:

```prolog
approved_packet(marta_sol, repair_packet_rp31, tide_engineer, Time).
released_funds(lena_park, repair_funds, treasurer, Time).
certified_relief_by(lamp_rice, lena_pierce, Time).
clarified_meaning(spanish_note_asha_aprobo, verified_receipt(asha_rin, repair_packet_rp31), not_payment_approval).
full_payment_authorized_record(repair_packet_rp31, Time).
```

## 5. Handle duplicate titles by date

`Acting Watch Captain` is not a stable person.

Correct:
- Oren Hale: May 1-May 10.
- Orin Hale: May 11-May 20.
- Orrin Hall: unresolved damaged log name.

A query with date can answer. A query without date may return multiple bindings. A correction without target should clarify.

## 6. Use helper substrates for rule families

Do not let the LLM invent raw arithmetic or unsupported Prolog fragments.

Recommended deterministic helpers:

```prolog
value_greater_than(Cargo, Threshold).
value_at_most(Cargo, Threshold).
hours_at_least(Time1, Time2, Hours).
within_six_hours_before(FeverTime, ClearanceTime).
```

Potential later helpers:

```prolog
signed_by_role(Document, Role).
safety_hold_active_at(Time).
business_deadline_with_extension(Event, Hours).
```

## 7. Promote rules only after probes

A rule is not durable merely because it parses. Use the Glass Tide doctrine:

```text
mapper admission
runtime load
isolated firing test
body-goal support check
fanout check
positive probes
negative probes
promotion-ready filtering
deterministic union
```

Suggested authored probes:

### Filing

Positive:
```prolog
permit_timely(dock_permit_dp44).
```

Negative:
```prolog
permit_late_without_extension(dock_permit_dp44).
```

### Payment

Positive:
```prolog
repair_payment_authorized(repair_packet_rp31).
temporary_stabilization_authorized(emergency_start_order_eso7).
```

Negative:
```prolog
repair_payment_authorized_by_pilot_signature(repair_packet_rp31).
```

### Quarantine

Positive:
```prolog
quarantine_clearance_eligible(juno_mare).
```

Negative:
```prolog
quarantine_clearance_eligible(pavi_chen).
```

### Cargo tax

Positive:
```prolog
derived_tax_status(glass_eels, taxable, harbor).
derived_tax_status(seed_crystals, exempt, harbor).
derived_tax_status(lamp_rice, exempt, harbor).
derived_tax_status(mirror_seeds, taxable, harbor).
```

Negative:
```prolog
derived_tax_status(lamp_rice, taxable, harbor).
derived_tax_status(mirror_seeds, exempt, harbor).
```

### Salvage

Positive:
```prolog
derived_reward_status(tomas_reed, salvage_reward, crate_c17).
derived_reward_status(nell_quill, no_salvage_reward, crate_c71).
```

Negative:
```prolog
derived_reward_status(nell_quill, salvage_reward, crate_c71).
```

## 8. Expected failure modes

### Predicate collapse

The model may emit generic predicates:
```prolog
approved(X,Y).
valid(X).
rule_applies(X).
```

This will destroy queryability.

### Claim/fact collapse

The model may turn:
```text
Ivo claims Kai Morano caused confusion.
```
into:
```prolog
caused(kai_morano, mooring_alarm_confusion).
```

This is a serious failure.

### Translation overcommit

The model may treat translated notes as authoritative facts. It must preserve them as `translated_claim` unless adopted.

### Helper misuse

The model may write:
```prolog
value_greater_than(Value, 500)
```
instead of:
```prolog
value_greater_than(Cargo, 500)
```

Mapper/helper-contract verification should catch this.

### Ambiguous correction overcommit

The model may retract Oren/Orin facts from the vague oral correction. It should not. Only the later written correction is safe.

### Title identity collapse

The model may merge Oren, Orin, and Orrin. It must not.

## 9. Scoring dimensions

Score this fixture on separate surfaces:

```text
entity/alias accuracy
claim-vs-finding discipline
translation/source-status discipline
CE ask/no-ask precision
safe partial preservation
context-write violations
fact extraction accuracy
rule admission count
promotion-ready rule count
positive/negative probe success
QA exact/partial/miss
unsafe durable write count
```

Do not collapse this into a single score too early.

## 10. What "amazing" looks like

A strong Prethinker run should:

1. build a clear backbone of people, roles, documents, times, events;
2. refuse to merge Oren/Orin/Orrin;
3. preserve Ash Rinn as same as Asha Rin only because the clerk clarified it;
4. preserve translated notes as claims unless adopted;
5. keep cause claims separate from tribunal findings;
6. ask on genuinely blocked ambiguous inputs;
7. avoid asking when multiple bindings or broad answers are enough;
8. acquire helper-supported tax, quarantine, payment, and salvage rules;
9. promote only rules that pass positive and negative probes;
10. answer the 40-question battery without turning claims into facts.
