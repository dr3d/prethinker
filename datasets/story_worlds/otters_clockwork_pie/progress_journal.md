# Otters Story-World Progress Journal

This is the side ledger for making Prethinker increasingly good at the
`The Three Otters and the Clockwork Pie` benchmark.

The point is not to cherry-pick polished runs. The point is to keep visible
numbers as the system moves from shallow safe extraction toward source-faithful,
queryable narrative logic.

## Run OTR-001 - Cold Current Pipeline Baseline

- Timestamp: `2026-04-30T01:27:58Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: raw story -> intake plan -> profile bootstrap/review/retry -> source
  compile by LLM-authored plan passes -> QA first 20
- Expected Prolog was used only for after-the-fact signature comparison. It was
  not used as profile guidance.
- Local compile artifact:
  `tmp/domain_bootstrap_file/domain_bootstrap_file_20260430T012758919267Z_story_qwen-qwen3-6-35b-a3b.json`
- Local QA artifact:
  `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260430T013055910737Z_qa_qwen-qwen3-6-35b-a3b.json`

### Headline

Safe-ish and structured, but not yet a real story-world reasoner.

The run discovered a plausible profile and admitted many facts, but it did not
produce the event/temporal/causal/final-state reasoning surface needed for the
QA battery. This is a good first ugly dot on the graph.

### Compile Metrics

| Metric | Value |
| --- | ---: |
| Parsed profile JSON | `true` |
| Profile rough score | `0.778` |
| Candidate predicates | `25` |
| Generic predicates | `0` |
| Repeated structures | `3` |
| Admission risks | `5` |
| Source compile admitted ops | `96` |
| Source compile skipped ops | `4` |
| Unique facts | `91` |
| Unique rules | `0` |
| Unique queries | `0` |
| Emitted predicate signatures | `15` |
| Expected gold signatures | `113` |
| Emitted/gold signature recall | `0.000` |

### QA First-20 Metrics

| Metric | Value |
| --- | ---: |
| Questions | `20` |
| Parsed query workspaces | `20/20` |
| Query rows attempted | `20/20` |
| Judge exact | `7` |
| Judge partial | `0` |
| Judge miss | `13` |
| Exact rate | `0.350` |
| Runtime load errors | `0` |
| Proposed writes during QA | `0` |

### What It Got Right

- Did not collapse the story into bears/porridge/chairs/beds in the compiled KB.
- Produced a source-local cast: Little Slip, Middle-sized Otter, Great Long
  Otter, Tilly, aunt, clockwork pie, boats, boots, mugs.
- Captured some ownership and object inventory.
- Captured some speech acts as `reported_speech/3`.
- Captured some internal-state/remediation facts.

### What Failed

- No durable event ledger: no `event/5`-style spine and no stable `story_time/2`.
- No real temporal reasoning surface: no admitted ordering graph equivalent to
  the gold KB.
- No causal layer rich enough for "why did X happen?" questions.
- No final-state model strong enough to distinguish "happened during the story"
  from "true after repair."
- Predicate surfaces drifted away from the reference KB, making QA query planning
  fragile.
- Several first-20 questions failed because the compiled KB lacked direct
  house-membership, location, errand, or object-component support in the shapes
  the QA planner could query.

### Next Hypotheses

1. Add narrative-source context pressure that asks the model for an event ledger,
   temporal anchors, causal consequences, and final-state updates when the
   source type is a closed story or fable.
2. Keep the fix as context engineering. Do not add Python phrase handling or
   story-specific extraction rules.
3. Track progress with both compile metrics and QA metrics; QA is the harder,
   more honest signal.
4. Add phase-level QA scoring after the first full 100-question run so we can see
   whether improvements are coming from entity/object facts, chronology,
   causality, speech/truth, or final-state modeling.

## Run OTR-002 - Narrative Context Pressure

- Timestamp: `2026-04-30T01:38:51Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: same as OTR-001, plus generic narrative-source compiler pressure from
  the LLM-owned intake classification/domain hint.
- Expected Prolog was used only for after-the-fact signature comparison. It was
  not used as profile guidance.
- Local compile artifact:
  `tmp/domain_bootstrap_file/domain_bootstrap_file_20260430T013851541293Z_story_qwen-qwen3-6-35b-a3b.json`
- Local QA artifact:
  `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260430T014129252648Z_qa_qwen-qwen3-6-35b-a3b.json`

### Headline

Small but real movement: profile shape improved and QA exact moved from `7/20`
to `9/20`.

The model now tries to build chronology, causality, speech, evaluations, and
state facts. The remaining failure is mostly canonical predicate drift and a
still-too-thin event ledger.

### Compile Metrics

| Metric | OTR-001 | OTR-002 |
| --- | ---: | ---: |
| Parsed profile JSON | `true` | `true` |
| Profile rough score | `0.778` | `0.889` |
| Candidate predicates | `25` | `22` |
| Generic predicates | `0` | `0` |
| Repeated structures | `3` | `2` |
| Admission risks | `5` | `4` |
| Source compile admitted ops | `96` | `71` |
| Source compile skipped ops | `4` | `2` |
| Unique facts | `91` | `63` |
| Unique rules | `0` | `0` |
| Unique queries | `0` | `0` |
| Emitted predicate signatures | `15` | `16` |
| Expected gold signatures | `113` | `113` |
| Emitted/gold signature recall | `0.000` | `0.000` |

### QA First-20 Metrics

| Metric | OTR-001 | OTR-002 |
| --- | ---: | ---: |
| Questions | `20` | `20` |
| Parsed query workspaces | `20/20` | `20/20` |
| Query rows attempted | `20/20` | `20/20` |
| Judge exact | `7` | `9` |
| Judge partial | `0` | `0` |
| Judge miss | `13` | `11` |
| Exact rate | `0.350` | `0.450` |
| Runtime load errors | `0` | `0` |
| Proposed writes during QA | `0` | `0` |

### What Improved

- Profile rough score improved by `0.111`.
- The profile became less generic while adding event/order/state vocabulary.
- The compile emitted `happens_before/2`, `results_in/2`, `entity_state/3`,
  `says/3`, and `evaluates_as/3`, showing the model understood the needed
  story-world layers.
- QA exact rate improved by `0.100`.

### What Still Failed

- Predicate canonicalization drift remains severe: the model understood the
  semantic role but chose near-synonyms such as `happens_before/2` instead of
  `before/2`, `says/3` instead of `said/3`, and `evaluates_as/3` instead of
  `judged/4`.
- The event ledger is still skeletal. It has ordering relations, but not a
  stable `event/5` plus `story_time/2` spine.
- Final-state and repair semantics are present only as shallow remediation
  facts, not as durable current-state support.

### Next Hypotheses

1. Add a generic story-world predicate convergence module: event spine,
   story-time, source-local cast, speech, subjective judgment, causality,
   ownership/design, and final-state predicates.
2. Treat that module as a selectable context profile, not a Python prose parser.
3. Add benchmark metadata and integrity checks so QA misses can be attributed to
   entity, chronology, speech/truth, causality, or final-state failures.

## Run OTR-003 - Canonical Story-World Predicate Pressure

- Timestamp: `2026-04-30T01:47:16Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: OTR-002 plus canonical story-world predicate pressure for event spine,
  speech, judgment, ownership, locations, causality, and final states.
- Expected Prolog was used only for after-the-fact signature comparison. It was
  not used as profile guidance.
- Local compile artifact:
  `tmp/domain_bootstrap_file/domain_bootstrap_file_20260430T014716942112Z_story_qwen-qwen3-6-35b-a3b.json`
- Local QA artifact:
  `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260430T014954807164Z_qa_qwen-qwen3-6-35b-a3b.json`

### Headline

The run traded breadth for reference alignment. That is useful.

The profile became smaller and rough score dipped, but emitted/gold predicate
signature recall finally moved from `0.000` to `0.097`, with emitted signature
precision at `0.688`. QA exact dipped from `9/20` to `8/20`, but partials rose
from `0` to `3`, so exact+partial support improved to `11/20`.

### Compile Metrics

| Metric | OTR-001 | OTR-002 | OTR-003 |
| --- | ---: | ---: | ---: |
| Parsed profile JSON | `true` | `true` | `true` |
| Profile rough score | `0.778` | `0.889` | `0.833` |
| Candidate predicates | `25` | `22` | `17` |
| Generic predicates | `0` | `0` | `0` |
| Repeated structures | `3` | `2` | `1` |
| Admission risks | `5` | `4` | `4` |
| Source compile admitted ops | `96` | `71` | `96` |
| Source compile skipped ops | `4` | `2` | `2` |
| Unique facts | `91` | `63` | `93` |
| Unique rules | `0` | `0` | `0` |
| Unique queries | `0` | `0` | `0` |
| Emitted predicate signatures | `15` | `16` | `16` |
| Expected gold signatures | `113` | `113` | `113` |
| Emitted/gold signature recall | `0.000` | `0.000` | `0.097` |
| Emitted/gold signature precision | `0.000` | `0.000` | `0.688` |

### QA First-20 Metrics

| Metric | OTR-001 | OTR-002 | OTR-003 |
| --- | ---: | ---: | ---: |
| Questions | `20` | `20` | `20` |
| Parsed query workspaces | `20/20` | `20/20` | `20/20` |
| Query rows attempted | `20/20` | `20/20` | `20/20` |
| Judge exact | `7` | `9` | `8` |
| Judge partial | `0` | `0` | `3` |
| Judge miss | `13` | `11` | `9` |
| Exact rate | `0.350` | `0.450` | `0.400` |
| Exact + partial rate | `0.350` | `0.450` | `0.550` |
| Runtime load errors | `0` | `0` | `0` |
| Proposed writes during QA | `0` | `0` | `0` |

### What Improved

- The profile emitted canonical predicates such as `event/5`, `story_time/2`,
  `before/2`, `causes/2`, `said/3`, `judged/4`, `owned_by/2`,
  `initial_location/2`, `location_after_event/3`, and
  `condition_after_event/3`.
- The compiled KB now has a recognizable event spine rather than only isolated
  object/state facts.
- Signature precision against the reference style reached `0.688`.

### What Still Failed

- The profile review pass introduced an archetype label (`Goldilocks pattern`)
  absent from the source; the retry profile then used `goldilocks_trial` as a
  repeated-structure name. It did not become a durable fact, but profile
  vocabulary should also remain source-local.
- The event spine is still sparse and uneven. Many source events remain omitted.
- The model aligned with reference predicate families but did not yet recover
  enough event detail for high exact QA support.

### Next Hypotheses

1. Tighten profile-review guidance so review/retry suggestions cannot import
   famous-story archetype labels absent from the source.
2. Keep canonical pressure, but ask for source-local repeated-structure names
   such as `threefold_fit_trial` instead of external template labels.
3. Add source-fidelity checks for profile vocabulary, not only admitted facts.

## Run OTR-004 - Source-Local Retry Guard

- Timestamp: `2026-04-30T01:54:20Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: OTR-003 plus retry safety language requiring external archetype labels
  to be translated into source-local repeated-structure names.
- Expected Prolog was used only for after-the-fact signature comparison. It was
  not used as profile guidance.
- Local compile artifact:
  `tmp/domain_bootstrap_file/domain_bootstrap_file_20260430T015420696045Z_story_qwen-qwen3-6-35b-a3b.json`
- Local QA artifact:
  `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260430T015703092852Z_qa_qwen-qwen3-6-35b-a3b.json`

### Headline

Useful negative result: source-locality improved, but the profile became timid.

The repeated structure was renamed to `fit_trial`, but external-archetype wording
still appeared in review/risk prose, and QA fell to `5 exact + 2 partial`.

### Metrics

| Metric | OTR-003 | OTR-004 |
| --- | ---: | ---: |
| Profile rough score | `0.833` | `0.833` |
| Candidate predicates | `17` | `11` |
| Source compile admitted ops | `96` | `55` |
| Source compile skipped ops | `2` | `1` |
| Unique facts | `93` | `55` |
| Emitted/gold signature recall | `0.097` | `0.044` |
| Emitted/gold signature precision | `0.688` | `0.455` |
| QA exact | `8/20` | `5/20` |
| QA partial | `3/20` | `2/20` |
| QA exact + partial | `11/20` | `7/20` |

### Lesson

The source-local guard needs to prevent absent external labels everywhere in the
control plane, but it must not collapse the predicate palette. A clean profile
that cannot answer the story is not progress.

## Run OTR-005 - Source-Local Plus Coverage Pressure

- Timestamp: `2026-04-30T02:03:06Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: OTR-004 plus explicit coverage pressure: preserve cast/entity taxonomy,
  ownership/design, locations, event spine, order, speech, judgment, causality,
  remediation, and final state when source/profile support them.
- Expected Prolog was used only for after-the-fact signature comparison. It was
  not used as profile guidance.
- Local compile artifact:
  `tmp/domain_bootstrap_file/domain_bootstrap_file_20260430T020306269071Z_story_qwen-qwen3-6-35b-a3b.json`
- Local QA artifact:
  `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260430T020558861331Z_qa_qwen-qwen3-6-35b-a3b.json`

### Headline

Coverage came back, but synonym drift came with it.

The run admitted more facts than any previous pass (`102`), but profile rough
score dropped to `0.722` and a starter frontier case drifted back to `says/3`
instead of the canonical `said/3`. QA landed at `8 exact + 2 partial`, below
OTR-003's best exact+partial score.

### Metrics

| Metric | OTR-003 | OTR-004 | OTR-005 |
| --- | ---: | ---: | ---: |
| Profile rough score | `0.833` | `0.833` | `0.722` |
| Candidate predicates | `17` | `11` | `15` |
| Source compile admitted ops | `96` | `55` | `102` |
| Source compile skipped ops | `2` | `1` | `2` |
| Unique facts | `93` | `55` | `99` |
| Emitted/gold signature recall | `0.097` | `0.044` | `0.062` |
| Emitted/gold signature precision | `0.688` | `0.455` | `0.467` |
| QA exact | `8/20` | `5/20` | `8/20` |
| QA partial | `3/20` | `2/20` | `2/20` |
| QA exact + partial | `11/20` | `7/20` | `10/20` |

### Current Best

OTR-003 is still the best balanced point:

- strongest emitted/gold signature recall so far: `0.097`
- strongest emitted/gold signature precision so far: `0.688`
- strongest first-20 exact+partial QA support so far: `11/20`

### Next Hypotheses

1. The next improvement should not add more generic prose. It should use the
   fixture's ontology registry as a profile candidate roster so the model can
   choose from source-relevant canonical predicates without seeing target facts.
2. Add mechanical source-fidelity diagnostics for control-plane output: no
   absent external tale names in profile review, retry guidance, profile risks,
   repeated-structure names, or starter cases.
3. Add phase-level QA scoring so we can see whether OTR-003's gains came from
   entity/static facts, chronology, speech, causality, or final state.

## Run OTR-006 - Registry-Guided Profile Discovery

- Timestamp: `2026-04-30T02:24:13Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: profile bootstrap with `ontology_registry.json` provided as a candidate
  predicate roster. The registry supplied vocabulary only, not source facts or
  expected answers.

### Headline

Big compile win, disappointing QA transfer.

Profile rough score reached `0.944`, emitted/gold signature recall reached
`0.195`, and emitted/gold precision reached `0.917`. That is the best compile
alignment so far by a lot. First-20 QA, however, fell to `6 exact + 1 partial`.

### Lesson

Registry-guided discovery solves a large part of predicate drift, but it does
not automatically solve coverage or query planning. The model can choose much
better predicate surfaces and still omit support needed for early QA questions.

## Run OTR-007 - Direct Registry Profile

- Timestamp: `2026-04-30T02:30:35Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: bypass profile rediscovery and use `ontology_registry.json` directly as
  the draft profile palette.

### Headline

Direct registry mode is precise but too broad.

The profile exposed all `113` registry predicates. Emitted/gold precision reached
`1.000`, but recall landed at `0.150`, compile coverage fell to `68` facts, and
QA reached only `7 exact + 2 partial`.

### Lesson

A giant predicate menu is not enough. The model needs a narrowed working subset
or profile plan, not every possible story-world predicate at once.

## Run OTR-006Q - Query Strategy Rerun

- Timestamp: `2026-04-30T02:37:03Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: rerun QA over OTR-006's compiled KB after adding generic story-world QA
  query guidance.

### Headline

Query prompting alone did not rescue the run.

Exact rose from `6` to `7`, but the single partial was lost. Net exact+partial
support stayed `7/20`.

### Current Read

The fastest path upward is now clearer:

1. Use registry-guided profile discovery, not direct full-registry mode.
2. Improve compile coverage for early QA support: setting, kind/species,
   location, errand, intended-user, event, and final-state facts.
3. Add phase-level scoring so we stop treating all misses as one blob.

## Run OTR-006R - Placeholder-Normalized QA Rerun

- Timestamp: `2026-04-30T02:43:59Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: rerun QA over OTR-006's compiled KB after normalizing generic query
  placeholder constants such as `owner`, `character`, `speaker`, and
  `consequence` into Prolog variables.

### Headline

Small query-surface cleanup helped, but did not change the main diagnosis.

Exact first-20 QA support rose from `7/20` to `8/20`. The run still missed
`12/20`, mostly because the compiled KB does not yet carry enough early-story
support for setting, errand, designed-for ownership, and event-spine questions.

### Lesson

Structural query placeholder normalization is useful, but the next large gain
must come from better model-authored compile coverage. We should keep pushing
context choreography and predicate-roster pressure rather than adding Python
language patches.

## Run OTR-008 - Direct Registry Flat Plus Focused Passes

- Timestamp: `2026-04-30T12:20:03Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: direct `ontology_registry.json` profile, flat-plus-focused intake
  passes, generic narrative source-fidelity guidance, and mapper scratch-text
  hygiene.

### Headline

Best balanced first-20 QA result so far under the lean current pipeline:
`9 exact + 2 partial = 11/20`.

Compile admitted `82` operations with `0` skips, emitted/gold signature recall
reached `0.292`, and precision stayed `1.000`. This does not beat the best
one-off compile recall observed during exploratory runs, but it ties the best
exact-only QA result and ties the best exact+partial support while keeping the
mapper cleaner.

### What Improved

- Early inventory questions finally landed better: little mug, middle boots,
  great boat, and boat location all reached exact answers.
- Food extraction improved enough for exact answers to the bake/ingredient
  questions.
- The mapper now blocks obvious model scratch-text leakage from becoming durable
  facts. This is structural admission hygiene, not prose preprocessing.

### Remaining Misses

- Species/kind support is still not transferred reliably into QA.
- Errand sender/items regressed in this run even though earlier runs handled
  them.
- The half-birthday and swallowed-wheel support remains thin.
- Query planning still misses some available support and sometimes asks overly
  narrow predicates.

### Lesson

Otters is now a good frontier fixture precisely because it refuses to be solved
by a single prompt tweak. The current weak point is not one bug; it is the
interaction between source-wide compile coverage, stable atom choice across
passes, and QA query planning over a partially compiled KB.
