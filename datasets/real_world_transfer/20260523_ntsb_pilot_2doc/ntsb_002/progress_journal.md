# Progress Journal

## 2026-05-23 Intake Normalization

Promoted this fixture from the two-document NTSB pilot intake package into `datasets/real_world_transfer/20260523_ntsb_pilot_2doc`. The source text and oracle were preserved, QA was converted to the runner-compatible numbered-question format, the incoming QA file was retained as `qa_authored.md`, and the original PDF was fetched from the official source URL.

No compile or QA measurement has been recorded yet for this canonical dataset location.

## 2026-05-23 q024 Oracle Wording

Adjusted the q024 reference answer to stay inside source text. The incoming wording said recovery damage complicated impact-damage analysis; the source supports the narrower statement that post-casualty investigators found fractures and indentations that appeared to be from recovery activities.

## 2026-05-23 Transfer Spotcheck

Compiled in the two-document NTSB pilot batch with OpenRouter `qwen/qwen3.6-35b-a3b`.
The compile parsed, but the quality gate held on `risk_count>5`.

Initial QA was 22 exact / 2 partial / 1 miss. After the source-record
clock-duration repair and q024 oracle grounding correction, replay QA was 23
exact / 2 partial / 0 miss with 0 compatibility rows, runtime load errors, or
write proposal rows.

The remaining partials are useful product pressure. q019 requires aggregating
separate weather-station rows into a station range while preserving the crew
estimate as a distinct source. q024 now has source support for salvage dates
and recovery-activity damage, but the question asks about physical-evidence
completeness, which still wants an explicit evidence-integrity/source-surface
relation rather than a loose causal inference.

## 2026-05-23 Partial Clearance

Follow-up repairs cleared both remaining partials. q019 recovered after adding
query-only source-record numeric range support for range/comparison questions.
q024 recovered after adding a narrow source-text vocabulary bridge from salvage
language to recovery-activity language. Replay QA was 25 exact / 0 partial / 0
miss with 0 compatibility rows, runtime load errors, or write proposal rows.
