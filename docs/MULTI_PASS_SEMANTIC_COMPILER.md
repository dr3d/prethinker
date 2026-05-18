# Multi-Pass Semantic Compiler

Last updated: 2026-05-18

This document is the current doctrine for multi-pass compilation. Older
experiment logs and rule-lens run diaries were archived to
`C:\prethinker_tmp_archive\docs_markdown_sweep_20260518` and remain recoverable
through Git history.

## Current Thesis

A single LLM compile is one viewpoint. Prethinker should build a governed
artifact by accumulating multiple safe semantic views, but only after
deterministic admission:

```text
source
  -> deterministic source ledgers
  -> profile/context plan
  -> focused semantic passes
  -> mapper admission per pass
  -> deterministic safe-surface union
  -> QA over admitted state, ledgers, selectors, and guards
```

The invariant is unchanged:

```text
LLMs propose.
The mapper admits.
Only admitted clauses accumulate.
Python does not read prose to invent meaning.
```

## What A Pass May Do

A pass may propose a bounded semantic surface:

- backbone facts: entities, events, roles, statuses, quantities, dates;
- source/provenance rows: document roles, source labels, evidence status;
- temporal/status rows: intervals, supersession, deadlines, effective windows;
- rule rows: explicit source-stated conditions, exceptions, thresholds;
- epistemic rows: claims, disputes, retractions, unsupported or unstated facts;
- query-relevant source coordinates preserved by deterministic ledgers.

A pass may not become durable truth by itself. The mapper must still validate
schema shape, predicate palette, arity, argument roles, source status, safety,
profile contracts, and conflict/correction rules.

## Safe-Surface Accumulation

Safe union is deterministic. It operates over admitted structured rows, not raw
source prose and not answer keys:

```text
admitted facts
admitted rules
admitted queries
admitted retraction plans
deterministic ledgers
```

If a candidate surface helps one row but drops backbone rows, the result is a
compile-stability coordinate, not permission to replace the compiler. Current
work measures palette stability, row delivery collapse, vague event/detail
wrappers, stranded source-record values, and preservation of concrete
backbone rows before spending QA cycles.

## Rule And Derived-State Discipline

Executable rules are allowed only through the explicit rule path. A rule must:

- have a real `Head :- Body` shape;
- keep head variables bound in the body;
- use profile-approved predicates and deterministic runtime predicates;
- avoid claim-to-fact, permission-from-occurrence, and class-fanout collapse;
- pass isolated and dependency-composed promotion checks before being treated
  as promotion-ready;
- remain diagnostic until the product policy admits it as durable behavior.

Runtime predicates such as arithmetic, temporal comparison, interval overlap,
and threshold checks are deterministic substrate. They should compose admitted
rows; they should not smuggle source interpretation into Python.

## Compile-Stability Layer

The newest pressure is no longer "add another broad pass." It is whether the
compiler reliably emits the concrete rows that profiles and priors make
available.

Current stability checks ask:

- Did the compile preserve source-record ledgers and direct admitted facts?
- Did a candidate palette offer useful predicates that the compile failed to
  deliver as rows?
- Did vague `detail` or `event` wrappers appear while concrete backbone rows
  disappeared?
- Did multi-draw palette priors stabilize vocabulary without supplying facts,
  answers, or source authority?
- Did a repair transfer to unlike documents without fixture nouns, row ids,
  answer strings, or local organizations?

Multi-pass work is successful when it makes the compiled artifact sharper and
more reproducible. It is not successful merely because a new pass emits more
rows.

## Evidence Labels

Results should be labeled before comparison:

- `cold_unseen`: source-only run before tuning or profile help;
- `cold_after_general_architecture_change`: rerun after a generic change;
- `assisted_profile`: run with a non-oracle profile or palette prior;
- `oracle_calibration`: run with answer-shaped or gold material intentionally
  exposed for engineering;
- `regression_replay`: rerun to ensure a generic change did not rot existing
  behavior;
- `fixed_compile_qa`: QA-only rerun over frozen compile artifacts.

Do not compare `oracle_calibration` scores to cold generalization baselines.

## Current Lesson

The target is not one perfect compile. The target is a governed symbolic
artifact built from admitted semantic surfaces, deterministic source ledgers,
and measured query behavior. Each new pass must earn its place by adding a
transferable surface without weakening source fidelity or direct answerability.
