# Fixture Notes

## Intake

Received as a rough NTSB pilot package in `tmp` on May 23, 2026. The nested package contained one complete document fixture, `ntsb_aviation_001`, plus a manifest reference to `ntsb_marine_001` marked `template_ready` but not present as a usable fixture. The package did not include the promised PDF, so the original NTSB PDF was fetched from the source URL in `metadata.json` and retained as `source_original.pdf`.

## Fitness

Usable for a one-document shakedown of the real-world transfer harness. It should not be treated as a clean thermometer claim because it was assembled quickly, the source extraction includes visible encoding artifacts, and the package-level manifest overstated the completed document count.

## Pressure

The document stresses structured table extraction, source-authority statements, causal-chain handling, operator-claim versus NTSB-finding separation, timeline fields, and units in weather/aircraft data.

## Normalization

The canonical `qa.md` was regenerated as questions-only. Reference answers are retained in `oracle.jsonl` and `qa_battery.json` for after-the-fact scoring only.
