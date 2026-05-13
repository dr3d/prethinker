# CTO Architecture Brief

Last updated: 2026-05-12

This is the fastest orientation for a new high-context collaborator. Read it
as the current operating doctrine, not as a research diary.

## Invariant

```text
LLM proposes.
Mapper admits.
KB remembers.
Helpers compose.
Selector chooses.
Answer reports only what support allows.
```

Prethinker is a governed semantic-intake workbench. Its purpose is not to make
an LLM more confident; it is to turn selected language into auditable symbolic
state while preserving the authority boundary.

## Current Shape

- `process_utterance()` in `src/mcp_server.py` is the canonical runtime
  entrypoint.
- `semantic_router_v1` chooses context/profile/action plans; it is context
  selection, not write authority.
- `semantic_ir_v1` is the model-owned semantic workspace.
- `src/semantic_ir.py` owns deterministic mapper admission, projection,
  quarantine, and diagnostics.
- The Prolog KB is the durable truth layer.
- Compiled KB packages are the source-document product: admitted `world.pl`,
  admitted `epistemic.pl`, helper surfaces, manifests, and non-truth
  diagnostics.
- Rows are measurements against frozen artifacts. Rows are not truth.

## Architecture Map

```text
source or utterance
  -> router/profile/context plan
  -> Semantic IR proposal
  -> deterministic mapper admission
  -> KB mutation, query, clarification, quarantine, or rejection
  -> compiled package / trace / ledger
  -> row-level QA, selectors, helpers, and guards over frozen state
```

## Lenses, Ledgers, Helpers, Guards

- **Lenses** are model-owned reading strategies. No one lens should do every
  job.
- **Deterministic ledgers** preserve exact source addressability: IDs, row
  labels, table cells, section names, docket IDs, packet names, and numeric
  tokens. They are substrate, not interpretation.
- **Helpers** compose admitted facts into reusable counts, intervals, joins,
  and derived support. They must not read prose or silently choose ambiguous
  scope.
- **Selectors** choose the best encounter surface for a question.
- **Guards** prevent tempting but wrong selector choices. Treat them as
  sensors and bandages, not the desired final architecture.

## Guard Compression State

Guard compression has reached terminal-audit mode. The active workbench for the
completed compression cycle is `docs/GUARD_GENERALIZATION_WORKSHEET.md`; do not
restart guard retirement just to make the count smaller.

Current selector ledger accounting from the terminal audit:

- `5` active guards
- `0` high-priority `candidate_guard:helper_pressure` entries
- `186` scar guards
- `0` high-priority singleton `candidate_guard` entries
- `4` semantic families
- `0` unclassified reasons

The danger is not raw guard count by itself. The danger is fixture vocabulary
becoming architecture. A good guard can be stated for a never-seen document.
A bad guard remembers local nouns.

Good:

```text
Prefer count-bearing surfaces that bind the requested measure and the question's
event, interval, population, or status scope.
```

Bad:

```text
Prefer Green Group return-coach rows.
```

## Generality Rule

If a proposed fix cannot be described without fixture names, row IDs, local
people, local organizations, or story nouns, it is probably not architecture
yet.

Retire a guard only when its replacement is a reusable substrate, compile
surface, helper, predicate contract, or scoring principle, and replay proves no
regression on the birth row plus unlike rows.

The remaining active guards should be treated as source-fidelity,
baseline-arbitration, or legitimate singleton-sentinel pressure unless a new
boundary hunt proves a transferable replacement.

## Language Boundary

Prethinker has not become English-only as an architecture. The intended split
is still language-flexible:

- the model reads the user's language or the source document's language;
- the router chooses profile/context scaffolding;
- Semantic IR carries structured intent and proposed operations;
- the mapper validates structure, authority, and predicate contracts without
  relying on English phrase matches.

The project should resist Python-side language handling. A multilingual gain
should come from model context, profile contracts, source-addressability
ledgers, or mapper/schema generality, not from hard-coded English wording.

## Retired Lanes

The lab-automation, public benchmarking, and publishing projects are gone from
the active architecture. Git history preserves them. Do not rebuild them or
route new work through them unless the project explicitly reopens that product
question.

OpenRouter parallel-lane pressure is still active research, not retired
benchmarking. "Multi-lane" just means parallel hosted LLM runs over separate
artifacts, like the local 5090 workflow. Keep any setup notes inside the
current architecture, boundary, or guard workbench docs; do not create a
separate OpenRouter process lane unless it becomes real product architecture.

Default future hosted pressure to six lanes. The first wide corpus run at 12
lanes completed QA over successful compiles, but the compile phase hit provider
429s and one incomplete read; treat that as provider evidence, not architecture
failure.

## Next CTO Job

Run the boundary hunt. Use `docs/BOUNDARY_HUNT_WORKSHEET.md` as the live
workbench and `docs/BOUNDARY_PROBE_RESEARCH_METHOD.md` as the doctrine.

The seed measurement is the 2026-05-12 wide OpenRouter corpus run:

- compile attempted `56` source-backed fixtures;
- `32` compile artifacts were produced;
- QA40 over those `32` fixtures completed `1008 / 76 / 134` over `1218`
  questions;
- exact rate was `0.8276`;
- runtime load errors and write proposal rows were both `0`;
- helper pressure was `2877` rows, `2.854` rows per exact answer, and
  `0.1585` candidate-helper share;
- the 210 not-exact rows are boundary coordinates, not permission for
  fixture-specific tuning.

Start with class-level boundary work:

1. Classify not-exact rows by fixture-free failure geometry, especially
   compile-surface, hybrid-join, query-surface, answer-surface, source-fidelity,
   helper-volume, and judge-ambiguity pressure.
2. Design small probe fixtures that isolate one tricky axis at a time.
3. Repair only when the replacement can be stated without fixture names, row
   ids, question ids, answer strings, local people, local organizations, or
   story nouns.
4. Replay on unlike rows before promoting any helper, predicate, query-plan, or
   selector principle.

## Repo Hygiene

- `tmp/` is scratch only. It should stay empty except for ad hoc handoffs and
  local experiments.
- Durable but non-day-to-day artifacts belong under
  `C:\prethinker_tmp_archive`.
- Commit source, tests, compact durable docs, guard ledger/rollup sidecars, and
  small public assets that docs actually reference.
- Do not commit generated run dumps, test caches, licensed UMLS assets, or
  one-off selector replay output.

## Progress Journals

Maintain a journal entry for every meaningful research slice. Fixture-specific
work belongs in that fixture's `progress_journal.md`. Cross-harness boundary
work belongs in `docs/BOUNDARY_HUNT_WORKSHEET.md`. The guard worksheet is now
the compression archive unless a boundary hunt reveals a new transferable guard
replacement.

Each entry should capture the date, the changed surface, the measured result,
the artifact path when useful, the tests run, and the architecture lesson. It
must also show trajectory: the prior pressure, the intervention, the new
measurement, and the next pressure. Do not journal story nouns as architecture;
phrase the lesson at the reusable substrate, selector, helper, or ledger level.
