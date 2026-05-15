# Boundary Probe Research Method

Last updated: 2026-05-12

This note is internal research doctrine for future CTO/Codex work. It describes
how to use fixtures, the completed guard-compression archive, helper pressure,
and diagnostics to characterize what Prethinker can and cannot currently
quantize.

Here, **quantize** means: preserve answer-bearing source meaning as named,
queryable, auditable coordinates rather than as opaque prose, fixture-local
helper behavior, or selector luck. It does not mean "capture all meaning."

It is not a public claim that Prethinker captures "meaning" in full. The safer
claim is narrower and more useful:

```text
Prethinker projects source language into a named coordinate system. The
research target is to characterize which source meanings land cleanly in that
system, which remain diagnostic residue, and which boundary cases reveal a
missing coordinate.
```

## Working Metaphor

Think of Prethinker as a boundary hunt.

This is a working metaphor, not a claim that language has a crisp mathematical
edge. The useful question is where the current instrument behaves as if a source
meaning has a stable coordinate, and where it visibly loses, blurs, or quarantines
that meaning.

Each compile projects natural language into structured coordinates:

- predicate and arity;
- source envelope and source addressability;
- temporal anchor;
- epistemic state;
- authority and provenance;
- helper/support-kind surfaces;
- selector and guard behavior;
- diagnostics, quarantine, and residue.

In this document, a **coordinate** is one of those concrete system surfaces: a
predicate contract, helper/support-kind row, source-record address, scoring
principle, diagnostic, guard, scar, or quarantine event. It is not an abstract
semantic truth floating outside the artifact.

Meaning that lands cleanly in named coordinates, with provenance and the right
epistemic envelope intact, is inside the current Prethinker set: durable,
governable, and queryable.

Meaning that does not land cleanly is outside or at the edge. It may remain as
source text, diagnostic residue, helper pressure, selector uncertainty, a guard,
or a clarification/quarantine event.

The research target is the boundary, not the easy interior.

## Why This Matters Now

When the selector surface had roughly 190 fixture-shaped guards, the boundary
was hard to see. Everything looked like a hole.

After compression into named semantic families and reusable scoring principles,
the current set has shape. The shape makes incompleteness visible. Remaining
guards, scars, helper-pressure rows, and diagnostics are no longer just cleanup
work; they are observations about where the coordinate system is thin.

The goal is not zero guards. Some stable singletons may be legitimate boundary
sentinels. The goal is:

```text
No hidden fixture vocabulary. No row IDs or story nouns as architecture. Every
remaining guard either generalizes, scars, or earns a keeper rationale.
```

## Probe, Do Not Randomly Ingest

New fixtures should be designed as probes, not random documents.

Before running a fixture, write the prediction:

```text
This fixture should stress <axis> because current architecture does not yet
distinguish <X> from <Y>.
```

Examples:

- authority/provenance boundary: document status versus actual governing
  authority;
- temporal boundary: current state versus historical state versus correction;
- rationale boundary: explanation surface versus adjacent operational status;
- source-addressability boundary: exact source row needed but semantic
  predicate is too broad;
- grid-fit boundary: source meaning exists but no current predicate/helper axis
  can name it.

After the run, record the result as a boundary update:

- `interior_extended`: the existing coordinate system handled it cleanly;
- `boundary_ambiguity`: multiple surfaces partially fit and selector/guard
  behavior exposes the edge;
- `missing_axis`: the source meaning is real but cannot currently be named
  without fixture vocabulary;
- `outside_scope`: the miss is outside present research claims;
- `fixture_language_leak`: the proposed fix would encode local nouns, row IDs,
  question IDs, or answer vocabulary.

## Escape-Time Observations

Prethinker already produces boundary observations during normal work:

- guard activations;
- scar guards;
- helper pressure and candidate-helper breadth;
- selector uncertainty;
- compile diagnostics;
- quarantine and clarification requests;
- missing slots and struggle signals;
- source rows preserved only as addressable residue;
- failed or volatile QA replays.

Treat these as observations of where meaning stayed bounded or escaped the
current coordinate system.

Do not confuse an exact answer with full quantization. A fixture can be answered
while still exposing helper bloat, source-note leakage, or a guard that only
works because it remembers local vocabulary.

## Third Axis: Grid-Fit

The older two-axis frame is:

- compile-time fidelity;
- retention durability.

Add a third axis:

```text
grid-fit: how much of the source's answer-bearing meaning lands in named,
transferable coordinates rather than opaque residue or fixture-local helpers.
```

Grid-fit is not just exact-answer rate. It asks:

- Did the architecture name the answer-bearing distinction?
- Is the coordinate reusable on unlike documents?
- Did helper rows stay bounded?
- Did source addressability remain intact?
- Did the selector choose through general scoring rather than a local guard?

## Domain Boundary Tests

A set characterized on one corpus may be fitted to that corpus.

Domain-2 work should test whether the boundary transfers. A legal corpus, a
medical corpus, and a school/activity corpus may place pressure on different
axes. The falsifiable research question is:

```text
Is Prethinker's coordinate system capturing transferable document meaning, or
only the recurring shapes of the current fixture corpus?
```

The answer should come from designed probes, not broad optimism.

Domain work is pressure, not expansion for its own sake. A new domain is useful
when it asks an unlike version of an existing boundary question or reveals a
missing coordinate that the current corpus could not expose.

## Operating Rules

1. Do not let fixture nouns become substrate.
2. Do not retire a guard because one row now wins.
3. Retire a guard only when a reusable predicate, helper, compile, or scoring
   principle explains the win.
4. Preserve scars when a local accident is worth remembering but should not be
   active behavior.
5. Let some singletons remain if they have a real edge-case rationale.
6. Use OpenRouter or local parallel lanes for pressure, but treat hosted
   variation separately from architecture evidence.
7. Stop a compression lane when the remaining cases are source-fidelity,
   baseline-arbitration, or legitimate singleton sentinels rather than
   transferable architecture pressure.
8. Journal every meaningful move as:

```text
before -> prediction -> intervention -> after -> boundary update -> next probe
```

## Fixture Design Template

Use this template when adding or selecting the next probe fixture:

```markdown
## Probe: <short name>

Prediction:
This should stress <axis> because <current principle> may confuse <X> with <Y>.

Expected Interior:
If the current architecture is sufficient, the answer should land through
<predicate/helper/source/scoring surface> without a new fixture-specific guard.

Expected Escape:
If it escapes, look for <diagnostic residue/helper pressure/selector ambiguity>.

Forbidden Fix:
Do not encode <local names, row ids, answer words, fixture-specific phrases>.

Result:
- exact / partial / miss:
- helper pressure:
- guards triggered:
- diagnostics/quarantine:

Boundary Update:
interior_extended | boundary_ambiguity | missing_axis | outside_scope |
fixture_language_leak

Next Probe:
<unlike fixture or axis variant>
```

## Relation To Active Worksheets

The boundary-hunt worksheet is now the active movement log for broad corpus
coordinates, designed probes, and helper/source cleanup:

- `docs/BOUNDARY_HUNT_WORKSHEET.md`

The guard-generalization worksheet is now a completed compression archive in
Git history/cold storage unless a boundary hunt discovers a new transferable
guard replacement.

When guard count drops, ask what changed:

- Did a reusable substrate principle emerge?
- Did a family split into cleaner semantic pressure?
- Did a helper surface earn transfer?
- Did a singleton become a keeper?
- Did the compression reveal a new largest boundary family?

Compression is useful because it makes topology visible. It is not the final
research target.

When wide-corpus not-exact rows appear, ask a different question:

- Is this a missing coordinate, a blurry interior, or provider/judge noise?
- Can a focused fixture isolate the failed distinction?
- Can a resolution fixture perturb a green row enough to reveal whether the
  coordinate is actually sharp?
- What fix is forbidden because it would encode fixture vocabulary?

## Terminal Audit

Compression work has a stop condition.

When remaining guards or helpers no longer imply a reusable coordinate, do not
keep squeezing them just to make a count smaller. Stable residue can be a valid
boundary observation.

Examples of terminal residue:

- source-fidelity singletons where the safest answer surface is an exact
  source row or archival row-value fallback;
- baseline-arbitration guards that prevent a broad but attractive candidate
  surface from overruling direct identity/name/role support;
- helper rows that expose useful source prose but still parse local phrasing
  rather than a transferable source-record relation;
- diagnostics or quarantines that correctly say "the current coordinate system
  should not name this yet."

Terminal audit does not mean "do nothing." It means switch the work from bulk
retirement to one of these moves:

- add unlike transfer evidence;
- improve source addressability;
- split helper pressure into clean source-coordinate rows versus candidate
  prose-derived rows;
- write the keeper rationale and leave the sentinel active;
- scar the local accident and remove active behavior.

The final target is a characterized boundary: a map of what Prethinker can
quantize, where it becomes ambiguous, and what new axes would be needed to
extend the set without smuggling fixture memory into the architecture.
