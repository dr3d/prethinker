# Project State

Last updated: 2026-04-27

## One-Sentence Shape

Prethinker is a governed natural-language-to-Prolog workbench: neural models propose semantic workspaces, deterministic gates decide what can become durable KB state, and the UI shows that process live.

## Current Center

- Runtime: `src/mcp_server.py`, especially `process_utterance()`.
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
- The console now defaults to the current LM Studio Semantic IR lane (`qwen/qwen3.6-35b-a3b`) instead of the older 9B/Ollama parser path, while still keeping Freethinker off by default.
- Long story-like utterances in the UI can use segmented Semantic IR ingestion: the gateway splits the narrative into focused segments, processes each through the canonical `process_utterance()` path, dedupes applied mutations, and exposes segment-level workspace/admission traces.
- Mixed long utterances can now segment at query boundaries, so questions do not pile up in the same semantic workspace as surrounding write facts.
- The generic predicate registry now includes a small story-world event/state palette (`tasted/2`, `sat_in/2`, `lay_in/2`, `broke/1`, `asleep_in/2`, `was_tasted/1`, `was_eaten/1`, `was_sat_in/1`, `was_lain_in/1`, etc.) so narrative ingestion no longer has to squeeze ordinary events into `inside/2`, `at/2`, or `carries/2`.
- The mapper now blocks placeholder-like durable write arguments such as `unknown_agent`, while the prompt steers unknown-actor observations toward passive object-state predicates when those are available.
- `medical@v0` Semantic IR calls now receive profile-owned predicate contracts and compact UMLS bridge context before the model proposes a workspace. This lets the model normalize examples like `Coumadin` to `warfarin` and see argument-role/semantic-group expectations, while the deterministic mapper still owns admission.
- The profile context now explicitly treats an explicit named patient as sufficient grounding for the research profile, while pronouns, multiple candidates, aliases, and missing patient identity still require clarification.
- A thin domain-profile roster now exists in `modelfiles/domain_profile_catalog.v0.json` and is included in Semantic IR input as `available_domain_profiles`. This is the first skill-directory-style control-plane hook: it advertises possible profile contexts without loading every thick package or authorizing writes.
- Declarative starter profile packages now exist for exploration: `modelfiles/profile.story_world.v0.json`, `modelfiles/profile.probate.v0.json`, and `modelfiles/profile.legal_courtlistener.v0.json`. They provide mock thick context and predicate contracts for future routing experiments without changing runtime admission authority.
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
- Treat richer domain context as a catalog/skill mechanism, not hardwired prompt drift. The next profile-aware step is a measured domain-profile selector that can choose `medical@v0` or another cataloged profile without granting write authority.
- Grow deterministic stored-logic admission beyond the first guard: profile-declared functional predicates, temporal scope, negation policy, and richer contradiction probes are still open.
- Extend predicate-palette enforcement with profile-owned type contracts and better UI surfacing for skipped operations.
- Promote scenario-local predicate contracts into reusable profile/predicate manifests, then enforce those contracts deterministically where possible.
- Expand trace views around admission contracts so reviewers can see not only the model decision, but also which exact boundary checks passed.
- Build a new held-out frontier pack instead of over-polishing Silverton: cross-document temporal causality, aliases, corrections, disputed claims, and profile type pressure.
- Port the new cross-turn frontier pack into a runner only after deciding which expectations should be hard regression gates versus research pressure gauges.
- Explore domain-profile selection with the starter profiles: first offline roster-selection traces, then optional gateway traces, before any automatic context loading affects normal runs.
- Keep expanding the CourtListener lane with small live API slices and curated synthetic boundaries. Generated live data remains ignored under `datasets/courtlistener/generated/` unless a tiny fixture is intentionally curated.
- Run the SEC adapter against a small EDGAR submissions slice only after setting `SEC_USER_AGENT` and choosing a durable cache/review policy. Keep generated live data under ignored `datasets/sec_edgar/generated/`.
- Keep the Semantic IR harness model-agnostic, but use `qwen/qwen3.6-35b-a3b` as the default development model unless a specific comparison question needs another local model.
- Tighten narrative ingestion next around stable object identity, event observation predicates, and temporal/event ordering instead of adding story-specific Python phrase patches.
- Keep a regular regression cadence around segmentation, predicate-palette admission, stored-logic conflicts, and rule/query mixed turns; the frontier is productive enough that small improvements can easily re-open older failure modes.

## Verification Snapshot

Recent verified results:

- Full suite after SEC/contracts third-domain scaffold: `299 passed`
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
- Python compile check for touched runtime files passed

Rerun the full suite before committing a new stopping point.

## Reading Order

1. `README.md`
2. `AGENT-README.md`
3. `docs/PRETHINK_GATEWAY_MVP.md`
4. `docs/PUBLIC_DOCS_GUIDE.md`
5. `docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md`
6. `docs/SEMANTIC_IR_MAPPER_SPEC.md`
7. `docs/SEMANTIC_IR_MODEL_MATRIX.md`
8. `docs/DOMAIN_PROFILE_CATALOG.md`
9. `docs/COURTLISTENER_DOMAIN.md`
10. `docs/SEC_CONTRACTS_DOMAIN.md`
11. `docs/GUARDRAIL_DEPENDENCY_AB.md`
12. `docs/UMLS_MVP.md`
13. `docs/MEDICAL_PROFILE.md`
14. `docs/FREETHINKER_DESIGN.md`
15. `docs/CONSOLE_TRYBOOK.md`
16. `ui_gateway/README.md`

## What Was Pruned

Historical markdown reports, dated prompt snapshots, run summaries, and large session/source notes were removed from the forward-facing tree. Git history still carries them. The repo should now privilege compact current-state docs over a stack of stale status artifacts.
