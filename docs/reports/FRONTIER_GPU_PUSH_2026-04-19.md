# Frontier GPU Push — April 19, 2026

## Headline

The frontier scaffolding held cleanly on a fresh GPU push:

- Safety gate: `126 passed`
- Blocksworld guarded lane: stable and green
- Glitch temporal line lane: stable at the recovered April 19 level
- HN midground lane: still difficult, but one concrete bogus retract failure was removed

## Stable Lanes

### Safety Gate

- Command: `python scripts/run_safety_gate.py`
- Result: `126 passed`

### Blocksworld Guarded Lane

- Summary: [tmp/blocksworld_lane_guarded_20260419_frontier.summary.json](</D:/_PROJECTS/prethinker/tmp/blocksworld_lane_guarded_20260419_frontier.summary.json>)
- Report: [BLOCKSWORLD_LANE_GUARDED_2026-04-19.md](</D:/_PROJECTS/prethinker/docs/reports/BLOCKSWORLD_LANE_GUARDED_2026-04-19.md>)

Headline metrics:

- symbolic solved/replay verified: `20/20`
- prethinker pilot pass: `8/8`
- avg init hit: `0.458334`
- avg goal hit: `0.458334`
- zero-hit case count: `0`

### Glitch Temporal Recheck

- Summary: [tmp/glitch_frontier_recheck_temporal4_20260419.summary.json](</D:/_PROJECTS/prethinker/tmp/glitch_frontier_recheck_temporal4_20260419.summary.json>)
- Report: [GLITCH_FRONTIER_RECHECK_TEMPORAL4_2026-04-19.md](</D:/_PROJECTS/prethinker/docs/reports/GLITCH_FRONTIER_RECHECK_TEMPORAL4_2026-04-19.md>)

Headline metrics:

- pipeline pass: `1/1`
- coverage: `0.85`
- precision: `0.92`
- exam: `11/14`
- temporal exam: `3/5`
- score: `0.8914`

This matched the earlier April 19 temporal recovery result, which makes the temporal improvement look reproducible rather than lucky.

## HN Midground

### MCP-vs-Skills Debate Thread

- Summary: [hn_mcp_over_skills_debate_v3_frontier12.summary.json](</D:/_PROJECTS/prethinker/tmp/runs/hn_midground_v3_frontier12_20260419/hn_mcp_over_skills_debate_v3_frontier12.summary.json>)

Headline:

- session stayed alive end-to-end
- no pending clarifications
- readiness grade: `C`

This remained dominated by speculative/opinion turns that mostly stayed on `other`, which matches the known wild-mode limitation.

### Signal Notification Forensics Thread

- Before fix: [hn_signal_notification_forensics_v3_frontier12.summary.json](</D:/_PROJECTS/prethinker/tmp/runs/hn_midground_v3_frontier12_20260419_signal/hn_signal_notification_forensics_v3_frontier12.summary.json>)
- After fix: [hn_signal_notification_forensics_v3_frontier12_fix1.summary.json](</D:/_PROJECTS/prethinker/tmp/runs/hn_midground_v3_frontier12_20260419_signal_fix1/hn_signal_notification_forensics_v3_frontier12_fix1.summary.json>)

Headline:

- readiness grade stayed `C`
- the first factual OP turn still compiled plausibly
- the bad explicit-goal fallback no longer fabricated `retract(tudy (my article)).`

## Improvement Made During This Push

The explicit Prolog-like fallback in [kb_pipeline.py](</D:/_PROJECTS/prethinker/kb_pipeline.py>) was tightened so it now requires:

- a real clause boundary before the predicate name
- immediate `predicate(` shape rather than accepting prose like `Study (my article)`

Focused regressions were added in [tests/test_split_extraction_refine.py](</D:/_PROJECTS/prethinker/tests/test_split_extraction_refine.py>).

Result:

- `Case Study (my article)` no longer gets misread as a retract target
- the HN Signal thread still runs, but the bogus retract target disappears
- the general safety scaffold remains green

## Bottom Line

The stable lanes are still stable. The temporal lane recovery held. The HN lane is still the hardest frontier, but it is at least slightly less brittle after this pass, and the supporting scaffolding remains healthy enough to keep spending GPU time on the right problems.
