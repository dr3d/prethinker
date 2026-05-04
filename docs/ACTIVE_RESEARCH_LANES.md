# Active Research Lanes

Last updated: 2026-05-03

This page is the short operational map for choosing the next few hours of work.
It is intentionally stricter than a brainstorm: new ideas belong here only if
they advance multiple fixtures or protect the evidence quality of the project.

## Selection Rule

Prefer work that satisfies at least one of these:

- improves two or more cold fixtures without oracle context;
- improves one hard fixture and preserves regression fixtures;
- reduces a dominant cross-fixture failure surface;
- improves public/demo behavior without weakening the mapper authority boundary;
- makes future GPU runs cheaper or easier to interpret.

Avoid work that only raises one fixture score by adding input-specific hints,
gold KB vocabulary, answer-shaped strategy, or Python prose interpretation.

## Current Priority Order

| Priority | Lane | Why It Matters Now | Good Next Move |
| ---: | --- | --- | --- |
| 1 | Source-surface acquisition | Cold rollup shows compile gaps dominate: `159` compile gaps versus `35` hybrid/reasoning, `26` query, and `5` answer gaps. | Improve compact acquisition/lens coverage and replay against unlike fixtures such as Oxalis, Three Moles, Calder, and Avalon. |
| 2 | Rule composition and promotion | Product power comes from executable inference, but cold fixtures still admit `0` rules by default. Glass Tide proved the staged path. | Generalize body-fact -> rule-lens -> shortcut-audit -> probe workflow to Avalon/Sable/Oxalis without fixture-specific clauses. |
| 3 | Temporal/status/reasoning helpers | Regulatory, grant, ledger, recall, and story fixtures all need dates, intervals, deadlines, status-at-time, threshold, and exception helpers. | Add helper substrates only when two fixtures need the same helper shape. |
| 4 | Clarification and stenographer mode | Live UI use is streaming, not monolithic. CE and queued delivery protect truth while reducing interruption. | Build fixtures/runs that score queued-slot closure, safe partials, and later-turn resolution. |
| 5 | Query-surface selection | APR showed the KB can contain the answer while the query planner fails to ask for it. | Apply row-level/evidence-mode selectors after compile/reasoning changes, not as a substitute for missing source surface. |
| 6 | Anti-meta-rot cold replay | The harness must not become good only at its favorite fixtures. | Every general harness change should replay at least two cold fixtures and one older regression fixture. |
| 7 | Public research narrative | Visitors need to understand the newest real insight without drowning in run history. | Keep docs headline/current-lanes pages current; push journals after meaningful runs. |
| 8 | Domain expansion lanes | UMLS, CourtListener, SEC/contracts, and future finance/metathesaurus-style packs matter, but they should not distract from core compiler/governance lessons. | Advance when a domain pack tests a general admission, ontology, or rule-boundary problem. |

## Current Evidence

Cold baseline snapshot across `10` held-out fixtures:

```text
questions: 470
exact / partial / miss: 245 / 81 / 144
exact rate: 0.521
exact+partial rate: 0.694
failure surfaces:
  compile: 159
  hybrid/reasoning: 35
  query: 26
  answer: 5
```

This says the most useful next work is not a UI flourish, a broader prompt, or
a single fixture registry. The broadest payoff is better acquisition of the
right source surface, followed by reusable reasoning/rule substrates.

## Representative Fixtures

Use small sets rather than the whole zoo for each cycle:

| Cycle Type | Fixtures | Why |
| --- | --- | --- |
| Compile acquisition | Oxalis, Three Moles, Calder, Avalon | Regulatory deadlines, story causality, long state ledger, grant rows. |
| Rule composition | Glass Tide, Avalon, Sable Creek | Existing rule doctrine plus two fresh governance variants. |
| Temporal/status | Iron Harbor, Oxalis, Dulse, Ridgeline | Deadline, recall, ledger debt, fire/notice timing. |
| CE/stenographer | Clarification Eagerness Trap plus a turnstream variant | Ask/queue/hold/resolve behavior under authority boundaries. |
| Anti-regression | Iron Harbor, APR, CE, Glass Tide | Older successes that should not silently degrade. |

## GPU Cycle Template

Each long work block should look like this:

1. Pick one cross-cutting failure surface.
2. Choose two or three representative fixtures.
3. Run the smallest diagnostic replay that can show movement.
4. If a change helps only one fixture, label it fixture-local and do not make it default.
5. If it helps more than one fixture, promote the harness change and run targeted regression.
6. Record numbers in the fixture journal and public state summary.
7. Push after tests pass.

## Current Best Next Bite

Work on source-surface acquisition with rule/reasoning readiness in mind:

```text
target = compact acquisition coverage that improves unlike fixtures
first probes = Oxalis + Three Moles + Avalon
guardrails = no source-specific predicate clues, no gold KB, no QA-derived context
success = at least two fixtures improve or one improves with zero regression
```

That lane advances the most other lanes because better source rows feed rules,
temporal helpers, query planning, CE decisions, and public demos.

Current update: Three Moles improved when source_entity_ledger_v1 added
powerless `coverage_targets`, but an anti-meta-rot replay on Oxalis regressed
when the partial-skeleton recovery instruction was global. Keep that recovery
scoped to ledger-backed narrative passes until another unlike fixture shows
positive transfer.

Activation update: query-mode selection now has deterministic structural and
hybrid structural+LLM controls. The hybrid path saves LLM calls on confident
rows and reached Avalon's Rule8 comparison upper bound (`27 exact / 12 partial
/ 1 miss`) while using structural choice on `13/40` rows. It regressed Three
Moles and Sable because LLM fallback overrode structurally exact relaxed
evidence, so hybrid selection remains diagnostic-only until uncertainty gating
transfers across unlike fixtures.
