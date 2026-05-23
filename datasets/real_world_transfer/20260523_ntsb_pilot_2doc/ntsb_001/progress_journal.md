# Progress Journal

## 2026-05-23 Intake Normalization

Promoted this fixture from the two-document NTSB pilot intake package into `datasets/real_world_transfer/20260523_ntsb_pilot_2doc`. The source text and oracle were preserved, QA was converted to the runner-compatible numbered-question format, the incoming QA file was retained as `qa_authored.md`, and the original PDF was fetched from the official source URL.

No compile or QA measurement has been recorded yet for this canonical dataset location.

## 2026-05-23 Transfer Spotcheck

Compiled in the two-document NTSB pilot batch with OpenRouter `qwen/qwen3.6-35b-a3b`.
The compile parsed, but the quality gate held on source-claim carrier/backbone
coexistence delivery.

Initial QA was 24 exact / 0 partial / 1 miss. The miss was q009, a duration
question asking minutes from Seattle departure to the accident. Source-record
rows contained both clock endpoints (1328 and 1620), but the KB did not have a
durable accident event fact for the endpoint. After adding general
source-record clock-duration support, replay QA was 25 exact / 0 partial / 0
miss with 0 compatibility rows, runtime load errors, or write proposal rows.

The follow-up full two-document replay after range/recovery query-surface
repairs stayed clean for this fixture: 25 exact / 0 partial / 0 miss.
