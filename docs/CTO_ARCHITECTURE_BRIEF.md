# CTO Architecture Brief

Last updated: 2026-05-28

> Status: historical pre-reset orientation. Use
> [Closed Domain Predicate Packs Technical Note](https://github.com/dr3d/prethinker/blob/main/docs/CLOSED_DOMAIN_PREDICATE_PACKS_TECHNICAL_NOTE.md),
> [Active Research Lanes](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md),
> and
> [Domain Pack Research Evidence](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PACK_RESEARCH_EVIDENCE.md)
> for current score posture and operating direction.

This was the fastest orientation for a high-context collaborator before the
domain-pack phase close. Read it as historical architecture context, not as the
current claim-bearing research note.

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

## Current CTO Job

This brief is historical; use the closed-domain technical note for current
score posture. The current CTO job is to preserve the narrow research result
without drifting back into old scoreboard behavior:

1. keep public docs explicit that old 90%+ QA scorecards are historical;
2. keep SEC as the clean methods example for closed skeleton transfer;
3. keep FDA as the richer case study with both positive transfer and boundary
   evidence;
4. keep NTSB as corroborating boundary evidence, not as a new row-grinding
   target;
5. keep fixture-shaped vocabulary, prose-shaped atoms, source-record prose
   routing, and query-text routing out of active prompts/config/code;
6. treat any next experiment as a named research-gap test, not as an attempt to
   recover an old headline number.

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
