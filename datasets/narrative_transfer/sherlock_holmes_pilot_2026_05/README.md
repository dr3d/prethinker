# Sherlock Holmes Thermometer Pilot 2026-05

This is a one-document narrative-fiction transfer test for Prethinker. It lives
under `datasets/narrative_transfer` because it is a narrative reasoning probe,
not real-world transfer evidence. It pressures audit grammar on fiction, where
there is no external ground truth and internal textual consistency is the only
answer authority.

The pilot contains one document and 25 QA items drawn from Arthur Conan Doyle's "The Red-Headed League" in *The Adventures of Sherlock Holmes*.

## Why This Story

"The Red-Headed League" is linear, deterministic, and deduction-forward. It contains explicit testimony, aliases, stated rules, a revealed causal mechanism, and a first-person narrator whose knowledge is bounded by observation and later explanation. That makes it a useful first fiction thermometer before trying harder literary structures.

Expected transfer ceiling for this pilot is 60-70% exact, per pre-test
consultation. This expected ceiling is not a target score; it is a reminder
that prose fiction applies different pressure than regulatory or investigative
documents. Because this is a famous public-domain story, scores should not be
treated as clean unseen evidence.

## What It Tests

- Direct narrative fact extraction from prose and dialogue
- Timeline reconstruction across embedded testimony and later action
- Actor/action attribution when characters use aliases
- Causal-chain recovery from Holmes's retrospective explanation
- Stated-rule handling inside a fictional employment scheme
- Counting and quantity handling without external verification
- Source limitation awareness for first-person narration

## What It Does Not Test

This pilot intentionally does not test symbolism, unreliable narration, non-linear structure, or high-subtext interpretation. Those are out of scope by design.

## Question Categories

| Category | Count |
| --- | ---: |
| direct_lookup | 5 |
| timeline | 4 |
| actor_action | 3 |
| causal_chain | 3 |
| policy_rule | 2 |
| count_table | 2 |
| contradiction | 2 |
| unresolved_issue | 1 |
| as_of_date | 1 |
| source_limitation | 2 |

## Data Discipline

No invented story content was added. `source_original.txt` and `source.md` are extracted from the Project Gutenberg HTML edition of *The Adventures of Sherlock Holmes*, limited to Adventure II, "The Red-Headed League." Oracle answers are grounded only in the story text and refer to in-text source spans, not external verification.
