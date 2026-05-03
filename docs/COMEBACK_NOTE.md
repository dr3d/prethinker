# Comeback Note

Last updated: 2026-05-03 13:30 America/New_York

This note is for the next Codex session after a system reboot. It captures the
current research state and the next useful moves. The durable repo head before
this note was `3c1d856`.

## Ground Rules

- Keep Python out of language understanding.
- Python may handle structured JSON, admitted Prolog clauses, scoring records,
  deterministic validation, test orchestration, and documentation.
- Python must not read source prose to derive predicates, facts, entities,
  answers, or rule meanings.
- Evidence lanes matter. Do not compare cold, diagnostic replay, assisted, and
  oracle calibration scores as if they were the same claim.
- No more fixtures for now. Scott intentionally flooded the fixture pipeline;
  the next work should improve the harness and rotate across existing fixtures.

## Recent Published Commits

- `d50bc0e Add rule-lens backbone support index`
  - Added deterministic admitted-fact signature support summaries to
    `scripts/run_rule_acquisition_pass.py`.
  - This gives rule lenses counts/examples of already-admitted Prolog predicate
    signatures, without interpreting raw source prose.
  - Sable Creek `SC-004` produced the first fresh-fixture promotion-ready rule:

```prolog
derived_status(AmendmentId, requires_public_hearing, budget_amendment) :-
    amendment_introduced(AmendmentId, _, _, Amount),
    number_greater_than(Amount, 50000).
```

- `95ab0bc Gate unsupported durable rule constructs`
  - Hardened `src/semantic_ir.py` mapper rule admission.
  - Durable LLM-authored rule clauses are now skipped when they use raw Prolog
    negation, disjunction, lists, arithmetic, equality, or comparisons.
  - These constructs should be represented through deterministic helper
    predicates or future explicitly supported substrates.

- `0d399aa Record Avalon post-gate rule union`
  - Recorded Avalon `AG-005` and `AG-006`.
  - Post-gate Section A rule replay retained `3` executable clauses, including
    `2` promotion-ready Rule 5 matching-fund helper-composed branches and `0`
    unsupported body goals.
  - Unioning those post-gate rules into AG-001 produced:
    `27 exact / 10 partial / 3 miss`.
  - Older rule union had `27 exact / 8 partial / 5 miss`, so the gate reduced
    misses without losing exact count.
  - Mode comparison upper bound across baseline, old union, and post-gate union
    is `29 exact / 9 partial / 2 miss`, proving row-level activation still has
    headroom.

- `3c1d856 Record CE source-context regression check`
  - Reran Clarification Eagerness after rule work.
  - CET-013 with source context:
    `40/40` correct, `0` over-eager, `0` under-eager, `0` unsafe candidates,
    `0` context-write violations, `10/10` blocked-slot coverage.
  - Safe partials were `11/13`, so remaining CE nuance is safe-partial richness,
    not ask/no-ask posture.

## Current Test State

Latest full suite before this note:

```text
450 passed, 2 subtests passed
```

No Python runners were active after the last check. Worktree was clean before
creating this note.

## Current Research Thesis

The central insight is now:

```text
A single LLM pass is one viewpoint.
Semantic parallax uses multiple constrained lenses.
Only mapper-admitted clauses accumulate.
Rules become useful only after mapper admission, runtime trial,
body-support checks, helper-substrate checks, positive/negative probes,
and promotion filtering.
```

Multi-pass semantic compilation is no longer just a docs idea. It has evidence:

- APR showed safe-support union can beat a single compile.
- Glass Tide showed rule branches need separate lenses and promotion trials.
- Sable showed a fresh governance fixture can produce a body-supported
  promotion-ready rule under stricter gates.
- Avalon showed the stricter mapper keeps useful helper-composed rules while
  dropping unsupported raw Prolog constructs.
- CE stayed stable after rule work, which means admission/clarification posture
  did not regress.

## Important Fixture State

### Sable Creek Budget

- Cold baseline `SC-001`: `20 exact / 8 partial / 12 miss`.
- Rule diagnostics:
  - `SC-002`: found unsafe unbound-head and fact-shaped rule clauses.
  - `SC-003`: compact guidance made failures cleaner but not promotion-ready.
  - `SC-004`: backbone fact-signature support produced first promotion-ready
    fresh-fixture rule.
- Key lesson: support summary over admitted Prolog rows helps the LLM choose
  body predicates that actually exist.

### Avalon Grant Committee

- Cold baseline `AG-001`: `25 exact / 12 partial / 3 miss`.
- Rule 5 helper lens `AG-003`: `3` promotion-ready threshold/ratio rules.
- Old union `AG-004`: `27 exact / 8 partial / 5 miss`.
- Post-gate union `AG-006`: `27 exact / 10 partial / 3 miss`.
- Key lesson: better mapper hygiene reduces harmful rule-surface perturbation,
  but global rule activation can still move answers around. Need row-level
  activation or fallback selection.

### Clarification Eagerness Trap

- Source-context high water remains stable at `40/40`.
- No-source-context run regressed to `24/40` due to over-eager asks, proving CE
  must always report context availability.
- Current remaining CE edge: safe partial preservation, not ask/no-ask.

### Cold Generalization Lane

The currently recorded aggregate over ten newly admitted source-only fixtures:

```text
245 exact / 81 partial / 144 miss across 470 QA items
exact = 0.521
exact+partial = 0.694
```

The cold lane is meant to guard against overfitting. Do not over-bake one
fixture. Rotate across them.

## Next Best Work

1. **Row-Level Activation / Fallback Selection**
   - Problem: safe accumulated surfaces can rescue some QA rows but perturb
     already-correct rows.
   - Evidence: Avalon post-gate rule union has diagnostic upper bound
     `29 exact / 9 partial / 2 miss`, but no oracle selector is allowed.
   - Needed: pre-judge structural signals for when to activate alternate
     evidence/rule surfaces.
   - Candidate signals:
     - baseline query returned no rows;
     - baseline query rows lack answer-bearing variables;
     - baseline query uses only generic source records;
     - alternate surface contributes derived rows whose head predicate matches
       question mode;
     - baseline self_check or failure classifier predicts query-surface or
       hybrid-join risk.
   - Do not use reference answers or judge labels at runtime. Use them only for
     diagnostic reporting.

2. **Rule Composition**
   - Current durable mapper blocks raw Prolog control constructs.
   - Next helper substrates likely needed:
     - bounded negation / absence;
     - disjunction as enumerated helper relations;
     - temporal comparisons through helpers;
     - business-day / deadline helpers;
     - aggregate threshold helpers with intermediate conditions.
   - Keep branch types explicit:
     `threshold`, `exception`, `priority_override`, `aggregation`,
     `temporal_window`, `bounded_negation`, `role_join`.

3. **Regression Cadence**
   - Any central mapper/rule change should rerun:
     - full pytest;
     - a compact CE source-context run;
     - one rule-heavy replay from Avalon or Glass Tide;
     - one fresh/cold fixture summary if practical.

4. **Docs / Public Framing**
   - `docs/CURRENT_RESEARCH_HEADLINE.md` is the daily/front-page research
     headline.
   - Keep it current and punchy, not desperate.
   - The project’s credibility comes from transparent journals, not hype.

## Useful Commands

Full tests:

```powershell
python -m pytest -q
```

Sable-style rule lens pattern:

```powershell
python scripts\run_rule_acquisition_pass.py `
  --text-file datasets\story_worlds\sable_creek_budget\story.md `
  --backbone-json tmp\cold_baselines\sable_creek_budget\domain_bootstrap_file_20260503T155415725989Z_story_qwen-qwen3-6-35b-a3b.json `
  --profile-registry tmp\cold_baselines\sable_creek_budget\source_derived_registry_sable_creek_budget.json `
  --domain-hint "municipal charter amendment threshold rule diagnostic replay" `
  --out-dir tmp\cold_baselines\sable_creek_budget\rules `
  --source-line-start 5 `
  --source-line-end 18 `
  --compact-guidance `
  --operation-target 2 `
  --max-tokens 2200 `
  --timeout 60 `
  --temperature 0.0 `
  --top-p 0.82 `
  --rule-class threshold `
  --allowed-predicate-filter "charter_rule/3,voting_threshold/3,amendment_introduced/4,derived_condition/3,derived_status/3,number_greater_than/2,number_at_most/2"
```

Avalon post-gate style comparison:

```powershell
python scripts\compare_qa_mode_artifacts.py `
  --group avalon:baseline=tmp\cold_baselines\avalon_grant_committee\domain_bootstrap_qa_20260503T143610001875Z_qa_qwen-qwen3-6-35b-a3b.json,old_rule_union=tmp\cold_baselines\avalon_grant_committee\union\domain_bootstrap_qa_20260503T151019375682Z_qa_qwen-qwen3-6-35b-a3b.json,postgate_rule_union=tmp\cold_baselines\avalon_grant_committee\union\domain_bootstrap_qa_20260503T172017844591Z_qa_qwen-qwen3-6-35b-a3b.json `
  --out-md tmp\cold_baselines\avalon_grant_committee\union\avalon_rule_union_mode_comparison.md `
  --out-json tmp\cold_baselines\avalon_grant_committee\union\avalon_rule_union_mode_comparison.json
```

CE source-context check:

```powershell
python scripts\run_clarification_eagerness_fixture.py `
  --surface both `
  --include-source-context `
  --temperature 0.0 `
  --max-tokens 2200 `
  --timeout-seconds 60
```

## Watchouts

- `rg.exe` threw `Access is denied` once after the repo move to `C:\prethinker`.
  PowerShell `Select-String` fallback worked. If this persists, diagnose later;
  not currently a blocker.
- Local temp artifacts are large and mostly ignored. Preserve named progress
  journals and metrics in repo; do not commit bulky tmp JSON unless explicitly
  desired.
- Be careful with path typos in metrics. Some previous hand edits briefly used
  `qwen3-6b-a3b`; correct model string is `qwen-qwen3-6-35b-a3b` in artifact
  filenames.
- Do not generate new fixtures right now. Scott explicitly said no more fixtures.

## Suggested First Action After Reboot

1. Run `git status --short`.
2. Read this note plus:
   - `docs/CURRENT_RESEARCH_HEADLINE.md`
   - `docs/MULTI_PASS_SEMANTIC_COMPILER.md`
   - `datasets/story_worlds/avalon_grant_committee/progress_journal.md`
   - `datasets/story_worlds/sable_creek_budget/progress_journal.md`
3. If this note is not committed yet, commit it.
4. Continue with row-level activation / fallback selection research.
