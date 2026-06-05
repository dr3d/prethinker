# Oracle Authoring Notes — state_ag_settlement_aod_transfer_002

Instrument: NY OAG Assurance of Discontinuance, In re Equinox Group, LLC, Equinox Holdings, Inc.,
Equinox Media, LLC, and SoulCycle LLC — Assurance No. 24-099.
Authored from `source.md` + `ontology_registry.json` only; blind to model outputs/run artifacts.
The captured `source.md` is the OAG **Findings** (paras 1-87). Provenance states the relief, monetary,
release, reporting, and signature provisions follow the Findings and are **not** reproduced here.

## Expected facts (18) and source basis

### Instrument (1)
- `state_ag_instrument(aod_24_099, assurance_of_discontinuance, new_york_attorney_general, equinox_group_llc, assurance_24_099, not_stated, caption)`.
  Caption: "ASSURANCE OF DISCONTINUANCE", "Assurance No. 24-099", issued by the OAG, primary
  respondent "Equinox Group, LLC ('Equinox Group' or 'Respondents')". **effective_date = not_stated**:
  the Findings extract states no execution/effective date for the AOD. (The packet `metadata.json`
  carries source_date 2025-05-19, but that string does not appear in `source.md`, so it is not
  authored here — and the forbidden file pins it as a control.)

### Parties (5) — caption
- regulator `new_york_attorney_general`; respondents `equinox_group_llc`, `equinox_holdings_inc`,
  `equinox_media_llc`, `soulcycle_llc`. The caption names exactly these four respondents and the
  investigating Attorney General.

### Authority citations (5) — investigation authority (opening paragraph)
- The opening sentence: "commenced an investigation pursuant to Executive Law § 63(12), General
  Business Law §§ 349, 350, and 527-a, and the Restore Online Shoppers' Confidence Act, 15 U.S.C.
  § 8403(3)." -> `executive_law_63_12`, `gbl_349`, `gbl_350`, `gbl_527_a`, `rosca_15_usc_8403_3`,
  all role `investigation_authority`. (The GBL § 527/§ 527-a sub-paragraph definitions in paras 2-7
  and GBL § 624(2) in the material-terms lists are legal-framework / material-term prose and are NOT
  authored as instrument authority citations.)

### Events (3) — exact-date only
- `conduct_period_start v_2021_02_09` (para 16: "Since at least February 9, 2021 ... Respondents
  offered automatically renewing memberships through Equinox and Equinox Media").
- `enrollment_disclosure_revision v_2023_07_15` (paras 59-67: "On July 15, 2023, SoulCycle updated
  the page to add 'This membership is a recurring payment ...'").
- `online_cancellation_established v_2024_07_28` (paras 47-54: "Beginning July 28, 2024, Equinox
  established an online cancellation option for all New York members").

### Contact channels (4) — cancellation emails, brand-correct
- `cancellations_equinox_com` -> `equinox_holdings_inc` (Equinox brand; para 32; Equinox owned by
  Equinox Holdings, Inc per para 17).
- `yoursoulmatters_soul_cycle_com` -> `soulcycle_llc` (Soul Renew; para 58).
- `hello_equinoxplus_com` and `hello_equinoxmedia_com` -> `equinox_media_llc` (Equinox+, operated
  through Equinox Media; paras 77-80).

## Empty lanes (intentional)
- `state_ag_obligation`, `state_ag_monetary_payment`, `state_ag_signature`: the relief, monetary, and
  signature provisions are not in the captured Findings extract, so no facts are authorable for these
  carriers. Converting Findings narrative into obligations, mis-typing a consumer charge as a
  settlement payment, or inventing a signature would be unsupported — these are forbidden controls.

## Omitted / ambiguous areas (deliberately not authored)
- **Month-only dates** could not become `v_YYYY_MM_DD`: SoulCycle/Soul Renew start "September 2021";
  Equinox App PT/Pilates revision "July 2021"; webchat-cancellation end "March 2023"; "Process updated
  September 2022". No exact day -> omitted rather than guess a day.
- **Blink Fitness bankruptcy v_2024_08_12** (para 15) is exact, but Blink is a non-respondent
  subsidiary and the event is background to a different entity, not relevant to this instrument ->
  omitted (and Blink-as-respondent is a forbidden control).
- **Material-terms / cancellation-exception lists** (paras 22, 58) and the recurring three-part
  violation language are findings substance, not skeleton anatomy -> not authored as obligations.
- **Letitia James** named in the caption is captured via the `regulator` party (office), not as a
  signatory (no signature block in the extract).
- **GBL § 527/§ 527-a sub-paragraphs and § 624(2)** appear as legal-framework/material-term prose;
  only the opening investigation-authority list is authored as citations.

## Forbidden controls (12) — what they test
instrument date not in the source body; Blink-as-respondent (wrong/added party); SoulCycle-as-regulator
(wrong role); caption-roster blob (prose party_name); GBL 624(2) as investigation authority (wrong
authority role); statutory-definition prose in a citation slot; cancellations@equinox.com tied to
SoulCycle and yoursoulmatters tied to Equinox (wrong contact attachments); narrative sentence in a
channel_value slot; a Findings disclosure recast as a prospective obligation; the $300 Equinox
initiation fee mis-typed as a settlement penalty payment; and the "save the member" narrative as a
dated event.

All facts use only registered `state_ag_settlement_v1` signatures with correct arities; forbidden set
is disjoint from expected; both files parse.
