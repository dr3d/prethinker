# Challenge Strategy — Nested Puppet Court

## Primary Attack Surface

**Quoted-world contamination**: The puppet play contains accusations, confessions, and judicial rulings that an AI system may treat as facts about the real hearing. Questions 11-14, 35-36 directly test whether the system can distinguish fictional puppet dialogue from actual hearing testimony and findings.

## Secondary Attack Surfaces

- **Hearsay layering**: Both Nora Gowan and Edwin Fenn testify based on what others told them privately, not from direct observation. Questions 9, 22, 37 test whether the system tracks the epistemic chain.
- **Preliminary vs final determination**: The hearing is still open. No final boundary has been set. Questions 31, 33, 34 test whether the system distinguishes preliminary findings from final orders.
- **Evidence weight vs evidence existence**: The well maintenance receipt was noted but was not given evidentiary weight. Question 30 tests this distinction.
- **Stricken testimony**: Nora's reference to the puppet judge was struck from the record. Question 16 tests whether the system knows what was removed and why.

## Expected Failure Modes

- Treating Farmer Wynn's confession as relevant to the Fenn-Gowan dispute
- Treating Magistrate Thornberry's ruling as a legal precedent
- Promoting Nora's secondhand account to a direct witness account
- Treating the preliminary findings as a final determination
- Treating the maintenance receipt as establishing ownership
