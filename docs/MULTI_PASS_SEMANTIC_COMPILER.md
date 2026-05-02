# Multi-Pass Semantic Compiler

Last updated: 2026-05-02

This note captures the current architecture direction exposed by the Anaplan
and Glass Tide experiments.

## Thesis

A single LLM compile is a viewpoint. Prethinker should not optimize for one
perfect giant pass. It should accumulate multiple mapper-admitted semantic
views:

```text
source
  -> backbone lens
  -> support/source lens
  -> temporal/status lens
  -> rule lens
  -> mapper admission per lens
  -> deterministic safe-surface union
  -> Prolog query/trial surface
```

The invariant does not change:

```text
LLMs propose.
The mapper admits.
Only admitted clauses accumulate.
Python does not read prose to derive meaning.
```

## Formal Complement: Semantic Determination Audit

The shortcut-freeness literature gives a useful warning for this architecture:
passing structural constraints is not the same as having the intended meaning.
A candidate can be right-shaped but wrong-meaning:

- `approved` might mean a claim status, a reviewer action, or a payment release;
- an allegation can be collapsed into a finding;
- a binary event predicate can pass arity/type checks while its argument roles
  are inverted;
- two profile-valid predicate surfaces can answer different questions from the
  same admitted-looking rows.

The multi-pass compiler should eventually include a deterministic semantic
determination audit over structured candidates and profile contracts:

```text
structured candidate alternatives
  -> finite-domain validation over profile pins/contracts
  -> search for another valid mapping
  -> admit invariant rows, hold/clarify shortcut-sensitive rows
```

This is not runtime NLP. Python or an ASP/CSP backend may enumerate structured
alternatives, validate constraints, and report shortcut witnesses. It must not
derive the alternatives from raw prose. The LLM proposes alternatives; profile
contracts and mapper policy determine which mappings are admissible.

In Prethinker terms, predicate aliases, argument-role contracts, source-status
validators, and clarification answers are **pins**. They reduce the space of
valid-but-wrong mappings without weakening the authority boundary.

## Why This Exists

APR proved that a deterministic union of safe compiles can beat either compile
alone. The high-water Anaplan path reached `42 exact / 1 partial / 0 miss` by
accumulating independently admitted backbone/support surfaces.

Glass Tide then showed the rule-ingestion version of the same lesson:

- A single default compile preserved charter rules as source records, but
  admitted `0` executable rules.
- Adding rule pressure to that same broad compile regressed the admitted
  surface and still admitted `0` executable rules.
- A separate rule lens admitted executable clauses, but runtime trial exposed
  two new risks: overgeneralized class-predicate fanout and dormant rules whose
  bodies had no matching backbone facts.
- The latest Glass Tide rule trials added active predicate palettes,
  body-goal support checks, lifecycle labels, and authored positive/negative
  probes. GLT-023 has a role-joined repair rule that derives
  `derived_authorization(repair_order_71, valid, glass_tide_repair)` and does
  not derive the one-signer repair order. GLT-024 has threshold tax rules that
  pass high-value/low-value probes but fail the high-value relief-cargo
  exemption probe.

So the next architecture is not "more prompt." It is pass specialization.

## Initial Lenses

Start with four lenses, not twelve.

### Backbone Lens

Captures the central source surface:

- people, roles, places, objects, source documents
- core events and statuses
- recommendations or requirements
- source-stated rule records
- basic claims and evidence rows

It should avoid deep rationale, speculative rules, and broad inferred
consequences.

### Support / Source Lens

Adds reasons, effects, tradeoffs, exceptions, and source-priority support to an
already-admitted backbone. It should not invent a new domain surface.

### Temporal / Status Lens

Extracts state changes, time anchors, validity windows, temporal order,
deadlines, and duration helpers. This lens exists because temporal detail tends
to crowd out ordinary fact extraction when mixed into one giant pass.

### Rule Lens

Converts explicit source-stated conditional guidance into executable rule
candidates. The first rule-lens implementation is
`scripts/run_rule_acquisition_pass.py`.

Rule candidates must:

- use `operation="rule"`
- include a one-line `candidate_operations[].clause`
- use only allowed predicates
- keep head variables bound in the body
- use uppercase Prolog variables when a value should bind across the head and
  body
- avoid class-predicate fanout
- avoid permission-from-occurrence collapse
- avoid claim-to-finding collapse
- match body-goal argument patterns against admitted support rows
- pass mapper admission before runtime trial

## Safe-Surface Accumulation

Union is deterministic and operates only on mapper-admitted clauses:

```text
admitted facts
admitted rules
admitted queries
admitted retraction plans
```

It does not read source prose, infer new clauses, or consult answer keys.

Current utility:

```text
scripts/union_domain_bootstrap_compiles.py
```

## Runtime Trial

Executable rules need a second diagnostic beyond admission:

```text
Can the rule load?
Does it fire?
Does it fan out too broadly?
Does it derive from the intended support rows?
Does it pass authored positive and negative probes?
```

The first rule-lens script records runtime load errors, derived-head query
rows, firing-rule count, high-fanout count, unsupported body signatures, and
unsupported body goals/fragments. It also accepts authored positive and
negative Prolog probes. These are diagnostics, not automatic truth decisions.
The script now wraps LM Studio calls in a hard child-process deadline, so a
stalled local model call returns a clean failed artifact instead of leaving a
runaway Python process in the workspace.

Rule lifecycle is now reported separately:

```text
candidate_rule
mapper_admitted_rule
runtime_loadable_rule
firing_rule
promotion_ready_rule
durable_rule
```

A rule is currently counted as promotion-ready in the temporary trial only when
it loads, fires at least once, stays below the fanout threshold, and has no
unsupported body signatures, goals, or fragments. Promotion-ready is still a
diagnostic label; durable rule admission remains a separate product decision.
Probe-adjusted promotion readiness additionally requires all supplied positive
and negative probes to pass.

## Open Problems

- Pass planner: the router should choose lenses and source spans instead of
  dumping a full document into every pass.
- Rule verifier: admitted rules need checks for fanout, dormant bodies,
  unsupported body predicates, unsupported body-goal argument patterns, and
  unsupported body fragments such as equality/comparison leftovers. Positive and
  negative probes should become standard for any rule class that might
  overgeneralize.
- Helper substrate: threshold/exception rules such as taxability need
  deterministic helper predicates before the rule lens can safely emit
  executable clauses. Glass Tide now uses `value_greater_than/2` and
  `value_at_most/2` as query-only helpers resolved from admitted value facts.
- Exception substrate: GLT-024 shows threshold helpers are not enough for
  exception branches. Relief-style exemptions need either a dedicated exception
  lens or a bounded helper shape.
- Scope and placeholder discipline: recent preflight runs showed that a
  role-joined rule can be body-supported but still fail probes if the model uses
  a neighboring scope atom, or can be syntactically admitted but dormant if it
  uses lowercase role placeholders such as `warden` and `repair_order` instead
  of variables or admitted source atoms.
- Predicate surface: rule bodies need a backbone with enough explicit
  status/evidence/temporal predicates to fire without inventing facts.
- Conflict-aware union: multiple admitted lenses may produce compatible
  distinctions, synonym drift, or direct conflicts.
- Metrics: track QA lift per admitted clause, duplicate rate, conflict rate,
  firing-rule count, high-fanout count, and rule-derived answer count.

## Current Lesson

The right target is not one perfect compile.

The right target is a governed symbolic surface built from multiple safe,
auditable semantic lenses.
