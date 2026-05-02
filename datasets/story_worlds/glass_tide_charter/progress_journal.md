# Glass Tide Charter Progress Journal

This journal tracks Prethinker's progress on the Glass Tide rule-ingestion fixture.

Keep the ugly deltas. The point is to learn where rule compilation breaks: source-stated rule extraction, executable rule admission, exception preservation, temporal helper support, negation-as-failure boundaries, claim-vs-finding discipline, permission-vs-event discipline, and post-ingestion QA over derived answers.

## GLT-000 - Fixture Admission

- Timestamp: `2026-05-02T00:00:00Z`
- Source: `tmp/The Glass Tide Charter`
- Destination: `datasets/story_worlds/glass_tide_charter`
- Mode: `fixture_setup`
- Expected Prolog guidance: no model run yet.
- Profile guidance: not run yet.

### Headline

Glass Tide is admitted as a rule-ingestion frontier fixture. It contains a source fixture, oracle-only gold KB with executable rules, 100-question QA battery, first-20 support scaffold, generic assisted-mode starter profile, failure buckets, and metrics ledger.

### Why This Hurts

This fixture is designed to expose whether Prethinker can move beyond fact/support-row accumulation toward governed executable rules. The hard parts are exceptions, priority rules, temporal windows, bounded absence, source-ranking, permissions that are not events, and claims that are not findings.

### First Measurement Plan

1. Run a cold source/profile compile with no starter registry and no gold artifacts in model context.
2. Run first-20 QA and record exact/partial/miss.
3. Run full-100 QA if the first-20 surface is not empty.
4. Separately test profile-guided product mode with the generic starter registry.
5. Do not use gold KB signatures, QA answers, or support map as prompt guidance for any cold/source-aware claim.

## GLT-001 - Cold Dense Rule Source Baseline

- Timestamp: `2026-05-02T14:57:58Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T145758760457Z_story_qwen-qwen3-6-35b-a3b.json`
- Mode: `cold_compile`
- Profile guidance: no starter registry; no gold artifacts in model context.
- Model: `qwen/qwen3.6-35b-a3b`

### Result

- Profile bootstrap parsed: no.
- Intake plan parsed: yes.
- Compile skipped because profile-bootstrap JSON overflowed or failed closure.

### Lesson

This is a control-plane failure before rule ingestion is even tested. The model recognized the source as a dense charter/rule fixture and produced a plausible large profile, but the profile-bootstrap response exceeded the reliable JSON boundary. The next cold experiment needs a more compact profile-bootstrap contract for dense rule sources: reusable predicate families, bounded candidate counts, and no exhaustive rule prose inside the profile object.

## GLT-002 - Assisted Generic Rule Profile Baseline

- Timestamp: `2026-05-02T15:03:45Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T150345032820Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T150726869674Z_qa_qwen-qwen3-6-35b-a3b.json`
- Mode: `profile_guided_product_mode`
- Profile guidance: generic `ontology_registry.json`; not derived from the gold KB.
- Model: `qwen/qwen3.6-35b-a3b`

### Result

- Profile parsed: yes.
- Candidate predicates: `22`
- Compile admitted: `92`
- Compile skipped: `231`
- Admitted executable rules: `0`
- First-20 QA: `7 exact / 2 partial / 11 miss`
- Runtime load errors: `0`
- QA write proposals: `0`

### Lesson

This is usefully bad. The assisted starter profile preserves explicit rule records such as source_rule/rule_text/rule_candidate rows, but it does not yet push the compiler into safe executable `operation='rule'` clauses. The failure is not ordinary fact extraction; it is the exact frontier this fixture was built to hurt: turning source-stated charter rules into admitted, executable symbolic rules while preserving exceptions, source priority, permissions, and claim-vs-finding boundaries.

## GLT-003 - Single-Pass Rule-Pressure Regression

- Timestamp: `2026-05-02T15:16:55Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T151655233007Z_story_qwen-qwen3-6-35b-a3b.json`
- Mode: `profile_guided_product_mode`
- Profile guidance: generic `ontology_registry.json`; not derived from the gold KB.
- Change: added a narrow `rule_ingestion_source_compiler_strategy_v1` context module.
- Model: `qwen/qwen3.6-35b-a3b`

### Result

- Profile parsed: yes.
- Candidate predicates: `22`
- Compile admitted: `66`
- Compile skipped: `216`
- Admitted executable rules: `0`

### Lesson

This is a valuable regression. Adding more rule-ingestion pressure to the same broad compile caused a thinner admitted surface and still did not produce executable rules. The model did preserve source_rule/rule_text rows, but the single-pass compiler still treated rules as records rather than executable clauses. This supports the multi-pass compiler hypothesis: rule acquisition should probably be a separate semantic lens over an already-admitted backbone, not extra prose pressure inside the default compile.

## GLT-004 - First Rule Lens Over GLT-002 Backbone

- Timestamp: `2026-05-02T15:23:34Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T152334556030Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Backbone: `GLT-002`
- Mode: `rule_acquisition_lens`

### Result

- Admitted executable rules: `3`
- Skipped rule proposals: `9`
- Runtime rule load errors: `0`

### Lesson

This is the first qualitative break from rule records to executable rules. However, the admitted rules mostly did not fire against the GLT-002 backbone because GLT-002 preserved source_rule/rule_text rows but lacked the body facts needed for inference. Rule acquisition needs a richer admitted surface before it can be useful.

## GLT-005 - Rule Lens Over GLT-002+GLT-003 Union

- Timestamp: `2026-05-02T15:24:39Z`
- Union artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T152417875559Z_glass-tide-glt002-glt003-union_qwen-qwen3-6-35b-a3b.json`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T152439304203Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `safe_surface_union_then_rule_lens`

### Result

- Union surface: `128` admitted facts, `0` rules, `0` runtime load errors.
- Rule lens admitted: `9` executable rules.
- Runtime rule load errors: `0`

### Lesson

Safe-surface accumulation helped. The union surface gave the rule lens more event/body vocabulary and rule admission rose from `3` to `9`. The new problem was overgeneralization: several rules were syntactically admissible but noisy, using broad class predicates such as person/place/cargo as loose binders. This is the first clear Glass Tide evidence for the next rule frontier: rule admission must measure runtime yield and fanout, not merely clause parseability.

## GLT-006 - Anti-Fanout Guidance Too Loose For JSON

- Timestamp: `2026-05-02T15:26:29Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T152629011325Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `rule_acquisition_lens_with_runtime_yield`

### Result

- Rule lens admitted: `11` executable rules.
- Runtime rule load errors: `0`
- Firing rules: `8`
- High-fanout behavior: present.

### Lesson

Runtime yield diagnostics exposed the true risk. More rules fired, but some fired absurdly broadly because the model used class predicates as binders and inferred permission from occurrence. This is not a mapper syntax problem; it is rule overgeneralization. The rule lens needs a verifier/overgeneralization policy: each head variable should be relation-bound, not merely class-bound.

## GLT-007 - Strict Anti-Fanout JSON Failures

- Timestamp: `2026-05-02T15:28:07Z` and `2026-05-02T15:28:50Z`
- Rule artifacts:
  - `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T152807929272Z_story-rules_qwen-qwen3-6-35b-a3b.json`
  - `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T152850852990Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `strict_rule_lens`

### Result

- Both runs failed JSON parsing due unterminated rule-clause strings.

### Lesson

Rule clauses are structurally fragile JSON payloads. Rule-lens prompts need the same compact-output discipline as focused source passes: one-line clause strings, small operation targets, and no prose inside clause fields.

## GLT-008 - One-Line Rule Clause Contract

- Timestamp: `2026-05-02T15:29:49Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T152949957017Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `strict_rule_lens_one_line_clauses`

### Result

- Rule lens admitted: `10` executable rules.
- Runtime rule load errors: `0`
- Firing rules: `0`
- High-fanout rules: `0`

### Lesson

The one-line clause contract fixed JSON and the anti-fanout guidance eliminated broad noisy derivations, but the rules no longer fired. This is the other side of the rule frontier: safe executable rules require body facts that match the admitted backbone. If the surface lacks status/body predicates, stricter rules become clean but dormant.

## GLT-009 - Cold Compact Profile Bootstrap Recovery

- Timestamp: `2026-05-02T15:33:52Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T153352137739Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T153708238726Z_qa_qwen-qwen3-6-35b-a3b.json`
- Mode: `cold_compile`
- Profile guidance: no starter registry; no gold artifacts in model context.

### Result

- Profile parsed: yes.
- Candidate predicates: `18`
- Compile admitted: `274`
- Compile skipped: `93`
- Admitted executable rules: `0`
- First-20 QA: `13 exact / 3 partial / 4 miss`

### Lesson

The compact profile-bootstrap guidance fixed the GLT-001 cold failure. Cold discovery now builds a much richer symbolic surface and immediately beats the assisted generic baseline on first-20 QA (`13/20` exact versus `7/20`). It still does not emit executable rules, which confirms rule acquisition is a separate lens problem, not solved by a better default compile.

## GLT-010 - Cold Backbone Rule-Lens Timeout

- Timestamp: `2026-05-02T15:40:00Z`
- Mode: `cold_backbone_rule_lens`

### Result

- Rule-lens attempts over the full cold backbone timed out even with smaller operation targets, backbone fact limits, and source character limits.

### Lesson

Whole-source rule acquisition over a rich cold backbone is too expensive and unreliable as a single prompt. The next implementation should use planned/span-specific rule lenses: one charter rule family or source span at a time, with the admitted backbone subset selected by a pass planner rather than dumped wholesale.

## GLT-011 - Authored-Span Rule Lens Tooling

- Timestamp: `2026-05-02T19:11:17Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T191117340594Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `authored_span_rule_lens`
- Change: `scripts/run_rule_acquisition_pass.py` gained exact Markdown-heading and line-range source selection.

### Result

- Full `Charter rules read aloud before the glass tide` section still timed out.
- Single-line probe over the living-cargo rule returned quickly but failed JSON because the model spent output on long `self_check` prose and truncated the object.
- The raw candidate rules also used unsafe/unsupported constructs such as `not`, comparison, and broad exception predicates.

### Lesson

Span selection solves the timeout shape only if the rule lens also has compact-output discipline. Rule acquisition cannot be allowed to write an essay in `self_check`; it needs a hard candidate-operation cap, one-line clauses, and a tiny self-check budget.

## GLT-012 - Span-Local Rule Cap And Predicate-Filtered Backbone

- Timestamp: `2026-05-02T19:18:35Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T191835404068Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `line_range_rule_lens_with_backbone_predicate_filter`
- Source span: `story.md:L42`

### Result

- Runtime returned in seconds rather than timing out.
- Rule proposals parsed.
- `0` executable rules admitted.
- `3` rule proposals skipped.
- Skip reasons exposed rule-shape errors: `member/2` was outside palette and one `derived_permission` proposal had arity `3` instead of required `4`.

### Lesson

Predicate-filtered admitted-backbone context is the right speed path. The next issue is not latency; it is rule-shape discipline. The model still reaches for list/member and wrong-head arity unless those are explicitly pinned.

## GLT-013 - First Span-Local Clean Rule Admission

- Timestamp: `2026-05-02T19:19:54Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T191954446687Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `span_local_rule_lens_hard_cap`
- Source span: `story.md:L42`

### Result

- `1` executable rule admitted.
- `0` skipped operations.
- Runtime rule load errors: `0`.
- Firing rules: `0`.
- High-fanout rules: `0`.

### Lesson

This is the first clean span-local rule admission over the cold Glass Tide backbone. The rule was safe enough to load and did not fan out, but it was dormant because its body referenced predicate shapes that had no matching admitted facts. This confirms that rule admission needs a runtime trial/verifier, not just mapper parseability.

## GLT-014 - Body-Support Runtime Diagnostics

- Timestamp: `2026-05-02T19:21:11Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T192111476978Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `rule_runtime_body_support_diagnostics`
- Source span: `story.md:L42`

### Result

- `1` executable rule admitted.
- Runtime rule load errors: `0`.
- Firing rules: `0`.
- Dormant rules: `1`.
- Unsupported body signatures: `temporal_window/4`, `event_at/3`.

### Lesson

The rule verifier now explains dormancy mechanically. The admitted rule is not unsafe fanout; it is unsupported-body dormancy. This is a better diagnostic surface for rule promotion: a rule can be syntactically admitted, runtime-loadable, and still not promotion-ready because its body predicates do not have admitted fact support.

## GLT-015 - Salvage Rule Negative Probe

- Timestamp: `2026-05-02T19:21:45Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T192145370705Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `span_local_salvage_rule_probe`
- Source span: `story.md:L54`

### Result

- `0` executable rules admitted.
- `1` rule proposal skipped.
- Skip reason: unsupported `exception/2` predicate outside the active palette.

### Lesson

The mapper correctly blocked an attractive but wrong shortcut: the model tried to express the sacred-cargo exception through a generic `exception/2` surface instead of the fixture's supported `rule_exception/2` / source-specific support rows. This is the rule-ingestion version of predicate canonicalization drift.

## GLT-016 - Active Predicate Palette Rule Firing

- Timestamp: `2026-05-02T19:34:16Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T193416383507Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `active_predicate_palette_rule_lens`
- Source span: `story.md:L42`

### Result

- `1` executable rule admitted.
- Runtime rule load errors: `0`.
- Firing rules: `1`.
- Dormant rules: `0`.
- Unsupported body signatures: `0`.
- Derived runtime row: `derived_authorization(repair_order_71, valid, glass_tide_repair)`.
- Admitted rule:

```prolog
derived_authorization(RepairOrder, valid, glass_tide_repair) :-
    entity_property(RepairOrder, authorized_by, mara_vale_and_juno_vale).
```

### Lesson

The first Glass Tide rule now loads and fires. The key structural move was exposing an active predicate palette for the rule lens, not merely filtering admitted backbone examples. Earlier GLT-014 let the model see unsupported temporal/event predicates and produced a safe but dormant rule. GLT-016 limited the rule pass to predicates that were active for this lens and already had admitted fact support, so the model built a firing body over `entity_property/3`.

This is a rule-ingestion milestone, but it is not the finish line. The rule is instance-support-shaped rather than a full two-signer generalization, which is acceptable for a query-only trial but not yet strong durable rule admission. The next frontier is a body-fact acquisition lens or a role-aware signature that can support a more general rule without reintroducing unsupported-body dormancy.

## GLT-017 - Body-Goal Support Diagnostics

- Timestamp: `2026-05-02T19:37:25Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T193725270757Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `rule_runtime_body_goal_support_diagnostics`
- Source span: `story.md:L54`

### Result

- `2` executable rules admitted.
- Runtime rule load errors: `0`.
- Firing rules: `0`.
- Dormant rules: `2`.
- Unsupported body signatures: `0`.
- Unsupported body goals: `2`.

### Lesson

Signature-level support was too coarse for rule promotion. The dormant salvage rules used admitted predicates such as `entity_property/3`, but rewrote the argument pattern into unsupported constants like `entity_property(Cargo, type, sacred_cargo)` instead of matching admitted rows such as `entity_property(bell_of_saint_loam, sacred_status, sacred)`. The runtime verifier now reports body-goal support where constants must match and variables are wildcards.

This exposes the formal shortcut shape directly: the rule was right-shaped at the predicate/arity level but wrong-meaning at the argument-mapping level. Durable rule promotion needs body-goal support, not only rule load success and predicate-signature support.

## GLT-018 - Variable Hygiene Restores Firing Rule

- Timestamp: `2026-05-02T19:38:28Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T193828487433Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `active_predicate_palette_with_body_goal_support`
- Source span: `story.md:L42`

### Result

- `1` executable rule admitted.
- Runtime rule load errors: `0`.
- Firing rules: `1`.
- Dormant rules: `0`.
- Unsupported body signatures: `0`.
- Unsupported body goals: `0`.
- Derived runtime row: `derived_authorization(repair_order_71, valid, glass_tide_repair)`.

### Lesson

Body-goal diagnostics also caught a variable/constant shortcut. A quick intermediate rerun used lowercase `repair_order` where Prolog required uppercase `RepairOrder`, turning a general rule into a nonmatching constant rule. The rule-lens prompt now pins Prolog variable hygiene explicitly: uppercase tokens are variables, lowercase tokens are constants.

GLT-018 is the cleanest rule-trial artifact so far: active predicate palette, loadable rule, firing derived row, zero unsupported body goals, and zero fanout. Promotion remains query-only because the rule is still shaped around an admitted combined signer property rather than a fully general two-role signer relation.

## GLT-019 - Role-Joined Repair Rule

- Timestamp: `2026-05-02T19:42:08Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T194208282290Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `role_joined_active_predicate_rule_lens`
- Source span: `story.md:L42`

### Result

- `1` executable rule admitted.
- Runtime rule load errors: `0`.
- Firing rules: `1`.
- Dormant rules: `0`.
- Unsupported body signatures: `0`.
- Unsupported body goals: `0`.
- High-fanout rules: `0`.
- Derived runtime row: `derived_authorization(repair_order_71, valid, glass_tide_repair)`.

Admitted rule:

```prolog
derived_authorization(RepairOrder, valid, glass_tide_repair) :-
    holds_role(Warden, harbor_warden, active),
    holds_role(Engineer, chief_tide_engineer, active),
    authorized_action(RepairOrder, Warden, valid),
    authorized_action(RepairOrder, Engineer, valid).
```

### Lesson

This is the best rule shape so far. GLT-018 proved a rule could fire, but it depended on a combined `authorized_by` property. GLT-019 removed `entity_property/3` from the active rule palette and forced the rule lens to build over role and authorization rows already present in the admitted backbone. The result is a more general two-role condition that still fires exactly once and does not authorize repair order 72.

This is the useful version of semantic parallax for rules: the backbone pass admitted role/action rows, the rule lens saw only the relevant active predicate palette, the mapper admitted the clause, and the runtime trial proved the rule could fire without unsupported body goals or fanout.

## GLT-020 - Tax Rule Timeout Negative Control

- Timestamp: `2026-05-02T19:48:00Z`
- Mode: `tax_rule_active_palette_probe`
- Source span: `story.md:L50`

### Result

- Two tax-rule probes timed out.
- The second probe used a narrower active palette, `operation_target=1`, reduced backbone limits, and a shorter timeout, but still did not return structured JSON.

### Lesson

The tax rule is the next harder rule class: it combines thresholds, exceptions, and class/status distinctions. Brute-force rule prompting is the wrong path for this shape. The compiler should probably defer threshold/arithmetic rules unless the active surface already has helper predicates such as `greater_than/2`, `value_above/3`, or query-only arithmetic support.

This negative control strengthens the rule-lens design: GLT-019 shows role-joined rules can be acquired and fired when the admitted body surface is explicit. GLT-020 shows threshold/exception rules need a different helper-substrate lens rather than more prose pressure.

## GLT-021 - Promotion-Ready Rule Metric

- Timestamp: `2026-05-02T19:54:21Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T195421354789Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `rule_trial_promotion_ready_metric`
- Source span: `story.md:L42`

### Result

- `1` executable rule admitted.
- Runtime rule load errors: `0`.
- Firing rules: `1`.
- High-fanout rules: `0`.
- Unsupported body signatures: `0`.
- Unsupported body goals: `0`.
- Unsupported body fragments: `0`.
- Promotion-ready rules: `1`.

### Lesson

The rule trial now has a compact promotion-readiness diagnostic: a rule is promotion-ready only if it loads, fires at least once, does not fan out above the trial threshold, and has no unsupported body signatures, unsupported body goals, or unsupported body fragments. This does not make the rule durable by itself, but it gives the harness a clean structural score for the next rule-ingestion runs.

## GLT-022 - Numeric Helper Substrate For Tax Rules

- Timestamp: `2026-05-02T20:01:03Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T200103719615Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `numeric_helper_substrate_tax_rule_lens`
- Source span: `story.md:L50`

### Result

- Added deterministic runtime helpers:
  - `value_greater_than(Entity, Threshold)`
  - `value_at_most(Entity, Threshold)`
- `2` executable tax rules admitted.
- Runtime rule load errors: `0`.
- Firing rules: `2`.
- Promotion-ready rules: `2`.
- Dormant rules: `0`.
- Unsupported body signatures: `0`.
- Unsupported body goals: `0`.
- Unsupported body fragments: `0`.

Admitted rules:

```prolog
derived_tax_status(Cargo, taxable, harbor) :-
    entity_property(Cargo, value, Value),
    value_greater_than(Cargo, 100),
    entity_property(Cargo, relief_status, not_relief).

derived_tax_status(Cargo, exempt, harbor) :-
    entity_property(Cargo, value, Value),
    value_at_most(Cargo, 100).
```

### Lesson

GLT-020 showed that threshold/exception rules timed out without a helper substrate. GLT-022 confirms the fix: arithmetic-like rule bodies should use deterministic virtual helper predicates rather than raw comparison operators or more prompt pressure. The helper predicates live in the Prolog runtime/engine layer and resolve from admitted `entity_property(Entity, value, Value)` facts, so Python still does not interpret source prose.

This is not the complete tax rule yet. The high-value relief-cargo exception still needs its own rule/support shape, because the emitted exemption rule covers low-value cargo but not relief cargo valued over 100. The important gain is architectural: threshold rules can now be acquired, loaded, fired, and promotion-scored when the helper substrate is present.

## GLT-023 - Positive/Negative Probe-Gated Role Join

- Timestamp: `2026-05-02T21:10:46Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T211046591005Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `probe_gated_role_join_rule_trial`
- Rule class: `role_join`
- Source span: `story.md:L42`

### Result

- `1` executable rule admitted.
- Runtime rule load errors: `0`.
- Firing rules: `1`.
- Promotion-ready rules: `1`.
- Unsupported body goals: `0`.
- Positive probes: `1/1`.
- Negative probes: `1/1`.
- Unexpected probe solutions: `0`.
- Probe-adjusted promotion ready: `true`.

Positive probe:

```prolog
derived_authorization(repair_order_71, valid, glass_tide_repair).
```

Negative probe:

```prolog
derived_authorization(repair_order_72, valid, glass_tide_repair).
```

### Lesson

GLT-023 makes the GLT-019 claim stronger. It is no longer enough to say that the role-joined rule fires once; the harness now records authored positive and negative Prolog probes after temporary rule loading. The repair rule derives the valid dual-signature repair order and does not derive the one-signer repair order. This formalizes the next lifecycle step: promotion readiness should be probe-gated before a rule is considered for durable admission.

## GLT-024 - Probe-Adjusted Threshold Rule Trial

- Timestamp: `2026-05-02T21:11:00Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T211100855690Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `probe_adjusted_threshold_rule_trial`
- Rule class: `threshold`
- Source span: `story.md:L50`

### Result

- `2` executable rules admitted.
- Runtime rule load errors: `0`.
- Firing rules: `2`.
- Promotion-ready rules: `2`.
- Unsupported body goals: `0`.
- Positive probes: `2/3`.
- Negative probes: `1/1`.
- Unexpected probe solutions: `0`.
- Probe-adjusted promotion ready: `false`.

Passing positive probes:

```prolog
derived_tax_status(glass_eels, taxable, harbor).
derived_tax_status(seed_crystals, exempt, harbor).
```

Missed positive probe:

```prolog
derived_tax_status(lamp_rice, exempt, harbor).
```

Passing negative probe:

```prolog
derived_tax_status(lamp_rice, taxable, harbor).
```

### Lesson

The numeric helper substrate still works, and the taxable/non-taxable threshold rows remain clean. The new probe layer exposes the real remaining edge: high-value relief cargo is correctly not taxable, but the exemption rule is not yet acquired. That means rule promotion cannot rely only on load/firing/body-support checks. Exception-bearing rule classes need positive and negative probes that cover the exception branch, plus probably a dedicated exception lens or helper substrate.

## GLT-025 - Relief-Cargo Exception Branch With Scope Discipline

- Timestamp: `2026-05-02T22:40:21Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T224021055106Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `exception_branch_scope_disciplined_trial`
- Rule class: `exception`
- Source span: `story.md:L50`

### Result

- Source-pass LM Studio calls now send `reasoning_effort="none"` through the shared structured JSON helper, matching the main Semantic IR runtime policy.
- `2` executable exception/low-value rules admitted.
- Runtime rule load errors: `0`.
- Firing rules: `2`.
- Promotion-ready rules: `2`.
- Unsupported body goals: `0`.
- Positive probes: `1/1`.
- Negative probes: `1/1`.
- Unexpected probe solutions: `0`.
- Probe-adjusted promotion ready: `true`.

Passing positive probe:

```prolog
derived_tax_status(lamp_rice, exempt, harbor).
```

Passing negative probe:

```prolog
derived_tax_status(lamp_rice, taxable, harbor).
```

### Lesson

The exception branch was not blocked by source understanding. The first narrow exception run derived `lamp_rice` as exempt, but used `tax_rule_relief` as the third argument instead of the governed scope `harbor`. The authored positive probe caught that right-body/wrong-head-scope error. Adding generic derived-head scope guidance fixed it: scope arguments should name the governed domain, action, or object from the source, not the rule id, proof reason, or clause label.

This is a useful small victory for semantic parallax: the exception lens can acquire the high-value relief-cargo branch when it is isolated from the threshold bundle.

## GLT-026 - Full Tax Bundle Exposes Numeric Helper Misuse

- Timestamp: `2026-05-02T22:40:40Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T224040840534Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `combined_threshold_exception_helper_misuse_trial`
- Rule class: `threshold_exception`
- Source span: `story.md:L50`

### Result

- `4` executable rules admitted.
- Runtime rule load errors: `0`.
- Firing rules: `4`.
- Recomputed promotion-ready rules after verifier hardening: `2`.
- Unsupported body fragments after verifier hardening: `2`.
- Positive probes: `1/3`.
- Negative probes: `1/1`.
- Unexpected probe solutions: `0`.
- Probe-adjusted promotion ready: `false`.

The model emitted the right kind of helper, but used the numeric value variable as the helper subject:

```prolog
derived_tax_status(Cargo, exempt, harbor) :-
    entity_property(Cargo, value, Value),
    value_at_most(Value, 100).

derived_tax_status(Cargo, taxable, harbor) :-
    entity_property(Cargo, value, Value),
    value_greater_than(Value, 100),
    entity_property(Cargo, relief_status, not_relief).
```

The helper contract is entity-based:

```prolog
value_at_most(Cargo, 100).
value_greater_than(Cargo, 100).
```

### Lesson

GLT-026 turns a subtle runtime/query miss into a structural verifier rule. The rule trial now flags `value_at_most(Value, 100)` and `value_greater_than(Value, 100)` when `Value` is the numeric variable from `entity_property(Cargo, value, Value)`. This is not language handling in Python; it is contract verification over proposed Prolog clauses.

The combined tax bundle also remains operationally fragile: a later retry of the same combined shape stalled while the GPU was idle. For the next cycle, keep threshold and exception branches as separate semantic lenses, then accumulate mapper-admitted rules through deterministic union instead of forcing all branches into one LLM pass.

## GLT-027 - Deterministic Rule-Surface Union Beats One-Pass Tax Bundle

- Timestamp: `2026-05-02T23:23:45Z`
- Union artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T232345474313Z_glass-tide-tax-rule-union-glt027_qwen-qwen3-6-35b-a3b.json`
- Source rule artifacts:
  - `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T211100855690Z_story-rules_qwen-qwen3-6-35b-a3b.json`
  - `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T224021055106Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Mode: `deterministic_promotion_ready_rule_union`
- Rule class: `threshold_exception`

### Result

- No source prose read during union.
- No new rules inferred during union.
- `3` accumulated executable rules retained after promotion-readiness filtering.
- Runtime rule load errors: `0`.
- Promotion-ready rules: `3`.
- Unsupported body fragments: `0`.
- Positive probes: `3/3`.
- Negative probes: `1/1`.
- Unexpected probe solutions: `0`.
- Probe-adjusted promotion ready: `true`.

Accumulated rules:

```prolog
derived_tax_status(Cargo, taxable, harbor) :-
    entity_property(Cargo, value, Value),
    value_greater_than(Cargo, 100),
    entity_property(Cargo, relief_status, not_relief).

derived_tax_status(Cargo, exempt, harbor) :-
    entity_property(Cargo, value, Value),
    value_at_most(Cargo, 100).

derived_tax_status(Cargo, exempt, harbor) :-
    entity_property(Cargo, type, relief_cargo).
```

Passing positive probes:

```prolog
derived_tax_status(glass_eels, taxable, harbor).
derived_tax_status(seed_crystals, exempt, harbor).
derived_tax_status(lamp_rice, exempt, harbor).
```

Passing negative probe:

```prolog
derived_tax_status(lamp_rice, taxable, harbor).
```

### Lesson

This is the clearest Glass Tide proof for multi-pass semantic compilation so
far. A forced combined tax pass produced right-looking but helper-misused rules.
Separate threshold and exception lenses each captured a useful safe view.
Deterministic union over mapper-admitted outputs, followed by promotion-ready
filtering and authored probes, produced a stronger accumulated rule surface
than either source pass and stronger than the one-pass bundle.

This is semantic parallax as executable-rule engineering: depth came from
accumulating safe views, not from asking one prompt to see everything at once.

## GLT-028 - Salvage Body-Fact Acquisition Lens

- Timestamp: `2026-05-02T23:28:42Z`
- Body-fact artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T232842128309Z_story-support_qwen-qwen3-6-35b-a3b.json`
- Body/backbone union artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T232859146524Z_glass-tide-salvage-body-union-glt028_qwen-qwen3-6-35b-a3b.json`
- Mode: `salvage_body_fact_lens`
- Source span: `story.md:L130-L132`

### Result

- `5` body facts admitted.
- `0` skipped operations.
- Runtime load errors after deterministic union with the backbone: `0`.

Admitted body facts:

```prolog
recovered_from_water(tomas_reed, blue_salt_crate_c17, 21_10).
abandoned(blue_salt_crate_c17).
not_sacred(blue_salt_crate_c17).
recovered_from_water(nell_quill, bell_of_saint_loam, 21_25).
sacred(bell_of_saint_loam).
```

### Lesson

The original backbone had cargo identities, sacred/not-sacred status, and
locations, but it lacked the actor recovery relation needed by any safe salvage
reward rule. A rule lens alone cannot fix missing body support. GLT-028 adds a
body-fact acquisition lens: same raw source, narrow source span, narrow
rule-body predicate palette, normal mapper admission.

This is not Python NLP. Python selected an authored source span and predicate
palette; the LLM proposed the rows, and the mapper admitted them.

## GLT-029 - Salvage Rule Union With Sacred-Cargo Negative Probe

- Timestamp: `2026-05-02T23:31:04Z`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T233042669249Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Union artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T233104630717Z_glass-tide-salvage-rule-union-glt029_qwen-qwen3-6-35b-a3b.json`
- Mode: `salvage_rule_body_fact_union_trial`
- Rule class: `exception`

### Result

- `2` accumulated executable rules retained after promotion-readiness filtering.
- Runtime rule load errors: `0`.
- Promotion-ready rules: `2`.
- Positive probes: `1/1`.
- Negative probes: `1/1`.
- Unexpected probe solutions: `0`.
- Probe-adjusted promotion ready: `true`.

Accumulated rules:

```prolog
derived_reward_status(Actor, salvage_reward, Cargo) :-
    recovered_from_water(Actor, Cargo, _Time),
    abandoned(Cargo),
    not_sacred(Cargo).

derived_reward_status(Actor, no_salvage_reward, Cargo) :-
    recovered_from_water(Actor, Cargo, _Time),
    sacred(Cargo).
```

Passing probes:

```prolog
derived_reward_status(tomas_reed, salvage_reward, blue_salt_crate_c17).
% and no rows for:
derived_reward_status(nell_quill, salvage_reward, bell_of_saint_loam).
```

### Lesson

GLT-029 confirms that the MPSC pattern transfers beyond tax thresholds:

```text
body-fact lens
-> rule lens
-> deterministic union
-> promotion-ready filtering
-> positive/negative probes
```

The rule lens also tried to emit a negation-based fallback rule using `\+`.
The verifier treated the leftover negation fragment as unsupported, and the
union tool dropped that non-promotion-ready rule. This is exactly the intended
safety posture: bad rule shapes can appear in proposals without becoming part
of the accumulated executable surface.

## GLT-030/031 - Isolated Per-Rule Promotion Trial

- Timestamp: `2026-05-02T23:37:41Z`
- Tax union artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T233741901432Z_glass-tide-tax-rule-union-glt030-isolated_qwen-qwen3-6-35b-a3b.json`
- Salvage union artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T233741869423Z_glass-tide-salvage-rule-union-glt031-isolated_qwen-qwen3-6-35b-a3b.json`
- Mode: `isolated_rule_for_promotion_combined_rules_for_probes`

### Result

Tax rerun:

- `3` executable rules loaded.
- Isolated firing rules: `3`.
- Isolated promotion-ready rules: `3`.
- Positive probes: `3/3`.
- Negative probes: `1/1`.
- Probe-adjusted promotion ready: `true`.

Salvage rerun:

- `2` executable rules loaded.
- Isolated firing rules: `2`.
- Isolated promotion-ready rules: `2`.
- Positive probes: `1/1`.
- Negative probes: `1/1`.
- Probe-adjusted promotion ready: `true`.

### Lesson

The runtime verifier now separates two scopes:

```text
isolated rule trial -> promotion-readiness, firing, dormancy, fanout
combined rule trial -> authored positive/negative probes over the accumulated surface
```

This matters because two sibling rules can share a derived head. A broad head
query such as `derived_reward_status(V1, V2, V3)` can see rows produced by a
previous sibling rule if all rules are already loaded into the same runtime.
Promotion scoring now asks whether each rule fires by itself against the
backbone before the union-level probe pass checks the accumulated behavior.

The previous high-water results held under this stricter verifier: tax stayed
at `3` promotion-ready rules and salvage stayed at `2`.

## GLT-032/034 - Quarantine Temporal Clearance Rule

- Timestamp: `2026-05-02T23:45:45Z`
- Body-fact artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T234156001349Z_story-support_qwen-qwen3-6-35b-a3b.json`
- Body/backbone union artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T234209792368Z_glass-tide-quarantine-body-union-glt032_qwen-qwen3-6-35b-a3b.json`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T234310003740Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Promotion-filtered union artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T234545984607Z_glass-tide-quarantine-rule-union-glt034_qwen-qwen3-6-35b-a3b.json`
- Mode: `quarantine_temporal_helper_rule_trial`
- Rule class: `temporal_window`

### Result

Body-fact lens:

- `8` body facts admitted.
- `0` skipped operations.
- Runtime load errors after deterministic union with the backbone: `0`.

Admitted body facts:

```prolog
quarantine_patient(dax_orr).
no_fever(dax_orr, 10_00).
negative_test(dax_orr, 10_00).
negative_test(dax_orr, 17_00).
quarantine_patient(mira_gale).
no_fever(mira_gale, 12_00).
negative_test(mira_gale, 12_00).
negative_test(mira_gale, 17_00).
```

Rule union:

- `1` executable rule retained after isolated promotion-readiness filtering.
- Runtime rule load errors: `0`.
- Promotion-ready rules: `1`.
- Positive probes: `1/1`.
- Negative probes: `1/1`.
- Probe-adjusted promotion ready: `true`.

Retained rule:

```prolog
derived_clearance_status(dax_orr, cleared, quarantine) :-
    quarantine_patient(dax_orr),
    no_fever(dax_orr, _),
    negative_test(dax_orr, T1),
    negative_test(dax_orr, T2),
    hours_at_least(T1, T2, 6).
```

Passing probes:

```prolog
derived_clearance_status(dax_orr, cleared, quarantine).
% and no rows for:
derived_clearance_status(mira_gale, cleared, quarantine).
```

### Lesson

GLT-032/034 adds the temporal-helper version of the rule-ingestion pattern.
The source says two negative tests must be at least six hours apart. The LLM
owns the body-fact rows and rule proposal; deterministic code supplies the
query-only helper `hours_at_least/3`, admits only mapper-safe clauses, and tests
the rule in isolated runtime scope.

The first quarantine attempt was useful-bad: the LLM proposed the right general
condition, but the mapper blocked generic scope arguments or the verifier
treated `hours_at_least/3` as an unsupported standalone generator. The harness
now distinguishes context-dependent helpers: if an isolated rule fires, the
helper has proven itself inside the conjunction and does not count as an
unsupported body goal.

The retained rule is instance-shaped, not yet a durable generalized quarantine
law. That is still progress: Prethinker can now acquire and verify a
source-faithful temporal clearance consequence while rejecting the Mira case
whose tests were only five hours apart.

## GLT-035/036 - Council Budget-Veto Rule Branch

- Timestamp: `2026-05-02T23:49:27Z`
- Body-fact artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T234841576063Z_story-support_qwen-qwen3-6-35b-a3b.json`
- Body/backbone union artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T234855691562Z_glass-tide-council-body-union-glt035_qwen-qwen3-6-35b-a3b.json`
- Rule artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T234910949153Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Promotion-filtered union artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T234927415542Z_glass-tide-council-veto-rule-union-glt036_qwen-qwen3-6-35b-a3b.json`
- Mode: `council_budget_veto_rule_trial`
- Rule class: `priority_override`

### Result

Body-fact lens:

- `8` body facts admitted.
- `0` skipped operations.
- Runtime load errors after deterministic union with the backbone: `0`.

Admitted body facts:

```prolog
proposal(copper_rails_proposal).
budget_matter(copper_rails_proposal).
supported(copper_rails_proposal, mara_vale).
supported(copper_rails_proposal, juno_vale).
supported(copper_rails_proposal, ilya_sen).
supported(copper_rails_proposal, tomas_reed).
treasurer_veto(copper_rails_proposal, sera_voss).
no_emergency_override(copper_rails_proposal).
```

Rule union:

- `1` executable rule retained after isolated promotion-readiness filtering.
- Runtime rule load errors: `0`.
- Promotion-ready rules: `1`.
- Positive probes: `1/1`.
- Negative probes: `1/1`.
- Probe-adjusted promotion ready: `true`.

Retained rule:

```prolog
derived_status(Proposal, failed, council_budget_veto) :-
    proposal(Proposal),
    budget_matter(Proposal),
    treasurer_veto(Proposal, _),
    no_emergency_override(Proposal).
```

Passing probes:

```prolog
derived_status(copper_rails_proposal, failed, council_budget_veto).
% and no rows for:
derived_status(copper_rails_proposal, passed, council_budget_veto).
```

### Lesson

GLT-035/036 adds the priority/override branch without yet solving vote-count
aggregation. The body-fact lens captured support votes, veto, and explicit
absence of emergency override. The rule lens proposed several branches, but
the verifier retained only the clean veto/failure rule and dropped branches
that required unsupported negation or normal-vote aggregation.

This is the right incremental posture for council voting: acquire and verify
the veto branch first, then add a separate count/aggregation helper substrate
for the normal three-of-five pass rule.
