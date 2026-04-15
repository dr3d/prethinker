# Focus Execution Plan

Last updated: 2026-04-15

## Objective

Keep one spine:

`English -> deterministic KB -> reliable interrogation`

No side quests unless they improve this path.

## Default Operating Stack

- Parser model: `qwen3.5:9b`
- Runtime: `core`
- Prompt source: `modelfiles/semantic_parser_system_prompt.md`
- Registry: strict (`--strict-registry`)
- Type schema: scenario-specific where available (Goldilocks profile for Goldilocks)
- Clarification: enabled with bounded rounds
- Frontend proposal: `off` during baseline stabilization

## Phases

1. Stabilize core
- Mandatory post-run interrogation for every baseline batch.
- Use one command path only.
- Freeze non-essential feature work.

2. Real-world pressure
- Focus on HN middle-noise lane and curated story regression.
- Promote repeated failure patterns into regression scenarios.

3. Medical lane (after UMLS approval)
- Start with a constrained UMLS subset.
- Add medical predicate/type profile.
- Run medical interrogation packs.

4. Frontend evolution
- Introduce constrained frontend proposals in `shadow` mode first.
- Promote to `active` only with consistent metric improvement.

## Hard Gates

- Fact precision >= `0.90`
- Fact coverage >= `0.85`
- Exam pass rate >= `0.80`
- Temporal exam pass rate >= `0.70`
- Incorrect KB mutation rate <= `0.02`

## Single Command Path

Run the focused baseline cycle (Goldilocks + HN middle-noise mini-pack):

```powershell
python scripts/run_gate_cycle.py --batch baseline_focus
```

Outputs:
- `tmp/runs/focus_cycles/<run_name>/summary.json`
- `tmp/runs/focus_cycles/<run_name>/summary.md`
- scenario-level pipeline + interrogator artifacts in same folder

## Weekly Rhythm

1. Run baseline focus cycle.
2. Review failed scenarios and interrogator bogus/missed facts.
3. Promote repeated misses to regression scenarios.
4. Re-run focus cycle and compare deltas.

## UMLS Readiness (pending approval email)

Pre-stage now:
- UMLS import pipeline skeleton
- medical registry/type schema profile
- medical interrogation pack templates

Go-live when license arrives:
- ingest a small validated slice first
- compare against pre-UMLS baseline using same interrogation gates
