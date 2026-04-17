# General Predicate Registry — First Population

Date: 2026-04-17
Author: Claude (Opus 4.6) via Cowork
Target: Priority 1 of `CODE-HANDOFF.md` (2026-04-17)

## 1) What changed

- `modelfiles/predicate_registry.json` was empty (`{"canonical_predicates": []}`).
- It now contains 56 canonical predicates.
- The prior empty file is preserved at `modelfiles/predicate_registry.json.empty-backup-2026-04-17`.

## 2) How the predicate set was chosen

Method: mine every `kb_store/*/kb.pl` produced by the pipeline (169 files), extract
head and body predicate signatures, rank by KB-coverage and arity stability.

Rules:
- `kb_count >= 2` (predicate appeared in at least two independent KB runs)
- Single dominant arity, with dominant fraction >= 85% of occurrences
- Name length <= 28 chars, <= 3 underscores (reject phrasal parse drift)

Result:
- 55 mined predicates met the threshold
- 1 added manually: `at_step/2` — required for temporal mode per
  `docs/RUNTIME_SETTINGS_CHEATSHEET.md`; temporal runs weren't yet present
  in general KBs, so it was injected rather than mined.
- 4 sanity-rejected phrasal-drift names (see §4)
- 98 low-coverage (`kb_count == 1`) predicates excluded; they will be
  treated as unknown by strict mode and should either be promoted when
  they recur or flagged for the parser team.

Raw inventory: `tmp/predicate_inventory.json`, `tmp/predicate_inventory.md`
Candidate build: `tmp/predicate_registry.candidate.json`,
`tmp/predicate_registry.candidate.md`
Miner scripts: `tmp/mine_predicates.py`, `tmp/build_registry_candidate.py`

## 3) Expected blast radius

- Strict general lanes (e.g. `run_story_pack_suite.py` with
  `--predicate-registry modelfiles/predicate_registry.json --strict-registry`)
  that previously emitted one-off predicates will now fail admission.
- This is the intended direction: the handoff flagged the previous
  "strict" scores (mid 0.6452, upper-mid 0.8718) as misleading because the
  registry was empty. Honest re-scoring against this populated registry
  is the next step.
- The Blocksworld lane is unaffected: it uses `predicate_registry.blocksworld.json`.

## 4) Parser observation worth flagging

A mined "phrasal predicate" worth escalating as a parser bug (not a
registry issue):

- `tracking_maritime_handoff_custody/1` appeared in **4 independent KBs**
  under different `acid_05_long_context_lineage_*` and related dirs.
- Length 33, 4 underscores — this is not random drift. The parser is
  systematically converting a whole phrase ("tracking maritime handoff
  custody") into a single predicate identifier when processing the Ledger-
  class material.
- Other phrasal drift found: `site_prep_is_a_task/1`,
  `go_live_is_a_milestone/0`, `go_live_is_a_task/1`.

Recommendation: add a max-predicate-name-length policy (or underscore
count) to the parser's post-filter so these fail early rather than
polluting strict admission thresholds. Treat `tracking_maritime_handoff_custody`
specifically as a regression fixture.

## 5) Verification done locally

- `python scripts/run_safety_gate.py`: **78 passed** before and after the
  registry change. No structural regression.
- Registry file validates as JSON and parses to 56 predicates
  (arity 1: 16, arity 2: 38, arity 3: 2).

## 6) What still needs to run (requires live Ollama)

The sandbox that produced this change cannot reach the local Ollama
server. Please re-run on the Windows box:

```powershell
# Blocksworld baseline (must stay green)
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
  --summary-json tmp/blocksworld_lane_gate_post_registry_20260417.summary.json `
  --summary-md docs/reports/BLOCKSWORLD_LANE_POST_REGISTRY_2026-04-17.md

# Honest narrative strict re-run (replaces the provisional 0.6452 / 0.8718)
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

Expected: Blocksworld gate still green, zero-hit still 0. Narrative
scores likely to drop initially as the strict gate finally bites — that
drop is the honest number the handoff has been asking for.
