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

### IHR-004 - Direct Registry With Argument Contracts

Adding explicit `args` to `ontology_registry.json` and teaching direct registry
profiles to preserve those argument contracts lifted emitted/gold signature
recall to `0.929` and first-20 QA to `10 exact + 1 partial`.

This is the strongest current Iron Harbor run.

### Lesson

Domain packs need more than predicate names. They need predicate contracts.
For known domains, direct profile loading from a curated registry is cleaner
than asking the LLM to rediscover the palette every time. For unknown domains,
bootstrap remains useful, but the resulting profile should be reviewed and
contracted before it becomes a serious ingestion target.
