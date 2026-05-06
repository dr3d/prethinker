# Cross-Fixture Repair Slices

This report merges repair-target artifacts and looks for repeated failure
themes across fixtures. It is a planning tool, not a source interpreter.

## Policy

- Reads repair-target artifacts only.
- Does not inspect fixture source prose, gold KBs, or answer keys.
- Recommends only themes with targets in multiple fixtures by default.

## Summary

- targets: `72`
- fixtures: `10`
- recommended slices: `9`
- top theme: `rule_interpretation_application`
- theme counts: `{'answer_restraint_surface': 2, 'authority_document_control': 9, 'classify_before_repair': 4, 'entity_role_identity': 5, 'object_state_custody': 14, 'quantity_arithmetic_capacity': 3, 'rationale_claim_uncertainty': 10, 'rule_interpretation_application': 16, 'temporal_status_deadline': 9}`

## Recommended Slices

## First Action Result

The first run attacked `rule_interpretation_application` on Heronvale and
Meridian with a scoped source-surface compile. Meridian is the clean win:
full-40 improved from `26 / 10 / 4` in the archived comparison baseline to
`39 / 1 / 0`, with `14` rescued rows and `0` baseline-exact regressions.
Heronvale is useful but bounded: the targeted repair rows were `3 / 0 / 0`,
but full QA was `21 / 3 / 1`, with one baseline-exact regression and a result
below the existing row-selector high-water. Treat this as a candidate mode and
transfer probe, not as a new global compile default.

## Second Action Result

The next run attacked `object_state_custody` on Fenmore and Larkspur with a
combined object/state/custody compile. The result is a useful rejection:
Fenmore's combined compile scored only `12 / 3 / 10` against a `20 / 1 / 4`
baseline, and Larkspur scored `27 / 7 / 6` against the sharper final-state
lens at `36 / 2 / 2`. The broad surface is not promotable. The positive gain
is selector machinery: on Fenmore, adding the rejected object/status artifact
to the frozen roster creates a `25 / 0 / 0` upper bound, and a new
reason-named deaccession-yet status guard reaches it with `25/25` selected-best
rows and `0` selector errors. Treat object state, custody roster,
permission/motive, conservation rationale, and deaccession status as separate
surfaces.

## Third Action Result

The next run attacked `temporal_status_deadline` on Ashgrove and Copperfall.
Ashgrove shows the useful path: the broad temporal compile is weaker as a
standalone mode (`19 / 5 / 1`) than the operational variant (`21 / 4 / 0`), but
it carries an adjusted-expiration surface that the selector can use. Adding
adjusted-expiration and correction-entitlement guards moves Ashgrove's frozen
selector from `22 / 3 / 0` to the `24 / 1 / 0` upper bound with `25/25`
selected-best rows and `0` selector errors. Copperfall is the boundary marker:
the same broad temporal surface regresses full QA to `25 / 5 / 10` against the
documented `38 / 1 / 1` high-water. It rescues the original-answer-deadline row
but still chooses the wrong deadline family for the later reply-deadline row.
Treat temporal status, adjusted expiration, correction entitlement, and
deadline-family query disambiguation as separate surfaces.

### `rule_interpretation_application`

- priority score: `115`
- targets: `16`
- fixtures: `3` - fenmore_seedbank, heronvale_arts, meridian_permit_board
- surfaces: `{'compile_surface_gap': 11, 'hybrid_join_gap': 5}`
- lanes: `{'helper_or_query_join_repair': 5, 'scoped_source_surface_repair': 11}`
- purpose: Acquire or apply rule text, conditions, interpretations, eligibility, approval, and compliance surfaces.

| Fixture | Row | Verdict | Surface | Question |
| --- | --- | --- | --- | --- |
| `fenmore_seedbank` | `q015` | `miss` | `compile_surface_gap` | Why was FB-2026-006 split to Vault 4? |
| `heronvale_arts` | `q004` | `miss` | `compile_surface_gap` | What is the effective matching percentage for Application C (Espinoza)? |
| `heronvale_arts` | `q009` | `miss` | `compile_surface_gap` | Can the Heronvale Poetry Circle apply as currently constituted? |
| `heronvale_arts` | `q010` | `miss` | `compile_surface_gap` | What is the Foundation Director's suggested remedy for the Poetry Circle? |
| `meridian_permit_board` | `q014` | `miss` | `compile_surface_gap` | What materials does Lindqvist propose for the addition? |
| `meridian_permit_board` | `q023` | `miss` | `compile_surface_gap` | Does the shared-parking arrangement require Board approval? |
| `meridian_permit_board` | `q038` | `miss` | `compile_surface_gap` | What happens if the Board classifies the REO coverage limit as appearance-related instead of dimensional? |
| `meridian_permit_board` | `q039` | `miss` | `compile_surface_gap` | Does the 2021 Board interpretation constitute codified law? |

### `object_state_custody`

- priority score: `106`
- targets: `14`
- fixtures: `2` - fenmore_seedbank, larkspur_clockwork_fair
- surfaces: `{'compile_surface_gap': 14}`
- lanes: `{'scoped_source_surface_repair': 14}`
- purpose: Acquire object current-state, condition, location, custody, ownership, award, and device transition surfaces.

| Fixture | Row | Verdict | Surface | Question |
| --- | --- | --- | --- | --- |
| `fenmore_seedbank` | `q016` | `miss` | `compile_surface_gap` | Is the Vault 4 split a viability concern? |
| `larkspur_clockwork_fair` | `q011` | `miss` | `compile_surface_gap` | What thread is currently in the Pearlescent Loom? |
| `larkspur_clockwork_fair` | `q012` | `miss` | `compile_surface_gap` | What is the current condition of the Gilt Salamander's appearance? |
| `larkspur_clockwork_fair` | `q014` | `miss` | `compile_surface_gap` | What color light does the Moth Lantern currently emit? |
| `larkspur_clockwork_fair` | `q015` | `miss` | `compile_surface_gap` | Where is the Compass Rose at the end of the fair? |
| `larkspur_clockwork_fair` | `q023` | `miss` | `compile_surface_gap` | Why can't the Pearlescent Loom demonstrate its temperature-chromatic function? |
| `larkspur_clockwork_fair` | `q025` | `miss` | `compile_surface_gap` | What chain of events led to the Salamander's damaged foreleg? |
| `larkspur_clockwork_fair` | `q028` | `miss` | `compile_surface_gap` | Why did Cassia modify the Moth Lantern? |

### `rationale_claim_uncertainty`

- priority score: `97`
- targets: `10`
- fixtures: `5` - fenmore_seedbank, harrowgate_witness_file, heronvale_arts, larkspur_clockwork_fair, veridia_intake
- surfaces: `{'compile_surface_gap': 9, 'hybrid_join_gap': 1}`
- lanes: `{'helper_or_query_join_repair': 1, 'scoped_source_surface_repair': 9}`
- purpose: Acquire explicit reasons, source-note rationale, corrections, unresolved questions, claim status, and evidentiary posture.

| Fixture | Row | Verdict | Surface | Question |
| --- | --- | --- | --- | --- |
| `heronvale_arts` | `q022` | `miss` | `compile_surface_gap` | What correction was made to Application C? |
| `larkspur_clockwork_fair` | `q026` | `miss` | `compile_surface_gap` | Why did Thane permit Tobias to repair the Bottled Storm? |
| `larkspur_clockwork_fair` | `q027` | `miss` | `compile_surface_gap` | Why did Thane NOT permit Cassia's Moth Lantern modification? |
| `larkspur_clockwork_fair` | `q034` | `miss` | `compile_surface_gap` | Is Stellan Voss still a suspect in the thread substitution? |
| `fenmore_seedbank` | `q024` | `partial` | `compile_surface_gap` | Has the bur oak lot been deaccessioned yet? |
| `harrowgate_witness_file` | `q039` | `partial` | `compile_surface_gap` | List all unresolved questions at the end of the document. |
| `heronvale_arts` | `q025` | `partial` | `compile_surface_gap` | List all unresolved questions at the end of the document. |
| `larkspur_clockwork_fair` | `q029` | `partial` | `compile_surface_gap` | What is the difference between the Storm repair (permitted) and the Lantern modification (not permitted)? |

### `temporal_status_deadline`

- priority score: `84`
- targets: `9`
- fixtures: `4` - ashgrove_permit, copperfall_deadline_docket, larkspur_clockwork_fair, veridia_intake
- surfaces: `{'compile_surface_gap': 4, 'hybrid_join_gap': 5}`
- lanes: `{'helper_or_query_join_repair': 5, 'scoped_source_surface_repair': 4}`
- purpose: Repair status-at-date, deadline, expiration, grace-period, and interval arithmetic rows.

| Fixture | Row | Verdict | Surface | Question |
| --- | --- | --- | --- | --- |
| `ashgrove_permit` | `q006` | `miss` | `hybrid_join_gap` | What is the adjusted permit expiration after reinstatement? |
| `ashgrove_permit` | `q015` | `miss` | `hybrid_join_gap` | What was the permit status on May 1, 2026? |
| `ashgrove_permit` | `q016` | `miss` | `compile_surface_gap` | What was the permit status on June 10, 2026? |
| `ashgrove_permit` | `q017` | `miss` | `compile_surface_gap` | What was the permit status on October 1, 2026? |
| `copperfall_deadline_docket` | `q024` | `miss` | `compile_surface_gap` | What was the original answer deadline before the motion to dismiss was filed? |
| `veridia_intake` | `q019` | `miss` | `hybrid_join_gap` | After Turn 16 but before Turn 23, should the system commit the lab exhaust fan recertification status? |
| `copperfall_deadline_docket` | `q034` | `partial` | `hybrid_join_gap` | When was the deadline for Orion's reply? |
| `larkspur_clockwork_fair` | `q024` | `partial` | `compile_surface_gap` | Why was Stellan initially suspected of the thread substitution? |

### `authority_document_control`

- priority score: `73`
- targets: `9`
- fixtures: `2` - northbridge_authority_packet, veridia_intake
- surfaces: `{'compile_surface_gap': 9}`
- lanes: `{'scoped_source_surface_repair': 9}`
- purpose: Acquire controlling-document, issuing-authority, notification, parameter, inspection, and priority surfaces.

| Fixture | Row | Verdict | Surface | Question |
| --- | --- | --- | --- | --- |
| `northbridge_authority_packet` | `q007` | `miss` | `compile_surface_gap` | What does the SWIFA Agreement require regarding fire hydrants? |
| `northbridge_authority_packet` | `q010` | `miss` | `compile_surface_gap` | What was the vote on Resolution 2026-14? |
| `northbridge_authority_packet` | `q017` | `miss` | `compile_surface_gap` | How many customers will be affected by the project? |
| `northbridge_authority_packet` | `q020` | `miss` | `compile_surface_gap` | Is there a penalty for missing the Resolution's 18-month timeline? |
| `northbridge_authority_packet` | `q021` | `miss` | `compile_surface_gap` | When the Resolution and SWIFA Agreement conflict, which document controls? |
| `northbridge_authority_packet` | `q026` | `miss` | `compile_surface_gap` | Can SWIFA inspect the project? |
| `northbridge_authority_packet` | `q012` | `partial` | `compile_surface_gap` | Why do the Resolution and SWIFA Agreement specify different pipe diameters? |
| `northbridge_authority_packet` | `q029` | `partial` | `compile_surface_gap` | Who has authority to approve customer interruptions exceeding 8 hours? |

### `entity_role_identity`

- priority score: `63`
- targets: `5`
- fixtures: `4` - greywell_pipeline, harrowgate_witness_file, larkspur_clockwork_fair, veridia_intake
- surfaces: `{'compile_surface_gap': 3, 'hybrid_join_gap': 2}`
- lanes: `{'helper_or_query_join_repair': 2, 'scoped_source_surface_repair': 3}`
- purpose: Acquire identity, person-role, roster, role-holder, and named-actor surfaces.

| Fixture | Row | Verdict | Surface | Question |
| --- | --- | --- | --- | --- |
| `greywell_pipeline` | `q003` | `miss` | `hybrid_join_gap` | Who isolated Segment 4? |
| `harrowgate_witness_file` | `q016` | `miss` | `compile_surface_gap` | Who sits on the Review Panel? |
| `larkspur_clockwork_fair` | `q007` | `miss` | `compile_surface_gap` | Which exhibitor is the youngest? |
| `veridia_intake` | `q013` | `miss` | `compile_surface_gap` | Who originally flagged the parking lot drainage issue? |
| `veridia_intake` | `q001` | `partial` | `hybrid_join_gap` | Who is the facilities director at Veridia Research Campus? |

### `classify_before_repair`

- priority score: `53`
- targets: `4`
- fixtures: `4` - fenmore_seedbank, greywell_pipeline, heronvale_arts, veridia_intake
- surfaces: `{'compile_surface_gap': 3, 'hybrid_join_gap': 1}`
- lanes: `{'helper_or_query_join_repair': 1, 'scoped_source_surface_repair': 3}`
- purpose: Rows that need human or more specific artifact classification before harness work.

| Fixture | Row | Verdict | Surface | Question |
| --- | --- | --- | --- | --- |
| `veridia_intake` | `q007` | `miss` | `compile_surface_gap` | What did the board decide about the ventilation concern in Turn 06? |
| `fenmore_seedbank` | `q019` | `partial` | `compile_surface_gap` | What is the current status of FB-2026-003? |
| `greywell_pipeline` | `q012` | `partial` | `compile_surface_gap` | What is the current operational status of Segment 4? |
| `heronvale_arts` | `q011` | `partial` | `hybrid_join_gap` | Which applications have community impact priority? |

### `quantity_arithmetic_capacity`

- priority score: `42`
- targets: `3`
- fixtures: `3` - fenmore_seedbank, meridian_permit_board, northbridge_authority_packet
- surfaces: `{'compile_surface_gap': 2, 'hybrid_join_gap': 1}`
- lanes: `{'helper_or_query_join_repair': 1, 'scoped_source_surface_repair': 2}`
- purpose: Repair numeric capacity, cost, percentage, threshold, fund-balance, and quantity arithmetic rows.

| Fixture | Row | Verdict | Surface | Question |
| --- | --- | --- | --- | --- |
| `fenmore_seedbank` | `q017` | `miss` | `compile_surface_gap` | What germination rate threshold triggers reclassification to condition D? |
| `meridian_permit_board` | `q007` | `miss` | `compile_surface_gap` | What is the existing use of Lot 12? |
| `northbridge_authority_packet` | `q014` | `partial` | `hybrid_join_gap` | Can the Town afford the additional $400,000? |

### `answer_restraint_surface`

- priority score: `24`
- targets: `2`
- fixtures: `2` - greywell_pipeline, veridia_intake
- surfaces: `{'answer_surface_gap': 2}`
- lanes: `{'answer_surface_repair': 2}`
- purpose: Repair rows whose evidence exists but the answer needs better uncertainty, current-position, or evidentiary wording.

| Fixture | Row | Verdict | Surface | Question |
| --- | --- | --- | --- | --- |
| `greywell_pipeline` | `q025` | `partial` | `answer_surface_gap` | What is the evidentiary status of the unnamed source report about the contractor vehicle? |
| `veridia_intake` | `q009` | `partial` | `answer_surface_gap` | After Turn 13, what is the board's current position on the ventilation concern? |
