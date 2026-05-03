# Cold Baseline Failure Rollup

Generated: 2026-05-03T15:32:07+00:00

This report aggregates existing `cold_unseen` QA artifacts. It does not read
source prose, gold KBs, oracle strategies, or answer-shaped profile material.

## Headline

- Runs: `7`
- Questions: `350`
- Exact / partial / miss: `189` / `58` / `103`
- Exact rate: `0.540`
- Exact+partial rate: `0.706`

## Run Table

| Run | Fixture | Qs | Exact | Partial | Miss | Admitted | Skipped | Facts | Rules | Artifact |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `AG-001` | avalon_grant_committee | 40 | 25 | 12 | 3 | 114 | 6 | 109 | 0 | `tmp\cold_baselines\avalon_grant_committee\domain_bootstrap_qa_20260503T143610001875Z_qa_qwen-qwen3-6-35b-a3b.json` |
| `BLM-001` | black_lantern_maze | 40 | 27 | 7 | 6 | 299 | 28 | 299 | 0 | `tmp\cold_baselines\black_lantern_maze\domain_bootstrap_qa_20260503T060152766469Z_qa_qwen-qwen3-6-35b-a3b.json` |
| `DL-001` | dulse_ledger | 40 | 27 | 7 | 6 | 70 | 21 | 52 | 0 | `tmp\cold_baselines\dulse_ledger\domain_bootstrap_qa_20260503T153106149780Z_qa_qwen-qwen3-6-35b-a3b.json` |
| `CAL-001` | ledger_at_calders_reach | 110 | 65 | 9 | 36 | 187 | 23 | 180 | 0 | `tmp\cold_baselines\ledger_at_calders_reach\domain_bootstrap_qa_20260503T054553171055Z_qa_qwen-qwen3-6-35b-a3b.json` |
| `RF-001` | ridgeline_fire | 40 | 17 | 10 | 13 | 133 | 27 | 130 | 0 | `tmp\cold_baselines\ridgeline_fire\domain_bootstrap_qa_20260503T051902240724Z_qa_qwen-qwen3-6-35b-a3b.json` |
| `MMM-001` | three_moles_moon_marmalade_machine | 40 | 10 | 8 | 22 | 174 | 10 | 110 | 0 | `tmp\cold_baselines\three_moles\domain_bootstrap_qa_20260503T045525066737Z_qa_qwen-qwen3-6-35b-a3b.json` |
| `V9-001` | veridia9_supply_chain_patent_dispute | 40 | 18 | 5 | 17 | 94 | 13 | 79 | 0 | `tmp\cold_baselines\veridia9\domain_bootstrap_qa_20260503T050519283344Z_qa_qwen-qwen3-6-35b-a3b.json` |

## Cross-Fixture Failure Surfaces

| Surface | Count | General next action |
| --- | ---: | --- |
| Compile | 116 | Improve lens coverage or acquisition passes; do not tune from one fixture alone. |
| Hybrid/Reasoning | 27 | Add or exercise deterministic reasoning helpers, joins, set-difference, aggregation, or temporal substrate. |
| Query | 15 | Improve post-ingestion query support bundles over already admitted rows. |
| Answer | 3 | Tighten answer normalization or judge/verbalization policy without changing ingestion. |

## Fixture Surface Matrix

| Run | Compile | Query | Hybrid/Reasoning | Answer | Uncertain |
| --- | ---: | ---: | ---: | ---: | ---: |
| `AG-001` | 11 | 2 | 2 | 0 | 0 |
| `BLM-001` | 7 | 0 | 6 | 0 | 0 |
| `DL-001` | 9 | 0 | 4 | 0 | 0 |
| `CAL-001` | 37 | 6 | 2 | 0 | 0 |
| `RF-001` | 12 | 5 | 6 | 0 | 0 |
| `MMM-001` | 22 | 2 | 4 | 2 | 0 |
| `V9-001` | 18 | 0 | 3 | 1 | 0 |

## Non-Exact Query Evidence Return

This is a post-run support proxy. It counts whether the generated Prolog
queries returned rows for non-exact QA items. Returned rows are not proof
of correctness; they only show that the query path found some symbolic
surface to work with.

| Evidence state | Count |
| --- | ---: |
| `rows_returned` | 92 |
| `partial_rows_returned` | 66 |
| `no_queries` | 3 |

| Surface | Rows returned | No rows returned | Partial rows returned | No queries |
| --- | ---: | ---: | ---: | ---: |
| Compile | 66 | 0 | 47 | 3 |
| Hybrid/Reasoning | 17 | 0 | 10 | 0 |
| Query | 6 | 0 | 9 | 0 |
| Answer | 3 | 0 | 0 | 0 |
| Uncertain | 0 | 0 | 0 | 0 |

## Current Read

- Compile gaps dominate the cold set, so the next broad architecture work should
  improve source-surface acquisition and lens coverage rather than only query wording.
- Hybrid/reasoning gaps are the next largest signal and should be attacked with
  deterministic helper substrates, joins, aggregation, and rule-promotion probes.
- Query and answer gaps are real but smaller in this snapshot; they should be
  handled with targeted replay packs after compile/reasoning changes.
- Non-exact rows with returned query evidence are especially useful for
  separating query/answer/reasoning problems from pure acquisition gaps.

## Non-Exact Row Index

This is an index for choosing targeted replays. It is not a prompt source.

| Run | Row | Verdict | Surface | Evidence | Suggested next action |
| --- | --- | --- | --- | --- | --- |
| `MMM-001` | `q013` | partial | answer_surface_gap | `rows_returned`/10 rows | The system retrieved the attribute 'too_shiny' but failed to retrieve or render the specific descriptive phrase 'lit Mina’s ears from inside' because that specific string or its... |
| `MMM-001` | `q019` | partial | answer_surface_gap | `rows_returned`/1 rows | The system needs to map the attribute 'too_telltale' with category 'privacy' to the natural language description 'announced every thought in her head'. This is a semantic interp... |
| `V9-001` | `q007` | partial | answer_surface_gap | `rows_returned`/1 rows | Add a predicate such as `legal_name(org_aether_bio, 'Aether Bio-Ventures SA (Luxembourg)')` to the KB or update the query plan to join with a name resolution table if one exists... |
| `AG-001` | `q003` | partial | compile_surface_gap | `rows_returned`/4 rows | Retrieve `corrected_field` and `original_value` for the NYA correction to verify the 12,000/40,000 split. Investigate if 'committee disagreement' is encoded in `basis_finding` o... |
| `AG-001` | `q006` | partial | compile_surface_gap | `partial_rows_returned`/6 rows | Check if the KB contains a `revised_amount` predicate or a `budget_revision` record linking to the exclusion of specific line items (e.g., food-truck bazaar) and the new total (... |
| `AG-001` | `q007` | partial | compile_surface_gap | `partial_rows_returned`/10 rows | Check the source document for any specific project component details for anya_petrov that might map to an ineligible category or a 'food-truck bazaar' component, or verify if th... |
| `AG-001` | `q008` | partial | compile_surface_gap | `rows_returned`/11 rows | Ingest the revised requested amount for app4 or the rule linking correction IDs to specific field updates. |
| `AG-001` | `q010` | miss | compile_surface_gap | `rows_returned`/3 rows | Ingest the fact linking Lucia Bianchi to Sunrise Community Land Trust (e.g., `board_member(lucia_bianchi, sunrise_community_land_trust).`) and ensure the rule application logic... |
| `AG-001` | `q014` | partial | compile_surface_gap | `partial_rows_returned`/6 rows | Ingest the missing prior grant history fact for sunrise_community_land_trust (app5) for FY2024 and ensure the eligibility logic correctly evaluates the 'awarded' vs 'disbursed'... |
| `AG-001` | `q025` | partial | compile_surface_gap | `partial_rows_returned`/6 rows | Retrieve `original_value` and `corrected_field` for `corr_petrov_1` and `requested_amount` for `anya_petrov` to enable the numerical comparison required by the reference answer. |
| `AG-001` | `q026` | miss | compile_surface_gap | `rows_returned`/3 rows | Check if the KB contains any interpretation records, meeting minutes, or basis findings specifically linked to Rule 3 or mentioning 'Worthington'. If absent, the KB is incomplet... |
| `AG-001` | `q029` | partial | compile_surface_gap | `partial_rows_returned`/5 rows | The system needs to query the rule conditions for `rule_id(r4, project_category)` to extract the `eligible_categories` value, rather than querying the `project_category/2` predi... |
| `AG-001` | `q030` | miss | compile_surface_gap | `partial_rows_returned`/6 rows | Check if the KB ingestion missed multi-category mappings for anya_petrov or if the reference answer relies on external knowledge not present in the symbolic KB. |
| `AG-001` | `q038` | partial | compile_surface_gap | `partial_rows_returned`/7 rows | Check source document for application submission date, conditional approval vote date, and specific grant award amount. |
| `BLM-001` | `q021` | partial | compile_surface_gap | `rows_returned`/20 rows | Retrieve `event_outcome` for the identified test events and `event_timestamp` for those same events to verify the 'negative' status and temporal gap. Additionally, query for any... |
| `BLM-001` | `q022` | miss | compile_surface_gap | `no_queries`/0 rows | Ingest missing person and event data for Pavi Chen/Sin. |
| `BLM-001` | `q029` | miss | compile_surface_gap | `rows_returned`/22 rows | The KB lacks the supporting fact for the reference answer and contains contradictory evidence. This is a compile surface gap because the necessary support is absent from the com... |
| `BLM-001` | `q034` | miss | compile_surface_gap | `rows_returned`/36 rows | The KB is missing the fact for 'Claim SC-88'. This is a data ingestion or coverage gap, not a query planning or reasoning failure. |
| `BLM-001` | `q035` | miss | compile_surface_gap | `rows_returned`/22 rows | Query `claim_content` and `claim_status` predicates to retrieve the specific claim and its adoption status. |
| `BLM-001` | `q036` | miss | compile_surface_gap | `rows_returned`/22 rows | The KB appears to lack a direct link between the 'unadopted' claim regarding Kai Morano and a 'finding' that explicitly states the tribunal rejected this specific allegation, or... |
| `BLM-001` | `q037` | miss | compile_surface_gap | `rows_returned`/22 rows | Query `claim_status(claim_eli_kest_witness, Status)` and `claim_content(claim_eli_kest_witness, Content)` to verify the status of Eli's witness statement. |
| `DL-001` | `q009` | miss | compile_surface_gap | `rows_returned`/1 rows | Check if the due date is stored in a different predicate (e.g., `due_date/3` or within `salt_provision/4` if it tracks terms) or if `debt_status/4` is intended to store status f... |
| `DL-001` | `q014` | partial | compile_surface_gap | `rows_returned`/17 rows | Check ingestion logs for clauses related to 'storm_exception' or 'custom_exception' negation. If absent, this is a KB coverage gap. |
| `DL-001` | `q019` | miss | compile_surface_gap | `partial_rows_returned`/5 rows | Ingest restitution/return facts for Entry 7 or rules deriving them from the apprentice_exception violation. |
| `DL-001` | `q020` | miss | compile_surface_gap | `rows_returned`/4 rows | Ingest restitution/return obligations rules and facts linking Entry 3 to the specific return duties of Yara Duvall and Luca Cole. |
| `DL-001` | `q028` | miss | compile_surface_gap | `partial_rows_returned`/20 rows | ingest_general_trade_predicate |
| `DL-001` | `q030` | miss | compile_surface_gap | `rows_returned`/1 rows | Check for predicates like 'clerk_disclaimer/2' or 'belief_status/2' that encode the epistemic limitation of the observation. |
| `DL-001` | `q032` | partial | compile_surface_gap | `partial_rows_returned`/13 rows | Ingest quantity facts for Entry 1 and the rule definition for counsel_custom threshold logic. |
| `DL-001` | `q036` | miss | compile_surface_gap | `partial_rows_returned`/14 rows | The KB lacks the necessary meta-data or negative facts to support the reference answer. This is a knowledge gap in the compiled inventory. |
| `DL-001` | `q040` | partial | compile_surface_gap | `partial_rows_returned`/7 rows | Investigate if the source document contains explicit statements linking Entry 1 to the Counsel Custom and the execution status of Entry 3's restitution. If these facts exist in... |
| `CAL-001` | `q002` | miss | compile_surface_gap | `partial_rows_returned`/27 rows | Check if 'celia_voss' has a residence fact pointing to 'vesper_house' in the source document, or if a rule exists linking her to that location. |
| `CAL-001` | `q003` | miss | compile_surface_gap | `rows_returned`/27 rows | Check if the source document contains a specific fact or rule defining the parent-child relationship between Celia Voss and Leona Voss that was not ingested or indexed correctly. |
| `CAL-001` | `q010` | miss | compile_surface_gap | `rows_returned`/20 rows | Check source document for explicit 'spouse' or 'husband' relations between Mireya Sol Elling and Iain Elling. If present, the KB is missing this relation (compile_surface_gap).... |
| `CAL-001` | `q013` | miss | compile_surface_gap | `partial_rows_returned`/19 rows | Investigate if 'senior_horticulturist' is an alias for 'manager' or if the role was held by Lina Moor under a different predicate or name not captured in the current inventory.... |
| `CAL-001` | `q015` | miss | compile_surface_gap | `no_queries`/0 rows | Ingest clauses linking June Kestrel to the Old Salt Inn (e.g., `resided_in(june_kestrel, loc_old_salt_inn, ...)` or an event describing her living there). |
| `CAL-001` | `q017` | miss | compile_surface_gap | `partial_rows_returned`/79 rows | Ingest familial relationship facts (e.g., sibling_of/2 or brother_of/2) linking mara_elling and iain_elling. |
| `CAL-001` | `q018` | miss | compile_surface_gap | `partial_rows_returned`/1 rows | Check source document for parentage facts linking Mireya Sol Elling and Tobin. |
| `CAL-001` | `q019` | miss | compile_surface_gap | `partial_rows_returned`/1 rows | Check if the KB contains a `parent_of` or `father_of` predicate that was not ingested or is missing for this specific pair. If the KB relies on inference from `rule_guardian_act... |
| `CAL-001` | `q020` | miss | compile_surface_gap | `rows_returned`/44 rows | Ingest familial relationship facts (e.g., `sibling_of(Farid, Nessa)` or `brother_of(Farid, Nessa)`) into the KB. |
| `CAL-001` | `q021` | partial | compile_surface_gap | `rows_returned`/20 rows | The KB is missing the explicit marital status relation or a rule linking 'separation agreement' to 'still married' status for the specific date. Without this fact or rule, the s... |
| `CAL-001` | `q024` | partial | compile_surface_gap | `rows_returned`/3 rows | Check source document for clauses linking identity discovery to land surveys or drafting errors. |
| `CAL-001` | `q025` | miss | compile_surface_gap | `rows_returned`/2 rows | Check source document for clauses linking 'ian_morrow' or 'iain_elling' to medical admission, injury, or confusion events. |
| `CAL-001` | `q026` | miss | compile_surface_gap | `partial_rows_returned`/31 rows | The query plan should have utilized the `alias_of/2` predicate to link `quentin_marr` to `quinn_damar`, or queried `knew/2` for the identity revelation event. The failure is tha... |
| `CAL-001` | `q027` | miss | compile_surface_gap | `partial_rows_returned`/25 rows | Investigate why the `event_date` predicate did not match the `2021` constant despite the presence of `2021_03` facts, or verify if the KB ingestion failed to persist these speci... |
| `CAL-001` | `q028` | partial | compile_surface_gap | `partial_rows_returned`/5 rows | Check source document for clauses linking mireya_sol_elling or evt_mireya_death to saint_arlen_school or evacuation activities. |
| `CAL-001` | `q029` | miss | compile_surface_gap | `partial_rows_returned`/25 rows | Ingest facts describing the fuel drum incident and its effect on Ashdown Cottage No. 3. |
| `CAL-001` | `q030` | miss | compile_surface_gap | `partial_rows_returned`/8 rows | Check source document for clauses linking the marsh parcel dispute or the avulsion rule to the Ruth Gale storm/flood event. |
| `CAL-001` | `q044` | miss | compile_surface_gap | `partial_rows_returned`/6 rows | Check source document for the specific date threshold associated with the `rule_tideglass_charter` condition or the rule definition itself. |
| `CAL-001` | `q055` | miss | compile_surface_gap | `partial_rows_returned`/6 rows | Ingest the definition or conditions of the 'avulsion_boundary_rule' into the KB. |
| `CAL-001` | `q058` | miss | compile_surface_gap | `rows_returned`/19 rows | Ingest familial relationship facts (e.g., `parent_of(iain_elling, tobin)`) and occupational status facts linking Iain Eling to the 'active harbor worker' condition. |
| `CAL-001` | `q059` | miss | compile_surface_gap | `partial_rows_returned`/62 rows | Check source document for Elin Soren's family details and application context. |
| `CAL-001` | `q060` | miss | compile_surface_gap | `rows_returned`/44 rows | Ingest facts linking Tobin to the scholarship and facts detailing his household's residence duration and location. |
| `CAL-001` | `q061` | miss | compile_surface_gap | `partial_rows_returned`/79 rows | ingest_residence_events |
| `CAL-001` | `q067` | miss | compile_surface_gap | `rows_returned`/25 rows | Retrieve `rule_condition` clauses and `temporary_guardian_of` facts to support the logical inference of guardianship termination. |
| `CAL-001` | `q070` | miss | compile_surface_gap | `partial_rows_returned`/26 rows | Check source document for facts linking 'red ledger' to 'Iris Vale' or 'Dock 7' fire event. If present, the KB ingestion failed to capture the relation. |
| `CAL-001` | `q071` | miss | compile_surface_gap | `partial_rows_returned`/14 rows | Check source document for ledger transfer events involving Iris and Owen Pike. |
| `CAL-001` | `q072` | miss | compile_surface_gap | `partial_rows_returned`/31 rows | Check the source document for facts involving 'owen_pike'. If 'owen_pike' is a giver/receiver in the source but missing from the KB, this is a compilation error. If 'owen_pike'... |
| `CAL-001` | `q073` | miss | compile_surface_gap | `rows_returned`/3 rows | Ingest clauses linking `obj_red_ledger` to the specific financial and logistical details (sublease payments, invoices, fuel-drum storage). |
| `CAL-001` | `q076` | miss | compile_surface_gap | `partial_rows_returned`/44 rows | Check the source document for any mention of the Moth's recovery to determine if the KB is incomplete or if the reference answer is hallucinated. |
| `CAL-001` | `q077` | partial | compile_surface_gap | `rows_returned`/3 rows | Check if the source document contains clauses linking Quinn to the Moth (e.g., `boarded(quentin_marr, moth)` or similar) and ingest them if missing. |
| `CAL-001` | `q081` | miss | compile_surface_gap | `no_queries`/0 rows | Add a residence/occupancy predicate (e.g., `resides_at/3`) to the KB schema and ingest relevant facts linking persons to Vesper House with temporal validity. |
| `CAL-001` | `q084` | miss | compile_surface_gap | `partial_rows_returned`/49 rows | Check source document for residence facts for Jonas Voss in 2025-2026. |
| `CAL-001` | `q088` | partial | compile_surface_gap | `partial_rows_returned`/3 rows | Check if the 'QM consulting presence' is linked to the discovered artifacts via a different predicate (e.g., `owned_by`, `caused_by`, or a specific `related_to` relation) or if... |
| `CAL-001` | `q090` | miss | compile_surface_gap | `rows_returned`/5 rows | Check if there is a missing 'knew' or 'believed_by' fact linking Quinn to the boundary rule, or if the 'discovered_by' fact for the rule should have been linked to Quinn. |
| `CAL-001` | `q095` | miss | compile_surface_gap | `partial_rows_returned`/6 rows | Verify if the KB supports deriving that 'finding Iain alive' constitutes 'resuming ordinary residence'. If not, the KB is missing the logical link between survival and residence... |
| `CAL-001` | `q096` | miss | compile_surface_gap | `rows_returned`/3 rows | Check if the source document contains a clause linking Quinn's paper work to the marsh parcel location or the avulsion line. |
| `CAL-001` | `q097` | miss | compile_surface_gap | `rows_returned`/5 rows | Ingest evidence linkage clauses. |
| `RF-001` | `q004` | miss | compile_surface_gap | `rows_returned`/4 rows | Ingest facts linking `robert_tanaka` to `ic_certification_level` with value `type_1`. |
| `RF-001` | `q006` | miss | compile_surface_gap | `rows_returned`/1 rows | Ingest zoning/land-use facts for 'Mill District' (e.g., `zoning(Mill_District, commercial).`) and WUI boundary facts. |
| `RF-001` | `q007` | miss | compile_surface_gap | `rows_returned`/70 rows | Ingest location-entity mapping for 'Mill District' and link it to the relevant evacuation events or standing orders. |
| `RF-001` | `q008` | miss | compile_surface_gap | `rows_returned`/91 rows | Ingest missing event data for Mill District or correct the entity name if it is a synonym for an existing district. |
| `RF-001` | `q011` | miss | compile_surface_gap | `partial_rows_returned`/97 rows | Check source document for red flag warning cancellation details on June 16. |
| `RF-001` | `q015` | miss | compile_surface_gap | `partial_rows_returned`/111 rows | Ingest missing event_timestamp facts for June 16 events (evt_lift_pinecrest, evt_lift_elk, and Tanaka's certification event). |
| `RF-001` | `q017` | partial | compile_surface_gap | `rows_returned`/2 rows | Add a lookup table or definition clause mapping 'dual_authorization_ic_and_air_ops' to the specific roles 'Incident Commander' and 'Air Operations Coordinator', or add explicit... |
| `RF-001` | `q030` | miss | compile_surface_gap | `rows_returned`/8 rows | The system lacks a structured representation of the aid details (e.g., a `aid_received/3` or `resource_dispatched/3` predicate) linked to the mutual aid events. The current quer... |
| `RF-001` | `q031` | miss | compile_surface_gap | `partial_rows_returned`/45 rows | Check source document for '923 acres' and 'June 17' containment data; ingest if missing. |
| `RF-001` | `q032` | miss | compile_surface_gap | `partial_rows_returned`/79 rows | Ingest the timestamp for evt_review_convened into event_timestamp/2. |
| `RF-001` | `q034` | miss | compile_surface_gap | `rows_returned`/2 rows | Ingest member appointment facts and affiliation/origin data for board members. |
| `RF-001` | `q039` | partial | compile_surface_gap | `partial_rows_returned`/67 rows | Check source document for Elk Meadow evacuation order lifting timestamp. |
| `MMM-001` | `q002` | miss | compile_surface_gap | `rows_returned`/1 rows | Investigate if the descriptive location of the kettle_house is encoded in a different predicate (e.g., `located_at(kettle_house, ...)` or a `says/3` statement describing it) or... |
