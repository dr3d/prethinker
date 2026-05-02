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
