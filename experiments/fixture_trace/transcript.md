# Fixture Trace: Black Lantern Maze

This companion transcript points at the contrast specimen currently embedded in
the viewer. Unlike the school roster run, this one includes non-answer model
decisions such as `clarify`, `mixed`, and `quarantine`.

Fixture:

- source: `datasets/story_worlds/black_lantern_maze/source.md`
- QA: `datasets/story_worlds/black_lantern_maze/qa.md`
- compile artifact: `../prethinker_tmp_archive/tmp_offload_20260504_001651/cold_baselines/black_lantern_maze/domain_bootstrap_file_20260503T055307250452Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `../prethinker_tmp_archive/tmp_offload_20260504_001651/cold_baselines/black_lantern_maze/domain_bootstrap_qa_20260503T060152766469Z_qa_qwen-qwen3-6-35b-a3b.json`
- trace viewer: `experiments/fixture_trace/index.html`

Run shape:

```text
source transcript sections: 18
source words: 2153
compile passes: 9
QA rows shown: 40 / 40
judge result: 27 exact / 7 partial / 6 miss
runtime load errors: 0
write proposal rows: 0
```

Decision contrast:

```text
q003  clarify   exact    Who are the two Lenas and what are their roles?
q007  clarify   partial  Should Orrin Hall be normalized to Oren or Orin?
q017  mixed     partial  What did ESO-7 authorize?
q018  mixed     exact    When did the safety hold begin and end?
q019  mixed     exact    Could full repair payment be released during the safety hold?
q022  quarantine miss    Was Pavi Chen cleared to disembark?
q039  mixed     exact    What does "Asha aprobo el paquete" mean in the file?
q040  clarify   exact    If the user asks "Was it late?", what should Prethinker do?
```

The important contrast row is `q040`: the model and projected decisions are
both `clarify`, and the judge marks that as exact because the correct behavior
is to ask what "it" refers to and which deadline/scope is meant.

To inspect the full source transcript, open the viewer and expand
`Source Transcript`, or open the source file listed above.
