# Dataset Transfer Worksheet

Last updated: 2026-05-13

This worksheet tracks external-dataset transfer work. It is separate from
`BOUNDARY_HUNT_WORKSHEET.md` because the hunt worksheet is now the architecture
case archive; this file is the intake and transfer-pressure board.

## Doctrine

- External datasets are measurement pressure, not permission to tune on their
  surface vocabulary.
- Sample into `tmp/` by default. Do not bulk-store upstream datasets in the
  repo.
- Preserve answer isolation: source and questions can compile; oracle answers
  are scoring-only.
- A transfer failure becomes architecture only after it is described without
  dataset names, row ids, answer strings, local people, or local organizations.
- Prefer small, focused samples that isolate one pressure over large runs that
  only produce unlabeled residue.

## Intake Tooling

`scripts/sample_mrc_transfer_fixtures.py` samples RACE-style machine reading
comprehension records into Prethinker incoming fixture shape:

```powershell
python scripts/sample_mrc_transfer_fixtures.py --dataset ehovy/race --config high --split validation --limit 5
```

Output defaults to `tmp/mrc_transfer_samples`. Each sampled passage has:

- `source.md` with passage text and source metadata;
- `qa.md` with questions and multiple-choice options only;
- `oracle.jsonl` with the answer key for after-the-fact scoring;
- `fixture_notes.md` with transfer/doctrine reminders.

The repo also has a local `datasets/` directory, so the sampler explicitly
guards against importing that namespace when it needs HuggingFace's
`load_dataset`.

## Candidate Lanes

| Lane | Purpose | First Sample |
| --- | --- | --- |
| RACE | Within-English school-style comprehension transfer; closest known match to current fixture shape. | 50-100 passages after a 5-passage smoke test. |
| CUAD | Legal contract transfer; tests domain shift and section/authority assumptions. | 10-20 documents once a CUAD adapter exists. |
| DROP | Arithmetic and discrete-operation stress; likely to pressure recent aggregation/counterfactual repairs. | Small sample after RACE smoke. |
| MultiWikiQA / Belebele | Non-English surface-risk pressure. | 5-10 samples per language after adapter shape is settled. |

## Progress Journal

### DT-001 - RACE-Style Intake Sampler

Before:

- Prethinker had a staging path for incoming fixtures, but no small,
  repeatable way to sample standard external MRC datasets into that shape.
- The natural HuggingFace import path was ambiguous because the repo has a
  local `datasets/` directory.

Prediction:

- A narrow adapter can create clean transfer fixtures without adding new
  architecture or committing upstream dataset content.
- The first adapter should preserve the existing `qa.md + oracle.jsonl`
  isolation contract so later transfer runs use the same staging discipline as
  hand-authored fixtures.

Intervention:

- Added `scripts/sample_mrc_transfer_fixtures.py`.
- Added unit coverage for answer-key isolation and compatibility with
  `stage_incoming_fixtures.py`.

After:

- RACE-style records can be sampled from HuggingFace or local JSONL into
  `tmp/mrc_transfer_samples`.
- The generated fixtures can be staged by the existing intake script.
- A one-passage live RACE smoke sample from HuggingFace staged cleanly.

Artifacts:

- `scripts/sample_mrc_transfer_fixtures.py`
- `tests/test_sample_mrc_transfer_fixtures.py`
- Smoke sample:
  `tmp\mrc_transfer_samples_race_smoke\race_high_validation_00000_high5060_txt`

Verification:

- `python -m pytest tests/test_sample_mrc_transfer_fixtures.py tests/test_stage_incoming_fixtures.py -q`
  -> `7 passed`.
- `python scripts\sample_mrc_transfer_fixtures.py --dataset ehovy/race --config high --split validation --limit 1 --out-root tmp\mrc_transfer_samples_race_smoke`
  -> wrote `1` fixture.
- `python scripts\stage_incoming_fixtures.py --root tmp\mrc_transfer_samples_race_smoke --out-root tmp\mrc_transfer_staged_race_smoke`
  -> `1` staged, `0` failed.

Lesson:

- Transfer intake is its own boundary surface. The adapter should translate
  external dataset format into fixture shape, but must not translate dataset
  vocabulary into compiler or selector logic.

Next pressure:

- Run a 5-passage RACE sample as the first external transfer compile/QA
  candidate, then classify misses as transfer coordinates rather than tuning
  instructions.

### DT-002 - RACE Five-Passage Transfer Smoke

Before:

- The lab had strong internal and focused-probe evidence, but no fresh
  external MRC measurement in the current fixture shape.
- OpenRouter was expected to be the faster hosted lane, but prior wide runs
  showed provider throttling above six lanes.

Prediction:

- A tiny unseen RACE sample should expose whether the current architecture
  transfers to school-style comprehension prose without adding helpers or
  fixture vocabulary.
- Because RACE asks title/theme/false-option questions, some misses should be
  answer-surface or resolution gaps rather than ordinary selector failures.

Intervention:

- Sampled five RACE high-school validation passages into
  `tmp\mrc_transfer_samples_race5`.
- Staged them into `tmp\mrc_transfer_staged_race5`.
- Tried OpenRouter at five lanes and then one lane; both runs failed with
  provider `503`, so those were recorded as transport, not architecture.
- Ran local compile and QA using the same staged fixtures.

After:

- Staging: `5` fixtures staged, `0` failed.
- Compile: `5` fixtures compiled, `0` runner errors.
- QA: `15` questions, `7 exact / 2 partial / 6 miss`, exact rate `0.4667`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.
- Helper rows: `0`.

Artifacts:

- Samples: `tmp\mrc_transfer_samples_race5`
- Staged fixtures: `tmp\mrc_transfer_staged_race5`
- Failed OpenRouter compile attempts:
  `tmp\mrc_transfer_compile_race5_20260513`,
  `tmp\mrc_transfer_compile_race5_retry1_20260513`
- Local compile: `tmp\mrc_transfer_compile_race5_local_20260513`
- Local QA: `tmp\mrc_transfer_qa_race5_local_20260513`

Verification:

- `python scripts\stage_incoming_fixtures.py --root tmp\mrc_transfer_samples_race5 --out-root tmp\mrc_transfer_staged_race5`
  -> `5` staged, `0` failed.
- `python scripts\run_domain_bootstrap_file_batch.py ... --summarize-existing`
  -> all `5` local compile artifacts parsed.
- `python scripts\run_domain_bootstrap_qa_batch.py ... --lanes 2`
  -> `15` questions, `7 / 2 / 6`.

Boundary coordinates:

- Formula application over an extracted rule: the source compiled a general
  numeric rule and one stated instance, but the QA layer did not resolve a new
  instance of that rule.
- Title/theme generation: the KB held supporting facts for a passage theme,
  but no surface mapped those facts to a title-like answer.
- False-option selection: the KB contained evidence refuting an option, but the
  QA layer treated the reference answer as content to support rather than the
  selected false statement.
- Comparative timeline resolution: one side of a comparison was compiled while
  the other side was missing or not queryable.
- Background/role fact absence: answer-bearing educational or audience role
  distinctions were not emitted as queryable coordinates.
- Implicit consequence/attitude: source evidence supported a stance, but not
  the answer's psychological consequence phrasing.

Lesson:

- RACE is a good unlike fixture family because it pressures more than factual
  lookup. It reveals a boundary between symbolic fact extraction and
  exam-style answer selection: title synthesis, option negation, rule
  application, and implicit audience/theme inference. Those are transfer
  coordinates, not permissions to tune on RACE wording.

Next pressure:

- Build a tiny focused probe for one transfer coordinate at a time, starting
  with false-option selection or rule-application over an extracted formula.
- Keep title/theme generation separate; it may be a deliberate out-of-scope
  answer-rendering class rather than a compiler repair.
