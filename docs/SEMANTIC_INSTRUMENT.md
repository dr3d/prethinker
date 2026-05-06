# The Prethinker Semantic Instrument

## What This Document Is

Prethinker compiles natural language documents into governed knowledge bases. This document describes the *instrument* - the collection of semantic lenses, selector guards, and uncertainty distinctions that the system uses to read documents from multiple angles and decide what to believe.

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

---

## The Lens Roster

A **semantic lens** is a specific reading strategy applied to a document. Each lens extracts a different layer of meaning. No single lens sees everything. The system compiles the same document through multiple lenses and uses a selector to choose the best lens for each question.

### The Eleven Facets

Each lens targets one of these meaning surfaces:

| Facet | What It Captures | Why It Matters |
|-------|-----------------|----------------|
| **Source surface** | The basic facts: entities, dates, quantities, rules, corrections, exceptions | Without these facts in the KB, nothing downstream works. This is the foundation. |
| **Operational record** | Permit lifecycles, application dockets, status changes, reversals, corrections | A document that says "the permit was suspended, then reinstated" contains durable state that must be tracked as intervals, not just events. |
| **Rule composition** | Thresholds, precedence, activation conditions, exceptions, eligibility, override | Rules interact. A grant eligibility rule has an exception for different art forms. The exception must be evaluated together with the base rule, not separately. |
| **Temporal status** | Status-at-date, deadline arithmetic, business vs calendar days, effective/expired boundaries | "What was the permit status on May 15?" requires knowing that the suspension started April 28 and ended June 6. A point-in-time answer needs interval tracking. |
| **Authority** | Which document, person, board, or finding controls when accounts conflict | A staff memo recommends. A board votes. A review panel upholds. Each has different authority. The system must know which one controls. |
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

A **selector guard** is a named rule that prevents the selector from choosing the wrong lens. Each guard was discovered by watching the selector make a specific mistake on a specific fixture, then naming the mistake and adding a structural check.

### Guard Families

The 52 individual guards cluster into 7 semantic families:

| Family | What It Prevents | Example |
|--------|-----------------|---------|
| **Baseline readiness** | Overriding a strong baseline answer with a broader but less precise lens | Don't swap to the operational lens when baseline has the direct eligibility rule |
| **Question-act routing** | Matching the question type to the wrong evidence surface | A "was it filed on time" question needs filing/threshold evidence, not completion-window evidence |
| **Surface specificity** | Preferring volume over precision | Don't choose the lens with more rows if a smaller lens has the specific rationale note |
| **Requirement detail** | Accepting a partial answer when a more complete one exists | A count-only answer ("12 hydrants") is partial when another lens has count-plus-spacing ("12 hydrants, 300 feet apart") |
| **Temporal deadline** | Confusing deadline families | An original answer deadline, a resumed answer deadline, and a reply deadline are three different things with three different dates |
| **Authority/provenance** | Trusting the wrong source | A staff memo is not a board determination. An anonymous tip is not an established fact. |
| **State/custody** | Confusing current state with historical state | "Has it been deaccessioned?" needs current status, not the full history of the lot |

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

### Scores Across 25 Benchmarks

The instrument has been calibrated against 25 hostile benchmarks across 14 domain types. Current results on the surgical fixture batch (9 fixtures, 303 questions):

- **284 exact (94%)** with the selector
- **3 misses** remaining across the entire batch
- **2 perfect scores** (Fenmore 25/25, Greywell 25/25)
- **7 fixtures at zero misses**
- **Zero unauthorized writes** across the entire corpus

### Lens Transfer Evidence

Each lens has been tested for transfer - whether it helps on fixtures it wasn't designed for:

- The **rationale/contrast lens** transfers cleanly across Fenmore, Greywell, Heronvale, Veridia, and Ashgrove
- The **operational-record lens** transfers across all fixture types but must NOT be used as a global default - it helps status questions and hurts eligibility questions
- The **rule-interpretation lens** produced the strongest single-fixture gain (Meridian 27->39) but has not yet been tested for broad transfer
- The **temporal/deadline surface** was explicitly rejected as a global compile on Copperfall - it confuses deadline families

### Negative Results

These are as important as the positive ones:

- A broad object/state/custody surface blurred too many rows on Fenmore and Larkspur - the fix was a narrow deaccession-yet guard, not a bigger lens
- The partial-skeleton instruction that helped Three Moles (story world) hurt Oxalis (regulatory) - it was scoped back to narrative passes only
- A broader evidence-filter floor that helped Black Lantern's miss count hurt its exact count - evidence filtering is not "more is better"
- The temporal/status/deadline surface regressed Copperfall globally - deadline families need query-level disambiguation, not compile-level broadening

---

## Companion Documents

- **[Semantic Lens Roster](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_LENS_ROSTER.md)** - deeper lab calibration notes for the active lens roster, guardrail names, and uncertainty vocabulary.
- **[Selector Guard Family Rollup](https://github.com/dr3d/prethinker/blob/main/docs/SELECTOR_GUARD_FAMILY_ROLLUP.md)** - tracks whether the 52 individual guards are collapsing into a smaller number of semantic families (currently 7 families)
- **[Cross-Fixture Repair Slices](https://github.com/dr3d/prethinker/blob/main/docs/CROSS_FIXTURE_REPAIR_SLICES.md)** - tracks whether remaining failures form multi-fixture work slices (currently 72 targets across 10 fixtures, organized into 9 recommended slices)
- **[Frontier Fixture Strategy](https://github.com/dr3d/prethinker/blob/main/docs/FRONTIER_FIXTURE_STRATEGY.md)** - the benchmark design methodology, difficulty calibration, and cross-fixture regression protocol

---

## Design Philosophy

The goal is not a bigger model or a better prompt. The goal is a sharper instrument.

Each lens is a specific optic that sees one kind of meaning clearly. Each guard is a calibration rule that prevents the instrument from using the wrong optic. Each uncertainty state is a measurement category that prevents the instrument from collapsing distinct epistemic conditions into a single "don't know."

The instrument gets sharper by exposure to harder documents, honest measurement of what it gets wrong, and named architectural fixes that transfer across domains without regressing what already works.

Same telescope. Better optics. Every time.


