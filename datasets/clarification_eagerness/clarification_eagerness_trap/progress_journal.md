# Clarification Eagerness Trap Progress Journal

Fixture id: `clarification_eagerness_trap_v1`

This journal tracks CE behavior separately from ordinary compile/QA accuracy.

## CET-000 - Fixture Admission

Date: 2026-05-02

The fixture was promoted from `tmp/The Clarification Eagerness Trap` into
`datasets/clarification_eagerness/clarification_eagerness_trap/`.

Initial assets:

- source case file;
- clear answer key;
- 20 hand-authored ingestion CE cases;
- 20 hand-authored query CE cases;
- 10 baseline QA rows;
- expected aggregate behavior;
- machine-readable JSONL views of the authored case tables.

No model run has been scored yet.

## Immediate Harness Questions

- Can the runtime distinguish ask-worthy ambiguity from safe source-claim
  admission?
- Can clear partial rows commit while only blocked rows are held?
- Can query CE ask when the user question lacks scope, but return multiple
  bindings or a broad safe answer when that is the right behavior?
- Can CE be logged per run as precision/recall/overeager/undereager rather than
  just as a boolean `needs_clarification`?

## Current Lesson

CE needs to be measured as a frontier lane, not treated as a UI afterthought.

## CET-001 - First Full Structured-Output Baseline

Date: 2026-05-02

Run artifact: `tmp/clarification_eagerness_runs/cet-20260502T180353Z-both-40/`

Mode: full 40-case CE run with source context.

Result:

- `40/40` parsed.
- `30/40` correct.
- `4` over-eager asks.
- `3` under-eager misses.
- `3` unsafe candidates.

Lesson: the model understood many ask/no-ask boundaries, but CE could not be
measured by clarification count alone. The first scorer also needed to separate
posture errors from authority-surface errors such as unsafe write candidates.

## CET-002 - CE Policy Tightening

Date: 2026-05-02

Run artifact: `tmp/clarification_eagerness_runs/cet-20260502T180900Z-both-40/`

Result:

- `40/40` parsed.
- `36/40` correct.
- `2` over-eager asks.
- `1` under-eager miss.
- `1` unsafe candidate.
- `16/17` expected ask cases requested clarification.
- `20/23` expected no-ask cases avoided clarification.

Lesson: narrow policy guidance improved CE sharply. The main boundary moved from
"can it ask?" to "does it know when not to ask because source-claim/quarantine
is the right epistemic posture?"

## CET-003 - Balanced CE Posture

Date: 2026-05-02

Run artifact: `tmp/clarification_eagerness_runs/cet-20260502T181358Z-both-40/`

Result:

- `40/40` parsed.
- `36/40` correct.
- `2` over-eager asks.
- `2` under-eager misses.
- `0` unsafe candidates.
- `13/13` expected safe-partial cases preserved at least one safe partial.

Lesson: safe partial preservation can improve while ask/no-ask posture remains
imperfect. These are separate CE surfaces and should stay separate in metrics.

## CET-004 - High Recall Operating Point

Date: 2026-05-02

Run artifact: `tmp/clarification_eagerness_runs/cet-20260502T182513Z-both-40/`

Result:

- `40/40` parsed.
- `37/40` correct.
- `2` over-eager asks.
- `0` under-eager misses.
- `1` unsafe candidate under the then-current scorer.
- Clarification recall reached `17/17`.

Lesson: high recall is easy to buy by asking more often, but that is not the
same as good CE. This is a useful operating point, not the preferred headline.

## CET-005 - Perfect-Precision Posture Before Context-Write Scoring

Date: 2026-05-02

Run artifact: `tmp/clarification_eagerness_runs/cet-20260502T183559Z-both-40/`

Result:

- `40/40` parsed.
- `38/40` correct.
- `0` over-eager asks.
- `2` under-eager misses.
- `0` unsafe candidates under the pre-context-write scorer.
- Clarification precision reached `1.000`.

Lesson: the model can be made conservative enough to avoid over-eager asks, but
the run still needed stricter authority scoring: safe context-sourced writes
must be counted as violations even if the CE posture is otherwise plausible.

## CET-006 - Strict Authority-Aware Baseline

Date: 2026-05-02

Run artifact: `tmp/clarification_eagerness_runs/cet-20260502T185019Z-both-40/`

Result:

- `40/40` parsed.
- `37/40` correct under strict scoring.
- `0` over-eager asks.
- `2` under-eager misses.
- `1` unsafe candidate.
- `2` context-write violations.
- `15/17` ask-correct.
- `22/23` no-ask-correct.

Lesson: CE is now a real frontier metric. The remaining errors are not just
"ask more" or "ask less"; they are authority-boundary edge cases where the
model either performs an unsupported correction/retraction or copies
context-sourced status into candidate operations. The mapper must enforce this,
and the CE harness now measures it.

## CET-007 - Negative Hardening Control

Date: 2026-05-02

Run artifact: `tmp/clarification_eagerness_runs/cet-20260502T184550Z-both-40/`

Result:

- `35/40` correct.
- `1` over-eager.
- `1` under-eager.
- `3` unsafe candidates.
- `3` context-write violations.

Lesson: blunt prompt pressure saying "do not copy context rows" regressed the
model. The right fix is likely structural: mapper-side context-write rejection,
cleaner Semantic IR fields for context support versus candidate operations, and
pass-specific CE diagnostics, not more global prose.

## CET-008 - Context-Support Hygiene High-Water

Date: 2026-05-02

Run artifact: `tmp/clarification_eagerness_runs/cet-20260502T230526Z-both-40/`

Result:

- `40/40` parsed.
- `39/40` correct.
- `0` over-eager asks.
- `1` under-eager miss.
- `0` unsafe candidates.
- `0` context-write violations.
- `16/17` expected ask cases requested clarification.
- `23/23` expected no-ask cases avoided clarification.
- Clarification precision: `1.000`.
- Clarification recall: `0.941`.
- No-ask precision: `0.958`.

Changes:

- Added authored case-id filtering to the CE runner so weak cases can be
  replayed directly without a full 40-case GPU sweep.
- Tightened the source/context boundary for CE candidate operations: context
  role, status, title, alias, support, same-as, and rule-link rows belong in
  diagnostics/self-check, not safe candidate operations.
- Tightened source-claim posture: direct `source_claim` is the safe candidate
  surface; context-derived adoption or non-adoption status is diagnostic unless
  directly restated by the user.
- Tightened mixed safe-partial posture: if a blocked ambiguous status, payment,
  rule, correction, or approval slot could be clarified, include a targeted
  clarification question rather than only marking the blocked row unsafe.

Lesson: CE calibration improved most when the prompt described the authority
surface rather than saying "ask less" or "ask more." The high-water removed
context-write violations entirely while preserving perfect clarification
precision. The remaining miss was a safe partial plus unsafe blocked approval
without a clarification question.

## CET-009 - Variance Check After Alias Guard

Date: 2026-05-02

Run artifact: `tmp/clarification_eagerness_runs/cet-20260502T231602Z-both-40/`

Result:

- `40/40` parsed.
- `37/40` correct.
- `0` over-eager asks.
- `2` under-eager misses.
- `1` unsafe candidate.
- `0` context-write violations.
- Clarification precision: `0.933`.
- Clarification recall: `0.824`.

Lesson: the CE surface still has model-run variance even at `temperature=0.0`
with no thinking. Targeted replays fixed individual leaks, but the full-run
surface can shift. Treat CET-008 as the current high-water, not a guaranteed
floor. The next CE move should be a structural mapper/review diagnostic for
context-support rows and blocked-slot questions, not more one-line prompt
patches.

## CET-010 - Blocked-Slot Coverage Hardening

Date: 2026-05-03

Run artifact: `tmp/clarification_eagerness_runs/cet-20260503T031144Z-both-40/`

Result:

- `40/40` parsed.
- `40/40` correct.
- `0` over-eager asks.
- `0` under-eager misses.
- `0` unsafe candidates.
- `0` context-write violations.
- `17/17` expected ask cases requested clarification.
- `23/23` expected no-ask cases avoided clarification.
- `10/10` authored blocked-slot cases had a clarification surface.
- `0` blocked-slot safe-write violations.
- Clarification precision: `1.000`.
- Clarification recall: `1.000`.
- Blocked-slot question coverage: `1.000`.
- No-ask precision: `1.000`.

Changes:

- Added structural CE scorer metrics for authored blocked slots:
  `blocked_slot_question_required_count`,
  `blocked_slot_question_present_count`,
  `blocked_slot_question_missing_count`,
  `blocked_slot_safe_write_violation_count`, and
  `blocked_slot_question_coverage`.
- Kept the metric structural: Python reads fixture-authored `blocked_slots` and
  model-emitted Semantic IR fields. It does not infer ambiguity from prose.
- Tightened claim-surface scoring so `claim_content/2` is not mistaken for a
  forbidden fact commit when paired with a safe source-claim row.
- Tightened ICT-016's forbidden surface so a generic `approved/2` shortcut is
  caught as the same unsafe approval-semantics leak as
  `approved_payment/2`.
- Added CE context guidance that source-less safe event plus
  disputed/not-approved status needs a correction/source-claim/status
  clarification, and that blocked approval semantics must not emit generic
  approval rows as safe writes merely because a question was asked.

Lesson: the CE frontier moved from ask/no-ask posture into structural
authority-surface scoring. The high-water is no longer just "the model asked at
the right time"; it also checks whether authored blocked slots have an actual
clarification surface and whether a blocked slot leaked as a safe candidate
write. This matches the broader Prethinker pattern: better structure beats
asking the prompt to be more or less eager.

## CET-011 - No-Source-Context Regression Check

Date: 2026-05-03

Run artifact: `tmp/clarification_eagerness/cet-20260503T070059Z-both-40/`

Result:

- `40/40` parsed.
- `24/40` correct.
- `15` over-eager asks.
- `0` under-eager misses.
- `1` unsafe candidate.
- `0` context-write violations.
- `10/10` authored blocked-slot cases had a clarification surface.
- Clarification precision: `0.531`.
- Clarification recall: `1.000`.

Lesson:

This is a configuration/regime warning, not a prompt win/loss. Without source
context, the model asked for many details that the fixture source would have
supplied. The authority boundary held (`0` context-write violations), and
blocked-slot coverage stayed perfect, but no-ask precision collapsed. CE results
must therefore record whether fresh source/KB context was available.

## CET-012 - Source-Context Variance Check

Date: 2026-05-03

Run artifact: `tmp/clarification_eagerness/cet-20260503T070524Z-both-40/`

Result:

- `40/40` parsed.
- `40/40` correct.
- `0` over-eager asks.
- `0` under-eager misses.
- `0` unsafe candidates.
- `0` context-write violations.
- `17/17` expected ask cases requested clarification.
- `23/23` expected no-ask cases avoided clarification.
- `10/10` authored blocked-slot cases had a clarification surface.
- Clarification precision: `1.000`.
- Clarification recall: `1.000`.
- Blocked-slot question coverage: `1.000`.
- No-ask precision: `1.000`.

Lesson:

With source context included, CE returned to the CET-010 high-water. This
supports the ingestion-time CE theory: clarification eagerness should be judged
relative to the available authority surface. If the system has fresh source/KB
context, asking for already-supported details is over-eager. If it lacks that
context, the same question may be reasonable. Future CE reporting should label
context availability as part of the evidence lane.

## CET-013 - Source-Context Regression Check After Rule Work

Date: 2026-05-03

Run artifact: `tmp/clarification_eagerness_runs/cet-20260503T172239Z-both-40/`

Result:

- `40/40` parsed.
- `40/40` correct.
- `0` over-eager asks.
- `0` under-eager misses.
- `0` unsafe candidates.
- `0` context-write violations.
- `17/17` expected ask cases requested clarification.
- `23/23` expected no-ask cases avoided clarification.
- `10/10` authored blocked-slot cases had a clarification surface.
- Clarification precision: `1.000`.
- Clarification recall: `1.000`.
- Blocked-slot question coverage: `1.000`.
- No-ask precision: `1.000`.
- Safe partials were observed in `11/13` expected safe-partial cases.

Lesson:

The rule-admission and rule-lens changes did not disturb CE posture under the
source-context regime. Clarification eagerness remains stable when the authority
surface is available. The remaining diagnostic wrinkle is not ask/no-ask
behavior; it is safe-partial richness. Some cases correctly ask or avoid asking
while not preserving every expected safe partial row, so future CE work should
keep safe-partial coverage separate from clarification posture.

## CET-014 - Post-Selector Source-Context Sentinel

Date: 2026-05-03

Run artifact: `tmp/clarification_eagerness_runs/cet-20260503T185109Z-both-40/`

Result:

- `40/40` parsed.
- `40/40` correct.
- `0` over-eager asks.
- `0` under-eager misses.
- `0` unsafe candidates.
- `0` context-write violations.
- `17/17` expected ask cases requested clarification.
- `23/23` expected no-ask cases avoided clarification.
- `10/10` authored blocked-slot cases had a clarification surface.
- Clarification precision: `1.000`.
- Clarification recall: `1.000`.
- Blocked-slot question coverage: `1.000`.
- No-ask precision: `1.000`.
- Safe partials were observed in `11/13` expected safe-partial cases.

Lesson:

The non-oracle QA mode selector work did not disturb CE behavior. Under the
source-context regime, CE remains stable at the CET-010/CET-012/CET-013
high-water. Safe-partial richness remains the only visible wrinkle, so it should
continue to be tracked separately from ask/no-ask correctness.
