# Frontier Fixture Strategy

Last updated: 2026-05-03

This note describes what kinds of new fixtures should exercise Prethinker's
weaknesses next. It is not a score report. It is a design guide for generating
harder research inputs without leaking oracle answers into the compile path.

## Current Frontier

The current harness is strongest when a source can be compiled into a broad
safe symbolic surface and queried directly. The next fixtures should stress the
parts that are still brittle:

- executable rule composition, especially multi-step derived conditions;
- temporal arithmetic and temporal status changes;
- authority separation between committees, officers, panels, witnesses, and
  interpreters;
- clarification eagerness during ingestion and query;
- unresolved questions that must remain unresolved;
- correction handling where the corrected value does or does not change an
  outcome;
- query-surface mode selection without post-hoc oracle labels;
- stenographer-mode turn streams where only the current utterance plus prior
  admitted/pending state is visible;
- anti-meta-rot checks on cold fixtures that resemble prior successes only in
  abstract shape, not in surface vocabulary.

## Fixture Evidence Lanes

Every new fixture should declare its evidence lane before any run:

| Lane | Meaning |
| --- | --- |
| `cold_unseen` | Source plus QA only. No gold KB, registry, answer-shaped strategy, or expected Prolog in compile context. |
| `diagnostic_replay` | Rerun after a general harness change. Useful for checking transfer, not for claiming first-pass generality. |
| `assisted_domain_pack` | Uses a non-oracle domain pack prepared independently of the fixture text. Useful product-like lane. |
| `oracle_calibration` | Uses gold KB, expected predicates, or answer-shaped material on purpose. Useful for engineering ceilings, not public cold claims. |
| `hardened_variant` | A revised adversarial descendant of an older fixture. Useful for anti-overfit checks. |

The label is part of the result. Do not compare `oracle_calibration` scores to
`cold_unseen` scores as if they measure the same thing.

## Next Fixture Types

### 1. Rule-Composition Charter

Goal: test whether Prethinker can acquire intermediate derived conditions and
compose them into final outcomes without sibling-rule contamination.

Required ingredients:

- at least three rule branches that interact;
- one intermediate threshold condition;
- one exception branch;
- one priority or override branch;
- one final outcome that depends on the intermediate condition plus the
  exception or priority branch;
- authored positive and negative probes for each branch and for the final
  outcome.

Good questions:

- Which intermediate condition is met?
- Which exception blocks the otherwise valid rule?
- Which final status follows after priority resolution?
- Which tempting final status must not be derived?

Avalon Grant Committee is a good immediate candidate for this lane: eligibility
rules, formal interpretation authority, conditional approval, quorum, recusal,
and appeal finality all interact.

### 2. Clarification-In-The-Middle Fixture

Goal: test CE during source ingestion, not only after a query.

Required ingredients:

- an ambiguous identity, role, amount, or date inside the source;
- enough safe rows to partially admit;
- one unsafe candidate that must block pending clarification;
- one safe quarantine path where asking would be over-eager;
- one later correction or interpretation that resolves the ambiguity.

Good questions:

- What can be safely admitted before clarification?
- What must be held?
- What question should be asked?
- What answer becomes possible after the clarification?

This lane should score separately:

- ask/no-ask posture;
- safe partial preservation;
- blocked-slot question coverage;
- unsafe candidate count;
- context-write violation count.

### 2a. Stenographer-Mode Stream

Goal: test the same source as a sequence of incoming utterances, not as a
monolithic document.

Required ingredients:

- explicit turn order;
- some turns that can commit immediately;
- some turns that must create pending clarification before any mutation;
- at least one clarification answer several turns after the ambiguous source
  fragment in a controlled diagnostic variant;
- at least one queued clarification that should not interrupt immediately;
- one current-turn query boundary where setup and question arrive together;
- final QA that can be compared with a document-ingestion replay without
  merging the evidence lanes.

Good questions:

- What was safely admitted before the clarification?
- Which turn opened the pending slot?
- Which later turn closed it?
- Which question should be queued instead of asked immediately?
- Did the clarification answer mutate the original staged utterance rather than
  the answer text itself?
- Did sentence-at-a-time streaming preserve atom identity as well as document
  ingestion?

### 3. Temporal-Status Ledger

Goal: force durable state over time, not just point facts.

Required ingredients:

- at least five dated events;
- at least two intervals with start/end status;
- one correction replacing an old date or amount;
- one relative deadline;
- one business-day or calendar-day distinction;
- one answer requiring "status at time T" rather than current status.

Good questions:

- What was true on date D?
- Which deadline was missed?
- Which state was superseded?
- Which derived status changed after the correction?

### 4. Authority-Layer Dispute

Goal: preserve who has power to decide, interpret, appeal, certify, waive, or
override.

Required ingredients:

- at least three authority bodies;
- a statement by one body that is not binding;
- a formal interpretation by the correct authority;
- an appeal path with limited outcomes;
- a source claim that is not adopted as a finding.

Good questions:

- Who had authority to decide X?
- Was Y a final decision or merely a claim?
- Did the appeal body reverse, uphold, or remand?
- Which body could not hear the appeal?

### 5. Query-Mode Selector Fixture

Goal: test whether alternate query modes can be activated only when useful.

Required ingredients:

- rows answerable by baseline query path;
- rows requiring broader evidence bundles;
- rows where broader evidence introduces noise;
- rows where narrow evidence filtering rescues a miss;
- no answer-key access during selection.

Useful metric:

```text
selector_exact >= baseline_exact
selector_exact_regressions == 0
rescued_rows > 0
```

The current query-mode comparison report shows headroom, but its
perfect-selector counts are post-hoc. A real fixture should contain pre-judge
signals for when evidence expansion is justified.

### 6. Source-Local Story With Rule-Like Norms

Goal: keep the story-world lane alive without letting it become only recall.

Required ingredients:

- fictional objects and roles with no famous-template priors;
- explicit local norms or customs;
- at least one violated norm;
- speech versus narrator truth;
- final-state repair;
- one subjective judgment that must not become objective fact;
- one rule-like norm that should produce a queryable rule or derived condition.

Good questions:

- What did the narrator state as fact?
- What did a character merely say?
- Which local norm was violated?
- What final state changed?

### 7. Counterfactual Governance Fixture

Goal: answer hypothetical questions without writing hypothetical facts.

Required ingredients:

- a real outcome under current facts;
- at least two counterfactual branches;
- one counterfactual that changes procedure but not outcome;
- one counterfactual that changes outcome;
- one counterfactual blocked by an unresolved authority question.

Good questions:

- If condition C had held, what would change?
- Which facts remain unchanged?
- Which conclusion is only hypothetical?

## Fixture Quality Rules

New fixtures should be hostile, but clean:

- Source and QA must match.
- QA may contain expected answers, but answers are scoring material only.
- Do not include a gold KB for `cold_unseen` fixtures.
- If a gold KB exists, put it in an oracle lane and label it.
- Avoid answer-shaped strategy files for cold fixtures.
- Prefer 40-question batteries for fast cold baselines, then 100-question
  batteries when a lane becomes mature.
- Include enough row categories to diagnose failures: compile, query,
  hybrid/reasoning, answer, CE, rule-composition.
- Keep source-local names fresh so the harness cannot coast on prior fixtures.

## Difficulty Calibration

Fixtures should be difficult enough to expose failure structure, not so
difficult that every row collapses into one undiagnosed miss bucket.

For a new `cold_unseen` 40-question fixture, the ideal first baseline is roughly:

```text
exact: 40-60%
exact+partial: 55-75%
misses: enough to classify by surface
runtime/write safety: clean or nearly clean
```

Interpretation:

- `80%+` exact on the first cold run usually means the fixture is too easy or
  too close to an already-trained harness shape. Harden it or move it to a
  regression lane.
- `10-20%` exact can still be valuable, but it is usually a diagnostic stressor
  rather than a productive iterative benchmark. Use it to discover a missing
  substrate, not to tune prompts blindly.
- The best research fixtures produce mixed outcomes: some rows exact, some
  partial with useful evidence, some clear misses, and failures distributed
  across compile, query, hybrid/reasoning, answer, CE, or rule-composition
  surfaces.

If a fixture is too easy, harden it by adding interacting branches, temporal
status questions, unresolved authority questions, counterfactuals, or
near-miss negative cases. If it is too hard, split it into a smaller focused
fixture so the first failure gradient is visible.

## Cross-Fixture Replay Protocol

A general harness change should not be trusted because it improves one active
fixture. It should survive regression replay.

Use this protocol after changes to any general component:

- semantic lens planning;
- source-pass output schema or retry policy;
- mapper admission policy;
- helper predicates or temporal substrate;
- rule verifier or promotion filtering;
- post-ingestion query planning or evidence-bundle selection;
- answer/judge normalization.

Minimum replay:

```text
1. Active target fixture.
2. One cold fixture from a different domain shape.
3. One older high-water fixture that previously looked strong.
4. One known weak fixture whose failures should not be hidden.
```

Preferred replay, when GPU time allows:

```text
all admitted cold_unseen fixtures
+ Glass Tide rule probes
+ Clarification Eagerness hard set
+ APR or Iron Harbor high-water regression checks
```

Regressions on previously passing rows should be treated as bugs or documented
tradeoffs, not silently accepted as the cost of improving the current fixture.
If a change helps one fixture but hurts another, record the result as
`diagnostic_replay`, classify the regression surface, and decide whether the
change needs a selector, guard, or narrower activation condition.

## Current Recommendation

Use Avalon Grant Committee as the immediate rule-composition baseline. It should
stress:

- prior-grant waiting-period rules;
- formal interpretation overriding naive text reading;
- conditional approval plus deadline satisfaction;
- quorum and recusal arithmetic;
- appeal body separation;
- counterfactual procedure versus substantive outcome.

Then run Ridgeline Fire as an anti-overfit replay for rule/deadline/authority
logic, because it is adjacent to Iron Harbor but not the same fixture.

After Avalon and Ridgeline, generate one fixture that is deliberately CE-heavy
during ingestion, and one fixture that is temporal-status-heavy with
business-day and calendar-day windows. That gives four complementary pressure
tests instead of over-baking one story family.
