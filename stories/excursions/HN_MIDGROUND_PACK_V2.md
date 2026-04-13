# HN Midground Pack v2

Generated on: 2026-04-13 21:46:38 UTC

Purpose:
- provide middle-ground, real-world HN threads with enough noise to pressure parsing without pure chaos.
- each snapshot includes OP text + sampled comment transcript for immediate scenario conversion.

Artifacts:
- manifest: `stories/excursions/hn_midground_manifest_v2.json`
- snapshots: `stories/excursions/hn_midground_v2/*.json`

Selected threads:
- `hn_docker_spain_block` (G2, incident_policy)
  - HN: https://news.ycombinator.com/item?id=47738883
  - Title: Tell HN: Docker pull fails in Spain due to football Cloudflare block
  - Descendants: 401 | Harvested comments: 120
  - Snapshot: `stories/excursions/hn_midground_v2/hn_docker_spain_block.json`
- `hn_anthropic_cache_ttl_downgrade` (G2, vendor_contract)
  - HN: https://news.ycombinator.com/item?id=47736476
  - Title: Anthropic downgraded cache TTL on March 6th
  - Descendants: 412 | Harvested comments: 120
  - Snapshot: `stories/excursions/hn_midground_v2/hn_anthropic_cache_ttl_downgrade.json`
- `hn_quota_exhaustion_claims` (G3, service_reliability)
  - HN: https://news.ycombinator.com/item?id=47739260
  - Title: Pro Max 5x quota exhausted in 1.5 hours despite moderate usage
  - Descendants: 639 | Harvested comments: 120
  - Snapshot: `stories/excursions/hn_midground_v2/hn_quota_exhaustion_claims.json`
- `hn_email_reputation_gmail` (G2, deliverability_ops)
  - HN: https://news.ycombinator.com/item?id=47738978
  - Title: We have a 99% email reputation, but Gmail disagrees
  - Descendants: 298 | Harvested comments: 120
  - Snapshot: `stories/excursions/hn_midground_v2/hn_email_reputation_gmail.json`
- `hn_distilling_ban_unconstitutional` (G3, legal_reasoning)
  - HN: https://news.ycombinator.com/item?id=47751781
  - Title: US appeals court declares 158-year-old home distilling ban unconstitutional
  - Descendants: 214 | Harvested comments: 97
  - Snapshot: `stories/excursions/hn_midground_v2/hn_distilling_ban_unconstitutional.json`
- `hn_wordpress_plugins_backdoor` (G3, security_incident)
  - HN: https://news.ycombinator.com/item?id=47755629
  - Title: Someone Bought 30 WordPress Plugins and Planted a Backdoor in All of Them
  - Descendants: 126 | Harvested comments: 96
  - Snapshot: `stories/excursions/hn_midground_v2/hn_wordpress_plugins_backdoor.json`

Turnsets:
- ready-to-run turn files: stories/excursions/hn_midground_v2/turnsets/*.json
- each turnset contains OP + 11 sampled comments (12 turns total)
