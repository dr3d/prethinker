# fixture_notes — ntsb_engine_power_001

## Why this document is a good ACH stress test

This is the **designated balanced fixture** for the batch: the winning hypothesis depends on a single physical finding, and removing that finding plausibly changes the winner. It exists to test whether an ACH/sensitivity routine reports real sensitivity rather than always returning zero.

## The competing explanations are genuinely in tension within the source

The Analysis section weighs three causes for the partial loss of engine power, and each has both supporting and undercutting evidence inside the same document:

- **Fuel exhaustion (h1).** Supported by the empty tanks with no leak, and by the gradual throttle-unresponsive fade. Undercut on its face by the pilot's belief that 10+ gallons remained — which the report converts into support by inferring the pilot's fuel math was wrong.
- **Carburetor icing (h2).** Supported affirmatively by the FAA icing-probability chart placing the flight in the "serious icing at glide power" band. Undercut by the pilot's statement that he applied carburetor heat and enrichened the mixture.
- **Throttle/mechanical (h3).** Kept alive only because impact damage prevented documenting the throttle cable's full travel. Undercut by everything that could be examined being normal (cabling attached, no restriction, no preimpact anomalies).

## The sensitivity hinge

The empty-tanks/no-leak finding (evidence row e1) is the only direct physical anchor for fuel exhaustion. The carburetor-icing hypothesis has independent affirmative support (conducive conditions) that is only partly offset by the carb-heat statement. So:

- With e1 present, fuel exhaustion wins (matching the report's probable cause).
- With e1 removed, fuel exhaustion is left resting on a speculative "calculations could have been wrong," while icing retains affirmative environmental support — plausibly flipping the winner to h2.

A correct ACH read should mark this fixture **high** sensitivity and name e1 as pivotal. An engine that reports zero sensitivity here, or that cannot identify which evidence row is load-bearing, is failing the test this fixture is built for.

## Source-containment

Every fact needed to answer the QA and to run the ACH is present in source.md. The technical terms that matter — carburetor heat as the icing mitigation, "conducive to serious icing at glide power," "no preimpact anomalies," "did not appear to have leaked" — are quoted from the report itself. No outside aviation expertise, acronym expansion, or agency background is required. Acronyms that appear (VMC, msl, rpm, FAA, FSDO) are not load-bearing for any answer; where a term carries weight, the report states its meaning in context.

## Real-document messiness preserved

- Two readings of the same fact: "should have contained at least 10 gallons" cuts against fuel exhaustion literally but is used to support it via faulty-planning inference.
- An absence-of-evidence gap (undocumentable throttle-cable travel) that prevents fully eliminating a hypothesis without affirmatively supporting it.
- A self-reported mitigation (carb heat) that the investigation neither confirms nor disproves but treats as weakening the icing hypothesis.
- The NTSB's own framing (Defining Event and probable cause both naming fuel exhaustion) is present in the document, so a system can be tested on whether it reasons from evidence or simply parrots the stated conclusion.
