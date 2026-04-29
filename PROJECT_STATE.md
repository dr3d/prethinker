# Project State

Last updated: 2026-04-29

## One-Sentence Shape

Prethinker is a governed natural-language-to-Prolog workbench: neural models propose semantic workspaces, deterministic gates decide what can become durable KB state, and the UI shows that process live.

## Current Center

- Runtime: `src/mcp_server.py`, especially `process_utterance()`.
- Current pipeline reference: `docs/CURRENT_UTTERANCE_PIPELINE.md`.
- UI: `ui_gateway/`, served locally by `python ui_gateway/main.py` using the stdlib `ThreadingHTTPServer`.
- Active profile: `medical@v0`; active profile-lane experiments: `legal_courtlistener@v0` and `sec_contracts@v0`.
- Active research asset: local UMLS Semantic Network KB built from `sn_current.tgz`.
- Active architecture pivot: two-pass `semantic_router_v1 -> semantic_ir_v1`, using the LLM as the context/profile planner and the deterministic mapper as the admission authority.
- Current development model: `qwen/qwen3.6-35b-a3b` through LM Studio/OpenAI-compatible structured output. This is the best-known local path, not a permanent product dependency.
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
- Local model-family testing shows model choice still matters even with LM Studio structured output. Nemotron underfit the current contract, Gemma 26B was a serious different-family challenger, and `qwen/qwen3.6-35b-a3b` remains the default development model.
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
- The console now defaults to the current LM Studio Semantic IR lane (`qwen/qwen3.6-35b-a3b`) instead of the former Ollama parser path.
- Long story-like utterances in the UI can use segmented Semantic IR ingestion: the gateway splits the narrative into focused segments, processes each through the canonical `process_utterance()` path, dedupes applied mutations, and exposes segment-level workspace/admission traces.
- Mixed long utterances can now segment at query boundaries, so questions do not pile up in the same semantic workspace as surrounding write facts.
- The generic predicate registry now includes a small story-world event/state palette (`tasted/2`, `sat_in/2`, `lay_in/2`, `broke/1`, `asleep_in/2`, `was_tasted/1`, `was_eaten/1`, `was_sat_in/1`, `was_lain_in/1`, etc.) so narrative ingestion no longer has to squeeze ordinary events into `inside/2`, `at/2`, or `carries/2`.
- Public docs now foreground recent Semantic IR results and remove pre-mid-April media/generated run records from the forward-facing tree; Git history remains the archive for those older artifacts.
- The mapper now blocks placeholder-like durable write arguments such as `unknown_agent`, while the prompt steers unknown-actor observations toward passive object-state predicates when those are available.
- `medical@v0` Semantic IR calls now receive profile-owned predicate contracts and compact UMLS bridge context before the model proposes a workspace. This lets the model normalize examples like `Coumadin` to `warfarin` and see argument-role/semantic-group expectations, while the deterministic mapper still owns admission.
- The profile context now explicitly treats an explicit named patient as sufficient grounding for the research profile, while pronouns, multiple candidates, aliases, and missing patient identity still require clarification.
- A thin domain-profile roster now exists in `modelfiles/domain_profile_catalog.v0.json` and is included in Semantic IR input as `available_domain_profiles`. This is the first skill-directory-style control-plane hook: it advertises possible profile contexts without loading every thick package or authorizing writes.
- `active_profile=auto` now uses model-owned `semantic_router_v1` as the first-pass context/profile/guidance controller before the Semantic IR compiler. It emits a strict control-plane JSON object, loads only the selected profile context/contracts, and never authorizes writes.
- Profile packages still own declarative `selection_keywords`, `selection_hints`, predicate contracts, and domain context, but those are now context assets for the router/compiler rather than a Python keyword selector.
- The former Python catalog selector has been removed from the active runtime and research harnesses. Current traces and metrics center router quality, compiler validity, admission diagnostics, and anti-coupling flags.
- The multilingual router probe is the cleanest current evidence for the wall-sign rule: `router_ok=10/10` and full router -> compiler JSON success `10/10` on raw Spanish, French, German, Portuguese, Italian, Japanese, and code-switched turns.
- `semantic_ir_lava_pack_v2` is now explicitly a calibration pack, not held-out evidence. It reached `36/36` after exposing router/profile ownership gaps, but those gaps influenced the router guidance.
- `semantic_ir_lava_pack_v3` began as the fresh held-out router frontier. Its first honest result was router `14/17` with compiler JSON `17/17` on the full pass. After that, v3 became calibration/repair evidence rather than pristine held-out evidence.
- Generic router/profile repairs took Lava v3 to router `17/17`, compiler JSON `17/17`, and only bootstrap review-only skip diagnostics on the two unexpected-domain turns. The fixes were structural: context-integrity guidance, bootstrap-aware scoring/diagnostics, bootstrap review-only admission, `court_or_judge` institution handling, and scoped probate witness-eligibility predicates.
- The router agility harness now emits `anti_coupling_diagnostics_v1` after the compiler/mapper pass. It flags low-confidence admissions, strict profile misses with admissions, semantic near misses with admissions, profile/predicate mismatches, out-of-palette skips, and cases where admitted predicates fit another profile better. Bootstrap fallback is treated as a valid context-engineering request rather than a profile miss.
- `semantic_router_v1` now emits a `context_audit` block explaining why the profile/context was selected, which context sources should be loaded, which secondary profiles were considered, and why they were not primary. Runtime and router harness traces copy this as `context_audit_v1` with loaded context/contract/predicate counts.
- The router harness now also emits `router_diagnostics_v1`, a structural router/compiler alignment layer that can flag cases such as "router chose medical, but the compiler emitted legal predicate surfaces" without inspecting raw language.
- Mapper admission diagnostics now include human-readable `admission_justifications` derived from deterministic gates and rationale codes. Each operation can explain accepted-because and blocked-because reasons such as allowed palette, predicate contract pass, direct source, source-policy block, or missing durable rule clause.
- A first labeled router training seed lives at `docs/data/router_training/router_training_seed_v1.jsonl` with 164 examples assembled from frontier packs, multilingual probes, and mixed-domain agility cases.
- `semantic_ir_lava_pack_v4` is now the next fresh held-out candidate. It directly targets five architecture hazards called out from the current utterance pipeline: truth-maintenance dependency explosion, predicate canonicalization drift, claim/fact/observation promotion, segmentation semantics, and multilingual ontology pressure.
- A new research note, `docs/DOMAIN_BOOTSTRAPPING_META_MODE.md`, captures the meta-profile idea: when no domain profile exists, a strong model may propose candidate entity types, predicates, contracts, risks, clarification policies, and starter frontier cases. This is review material for creating a profile, not authority for durable writes.
- A first `profile_bootstrap_v1` harness now exists at `scripts/run_profile_bootstrap.py` with a contracts/compliance seed fixture. It asks the local structured-output model to propose a candidate domain profile, then scores schema validity, generic predicate use, and whether starter frontier cases stay inside the proposed predicate palette and arities.
- `scripts/run_profile_bootstrap_loop.py` now closes the meta-profile loop: it loads a local profile bootstrap run, projects its candidate predicates/contracts into a temporary Semantic IR profile, runs the generated starter cases through the normal model+mapper path, and scores valid JSON, palette skips, must-not violations, and expected-boundary hits.
- `scripts/run_domain_bootstrap_file.py` now captures the Codex-style open-domain move as an explicit LLM-owned profile-bootstrap path: Python reads a raw text file, the model proposes the predicate/entity surface, and optional source compilation uses that draft profile without Python deriving predicates or segmenting the language.
- Raw-file bootstrapping now has a first-class `intake_plan_v1` control-plane pass. The model proposes the source boundary, epistemic stance, symbolic/entity/predicate-family strategy, focused pass plan, and risk policy before profile/bootstrap compilation. This is the explicit version of the document-to-logic strategy Codex was doing implicitly.
- The raw-file runner can now compile by LLM-authored intake passes via `--compile-plan-passes`. Python iterates over the model's pass plan and carries context; it does not choose semantic segments from the source text. This gives dense documents source-boundary, principles/rules, repeated-records, declarations, and pledge passes instead of one operation-budget-constrained gulp.
- `profile_bootstrap_v1` now has a first-class `repeated_structures` block. This captures the document-to-logic compiler move where the model sees a repeated list, such as Declaration-style grievances, and proposes a stable record predicate plus property predicates like `grievance/2`, `grievance_actor/2`, `grievance_target/2`, `grievance_method/2`, and `grievance_purpose/2`.
- Raw-file source compilation now has a generic operation-budget policy for long documents: preserve source/provenance boundary, core speech acts, representative repeated records, and concluding commitments, while marking `segment_required_for_complete_ingestion` instead of letting one repeated list consume the entire Semantic IR operation cap.
- Raw-file profile bootstrapping now has a compact LLM retry when the structured profile JSON is invalid or truncated. The retry asks the model to emit a smaller unique predicate surface; Python does not repair or reinterpret the language.
- Declaration/Proclamation calibration exposed the next hard edge: predicate canonicalization drift. The model can understand a document and still offer competing equivalent predicate surfaces. Current guidance pushes the LLM to choose one canonical family; the intended repair remains profile/schema/context pressure, not Python synonym rewriting.
- The Semantic IR candidate-operation cap is now `128` per turn, raised from `64` after Declaration/Proclamation calibration showed the previous cap was crowding out dense document sections.
- A post-ingestion document QA runner now lives at `scripts/run_domain_bootstrap_qa.py`. It loads admitted facts/rules from a raw-file compile run, gives the QA model the actual compiled KB predicate inventory and representative clauses, maps question turns through Semantic IR, and executes admitted query clauses against the local Prolog runtime. The QA file can carry human reference answers without feeding them back into profile bootstrap or source compilation.
- The mapper now admits positive direct `operation='rule'` records with predicate+args but no executable clause as fact-like rule records, with rationale `rule_label_demoted_to_fact_record`. This is a structural repair for model administrative labels; true executable rules still require a clause, and negative/general rule operations still do not become facts.
- The mapper now blocks variable-like no-clause rule stubs from being demoted into facts. This closes a concrete policy-demo failure where `operation='rule'` plus `args=['R', ...]` could otherwise become a bogus durable atom such as `violation(r, reimbursement_policy).`
- A focused cross-turn policy/reimbursement demo runner now lives at `scripts/run_policy_reimbursement_demo.py`. It records reimbursement rules, ingests February events, asks which reimbursements violated policy, applies an explicit approval correction, and verifies that derived `violation/2` answers are not written as durable facts.
- A mixed-domain agility harness now lives at `scripts/run_mixed_domain_agility.py`. It randomizes Goldilocks, Glitch, Ledger, Silverton, Harbor, CourtListener, SEC/contracts, and medical scenarios through `active_profile=auto` so router-owned profile switching can be tested as a stream rather than isolated lanes.
- Router prompt/context policy now makes recent context visible for anaphoric/follow-up utterances such as "it came back high", while keeping the final profile choice in `semantic_router_v1` rather than Python keyword logic.
- Declarative starter profile packages now exist for exploration: `modelfiles/profile.story_world.v0.json`, `modelfiles/profile.probate.v0.json`, and `modelfiles/profile.legal_courtlistener.v0.json`. They provide mock thick context and predicate contracts for future routing experiments without changing runtime admission authority.
- The probate profile now owns a few noisy selection aliases for the Silverton/London frontier, such as `Btrice`, `Londn`, `Londres`, `ONT`, and weekend/country shorthand. These are context-loading hints, not mapper admission rules.
- The legal/probate/SEC starter profiles now carry a broader profile-owned predicate surface for the current frontier packs: legal source documents, access logs, relative-date anchors, interval facts, probate guardianship/conditional-gift facts, and contract-like clearance/lock/stock state.
- The mapper now collapses duplicate admitted candidate operations. This catches schema-cap repetition floods without teaching Python any story-specific language.
- The rule/query frontier now has its own `rule_query_semantics` bakeoff group. It stresses mixed turns where English policy, direct facts, explicit questions, necessary conditions, recusal rules, and derived compliance answers must stay separated.
- Prompt policy now tells the model to preserve compound query targets such as "active access with expired sponsorship" as multiple query operations when the palette supports them, and to bind queries to named subjects rather than generic class nouns.
- Medical safety projection now rejects clinical dose/treatment advice queries even if the same utterance contains otherwise safe medical-memory facts. This keeps bounded medical memory separate from clinical recommendation.
- Predicate contract role validation now treats `authority_or_source` as intentionally broad, so authorities such as auditors can be admitted without being mistaken for source-document role violations.
- A first-pass CourtListener adapter shell now lives under `adapters/courtlistener/`. It includes a conservative token-based REST client, normalizer, legal predicate contracts, harness conversion, README, and an offline synthetic legal seed fixture for claim/finding, citation, role-scope, docket, and identity-boundary tests.
- First CourtListener live smoke generated ignored `breach of lease` and `summary judgment` harness slices and ran legal Semantic IR cases through LM Studio. All emitted valid JSON; the legal palette preserved claim/finding, citation-not-endorsement, docket-not-holding, role-scope, and ambiguous judge identity boundaries.
- `sec_contracts@v0` is now the third large starter domain. It targets SEC/EDGAR and contract-obligation intake: filing/exhibit provenance, party roles, obligations, rights, conditions, effective/termination triggers, and breach-event boundaries.
- A first-pass SEC EDGAR adapter shell now lives under `adapters/sec_edgar/`. It requires `SEC_USER_AGENT` for live calls, caches raw responses locally, emits harness cases, and includes an offline synthetic fixture for obligation-not-fact and condition-not-event tests.
- First SEC live smoke generated ignored Apple/Microsoft filing harness data and ran 11 Semantic IR cases through LM Studio. All emitted valid JSON; adding `filer_of/2` fixed an initial palette gap where filing metadata was being squeezed into `party_to_contract/3`.
- A new held-out cross-turn frontier proposal lives at `docs/data/frontier_packs/semantic_ir_cross_turn_frontier_pack_v1.json`. It targets identity drift, claim/observation separation, noisy multilingual corrections, mixed rule/query/fact turns, temporal corrections, and domain type ambiguity.
- A new `policy_demo` Semantic IR bakeoff group now targets the "talk your rules into existence" demo family: reimbursement-policy violations, meeting commitments, access sponsorship expiry, customer-support override ladders, story-world throne claims, and business dependency credibility.
- Prompt/context policy now explicitly separates pure answers from mixed write+query turns, prioritizes direct grounded facts before complex rule clauses under the operation cap, requires explicit query operations for explicit questions, and blocks necessary-condition-to-sufficient-rule inversions such as turning "no launch without QA" into `launch_allowed(...)`.
- Epistemic Worlds v1 now surfaces projection-blocked and supported-but-skipped writes as scoped diagnostic memory instead of global truth. The mapper can preserve the candidate as fixed wrapper clauses such as `world_operation/4`, `world_arg/4`, and `world_policy/3`; these are diagnostic scoped-memory clauses and do not enter the durable domain predicates.

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

Top priority:

- Represent temporal facts durably enough that extracted dates, intervals, corrections, and relative-time anchors can support real KB queries instead of staying only in the semantic workspace. This is the highest-leverage architecture move because it unlocks the policy-demo path: record rules/events, ask which cases violate or remain blocked, and show why without writing derived conclusions as facts.

Supporting architecture:

- Grow deterministic stored-logic admission beyond the first guard: profile-declared functional predicates, temporal scope, negation policy, and richer contradiction probes are still open.
- Grow clause support records and the `truth_maintenance` proposal block into a real dependency layer: derived conclusions should eventually point to supporting facts, rules, source documents, and retractions without granting model-proposed consequences write authority.
- Decide when Epistemic Worlds should graduate from diagnostic payloads into optional durable scoped memory. The first slice preserves rejected/quarantined candidates without polluting global truth; the next step is explicit world-query UX and policy for which worlds are persisted.
- Push the remaining mapper frontier: durable rule admission for quantified exception language, better decision-label calibration for safe partial commits, and cleaner nested event predicate shapes.
- Keep profile contracts out of the generic mapper: profile packages should own domain type/grounding policy, while the mapper stays structural and auditable.
- Promote scenario-local predicate contracts into reusable profile/predicate manifests so fewer expectations live only inside individual frontier packs.

Router/context work:

- Treat richer domain context as a catalog/skill mechanism, not hardwired prompt drift. The current auto path is router-owned and measured; next steps are multi-profile turns, router confidence UX, and deciding when mixed-domain utterances should be segmented before Semantic IR.
- Treat `docs/data/router_training/router_training_seed_v1.jsonl` as a router contract surface, not a fine-tuning set. It is large enough to harden schema/prompt expectations, but still thin around bootstrap and legal/probate boundary tension.
- Expand router/profile-selection tests from clean synthetic switching into messy mixed-domain turns. Profile selection is advisory context loading, not admission authority.
- Prototype `profile_bootstrap_v1`: feed 5-20 texts from an unfamiliar domain and ask the model to propose entity types, predicates, argument contracts, admission risks, clarification policies, and starter frontier cases. The first success criterion is reviewable profile-design material, not automatic profile authority.

Demo-critical evidence and UX:

- Push the policy-demo frontier into the UI/prompt book once the command-line harness stays stable: the highest-impact demo is still "record reimbursement policy, ingest February events, ask which reimbursements violated policy, and show why without writing derived violation facts."
- Expand trace views around admission contracts so reviewers can see not only the model decision, but also which exact boundary checks passed.

Polish:

- Make the prompt-book examples meatier: each demo should show an utterance, the expected clarification or commit behavior, and the reason it is safer than a plain chatbot answer.
- Wire more Semantic Network explanations into the UI, especially type ancestry and relation paths.

Regression hygiene:

- Keep measuring router/compiler/admission quality directly on Glitch, Ledger, medical ambiguity, temporal packs, and mixed-domain Lava packs. The old Python-selector comparison has served its purpose and is no longer a useful frontier metric.
- Use the truth-maintenance/admission delta as a regular frontier metric: the next good improvements should reduce fuzzy edges by improving model workspace quality, profile contracts, or predicate surfaces, not by adding English phrase patches.
- Keep a regular regression cadence around segmentation, predicate-palette admission, stored-logic conflicts, and rule/query mixed turns; the frontier is productive enough that small improvements can easily re-open older failure modes.
- Keep improving reset/session hygiene so first utterances after reset cannot inherit stale entity context.

Domain/data lanes:

- Expand the medical profile only when the new predicate earns its place through tests and a clear demo.
- Keep expanding the CourtListener lane with small live API slices and curated synthetic boundaries. Generated live data remains ignored under `datasets/courtlistener/generated/` unless a tiny fixture is intentionally curated.
- Run the SEC adapter against a small EDGAR submissions slice only after setting `SEC_USER_AGENT` and choosing a durable cache/review policy. Keep generated live data under ignored `datasets/sec_edgar/generated/`.
- Tighten narrative ingestion next around stable object identity, event observation predicates, and temporal/event ordering instead of adding story-specific Python phrase patches.
- Keep the Semantic IR harness model-agnostic, but use `qwen/qwen3.6-35b-a3b` as the default development model unless a specific comparison question needs another local model.

## Verification Snapshot

**Current headline:** latest full pytest suite `388 passed`; latest Lava v5 sampled run stayed `60/60` parsed JSON, `60/60` domain selector, `60/60` admission-safe, `45/60` semantic-clean, `41/60` full expectation score, `0` fuzzy edge kinds, and `0/60` temp-0 signature variance groups. Current best demo pressure point remains the reimbursement policy cross-turn run: `4/4` parsed, `4/4` apply-error-free, `4/4` expected query matches, and no derived violation write leak.

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
- Harbor frontier latest focused pass: `14/14` JSON/schema, raw model labels `12/14`, mapper-projected decisions `12/14`, admission contracts `13/14`, admission checks `51/52`, average rough score `0.95`. The remaining admission miss is a useful temporal-correction frontier: the model asserts the new relative-date anchor and retracts the derived relative date, but may omit the old `dated_on/2` anchor retraction.
- Goldilocks full-story segmented Semantic IR smoke after narrative palette: `56` deduped mutations across `50` segments in about `180s`; major bad-write artifacts from the first UI attempt (`unknown_agent`, voice-as-`carries`, nonsensical `inside(...)` writes, and stray `head` facts) were removed.
- Focused post-story-ingestion verification: `55 passed` across semantic IR runtime, UI gateway phases, and gateway config.
- Live LM Studio medical smoke after profile-context wiring: `Priya is taking Coumadin.` committed `taking(priya, warfarin).`; `His serum creatinine was repeated this afternoon.` still required patient-identity clarification.
- Live LM Studio auto-profile smoke selected `medical@v0`, `legal_courtlistener@v0`, `sec_contracts@v0`, then `medical@v0` across four turns, with each turn receiving the expected domain context and predicate palette.
- Mixed-domain agility smoke, seed `42`, selected expected profiles for `12/12` shuffled turns and produced valid Semantic IR for `12/12`. The stream included Glitch, Goldilocks, Ledger, CourtListener, SEC/contracts, and medical turns. Trace rendered locally under ignored `tmp/semantic_ir_trace_views/`.
- Mixed-domain guardrail/profile tightening on the same seed reduced bad admitted placeholder/loose-trait clauses from `4` to `0`: `null`/generic actor writes are now skipped, `docket_entry(... null ...)` no longer reaches facts, and the story profile steers descriptive traits to `has_trait/2` instead of `owns/2`.
- Historical mixed-domain selector runs are superseded by router-first evaluation; Git history retains the pre-router records.
- Wider mixed-domain LM Studio runs reached `40/40` profile selections and `40/40` valid Semantic IR across CourtListener, Harbor, Ledger/probate, Silverton, SEC/contracts, Glitch, Goldilocks, and medical cases.
- The same seed now demonstrates better admitted structure on hard cases: Harbor relative-date correction emits `document_dated/2` plus `relative_date_resolves_to/3` with retractions; document-priority conflict retracts the draft parcel name and asserts the recorded deed name; probate conditional-gift over-expansion dropped from `64` admitted writes to `2`; out-of-district temporal spans now use interval ids plus `outside_district_interval/3`.
- Predicate-contract role gate focused verification: semantic IR runtime battery `48 passed`; profile/mixed/MCP/render focused battery `64 passed`.
- Mixed-domain agility seed `2718` after contract-role enforcement: real LM Studio pass kept `40/40` profile selections and `40/40` valid Semantic IR. The mapper caught a genuine `interval_start/2` role mismatch where the model put a date in the interval slot, while preserving the previously good Harbor interval representation.
- Mixed-domain agility seed `2718` after profile validators and temporal gate: real LM Studio pass again kept `40/40` profile selections and `40/40` valid Semantic IR. The legal profile validator fired once, blocking an allegation-shaped `finding/4` while preserving the corresponding `claim_made/4`; targeted unit tests cover the SEC validator and inverted-interval failure cases.
- Python compile check for touched runtime files passed; full pytest suite then reached `316 passed`
- Focused truth-maintenance schema/trace/alignment verification: `54 passed` across semantic IR runtime and trace rendering; compile check passed for touched Semantic IR scripts. Live LM Studio `qwen/qwen3.6-35b-a3b` truth-maintenance smoke covered correction-plus-claim, rule-consequence-as-query, and observed-document-vs-witness-claim turns. The model emitted support links, conflicts, retraction plans, and `query_only`/`do_not_commit` consequences while the mapper admitted only candidate-operation effects. The first live alignment mini-battery reported `0` fuzzy edges across those three cases.
- Live LM Studio KB-context smoke: with `lives_in(mara, london).` in the KB, `Actually, Mara lives in Paris now.` produced a safe retract/assert pair and cited the old KB clause in `truth_maintenance`; the normal `process_utterance()` path retracted London and asserted Paris. `Mara lives in Paris now.` without an explicit correction marker produced a clarification question and no facts.
- Prompt-molded KB-context smoke: with a single current-state subject candidate from `lives_in(mara, london).`, `Actually, she lives in Paris now.` resolved `she` to Mara, produced retract/assert operations, and yielded `0` truth-maintenance fuzzy edges. The same battery showed KB-backed queries stay as queries and claim-vs-observation turns preserve conflict pressure instead of overwriting observed facts.
- Rule/query semantics focused bakeoff, current best local model and `best_guarded_v2`: `9/9` JSON/schema, `9/9` raw model decisions, `9/9` mapper-projected decisions, admission contracts `9/9`, admission checks `75/75`, average rough score `0.96`. This is the current best "talk your rules into existence" pressure pack.
- Focused policy/reimbursement cross-turn demo with `qwen/qwen3.6-35b-a3b` through LM Studio: `4/4` parsed OK, `4/4` apply error free, `4/4` expected query matches, `4/4` no derived violation write leak, rough score `1.000`. The successful path installed four executable rules from English policy, derived `r1`/`r2` after event ingestion, then retracted `approved_by(r2, lena).` and changed the derived answer to only `r1`.
- Domain bootstrap calibration, raw Declaration document: one flat Semantic IR source compile with target-signature guidance reached emitted signature recall `0.159`; LLM-authored intake-plan pass compilation raised that to `0.623` with `234` admitted operations. This is the best current evidence that the Codex-like planning move belongs inside Prethinker as an LLM control-plane pass.
- Domain bootstrap calibration, raw Proclamation document: after canonical predicate-family guidance and compact profile retry, plan-pass compilation reached profile signature recall `0.795`, emitted signature recall `0.402`, and `302` admitted operations. The remaining gap is mostly predicate-surface/style drift, not basic document comprehension.
- Profile bootstrap harness smoke on `datasets/profile_bootstrap/samples/contracts_compliance_seed_8.jsonl` with `qwen/qwen3.6-35b-a3b`: parsed OK, rough score `1.000`, `10` candidate predicates, `0` generic predicates, `0` unknown positive predicate refs in starter cases, and `8` starter frontier cases. Treat this as profile-design review material, not an approved contracts profile.
- Profile bootstrap closed-loop smoke on the latest contracts/compliance draft: `8/8` valid Semantic IR, `8/8` zero out-of-palette skip cases, `8/8` zero must-not violation cases, `7/8` expected-boundary hit cases, `16` admitted clauses, loop rough score `0.969`. The remaining miss is profile-surface ambiguity: prohibition-with-exception versus conditional-right representation.
- Raw-file bootstrap smoke on `tmp/declaration.md` with `qwen/qwen3.6-35b-a3b`: parsed `profile_bootstrap_v1`, rough score up to `1.000`, `0` generic predicates, and a Declaration-style repeated grievance structure with no palette drift. Optional whole-source compile now succeeds and emits a balanced skeleton with source/document facts, source-attributed claims or principles, representative grievance records, declaration/pledge facts depending on the run, and `segment_required_for_complete_ingestion` when the full grievance list exceeds the Semantic IR operation cap. With the supplied `tmp/declaration.pl` signature roster used as calibration guidance, profile signature recall reached `67/69` (`0.971`) and one-shot compile signature recall reached `30/69` (`0.435`).
- Raw-file bootstrap smoke on `tmp/proclamation.md` with supplied `tmp/proclamation.pl` expected Prolog: without target-signature guidance the model produced a sane abstract recall-proclamation profile but low expected-surface overlap. With calibration guidance from the expected signature roster, profile signature recall reached `91/122` (`0.746`) and one-shot compile signature recall reached `23/122` (`0.189`). This is strong evidence that profile/ontology discovery can align to a human target surface, while long-document compilation now needs LLM-owned multi-pass intake planning rather than a larger pile of Python segmentation rules.
- After adding the document-to-logic compiler recipe to bootstrap guidance, the same declaration raw-file smoke still parsed cleanly and proposed a more epistemically explicit profile: rough score `1.000`, `8` candidate predicates, `0` generic predicates, and a direct admission risk against treating grievances as objective facts. The model still preferred compact `grievance/2` over stable grievance ids plus actor/target/method predicates, exposing the next profile-bootstrap frontier: repeated-structure decomposition should become an explicit output field rather than hidden in free-form guidance.
- Mixed-domain agility seed `314159` initially exposed two profile/context-selection misses: noisy `Btrice/Londn ONT` probate text and an anaphoric medical follow-up, `It came back high after the repeat this afternoon.` Those records are now historical context for the router-first path.
- Full pytest after rule/query and clinical-boundary work: `347 passed`.
- Broad 111-scenario Semantic IR bakeoff after the same work: `111/111` JSON/schema, raw model decisions `79/111`, mapper-projected decisions `86/111`, admission contracts `26/27`, admission checks `168/169`, average rough score `0.90`. Remaining low-score cases are mostly policy-label calibration and temporal/retraction frontier pressure, not JSON or mapper-admission collapse.
- Focused router/frontier/domain verification after `semantic_router_v1`, multilingual probe, Lava v2/v3 packs, and anti-coupling diagnostics: `88 passed`.
- Full pytest after router/frontier/trace work: `364 passed`.
- Full pytest after router-first streamlining and Python selector retirement: `361 passed`.
- Full pytest after router diagnostics, context audit, admission justification, and router training seed: `367 passed`.
- Full pytest after Epistemic Worlds v1 diagnostic scoped-memory slice: `372 passed`.
- Full pytest after Lava v5 truth-maintenance hardening and scoped support-link tests: `374 passed`.
- Lava v5 truth-maintenance hardening rerun over `60` attempts stayed `60/60` parsed JSON, `60/60` domain selector, `60/60` admission-safe, and `0/60` temp-0 variance groups. Epistemic Worlds captured `52` scoped operation(s) across `27/60` records, while fuzzy edge kinds dropped to `{}` after scoped retraction-plan preservation, structured reject/clarify policy alignment, skipped-query scoped memory, and soft handling for out-of-range question support links.
- Full pytest after source-record identity-ambiguity alignment and Lava expectation-surface scoring: `377 passed`.
- Multilingual router probe: `router_ok=10/10`, `compiler_parsed_ok=10/10`.
- Lava v2 calibration router probe: `router_ok=36/36`; calibration evidence only, because v2 influenced router guidance.
- Lava v3 first held-out router probe with bootstrap-aware scoring: `router_ok=14/17`, `router_score_avg=0.868`.
- Lava v3 repair/calibration pass after generic router/profile fixes: `router_ok=17/17`, `router_score_avg=0.991`, `compiler_parsed_ok=17/17`, with anti-coupling reduced to intentional bootstrap review-only skips on the two unexpected-domain cases: `bootstrap_review_only_skips=2`.
- Lava v4 first pass: router-only smoke reached `25/25` profile choices. Full router -> Semantic IR pass reached `25/25` router choices and `25/25` compiler JSON, with anti-coupling limited to `mapper_skips_tied_to_profile_context=3`. The isolated lava-sweep scorer reached expectation `11/25`, which is useful pressure rather than a failure of format: most misses are semantic/admission-frontier cases around dependency invalidation, epistemic promotion, and multilingual ontology normalization.
- Router context-audit schema smoke after adding `context_audit`: `3/3` Lava v4 router-only records parsed through LM Studio structured output, and the trace includes why-this-profile / why-not-secondary audit text.
- Adaptive-depth speed path: pinned `active_profile` turns skip `semantic_router_v1`, auto-router selections are cached for exact replay/retry signatures, and the Semantic IR compiler now receives a focused selected/candidate profile roster instead of the full profile catalog.
- Lava v5 fresh frontier pack now exists at `docs/data/frontier_packs/semantic_ir_lava_pack_v5.json`. First 35B LM Studio smoke: router-only sampled pass `12/12`; full router -> compiler pass `15/15` router choices and `15/15` compiler JSON. The lava scorer over originals plus typo/bad-grammar/context-switch variants reached `120/120` parsed JSON and `120/120` domain selector checks, with `0/60` temperature-0 signature variance groups. Expectation score was intentionally harsh at `34/120`; the exposed weak spots are necessary-vs-sufficient rule semantics, temporal anchor correction/retraction plans, Spanish probate correction, bootstrap typo admission, and source-fidelity expectation phrasing.
- Full pytest after document-intake planning and post-ingestion QA runner work: `388 passed`.
- Proclamation post-ingestion QA smoke over the first `10` answer-key probes: `10/10` questions carried human reference answers, `10/10` parsed Semantic IR, `9/10` emitted admitted query rows, `0` proposed writes, and `0` runtime load errors. The smoke exposed the next QA-specific weak spot: the model needs stronger compiled-KB-surface guidance for variable syntax and multi-hop query planning, not more Python NLP.
- Lava expectation scoring now separates semantic/diagnostic mentions, query-surface mentions, and admitted durable unsafe clauses. A forbidden concept appearing in self-check, unsafe-implication text, or a read-only query is no longer treated the same as a forbidden KB mutation; summaries report semantic-clean and admission-safe counts separately. A conservative rescore of the existing Lava v5 JSONL showed durable admission safety `120/120`, which reframes many remaining misses as semantic coverage or expectation-phrasing pressure rather than unsafe writes.
- Fresh Lava v5 sampled rerun after the scoring change: `60/60` parsed JSON, `60/60` domain selector checks, `60/60` admission-safe, `46/60` semantic-clean, `21/60` full expectation score, and `0/60` temp-0 signature variance groups. The strongest current signal is safety under messy variants; the next weak spots are rule sufficiency, temporal retraction/admission, bootstrap review-only behavior, and source-fidelity expectations that punish diagnostic mentions of forbidden prior-story names.
- Lava v5 follow-up after profile/palette overlay and query-arity prompt guidance: the rule/query case now admits `depends_on(launch, qa_signoff).`, `depends_on(launch, legal_approval).`, `announced_on(marketing, launch_date).`, and the read-only query `blocked_by(launch, blocker).` without mapper warnings. A final 60-attempt sampled rerun stayed `60/60` parsed JSON, `60/60` domain selector, `60/60` admission-safe, and `0/60` temp-0 signature variance groups. Remaining misses are mainly missing semantic anchors, temporal label calibration, and exception-rule representation, not unsafe durable writes.
- Lava v5 source-record alignment rerun over `60` attempts stayed `60/60` parsed JSON, `60/60` domain selector, `60/60` admission-safe, `45/60` semantic-clean, `41/60` full expectation score, `0/60` temp-0 signature variance groups, and `{}` fuzzy edge kinds. The repaired fuzzy edge was an identity-ambiguity case where a neutral source record should be admitted while the person-linking inference remains quarantined.
- `docs/FRONTIER_DATASET_SURVEY.md` captures next useful public/research data sources and pack concepts: CUAD/ContractNLI/MAUD/LegalBench-RAG for obligations and legal source spans, MeetingBank/QMSum/municipal minutes for commitments and votes, PubMedQA/MedNLI/RadNLI/MedSafetyBench for bounded medical evidence/safety, ParlaMint for multilingual policy, and TKGQA/FActScore/QAGS-style patterns for truth maintenance and source fidelity.

## Reading Order

1. `README.md`
2. `AGENT-README.md`
3. `docs/PRETHINK_GATEWAY_MVP.md`
4. `docs/PUBLIC_DOCS_GUIDE.md`
5. `docs/CURRENT_UTTERANCE_PIPELINE.md`
6. `docs/CONTEXT_CONTROL_ARCHITECTURE_BRIEF.md`
7. `docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md`
8. `docs/SEMANTIC_IR_MAPPER_SPEC.md`
9. `docs/PROJECT_HORIZON.md`
10. `docs/SEMANTIC_ROUTER_EXPERIMENT.md`
11. `docs/MULTILINGUAL_SEMANTIC_IR_PROBE.md`
12. `docs/NO_LANGUAGE_HANDLING_IN_PYTHON_AUDIT.md`
13. `docs/DOMAIN_PROFILE_CATALOG.md`
14. `docs/COURTLISTENER_DOMAIN.md`
15. `docs/SEC_CONTRACTS_DOMAIN.md`
16. `docs/UMLS_MVP.md`
17. `docs/MEDICAL_PROFILE.md`
18. `docs/CONSOLE_TRYBOOK.md`
19. `ui_gateway/README.md`

## What Was Pruned

Historical markdown reports, dated prompt snapshots, generated ladder/report HTML, stale run manifests, old parser-lane orchestration notes, generated `kb_runs/`, generated `kb_store/`, and large session/source notes were removed from the forward-facing tree. Git history still carries them. The repo should now privilege source, compact current-state docs, small fixtures, and tests over a stack of stale status artifacts.
