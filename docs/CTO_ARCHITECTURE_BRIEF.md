# CTO Architecture Brief

Last updated: 2026-05-28

This is the fastest orientation for a new high-context collaborator. Read it
as the current operating doctrine, not as a research diary.

## Invariant

```text
LLM proposes.
Mapper admits.
KB remembers.
Ledgers pin source coordinates.
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
  admitted `epistemic.pl`, deterministic ledgers, direct query surfaces,
  manifests, and non-truth diagnostics.
- Rows are measurements against frozen artifacts. Rows are not truth.

## Architecture Map

```text
source or utterance
  -> router/profile/context plan
  -> Semantic IR proposal
  -> deterministic mapper admission
  -> KB mutation, query, clarification, quarantine, or rejection
  -> compiled package / trace / ledger
  -> row-level QA, selectors, direct surfaces, ledgers, and guards over frozen state
```

## Lenses, Ledgers, Surfaces, Guards

- **Lenses** are model-owned reading strategies. No one lens should do every
  job.
- **Deterministic ledgers** preserve exact source addressability: IDs, row
  labels, table cells, section names, docket IDs, packet names, and numeric
  tokens. They are substrate, not interpretation.
- **Direct surfaces** are admitted predicates and deterministic ledger facts
  that make recurring roles, statuses, quantities, transitions, and authority
  envelopes queryable without query-time compatibility bridges.
- **Retired compatibility adapters** are forensic replay tools. They are not
  the preferred repair path.
- **Selectors** choose the best encounter surface for a question.
- **Guards** prevent tempting but wrong selector choices. Treat them as
  sensors and bandages, not the desired final architecture.

## Guard Compression State

Guard compression has reached terminal-audit mode. The completed compression
workbench was moved out of the front-door docs into cold archive/Git history;
do not restart guard retirement just to make the count smaller.

Current selector ledger accounting from the terminal audit:

- `5` active guards
- `0` high-priority compatibility-pressure entries
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
Prefer this fixture's return-coach rows.
```

## Generality Rule

If a proposed fix cannot be described without fixture names, row IDs, local
people, local organizations, or story nouns, it is probably not architecture
yet.

Retire a guard only when its replacement is a reusable substrate, compile
surface, deterministic ledger, predicate contract, or scoring principle, and
replay proves no regression on the birth row plus unlike rows.

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

The next CTO job is to preserve the publishable measurement claim while
continuing the next investigation cycle.

Current native fixed-compile direct-surface anchor:

- `2163` judged rows;
- `1997 exact / 46 partial / 120 miss`;
- `92.33%` exact;
- `0` compatibility rows;
- `0` runtime load errors;
- `0` write proposal rows.

Current transfer anchors:

- fresh ugly public 2026-05-28 R1: `197 / 3 / 0` over `200` rows (`98.5%`
  exact), with `0` compatibility rows, `0` runtime load errors, and `0` write
  proposal rows; compile gate still held at `2 / 6` old pass/hold and
  `4 / 6 / 0` blocking/diagnostic/advisory holds;
- fresh ugly public Batch 03 latest guarded slices: SEC `75 / 0 / 0`, non-SEC
  `216 / 6 / 3`, slice-combined current view `291 / 6 / 3` over `300` rows
  (`97.0%` exact), with `0` compatibility rows, `0` runtime load errors, and
  `0` write proposal rows; not a single fresh 300-row rerun;
- four externally sourced real-world fixtures: latest fixture-level
  `160 / 0 / 0`, with `4 / 4` compile gates clean;
- sealed unseen authored transfer: `152 / 1 / 6` over `160` rows (`95.0%`
  exact);
- earlier cold transfer baseline: `177 / 10 / 53` over `240` rows (`73.75%`
  exact).

Recent cleanup retired compatibility-era public artifacts, stale guard-rollup
surfaces, old selector mode labels, and prompt-facing terminology that made
retired compatibility adapters look like active architecture.

Continue only if you find one of these:

1. stale public docs or dead links;
2. fixture-shaped vocabulary in active prompt/config surfaces;
3. fresh stamp artifacts that still expose retired compatibility-adapter terms;
4. active code paths that would re-enable compatibility adapters by default.

The next-cycle investigation is May 28 R1 residue, source-record/query surface
boundaries, and native compile-gate tiering. The old native gate
headline shifted `26 / 30 -> 9 / 47` pass/hold; current tooling also separates
blocking, diagnostic, and advisory reasons. Do not hide those caveats; they are
part of the audit discipline that makes the measurement credible.

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
work belongs in that fixture's `progress_journal.md`. Cross-harness lessons
should be summarized in compact current docs when they become architecture; the
detailed worksheets live in Git history or `C:\prethinker_tmp_archive`.

Each entry should capture the date, the changed surface, the measured result,
the artifact path when useful, the tests run, and the architecture lesson. It
must also show trajectory: the prior pressure, the intervention, the new
measurement, and the next pressure. Do not journal story nouns as architecture;
phrase the lesson at the reusable substrate, direct-surface, selector, or
ledger level.
