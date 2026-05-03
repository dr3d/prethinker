# Cold Baseline Failure Rollup

Generated: 2026-05-03T06:19:04+00:00

This report aggregates existing `cold_unseen` QA artifacts. It does not read
source prose, gold KBs, oracle strategies, or answer-shaped profile material.

## Headline

- Runs: `5`
- Questions: `270`
- Exact / partial / miss: `137` / `39` / `94`
- Exact rate: `0.507`
- Exact+partial rate: `0.652`

## Run Table

| Run | Fixture | Qs | Exact | Partial | Miss | Admitted | Skipped | Facts | Rules | Artifact |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `BLM-001` | black_lantern_maze | 40 | 27 | 7 | 6 | 299 | 28 | 299 | 0 | `tmp\cold_baselines\black_lantern_maze\domain_bootstrap_qa_20260503T060152766469Z_qa_qwen-qwen3-6-35b-a3b.json` |
| `CAL-001` | ledger_at_calders_reach | 110 | 65 | 9 | 36 | 187 | 23 | 180 | 0 | `tmp\cold_baselines\ledger_at_calders_reach\domain_bootstrap_qa_20260503T054553171055Z_qa_qwen-qwen3-6-35b-a3b.json` |
| `RF-001` | ridgeline_fire | 40 | 17 | 10 | 13 | 133 | 27 | 130 | 0 | `tmp\cold_baselines\ridgeline_fire\domain_bootstrap_qa_20260503T051902240724Z_qa_qwen-qwen3-6-35b-a3b.json` |
| `MMM-001` | three_moles_moon_marmalade_machine | 40 | 10 | 8 | 22 | 174 | 10 | 110 | 0 | `tmp\cold_baselines\three_moles\domain_bootstrap_qa_20260503T045525066737Z_qa_qwen-qwen3-6-35b-a3b.json` |
| `V9-001` | veridia9_supply_chain_patent_dispute | 40 | 18 | 5 | 17 | 94 | 13 | 79 | 0 | `tmp\cold_baselines\veridia9\domain_bootstrap_qa_20260503T050519283344Z_qa_qwen-qwen3-6-35b-a3b.json` |

## Cross-Fixture Failure Surfaces

| Surface | Count | General next action |
| --- | ---: | --- |
| Compile | 96 | Improve lens coverage or acquisition passes; do not tune from one fixture alone. |
| Hybrid/Reasoning | 21 | Add or exercise deterministic reasoning helpers, joins, set-difference, aggregation, or temporal substrate. |
| Query | 13 | Improve post-ingestion query support bundles over already admitted rows. |
| Answer | 3 | Tighten answer normalization or judge/verbalization policy without changing ingestion. |

## Fixture Surface Matrix

| Run | Compile | Query | Hybrid/Reasoning | Answer | Uncertain |
| --- | ---: | ---: | ---: | ---: | ---: |
| `BLM-001` | 7 | 0 | 6 | 0 | 0 |
| `CAL-001` | 37 | 6 | 2 | 0 | 0 |
| `RF-001` | 12 | 5 | 6 | 0 | 0 |
| `MMM-001` | 22 | 2 | 4 | 2 | 0 |
| `V9-001` | 18 | 0 | 3 | 1 | 0 |

## Current Read

- Compile gaps dominate the cold set, so the next broad architecture work should
  improve source-surface acquisition and lens coverage rather than only query wording.
- Hybrid/reasoning gaps are the next largest signal and should be attacked with
  deterministic helper substrates, joins, aggregation, and rule-promotion probes.
- Query and answer gaps are real but smaller in this snapshot; they should be
  handled with targeted replay packs after compile/reasoning changes.

## Non-Exact Row Index

This is an index for choosing targeted replays. It is not a prompt source.

| Run | Row | Verdict | Surface | Suggested next action |
| --- | --- | --- | --- | --- |
| `MMM-001` | `q013` | partial | answer_surface_gap | The system retrieved the attribute 'too_shiny' but failed to retrieve or render the specific descriptive phrase 'lit Mina’s ears from inside' because that specific string or its... |
| `MMM-001` | `q019` | partial | answer_surface_gap | The system needs to map the attribute 'too_telltale' with category 'privacy' to the natural language description 'announced every thought in her head'. This is a semantic interp... |
| `V9-001` | `q007` | partial | answer_surface_gap | Add a predicate such as `legal_name(org_aether_bio, 'Aether Bio-Ventures SA (Luxembourg)')` to the KB or update the query plan to join with a name resolution table if one exists... |
| `BLM-001` | `q021` | partial | compile_surface_gap | Retrieve `event_outcome` for the identified test events and `event_timestamp` for those same events to verify the 'negative' status and temporal gap. Additionally, query for any... |
| `BLM-001` | `q022` | miss | compile_surface_gap | Ingest missing person and event data for Pavi Chen/Sin. |
| `BLM-001` | `q029` | miss | compile_surface_gap | The KB lacks the supporting fact for the reference answer and contains contradictory evidence. This is a compile surface gap because the necessary support is absent from the com... |
| `BLM-001` | `q034` | miss | compile_surface_gap | The KB is missing the fact for 'Claim SC-88'. This is a data ingestion or coverage gap, not a query planning or reasoning failure. |
| `BLM-001` | `q035` | miss | compile_surface_gap | Query `claim_content` and `claim_status` predicates to retrieve the specific claim and its adoption status. |
| `BLM-001` | `q036` | miss | compile_surface_gap | The KB appears to lack a direct link between the 'unadopted' claim regarding Kai Morano and a 'finding' that explicitly states the tribunal rejected this specific allegation, or... |
| `BLM-001` | `q037` | miss | compile_surface_gap | Query `claim_status(claim_eli_kest_witness, Status)` and `claim_content(claim_eli_kest_witness, Content)` to verify the status of Eli's witness statement. |
| `CAL-001` | `q002` | miss | compile_surface_gap | Check if 'celia_voss' has a residence fact pointing to 'vesper_house' in the source document, or if a rule exists linking her to that location. |
| `CAL-001` | `q003` | miss | compile_surface_gap | Check if the source document contains a specific fact or rule defining the parent-child relationship between Celia Voss and Leona Voss that was not ingested or indexed correctly. |
| `CAL-001` | `q010` | miss | compile_surface_gap | Check source document for explicit 'spouse' or 'husband' relations between Mireya Sol Elling and Iain Elling. If present, the KB is missing this relation (compile_surface_gap).... |
| `CAL-001` | `q013` | miss | compile_surface_gap | Investigate if 'senior_horticulturist' is an alias for 'manager' or if the role was held by Lina Moor under a different predicate or name not captured in the current inventory.... |
| `CAL-001` | `q015` | miss | compile_surface_gap | Ingest clauses linking June Kestrel to the Old Salt Inn (e.g., `resided_in(june_kestrel, loc_old_salt_inn, ...)` or an event describing her living there). |
| `CAL-001` | `q017` | miss | compile_surface_gap | Ingest familial relationship facts (e.g., sibling_of/2 or brother_of/2) linking mara_elling and iain_elling. |
| `CAL-001` | `q018` | miss | compile_surface_gap | Check source document for parentage facts linking Mireya Sol Elling and Tobin. |
| `CAL-001` | `q019` | miss | compile_surface_gap | Check if the KB contains a `parent_of` or `father_of` predicate that was not ingested or is missing for this specific pair. If the KB relies on inference from `rule_guardian_act... |
| `CAL-001` | `q020` | miss | compile_surface_gap | Ingest familial relationship facts (e.g., `sibling_of(Farid, Nessa)` or `brother_of(Farid, Nessa)`) into the KB. |
| `CAL-001` | `q021` | partial | compile_surface_gap | The KB is missing the explicit marital status relation or a rule linking 'separation agreement' to 'still married' status for the specific date. Without this fact or rule, the s... |
| `CAL-001` | `q024` | partial | compile_surface_gap | Check source document for clauses linking identity discovery to land surveys or drafting errors. |
| `CAL-001` | `q025` | miss | compile_surface_gap | Check source document for clauses linking 'ian_morrow' or 'iain_elling' to medical admission, injury, or confusion events. |
| `CAL-001` | `q026` | miss | compile_surface_gap | The query plan should have utilized the `alias_of/2` predicate to link `quentin_marr` to `quinn_damar`, or queried `knew/2` for the identity revelation event. The failure is tha... |
| `CAL-001` | `q027` | miss | compile_surface_gap | Investigate why the `event_date` predicate did not match the `2021` constant despite the presence of `2021_03` facts, or verify if the KB ingestion failed to persist these speci... |
| `CAL-001` | `q028` | partial | compile_surface_gap | Check source document for clauses linking mireya_sol_elling or evt_mireya_death to saint_arlen_school or evacuation activities. |
| `CAL-001` | `q029` | miss | compile_surface_gap | Ingest facts describing the fuel drum incident and its effect on Ashdown Cottage No. 3. |
| `CAL-001` | `q030` | miss | compile_surface_gap | Check source document for clauses linking the marsh parcel dispute or the avulsion rule to the Ruth Gale storm/flood event. |
| `CAL-001` | `q044` | miss | compile_surface_gap | Check source document for the specific date threshold associated with the `rule_tideglass_charter` condition or the rule definition itself. |
| `CAL-001` | `q055` | miss | compile_surface_gap | Ingest the definition or conditions of the 'avulsion_boundary_rule' into the KB. |
| `CAL-001` | `q058` | miss | compile_surface_gap | Ingest familial relationship facts (e.g., `parent_of(iain_elling, tobin)`) and occupational status facts linking Iain Eling to the 'active harbor worker' condition. |
| `CAL-001` | `q059` | miss | compile_surface_gap | Check source document for Elin Soren's family details and application context. |
| `CAL-001` | `q060` | miss | compile_surface_gap | Ingest facts linking Tobin to the scholarship and facts detailing his household's residence duration and location. |
| `CAL-001` | `q061` | miss | compile_surface_gap | ingest_residence_events |
| `CAL-001` | `q067` | miss | compile_surface_gap | Retrieve `rule_condition` clauses and `temporary_guardian_of` facts to support the logical inference of guardianship termination. |
| `CAL-001` | `q070` | miss | compile_surface_gap | Check source document for facts linking 'red ledger' to 'Iris Vale' or 'Dock 7' fire event. If present, the KB ingestion failed to capture the relation. |
| `CAL-001` | `q071` | miss | compile_surface_gap | Check source document for ledger transfer events involving Iris and Owen Pike. |
| `CAL-001` | `q072` | miss | compile_surface_gap | Check the source document for facts involving 'owen_pike'. If 'owen_pike' is a giver/receiver in the source but missing from the KB, this is a compilation error. If 'owen_pike'... |
| `CAL-001` | `q073` | miss | compile_surface_gap | Ingest clauses linking `obj_red_ledger` to the specific financial and logistical details (sublease payments, invoices, fuel-drum storage). |
| `CAL-001` | `q076` | miss | compile_surface_gap | Check the source document for any mention of the Moth's recovery to determine if the KB is incomplete or if the reference answer is hallucinated. |
| `CAL-001` | `q077` | partial | compile_surface_gap | Check if the source document contains clauses linking Quinn to the Moth (e.g., `boarded(quentin_marr, moth)` or similar) and ingest them if missing. |
| `CAL-001` | `q081` | miss | compile_surface_gap | Add a residence/occupancy predicate (e.g., `resides_at/3`) to the KB schema and ingest relevant facts linking persons to Vesper House with temporal validity. |
| `CAL-001` | `q084` | miss | compile_surface_gap | Check source document for residence facts for Jonas Voss in 2025-2026. |
| `CAL-001` | `q088` | partial | compile_surface_gap | Check if the 'QM consulting presence' is linked to the discovered artifacts via a different predicate (e.g., `owned_by`, `caused_by`, or a specific `related_to` relation) or if... |
| `CAL-001` | `q090` | miss | compile_surface_gap | Check if there is a missing 'knew' or 'believed_by' fact linking Quinn to the boundary rule, or if the 'discovered_by' fact for the rule should have been linked to Quinn. |
| `CAL-001` | `q095` | miss | compile_surface_gap | Verify if the KB supports deriving that 'finding Iain alive' constitutes 'resuming ordinary residence'. If not, the KB is missing the logical link between survival and residence... |
| `CAL-001` | `q096` | miss | compile_surface_gap | Check if the source document contains a clause linking Quinn's paper work to the marsh parcel location or the avulsion line. |
| `CAL-001` | `q097` | miss | compile_surface_gap | Ingest evidence linkage clauses. |
| `RF-001` | `q004` | miss | compile_surface_gap | Ingest facts linking `robert_tanaka` to `ic_certification_level` with value `type_1`. |
| `RF-001` | `q006` | miss | compile_surface_gap | Ingest zoning/land-use facts for 'Mill District' (e.g., `zoning(Mill_District, commercial).`) and WUI boundary facts. |
| `RF-001` | `q007` | miss | compile_surface_gap | Ingest location-entity mapping for 'Mill District' and link it to the relevant evacuation events or standing orders. |
| `RF-001` | `q008` | miss | compile_surface_gap | Ingest missing event data for Mill District or correct the entity name if it is a synonym for an existing district. |
| `RF-001` | `q011` | miss | compile_surface_gap | Check source document for red flag warning cancellation details on June 16. |
| `RF-001` | `q015` | miss | compile_surface_gap | Ingest missing event_timestamp facts for June 16 events (evt_lift_pinecrest, evt_lift_elk, and Tanaka's certification event). |
| `RF-001` | `q017` | partial | compile_surface_gap | Add a lookup table or definition clause mapping 'dual_authorization_ic_and_air_ops' to the specific roles 'Incident Commander' and 'Air Operations Coordinator', or add explicit... |
| `RF-001` | `q030` | miss | compile_surface_gap | The system lacks a structured representation of the aid details (e.g., a `aid_received/3` or `resource_dispatched/3` predicate) linked to the mutual aid events. The current quer... |
| `RF-001` | `q031` | miss | compile_surface_gap | Check source document for '923 acres' and 'June 17' containment data; ingest if missing. |
| `RF-001` | `q032` | miss | compile_surface_gap | Ingest the timestamp for evt_review_convened into event_timestamp/2. |
| `RF-001` | `q034` | miss | compile_surface_gap | Ingest member appointment facts and affiliation/origin data for board members. |
| `RF-001` | `q039` | partial | compile_surface_gap | Check source document for Elk Meadow evacuation order lifting timestamp. |
| `MMM-001` | `q002` | miss | compile_surface_gap | Investigate if the descriptive location of the kettle_house is encoded in a different predicate (e.g., `located_at(kettle_house, ...)` or a `says/3` statement describing it) or... |
| `MMM-001` | `q004` | miss | compile_surface_gap | Ingest rules or facts defining 'outsider' status or parentage relationships. |
| `MMM-001` | `q005` | miss | compile_surface_gap | Ingest or verify facts defining the kinship between Mina Moonbutton and the Burrow Mole characters. |
| `MMM-001` | `q007` | miss | compile_surface_gap | Check source document for 'counting doorbells', 'chasing a backward frog', and 'listening to a squeaking fence' to verify if they are present but missing from the KB. |
| `MMM-001` | `q008` | partial | compile_surface_gap | Check source document for clauses linking Moles to the creation of marmalade. |
| `MMM-001` | `q009` | miss | compile_surface_gap | Check source document for 'contains' or 'ingredient' facts. |
| `MMM-001` | `q010` | miss | compile_surface_gap | Check source document for causal rules linking Moles' departure to fog-leaves. |
| `MMM-001` | `q011` | partial | compile_surface_gap | Ingest the specific narrative clause linking brightness to the 'shine through whiskers' detail and the causal link to the delay. |
| `MMM-001` | `q016` | miss | compile_surface_gap | Check source document for ingestion of 'beetle-keys' facts or rules linking them to Mina's actions. |
| `MMM-001` | `q017` | miss | compile_surface_gap | Check if the KB contains a clause linking the key-swallowing event to the humming event or if the `says` fact is misattributed to the wrong event ID. |
| `MMM-001` | `q020` | miss | compile_surface_gap | Check source document for facts about 'little_nib_mole_cap' and 'secret' or 'privacy' attributes. |
| `MMM-001` | `q022` | miss | compile_surface_gap | Check source document for events involving 'pickled_thunder' or 'knock down'. |
| `MMM-001` | `q023` | miss | compile_surface_gap | Check source document for 'shelf' and 'jump' events or statements. |
| `MMM-001` | `q025` | partial | compile_surface_gap | Check source document for explicit facts linking the middle cart to 'receipt', 'permission slip', and 'explanation', or if 'forms' is the sole supported element. |
| `MMM-001` | `q026` | miss | compile_surface_gap | Add a predicate such as `accepted/2` or `accepted_by/2` to the KB schema and ingest the corresponding facts from the source document. |
| `MMM-001` | `q027` | miss | compile_surface_gap | Check the source document for facts defining Mina's role as 'Postmistress of the Moon' and ingest them into the KB. |
| `MMM-001` | `q028` | miss | compile_surface_gap | Ingest the clause defining the purpose/design of 'little_nib_mole_cart' (e.g., 'means(little_nib_mole_cart, carrying_turnips)' or similar) to support the reference answer. |
| `MMM-001` | `q033` | miss | compile_surface_gap | Ingest physical state predicates (e.g., `has_appearance/2`, `wearing/2`, `holding/2`) and possession facts linking Mina to 'pickled thunder' and 'humming'. |
| `MMM-001` | `q034` | miss | compile_surface_gap | Check if the source document contains a rule mapping 'says' or 'realizes' to 'learns' for this character, or if the ingestion process failed to ingest `learns(little_nib_mole, .... |
| `MMM-001` | `q036` | miss | compile_surface_gap | Check if the source document contains explicit statements about the number of keys removed. If so, the KB ingestion failed to capture quantitative facts or countable object inst... |
| `MMM-001` | `q037` | miss | compile_surface_gap | Ingest source text segments describing the physical attributes of keys or the specific incident involving a tooth mark. |
