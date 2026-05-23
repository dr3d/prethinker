# NTSB Marine Weather ACH Probe

This is the first real-document ACH overlay payload for Prethinker. It is built
from the wild real-world transfer fixture
`datasets/real_world_transfer/20260523_wild_01/ntsb_marine_investigation_001`
and its Qwen A3B source compile artifact.

The payload is manual by design. It selects a small set of admitted source
surfaces and asks whether they disconfirm competing explanations for the Baylor
J. Tregre casualty. The ACH scorer is deterministic and does not mutate the KB
or affect QA exact/partial/miss scoring.

The probe pressures:

- competing root-cause hypotheses over messy incident reports
- least-disconfirmation ranking rather than support-count ranking
- explicit treatment of absence evidence
- separation between documented weather-warning limits and crew-blame claims

