# GIC English Input Pipeline

Status note, 2026-04-27: this is a legacy note. It is retained only to explain
the older English-first parser lane and why the project moved toward
`semantic_ir_v1`.

The current live utterance path is described here:

- [docs/CURRENT_UTTERANCE_PIPELINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_UTTERANCE_PIPELINE.md)

The current research direction is described here:

- [docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md)

## What This Document Replaces

The original version of this note described the old Governed Intent Compiler
lane:

```text
English utterance
  -> strict parser prompt
  -> Prolog-ish parse object
  -> Python repair/canonicalization
  -> deterministic validation/apply
  -> KB mutation, query, clarification, or block
```

That path proved the authority-boundary idea: model output was provisional, and
only deterministic runtime code could mutate the KB.

It also exposed the main weakness. Too much language understanding was drifting
into Python-side rescue logic:

- pronoun and coreference hints
- family-bundle expansion
- inverse possessive rewrites
- subject-prefixed predicate canonicalization
- correction-form special cases
- temporal narration patches
- medical ambiguity holds

Those guardrails were often useful, but the trend was bad. Each new language
edge risked becoming another hand-coded semantic patch.

## What Changed

The current architecture moved the main semantic burden upstream into a richer
Semantic IR workspace:

```text
utterance + recent context + domain profile + KB seed
  -> semantic_ir_v1 workspace proposal
  -> deterministic mapper/admission policy
  -> KB mutation, query, clarification, quarantine, or rejection
```

The current default local model for that path is:

```text
qwen/qwen3.6-35b-a3b
```

The current goal is not to make Python parse more English. The goal is to let a
stronger model build a better semantic workspace, then let deterministic code
decide what is safe to admit.

## Why Keep This Page

This page is useful only as a historical contrast:

- the old lane showed why the authority boundary matters;
- the old lane showed how quickly parser rescue code can become domain- and
  test-specific;
- the new lane keeps the authority boundary while replacing many English
  repairs with explicit Semantic IR fields, predicate contracts, domain profile
  context, and mapper diagnostics.

If you are trying to understand the project as it works now, start with
[docs/CURRENT_UTTERANCE_PIPELINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_UTTERANCE_PIPELINE.md),
not this file.
