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

The new QA support map shows `8/20` first-20 questions have the required
symbolic support in the compiled KB. Of those, `7` became exact answers. The
remaining root-cause split is now visible: `12` compile-support gaps and `1`
query-planner miss despite available support.

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
- Some exact answers are still too forgiving: species and errand-sender answers
  can be judged exact even when the KB support is only character-level or has a
  predicate argument-order problem. The support map now catches that.

### Lesson

Otters is now a good frontier fixture precisely because it refuses to be solved
by a single prompt tweak. The current weak point is not one bug; it is the
interaction between source-wide compile coverage, stable atom choice across
passes, and QA query planning over a partially compiled KB.

## Run OTR-009 - Rotation Check After Iron Harbor Temporal Work

- Timestamp: `2026-04-30T13:46:14Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: first-20 QA rerun against the OTR-008 compile after Iron Harbor temporal
  query dependency-closure work.

### Headline

The story-world score stayed stable: `9 exact + 2 partial + 9 miss`, with
`20/20` rows producing queries and no write-proposal leaks.

### Lesson

The Iron Harbor temporal/query changes were scoped: they did not regress the
Otters source-fidelity path, but they also did not solve Otters' remaining
coverage problems. This is useful separation. Otters should keep pressure on
source-local entity/event coverage and prior-contamination resistance; Iron
Harbor should keep pressure on policy, temporal, and rule-substrate behavior.

## Run OTR-010 - Story QA Planner Hygiene After Harbor Work

- Timestamp: `2026-04-30T14:23:35Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: first-20 QA rerun against the OTR-008 compile after query-only
  set-difference work and story-world QA guidance tightening.

### Headline

The rerun reached `8 exact + 2 partial + 10 miss`. This is a small recovery from
an intermediate `7 exact + 1 partial` probe, but still below the OTR-008/009
high-water mark of `9 exact + 2 partial`.

### What Improved

- The species question now uses the compiled KB surface and reaches exact
  support by querying residents rather than failing with no query.
- Location and triad questions are at least querying plausible primitive
  predicates rather than leaking writes or invented composite predicates.
- Harbor-specific negative-query guidance did not create write leaks in the
  story-world QA path.

### What Failed

The remaining misses are mostly not answer-time bugs. They expose compile
coverage and atom-stability gaps:

- middle/great object ownership rows are missing or split across incompatible
  atoms;
- the home location is split between `willow_root_house` and
  `willow_tree_house`;
- the clockwork pie components, mint-gathering reason, pie-key, rules in the
  middle boat, and holes-in-boots support are absent or too indirect in the
  compiled KB;
- the planner still sometimes binds guessed atoms such as `boots_middle` or
  `boat_great` instead of first discovering canonical object rows.

### Lesson

Otters should not be solved by more answer-time prompt nudges. The next serious
move is compile-side: a source-local entity/object ledger and object-family
coverage pass that freezes canonical atoms before the event, ownership, design,
location, and final-state passes. That remains context choreography rather than
Python NLP.

## Run OTR-011 - Narrative Ledger Guidance Compile

- Timestamp: `2026-04-30T14:31:10Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: direct registry flat-plus-focused compile after adding stronger
  narrative compiler guidance for source-local ledger reuse and repeated
  object-family coverage.

### Headline

The compile admitted more structure (`94` operations) but first-20 QA landed at
`8 exact + 0 partial + 12 miss`. This is not an improvement over OTR-008/009.

### What Improved

The instruction did move one desired compile behavior: the new source compile
preserved more repeated object-family ownership rows, including middle/great
boot and mug ownership rows that earlier compiles often omitted.

### What Regressed

The same run destabilized other atom families:

- `willow_tree_house` and `willow_root_house` both appeared for the same home;
- `little_boat` and owner-prefixed boat atoms both appeared;
- some early household/location questions regressed even though object-family
  rows improved.

### Lesson

"Use a ledger" as prose guidance is not enough. The next architecture move
should be a separate LLM-authored `source_entity_ledger_v1` context artifact:
the model first proposes canonical characters, places, objects, object
families, aliases, and source-local atom names; later compile passes receive
that ledger and must reuse it. Python should not derive the ledger from prose;
it should only validate the structured ledger and pass it forward as context.

## Run OTR-012 - Experimental Source Entity Ledger

- Timestamp: `2026-04-30T14:40:00Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: opt-in prototype `source_entity_ledger_v1` pre-pass injected into
  flat-plus-focused compile context.

### Headline

The ledger pass itself was excellent, but the compile handoff is not yet good
enough. First-20 QA landed at `6 exact + 2 partial + 12 miss`, below the current
best.

### What Worked

The LLM-authored ledger found a strong source-local atom surface:

- `willow_root_house`
- `little_boat`, `middle_sized_boat`, `great_boat`
- `little_boots`, `middle_sized_boots`, `great_boots`
- `pie_key`
- `mint_sprig`
- `brass_wheels`
- `clockwork_pie`

It also produced useful object-family groups for mugs, boots, boats, and
knives.

### What Failed

The compiler used the ledger more consistently, but too timidly. It admitted
fewer total facts and still failed to emit enough ownership/design/component
coverage to improve QA. A follow-up prompt that explicitly told static passes
to cash in every ledger object family also failed to improve the compile.

### Decision

The mechanism is now kept behind an explicit `--source-entity-ledger` flag. It
is architecturally promising, but it should not become the default path until
the ledger-to-compile handoff demonstrably beats the simpler current pipeline.

## Run OTR-013 - Harbor Cross-Apply Recheck

- Timestamp: `2026-05-01T00:18Z` through `2026-05-01T00:37Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: direct story-world registry with the newer Harbor-style
  backbone-plus-detail compiler guidance, plus one optional
  `source_entity_ledger_v1` probe.

### Runs

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T001821386397Z_story_qwen-qwen3-6-35b-a3b.json`
  - first-20 QA: `8 exact / 1 partial / 11 miss`
  - support-map score: `4/20`
- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T002648305451Z_story_qwen-qwen3-6-35b-a3b.json`
  - first-20 QA: `6 exact / 2 partial / 12 miss`
- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T003502358556Z_story_qwen-qwen3-6-35b-a3b.json`
  - first-20 QA: `5 exact / 3 partial / 12 miss`

### Result

The Harbor-style context changes did not beat the current Otters high-water
mark. They improved some individual surfaces, such as taxonomy rows and errand
rows, but they also caused coverage tradeoffs: more static rows sometimes meant
less event/speech/judgment support, and the ledger path remained too timid.

### Lesson

Otters is now exposing a sharper frontier than simple guidance can solve:
source-local story worlds need an explicit ledger-to-compile contract with row
class floors or pass-specific completion checks. The model can build a strong
ledger, but the subsequent compile must be made to cash in that ledger across
typed/static/event/speech/judgment/final-state rows without Python interpreting
the prose.

## Run OTR-014 - Semantic Parallax 40-Question Baseline

- Timestamp: `2026-05-03T03:44Z` through `2026-05-03T03:52Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: current harness only, direct story-world registry, flat-plus-focused
  intake-plan compilation, compact focused-pass operations schema, and optional
  LLM-authored `source_entity_ledger_v1` context. No expected-Prolog guidance
  and no harness changes.

### Artifacts

- Compile:
  `tmp/otters_parallax_baseline/domain_bootstrap_file_20260503T034444202509Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/otters_parallax_baseline/domain_bootstrap_qa_20260503T035235817672Z_qa_qwen-qwen3-6-35b-a3b.json`
- Support score:
  `tmp/otters_parallax_baseline/20260503T035250372320Z_domain_bootstrap_file_20260503T034444202509Z_story_qwen-qwen3-6-35b-a3b_support.json`

### Result

The compile admitted `166` operations with `6` skips and produced `164` unique
facts, `0` rules, and `0` queries. Runtime loading was clean.

The first-40 QA baseline landed at:

- `17 exact`
- `4 partial`
- `19 miss`
- `40/40` parsed
- `40/40` rows with queries
- `0` write-proposal rows
- `0` runtime load errors

Failure-surface scoring over the first 40:

- `17` not applicable/exact rows
- `17` compile-surface gaps
- `3` query-surface gaps
- `3` answer-surface gaps

The existing support map covers the first 20 questions. On that slice, strict
support reached `9/20`; loose predicate/arity support reached `18/20`.

### Lesson

Semantic parallax substantially widened the admitted Otters surface compared
with earlier single-compile runs, but it did not automatically translate into a
dramatic QA jump. The first-40 result is now a current baseline for the richer
pipeline: the remaining bottleneck is split between compile-support coverage
and query/answer transfer over alternate but source-faithful predicate surfaces.

This is a stronger diagnostic position than the old first-20 score alone. The
next Otters move should be a true story-lens decomposition: ledger, static
object-family rows, event spine, speech/judgment, causality, and final-state
passes, each with a constrained output contract and deterministic admitted
union.

## Run OTR-015 - Post-Ingestion Evidence Filter Replay

- Timestamp: `2026-05-03T20:33Z`
- Evidence lane: `diagnostic_replay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: QA replay over the unchanged OTR-014 compile, with
  `evidence_bundle_plan_v1` and evidence-bundle context filtering enabled.
  The source was not recompiled, no gold KB or answer key entered the query
  planner, and QA write proposals remained disabled.

### Artifacts

- QA:
  `tmp/cold_baselines/otters_clockwork_pie/query_modes/domain_bootstrap_qa_20260503T203327073794Z_qa_qwen-qwen3-6-35b-a3b.json`
- Comparison:
  `tmp/cold_baselines/otters_clockwork_pie/query_modes/otters_query_mode_comparison.md`
- Selector:
  `tmp/cold_baselines/otters_clockwork_pie/query_modes/selector_direct_v1.json`

### Result

OTR-014 baseline:

```text
17 exact / 4 partial / 19 miss
```

Evidence-filter replay:

```text
22 exact / 5 partial / 13 miss
```

The replay rescued `9` baseline non-exact rows and caused `0` baseline-exact
regressions. Diagnostic perfect-selector upper bound:

```text
22 exact / 6 partial / 12 miss
```

The direct non-oracle selector selected:

```text
22 exact / 5 partial / 13 miss
selected best available mode on 39/40 rows
selector errors: 0
```

### Lesson

Otters now confirms that post-ingestion evidence access is not only a governance
fixture trick. A source-local story-world compile with many remaining
compile-surface gaps still gained substantially from better symbolic retrieval.

This does not erase the need for better story-lens compilation; `11` non-exact
rows still classify as compile-surface gaps. But it cleanly separates the
frontiers:

```text
story compile surface: still too thin for many causal/final-state questions
query surface: evidence filtering can recover answer support already present
activation surface: selector mostly follows the safer evidence mode, but misses
  one partial protection row
```
