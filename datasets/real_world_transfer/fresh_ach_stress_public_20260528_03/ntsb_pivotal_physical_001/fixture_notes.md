# fixture_notes — ntsb_pivotal_physical_001

## Why this source was chosen
A compact, self-contained NTSB general-aviation final report in which the probable cause (a stuck carburetor float from improper maintenance) hinges on a single in-flight physical signature, while a competing cause (carburetor icing) has genuine, document-stated support. It is a clean high-sensitivity case that is fresh (not used in any prior batch) and entirely public domain.

## Why the sensitivity target is high
The carburetor's physical condition is over-determined (out-of-tolerance float clearance, rub marks, twisted float, multiple unmet service bulletins), but those facts establish only that a stuck float COULD have happened. The link to what actually happened in flight rests on one row: the rich-mixture signature (a witness's abnormal exhaust observation plus carbon-fouled spark plugs), which is exactly why the report says the loss was "likely the result of a stuck carburetor float." Remove that row and the report's own logic degrades from "likely" to "could have," while the icing alternative — supported by an FAA chart showing serious-icing probability at cruise power — is held back only by the single fact that carb heat was applied at runup. So a single-row removal makes the winner much weaker and elevates the alternative: high sensitivity, with e1 as the pivotal row.

## Tempting wrong hypothesis
Carburetor icing (h2). It is genuinely supported (conducive conditions) and is the alternative the report explicitly had to rule out. A reader over-weighting environmental conditions and under-weighting the carb-heat-at-runup fact could pick it.

## Direct / partial / off-axis rows
- Direct to h1: e1 (rich-mixture signature, pivotal), e2 (float touching wall / out-of-tolerance), e3 (maintenance/SB non-compliance), e8 (soot cleared after normal-mixture run).
- Direct to h2: e4 (icing probability at cruise power).
- Counter to h2 (direct, negative): e5 (carb heat at runup).
- Knock-downs: e6 (fuel clean → against h3), e7 (clean exam / normal test run → against h4).

## Double-edged rows
- e5 is double-edged with e4: it is the only thing keeping icing from leading, so its presence/absence swings the h1-vs-h2 margin.
- e7 is mildly double-edged for h1: a smooth post-accident test run shows the float was not stuck at test time, which could be read against h1, but the in-flight rich-mixture signature (e1) implicates an intermittent stick during flight.

## Extraction quirks
- The report mixes "could have" (capability) language with a "likely" (causation) conclusion; the distinction is the whole point of the sensitivity design and must be preserved.
- Two separate float-clearance measurements are reported (one within tolerance for the throttle-body-to-bowl-gasket clearance, one out of tolerance for the float-to-bowl clearance); the out-of-tolerance one is the relevant defect.
- Times appear in both local (1528 PDT) and Zulu (2249Z) forms; section coordinates keep these together under [METEOROLOGICAL INFORMATION] and [HISTORY OF FLIGHT].
