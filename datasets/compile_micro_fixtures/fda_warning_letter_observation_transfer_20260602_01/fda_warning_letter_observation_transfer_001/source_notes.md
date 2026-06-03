# source_notes.md — fda_warning_letter_observation_transfer_001

Oracle notes only. Not consumed by compile. Every non-obvious expected row is
justified from `source.md` text below.

## Source

- Catalent Indiana, LLC - 718189 - 11/20/2025, CDER (Office of Manufacturing Quality).
- Real public-domain FDA document. Company is distinct from Rechon, Liebel-Flarsheim,
  and the prior transfer fixtures. Finished-pharma sterile injectable site (Bloomington,
  Indiana; facility acquired by Novo Nordisk, hence the recipient's Novo Nordisk address
  and email).

## Wrapper / identity / parties

- issuing office `office_of_manufacturing_quality`: the Issuing Office field reads "Office
  of Manufacturing Quality"; the signatory block confirms OMQ is within CDER, but the
  wrapper carrier preserves the source-stated office.
- FEI `3005949964`, location `bloomington_indiana`: "FEI 3005949964, at 1300 South
  Patterson Drive, Bloomington, Indiana."
- recipient `catalent_indiana_llc` under the correspondence-party contract's firm/entity
  preference; `maziar_doustdar` is a source-stated responsible official, not the expected
  recipient row. signatory `francis_godwin`; response contact `carrie_a_hughes`
  ("ATTN: Carrie A. Hughes").

## Chronology

- inspection `2025-06-23`..`2025-07-14`: "from June 23 to July 14, 2025."
- 483 response `2025-08-04`: "your August 4, 2025, response to our Form FDA 483."

## Regulatory meeting (positive control)

- `fda_regulatory_meeting(Meeting, Facility, v_2025_09_26, Src)`: "FDA held a teleconference
  with your firm on September 26, 2025." Live /4 shape carries the meeting DATE (no type atom).
  This is a meeting that OCCURRED, so the carrier is
  emitted positively (contrast with fixtures 002/003, where no meeting occurred and the
  absence is recorded as an omission). Date 2025-09-26 not carried in the /4 signature; note
  only. The GDUFA footnote (future Post-Warning-Letter-Meeting eligibility) is boilerplate
  and is NOT separately modeled because an actual meeting was held.

## Violations and the observation/record_review distinction

- Violation 1 (211.192) -> `investigation_failure`. Its detail subjects are
  `record_review_subject` because the citation is a failure-to-investigate allegation:
  - `mammalian_hair_contamination`: ">20 deviations related to extrinsic 'mammalian hair'
    contamination ... You did not initiate timely investigations in response to this
    contamination." The contamination is the SUBJECT of the investigation failure, not
    facility-design evidence.
  - `media_fill_termination`: "you terminated more than five media fill batches ... you
    failed to open a deviation or an investigation at the time of each failure."
  - `premature_capa_sunset` with role `corrective_action_evaluation`: FDA's critique of the
    firm's response - "heightened testing ... cannot be sunsetted until you have adequate
    data." This is evaluation of the firm's CAPA, not the cited deficiency, hence the role.
  - `response_status=response_inadequate` (role corrective_action_evaluation): "Your response
    is inadequate" appears under Violation 1.

- Violation 2 (211.113(b)) -> `contamination_control`. Its detail subjects are
  `observation_subject` because the contamination/EM evidence is cited as evidence of a
  facility/microbiological-control failure, not as an uninvestigated discrepancy:
  - `environmental_monitoring_failure`: "the 'most probable root cause' of an environmental
    monitoring failure of a sample was equipment surfaces that were occluded during
    decontamination." The EM failure is observed evidence that the contamination-control
    system failed. This is the row that must NOT be tagged record_review_subject.
  - `surface_contact_plate_sampling_inadequacy`: "your firm's use of contact plates is not as
    effective as using swab methods ... increase the risk of failing to detect microbial
    contaminants." Observed control inadequacy.
  - `decontamination_process_validation` (procedure_scope): occluded surfaces "not reliably
    exposed to ... decontamination" and the request to review exposure to a "validated
    decontamination process."
  - `response_status=response_inadequate` (role corrective_action_evaluation): "Your response
    is inadequate" appears under Violation 2.

The deliberate contrast: the EM failure (V2) is `observation_subject`; the mammalian-hair and
media-fill subjects (V1) are `record_review_subject`. Forbidden facts pin the swaps.

## Other rows

- `fda_adulteration_basis(..., '21 USC 351(a)(2)(B)', cgmp_nonconformance, ...)`: standard
  501(a)(2)(B) adulteration sentence.
- response requirements: "respond ... within 15 working days"; reply channel
  CDER-OC-OMQ-Communications@fda.hhs.gov with FEI 3005949964 and ATTN Carrie A. Hughes.
- conclusion scope: "not intended to be an all-inclusive list"; "You are responsible for
  investigating ... preventing their recurrence"; "regulatory or legal action ... seizure and
  injunction."

## Not represented

- No `fda_consultant_recommendation`: this letter contains no 21 CFR 211.34 consultant
  language. Absent, not source-stated, so neither emitted nor recorded as an omission.
- No `domain_omission`: a meeting was held and FEI is present, so no negative control applies
  here (fixtures 002/003 carry the FEI-absent omission).

## Uncertainty about atom choice

- Category `contamination_control` for V2 (211.113(b)) matches prior fixtures; `investigation_failure`
  for V1 matches the residue-family token.
- Detail-kind/value tokens (`surface_contact_plate_sampling_inadequacy`, `premature_capa_sunset`,
  `decontamination_process_validation`) are compact best-guesses; confirm value domains against the
  registry. The cross-fixture tokens (`observation_subject`, `record_review_subject`,
  `procedure_scope`, `violation_scope`, `corrective_action_evaluation`) are fixed by the worksheet.
- Live registry shapes applied: `fda_violation_detail/5` (no detail id; `response_status` used
  for CAPA/response critiques since `corrective_action` is not an allowed detail_kind);
  `fda_correspondence_party(Letter, Party, contact, ...)` (role `contact`, not response_contact);
  `v_`-atom dates; `cfr_` citation atoms; meeting carried as a `v_`-date.
