# Semantic Lens Roster

This document captures the current thinking behind Prethinker as a semantic
instrument. It is not a prompt grab bag. It is the start of a roster of the
meaning surfaces the harness should measure, hone, and compare as fixtures get
harder and scores climb.

## Artifact-First Orchestration

Prethinker should prefer artifact-first orchestration:

```text
compile once -> persist source/KB/IR/run artifacts -> run many cheap semantic parallax passes against frozen artifacts
```

The point is to stop treating every question as a fresh act of model
improvisation. A source compile should freeze an inspectable substrate: source
surface, admitted KB, Semantic IR, mapper diagnostics, compile health, and run
metadata. Later passes can then test query variants, selector policies, answer
restraint, failure classification, and repair lenses against the same frozen
world.

This turns the GPU from one big thinker into a small research factory. Python
holds the experiment steady, records what changed, and makes each pass
comparable. The model still performs semantic work; the harness keeps that work
bounded, replayable, and measurable.

## Lens Facets

Lens names should describe the guardrail or semantic reason for being, not the
fixture that first exposed the issue. A good lens answers:

- What meaning surface does this acquire, protect, or compare?
- Which failure surface does it target?
- Which fixtures expose it?
- Does it transfer to unlike fixtures?
- Does it preserve exact rows and authority boundaries?

Current facet roster:

| Facet | What It Measures | Example Pressure |
| --- | --- | --- |
| Source surface | Whether the KB admitted the facts, states, rules, actors, quantities, dates, corrections, and exceptions needed for later reasoning. | Compile gaps dominate current cold rollups. |
| Rule composition | Thresholds, precedence, activation, exception, vote, eligibility, override, and expiration behavior. | Glass Tide, Avalon, Sable, Oxalis. |
| Temporal/status | Status-at-date, interval overlap, deadline arithmetic, business/calendar day distinctions, supersession, and effective/expired boundaries. | Iron Harbor, Oxalis, Dulse, Ashgrove. |
| Authority | Which document, actor, correction, board, rule, vote, or finding controls when accounts conflict. | Northbridge, Greywell, Kestrel, CE. |
| Epistemic uncertainty | Whether the system distinguishes unknown, unstated, pending, disputed, retracted, superseded, unsupported, provisional, inferred, and resolved-negative states. | CE, Veridia Intake, stenographer/turnstream work. |
| Entity and role | Aliases, identity, titles, role changes, custody, ownership, membership, family, organization, and responsibility relationships. | Larkspur, Calder, Three Moles. |
| Query surface | Whether the post-compile query planner asks for the right predicates and joins already present in the KB. | APR, Veridia, Greywell. |
| Selector surface | Whether baseline, direct, protected, activation, evidence, or other modes are chosen under measured risk. | Larkspur, Avalon, Sable, incoming batches. |
| Answer surface | Whether the answer should be concise, hedged, cite uncertainty, refuse, stay quiet, or report insufficient support. | CE, Veridia, answer-surface gaps. |
| Struggle detection | Whether repeated passes have stopped adding unique semantic surface and should stop or continue only with a named expected contribution. | `semantic_progress_assessment_v1`. |

## Uncertainty Vocabulary

Uncertainty is a domain language, not a tone. Future harness work should avoid
collapsing these into a single "not sure" bucket:

| State | Meaning |
| --- | --- |
| `unknown` | The fact is not available in the current record. |
| `unstated` | The source never says it. |
| `pending` | A process has not resolved yet. |
| `disputed` | Competing accounts exist. |
| `retracted` | An earlier claim was withdrawn. |
| `superseded` | A newer rule, correction, or status replaces an older one. |
| `unadopted` | Someone asserted it, but the controlling authority did not accept it. |
| `unsupported` | No evidence in the compiled record supports the claim. |
| `inferred` | Derivable from admitted facts/rules, but not directly stated. |
| `provisional` | Temporarily true until a condition changes. |
| `resolved_negative` | The rule-status uncertainty has been resolved negatively, such as invalid, void, ineligible, denied, or not effective. |
| `temporally_unavailable` | Not yet effective, expired, outside the relevant interval, or before/after the controlling date. |

This matters because "I do not know," "the source does not say," "the source
contains conflicting accounts," "the rule has not activated," and "the answer is
no" are different semantic states. Prethinker should learn to hold them apart.

## Future Roster Shape

As scores approach the higher band, this roster should become more operational:

- each promoted lens gets a stable name and purpose;
- each lens links to the fixtures that expose it;
- each lens records current transfer evidence;
- each lens records failure surfaces helped and regressions caused;
- each uncertainty state gets examples from real fixture rows;
- row-level promotions remain artifact-gated, not vibe-gated.

The goal is an engineered thesaurus of semantic pressure points: not synonyms,
but ways meaning can fracture under question.
