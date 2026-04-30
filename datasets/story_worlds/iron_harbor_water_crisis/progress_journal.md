# Iron Harbor Water Crisis Progress Journal

## 2026-04-29 - Dataset Integration

- Integrated source story, QA battery, reference KB, and strategy notes from `tmp/The Iron Harbor Water Crisis`.
- Normalized text files to ASCII for fixture stability while retaining source-provided answers and translations.
- Added starter failure buckets and an ontology registry derived from the reference KB.

## TODO

- Run the reference KB through the deterministic Prolog layer and record baseline QA coverage.
- Run source-only story ingestion and compare admitted predicates against `ontology_registry.json`.
- Add progress rows after each benchmark attempt; do not rewrite historical rows.

## 2026-04-30 - Run IHR-001 - Registry-Guided Baseline

- Model: `qwen/qwen3.6-35b-a3b`
- Mode: profile bootstrap with `ontology_registry.json` supplied as a candidate
  predicate roster, followed by source compile and first-20 QA.

### Headline

Safe and parseable, but too thin.

The compile run parsed cleanly and admitted `64` candidate operations with only
`2` skips. Profile rough score was `0.880`. However, emitted/gold predicate
signature recall was only `0.036`, which means the model mostly avoided the
fixture's intended municipal-policy predicate surface.

First-20 QA reached `8 exact + 1 partial + 11 miss`. That is a useful baseline:
the system can answer some direct timeline and policy questions, but the KB
surface is not yet rich enough for a serious Iron Harbor interrogation.

### Lesson

Iron Harbor is not mainly a free-form story problem. It needs stronger
compile-time pressure toward policy clauses, temporal deadlines, notification
scope, authorization validity, correction records, and claim/finding separation.
The next improvement should come from context choreography and predicate-roster
selection, not Python reading the source text.

## 2026-04-30 - Runs IHR-002 through IHR-004 - Profile Shape and Contracts

### IHR-002 - Policy/Incident Context Profile Discovery

Adding a policy/incident compiler strategy improved profile shape but hurt QA.
The profile became prettier (`rough_score=1.000`, no generic predicates), yet
it replaced many registry predicates with generic-but-plausible surfaces such as
`policy_rule/3`, `measurement/4`, `deadline/3`, and `advisory_status/3`.

That produced a useful failure lesson: profile score is not enough. A profile
can be internally coherent and still drift away from the domain's intended
query surface.

### IHR-003 - Direct Registry Profile

Using the registry directly changed the picture. Emitted/gold signature recall
jumped to `0.857`, and first-20 QA rose to `8 exact + 2 partial`.

The failure mode also changed: the model now used the right predicates, but the
registry had only signatures and no argument contracts, so several emitted facts
had unstable slot order.

### IHR-004 - Direct Registry After Adding Argument Contracts

Adding explicit `args` to `ontology_registry.json` coincided with emitted/gold
signature recall rising to `0.929` and first-20 QA to `10 exact + 1 partial`.
Later inspection showed the registry loader was still stripping those `args`, so
this run should be read as a predicate-surface improvement, not as proof that
argument contracts were active yet.

This was the strongest Iron Harbor run at the time.

### Lesson

Domain packs need more than predicate names. They need predicate contracts.
For known domains, direct profile loading from a curated registry is cleaner
than asking the LLM to rediscover the palette every time. For unknown domains,
bootstrap remains useful, but the resulting profile should be reviewed and
contracted before it becomes a serious ingestion target.

## 2026-04-30 - Run IHR-005 - Placeholder-Normalized QA

Rerunning QA over the IHR-004 compiled KB after structural query-placeholder
normalization raised first-20 QA to `12 exact + 2 partial`.

The improvement came from treating model-emitted lowercase slot labels such as
`reading`, `mode`, `interval`, `zone`, `facility`, and `noticeid` as variables
inside query operations. This is not Python prose interpretation; it is cleanup
of structured query arguments after the model has already emitted a proposed
query.

### Current Remaining Edges

- Pre-correction values need a parked-claim/source-record predicate. The current
  compiled KB preserves authoritative corrected values better than superseded
  claims.
- Advisory status needs stricter argument-contract adherence; the model still
  sometimes uses `contamination_advisory/2` as `(subject, status)` instead of
  `(status, timestamp)`.
- Offline-duration and omitted-zone questions need either better multi-query QA
  planning or a small admitted rule layer for derived answers.

### Rejected Attempt

A heavier policy/incident QA strategy was tried and dropped because it reduced
first-20 QA to `9 exact + 1 partial`. More instructions are not automatically
better; the sharper win was keeping the context lean and improving structured
query argument handling.

## 2026-04-30 - Run IHR-006 - Contract-Adherence Guidance

Adding one concise compile instruction that predicate contracts are binding
raised first-20 exact QA to `13/20`. The compile admitted more rows (`123`) with
fewer skips (`4`) while preserving emitted/gold signature recall at `0.929`.

This is the strongest exact-answer Iron Harbor run so far.

### New Hard Edge

The remaining errors show a deeper contract problem: valid arity is not enough.
For example, the model can still emit a `contamination_advisory/2` clause with
the right arity but wrong argument roles. That suggests the next architectural
move should be mapper-side contract diagnostics or typed role checks: detect
contract-wrong operations, explain why they were skipped, and keep them out of
the durable KB. That is governance, not Python NLP.

## 2026-04-30 - Run IHR-007 - Preserved Argument Contracts

The registry loader now preserves `args` from `ontology_registry.json`, and the
contract gate now recognizes temporal role names such as `timestamp`,
`authorized_at`, `issued_at`, `taken_at`, and `inspected_on`.

Result:

- emitted/gold signature recall: `0.964`
- first-20 QA: `16 exact + 1 partial`
- malformed advisory clauses such as `contamination_advisory(intake_point_alpha, triggered)` were replaced by clean clauses such as `contamination_advisory(triggered, 2026_03_04t02_00)`

### Lesson

This is the cleanest Iron Harbor run so far, and it confirms the next design
principle: predicate contracts must travel with the profile, and the mapper
should enforce obvious structural contract roles. Otherwise the system can have
the right predicate name and still write a wrong fact.
