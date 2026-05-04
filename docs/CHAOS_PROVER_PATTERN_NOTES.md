# Chaos-Prover Pattern Notes

Date: 2026-05-04

Source inspected:

- `https://github.com/MyceliaCognition/chaos-prover`
- `https://github.com/MyceliaCognition/chaos-prover/blob/main/demo/demo_orchestrator.py`
- `https://github.com/MyceliaCognition/chaos-prover/tree/main/telemetry`

## Assessment

Do not integrate code directly. The public repository is useful as a pattern
catalog for harness design, not as a drop-in prover or selector.

The README describes a Lean 4 neuro-symbolic proof loop: neural tactic
generation proposes candidates, Lean deterministically verifies them, and only
compiler-accepted proofs count. The repository includes Lean fixtures,
telemetry, and a stripped demo orchestrator, while the adaptive search
algorithm, model weights, prompt engineering, combination synthesis, and full
MCP orchestration are explicitly not public.

## Useful Pattern

The reusable idea is:

```text
candidate -> isolated verifier -> telemetry -> risk gate -> patch/apply
```

For Prethinker, this maps to:

- compile/query/rule candidates as proposal-only artifacts;
- isolated Prolog or helper verifier runs before promotion;
- telemetry for attempts, novelty, cycles, failed candidate classes, verifier
  output, and accepted rule or selected mode;
- risk gates that block broad promotion when candidate families regress exact
  rows or repeat low-novelty failures.

## Concrete Borrowing

Borrow vocabulary and harness shape, not implementation:

- `attempts`, `winning_strategy`, `failed_tactics`, `strategies_explored`,
  `max_attempts`, and timeout/cycle thresholds are useful names for Prethinker
  run telemetry.
- The proof fixture pattern suggests a Prethinker rule-composition pattern:
  candidate transform plus deterministic closer, rather than monolithic
  free-form rule output.
- The generalization tests suggest keeping small mixed-domain cold suites that
  are intentionally unlike the development fixture.
- Failed tactic telemetry is a good model for zombie detection: repeated
  prefixes, malformed structured output, prose in code/proof slots, and
  repeated partial progress with low novelty.

## Mismatch

The repo is Lean-centric and axiomatized; it is not a Prolog architecture.
Because the real adaptive search engine is not included, there is no useful code
path to vendor. The useful takeaway is instrumentation discipline: let the
symbolic verifier decide acceptance, record every failed candidate class, and
make promotion conditional on telemetry rather than model confidence.
