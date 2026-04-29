# Story Packs

These files are retained as source material for Semantic IR frontier tests.
They should be exercised through the current Lava/router/mapper harnesses, not
through the retired story-runner/golden-KB parser lane.

Suggested naming:

- story file: `stories/<story_id>.md`
- scenario: `kb_scenarios/<story_id>.json`
- frontier case: `docs/data/frontier_packs/*.json`
- trace/report output: `tmp/semantic_ir_*` or `tmp/semantic_ir_trace_views`

Workflow:

1. Keep the raw story text as human-readable pressure material.
2. Add or update focused frontier cases that preserve the hard semantic edges.
3. Run the Lava/router/Semantic IR harnesses against those cases.
4. Promote only tests that expose soft edges: ambiguity, claim-vs-fact,
   temporal order, source fidelity, predicate drift, or unsafe admission.
