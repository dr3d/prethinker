# CLAUDE-WORK

Date: 2026-04-17
Author: Claude (Opus 4.6), acting via Cowork on Scott's workspace mount of `D:\_PROJECTS\prethinker`
Companion document: `CODE-HANDOFF.md` (Codex / GPT-5, same date)
Scope: one working session. Goal was to absorb the Codex handoff, verify the repo is where the handoff says it is, and start executing Priority 1.

This document is written to the same bar as `CODE-HANDOFF.md`. It separates evidence from opinion, records what was actually done vs. what remains, and names the specific things a next agent should touch first.

## 1) Session Snapshot

Incoming state was exactly as described in `CODE-HANDOFF.md` (2026-04-17). No surprises at the file-layout level.

Delivered in this session:
- Safety gate re-verified: **78 passed** (pre-change and post-change). Matches Codex claim.
- `modelfiles/predicate_registry.json` populated from empty → **56 canonical predicates**.
  - Evidence-based: 55 mined from `kb_store/*/kb.pl`, 1 added manually (`at_step/2`) for temporal mode.
- Empty original preserved at `modelfiles/predicate_registry.json.empty-backup-2026-04-17`.
- Provenance note: `docs/reports/GENERAL_REGISTRY_POPULATION_2026-04-17.md`.
- Mining artifacts: `tmp/predicate_inventory.{json,md}`, `tmp/predicate_registry.candidate.{json,md}`,
  `tmp/mine_predicates.py`, `tmp/build_registry_candidate.py`.

Not delivered (blocked by sandbox network):
- Blocksworld baseline re-verification with live Ollama. Sandbox cannot reach the host's `127.0.0.1:11434`.
- Narrative strict re-run against the newly-populated registry. Same reason.

See §7 for the reason and §9 for the commands to finish.

## 2) Non-Negotiable Operating Rules (inherited, respected)

Reaffirming these verbatim because this session's work touches every one of them:

1. **Raw-input rule.** I mined predicates from already-run KBs — no upstream rewriting of source text. The registry candidate is derived from what the parser _actually produced_, not what I thought the parser _should_ produce.
2. **Honest attribution rule.** The registry has 55 evidence-mined entries plus exactly 1 deliberately injected entry (`at_step/2`). The provenance doc labels that distinction. No inferred-but-claimed-mined entries.
3. **Human-facing artifact rule.** Did not apply to this session (no story runs were executed here). Will apply when the narrative re-runs happen.
4. **Regression-first rule.** Safety gate was run before and after the registry change. 78 → 78. The Blocksworld baseline in this session was _not_ re-verified against live Ollama; that verification is still owed.

## 3) What Was Verified (evidence)

### 3.1 Safety gate
```
$ python scripts/run_safety_gate.py
...
78 passed in 6.92s   (pre-change)
78 passed in 3.72s   (post-registry-change)
[pass] safety gate passed
```
Both runs green. py_compile green on all four targets declared in `scripts/run_safety_gate.py`:
`kb_pipeline.py`, `ingest_frontend.py`, `scripts/run_story_progressive_gulp.py`, `scripts/run_story_raw.py`.

### 3.2 Registry schema compatibility
Read the actual loader in `kb_pipeline.py`:
- `_load_predicate_registry` at line ~561
- `_build_registry_alias_map` at line ~573
- `_build_registry_signature_set` at line ~814
- Strict admission enforced at line ~868 (`strict_registry and unknown → errors`)

The schema my registry file writes to matches exactly:
`{ "canonical_predicates": [ { "name": str, "arity": int, "aliases": [str] } ] }`

Loader also injects registry signatures into the prompt at line ~1062 (`"Allowed predicate signatures: …"`). This means the populated registry now _also_ constrains the parser at generation time, not just at admission time. Worth remembering — if a narrative run starts producing very different outputs after this change, that prompt injection is the likely cause.

### 3.3 Mining statistics
- `kb.pl` files scanned in `kb_store/`: **169**
- Directories name-tagged as Blocksworld: **0** (all Blocksworld predicates live in domain-specific KBs but none are prefixed `blocksworld_` in `kb_store/`)
- Unique predicate names seen: **157**
- Long-tail predicates (appeared in exactly 1 KB): **101**

### 3.4 Inclusion rules for the candidate registry
- `kb_count >= 2` (predicate appeared in at least two independent KB runs)
- Single dominant arity OR dominant arity >= 85% of occurrences
- Name length <= 28 chars, <= 3 underscores (heuristic against phrasal parse drift)

Result:
- Included: **55** (see final registry file for the full list)
- Sanity-rejected: **4** (see §4)
- Low-coverage-rejected: **98** (kb_count==1; strict mode will now reject these until they re-occur and can be promoted)
- Arity-conflict-flagged: **0**

### 3.5 Predicates in the final registry, ranked by KB coverage
Top-15 most-supported, with arity:
1. `parent/2` — 94 KBs / 440 occ
2. `ancestor/2` — 81 / 265
3. `carries/2` — 37 / 41
4. `inside/2` — 33 / 85
5. `in_region/2` — 33 / 69
6. `lives_in/2` — 26 / 76
7. `man/1` — 20 / 46
8. `approver/2` — 15 / 70
9. `manager_of/2` — 15 / 36
10. `requester/2` — 15 / 66
11. `eligible/1` — 15 / 15
12. `conflict/2` — 13 / 35
13. `mortal/1` — 13 / 13
14. `at/2` — 8 / 19
15. `sibling/2` — 7 / 10

Full list: `modelfiles/predicate_registry.json` and `tmp/predicate_registry.candidate.md`.

### 3.6 Injected-not-mined
- `at_step/2` — default temporal predicate per `docs/RUNTIME_SETTINGS_CHEATSHEET.md`.
  Not yet present in any general-lane KB because the mined KBs weren't run with `--temporal-dual-write`.
  Without this, any strict general lane with temporal mode on would reject every temporal fact.

## 4) Findings That Deserve Separate Attention

### 4.1 Parser bug: phrase-as-predicate drift
One predicate surfaced in mining that is not drift but a repeat failure:
- **`tracking_maritime_handoff_custody/1`** appeared in **4 independent KBs** under the
  `acid_05_long_context_lineage_*` family. Length 33, 4 underscores. This is a whole
  phrase being jammed into a single predicate identifier.

Other single-KB instances of the same pattern:
- `site_prep_is_a_task/1` (rung_241)
- `go_live_is_a_milestone/0` (note the 0-arity! another parse failure on top)
- `go_live_is_a_task/1`

**This is not a registry problem.** The strict registry will now correctly reject these, but that's the downstream safety net. The upstream fix is a parser-side post-filter that rejects or repairs predicate names with:
- length > ~25 chars
- more than 3 underscores
- containing English filler tokens (`_is_a_`, `_to_a_`, `_of_the_`)
- arity 0 for a nominal concept (`go_live` as a bare atom is almost never what you want)

Recommend: add `tracking_maritime_handoff_custody` and a small synthetic analog to `tests/` as an explicit regression fixture, independent of any narrative score.

### 4.2 The long tail is bigger than it looks
98 predicates appear in exactly one KB. Many are plausible and will recur (`supervises/2`, `holds/2`, `recommended/2`, `violation/2`). Some are domain-specific one-offs. The strict registry will reject all of them on next run.

Two reasonable responses:
- **Keep strict strict.** Accept the short-term rejection storm. Promote predicates to the registry only when `kb_count` crosses 2 in a rolling window of runs.
- **Add a "soft registry" mode.** Admit unknown predicates but log them to a `pending_promotions` file. Human review promotes to canonical. (Not implemented.)

The first is honest to the handoff's philosophy ("the strict gate finally bites"). The second is more ergonomic for frontier lanes. My opinion: start strict. Measure the damage. Only soften if the damage is disproportionate to the signal.

### 4.3 Arity drift pattern to watch
`blocked` in mining had `{1: 10, 2: 1}`. Made the 85% threshold at 0.909. But one KB emitted `blocked/2`. That's either a semantically-different usage that deserves to be a separate predicate (e.g. `blocked_by(X,Y)`) or a parse slip. Worth inspecting the lone `blocked/2` KB and deciding which.

### 4.4 The "strict" vs "general" registry distinction is not cleanly named
`modelfiles/predicate_registry.json` is the general registry. `modelfiles/predicate_registry.blocksworld.json` is the Blocksworld registry. If more domains accrete (e.g. a legal-reasoning registry), the naming convention `predicate_registry.<domain>.json` is fine, but the _general_ one has no domain suffix and that asymmetry invites config-mismatch bugs.

Recommend: rename the general registry to `predicate_registry.general.json` in a future cycle and add a symlink / loader fallback. Low priority, moderate payoff for clarity.

## 5) Critique of the Handoff (my opinion, flagged as such)

Codex's handoff is unusually honest and well-structured. Three specific places where I would push back or add nuance:

### 5.1 The zero-hit gate is too lenient as the sole baseline guard
`--max-zero-hit 0` fails only when a case gets 0 init-hit AND 0 goal-hit. The current average is 0.458 / 0.458 across 8 pilot cases. A slow regression to 0.3 / 0.3 — still painful, still meaningful — would never trip the gate.

Recommend a companion flag: `--min-avg-init-hit 0.40 --min-avg-goal-hit 0.40` (or wherever the honest floor is after one stable baseline). Update `gates.zero_hit` summary block into `gates.hit_ratios` with both signals. This is a small code change in `scripts/run_blocksworld_lane.py`.

### 5.2 The config-mismatch footgun already fired once
Section 10 of `CODE-HANDOFF.md` admits: _"caveat: these used an effectively empty general strict registry"_. That's the footgun from Section 11 already having bitten. It deserves to be a hard guardrail, not a doc warning.

Specific implementation:
- In `scripts/run_story_pack_suite.py` and `scripts/run_story_progressive_gulp.py`, if `--predicate-registry` is a domain file (e.g. `*.blocksworld.json`) and the pack label does not claim to be that domain, exit non-zero unless `--allow-cross-domain-registry` is passed.
- Alternatively, require `--registry-profile {general,blocksworld,…}` and have the runner pick the file, removing the chance of wrong-path config.

### 5.3 Temporal question floor is enforced at the wrong layer
Section 11.4 notes: _"Some dense runs under temporal mode still emit too few temporal questions."_ Looking at the interrogator, the floor is set via `--exam-min-temporal-questions` but, per the handoff, not consistently reached. If the exam generator can't derive enough temporal questions from extracted content, it should synthesize fallback questions directly from `at_step/2` facts in the KB rather than silently under-covering. That keeps the contract honest.

## 6) What's Actually Changed On Disk This Session

Modified:
- `modelfiles/predicate_registry.json` — was `{"canonical_predicates": []}`, now has 56 entries.

Created:
- `modelfiles/predicate_registry.json.empty-backup-2026-04-17` — backup of the prior empty file.
- `docs/reports/GENERAL_REGISTRY_POPULATION_2026-04-17.md` — curated provenance note.
- `tmp/mine_predicates.py` — miner (keep; it's a useful tool for future re-mines).
- `tmp/build_registry_candidate.py` — candidate builder with threshold rules.
- `tmp/predicate_inventory.json` / `tmp/predicate_inventory.md` — full inventory with attribution.
- `tmp/predicate_registry.candidate.json` / `tmp/predicate_registry.candidate.md` — proposed registry + rejection rationale.
- `CLAUDE-WORK.md` — this document.

Not created (worth considering):
- A `tests/test_predicate_registry_sanity.py` that loads the registry, asserts arities are positive integers, asserts no duplicate names, asserts `at_step/2` is present when temporal mode is referenced elsewhere. Cheap, catches future corruption.
- A `tests/test_phrasal_predicate_regression.py` that feeds the pipeline a snippet known to have produced `tracking_maritime_handoff_custody` and asserts the extracted predicate name satisfies the sanity rules. This is a parser fix first, then a test.

## 7) Sandbox / Ollama Situation (and why work split the way it did)

Ollama is running on Scott's Windows box at `127.0.0.1:11434`. The Cowork sandbox this session runs in cannot reach it. Diagnostic:

- Outbound traffic from sandbox goes through a Squid proxy at `localhost:3128`.
- Proxy has a URL allowlist. Confirmed reachable: `pypi.org`, `github.com`, `api.anthropic.com`, `registry.npmjs.org`. Confirmed blocked by allowlist: `example.com`, `trycloudflare.com`, `api.ngrok.com`, `api.openai.com`.
- Host paths explicitly blocked at proxy: `host.docker.internal:11434`, `172.17.0.1:11434` → "Connection blocked by network allowlist".
- `127.0.0.1:11434` inside sandbox is the sandbox's own loopback, not Scott's host.

Implication: until Cowork's network allowlist (Admin → Capabilities) is broadened or a tunnel-endpoint domain is added to the allowlist, the sandbox cannot drive Ollama. This is a Cowork config constraint, not a bug.

Workable paths forward:
1. **Admin allowlist change.** Add a tunnel domain (`*.trycloudflare.com` or `*.ngrok-free.app` or a Tailscale Funnel hostname) to Cowork's allowlist, expose Ollama through that tunnel, set `--base-url` to the tunnel URL.
2. **Keep the split.** Claude in sandbox for code + analysis + scripts; Scott on Windows for Ollama-touching runs. This is what worked this session.

Prior agents (Codex per the handoff) probably did not hit this because they ran directly on Windows, not in a sandbox.

## 8) What the Next Agent Must Do First (priority-ordered)

### Priority 1 — Finish verifying the registry change on live Ollama
Ownership: Scott, on Windows, or Claude if the Ollama tunnel is set up.

```powershell
# 1) Blocksworld baseline must still pass (uses its own registry, so should be unaffected)
python scripts/run_blocksworld_lane.py `
  --sample-size 20 --max-objects 4 --planner-depth 12 `
  --run-prethinker --prethinker-cases 8 `
  --backend ollama --base-url http://127.0.0.1:11434 `
  --model qwen3.5:9b `
  --prompt-file modelfiles/semantic_parser_system_prompt.md `
  --context-length 8192 `
  --prethinker-split-mode full `
  --predicate-registry modelfiles/predicate_registry.blocksworld.json `
  --strict-registry --max-zero-hit 0 `
  --summary-json tmp/blocksworld_lane_post_registry_20260417.summary.json `
  --summary-md docs/reports/BLOCKSWORLD_LANE_POST_REGISTRY_2026-04-17.md

# 2) Narrative packs, now honestly strict, to replace the provisional 0.6452 / 0.8718
python scripts/run_story_pack_suite.py `
  --packs tmp/story_pack_mid.md,tmp/story_pack_upper_mid.md `
  --backend ollama --base-url http://127.0.0.1:11434 `
  --model qwen3.5:9b `
  --prompt-file modelfiles/semantic_parser_system_prompt.md `
  --context-length 8192 `
  --predicate-registry modelfiles/predicate_registry.json `
  --strict-registry `
  --exam-style detective --exam-question-count 20 --exam-min-temporal-questions 4
```

Expected: Blocksworld still 8/8 pipeline pass, zero-hit 0. Narrative scores may drop — that drop is the honest number the handoff was asking for. Record both in a new `docs/reports/NARRATIVE_PACKS_POST_REGISTRY_2026-04-17.md`.

### Priority 2 — Add the min-avg-hit gate to Blocksworld
Small code change in `scripts/run_blocksworld_lane.py`:
- Add `--min-avg-init-hit` and `--min-avg-goal-hit` flags.
- Fail non-zero if averages fall below the thresholds.
- Add the new signals to `gates.*` summary block.
- Update `CODE-HANDOFF.md` baseline command in Section 6 / Section 14.

This protects against slow regressions that would not trip `--max-zero-hit`.

### Priority 3 — Harden the config-mismatch guardrail
Two-part:
- Short path: validate `--predicate-registry` in the suite runners. If the file is a known domain-specific registry (detect by name suffix or content heuristics), require a `--allow-cross-domain-registry` override.
- Long path: introduce `--registry-profile {general,blocksworld,<future>}` and let the runner select the file. Deprecate the direct path argument over a few cycles.

### Priority 4 — Parser-side phrasal-drift filter + regression fixture
- Add predicate-name post-filter in `kb_pipeline.py` (or wherever clause normalization happens) that rejects/repairs names with length >25 or underscores >3. Decide whether to hard-reject or re-request.
- Add `tests/test_phrasal_predicate_regression.py` using the `tracking_maritime_handoff_custody` source material.

### Priority 5 — Temporal question floor enforcement in interrogator
- If exam generator can't meet `--exam-min-temporal-questions` from extracted content, synthesize from `at_step/2` facts before yielding.
- If still under-covered, emit a summary-level warning (not a silent pass).

### Priority 6 — CI-ish nightly loop
Not in scope this session. But Section 12 of `CODE-HANDOFF.md` describes a daily process that is entirely manual. A simple nightly job running safety gate + gated Blocksworld baseline and diffing the `.summary.json` against the prior day's would surface regressions at the moment they land.

## 9) Commands Scott Should Run, In Order

```powershell
# Sanity
ollama list
python scripts/run_safety_gate.py

# Confirm registry change didn't break Blocksworld
python scripts/run_blocksworld_lane.py `
  --sample-size 20 --max-objects 4 --planner-depth 12 `
  --run-prethinker --prethinker-cases 8 `
  --backend ollama --base-url http://127.0.0.1:11434 `
  --model qwen3.5:9b `
  --prompt-file modelfiles/semantic_parser_system_prompt.md `
  --context-length 8192 `
  --prethinker-split-mode full `
  --predicate-registry modelfiles/predicate_registry.blocksworld.json `
  --strict-registry --max-zero-hit 0 `
  --summary-json tmp/blocksworld_lane_post_registry_20260417.summary.json `
  --summary-md docs/reports/BLOCKSWORLD_LANE_POST_REGISTRY_2026-04-17.md

# Honest narrative strict re-run
python scripts/run_story_pack_suite.py `
  --packs tmp/story_pack_mid.md,tmp/story_pack_upper_mid.md `
  --backend ollama --base-url http://127.0.0.1:11434 `
  --model qwen3.5:9b `
  --prompt-file modelfiles/semantic_parser_system_prompt.md `
  --context-length 8192 `
  --predicate-registry modelfiles/predicate_registry.json `
  --strict-registry `
  --exam-style detective --exam-question-count 20 --exam-min-temporal-questions 4

# Optional: re-mine the registry after more KBs accumulate
python tmp/mine_predicates.py
python tmp/build_registry_candidate.py
# Inspect tmp/predicate_registry.candidate.md; diff against modelfiles/predicate_registry.json
```

## 10) Open Questions That Need Scott's Call

1. **Promotion threshold.** The candidate used `kb_count >= 2`. Is that the right floor, or should it be stricter (`>= 3`) to avoid noise, or looser (`>= 1`) to keep narrative lanes from imploding? My vote: keep `>=2` until one full narrative re-run tells us the damage size.
2. **Alias policy.** Several predicate pairs look like aliases but were not merged (e.g. `manager_of/2` vs `manages/2`; `approver/2` vs `approved_by/2`). Do you want them merged canonically, or kept distinct? The blocksworld registry uses aliases (`ontable` ↔ `on_table`) so the machinery supports it.
3. **Cross-domain registry behavior.** When running narrative content with the Blocksworld registry, should the pipeline fail fast (my recommendation) or just warn?
4. **`tracking_maritime_handoff_custody` fix direction.** Parser hard-rejects phrasal predicates, or parser re-requests with a shortening directive, or post-processor replaces with an anonymized canonical (`predicate_N`)? Each has different honesty tradeoffs.
5. **Cowork network access.** Do you want to enable an Ollama tunnel so I can drive lanes directly, or keep the split-work pattern from this session?

## 11) Appendix — Artifacts Index

Produced this session, by intended lifespan:

Curated (keep):
- `modelfiles/predicate_registry.json`
- `modelfiles/predicate_registry.json.empty-backup-2026-04-17`
- `docs/reports/GENERAL_REGISTRY_POPULATION_2026-04-17.md`
- `CLAUDE-WORK.md` (this file)

Useful tools (keep; they will be re-run):
- `tmp/mine_predicates.py`
- `tmp/build_registry_candidate.py`

Inspection artifacts (ephemeral, safe to delete):
- `tmp/predicate_inventory.json`
- `tmp/predicate_inventory.md`
- `tmp/predicate_registry.candidate.json`
- `tmp/predicate_registry.candidate.md`

## 12) Reading Order For The Next Agent

1. `CODE-HANDOFF.md` — the strategic map.
2. This document — what's changed since Codex wrote the map.
3. `docs/reports/GENERAL_REGISTRY_POPULATION_2026-04-17.md` — the registry fix in detail.
4. `docs/RUNTIME_SETTINGS_CHEATSHEET.md` — the knob reference.
5. `tmp/predicate_inventory.md` — if you're about to touch the registry again.

Then execute §8 Priority 1 on live Ollama before anything else.

## 13) Forward Assessment — Likely Successes, Likely Failures

This section is forecast, not fact. Confidence is labeled. Written at the end of the session for the next agent to stress-test.

### 13.1 Near-term, high confidence — Blocksworld re-run will stay green
Almost certain to pass. The Blocksworld lane uses `predicate_registry.blocksworld.json`, which was not touched. Hit ratios will remain ~0.458/0.458. If it breaks, treat as noise and look for environment drift, not registry impact. **~95% confidence.**

### 13.2 Near-term, genuinely uncertain — narrative re-run with populated registry
Two competing effects hit at once:
- **Precision gain:** the parser now sees a 56-signature allowlist injected into the prompt (`"You MUST use only allowed predicate signatures."`). Expect more conservative outputs, less invention.
- **Recall loss:** 98 singleton predicates (`kb_count == 1`) that survived silently before will now be strict-rejected. Anything that depended on those facts will fail admission.

Best-guess outcomes:
- **Mid pack** (prior provisional 0.6452) → likely drops into **0.40–0.55** range. Mid-pack content leaned on ops verbs that are mostly long-tail.
- **Upper-mid pack** (prior provisional 0.8718) → wide error bars. If it used core predicates (`parent`, `approver`, `requester`), may hold above **0.75**. If it relied on `supervises/2`, `set_task/1`, `completed/1`, `on_time/1` (all kb_count == 1 in my mining), it will drop into **0.55–0.70**.

**The drop is not a regression. It is the first honest number.** The temptation to "fix the numbers" by loosening strict mode or padding the registry with long-tail predicates is exactly the dishonest-strictness trap the handoff was built to escape. Resist it. Record the honest baseline, then improve from there.

### 13.3 Medium-term likely failures (the "this will keep biting" list)

**Phrasal-drift parser bug → systematically understated Ledger metrics.**
`tracking_maritime_handoff_custody/1` and its cousins will keep being emitted on Ledger-class content. Those facts will now be strict-rejected under the populated registry. The information was extracted; only the predicate name is broken. Until the parser-side post-filter lands (§8 Priority 4), Ledger exam pass rates will look worse than the actual extraction quality. **High confidence this persists until fixed.**

**Zero-hit gate will miss a slow Blocksworld regression.**
Current 0.458 average has significant headroom before any single case hits 0-init and 0-goal. A drift to 0.35 average is plausible after any model/prompt change and would not trip the gate. I expect this to happen within a few cycles unless the min-avg-hit gate lands (§8 Priority 2). **Medium-high confidence.**

**Config-mismatch footgun will fire again.**
It already fired once — the Section 10 caveat in `CODE-HANDOFF.md` is evidence of the bug having hit production metrics. Without the guardrail in §8 Priority 3, recurrence is a matter of time. **Treat as inevitable, not probabilistic.**

**Temporal coverage will stay flaky.**
`--exam-min-temporal-questions` is aspirational until the interrogator synthesizes fallback questions from `at_step/2` facts. Any "temporal reasoning pass rate" reported in the meantime has a silent denominator problem. **High confidence until §8 Priority 5 lands.**

### 13.4 Deferred decisions that may bite subtly

**Aliases not merged.** `manager_of/2` vs `manages/2`, `approver/2` vs `approved_by/2`, and similar pairs were left as distinct canonical predicates. If a story extracts with `manages/2` and a later question is phrased around "manager," the exam may fail a question the KB actually contains. Low-medium rate of false negatives. See §10 Q2.

**Registry size = prompt tokens.** 56 signatures injected into the prompt at generation time adds roughly 200–400 tokens to every parse. On `qwen3.5:9b` with `--context-length 8192` this is tolerable but not free. Watch for tail-end quality degradation on long inputs where the extra prompt eats into the content window. Low-probability issue but worth keeping an eye on.

**Bootstrap circularity of evidence-based mining.** The general registry is derived from the parser's own past outputs. That's the right move short-term but it means the parser's biases silently become the registry's biases. If the parser has systematic extraction gaps, the registry will codify them. Medium-term remedy is anchoring the registry against an external relation taxonomy (FrameNet / VerbNet / WordNet-relations). Not urgent; structural.

### 13.5 Structural oddity worth reconciling

Narrative provisional scores (0.6452 mid, 0.8718 upper-mid) are higher than the Blocksworld hit ratio (0.458). That inversion is suspicious when Blocksworld is the more structured lane. Most likely explanation: the scoring rubrics aren't comparable across lanes (exact init/goal state match is strictly harder than open exam Q&A). But if any dashboard or report starts treating lane scores as a single comparable axis, it will mislead readers. **Recommend documenting the rubric difference explicitly wherever lane scores appear side-by-side.**

### 13.6 Clean wins I expect

- Registry populated + provenance documented: problem solved until the general ontology is rotated.
- `tracking_maritime_handoff_custody` surfaced: pure signal that was not in the handoff. Fixable now that it's named.
- Safety gate stays durable: 78 tests, fast, consistent. No structural fragility observed.
- Codebase discipline: the repo is unusually self-honest about its own weaknesses, which is a strong predictor of being fixable.

### 13.7 The single biggest cross-cutting risk

Optimistic reinterpretation when numbers get uncomfortable.

If the narrative re-run drops significantly and the response is "let's back off `--strict-registry`" or "let's add the long-tail predicates too," the cultural discipline that makes Prethinker legible — honest attribution, strict-means-strict, regression-first — collapses back to theater.

The hardest thing to protect is not the code. It is the rule that a lower honest number beats a higher dishonest one. Watch for that drift the moment scores look bad.

---

If you are the next agent reading this: the registry is populated but not yet verified against a live model. That verification is the single highest-value action available. Do that first; everything else in §8 depends on it.
