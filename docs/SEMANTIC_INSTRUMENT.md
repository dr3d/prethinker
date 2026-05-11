# The Prethinker Semantic Instrument

## What This Document Is

Prethinker compiles natural language documents into governed knowledge bases. This document describes the *instrument* - the collection of semantic lenses, selector guards, helpers, and uncertainty distinctions that the system uses to read documents from multiple angles and decide what can be answered from admitted state.

Think of it as the spec sheet for a scientific instrument. A spectrometer has wavelength ranges, resolution limits, and calibration procedures. Prethinker has semantic lenses, selector guards, and an uncertainty vocabulary. Both instruments get sharper through calibration against known samples.

---

## Core Principle: Artifact-First Orchestration

Prethinker compiles a document once and freezes the result. Every subsequent analysis - different query strategies, selector policies, failure classifications, repair experiments - runs against the same frozen artifact. Nothing changes the compiled knowledge base after compilation.

```
Source document
  -> compile once -> frozen KB artifact
  -> run many cheap semantic passes against the frozen artifact
  -> compare results across passes
  -> identify which lens sees what the others miss
```

This turns the GPU from one big thinker into a small research factory. The model still does the semantic work. The harness keeps that work bounded, replayable, and measurable. Every experiment is comparable because the underlying knowledge base is the same.

The current mini-architecture is:

```text
compiled KB = durable state
row = measured encounter with that state
selector = chooses the best encounter surface
guard = prevents a tempting wrong surface
verdict = records what happened
```

Truth lives in the compiled KB. A row is the measured encounter where a
question tests that state. This distinction matters: a perfect KB that cannot
surface the right row under pressure is still not a useful answer system.

The instrument now has a separate deterministic pre-compile layer:

```text
semantic lenses = model-owned meaning proposals
deterministic ledgers = exact source addressability
helpers = query-time computation over admitted state
```

The deterministic ledgers are not lenses and not guards. They do not interpret
ownership, authority, status, causality, or counts. They preserve source
structure that should not depend on model memory: exact identifiers, headings,
line numbers, table rows, table cells, numeric tokens, and labeled official
prose. This is the boring but crucial layer that lets later semantic passes
point to the exact row, date, count, packet id, or printed label instead of
asking the model to remember or paraphrase it.

The next architectural image is a governed spreadsheet:

```text
known state = filled cells
degrees of freedom = blank cells with constraints, ranges, and dependencies
propagation = recomputing what must be true, what may be true, and what is impossible
```

Prethinker is not there yet as a general substrate. Today it has early pieces:
Prolog rule/query execution, query-only helpers, temporal ordering propagation,
and diagnostic truth-maintenance proposals. The intended direction is that
derived cells remain visibly derived. A propagated answer should point back to
its supporting facts, rules, constraints, and retractions instead of becoming a
silent durable fact.

---

## The Lens Roster

A **semantic lens** is a specific reading strategy applied to a document. Each lens extracts a different layer of meaning. No single lens sees everything. The system compiles the same document through multiple lenses and uses a selector to choose the best lens for each question.

### The Thirteen Facets

Each lens targets one of these meaning surfaces:

| Facet | What It Captures | Why It Matters |
|-------|-----------------|----------------|
| **Source surface** | The basic facts: entities, dates, quantities, rules, corrections, exceptions | Without these facts in the KB, nothing downstream works. This is the foundation. |
| **Operational record** | Permit lifecycles, application dockets, status changes, reversals, corrections | A document that says "the permit was suspended, then reinstated" contains durable state that must be tracked as intervals, not just events. |
| **Rule composition** | Thresholds, precedence, activation conditions, exceptions, eligibility, override | Rules interact. A grant eligibility rule has an exception for different art forms. The exception must be evaluated together with the base rule, not separately. |
| **Temporal status** | Status-at-date, deadline arithmetic, business vs calendar days, effective/expired boundaries | "What was the permit status on May 15?" requires knowing that the suspension started April 28 and ended June 6. A point-in-time answer needs interval tracking. |
| **Authority** | Which document, person, board, or finding controls when accounts conflict | A staff memo recommends. A board votes. A review panel upholds. Each has different authority. The system must know which one controls. |
| **Evidence provenance** | Who prepared, presented, dated, admitted, relied on, commissioned, corrected, or physically located a source artifact | A surveyor prepared a survey, but the hearing officer commissioned it. A ledger contains an entry, but the front desk is where that ledger was found. Those are different facts. |
| **Archival row ledger** | Exact printed source labels, exhibit IDs, catalog IDs, docket IDs, system names, roster rows, table rows, and source-section labels | A packet ID can prove an event was recorded, but a benchmark may ask for the printed source name: "Pyxis MedStation 4000 cabinet log, Room 504 excerpt." |
| **Epistemic uncertainty** | Unknown, unstated, pending, disputed, retracted, superseded, unsupported states | "Not substantiated" is not "innocent." "Operationally resolved" is not "formally investigated." These are different epistemic states that must not be collapsed. |
| **Entity and role** | Aliases, identity changes, custody, ownership, family relationships, role transitions | Two people named Voss who aren't related. A grandfather and granddaughter both named Wren. A device that changes hands three times. Identity must be tracked precisely. |
| **Query surface** | Whether the query planner asks for the right predicates already in the KB | The KB might contain the answer, but if the query asks for the wrong predicate or joins the wrong tables, the answer won't surface. |
| **Selector surface** | Whether the right lens is chosen for each question | A "why" question needs the rationale lens. A "what is the current status" question needs the operational lens. The selector must match questions to lenses. |
| **Answer surface** | Whether the answer should be concise, hedged, cite uncertainty, or refuse | Some questions deserve a crisp answer. Some deserve "not established." Some deserve "the document does not say." The answer shape must match the epistemic state. |
| **Struggle detection** | Whether repeated compilation passes have stopped adding useful facts | If the last three passes added zero new unique rows, the system should stop compiling and move to query-time improvements instead. |

---

## How Lenses Work Together

No lens is used alone. The system compiles a document through multiple lenses and then uses a **selector** to choose the best lens for each question.

Example from the Fenmore Seed Bank fixture:

- **"Who collected lot FB-2026-001?"** -> Baseline lens (has the collector name directly)
- **"What is the current operational status of the bur oak lot?"** -> Operational-record lens (has the status lifecycle)
- **"Is the cryogenic split a viability concern?"** -> Rationale/contrast lens (has the curator's note: "conservation measure, not viability concern")
- **"Has the bur oak lot been deaccessioned yet?"** -> Object/state lens (has the "scheduled but not formally completed" status)

Four questions about the same document. Four different lenses provide the best answer. The selector chooses without seeing the correct answer - it uses structural signals about what kind of evidence each question needs.

---

## Selector Guards

A **selector guard** is a named rule that prevents the selector from choosing the wrong lens. The selector is the steering wheel; guards are the rumble strips. Each guard was discovered by watching the selector make a specific mistake on a specific fixture, then naming the semantic mistake and adding a structural check.

### Guard Families

The guard return sites continue to cluster into 7 semantic families with 0
unclassified reasons in the current rollup. The exact count changes as the lab
discovers, merges, and retires guards; the live accounting is maintained in
`docs/SELECTOR_GUARD_FAMILY_ROLLUP.md` and
`docs/SELECTOR_GUARD_LEDGER.md`.

| Family | What It Prevents | Example |
|--------|-----------------|---------|
| **Baseline readiness** | Overriding a strong baseline answer with a broader but less precise lens | Don't swap to the operational lens when baseline has the direct eligibility rule |
| **Question-act routing** | Matching the question type to the wrong evidence surface | A "was it filed on time" question needs filing/threshold evidence, not completion-window evidence |
| **Surface specificity** | Preferring volume over precision | Don't choose the lens with more rows if a smaller lens has the specific rationale note |
| **Requirement detail** | Accepting a partial answer when a more complete one exists | A count-only answer ("12 hydrants") is partial when another lens has count-plus-spacing ("12 hydrants, 300 feet apart") |
| **Temporal deadline** | Confusing deadline families | An original answer deadline, a resumed answer deadline, and a reply deadline are three different things with three different dates |
| **Authority/provenance** | Trusting the wrong source | A staff memo is not a board determination. An anonymous tip is not an established fact. |
| **State/custody** | Confusing current state with historical state | "Has it been deaccessioned?" needs current status, not the full history of the lot |

The newest guards came from the cold-injected story-world batch. They route
survey-commission questions to explicit `report_commissioned_by` provenance,
ledger-location questions to `ledger_found_location`, intake-actor questions to
`item_received_from`, and source-claim/permission-request questions back to
witness-statement surfaces when a narrow provenance registry is too thin. The
Claude 8 dense-record batch added a printed source-provenance guard: when a
question asks which source recorded a specific event, archival row/source labels
beat generic packet identifiers. A follow-up lexical pinboard added a
timekeeping guard: when the question asks about clocking out of a timekeeping
system, assignment/timekeeping evidence beats physical badge-exit rows.

The guard roster is still in discovery mode. Do not parameterize the 7 families
yet. First merge exact or near duplicates, prove the merged guard by replaying
the rows that created the originals, and retire guards when better compile or
helper surfaces make them unnecessary. A new guard is healthy when it names a
semantic question/evidence mismatch; it is suspicious when it only names a
fixture.

---

## The Uncertainty Vocabulary

Most AI systems have one uncertainty state: "I don't know." Prethinker distinguishes twelve:

| State | What It Means | Example |
|-------|--------------|---------|
| **Unknown** | The fact is not in the compiled record | No information about this entity exists in the KB |
| **Unstated** | The source document never mentions it | The document describes 5 applicants but never states the total budget |
| **Pending** | A process has not resolved yet | The Home Occupation Permit application is pending |
| **Disputed** | Competing accounts exist | The Tally Clerk and Margaux disagree about whether Petra qualifies as a witness |
| **Retracted** | An earlier claim was withdrawn | The inspection date was corrected from February 1 to February 3 |
| **Superseded** | A newer rule or status replaces an older one | The 2021 Board interpretation replaces the strict textual reading |
| **Unadopted** | Someone asserted it but the controlling authority didn't accept it | The draft memo proposes a rule but the board never adopted it |
| **Unsupported** | No evidence supports the claim | The anonymous tip provides no supporting evidence |
| **Inferred** | Derivable from admitted facts but not directly stated | The 30% matching threshold on a $26,500 request is $7,950 (calculated, not stated) |
| **Provisional** | Temporarily true until a condition changes | The conditional approval expires if conditions aren't met within 30 days |
| **Resolved negative** | The question has been answered "no" | The permit is invalid. The applicant is ineligible. The appeal is denied. |
| **Temporally unavailable** | Not yet effective, expired, or outside the relevant interval | The flight hazard assessment expired at 20:30 and cannot authorize drops at 21:15 |

These distinctions matter because "I don't know," "the source doesn't say," "the source contains conflicting accounts," "the rule hasn't activated yet," and "the answer is no" are all different answers to the same question. A system that collapses them into a single "not sure" will get the wrong answer whenever the distinction matters - which is most of the time in legal, medical, regulatory, and compliance contexts.

---

## Current Instrument State

### Current Score Evidence

The instrument has been calibrated across hostile fixtures and fresh
cold-injected story worlds. Two current evidence bands matter:

- Prior surgical fixture batch: **284 / 303 exact (94%)**, with only **3**
  misses and zero unauthorized writes. This remains useful historical evidence;
  newer work is now focused on cold-fixture transfer and guard compression.
- 2026-05-07 cold-injected story-world batch: **361 / 400 exact (90.25%)**
  under row-gated selector replay, with **16 partial**, **23 miss**, and zero
  QA write proposals in the contributing runs.
- 2026-05-08 incoming-6 full-40 batch: cold baseline **186 / 16 / 38** moved to
  a diagnostic row-gated high-water of **240 / 0 / 0** over **240** rows. This
  proves reachable surfaces, not one global compiler; the contributing row
  shapes remain selector-scoped until transfer checks prove them.
- 2026-05-09 precision fixture batch: cold OpenRouter baseline **148 / 16 / 76**
  over **240** rows moved to **223 / 8 / 9** selected exact/partial/miss after
  candidate farming, guarded selection, and deterministic source-record ledger
  V2. The available candidate ceiling is now **232 / 4 / 4**. The lift came
  without a new semantic lens or guard family: the durable lesson is that exact
  source addressability is a separate substrate from model-owned meaning.
- Fresh perfect cold-batch fixtures now include **Nested Puppet Court 40/40**
  and **Clockmakers Three Ledgers 39/40 with zero misses** under row-gated
  evidence-provenance and ledger/object-provenance modes.

### Lens Transfer Evidence

Each lens has been tested for transfer - whether it helps on fixtures it wasn't designed for:

- The **rationale/contrast lens** transfers cleanly across Fenmore, Greywell, Heronvale, Veridia, and Ashgrove
- The **operational-record lens** transfers across all fixture types but must NOT be used as a global default - it helps status questions and hurts eligibility questions
- The **rule-interpretation lens** produced the strongest single-fixture gain (Meridian 27->39) but has not yet been tested for broad transfer
- The **temporal/deadline surface** was explicitly rejected as a global compile on Copperfall - it confuses deadline families
- The **evidence-provenance scaffold** is useful only as a row-gated lens so
  far: it closed Nested Puppet Court to 40/40 and moved Clockmakers to 39/40,
  while each registry compile regressed broad rows when used globally.

### Negative Results

These are as important as the positive ones:

- A broad object/state/custody surface blurred too many rows on Fenmore and Larkspur - the fix was a narrow deaccession-yet guard, not a bigger lens
- The partial-skeleton instruction that helped Three Moles (story world) hurt Oxalis (regulatory) - it was scoped back to narrative passes only
- A broader evidence-filter floor that helped Black Lantern's miss count hurt its exact count - evidence filtering is not "more is better"
- The temporal/status/deadline surface regressed Copperfall globally - deadline families need query-level disambiguation, not compile-level broadening
- The newest Oxalis/Three Moles pass preserves that discipline: recall accounting helpers, story choice contrast, and remediation-method support are query-only companions over admitted KB rows. They show targeted row rescues, but they do not change the headline score until a full replay proves exact-row protection.

---

## Companion Documents

- **[The Twelve Lenses](https://github.com/dr3d/prethinker/blob/main/docs/TWELVE_LENSES_EXPLAINED.md)** - plain-language guide to the reader/control lenses and how they differ.
- **[Semantic Lens Roster](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_LENS_ROSTER.md)** - deeper lab calibration notes for the active lens roster, guardrail names, archival row ledger, and uncertainty vocabulary.
- **[Selector Guard Family Rollup](https://github.com/dr3d/prethinker/blob/main/docs/SELECTOR_GUARD_FAMILY_ROLLUP.md)** - tracks whether guard return sites are collapsing into a smaller number of semantic families (currently 7 families, 0 unclassified)
- **[Cross-Fixture Repair Slices](https://github.com/dr3d/prethinker/blob/main/docs/CROSS_FIXTURE_REPAIR_SLICES.md)** - tracks whether remaining failures form multi-fixture work slices (currently 72 targets across 10 fixtures, organized into 9 recommended slices)
- **[Frontier Fixture Strategy](https://github.com/dr3d/prethinker/blob/main/docs/FRONTIER_FIXTURE_STRATEGY.md)** - the fixture design methodology, difficulty calibration, and cross-fixture regression protocol

---

## Design Philosophy

The goal is not a bigger model or a better prompt. The goal is a sharper instrument.

Each lens is a specific optic that sees one kind of meaning clearly. Each guard is a calibration rule that prevents the instrument from using the wrong optic. Each uncertainty state is a measurement category that prevents the instrument from collapsing distinct epistemic conditions into a single "don't know."

The instrument gets sharper by exposure to harder documents, honest measurement of what it gets wrong, named architectural fixes that transfer across domains, and the discipline to merge or retire guards rather than letting fixture-shaped rules accumulate forever.

Same telescope. Better optics. Every time.


