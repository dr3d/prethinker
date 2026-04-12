# Prethinker Explainer (X Article Draft)

This file is the public narrative draft for sharing Prethinker progress and design decisions.

## Latest Discoveries In Linguistic Parsing Science (As Observed In This Project)

The main discovery is that most real parser failures do not look like ignorance. They look like near-correctness. The model often understands the sentence well enough to sound right, but still chooses the wrong write target, flips an argument order, packs multiple operations into one blob, or treats a repair as commentary instead of an executable retract. That is the dangerous zone.

We have seen several concrete failure modes repeatedly.

First, English surface form is a bad predictor of argument order. Possessive, passive, and inversion forms all create false confidence. "A is B's parent," "A has B as a parent," and "A is parented by B" are close in wording and very different in Prolog direction. Early runs passed easy declaratives and still failed on these alternations.

Second, compound utterances are not just longer utterances. They are a different parsing problem. The model can semantically understand "assert this, retract that, and tell me whether the lineage still holds" while still serializing the whole turn as one malformed logic string. A large part of the hard-rung work was learning that multi-clause language must be unpacked explicitly, not merely "understood."

Third, natural-language retracts are unusually under-specified. People do not say `retract(parent(x,y))`. They say "undo that," "not that branch," "keep this edge," "swap the middle one," or "I tagged the wrong sibling." We learned that correction language needs its own normalization layer. Without that layer, the system either misses the retract or removes the wrong edge.

Fourth, exclusion language is a silent killer. Turns containing "not," "stays," or "keep" can look like ordinary retracts while actually specifying what must remain untouched. This project hit that exact bug class and had to add explicit handling so a repair turn could exclude preserved branches rather than wipe them out.

Fifth, clarification can hurt accuracy if asked at the wrong time. The lesson from the CE sweeps was not simply "ask more" or "ask less." It was that clarification helps when referents or write targets are genuinely unresolved, and hurts when the parse is already deterministic. Good clarification policy is selective friction.

Sixth, story-width frontier runs showed that failures move as the system improves. Early failures were basic routing and schema shape. Later failures were timing, correction semantics, branch preservation, and long-turn consistency. That is a healthier class of problem, but it is still a hard problem.

The honest takeaway is that linguistic parsing at high accuracy is less about broad semantic vibes and more about controlling narrow failure channels: argument direction, clause unpacking, retract targeting, pronoun carryover, and confidence illusion.

## Precise Mechanisms Of GIC Design And How High Accuracy Is Achieved

Prethinker is built as a Governed Intent Compiler, or GIC. Natural language is treated as source text that may propose writes, queries, or repairs, but proposal is not authority.

The architecture runs on two different memories because they solve different problems.

The first memory is the deterministic KB. This is the sharp memory. It lives in retained named Prolog corpora, supports exact queries, preserves provenance, and is the only memory allowed to count as state authority.

The second memory is the served LLM context. This is the mushy memory. It is useful for resolving phrasing, pronouns, likely referents, and clarification candidates, but it is probabilistic and non-authoritative by design. It can help interpret language. It cannot define truth.

That split is the core accuracy mechanism. We do not ask the LLM to both interpret and own the world state. We ask it to propose, then force the proposal through deterministic checks, normalization, and apply policy.

The MITM role is the control-plane interception point. Prethinker sits between the human utterance and any durable state mutation. Every turn is intercepted before write execution. The interceptor classifies the turn, normalizes it into one of the governed intents, decides whether the turn is safe enough to apply, and only then allows the runtime to assert, retract, or query. Without that MITM layer, wrong writes become conversationally plausible and operationally invisible.

Accuracy is also achieved by using two clarification paths, not one.

One path is direct user clarification. This is the highest-trust disambiguation source because the human owns the intended meaning. If a write target is ambiguous, user clarification can resolve the referent and authorize the mutation.

The other path is served-LLM clarification. In current runs this can be a separate model, often `gpt-oss:20b`, grounded with recent accepted turns plus a deterministic KB snapshot and bounded by confidence thresholds. Its job is to answer advisory clarification prompts when we want a synthetic clarification loop during evaluation or semi-automated operation.

Those two paths are intentionally asymmetric. The served LLM is advisory. The user is authoritative.

That trust boundary is non-negotiable. A served LLM answer can suggest a likely interpretation, but it does not manufacture certainty. Final commit authority for uncertain writes must come from deterministic KB disambiguation or explicit user confirmation. The MCP server and pipeline both reflect that same rule: writes can be blocked until confirmation, and clarification answers are recorded as inputs to governance, not as autonomous commit rights.

The robotic clarification voice is also intentional. It is not unfinished product design. It is an interface safety choice. The clarification text is brief, narrow, and almost mechanical because social fluency can disguise uncertainty. The system should sound like an instrument when it is asking for write authority. If a warmer conversational layer is wanted later, it can sit on top of this. The canonical control plane should remain plain.

## How Prethinker Was Built And Tuned

The project was built with a ladder method because single benchmark scores hide too much. We moved upward and wider at the same time.

Moving upward means increasing logical difficulty: facts, then rules, then transitive chains, then retractions, branch repair, exclusion language, story revisions, and multi-round clarification pressure.

Moving wider means holding the logical target fixed while making the English worse: paraphrase, passive voice, inversion, pronouns, typos, hedging, missing punctuation, mixed ingest/query turns, and repair language that sounds natural instead of formal.

That ladder design matters because many systems pass the clean lane and fail the width lane. In this repo, the frontier now reaches clean-root sweeps through `rung_200`, validated follow-up checks on `rung_210` and `rung_220`, and story plus CE frontier passes through `rung_360`. Just as important, the run logs show the misses that happened before those passes. The history is part of the method.

Tuning was not only prompt work. It was orchestration work. `kb_pipeline.py` now layers route selection, split extraction, schema and Prolog validation, optional repair, policy gating, deterministic runtime apply, and post-run validation. Many accuracy gains came from guardrails around the model, not from the model alone.

The development workflow also uses parallel agents for throughput and containment. Codex and agent54 work as separate operators with explicit file ownership and disjoint write sets. That lowers merge risk, keeps experiments auditable, and lets one agent extend scenarios or documentation while another hardens runtime behavior or evaluates frontier runs. In practice this is less about novelty than about keeping iteration speed high without corrupting the repo state.

The runtime and cost profile shape the tuning strategy. Real run campaigns here are not toy loops. Frontier sweeps, clarification cadence checks, story-width passes, and reruns after a guardrail change can consume multi-hour blocks on an RTX 5090. The binding constraint is usually wall-clock, GPU occupancy, and human attention for reading the failures, not merely the ability to launch another run. That pushes the project toward asymptotic improvement: smaller gains, better instrumentation, stricter scenario design, and more selective reruns instead of brute-force optimism.

This is why provenance, run retention, and curated evidence matter so much in this repo. When cycles are expensive, forgetting what changed is one of the most costly bugs.

## What This Means Now

Prethinker is no longer just a prompt experiment. It is a governed architecture for turning noisy language into deterministic state updates under explicit trust rules.

What it means now is simple.

The system is good enough to demonstrate real control-plane discipline, real frontier progress, and honest evidence of where it still breaks. It is not claiming universal semantic parsing. It is claiming that if memory matters, the right architecture is one where the model does not get to write alone.

![Pre-thinker Control Plane](docs/assets/prethinker-control-plane-infographic-v2.png)
