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
| Operational record/status | Permit lifecycles, intake logs, conservation ledgers, application dockets, corrections, reversals, unresolved items, status before/after, and row-level commit readiness. | Ashgrove, Greywell, Heronvale, Veridia. |
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

Latest selector lesson: specialized lenses can be answer-bearing or dazzlingly
irrelevant. `operational_record_status_v1` is not globally promoted; it is a
row-level candidate. `selector_baseline_readiness_guard` is the companion
restraint: if baseline has direct application/status, counterfactual rule, or
hold-readiness support and the competing surface is broad or relaxed-heavy, the
instrument keeps baseline rather than asking activation to admire extra rows.
`selector_question_act_guard` adds the other side of that restraint: if the
question asks about request filing, use request/reinstatement/threshold surface
rather than completion windows; if it asks whether to commit a status, use
pending/investigation process surface rather than a bare status value.
`selector_surface_specificity_guard` adds explicit surface preference for
cause/rationale notes, decision predicates, and priority predicates when nearby
status, condition, or event rows are tempting but less answer-bearing.
`selector_complete_operational_guard` closes the current frozen operational
record batch by naming the last distinction set: split-rationale questions need
actual split and lot-condition/policy surfaces; current-constitution eligibility
needs applicant type plus controlling interpretation; resubmission eligibility
needs proof/rule resolution rather than merely current applicant status. This
is selector calibration over persisted artifacts, not evidence that the compile
surface itself is complete.
`rationale_contrast_source_note_lens` captures source-stated reasons,
non-reasons, judgment calls, and explicit contrasts as answer-bearing note
surface without promoting those notes into policy. Its selector companions
prefer note rationale for why/contrast questions, direct collector predicates
for identity questions, pending `test_status` for not-yet-tested questions, and
threshold/storage policy surfaces for failed-viability hypotheticals.
The first transfer additions are `current_operational_final_state_guard`,
`evidentiary_report_surface_guard`, `board_concern_event_action_guard`, and
`commit_readiness_process_guard`. Together they keep rationale/contrast useful
for report, concern, and explanation rows while protecting final status and
commit/hold decisions from attractive but incomplete note or event surfaces.
The older-fixture transfer check marks the boundary: source-note rationale
transfers to record/discrepancy/correction surfaces, but it does not solve
Larkspur-style narrative motive, custody, or object-state coverage without a
stronger source-surface acquisition contract.
`final_object_state_transition_surface` is now separated from broad
state/custody prompting. It asks for named-device initial/current/final
condition, state-change event, repair/restoration possibility, and stated
state-change reason. Its guardrail is that identity/role questions should not
be overrun by object-state volume; Larkspur q009 is the active counterexample.
`custody_ownership_chain_surface` remains narrower still: use it for final
holder/ownership/custody rows such as q038, not as a general motive lens.
`official_role_authority_definition_surface` covers who-is questions where a
title alone is not enough. It asks for the role holder plus source-stated duties
and authority scope, so the selector can distinguish "this person made rulings"
from "this is the official role and what it controls."
The newest selector guards are named by answer surface:
`superlative_identity_surface_guard`, `official_role_definition_surface_guard`,
`current_component_state_surface_guard`, `custody_transfer_rationale_guard`,
and `award_placement_surface_guard`. They close the Larkspur overlay by routing
age/identity, role-authority, current component, custody why-have, and award
placement questions to the surface that actually carries the answer.
Calder adds the longitudinal conflict family:
`current_state_correction_conflict_surface`,
`possession_ownership_inheritance_distinction_surface`, and
`legal_title_default_transfer_surface`. Their guards are
`role_reinstatement_history_guard`, `carry_possession_surface_guard`,
`possession_ownership_distinction_guard`, `legal_title_transfer_guard`,
`contract_authority_surface_guard`, and
`guardianship_resumption_condition_guard`. These exist to separate stale
current-state rows, possession versus ownership, trust/default title, contract
authority, and non-retroactive guardianship effects.
Oxalis adds a regulatory access family that acts after a healthy compile rather
than replacing it: `universal_scope_enumeration_guard`,
`termination_denial_quantity_threshold_guard`,
`lot_affected_target_exclusion_guard`, and
`counterfactual_reclassification_deadline_guard`. These route all/any scoped
sets, denial rationales with threshold quantities, explicit negative lot checks,
and reclassification-deadline counterfactuals to evidence surfaces that carry
the relevant access pattern.
Rule activation now has a parallel family for promoted rule surfaces:
`deferment_rationale_interpretation_guard`,
`component_rule_condition_surface_guard`,
`recusal_rationale_rule_surface_guard`,
`post_recusal_vote_surface_guard`,
`counterfactual_recusal_outcome_guard`,
`window_merit_rule_condition_guard`,
`amendment_recall_authority_surface_guard`,
`rejection_cause_correction_surface_guard`, and
`hypothetical_reserve_status_arithmetic_guard`. These guards route questions
to the surface that carries the reason for activation: interpreted decision
support, project-category/rule-condition pairs, recusal procedure, combined
procedure-plus-eligibility counterfactuals, explicit window conditions,
recall-authority evidence, correction/clarification records, or reserve
arithmetic inputs. The Sable/Avalon replay reaches both fixtures' frozen
upper bounds without source prose, answer keys, judge labels, failure labels,
gold KBs, or strategy files in selector input.
The latest object/state/custody replay is intentionally negative: a combined
object-state-custody surface blurred too many rows on Fenmore and Larkspur.
The harness gain was instead a narrower selector distinction:
`deaccession_yet_status_surface_guard` routes "has X been deaccessioned yet?"
questions to compact scheduled/not-formally-completed status evidence instead
of broad lot-history volume. This keeps deaccession-yet status separate from
conservation rationale, operational thresholds, final object state, and custody
roster evidence.
The latest temporal/status/deadline replay repeats that shape. Broad temporal
surface is not a default compile mode: Ashgrove benefits only when the selector
uses the right row-level surface, and Copperfall regresses globally. The new
guards are named for the semantic reason rather than the fixture:
`adjusted_expiration_current_surface_guard` routes reinstatement/adjusted
expiration questions to explicit current-expiration predicates, and
`correction_entitlement_effect_surface_guard` routes correction-entitlement
questions to entitlement-rule plus extension-effect evidence. Copperfall keeps
the next boundary visible: original answer deadlines, resumed answer deadlines,
and later reply deadlines must be disambiguated as separate deadline families.

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

Companion inventory:
[Selector Guard Family Rollup](https://github.com/dr3d/prethinker/blob/main/docs/SELECTOR_GUARD_FAMILY_ROLLUP.md) is generated
from `scripts/select_qa_mode_without_oracle.py` and tracks whether many
individual selector guards are collapsing into a small number of semantic
families. The current rollup has `53` guard return sites, `52` unique guard
reasons, `7` families, and `0` unclassified reasons.

[Cross-Fixture Repair Slices](https://github.com/dr3d/prethinker/blob/main/docs/CROSS_FIXTURE_REPAIR_SLICES.md) is generated
from repair-target artifacts and tracks whether remaining failures are forming
multi-fixture semantic work slices. The current report has `72` targets across
`10` fixtures and recommends `9` multi-fixture slices.
