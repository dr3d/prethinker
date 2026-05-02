# Expected CE Behavior

Fixture id: `clarification_eagerness_trap_v1`

## Why this fixture exists

This fixture targets clarification eagerness as knowledge acquisition behavior. A correct run is not the run that asks the most questions. A correct run is the run that asks when a durable write, executable rule, identity merge, correction, or query answer would otherwise require an unauthorized choice.

## Expected aggregate behavior

### Ingestion cases

Total ingestion cases: 20

Expected distribution:

| Behavior | Count | Case IDs |
|---|---:|---|
| `clarify` | 7 | ICT-001, ICT-003, ICT-005, ICT-007, ICT-009, ICT-013, ICT-019 |
| `commit_partial_clarify_blocked` | 3 | ICT-008, ICT-012, ICT-016 |
| `commit_no_ask` | 6 | ICT-002, ICT-004, ICT-006, ICT-014, ICT-018, ICT-020 |
| `commit_claim_no_ask` | 2 | ICT-010, ICT-015 |
| `quarantine_no_ask` | 2 | ICT-011, ICT-017 |

Expected needed clarification count: 10  
Expected no-ask count: 10  
Safe partial cases expected: ICT-001, ICT-002, ICT-004, ICT-006, ICT-008, ICT-010, ICT-012, ICT-014, ICT-015, ICT-016, ICT-017, ICT-018, ICT-020

### Query cases

Total query cases: 20

Expected distribution:

| Behavior | Count | Case IDs |
|---|---:|---|
| `clarify` | 7 | QCT-001, QCT-003, QCT-005, QCT-007, QCT-009, QCT-017, QCT-019 |
| `answer` | 11 | QCT-002, QCT-004, QCT-006, QCT-008, QCT-010, QCT-012, QCT-013, QCT-015, QCT-016, QCT-018, QCT-020 |
| `answer_multiple` | 1 | QCT-011 |
| `answer_broad` | 1 | QCT-014 |

Expected query clarification count: 7  
Expected no-ask query count: 13

## What counts as correct clarification

A clarification is correct when it:

1. targets the blocked slot;
2. asks one compact question if possible;
3. does not turn the question into a durable write;
4. preserves clear safe partials;
5. does not demand irrelevant details.

Examples:

| Case | Good question | Bad question |
|---|---|---|
| ICT-001 | "Who does 'she' refer to?" | "Can you restate the whole case?" |
| ICT-005 | "Which rule do you mean?" | "What is a rule?" |
| ICT-007 | "What was filed on April 5?" | "Was the repair permit timely?" |
| ICT-009 | "Does the emergency exception affect only filing or also safety suspension?" | "Should I ignore the safety rule?" |
| QCT-001 | "What does 'it' refer to, and which deadline do you mean?" | "Was what late?" without recording target slots |

## Over-eagerness traps

Prethinker should not ask in these cases:

| Case | Why no ask is expected |
|---|---|
| ICT-002 | Local pronoun is clear. |
| ICT-004 | Date resolves title holder. |
| ICT-010 | Source-attributed claim can be committed as claim, not fact. |
| ICT-011 | Conflict can be quarantined or flagged; no need to ask before refusing bad panel-finding write. |
| ICT-014 | Clear panel finding. |
| ICT-015 | Contractor-letter source claim can be committed as claim. |
| ICT-018 | Summary is safe if support links are preserved; if unsupported, commit as claim or summary candidate, not clarification. |
| QCT-011 | Multiple bindings are the correct answer. |
| QCT-014 | Broad answer can preserve the distinction: attached but not needed. |
| QCT-020 | Direct answer from admitted finding. |

## Under-eagerness traps

Prethinker should ask or block in these cases:

| Case | Why asking/blocking matters |
|---|---|
| ICT-001 | Wrong pronoun resolution creates a bad durable actor row. |
| ICT-003 | Same title held by two people creates identity collapse risk. |
| ICT-005 | "The rule" could refer to multiple charter rules. |
| ICT-007 | Correction has no clear old target. |
| ICT-009 | Exception scope could create a dangerous executable rule. |
| ICT-013 | "Valid claim" conflates opened, payable, approved, and supported-by-finding meanings. |
| ICT-016 | "Approved payment" conflates countersign, release, and approval semantics. |
| QCT-001 | "Was it late?" cannot be answered safely without object/deadline scope. |
| QCT-003 | Actor and object are both ambiguous. |
| QCT-019 | User appears to request a write, but source boundary is unclear. |

## Suggested CE scoring log

For this fixture, log at minimum:

```text
fixture_id
base_ce
effective_ce
ce_mode
ce_phase
clarification_requested_count
clarification_correct_count
clarification_overeager_count
clarification_undereager_count
safe_partial_commit_count
blocked_row_count
resumed_turn_success_count
query_clarification_count
```

Derived metrics:

```text
clarification_precision = correct / requested
clarification_recall = correct / should_have_asked
overeager_rate = overeager / requested
undereager_rate = missed_needed_clarifications / ambiguity_cases
safe_partial_rate = safe_partials_committed / clear_rows_available
resume_success_rate = resumed_turn_success / clarification_answers
```

## Suggested assertion/query outcome schema

If Codex builds a runner around this fixture, each case can be reduced to this shape:

```json
{
  "case_id": "ICT-001",
  "surface": "ingestion",
  "expected_behavior": "clarify",
  "blocked_slots": ["actor"],
  "safe_partials_expected": true,
  "must_not_commit": ["approved(_, repair_packet)"],
  "acceptable_question_contains": ["who", "she", "refer"]
}
```

For query cases:

```json
{
  "case_id": "QCT-001",
  "surface": "query",
  "expected_behavior": "clarify",
  "clarification_target": ["object", "deadline_scope"],
  "must_not_answer_as_fact": true
}
```

## Design principle

Clarification is not failure. A good clarification is an admission-control success: the system noticed that durable truth would require a choice it was not authorized to make.
