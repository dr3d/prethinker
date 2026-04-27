# KB Interrogator

`kb_interrogator.py` grades a compiled `kb.pl` against source text and generates executable reasoning exams.

It does three things in one run:

1. Fact audit: flags likely missed facts and bogus facts.
2. Reasoning exam synthesis: builds query-level checks from the source material.
3. Deterministic scoring: executes those checks against Core runtime and reports pass/fail.

## Inputs

- Plain prose file: `.txt` / `.md`
- Scenario JSON (`utterances`)
- Run JSON (`turns[*].utterance`) from `kb_pipeline.py`

If source is run JSON, candidate KB can be auto-discovered from `kb_namespace.corpus_path`.

## Core Commands

Full-ingestion audit (explicit source + KB):

```powershell
python scripts/kb_interrogator.py `
  --source-text-file docs/data/roundtrip/goldilocks_roundtrip_input_story.md `
  --candidate-kb tmp/goldilocks_roundtrip_generated_kb.pl `
  --backend lmstudio --base-url http://127.0.0.1:1234 --model qwen/qwen3.6-35b-a3b `
  --exam-style general `
  --out-json tmp/goldilocks_interrogator.json `
  --out-md tmp/goldilocks_interrogator.md
```

As-you-go interrogation (prefix turns from a run JSON):

```powershell
python scripts/kb_interrogator.py `
  --source-text-file tmp/goldilocks_roundtrip_run_latest.json `
  --through-turn 12 `
  --backend lmstudio --base-url http://127.0.0.1:1234 --model qwen/qwen3.6-35b-a3b `
  --exam-style detective `
  --out-json tmp/goldilocks_interrogator_turn12.json `
  --out-md tmp/goldilocks_interrogator_turn12.md
```

Run JSON interrogation with KB auto-detect + exam scenario export:

```powershell
python scripts/kb_interrogator.py `
  --source-text-file tmp/goldilocks_roundtrip_run_latest.json `
  --backend lmstudio --base-url http://127.0.0.1:1234 --model qwen/qwen3.6-35b-a3b `
  --exam-style detective --exam-question-count 10 `
  --emit-exam-scenario tmp/scenarios/goldilocks_exam_from_interrogator.json `
  --out-json tmp/goldilocks_interrogator_detective.json `
  --out-md tmp/goldilocks_interrogator_detective.md
```

## Exam Styles

- `general`: balanced retrieval/composition/counterexample checks.
- `detective`: clue chains, contradiction pressure, suspect-elimination style checks.
- `medical`: symptom/finding/diagnosis and contraindication reasoning pressure.

## Output Artifacts

JSON report includes:

- `fact_audit.coverage_score`
- `fact_audit.precision_score`
- `fact_audit.missed_facts[]`
- `fact_audit.bogus_facts[]`
- `exam.pass_rate`
- per-question deterministic results

Markdown report is a fast human read for triage.

## Recommended Workflow

1. Ingest text/story into KB (`kb_pipeline.py`).
2. Run `kb_interrogator.py` on source + resulting KB.
3. Promote repeated misses/bogus patterns into new scenario/rung tests.
4. Re-run interrogator and compare pass rate + fact audit deltas.

## Near-Term Trajectory

- Detective lane: long-form Sherlock-style chapter ingestion plus chained suspect/alibi exam packs.
- Medical lane: guideline/case-note ingestion plus contraindication and temporal progression exam packs.

The interrogator is meant to be the gate that tells us whether extraction quality is real or just looks plausible.
