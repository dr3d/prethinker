# Causal-Chain End-State Ladder

This probe tests whether QA can answer end-state questions when the source
separates an upstream cause from an immediate ending event.

The key distinction:

- direct end-state question: answer the event that directly ended the state
- upstream-cause question: answer the event that caused the ending event
- mixed context: preserve both instead of collapsing them

No fixture names or dataset topics are used. A repair should only target a
generic join between cause/lead-to rows and end-state rows.
