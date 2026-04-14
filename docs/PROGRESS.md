# Deterministic English->Logic Compilation: Progress Note

Date: 2026-04-14

This cycle produced a real scientific result, even if it is not yet a clean victory. The latest local evidence says the project is getting better at compiling messy English narrative into a bounded logical ontology under deterministic gates, and it says that because the same 50-turn Goldilocks story now yields a much larger and less degenerate KB than it did a few hours earlier on the same model family. It also says we are still far from solved: some of the remaining failures are exactly the kinds of failures that matter if the claim is "English to logic" rather than "English to vaguely related symbols."

The framing here comes from the repo itself. The main README describes Prethinker as a neuro-symbolic workbench rather than a finished parser, and the wild-mode note explicitly treats real-language ingestion as the anti-overfitting lane rather than a demo lane. See [D:\_PROJECTS\prethinker\README.md](D:\_PROJECTS\prethinker\README.md) and [D:\_PROJECTS\prethinker\docs\WILD_MODE.md](D:\_PROJECTS\prethinker\docs\WILD_MODE.md).

## What changed scientifically in this cycle

The clearest evidence is a same-story comparison on `story_goldilocks_roundtrip.json`.

At `2026-04-14T13:21:51Z`, run `run-20260414T132151Z-story_goldilocks_roundtr-qwen3_5_9b-33896` wrote a badly compressed ontology from the story. It finished with `20` apply failures, `20` clarification requests, only `21` clauses, only `7` predicate signatures, and `17` route decisions of `other`. The artifact is [D:\_PROJECTS\prethinker\tmp\goldilocks_roundtrip_run_latest_qwen_ce.json](D:\_PROJECTS\prethinker\tmp\goldilocks_roundtrip_run_latest_qwen_ce.json).

At `2026-04-14T15:19:09Z`, run `run-20260414T151909Z-story_goldilocks_roundtr-qwen3_5_9b-21788` materially changed that picture. It still failed overall, but it dropped to `5` apply failures and `4` clarification requests, while expanding to `43` clauses and `21` predicate signatures, with `0` `route=other` turns. The artifacts are [D:\_PROJECTS\prethinker\tmp\goldilocks_roundtrip_run_guarded_v10.json](D:\_PROJECTS\prethinker\tmp\goldilocks_roundtrip_run_guarded_v10.json) and the promoted copy [D:\_PROJECTS\prethinker\docs\data\roundtrip\goldilocks_roundtrip_run.json](D:\_PROJECTS\prethinker\docs\data\roundtrip\goldilocks_roundtrip_run.json).

The relevant change was not "the model got smarter." The local evidence points to stronger deterministic gating and canonicalization in [D:\_PROJECTS\prethinker\kb_pipeline.py:2616](D:\_PROJECTS\prethinker\kb_pipeline.py:2616), [D:\_PROJECTS\prethinker\kb_pipeline.py:3179](D:\_PROJECTS\prethinker\kb_pipeline.py:3179), [D:\_PROJECTS\prethinker\kb_pipeline.py:3885](D:\_PROJECTS\prethinker\kb_pipeline.py:3885), [D:\_PROJECTS\prethinker\kb_pipeline.py:3971](D:\_PROJECTS\prethinker\kb_pipeline.py:3971), and [D:\_PROJECTS\prethinker\kb_pipeline.py:4159](D:\_PROJECTS\prethinker\kb_pipeline.py:4159):

- arrow-edge retract fallback normalizes `x->y edge` into `parent(x,y)`
- explicit exclusion/protection patterns catch `not x->y` and `x->y stays`
- `leading_subject_anchor_guard` repairs actor-argument drift
- `observed_asleep_event_guard` rewrites some narrative observations into a more stable `saw/2` form

That said, this is not a pure ablation. The guarded run changed several things at once: strict registry was turned on, a Goldilocks-specific predicate registry and type schema were added, clarification eagerness dropped from `0.55` to `0.2`, and max clarification rounds dropped from `3` to `1`. So the current evidence supports a combined-system claim, not an isolated-causality claim.

## Quantified wins

| Run | UTC start | Path | Apply failures | Clarification requests | Commit count | Clause count | Predicate signatures | `route=other` |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Unguarded Qwen+CE | 2026-04-14T13:21:51Z | `D:\_PROJECTS\prethinker\tmp\goldilocks_roundtrip_run_latest_qwen_ce.json` | 20 | 20 | 19 | 21 | 7 | 17 |
| Guarded v10 | 2026-04-14T15:19:09Z | `D:\_PROJECTS\prethinker\tmp\goldilocks_roundtrip_run_guarded_v10.json` | 5 | 4 | 39 | 43 | 21 | 0 |
| Published roundtrip copy | 2026-04-14T15:19:09Z | `D:\_PROJECTS\prethinker\docs\data\roundtrip\goldilocks_roundtrip_run.json` | 5 | 4 | 39 | 43 | 21 | 0 |

Exact run IDs:

- `run-20260414T132151Z-story_goldilocks_roundtr-qwen3_5_9b-33896`
- `run-20260414T151909Z-story_goldilocks_roundtr-qwen3_5_9b-21788`

The biggest empirical gains were simple and important:

- apply failures fell `20 -> 5`
- clarification requests fell `20 -> 4`
- committed turns rose `19 -> 39`
- clause count rose `21 -> 43`
- predicate coverage rose `7 -> 21`
- route drift to `other` fell `17 -> 0`

The ontology difference is not cosmetic. The weak run mostly collapsed the story into a tiny, noisy predicate set such as `goldilocks/1`, `has_big_chair/1`, `has_big_chair/2`, `has_small_bowl/2`, `saw/2`, and `tasted/2`. The guarded run recovered a much more story-shaped ontology, including `has_porridge/2`, `chairs_in_house/1`, `has_bed/2`, `sat_in/2`, `slept_in/2`, `ran_out_of/2`, `walked_through_forest/1`, `goldilocks_found/2`, and the size/fit predicates.

## Why these wins matter for English->logic compilation science

The central question here is not whether an LLM can emit some Prolog-like text. The question is whether a deterministic gate can force free-form English into a stable logical state space without constant human rescue.

This cycle gives a qualified yes on three fronts.

First, routing got much less brittle. In the weaker run, obvious narrative assertions were often routed as `other`, even when the downstream parse still tried to assert facts. That is a direct sign that the classifier and compiler were not aligned. In the guarded run, all 50 turns routed as `assert_fact`, which is not proof of correctness, but it is evidence that the gate is reducing classifier/compiler disagreement instead of amplifying it.

Second, the gate is now doing real canonicalization work. In the weaker run, "Goldilocks ran out of the house" became `goldilocks(ran_out_of_house).`, which is logically malformed in the important sense: it encodes an event as a unary fact on the entity rather than as a relation with explicit roles. In the guarded run, the same story yields `ran_out_of(goldilocks, house).` and also recovers `walked_through_forest(goldilocks).` for the final escape turn. That is closer to actual compilation than mere token shuffling.

Third, the guarded system is preserving more semantic distinctions instead of collapsing them into duplicates. The earlier run repeatedly reduced specific possessions and locations into generic atoms, which then got skipped as already present. A compiler that cannot keep `Mama Bear` and `Baby Bear` apart is not really compiling English narrative. The guarded run is still imperfect, but the jump from `7` to `21` predicate signatures suggests the deterministic constraints are starting to protect ontology shape against that collapse.

## Known failure modes still present

The wins are real, but the remaining failures are also real.

- Turn 5 of the guarded run still dies before compilation: "There were three bowls of porridge on the table." produced `Model did not return parseable JSON payload.` That is a plain compiler failure, not a subtle semantic miss.
- The guarded run still fails on nested event observations. For example, "Papa Bear saw that someone had tasted his porridge." compiles to `saw(papa_bear, tasted(someone, porridge_of(papa_bear))).` and then stalls in clarification because strict type expectations for `saw/2` do not like an event term in object position.
- The system still compresses plural or grouped entities too aggressively. "Goldilocks woke up and saw the three bears." becomes `saw(goldilocks, bear).` That is not nonsense, but it is a lossy abstraction of a semantically important count distinction.
- Some collisions are now hidden behind `skipped` instead of being fully solved. In the guarded run, `tasted(goldilocks, porridge).`, `sat_in(goldilocks, chair).`, and `slept_in(goldilocks, bed).` are still broad enough to merge distinct story events.
- The current roundtrip artifacts have `validation_total=0`. So these files show turn-level compilation behavior and ontology growth, but they do not yet prove that the final KB is correct against a strict end-state contract.
- Both current Goldilocks artifacts still end with `overall_status=failed`. The right scientific interpretation is "substantial movement under stress," not "problem solved."

## Next scientific bets

The next useful experiments are narrow and falsifiable.

- Run a real ablation matrix on the same story and seed: guard code only, registry only, type schema only, low-CE only, then all combined. Right now the evidence says the bundle works, but it does not say which component carries most of the gain.
- Split `saw/2` event-observation handling into two representations and compare failure rates: one arm with event reification such as `observed_event(papa_bear, E)`, one arm with explicit predicates like `noticed_tasted(papa_bear, someone, porridge_of(papa_bear))`.
- Add strict end-state validations to the roundtrip track. Until the run files contain validation rows, ontology growth can be measured but semantic fidelity cannot be claimed with enough rigor.
- Measure argument-role preservation directly. A small audit can score whether subject/object direction is retained after guards fire, especially on narrative observation sentences and possession phrases.
- Add plurality/count tests as first-class rungs. The current `bear` collapse suggests the compiler still lacks a principled way to represent collectives without either hallucinating identities or erasing multiplicity.
- Test whether duplicate-skips are masking over-broad predicates. If two different utterances compile to the same clause and the second is skipped, the metric should mark that as a semantic collision, not as quiet success.

## A short, honest bottom line

The local evidence says deterministic gates are now doing more than cleaning up syntax. They are materially changing what English survives into logic. On 2026-04-14, the Goldilocks roundtrip moved from a thin, drift-prone ontology with 20 stalled turns to a much denser 43-clause state with 39 commits and zero route drift to `other`.

That is meaningful progress.

It is also not the same thing as robust English->logic compilation. The remaining failures are exactly where the science gets hard: plural reference, nested event semantics, type-safe observation, and proof that the final KB is right rather than merely larger. That is a good place for the project to be, because the problem has become specific enough to study instead of vague enough to hand-wave.
