# Wild Failure Isolation (Science Loop)

Last updated: 2026-04-13
Source run: `tmp/runs/tracks/track_excursion_frontier_v2_full_summary_20260413_203539.json`

## Why This Exists

This file is the conversion layer from frontier failure to engineering action.
If a miss pattern appears repeatedly in real discourse, we treat it as a first-class test target and promote it into a rung.

## Snapshot (2026-04-13)

- Track: `excursion_frontier_v2_full`
- Result: `5/12` passed (`41.67%`)
- Failed scenarios: `7`

## Isolated Failure Cases

### 1) Relation drop in multi-clause policy discourse

Scenarios:

- `rung_454_excursion_coop_fed_policy_hold`
- `rung_456_excursion_coop_scotus_exception_logic`
- `rung_462_excursion_coop_fed_labor_inflation_balance`

Observed misses:

- `needs_confidence_before(chair, easing_policy)` -> `no_results`
- `liable(case_alpha)` -> `no_results`
- `requires(policy_easing, sustained_evidence)` -> `no_results`

Pattern:

- critical relation facts are lost while narrative context remains partly tracked
- turns frequently route to `other`, so no mutation is applied

### 2) Parenthetical exception collapse

Scenario:

- `rung_464_excursion_coop_scotus_parenthetical_exception`

Observed misses:

- `exception_for(notice_rule, emergency_response_entries)` -> `no_results`
- `applies_to(emergency_response_exception, case_beta)` -> `no_results`
- `does_not_apply_to(emergency_response_exception, case_alpha)` -> `no_results`

Pattern:

- parenthetical exception language causes major extraction loss
- this is currently the harshest failure (`1/5`, parse/apply failures present)

### 3) Scope correction persistence failure

Scenario:

- `rung_459_excursion_hn_scope_correction`

Observed miss:

- `corrected_scope_to(docker_pull_failures, single_isp_segment)` -> `no_results`

Pattern:

- correction instruction is heard, but not reliably committed as structured state

### 4) Advice and goal extraction misses in legal/noisy threads

Scenario:

- `rung_460_excursion_reddit_landlord_entry_timeline`

Observed misses:

- `seeks(tenant, terminate_lease)` -> `no_results`
- `advised_to(tenant, send_written_demand_first)` -> `no_results`

Pattern:

- conversational legal advice often routes as commentary (`other`) rather than commit-worthy relations

### 5) Scope split relation not captured

Scenario:

- `rung_457_excursion_hn_codex_claude_scope_split`

Observed miss:

- `prefers_for(op, claude, tiny_single_file_edits)` -> `no_results`

Pattern:

- preference/scope assignment sentence survives semantically but is not persisted as relation

## Candidate Fixes (Next Tricks To Pull)

1. Add a mixed-intent splitter before route finalization.
2. Add anti-`other` backstop when utterance contains fact-like relation templates.
3. Add explicit parenthetical-exception templates to prompt + deterministic normalizer.
4. Add lexical templates for advisory and goal intents (`seeks`, `advised_to`, `asked_about`).
5. Add correction-persistence guard that prioritizes `corrected_scope_to` style updates.
6. Expand rung validations to include negative checks (prevent false opposite commitments).

## Promotion Loop (Failure -> Rung)

1. Detect repeated failure signature in excursion runs.
2. Promote to explicit frontier rung with minimal story wrapping.
3. Add at least one positive and one negative validation.
4. Re-run ladder + excursion.
5. Keep the rung permanent if it catches a real blind spot.

## Already Promoted This Cycle

- `rung_465_frontier_failure_multiclause_scope_drop_guard`
- `rung_466_frontier_failure_exception_rule_partition`
- `rung_467_frontier_failure_question_advice_dual_intent`

These are the first direct artifacts from this failure-promotion loop.

## CE Boundary Findings (2026-04-13)

Additional sweeps showed a strong CE sensitivity boundary:

- `track_excursion_frontier_v2_full_cepush_summary_20260413.json`
  - settings: `ce=0.90`, rounds=`3`, served=`qwen3.5:9b`
  - result: `2/12` (`16.7%`)
- `track_excursion_failure_promotions_v1_cepush_summary_20260413.json`
  - settings: `ce=0.90`, rounds=`3`
  - result: `0/3` (`0.0%`)
- `track_excursion_failure_promotions_v1_cemed_summary_20260413.json`
  - settings: `ce=0.55`, rounds=`2`
  - result: `3/3` (`100%`)

Interpretation:

- high CE can over-escalate and starve factual commits.
- moderate CE restores commit flow but may under-exercise clarification routes in cleaner promoted-guard rungs.

## Clarification-Route Stress Findings

### Positive route exercise

- `20260413_221027_rung460_ce85_mitm/session_summary.json`
  - `committed_turns=9/9`
  - `fallback_resolution_total=4/4`
  - readiness grade `A`

### Hard stuck case

- `20260413_222531_hn_signal_v3_ce85_mitm/session_summary.json`
  - `committed_turns=13/15`
  - `pending_turns=2`
  - `fallback_resolution_total=0/4`
  - readiness grade `D`

Observed stuck pattern:

- clarification question asks for canonical user/predicate identity that remains unresolved.
- sidecar fallback answers are accepted but replay still ends in `clarification_requested` due max-round cap.

## Bare-vs-Baked Drift Check (Hard Cases)

Source: `tmp/runs/sp_parity/sp_parity_summary_push_20260413.json`

- scenarios: `4`
- parity mismatches: `1`
- mismatch case:
  - `rung_444_frontier_unpunctuated_coref_sweep`
  - runtime lane: `4/6` failed
  - baked lane: `2/6` failed

Takeaway:

- most tested hard cases were parity-aligned, but some non-trivial drift remains.
- keep parity checks in the loop when changing CE policy or prompt delivery mode.
