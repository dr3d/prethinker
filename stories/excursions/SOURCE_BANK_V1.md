# Excursion Source Bank v1

Last updated: 2026-04-13

Purpose:

- provide manageable real-world source material for `excursion_cooperative` and `excursion_wild` lanes
- keep a graded difficulty ramp so we can push harder without going chaotic too fast

Difficulty grades:

- `G1`: structured formal Q&A, low ambiguity
- `G2`: structured but longer with cross-speaker references
- `G3`: forum-style, mostly coherent, moderate noise
- `G4`: forum narrative with revisions/hedges and partial contradictions
- `G5`: high-noise multi-party thread fragments (reserved for later rounds)

## Pack: `excursion_cooperative_v1` (6)

1. `coop_fed_2025_03_19` (`G1`)
- Source: https://www.federalreserve.gov/mediacenter/files/FOMCpresconf20250319.pdf
- Why: clean institutional Q&A with explicit entities, policies, and temporal references.
- Suggested extraction: 8-12 turns from one question block + one follow-up.

2. `coop_fed_2024_09_18` (`G1`)
- Source: https://www.federalreserve.gov/mediacenter/files/FOMCpresconf20240918.pdf
- Why: declarative statements plus clarifying follow-ups; good for relation consistency checks.
- Suggested extraction: 8-12 turns, include one corrective follow-up.

3. `coop_fed_2024_01_31` (`G1`)
- Source: https://www.federalreserve.gov/mediacenter/files/FOMCpresconf20240131.pdf
- Why: repetitive policy language with subtle changes; useful for near-duplicate disambiguation.
- Suggested extraction: 6-10 turns from adjacent pages.

4. `coop_scotus_2024_22_913` (`G2`)
- Source: https://www.supremecourt.gov/oral_arguments/argument_transcripts/2023/22-913_9pg7.pdf
- Why: clear speaker labels with adversarial questioning and reformulations.
- Suggested extraction: 10-14 turns from one advocate segment.

5. `coop_scotus_2025_23_1197` (`G2`)
- Source: https://www.supremecourt.gov/oral_arguments/argument_transcripts/2025/23-1197_c07d.pdf
- Why: longer legal reasoning chains and frequent speaker switching.
- Suggested extraction: 10-14 turns with at least one rebuttal transition.

6. `coop_scotus_2026_25_365` (`G2`)
- Source: https://www.supremecourt.gov/oral_arguments/argument_transcripts/2025/25-365_l6gn.pdf
- Why: high turn density and topic pivots that pressure cross-turn state retention.
- Suggested extraction: 12-16 turns from a contiguous exchange.

## Pack: `excursion_wild_v1` (6)

Middle lane (`G3`, Hacker News):

1. `wild_hn_docker_spain_block` (`G3`)
- Source: https://news.ycombinator.com/item?id=47738883
- Why: incident narrative with causal speculation and corrections in comments.
- Suggested extraction: OP text + 6-10 top comments.

2. `wild_hn_codex_vs_claude` (`G3`)
- Source: https://news.ycombinator.com/item?id=47750069
- Why: comparative claims, hedges, and mixed evidence styles.
- Suggested extraction: OP text + 8-12 comments across opposing views.

3. `wild_hn_agents_private_keys` (`G3`)
- Source: https://news.ycombinator.com/item?id=47736831
- Why: security claims with policy framing and practical exceptions.
- Suggested extraction: OP text + 6-10 comments.

Noisy lane (`G4`, Reddit legal threads):

4. `wild_reddit_security_deposit_appeal` (`G4`)
- Source: https://www.reddit.com/r/legaladvice/comments/143pw0n/usca_update_landlord_has_not_returned_the/
- Why: timeline updates, outcome revision, and procedural next-step uncertainty.
- Suggested extraction: post body + 2-4 key moderator/system comments.

5. `wild_reddit_landlord_entered_furniture` (`G4`)
- Source: https://www.reddit.com/r/legaladvice/comments/t2ppb8
- Why: long personal narrative with dates, actions, and alleged violations.
- Suggested extraction: opening narrative paragraphs only (avoid deep comment tree at first).

6. `wild_reddit_commercial_entry_dozens` (`G4`)
- Source: https://www.reddit.com/r/legaladvice/comments/1lorwlj
- Why: claim/counterclaim framing, surveillance references, and legal-vs-practical ambiguity.
- Suggested extraction: OP narrative + 3-5 top comments.

## Immediate conversion plan

1. Convert `coop_fed_2024_01_31` -> one `excursion_cooperative` scenario.
2. Convert `wild_hn_docker_spain_block` -> one `excursion_wild` scenario.
3. Run through the current LM Studio Semantic IR path, usually
   `qwen/qwen3.6-35b-a3b` with structured output.
4. Promote recurrent failure patterns into new `rung_*` files only after repeatability.
