# Progress Journal

## 2026-05-23 Intake Normalization

Promoted the one complete NTSB aviation fixture from the rough incoming tmp package into `datasets/real_world_transfer/20260523`. Regenerated the QA surface to remove answer-bearing package header context, retained the source extraction as received, fetched the original public PDF from the metadata source URL, and isolated reference answers in scoring-only files.

No compile or QA measurement has been recorded yet for this fixture in its canonical dataset location.

## 2026-05-23 Shakedown Compile And QA

Ran the rough pilot through OpenRouter `qwen/qwen3.6-35b-a3b` with one lane.
The compile parsed and admitted `81` rows with `0` skips, but the compile
quality gate held on source-claim/source-authority delivery. This is useful
diagnostic pressure and should not be described as a clean compile gate pass.

Initial QA exposed a real active-harness routing weakness: later source-record
section and label headers were present in the compiled KB, but query hints only
used capped examples. The repair made full source-record section and label
header inventories available to the QA planner, while keeping the hints driven
by question text and compiled KB inventory only.

Final full QA replay after the source-record routing repair:

```text
25 exact / 0 partial / 0 miss
0 compatibility rows
0 runtime load errors
0 QA write proposal rows
```

Artifacts were moved out of repo `tmp` to
`C:\prethinker_tmp_archive\ntsb_pilot_shakedown_20260523`.
