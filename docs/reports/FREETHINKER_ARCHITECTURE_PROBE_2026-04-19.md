# Freethinker Architecture Probe (2026-04-19)

This note captures a quick local probe of whether Prethinker needs a bifurcated `Prethinker` / `Freethinker` architecture or whether a single larger-context `qwen3.5:9b` path can do the same work without extra hair.

## Question

Can one `qwen3.5:9b` with richer turn context and a suitable prompt do the clarification/disambiguation work cleanly enough, or does a split strict-compiler plus sidecar design earn its complexity?

## Method

Three styles were compared on a small ambiguity pack:

1. current canonical path
   - `process_utterance()` / no recent-turn sidecar
2. single-path context-enriched parser
   - same parser model
   - larger context
   - recent turns + active entities injected alongside the parser prompt
3. split-role prototype
   - same base model
   - separate Freethinker-style clarification prompt
   - Freethinker proposes a clarification answer or question
   - Prethinker recompiles using that answer

Raw artifacts:

- [tmp/freethinker_vs_singlepath_experiment_20260419.json](/D:/_PROJECTS/prethinker/tmp/freethinker_vs_singlepath_experiment_20260419.json)
- [tmp/singlepath_context_v2_20260419.json](/D:/_PROJECTS/prethinker/tmp/singlepath_context_v2_20260419.json)

## Cases

1. `unique_pronoun_scott`
   - prior: `Scott runs the bakery.`
   - current: `He lives in Salem.`
   - desired: resolve to `scott`

2. `unique_deictic_launch_plan`
   - prior: `The launch plan requires board approval.`
   - current: `It ships next week.`
   - desired: resolve to `launch_plan`

3. `ambiguous_he_scott_blake`
   - prior: `Scott met Blake yesterday.`
   - current: `He lives in Salem.`
   - desired: abstain / ask user

4. `ambiguous_she_selene_mara`
   - prior: `Selene emailed Mara about the lease.`
   - current: `She approved it.`
   - desired: abstain / ask user

## Findings

### 1. Current canonical path is conservative but context-starved

For all four cases, the current `Prethinker` path asked for clarification.

This is safe, but it means current console behavior is not exploiting recent-turn context for local discourse resolution.

### 2. Single-path parser + richer context did not improve meaningfully

Two variants were tried:

- mild context sidecar instructions
- stronger explicit reference-resolution instructions

Observed behavior:

- the parser still asked for clarification on all four cases
- in easy unique-reference cases, it still left `he` / `it` unresolved
- one stronger-context run even degraded argument order into `lives_in(salem, he).`

Interpretation:

- simply adding more context to the existing strict parser prompt is not enough
- the active parser prompt is strongly optimized for “ask when unsure,” not for contextual liaison work
- making a single-path design succeed would likely require retuning the main parser role itself

### 3. Split-role prototype did help on a uniquely grounded case

For `unique_pronoun_scott`:

- Freethinker proposed `Scott`
- recompilation produced `lives_in(scott, salem).`

This is a genuine win that the single-path parser did not achieve in the same probe.

### 4. Split-role prototype also overreached on an ambiguous case

For `ambiguous_he_scott_blake`:

- Freethinker incorrectly chose `Blake`
- recompilation then produced `lives_in(blake, salem).`

This is the clearest warning in the probe.

Interpretation:

- Freethinker can reduce unnecessary user clarification
- but a naïve auto-resolution policy is too risky for KB mutation

### 5. Freethinker is sensitive to the question it receives

For `unique_deictic_launch_plan`, Freethinker behaved differently depending on the wording of the clarification question.

- when biased by Prethinker’s original question about “the shipment,” it asked the user
- when asked a generic referent question, it tried to resolve

Interpretation:

- if Freethinker is used, it should not be overbound to a poor draft clarification question
- it needs access to the ambiguity packet and context sidecar, not just the literal question text

## Conclusion

The probe does **not** support “just give the current parser more context and everything gets better.”

In this small sample, the single-path richer-context parser:

- did not resolve the easy unique-reference cases
- stayed conservative
- and even degraded one output shape

The probe **does** support the idea that a separate contextual role can add useful capability.

However, it also shows that unrestricted Freethinker auto-resolution would be unsafe.

## Recommendation

The least-hairy next move is:

1. keep the current strict compiler path intact
2. use Freethinker first in `advisory_only` mode
3. let Freethinker improve clarification wording before allowing any auto-resolution
4. if auto-resolution is added later, restrict it to a very narrow `grounded_reference` policy

Practical implication:

- Freethinker has earned continued exploration
- but only as a bounded sidecar, not as a free write-unblocking agent
- and not yet as a replacement for the current parser path

## Working Read

If we want one-model simplicity, the best version is probably still:

- one base `qwen3.5:9b`
- two roles
- two prompts
- two authority levels

That is still architecturally split, even if the weights are the same.
