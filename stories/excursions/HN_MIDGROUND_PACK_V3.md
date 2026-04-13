# HN Midground Pack v3 (Harder)

Generated on: 2026-04-13 22:23:51 UTC

Purpose:
- push beyond v2 with denser disagreement, technical/legal uncertainty, and noisier claim-rebuttal structure.
- provide immediate turnsets for MITM and excursion stress loops.

Artifacts:
- manifest: `stories/excursions/hn_midground_manifest_v3.json`
- snapshots: `stories/excursions/hn_midground_v3/*.json`
- turnsets: `stories/excursions/hn_midground_v3/turnsets/*.json`

Selected threads:
- hn_mcp_over_skills_debate (G3, agent_tooling)
  - HN: https://news.ycombinator.com/item?id=47712718
  - Title: I still prefer MCP over skills
  - Descendants: 370 | Harvested comments: 140
  - Snapshot: stories/excursions/hn_midground_v3/hn_mcp_over_skills_debate.json
- hn_mythos_vuln_frontier (G4, security_reasoning)
  - HN: https://news.ycombinator.com/item?id=47732020
  - Title: Small models also found the vulnerabilities that Mythos found
  - Descendants: 339 | Harvested comments: 140
  - Snapshot: stories/excursions/hn_midground_v3/hn_mythos_vuln_frontier.json
- hn_signal_notification_forensics (G4, privacy_legal)
  - HN: https://news.ycombinator.com/item?id=47716490
  - Title: FBI used iPhone notification data to retrieve deleted Signal messages
  - Descendants: 305 | Harvested comments: 140
  - Snapshot: stories/excursions/hn_midground_v3/hn_signal_notification_forensics.json
- hn_france_windows_to_linux (G3, policy_geopolitics)
  - HN: https://news.ycombinator.com/item?id=47719486
  - Title: France to ditch Windows for Linux to reduce reliance on US tech
  - Descendants: 698 | Harvested comments: 140
  - Snapshot: stories/excursions/hn_midground_v3/hn_france_windows_to_linux.json
- hn_gitbutler_series_a_git_future (G3, startup_strategy)
  - HN: https://news.ycombinator.com/item?id=47712656
  - Title: We've raised $17M to build what comes after Git
  - Descendants: 751 | Harvested comments: 140
  - Snapshot: stories/excursions/hn_midground_v3/hn_gitbutler_series_a_git_future.json
- hn_20_dollar_stack_mrr (G3, ops_claims)
  - HN: https://news.ycombinator.com/item?id=47736555
  - Title: I run multiple $10K MRR companies on a $20/month tech stack
  - Descendants: 495 | Harvested comments: 140
  - Snapshot: stories/excursions/hn_midground_v3/hn_20_dollar_stack_mrr.json

Turnset policy:
- each turnset is OP + 14 sampled comments (15 turns).
- comment traversal uses BFS with `max_depth=4` and `max_comments=140`.

Use:
- recommended first run: `scripts/run_mitm_session.py` with `--max-turns 12` then full 15-turn pass.
- promote repeated misses into new `rung_47x` failure-guard scenarios.
