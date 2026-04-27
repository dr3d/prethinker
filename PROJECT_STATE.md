# Project State

Last updated: 2026-04-27

## One-Sentence Shape

Prethinker is a governed natural-language-to-Prolog workbench: neural models propose semantic workspaces, deterministic gates decide what can become durable KB state, and the UI shows that process live.

## Current Center

- Runtime: `src/mcp_server.py`, especially `process_utterance()`.
- Current pipeline reference: `docs/CURRENT_UTTERANCE_PIPELINE.md`.
- UI: `ui_gateway/`, served locally by `python ui_gateway/main.py` using the stdlib `ThreadingHTTPServer`.
- Active profile: `medical@v0`; active profile-lane experiments: `legal_courtlistener@v0` and `sec_contracts@v0`.
- Active research asset: local UMLS Semantic Network KB built from `sn_current.tgz`.
- Active architecture pivot: opt-in `semantic_ir_v1` compiler path using `qwen3.6:35b-a3b` through LM Studio/OpenAI-compatible structured output.
- Current demonstration surface: prompt-book UI plus live ledger cards showing route, semantic workspace, deterministic admission, clarification, blocked execution, and KB mutation outcomes.

## What Works Now

- The medical profile normalizes a bounded predicate palette: medication use, conditions, symptoms, allergies, lab tests, lab result states, and pregnancy.
- Clarification turns can prevent unsafe patient or lab-test guesses.
- Clarified medical restatements can now recover useful KB writes, such as resolving vague pressure language into a high blood-pressure measurement.
- Session reset now clears pending clarification, recent runtime memory, trace state, and runtime KB state.
- The UI can demonstrate write routes, query/clarification routes, mutation telemetry, and prompt-book-driven examples.
- The UMLS Semantic Network builder produces local Prolog facts for semantic types, semantic relations, structural rows, and inherited relation closures.
- The opt-in semantic IR runtime path can route and commit safe direct assertions without running the legacy parse-side English rescue chain.
- The current semantic IR edge battery shows `qwen3.6:35b-a3b` holding difficult provenance, temporal, exception, correction, and counterfactual distinctions with `20/20` decision labels and `0.976` average score in runtime A/B.
- A 10-case weak-edge fix pass now reaches `10/10` decision labels and `1.000` average score, with zero non-mapper parse rescues.
- Silverton probate packs are intentionally hard frontier batteries for claim/fact separation, identity ambiguity, temporal intervals, noisy spelling, multilingual fragments, and policy-label calibration. They are pressure gauges, not polished demo headlines yet.
- `medical@v0` now owns its UMLS semantic-group argument contracts in the profile manifest, so medical type steering stays profile-specific instead of leaking into the generic semantic IR mapper.
- The semantic IR mapper now has a structural placeholder-argument guard for writes and a minimal temporal fact vocabulary for dates, intervals, and temporal corrections.
- The semantic IR contract now allows `operation=rule` candidates to carry an executable `clause`, which lets structured-output model runs produce durable Prolog rules instead of only recognizing rule-like language.
- Runtime admission now has a first stored-logic conflict guard: likely-functional current-state overwrites and simple `may_*`/`cannot_*` modal contradictions are blocked before mutation.
- Local model-family testing now shows model choice still matters even with LM Studio structured output: Qwen 9B remains a strong small baseline, Nemotron underfits the current contract, and Gemma 26B is a serious different-family challenger.
- The A/B harness now separates exact decision labels, safe outcomes, semantic extraction score, and final KB safety, so hard packs can distinguish product-policy misses from unsafe KB writes.
- The noisy Silverton frontier improved through structural mapper policy: query-scoped identity premises stay out of the KB, initial-only person aliases project state writes to `mixed`, and claim-only wrappers with unsafe implications project to `quarantine`.
- Semantic IR candidate operations now go through deterministic predicate-palette admission. Out-of-palette assert/query/retract/rule predicate signatures are skipped with diagnostics before they reach the legacy parse shape.
- The final noisy Silverton miss was repaired by projecting speculative ambiguous observations with no safe operation to `quarantine`.
- The Harbor frontier pack now has admission-level contracts for selected scenarios: expected admitted facts/retracts/queries, forbidden admitted facts, skipped operations, and skip reasons.
- Predicate contracts can now be supplied in Semantic IR input payloads so a predicate's argument roles and ordering are explicit instead of being hidden in test expectations.
- The mapper now enforces obvious predicate-contract argument role mismatches. This extends palette admission from "is this predicate name/arity allowed?" to "do the proposed arguments fit the contract shape?", while leaving domain vocabulary in profile packages.
- Profile packages can now carry declarative admission validators on predicate contracts. The first legal and SEC validators block allegation-shaped `finding/4`, citation/unclear `holding/3`, obligation-shaped `breach_event/2`, and unevidenced `condition_met/2` proposals without baking those rules into the generic mapper.
- The mapper now has a first temporal sanity gate for interval facts: a proposed `interval_start/2` plus `interval_end/2` pair with parseable dates is skipped if the start is after the end.
- Admitted Semantic IR clauses now carry first-pass support records from mapper operation to runtime payload. Each support record includes the originating operation index, predicate, source, polarity, and rationale codes, giving the trace a seed for future dependency/truth-maintenance work.
- `semantic_ir_v1` now has a first-class `truth_maintenance` proposal block. The large model can propose support links, conflicts, retraction plans, and derived consequences; the mapper only copies that structure into diagnostics/traces and still admits durable effects exclusively from `candidate_operations`.
- Admission diagnostics now compare the model's `truth_maintenance` proposal against mapper outcomes. Trace reports show support/conflict/retraction/consequence counts plus fuzzy edges such as admitted operations without model support, skipped operations with model support, conflict-policy mismatches, and retraction-plan/admitted-retract mismatches.
- Semantic IR calls now receive a compact deterministic `kb_context_pack`: exact relevant KB clauses, likely functional current-state candidates, entity candidates, recent committed logic, and a small fallback snapshot. This gives the 35B model current-KB visibility for corrections and conflict reasoning without granting it write authority.
- `kb_context_pack` now includes role-aware `current_state_subject_candidates`, and the Semantic IR prompt payload carries explicit `kb_context_policy` guidance. This teaches the model how to use retrieved KB state for correction, pronoun resolution, claim-vs-observation boundaries, and conflict explanation without expanding Python-side language patches.
- `scripts/run_semantic_ir_lava_sweep.py` now provides a broad mixed-domain lava harness. It balances scenario sources, generates typo/bad-grammar/context-switch variants, can repeat temperature-0 runs for signature variance checks, applies admitted writes to a private stream KB, and records admitted queries without executing them by default so recursive toy-Prolog queries cannot monopolize CPU.
- The console now defaults to the current LM Studio Semantic IR lane (`qwen/qwen3.6-35b-a3b`) instead of the older 9B/Ollama parser path. Freethinker remains off and is no longer part of the mainline research path.
- Long story-like utterances in the UI can use segmented Semantic IR ingestion: the gateway splits the narrative into focused segments, processes each through the canonical `process_utterance()` path, dedupes applied mutations, and exposes segment-level workspace/admission traces.
- Mixed long utterances can now segment at query boundaries, so questions do not pile up in the same semantic workspace as surrounding write facts.
- The generic predicate registry now includes a small story-world event/state palette (`tasted/2`, `sat_in/2`, `lay_in/2`, `broke/1`, `asleep_in/2`, `was_tasted/1`, `was_eaten/1`, `was_sat_in/1`, `was_lain_in/1`, etc.) so narrative ingestion no longer has to squeeze ordinary events into `inside/2`, `at/2`, or `carries/2`.
- The mapper now blocks placeholder-like durable write arguments such as `unknown_agent`, while the prompt steers unknown-actor observations toward passive object-state predicates when those are available.
- `medical@v0` Semantic IR calls now receive profile-owned predicate contracts and compact UMLS bridge context before the model proposes a workspace. This lets the model normalize examples like `Coumadin` to `warfarin` and see argument-role/semantic-group expectations, while the deterministic mapper still owns admission.
- The profile context now explicitly treats an explicit named patient as sufficient grounding for the research profile, while pronouns, multiple candidates, aliases, and missing patient identity still require clarification.
- A thin domain-profile roster now exists in `modelfiles/domain_profile_catalog.v0.json` and is included in Semantic IR input as `available_domain_profiles`. This is the first skill-directory-style control-plane hook: it advertises possible profile contexts without loading every thick package or authorizing writes.
- `active_profile=auto` now has a first deterministic catalog selector. It chooses a profile from the thin roster, loads only that profile's thick context/contracts for the Semantic IR call, and records the selected profile plus reasons in the trace. A synthetic switch test covers medical -> legal -> SEC/contracts -> medical.
- The auto selector now also consumes explicit per-turn Semantic IR context, so research runners can test the "story so far + new sentence" shape without smuggling that context into the utterance text.
- Profile packages now own declarative `selection_keywords` in addition to thin roster hints. The selector can use those profile-owned hints while the mapper still owns admission.
- A mixed-domain agility harness now lives at `scripts/run_mixed_domain_agility.py`. It randomizes Goldilocks, Glitch, Ledger, Silverton, Harbor, CourtListener, SEC/contracts, and medical scenarios through `active_profile=auto` so profile switching can be tested as a stream rather than isolated lanes.
- Declarative starter profile packages now exist for exploration: `modelfiles/profile.story_world.v0.json`, `modelfiles/profile.probate.v0.json`, and `modelfiles/profile.legal_courtlistener.v0.json`. They provide mock thick context and predicate contracts for future routing experiments without changing runtime admission authority.
- The legal/probate/SEC starter profiles now carry a broader profile-owned predicate surface for the current frontier packs: legal source documents, access logs, relative-date anchors, interval facts, probate guardianship/conditional-gift facts, and contract-like clearance/lock/stock state.
- The mapper now collapses duplicate admitted candidate operations. This catches schema-cap repetition floods without teaching Python any story-specific language.
- A first-pass CourtListener adapter shell now lives under `adapters/courtlistener/`. It includes a conservative token-based REST client, normalizer, legal predicate contracts, harness conversion, README, and an offline synthetic legal seed fixture for claim/finding, citation, role-scope, docket, and identity-boundary tests.
- First CourtListener live smoke generated ignored `breach of lease` and `summary judgment` harness slices and ran legal Semantic IR cases through LM Studio. All emitted valid JSON; the legal palette preserved claim/finding, citation-not-endorsement, docket-not-holding, role-scope, and ambiguous judge identity boundaries.
- `sec_contracts@v0` is now the third large starter domain. It targets SEC/EDGAR and contract-obligation intake: filing/exhibit provenance, party roles, obligations, rights, conditions, effective/termination triggers, and breach-event boundaries.
- A first-pass SEC EDGAR adapter shell now lives under `adapters/sec_edgar/`. It requires `SEC_USER_AGENT` for live calls, caches raw responses locally, emits harness cases, and includes an offline synthetic fixture for obligation-not-fact and condition-not-event tests.
- First SEC live smoke generated ignored Apple/Microsoft filing harness data and ran 11 Semantic IR cases through LM Studio. All emitted valid JSON; adding `filer_of/2` fixed an initial palette gap where filing metadata was being squeezed into `party_to_contract/3`.
- A new held-out cross-turn frontier proposal lives at `docs/data/frontier_packs/semantic_ir_cross_turn_frontier_pack_v1.json`. It targets identity drift, claim/observation separation, noisy multilingual corrections, mixed rule/query/fact turns, temporal corrections, and domain type ambiguity.

## Local UMLS Assets

Kept locally and ignored:

- `tmp/licensed/umls/2025AB/NET/`
- `tmp/licensed/umls/2025AB/semantic_network_kb/`
- `tmp/licensed/umls/2025AB/prethinker_mvp/`

Removed from the workspace cleanup because they are large and reproducible from external source storage:

- full UMLS zip archives
- extracted full Metathesaurus `META/`
- transient run directories, coverage HTML, caches, and trace logs

## Semantic Network KB

The current builder creates a fuller KB than the original nine medical profile predicates. The local Semantic Network output includes:

- 127 semantic types
- 54 semantic relations
- 597 structural relation rows
- 6,217 inherited UI relation facts
- 6,217 inherited name relation facts

This is the next useful layer for type steering and explanation. It should support demos like "why did this medication normalize this way?" or "what semantic family does this lab-test concept belong to?" without turning the app into a broad medical diagnosis system.

## Near-Term Frontiers

- Make the prompt-book examples meatier: each demo should show an utterance, the expected clarification or commit behavior, and the reason it is safer than a plain chatbot answer.
- Wire more Semantic Network explanations into the UI, especially type ancestry and relation paths.
- Keep improving reset/session hygiene so first utterances after reset cannot inherit stale entity context.
- Expand the medical profile only when the new predicate earns its place through tests and a clear demo.
- Keep measuring guardrail dependency directly: compare old pipeline rescue-hook use against semantic IR direct coverage on Glitch, Ledger, medical ambiguity, and temporal packs.
- Push the remaining mapper frontier: durable rule admission for quantified exception language, better decision-label calibration for safe partial commits, and cleaner nested event predicate shapes.
- Represent temporal facts durably enough that extracted dates, intervals, corrections, and relative-time anchors can support real KB queries instead of staying only in the semantic workspace.
- Keep profile contracts out of the generic mapper: profile packages should own domain type/grounding policy, while the mapper stays structural and auditable.
- Treat richer domain context as a catalog/skill mechanism, not hardwired prompt drift. The current auto selector is deterministic and measured; next steps are multi-profile turns, selector confidence UX, and deciding when mixed-domain utterances should be segmented before Semantic IR.
- Grow deterministic stored-logic admission beyond the first guard: profile-declared functional predicates, temporal scope, negation policy, and richer contradiction probes are still open.
- Grow clause support records and the new `truth_maintenance` proposal block into a real dependency layer: derived conclusions should eventually point to supporting facts, rules, source documents, and retractions without granting model-proposed consequences write authority.
- Use the new truth-maintenance/admission delta as a regular frontier metric: the next good improvements should reduce fuzzy edges by improving model workspace quality, profile contracts, or predicate surfaces, not by adding English phrase patches.
- Expand `kb_context_pack` carefully under context-budget pressure: first measure correction/conflict gains, then consider ranked retrieval controls, ontology slices, source-priority summaries, and explicit KB/world manifests.
- Extend predicate-contract enforcement beyond obvious structural mismatches: more reusable profile validators, profile-owned type contracts, declared functional predicates, temporal scope, and better UI surfacing for skipped operations.
- Promote scenario-local predicate contracts into reusable profile/predicate manifests so fewer expectations live only inside individual frontier packs.
- Expand trace views around admission contracts so reviewers can see not only the model decision, but also which exact boundary checks passed.
- Build a new held-out frontier pack instead of over-polishing Silverton: cross-document temporal causality, aliases, corrections, disputed claims, and profile type pressure.
- Port the new cross-turn frontier pack into a runner only after deciding which expectations should be hard regression gates versus research pressure gauges.
- Expand auto profile-selection tests from clean synthetic switching into messy mixed-domain turns. Profile selection is still advisory context loading, not admission authority.
- Use the mixed agility harness as a regular pressure gauge. The next useful failures are not JSON validity; they are wrong profile selection, vague story predicates, placeholder/null write arguments, and mapper policy for partially good operations.
- Keep argument-role validation structural. The mapper now catches clear cases like `interval_start/2` receiving a date in the interval slot; the next useful gains are reusable contracts and richer profile validators, not phrase patches.
- Keep expanding the CourtListener lane with small live API slices and curated synthetic boundaries. Generated live data remains ignored under `datasets/courtlistener/generated/` unless a tiny fixture is intentionally curated.
- Run the SEC adapter against a small EDGAR submissions slice only after setting `SEC_USER_AGENT` and choosing a durable cache/review policy. Keep generated live data under ignored `datasets/sec_edgar/generated/`.
- Keep the Semantic IR harness model-agnostic, but use `qwen/qwen3.6-35b-a3b` as the default development model unless a specific comparison question needs another local model.
- Tighten narrative ingestion next around stable object identity, event observation predicates, and temporal/event ordering instead of adding story-specific Python phrase patches.
- Keep a regular regression cadence around segmentation, predicate-palette admission, stored-logic conflicts, and rule/query mixed turns; the frontier is productive enough that small improvements can easily re-open older failure modes.

## Verification Snapshot

Recent verified results:

- Full suite after SEC/contracts third-domain scaffold: `299 passed`
- Full suite after mixed-domain profile/context tightening: `308 passed`
- Full suite after clause-support provenance breadcrumbs: `313 passed`
- Full suite after Semantic IR lava harness and README front-door refresh: `318 passed`
- Focused profile-validator/temporal-gate verification: `125 passed`
- Focused clause-support verification: `53 passed` across semantic IR runtime and trace rendering.
- Focused semantic IR runtime battery: `23 passed`
- Focused profile-contract/domain-roster handoff verification: `7 passed`
- Focused CourtListener/domain-profile verification: `8 passed`
- CourtListener legal smoke: synthetic boundary pass `5/5` valid JSON with safe claim/finding, citation, role, docket, and identity behavior; live metadata smoke `9/9` valid JSON over synthetic plus ignored CourtListener API records
- Focused SEC/domain-profile verification: `9 passed`
- Edge runtime A/B: semantic IR `20/20` decision labels, `0.976` avg score, `0` non-mapper parse rescues
- Weak-edge runtime A/B: semantic IR `10/10` decision labels, `1.000` avg score, `0` non-mapper parse rescues
- Silverton noisy temporal pack: semantic IR `2/8` decision labels, `0.729` avg score; useful evidence that noisy language is less of a blocker than policy labels and temporal admission
- Focused profile/semantic mapper battery after profile-contract work: `39 passed`
- Rule/mutation conflict semantic IR pack: raw 35B prompt bakeoff `9/10` decisions, `0.95` average rough score; runtime A/B semantic IR `10/10` decisions versus legacy `6/10`, `0.917` average rough score, with `0` non-mapper rescues
- Model matrix snapshot: `google/gemma-4-26b-a4b` reached rule/mutation `10/10`, weak edges `10/10`, and hard edge `19/20`; latest `qwen/qwen3.6-35b-a3b` hard-edge rerun reached `17/20`; `nvidia/nemotron-3-nano` reached only `4/10` on rule/mutation and weak edges
- Noisy Silverton reached `8/8` exact labels and `8/8` safe outcomes, with `0.906` extraction average and `1.000` KB safety average. Treat this as a pressure-pack milestone, not proof of broad temporal or legal reasoning.
- Rule/mutation conflict pack still reaches semantic IR `10/10` exact labels after predicate-palette enforcement.
- Harbor frontier latest pass: `14/14` JSON/schema, raw model labels `13/14`, mapper-projected decisions `14/14`, admission contracts `14/14`, admission checks `52/52`, average rough score `0.96`.
- Goldilocks full-story segmented Semantic IR smoke after narrative palette: `56` deduped mutations across `50` segments in about `180s`; major bad-write artifacts from the first UI attempt (`unknown_agent`, voice-as-`carries`, nonsensical `inside(...)` writes, and stray `head` facts) were removed.
- Focused post-story-ingestion verification: `55 passed` across semantic IR runtime, UI gateway phases, and gateway config.
- Live LM Studio medical smoke after profile-context wiring: `Priya is taking Coumadin.` committed `taking(priya, warfarin).`; `His serum creatinine was repeated this afternoon.` still required patient-identity clarification.
- Live LM Studio auto-profile smoke selected `medical@v0`, `legal_courtlistener@v0`, `sec_contracts@v0`, then `medical@v0` across four turns, with each turn receiving the expected domain context and predicate palette.
- Mixed-domain agility smoke, seed `42`, selected expected profiles for `12/12` shuffled turns and produced valid Semantic IR for `12/12`. The stream included Glitch, Goldilocks, Ledger, CourtListener, SEC/contracts, and medical turns. Trace rendered locally under ignored `tmp/semantic_ir_trace_views/`.
- Mixed-domain guardrail/profile tightening on the same seed reduced bad admitted placeholder/loose-trait clauses from `4` to `0`: `null`/generic actor writes are now skipped, `docket_entry(... null ...)` no longer reaches facts, and the story profile steers descriptive traits to `has_trait/2` instead of `owns/2`.
- Hard mixed-domain agility seed `99`: before this pass, selector accuracy was `18/24`; after profile-owned hints and per-turn context, selector accuracy reached `24/24` and valid Semantic IR remained `24/24`.
- Wider mixed-domain agility seed `2718`: selector-only moved from `36/40` to `40/40`; the real LM Studio run reached `40/40` profile selections and `40/40` valid Semantic IR across CourtListener, Harbor, Ledger/probate, Silverton, SEC/contracts, Glitch, Goldilocks, and medical cases.
- The same seed now demonstrates better admitted structure on hard cases: Harbor relative-date correction emits `document_dated/2` plus `relative_date_resolves_to/3` with retractions; document-priority conflict retracts the draft parcel name and asserts the recorded deed name; probate conditional-gift over-expansion dropped from `64` admitted writes to `2`; out-of-district temporal spans now use interval ids plus `outside_district_interval/3`.
- Predicate-contract role gate focused verification: semantic IR runtime battery `48 passed`; profile/mixed/MCP/render focused battery `64 passed`.
- Mixed-domain agility seed `2718` after contract-role enforcement: real LM Studio pass kept `40/40` profile selections and `40/40` valid Semantic IR. The mapper caught a genuine `interval_start/2` role mismatch where the model put a date in the interval slot, while preserving the previously good Harbor interval representation.
- Mixed-domain agility seed `2718` after profile validators and temporal gate: real LM Studio pass again kept `40/40` profile selections and `40/40` valid Semantic IR. The legal profile validator fired once, blocking an allegation-shaped `finding/4` while preserving the corresponding `claim_made/4`; targeted unit tests cover the SEC validator and inverted-interval failure cases.
- Python compile check for touched runtime files passed; full pytest suite then reached `316 passed`
- Focused truth-maintenance schema/trace/alignment verification: `54 passed` across semantic IR runtime and trace rendering; compile check passed for touched Semantic IR scripts. Live LM Studio `qwen/qwen3.6-35b-a3b` truth-maintenance smoke covered correction-plus-claim, rule-consequence-as-query, and observed-document-vs-witness-claim turns. The model emitted support links, conflicts, retraction plans, and `query_only`/`do_not_commit` consequences while the mapper admitted only candidate-operation effects. The first live alignment mini-battery reported `0` fuzzy edges across those three cases.
- Live LM Studio KB-context smoke: with `lives_in(mara, london).` in the KB, `Actually, Mara lives in Paris now.` produced a safe retract/assert pair and cited the old KB clause in `truth_maintenance`; the normal `process_utterance()` path retracted London and asserted Paris. `Mara lives in Paris now.` without an explicit correction marker produced a clarification question and no facts.
- Prompt-molded KB-context smoke: with a single current-state subject candidate from `lives_in(mara, london).`, `Actually, she lives in Paris now.` resolved `she` to Mara, produced retract/assert operations, and yielded `0` truth-maintenance fuzzy edges. The same battery showed KB-backed queries stay as queries and claim-vs-observation turns preserve conflict pressure instead of overwriting observed facts.

## Reading Order

1. `README.md`
2. `AGENT-README.md`
3. `docs/PRETHINK_GATEWAY_MVP.md`
4. `docs/PUBLIC_DOCS_GUIDE.md`
5. `docs/CURRENT_UTTERANCE_PIPELINE.md`
6. `docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md`
7. `docs/SEMANTIC_IR_MAPPER_SPEC.md`
8. `docs/SEMANTIC_IR_MODEL_MATRIX.md`
9. `docs/PROJECT_HORIZON.md`
10. `docs/DOMAIN_PROFILE_CATALOG.md`
11. `docs/COURTLISTENER_DOMAIN.md`
12. `docs/SEC_CONTRACTS_DOMAIN.md`
13. `docs/GUARDRAIL_DEPENDENCY_AB.md`
14. `docs/UMLS_MVP.md`
15. `docs/MEDICAL_PROFILE.md`
16. `docs/CONSOLE_TRYBOOK.md`
17. `ui_gateway/README.md`

## What Was Pruned

Historical markdown reports, dated prompt snapshots, generated ladder/report HTML, stale run manifests, old parser-lane orchestration notes, generated `kb_runs/`, generated `kb_store/`, and large session/source notes were removed from the forward-facing tree. Git history still carries them. The repo should now privilege source, compact current-state docs, small fixtures, and tests over a stack of stale status artifacts.
