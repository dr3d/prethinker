# Policy Reimbursement Demo

Last updated: 2026-04-27

This is the current focused "talk your rules into existence" demo.

It tests whether Prethinker can:

1. Turn a plain-English reimbursement policy into executable Prolog rules.
2. Ingest later concrete reimbursement events as facts.
3. Ask which events violate the policy.
4. Apply an explicit correction and change the derived answer.
5. Keep derived violations out of durable KB facts.

The important claim is not that Python knows reimbursement English. The profile
context gives the Semantic IR model a small predicate palette and a few rule
shape examples. The model proposes rules/facts/queries, the mapper admits only
safe operations, and the Prolog runtime derives answers.

## Run It

```powershell
python scripts/run_policy_reimbursement_demo.py --backend lmstudio --base-url http://127.0.0.1:1234 --model qwen/qwen3.6-35b-a3b --timeout 600 --include-model-input
```

Local artifacts are written under ignored `tmp/policy_reimbursement_demo/`.

The runner also refreshes:

```text
tmp/policy_reimbursement_demo/policy_reimbursement_demo_latest.html
```

## Current Best Local Result

Latest local run with `qwen/qwen3.6-35b-a3b` through LM Studio structured
output:

- Turns: `4`
- Parsed OK: `4/4`
- Apply error free: `4/4`
- Expected query matches: `4/4`
- No derived violation write leak: `4/4`
- Rough score: `1.000`

The successful turn sequence:

1. Policy setup admits four executable rules:
   - `self_approval(R) :- requested_by(R, P), approved_by(R, P).`
   - `manager_conflict_approval(R) :- requested_by(R, Requester), approved_by(R, Approver), manages(Approver, Requester).`
   - `violation(R, reimbursement_policy) :- self_approval(R).`
   - `violation(R, reimbursement_policy) :- manager_conflict_approval(R).`
2. February event ingestion admits direct facts for `r1`, `r2`, and `r3`.
3. The runtime query `violation(R, reimbursement_policy).` returns `r1` and
   `r2`.
4. The correction "R2 was approved by Omar, not Lena" retracts the old approval,
   asserts the new one, and the same query now returns only `r1`.

## What This Proves

This is a small but concrete demonstration of the current direction:

```text
plain English policy
  -> Semantic IR executable rule proposal
  -> deterministic admission
  -> Prolog rule storage
  -> later facts
  -> derived query answer
```

The derived answer is not committed as a fact. It remains an answer produced by
runtime reasoning over admitted rules and facts.

## A Useful Failure We Fixed

The first live pass exposed a structural mapper bug. The model emitted
`operation="rule"` with variable-like args such as `R`, but without an
executable `clause`. The mapper was previously willing to demote some
no-clause rule records into fact-like records; in this case that created bad
facts such as:

```prolog
violation(r, reimbursement_policy).
```

The mapper now blocks variable-like rule stubs unless an executable clause is
present. Ground rule records may still be demoted into fact-like records when
that is the intended profile shape, but variable-bearing rules must provide a
real clause.

## Next Pressure

The demo is intentionally narrow. The next useful pressure is not more
reimbursement-specific code. It is broader policy language:

- exception ladders
- threshold policies
- scoped dates and expiration windows
- "unless" and "only if" language
- policy conflicts and overrides
- explanations that cite which rule path fired
