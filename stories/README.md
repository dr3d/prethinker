# Story Packs

These files are retained as source material for Semantic IR frontier tests.
They should be exercised through the current router/Semantic IR/mapper
harnesses, not through the retired story-runner/golden-KB parser lane.

Suggested naming:

- story file: `stories/<story_id>.md`
- scenario: `kb_scenarios/<story_id>.json`
- frontier case: prefer `datasets/story_worlds/` or a focused probe under
  `experiments/`
- trace/report output: `tmp/semantic_ir_*` or `tmp/semantic_ir_trace_views`

Workflow:

1. Keep the raw story text as human-readable pressure material.
2. Add or update focused frontier cases that preserve the hard semantic edges.
3. Run the router/Semantic IR harnesses against those cases.
4. Promote only tests that expose soft edges: ambiguity, claim-vs-fact,
   temporal order, source fidelity, predicate drift, or unsafe admission.
