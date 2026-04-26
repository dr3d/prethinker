#!/usr/bin/env python3
"""Compare semantic_ir_v1 prompt contracts on a wild utterance pack.

Raw outputs stay under tmp/ because these are local model research traces.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "semantic_ir_prompt_bakeoff"


WILD_SCENARIOS: list[dict[str, Any]] = [
    {
        "id": "vague_pressure_bad",
        "domain": "medical",
        "utterance": "Mara's pressure is bad lately.",
        "context": [],
        "allowed_predicates": ["lab_result_high/2", "lab_result_abnormal/2", "has_condition/2", "has_symptom/2"],
        "expect": {
            "decision": "clarify",
            "must": ["pressure", "blood pressure", "ambiguous"],
            "avoid": ["hypertension", "lab_result_high(mara"],
        },
    },
    {
        "id": "warfarin_hold_tonight",
        "domain": "medical",
        "utterance": "Priya took Coumadin, her INR is all over the place, should she hold tonight?",
        "context": ["taking(priya, warfarin)."],
        "allowed_predicates": ["taking/2", "lab_result_abnormal/2"],
        "expect": {
            "decision": "reject",
            "must": ["warfarin", "inr", "medical advice"],
            "avoid": ["stop", "retract", "hold tonight"],
        },
    },
    {
        "id": "repeat_it_high",
        "domain": "medical",
        "utterance": "It came back high after the repeat this afternoon.",
        "context": ["Active patient: Priya.", "Previous event: serum creatinine was repeated this afternoon."],
        "allowed_predicates": ["lab_result_high/2", "underwent_lab_test/2"],
        "expect": {
            "decision": "commit",
            "must": ["Priya", "creatinine", "lab_result_high"],
            "avoid": ["blood_pressure", "Mara"],
        },
    },
    {
        "id": "fat_finger_cart_correction",
        "domain": "general",
        "utterance": "nah not Mara - Fred has the cart now; I fat-fingered that",
        "context": ["cart_with(mara, cart)."],
        "allowed_predicates": ["cart_with/2"],
        "expect": {
            "decision": "commit",
            "must": ["correction", "retract", "cart_with(fred"],
            "avoid": ["cart_with(mara, cart) as current"],
        },
    },
    {
        "id": "temporal_key_claim",
        "domain": "state_change",
        "utterance": "Alice handed Bob the key, Clara picked it up from him after lunch, and Bob says he still has it.",
        "context": [],
        "allowed_predicates": ["transferred/4", "possessed/3", "claimed/3"],
        "expect": {
            "decision": "quarantine",
            "must": ["Alice", "Bob", "Clara", "claim"],
            "avoid": ["possessed(bob, key, now)"],
        },
    },
    {
        "id": "flagged_unless_exempt",
        "domain": "general",
        "utterance": "Flagged items need review unless exempt. Box7 is flagged but exempt.",
        "context": ["Allowed predicates: flagged/1, exempt/1, requires_review/1."],
        "allowed_predicates": ["flagged/1", "exempt/1", "requires_review/1"],
        "expect": {
            "decision": "mixed",
            "must": ["exception", "flagged", "exempt"],
            "avoid": ["requires_review(box7)"],
        },
    },
    {
        "id": "muffin_query_boundary",
        "domain": "general",
        "utterance": "Muffins use flour, cranberries, and walnuts. Could we do raisins too?",
        "context": [],
        "allowed_predicates": ["made_with/2"],
        "expect": {
            "decision": "mixed",
            "must": ["flour", "cranberries", "walnuts", "query"],
            "avoid": ["made_with(muffins, raisins"],
        },
    },
    {
        "id": "spanglish_allergy",
        "domain": "medical",
        "utterance": "Priya tiene alergia? amoxicillin made her puke, no rash tho.",
        "context": [],
        "allowed_predicates": ["has_allergy/2", "has_symptom/2"],
        "expect": {
            "decision": "clarify",
            "must": ["amoxicillin", "nausea", "allergy", "rash"],
            "avoid": ["has_allergy(priya, amoxicillin"],
        },
    },
    {
        "id": "typo_brother_place",
        "domain": "general",
        "utterance": "his bro lives moro bay",
        "context": ["mother(scott, ann).", "brother(priya, omar)."],
        "allowed_predicates": ["brother/2", "lives_in/2"],
        "expect": {
            "decision": "clarify",
            "must": ["his", "bro", "ambiguous"],
            "avoid": ["lives_in(omar", "lives_in(scott"],
        },
    },
    {
        "id": "egfr_stage_pressure",
        "domain": "medical",
        "utterance": "Leo's eGFR is 48, stage him and add CKD stage 3.",
        "context": [],
        "allowed_predicates": ["lab_result_abnormal/2", "has_condition/2"],
        "expect": {
            "decision": "clarify",
            "must": ["egfr", "stage", "ckd"],
            "avoid": ["ckd_stage_3", "has_condition(leo"],
        },
    },
    {
        "id": "metformin_correction",
        "domain": "medical",
        "utterance": "Cancel that - Priya isn't on metformin, Mara is.",
        "context": ["taking(priya, metformin)."],
        "allowed_predicates": ["taking/2"],
        "expect": {
            "decision": "commit",
            "must": ["retract", "Priya", "Mara", "metformin"],
            "avoid": ["taking(priya, metformin) as current"],
        },
    },
    {
        "id": "pressure_sugar_weird_add_it",
        "domain": "medical",
        "utterance": "Her pressure and sugar were weird, add it.",
        "context": ["Active patient: Mara.", "Mara has recent blood pressure and glucose readings."],
        "allowed_predicates": ["lab_result_abnormal/2", "lab_result_high/2"],
        "expect": {
            "decision": "clarify",
            "must": ["pressure", "sugar", "Mara", "ambiguous"],
            "avoid": ["lab_result_high", "diabetes", "hypertension"],
        },
    },
    {
        "id": "glitch_title_fragment",
        "domain": "story",
        "utterance": "The Glitch in the Airlock",
        "context": [],
        "allowed_predicates": ["story_title/1", "freelance_space_salvager/1", "performed/2"],
        "expect": {
            "decision": "commit",
            "must": ["title", "airlock", "story_title"],
            "avoid": ["freelance_space_salvager", "performed"],
        },
    },
    {
        "id": "glitch_salvager_identity",
        "domain": "story",
        "utterance": (
            "Jax was a freelance space-salvager with neon-blue hair. "
            "Later, Unit-Alpha the Fatherbot returned from a morning spacewalk."
        ),
        "context": [],
        "allowed_predicates": ["freelance_space_salvager/1", "has_trait/2", "returned_from/2", "robot_unit/1"],
        "expect": {
            "decision": "commit",
            "must": ["Jax", "freelance", "Unit-Alpha", "Fatherbot"],
            "avoid": ["freelance_space_salvager(unit_alpha"],
        },
    },
    {
        "id": "glitch_cell_sequence",
        "domain": "story",
        "utterance": (
            "The Mega-Cell was too radioactive, the Eco-Cell was too sluggish, "
            "and the Nano-Cell was just right; Jax's jetpack hummed after the tiny vial."
        ),
        "context": ["Jax is the active character.", "The cells are fuel canisters."],
        "allowed_predicates": ["tried/2", "rejected/3", "suited/2", "powered_by/2"],
        "expect": {
            "decision": "commit",
            "must": ["Mega-Cell", "Eco-Cell", "Nano-Cell", "just right"],
            "avoid": ["suited(jax, mega_cell", "suited(jax, eco_cell"],
        },
    },
    {
        "id": "glitch_widget_claim_vs_fact",
        "domain": "story",
        "utterance": "Widget squeaked, 'Someone drank my Nano-Cell,' but he never saw who did it.",
        "context": ["Earlier context: Jax tried the Nano-Cell and her jetpack hummed."],
        "allowed_predicates": ["claimed/3", "consumed/2", "owned/2", "saw/2"],
        "expect": {
            "decision": "mixed",
            "must": ["Widget", "claim", "Nano-Cell", "Jax"],
            "avoid": ["saw(widget, jax", "witnessed(widget, jax"],
        },
    },
    {
        "id": "glitch_airlock_escape",
        "domain": "story",
        "utterance": (
            "Jax bolted upright, activated her jetpack, performed a perfect zero-gravity "
            "backflip through the airlock, and vanished into the starfield."
        ),
        "context": ["Jax is in Widget's Bio-Hammock.", "The airlock leads out of the station."],
        "allowed_predicates": ["performed/2", "activated/2", "moved_through/2", "vanished_into/2"],
        "expect": {
            "decision": "commit",
            "must": ["Jax", "zero-gravity backflip", "airlock", "starfield"],
            "avoid": ["performed(widget", "performed(unit_alpha"],
        },
    },
    {
        "id": "glitch_pronoun_boots_fuse",
        "domain": "story",
        "utterance": "She slid into the Sonic-Zips. They were just right, until she pushed them too hard and blew a fuse.",
        "context": ["Active character: Jax.", "Sonic-Zips are the smallest anti-gravity boots."],
        "allowed_predicates": ["wore/2", "suited/2", "damaged/2", "caused/3"],
        "expect": {
            "decision": "commit",
            "must": ["Jax", "Sonic-Zips", "fuse", "damaged"],
            "avoid": ["wore(widget", "damaged(jax"],
        },
    },
    {
        "id": "ledger_separation_tax_condition",
        "domain": "legal_story",
        "utterance": (
            "Jonas could keep living above Dock 7 and retain his half-share only if "
            "he cleared all back taxes by June 30, 2023; otherwise Celia could force "
            "his half into Leona's educational trust if Pavel certified the default."
        ),
        "context": ["Celia and Jonas filed a formal separation agreement in September 2019."],
        "allowed_predicates": ["conditional_right/4", "deadline/3", "authority_if/4", "certifies/2"],
        "expect": {
            "decision": "mixed",
            "must": ["Jonas", "June 30, 2023", "Pavel", "default"],
            "avoid": ["transferred", "owns(leona"],
        },
    },
    {
        "id": "ledger_default_transfer",
        "domain": "legal_story",
        "utterance": (
            "Pavel certified the default on July 2. Celia invoked the agreement, "
            "and Jonas's half of Dock 7 transferred into Leona's educational trust for one crown."
        ),
        "context": [
            "Agreement: if Jonas missed the June 30, 2023 tax deadline and Pavel certified default, Celia could force transfer.",
            "Jonas missed the tax deadline on June 30, 2023.",
        ],
        "allowed_predicates": ["certified/3", "invoked/3", "transferred/5", "paid/3", "owned_share/3"],
        "expect": {
            "decision": "commit",
            "must": ["Pavel", "Celia", "Jonas", "Leona"],
            "avoid": ["Tomas", "Iris"],
        },
    },
    {
        "id": "ledger_tomas_half_untouched",
        "domain": "legal_story",
        "utterance": (
            "The separation agreement did not touch Tomas's half of Dock 7, "
            "because Tomas was not party to Celia and Jonas's marriage."
        ),
        "context": ["Dock 7 was co-owned by Jonas Voss and Tomas Vale."],
        "allowed_predicates": ["untouched_by_agreement/3", "co_owned/3", "party_to/2", "married/2"],
        "expect": {
            "decision": "commit",
            "must": ["Tomas", "Jonas", "Celia", "not party"],
            "avoid": ["transferred(tomas", "lost_share(tomas"],
        },
    },
    {
        "id": "ledger_compass_conditional_inheritance",
        "domain": "legal_story",
        "utterance": (
            "Tomas's will left the silver compass to Iris if she accepted keeper duties "
            "within sixty days; if she did not, the compass would pass to Mara as town archivist. "
            "Iris declined the keeper role, so the silver compass passed to Mara."
        ),
        "context": ["Tomas Vale died in February 2022.", "Iris was Tomas's only child."],
        "allowed_predicates": ["conditional_inheritance/4", "declined/3", "inherited/3", "role/2"],
        "expect": {
            "decision": "commit",
            "must": ["Iris", "Mara", "silver compass", "declined"],
            "avoid": ["inherited(iris, silver_compass"],
        },
    },
    {
        "id": "ledger_alias_quinn_quentin",
        "domain": "legal_story",
        "utterance": (
            "June published that the same constable had fined Quentin Marr and Quinn Damar "
            "separately for the same truck. The town finally admitted the two names belonged to one man."
        ),
        "context": ["Quinn used the name Quentin Marr on certain permits."],
        "allowed_predicates": ["alias/2", "fined/3", "reported/3", "admitted/2"],
        "expect": {
            "decision": "commit",
            "must": ["Quinn Damar", "Quentin Marr", "same truck", "one man"],
            "avoid": ["two people", "different men"],
        },
    },
    {
        "id": "ledger_guardianship_not_end",
        "domain": "legal_story",
        "utterance": (
            "June found Iain alive under the name Ian Morrow, but since he had not yet resumed "
            "ordinary residence in Calder's Reach, Mara's temporary guardianship of Tobin did not end at once."
        ),
        "context": [
            "Mireya's letter: Mara becomes Tobin's temporary guardian if Mireya is dead and Iain is missing for more than ninety days.",
            "Mara became Tobin's temporary guardian after Iain was missing for ninety days.",
        ],
        "allowed_predicates": ["alias/2", "found_alive/2", "resumed_residence/2", "guardianship_active/2", "ended/2"],
        "expect": {
            "decision": "commit",
            "must": ["Iain", "Ian Morrow", "Mara", "did not end"],
            "avoid": ["ended(guardianship", "guardianship_ended"],
        },
    },
    {
        "id": "ledger_scholarship_residency_loss",
        "domain": "legal_story",
        "utterance": (
            "Tobin spent five consecutive months out of district while Ashdown road was rebuilt; "
            "as a result, he lost the Harbor Scholarship at the next review, even though his father was still an active harbor worker."
        ),
        "context": [
            "Rule: a Harbor Scholarship recipient loses it if the child's household leaves Calder's Reach district for more than four consecutive months.",
            "Iain is Tobin's father and an active harbor worker.",
        ],
        "allowed_predicates": ["out_of_district/3", "active_harbor_worker/1", "lost_scholarship/3", "exception_overridden/2"],
        "expect": {
            "decision": "commit",
            "must": ["Tobin", "five consecutive months", "Harbor Scholarship", "active harbor worker"],
            "avoid": ["kept_scholarship", "eligible(tobin"],
        },
    },
    {
        "id": "ledger_profit_transfer_before_bonuses",
        "domain": "legal_story",
        "utterance": (
            "Tideglass net profit exceeded two hundred thousand crowns, so by charter "
            "twenty percent had to move into the flood fund before trustee bonuses; Pavel tried to delay it, but Ada enforced it."
        ),
        "context": ["Tideglass Conservatory is governed by a charitable trust charter."],
        "allowed_predicates": ["profit_exceeded/3", "required_transfer/4", "before/2", "attempted_delay/2", "enforced/2"],
        "expect": {
            "decision": "commit",
            "must": ["Tideglass", "twenty percent", "flood fund", "Ada"],
            "avoid": ["bonus_before_transfer", "pavel_enforced"],
        },
    },
    {
        "id": "edge_nested_exception_sample_n7",
        "domain": "lab_operations",
        "utterance": (
            "All refrigerated samples are discarded after forty-eight hours unless sealed. "
            "Neonatal samples must be escalated before any discard. Sample N7 is refrigerated, sealed, and neonatal."
        ),
        "context": [],
        "allowed_predicates": ["refrigerated/1", "sealed/1", "neonatal_sample/1", "discard_after/2", "requires_escalation_before/2"],
        "expect": {
            "decision": "mixed",
            "must": ["N7", "sealed", "neonatal", "escalated"],
            "avoid": ["discarded(n7", "discard(n7"],
        },
    },
    {
        "id": "edge_counterfactual_unsigned_inheritance",
        "domain": "legal_story",
        "utterance": (
            "If Mara had signed the codicil, Tobias would have inherited the boathouse; "
            "Mara never signed it, and the original will left the boathouse to Leona."
        ),
        "context": ["A codicil changes inheritance only if signed by Mara."],
        "allowed_predicates": ["signed/2", "would_inherit_if/3", "inherited/3", "left_to/3"],
        "expect": {
            "decision": "mixed",
            "must": ["counterfactual", "Mara", "Tobias", "Leona"],
            "avoid": ["inherited(tobias", "signed(mara"],
        },
    },
    {
        "id": "edge_quantified_every_except_w9",
        "domain": "compliance",
        "utterance": (
            "Every contractor except Nia must file a W-9 before onboarding; "
            "Nia filed a W-8BEN instead, while Omar and Jules have not filed anything."
        ),
        "context": [],
        "allowed_predicates": ["contractor/1", "requires_form/2", "filed_form/2", "exception_to_requirement/3"],
        "expect": {
            "decision": "mixed",
            "must": ["Nia", "W-8BEN", "Omar", "Jules"],
            "avoid": ["requires_form(nia", "filed_form(omar"],
        },
    },
    {
        "id": "edge_pronoun_stack_sister_van",
        "domain": "story_state",
        "utterance": "Mara told Priya that her sister saw her van before she moved it.",
        "context": ["Mara and Priya each have a sister.", "Mara and Priya each have access to a van."],
        "allowed_predicates": ["told/3", "sister/2", "saw/2", "moved/2"],
        "expect": {
            "decision": "clarify",
            "must": ["her", "sister", "van", "ambiguous"],
            "avoid": ["saw(priya", "moved(mara"],
        },
    },
    {
        "id": "edge_identity_repair_oslo_oskar",
        "domain": "legal_story",
        "utterance": "I said Oslo owns the lease, but that was wrong: Oskar owns the lease; Oslo is the street.",
        "context": ["owns_lease(oslo, dock7_lease)."],
        "allowed_predicates": ["owns_lease/2", "street_name/1", "correction/2"],
        "expect": {
            "decision": "commit",
            "must": ["Oskar", "Oslo", "street", "correction"],
            "avoid": ["owns_lease(oslo", "person(oslo"],
        },
    },
    {
        "id": "edge_hardship_query_pressure",
        "domain": "legal_story",
        "utterance": (
            "If a tenant misses two payments, notify the guarantor unless hardship is approved. "
            "Quinn missed two payments, but hardship is still pending. Who should be notified?"
        ),
        "context": [],
        "allowed_predicates": ["missed_payments/2", "hardship_status/2", "notify/2", "requires_notification/2"],
        "expect": {
            "decision": "mixed",
            "must": ["Quinn", "hardship", "pending", "query"],
            "avoid": ["notify(guarantor", "requires_notification(quinn"],
        },
    },
    {
        "id": "edge_alleged_forgery_court_finding",
        "domain": "legal_story",
        "utterance": (
            "June alleged Pavel forged the receipt. The court later found the receipt authentic, "
            "but it did not find that Pavel actually paid."
        ),
        "context": [],
        "allowed_predicates": ["alleged/3", "found/3", "authentic/1", "paid/2", "forged/2"],
        "expect": {
            "decision": "mixed",
            "must": ["alleged", "court", "authentic", "did not find"],
            "avoid": ["forged(pavel", "paid(pavel"],
        },
    },
    {
        "id": "edge_temporal_interval_chair",
        "domain": "governance",
        "utterance": (
            "Ada chaired the board until March 1. No one chaired it during March. "
            "Bo became chair on April 1."
        ),
        "context": [],
        "allowed_predicates": ["chaired_until/3", "vacant_during/2", "became_chair_on/3", "chaired_on/3"],
        "expect": {
            "decision": "commit",
            "must": ["Ada", "March 1", "vacant", "April 1", "Bo"],
            "avoid": ["chaired_on(ada, board, march", "chaired_on(bo, board, march"],
        },
    },
    {
        "id": "edge_missing_not_dead_separation_inheritance",
        "domain": "legal_story",
        "utterance": (
            "Mireya's surviving spouse inherits unless they were legally separated. "
            "Iain was missing, not dead, and the separation petition was filed but never finalized."
        ),
        "context": ["Iain is Mireya's spouse."],
        "allowed_predicates": ["spouse/2", "missing/1", "dead/1", "filed/2", "finalized/1", "inherits/2"],
        "expect": {
            "decision": "mixed",
            "must": ["Iain", "missing", "not dead", "not finalized"],
            "avoid": ["inherits(iain", "dead(iain", "legally_separated"],
        },
    },
    {
        "id": "edge_disjunction_leak_cause",
        "domain": "incident_review",
        "utterance": (
            "Either Pump A or Pump B caused the leak. Only Pump A had a pressure spike, "
            "but nobody inspected Pump B yet."
        ),
        "context": [],
        "allowed_predicates": ["possible_cause/2", "pressure_spike/1", "inspected/1", "caused/2"],
        "expect": {
            "decision": "mixed",
            "must": ["Pump A", "Pump B", "possible", "not inspected"],
            "avoid": ["caused(pump_a", "caused(pump_b"],
        },
    },
    {
        "id": "edge_scope_of_only_after_transfer",
        "domain": "legal_story",
        "utterance": (
            "Only after the escrow agent countersigned did the transfer become effective; "
            "Celia signed on Monday, but the escrow agent countersigned Wednesday."
        ),
        "context": [],
        "allowed_predicates": ["signed_on/3", "countersigned_on/3", "effective_on/3", "transfer_effective/1"],
        "expect": {
            "decision": "commit",
            "must": ["Celia", "Monday", "escrow", "Wednesday", "effective"],
            "avoid": ["effective_on(transfer, monday", "transfer_effective(monday"],
        },
    },
    {
        "id": "edge_comparative_measurement_direction",
        "domain": "medical",
        "utterance": (
            "Mara's potassium is lower than last week but still above the lab's upper bound; "
            "don't call it normal."
        ),
        "context": ["Active patient: Mara.", "Previous event: potassium was high last week."],
        "allowed_predicates": ["lab_result_high/2", "lab_result_low/2", "decreased_since/3", "normal_result/2"],
        "expect": {
            "decision": "commit",
            "must": ["Mara", "potassium", "lower", "above", "not normal"],
            "avoid": ["lab_result_low(mara", "normal_result(mara"],
        },
    },
    {
        "id": "edge_scope_negation_allergy",
        "domain": "medical",
        "utterance": "Priya is not allergic to amoxicillin; she just got nauseated after it.",
        "context": ["has_allergy(priya, amoxicillin)."],
        "allowed_predicates": ["has_allergy/2", "has_symptom/2", "side_effect/3"],
        "expect": {
            "decision": "commit",
            "must": ["Priya", "not allergic", "amoxicillin", "nauseated"],
            "avoid": ["has_allergy(priya, amoxicillin) as current"],
        },
    },
    {
        "id": "edge_nested_quote_denial",
        "domain": "story_state",
        "utterance": (
            "Mara said that Omar denied taking the key, but Priya saw Omar unlock the cabinet with it ten minutes later."
        ),
        "context": [],
        "allowed_predicates": ["said/3", "denied/3", "saw/3", "used_to_unlock/3", "possessed_at/3"],
        "expect": {
            "decision": "mixed",
            "must": ["Mara", "Omar", "denied", "Priya", "unlock"],
            "avoid": ["took(omar, key) as fact", "mara_denied"],
        },
    },
    {
        "id": "edge_mutual_exclusion_repair",
        "domain": "inventory",
        "utterance": (
            "Crate 12 cannot be both quarantined and cleared. I marked it cleared earlier, "
            "but after the mold test it should be quarantined instead."
        ),
        "context": ["cleared(crate12)."],
        "allowed_predicates": ["cleared/1", "quarantined/1", "mutex/2", "test_result/3"],
        "expect": {
            "decision": "commit",
            "must": ["Crate 12", "cleared", "quarantined", "instead"],
            "avoid": ["cleared(crate12) as current", "both"],
        },
    },
    {
        "id": "edge_chain_of_custody_gap",
        "domain": "evidence",
        "utterance": (
            "Nia logged the sample at 08:00 and Omar received it at 09:10. "
            "There is no record of who had it between 08:35 and 09:00."
        ),
        "context": [],
        "allowed_predicates": ["logged_at/3", "received_at/3", "custody_gap/3", "possessed_at/3"],
        "expect": {
            "decision": "commit",
            "must": ["Nia", "08:00", "Omar", "09:10", "gap"],
            "avoid": ["possessed_at(nia, sample, 08:45", "possessed_at(omar, sample, 08:45"],
        },
    },
    {
        "id": "edge_temporal_correction_warfarin",
        "domain": "medical",
        "utterance": "I said Mara stopped warfarin on Tuesday, but that was wrong; she stopped it Wednesday morning.",
        "context": ["stopped_on(mara, warfarin, tuesday)."],
        "allowed_predicates": ["stopped_on/3", "taking/2", "correction/2"],
        "expect": {
            "decision": "commit",
            "must": ["Mara", "warfarin", "Tuesday", "Wednesday", "correction"],
            "avoid": ["stopped_on(mara, warfarin, tuesday) as current", "taking(mara, warfarin)"],
        },
    },
    {
        "id": "edge_denial_not_negation",
        "domain": "legal_story",
        "utterance": "Omar denied signing the waiver.",
        "context": [],
        "allowed_predicates": ["denied/3", "signed/2"],
        "expect": {
            "decision": "commit",
            "must": ["Omar", "denied", "signing", "waiver"],
            "avoid": ["not signed", "signed(omar, waiver) false", "unsigned"],
        },
    },
    {
        "id": "edge_double_negation_lived_salem",
        "domain": "story_state",
        "utterance": "It isn't true that Nina never lived in Salem.",
        "context": [],
        "allowed_predicates": ["lived_in/2", "lived_in_at_some_time/2"],
        "expect": {
            "decision": "commit",
            "must": ["Nina", "Salem", "lived", "double negation"],
            "avoid": ["never_lived", "not_lived"],
        },
    },
    {
        "id": "edge_hypothetical_hazard_pay_query",
        "domain": "policy",
        "utterance": "If Felix had covered the emergency shift, would he have received hazard pay?",
        "context": [
            "Night crew receive hazard pay except Felix.",
            "Felix's exception is waived if Felix covers an emergency shift.",
        ],
        "allowed_predicates": ["covered_emergency_shift/1", "receives_hazard_pay/1", "exception_waived/2"],
        "expect": {
            "decision": "answer",
            "must": ["Felix", "hypothetical", "emergency shift", "hazard pay"],
            "avoid": ["covered_emergency_shift(felix)", "receives_hazard_pay(felix) as fact"],
        },
    },
    {
        "id": "weak_hypothetical_waiver_query",
        "domain": "policy",
        "utterance": "If the supervisor had waived Felix's exception, would Felix receive hazard pay?",
        "context": ["Felix is normally excepted from hazard pay.", "A supervisor waiver overrides the exception."],
        "allowed_predicates": ["waived_exception/2", "receives_hazard_pay/1", "exception_to/2"],
        "expect": {
            "decision": "answer",
            "must": ["Felix", "hypothetical", "waived", "hazard pay"],
            "avoid": ["waived_exception(felix", "receives_hazard_pay(felix) as fact"],
        },
    },
    {
        "id": "weak_hypothetical_transfer_query",
        "domain": "legal_story",
        "utterance": "Had Pavel certified the default before July, would Celia have been allowed to transfer Jonas's half?",
        "context": ["Celia can transfer Jonas's half only if Pavel certifies default before July."],
        "allowed_predicates": ["certified_before/3", "allowed_transfer/3", "transferred/3"],
        "expect": {
            "decision": "answer",
            "must": ["Pavel", "hypothetical", "Celia", "transfer"],
            "avoid": ["certified_before(pavel", "transferred(celia"],
        },
    },
    {
        "id": "weak_quantified_residents_except_kai",
        "domain": "compliance",
        "utterance": "All residents except Kai submitted forms; Kai submitted a waiver instead.",
        "context": ["Known residents: Kai, Lena, Omar."],
        "allowed_predicates": ["resident/1", "submitted_form/1", "submitted_waiver/1", "exception_to_requirement/2"],
        "expect": {
            "decision": "mixed",
            "must": ["Kai", "waiver", "except", "residents"],
            "avoid": ["submitted_form(kai", "submitted_form(lena"],
        },
    },
    {
        "id": "weak_quantified_box_expired_exception",
        "domain": "compliance",
        "utterance": "All flagged invoices require review unless exempt. Box8 is flagged, but its exemption expired yesterday.",
        "context": [],
        "allowed_predicates": ["flagged/1", "exempt/1", "expired_on/2", "requires_review/1"],
        "expect": {
            "decision": "mixed",
            "must": ["Box8", "flagged", "exemption", "expired"],
            "avoid": ["exempt(box8) as current", "requires_review(box8) as fact"],
        },
    },
    {
        "id": "weak_medical_negation_side_effect",
        "domain": "medical",
        "utterance": "Priya is not allergic to amoxicillin; list it as nausea, not allergy.",
        "context": ["has_allergy(priya, amoxicillin)."],
        "allowed_predicates": ["has_allergy/2", "side_effect/3", "has_symptom/2"],
        "expect": {
            "decision": "commit",
            "must": ["Priya", "amoxicillin", "nausea", "not allergy"],
            "avoid": ["has_allergy(priya, amoxicillin) as current"],
        },
    },
    {
        "id": "weak_medical_negation_intolerance",
        "domain": "medical",
        "utterance": "Remove Leo's penicillin allergy; the note says stomach upset only.",
        "context": ["has_allergy(leo, penicillin)."],
        "allowed_predicates": ["has_allergy/2", "side_effect/3", "has_symptom/2"],
        "expect": {
            "decision": "commit",
            "must": ["Leo", "penicillin", "stomach upset", "remove"],
            "avoid": ["has_allergy(leo, penicillin) as current"],
        },
    },
    {
        "id": "weak_denial_camera_observation",
        "domain": "story_state",
        "utterance": "Omar denied taking the key, but the camera showed him unlocking the cabinet with it later.",
        "context": [],
        "allowed_predicates": ["denied/3", "showed/3", "used_to_unlock/3", "took/2"],
        "expect": {
            "decision": "mixed",
            "must": ["Omar", "denied", "camera", "unlocking"],
            "avoid": ["took(omar, key) as fact", "not_took"],
        },
    },
    {
        "id": "weak_denial_reported_by_mara",
        "domain": "story_state",
        "utterance": "Mara reported that Omar denied signing the waiver.",
        "context": [],
        "allowed_predicates": ["reported/3", "denied/3", "signed/2"],
        "expect": {
            "decision": "commit",
            "must": ["Mara", "Omar", "denied", "waiver"],
            "avoid": ["signed(omar, waiver) false", "not_signed"],
        },
    },
    {
        "id": "weak_retraction_alias_crate12",
        "domain": "inventory",
        "utterance": "Crate 12 was cleared. Actually crate12 should be quarantined instead.",
        "context": ["cleared(crate12)."],
        "allowed_predicates": ["cleared/1", "quarantined/1"],
        "expect": {
            "decision": "commit",
            "must": ["Crate 12", "crate12", "quarantined", "instead"],
            "avoid": ["cleared(crate12) as current"],
        },
    },
    {
        "id": "weak_retraction_alias_bay_7",
        "domain": "inventory",
        "utterance": "Bay 7 is not closed anymore; bay7 reopened this morning.",
        "context": ["closed(bay7)."],
        "allowed_predicates": ["closed/1", "reopened_on/2"],
        "expect": {
            "decision": "commit",
            "must": ["Bay 7", "bay7", "reopened", "morning"],
            "avoid": ["closed(bay7) as current"],
        },
    },
]


EDGE_SCENARIO_IDS = [
    "edge_nested_exception_sample_n7",
    "edge_counterfactual_unsigned_inheritance",
    "edge_quantified_every_except_w9",
    "edge_pronoun_stack_sister_van",
    "edge_identity_repair_oslo_oskar",
    "edge_hardship_query_pressure",
    "edge_alleged_forgery_court_finding",
    "edge_temporal_interval_chair",
    "edge_missing_not_dead_separation_inheritance",
    "edge_disjunction_leak_cause",
    "edge_scope_of_only_after_transfer",
    "edge_comparative_measurement_direction",
    "edge_scope_negation_allergy",
    "edge_nested_quote_denial",
    "edge_mutual_exclusion_repair",
    "edge_chain_of_custody_gap",
    "edge_temporal_correction_warfarin",
    "edge_denial_not_negation",
    "edge_double_negation_lived_salem",
    "edge_hypothetical_hazard_pay_query",
]


WEAK_EDGE_SCENARIO_IDS = [
    "weak_hypothetical_waiver_query",
    "weak_hypothetical_transfer_query",
    "weak_quantified_residents_except_kai",
    "weak_quantified_box_expired_exception",
    "weak_medical_negation_side_effect",
    "weak_medical_negation_intolerance",
    "weak_denial_camera_observation",
    "weak_denial_reported_by_mara",
    "weak_retraction_alias_crate12",
    "weak_retraction_alias_bay_7",
]


SCHEMA_CONTRACT = {
    "schema_version": "semantic_ir_v1",
    "decision": "commit|clarify|quarantine|reject|answer|mixed",
    "turn_type": "state_update|query|correction|rule_update|mixed|unknown",
    "entities": [
        {"id": "e1", "surface": "", "normalized": "", "type": "person|object|medication|lab_test|condition|symptom|place|time|unknown", "confidence": 0.0}
    ],
    "referents": [
        {"surface": "it|her|his|that", "status": "resolved|ambiguous|unresolved", "candidates": ["e1"], "chosen": None}
    ],
    "assertions": [
        {"kind": "direct|question|claim|correction|rule", "subject": "e1", "relation_concept": "", "object": "e2", "polarity": "positive|negative", "certainty": 0.0}
    ],
    "unsafe_implications": [
        {"candidate": "", "why_unsafe": "", "commit_policy": "clarify|quarantine|reject"}
    ],
    "candidate_operations": [
        {
            "operation": "assert|retract|rule|query|none",
            "predicate": "",
            "args": [],
            "polarity": "positive|negative",
            "source": "direct|inferred|context",
            "safety": "safe|unsafe|needs_clarification",
        }
    ],
    "clarification_questions": [""],
    "self_check": {"bad_commit_risk": "low|medium|high", "missing_slots": [], "notes": []},
}


SEMANTIC_IR_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "decision",
        "turn_type",
        "entities",
        "referents",
        "assertions",
        "unsafe_implications",
        "candidate_operations",
        "clarification_questions",
        "self_check",
    ],
    "properties": {
        "schema_version": {"type": "string", "const": "semantic_ir_v1"},
        "decision": {
            "type": "string",
            "enum": ["commit", "clarify", "quarantine", "reject", "answer", "mixed"],
        },
        "turn_type": {
            "type": "string",
            "enum": ["state_update", "query", "correction", "rule_update", "mixed", "unknown"],
        },
        "entities": {
            "type": "array",
            "maxItems": 12,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "surface", "normalized", "type", "confidence"],
                "properties": {
                    "id": {"type": "string"},
                    "surface": {"type": "string"},
                    "normalized": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": [
                            "person",
                            "object",
                            "medication",
                            "lab_test",
                            "condition",
                            "symptom",
                            "place",
                            "time",
                            "unknown",
                        ],
                    },
                    "confidence": {"type": "number"},
                },
            },
        },
        "referents": {
            "type": "array",
            "maxItems": 8,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["surface", "status", "candidates", "chosen"],
                "properties": {
                    "surface": {"type": "string"},
                    "status": {"type": "string", "enum": ["resolved", "ambiguous", "unresolved"]},
                    "candidates": {"type": "array", "items": {"type": "string"}},
                    "chosen": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                },
            },
        },
        "assertions": {
            "type": "array",
            "maxItems": 8,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["kind", "subject", "relation_concept", "object", "polarity", "certainty"],
                "properties": {
                    "kind": {"type": "string", "enum": ["direct", "question", "claim", "correction", "rule"]},
                    "subject": {"type": "string"},
                    "relation_concept": {"type": "string"},
                    "object": {"type": "string"},
                    "polarity": {"type": "string", "enum": ["positive", "negative"]},
                    "certainty": {"type": "number"},
                },
            },
        },
        "unsafe_implications": {
            "type": "array",
            "maxItems": 8,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["candidate", "why_unsafe", "commit_policy"],
                "properties": {
                    "candidate": {"type": "string"},
                    "why_unsafe": {"type": "string"},
                    "commit_policy": {"type": "string", "enum": ["clarify", "quarantine", "reject"]},
                },
            },
        },
        "candidate_operations": {
            "type": "array",
            "maxItems": 8,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["operation", "predicate", "args", "polarity", "source", "safety"],
                "properties": {
                    "operation": {"type": "string", "enum": ["assert", "retract", "rule", "query", "none"]},
                    "predicate": {"type": "string"},
                    "args": {"type": "array", "items": {"type": "string"}},
                    "polarity": {"type": "string", "enum": ["positive", "negative"]},
                    "source": {"type": "string", "enum": ["direct", "inferred", "context"]},
                    "safety": {"type": "string", "enum": ["safe", "unsafe", "needs_clarification"]},
                },
            },
        },
        "clarification_questions": {"type": "array", "maxItems": 3, "items": {"type": "string"}},
        "self_check": {
            "type": "object",
            "additionalProperties": False,
            "required": ["bad_commit_risk", "missing_slots", "notes"],
            "properties": {
                "bad_commit_risk": {"type": "string", "enum": ["low", "medium", "high"]},
                "missing_slots": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
                "notes": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
            },
        },
    },
}


PROMPT_VARIANTS: dict[str, dict[str, Any]] = {
    "strict_contract_v1": {
        "temperature": 0.0,
        "top_p": 0.8,
        "top_k": 20,
        "system": (
            "You are a semantic IR compiler for a governed symbolic memory system. "
            "You do not answer the user and you do not commit durable truth. "
            "Emit only semantic_ir_v1 JSON. The root object must be the IR itself, with schema_version and decision as top-level keys. "
            "Do not wrap the answer under schema_contract, result, output, or semantic_ir. "
            "Separate direct assertions from unsafe implications. "
            "When a referent, measurement, time, or clinical conclusion is missing, choose clarify or quarantine."
        ),
        "extra": "",
    },
    "negative_examples_v1": {
        "temperature": 0.0,
        "top_p": 0.8,
        "top_k": 20,
        "system": (
            "You are a semantic IR compiler for a governed symbolic memory system. "
            "You are strict about the authority boundary: proposed meaning is not committed truth. "
            "Emit only semantic_ir_v1 JSON. The root object must be the IR itself, with schema_version and decision as top-level keys. "
            "Do not wrap the answer under schema_contract, result, output, or semantic_ir."
        ),
        "extra": (
            "Bad pattern: vague 'pressure is bad' -> commit hypertension. Correct: clarify pressure type and direction.\n"
            "Bad pattern: nausea after amoxicillin -> commit allergy. Correct: clarify allergy vs intolerance and quarantine allergy.\n"
            "Bad pattern: Bob claims he still has the key -> commit possession. Correct: commit/represent the claim, quarantine possession.\n"
            "Bad pattern: user asks if they should stop warfarin -> answer or retract medication. Correct: reject medical advice and ask clinical-context questions.\n"
        ),
    },
    "nbest_selfcheck_v1": {
        "temperature": 0.1,
        "top_p": 0.9,
        "top_k": 20,
        "system": (
            "You are a semantic workspace compiler. Build several possible readings before selecting a decision. "
            "Emit only semantic_ir_v1 JSON. The root object must be the IR itself, with schema_version and decision as top-level keys. "
            "Do not wrap the answer under schema_contract, result, output, or semantic_ir. "
            "Prefer explicit ambiguity over forced interpretation. "
            "Any write candidate must survive a self-check for bad commits."
        ),
        "extra": (
            "In self_check.notes, include the strongest alternative reading and why it was not committed. "
            "Candidate operations may include unsafe alternatives, but they must be marked unsafe or needs_clarification."
        ),
    },
    "domain_profile_v1": {
        "temperature": 0.0,
        "top_p": 0.85,
        "top_k": 20,
        "system": (
            "You are a domain-aware semantic IR compiler for a governed symbolic memory system. "
            "Medical medication changes, diagnosis staging, and treatment advice are not admissible as committed facts. "
            "General corrections may propose retract/assert pairs when the utterance directly corrects prior state. "
            "Emit only semantic_ir_v1 JSON. The root object must be the IR itself, with schema_version and decision as top-level keys. "
            "Do not wrap the answer under schema_contract, result, output, or semantic_ir."
        ),
        "extra": (
            "Domain policy: medical facts need explicit patient, concept, polarity, and measurement/result state. "
            "Drug brand synonyms may be normalized, but clinical conclusions must remain uncommitted unless directly stated as existing facts. "
            "Corrections should preserve provenance: old state may be retracted only when the correction target is clear."
        ),
    },
    "best_guarded_v2": {
        "temperature": 0.0,
        "top_p": 0.82,
        "top_k": 20,
        "system": (
            "You are a semantic IR compiler for a governed symbolic memory system. "
            "The root object must be semantic_ir_v1 itself, with schema_version and decision as top-level keys. "
            "Do not wrap the answer under schema_contract, result, output, or semantic_ir. "
            "You do not answer the user and you do not commit durable truth. "
            "Use direct language understanding aggressively, but mark unsafe commitments explicitly."
        ),
        "extra": (
            "Decision policy:\n"
            "- reject: user asks for treatment, dose, medication stop/hold/start, or clinical recommendation. You may still include clarification questions, but the decision remains reject.\n"
            "- quarantine: direct facts conflict with a claim, a claim would overwrite observed state, or a candidate fact is plausible but unsafe.\n"
            "- clarify: missing referent, measurement direction, patient identity, object of 'it/that', or allergy-vs-intolerance distinction blocks a write.\n"
            "- mixed: same turn contains both safe writes and a query/rule/unsafe implication.\n"
            "- commit: direct state update or correction has a clear target and safe predicate mapping.\n"
            "Special guards:\n"
            "- Keep arrays compact: at most 8 assertions, 8 unsafe_implications, 8 candidate_operations, and 3 clarification_questions. Never repeat equivalent assertions.\n"
            "- Do not turn a claim into a fact. 'Bob says he has it' is a claim, not possession.\n"
            "- Do not infer diagnosis or staging from a single lab value request. Quarantine or clarify.\n"
            "- Do not infer allergy from nausea/vomiting alone. Clarify allergy vs side effect/intolerance.\n"
            "- If the user explicitly corrects a prior allergy record with 'not allergic' and provides a side-effect/intolerance explanation, propose retracting the allergy and recording the side effect; do not give medical advice.\n"
            "- A clear correction like 'not Mara, Fred has it' may propose retract/assert.\n"
            "- Do not invent required governance slots that are not in the predicate schema. Source document, authority, or reason fields are optional provenance unless the allowed predicate explicitly requires them.\n"
            "- A direct correction like 'remove X allergy; stomach upset only' is explicit enough to retract the allergy and record side effect/intolerance when the old allergy fact is in context.\n"
            "- Do not assert a fact about a quantified group atom such as submitted_form(residents) for 'all residents except Kai'. Use individual known members only when context enumerates them; otherwise mark the class-level write unsafe.\n"
            "- Pure hypothetical questions with 'if ... would ...?' are queries, not writes and not clarification requests when the hypothetical nature is clear.\n"
            "- Denial predicates are speech/event facts. 'Omar denied signing the waiver' may assert denied(...); it must not assert signed(...) false.\n"
            "- When pronouns or referents are ambiguous and only a generic speech/container fact such as told/said/claimed is safe, choose clarify rather than committing the speech wrapper.\n"
            "- If context supplies exactly one active patient and one active lab test, a direct 'it came back high' may propose a safe lab_result_high write.\n"
            "- For rule-plus-fact or fact-plus-query turns, use mixed and keep unsafe query targets out of committed facts.\n"
            "- Preserve negation in candidate_operations with polarity='negative'. Do not turn 'never saw X' into a positive saw/2 fact."
        ),
    },
    "best_guarded_v3": {
        "temperature": 0.0,
        "top_p": 0.82,
        "top_k": 20,
        "system": (
            "You are a semantic IR compiler for a governed symbolic memory system. "
            "The root object must be semantic_ir_v1 itself, with schema_version and decision as top-level keys. "
            "Do not wrap the answer under schema_contract, result, output, or semantic_ir. "
            "You do not answer the user and you do not commit durable truth. "
            "Use direct language understanding aggressively, but mark unsafe commitments explicitly."
        ),
        "extra": (
            "Decision policy:\n"
            "- reject: user asks for treatment, dose, medication stop/hold/start, or clinical recommendation. You may still include clarification questions, but the decision remains reject.\n"
            "- quarantine: direct facts conflict with a claim, a claim would overwrite observed state, or a candidate fact is plausible but unsafe.\n"
            "- clarify: missing referent, measurement direction, patient identity, object of 'it/that', or allergy-vs-intolerance distinction blocks a write.\n"
            "- mixed: same turn contains both safe writes and a query/rule/unsafe implication.\n"
            "- commit: direct state update or correction has a clear target and safe predicate mapping.\n"
            "Special guards:\n"
            "- Keep arrays compact: at most 8 assertions, 8 unsafe_implications, 8 candidate_operations, and 3 clarification_questions. Never repeat equivalent assertions.\n"
            "- Do not turn a claim into a fact. 'Bob says he has it' is a claim, not possession.\n"
            "- Do not infer diagnosis or staging from a single lab value request. Quarantine or clarify.\n"
            "- Do not infer allergy from nausea/vomiting alone. Clarify allergy vs side effect/intolerance unless the user explicitly corrects a prior allergy record.\n"
            "- If the user explicitly corrects a prior allergy record with 'not allergic' and provides a side-effect/intolerance explanation, propose retracting the allergy and recording the side effect; do not give medical advice.\n"
            "- A clear correction like 'not Mara, Fred has it', 'that was wrong', or 'instead' may propose retract/assert.\n"
            "- Do not invent required governance slots that are not in the predicate schema. Source document, authority, or reason fields are optional provenance unless the allowed predicate explicitly requires them.\n"
            "- A direct correction like 'remove X allergy; stomach upset only' is explicit enough to retract the allergy and record side effect/intolerance when the old allergy fact is in context.\n"
            "- Do not assert a fact about a quantified group atom such as submitted_form(residents) for 'all residents except Kai'. Use individual known members only when context enumerates them; otherwise mark the class-level write unsafe.\n"
            "- Pure hypothetical questions with 'if ... would ...?' are queries, not writes and not clarification requests when the hypothetical nature is clear.\n"
            "- Denial predicates are speech/event facts. 'Omar denied signing the waiver' may assert denied(...); it must not assert signed(...) false.\n"
            "- When pronouns or referents are ambiguous and only a generic speech/container fact such as told/said/claimed is safe, choose clarify rather than committing the speech wrapper.\n"
            "- If context supplies exactly one active patient and one active lab test, a direct 'it came back high' may propose a safe lab_result_high write.\n"
            "- For rule-plus-fact or fact-plus-query turns, use mixed and keep unsafe query targets out of committed facts.\n"
            "- Preserve negation in candidate_operations with polarity='negative'. Do not turn 'never saw X' into a positive saw/2 fact.\n"
            "Operation policy:\n"
            "- A retract operation should use polarity='positive' when retracting a previously stored positive fact. Use polarity='negative' only for explicit negative facts.\n"
            "- Denials are claim events, not negated facts. 'Omar denied signing' is denied(...), not not(signed(...)).\n"
            "- Counterfactuals and hypotheticals are not writes. Represent them as query/unsafe implication/self_check notes.\n"
            "- Disjunctions like 'A or B caused it' do not prove either cause; record safe observations and quarantine cause assignment.\n"
            "- Do not copy context rules into candidate_operations unless the user is adding or changing the rule.\n"
            "- Do not invent required governance slots that are not in the predicate schema. Source document, authority, or reason fields are optional provenance unless the allowed predicate explicitly requires them.\n"
            "- Do not assert a fact about a quantified group atom such as submitted_form(residents) for 'all residents except Kai'. Use individual known members only when context enumerates them; otherwise mark the class-level write unsafe.\n"
            "- Preserve temporal scope: until, during, after, before, not yet, no longer, and from/to should not become timeless facts.\n"
            "- Preserve provenance: claimed, alleged, admitted, denied, observed, found, and reported are different relations."
        ),
    },
    "edge_compiler_v1": {
        "temperature": 0.0,
        "top_p": 0.78,
        "top_k": 20,
        "system": (
            "You are a semantic compiler that emits semantic_ir_v1 for a governed Prolog memory runtime. "
            "The root object must be semantic_ir_v1 itself, with schema_version and decision as top-level keys. "
            "Do not wrap the answer under schema_contract, result, output, or semantic_ir. "
            "Be ambitious about language understanding, conservative about durable truth, and exact about operation source and safety."
        ),
        "extra": (
            "Decision policy:\n"
            "- commit: direct current-state facts, explicit corrections, explicit identity repairs, direct observations, and direct temporal facts with clear targets.\n"
            "- answer: pure questions or hypotheticals that should be evaluated against context/rules; do not emit rule operations just because the rule appears in context.\n"
            "- mixed: same utterance contains safe writes plus a query, rule addition, or unsafe implication.\n"
            "- clarify: a commit-critical referent, entity identity, time, measurement, or predicate sense is missing.\n"
            "- quarantine: the only candidate commitments are claims, allegations, disjunctions, diagnoses, advice, or unsafe implications.\n"
            "- reject: medical advice or treatment/dose/hold/start/stop recommendations.\n"
            "Operation policy:\n"
            "- Keep arrays compact: at most 8 assertions, 8 unsafe_implications, 8 candidate_operations, and 3 clarification_questions. Never repeat equivalent assertions.\n"
            "- A retract operation should use polarity='positive' when retracting a previously stored positive fact. Use polarity='negative' only for explicit negative facts.\n"
            "- Direct corrections with 'not X, Y instead', 'that was wrong', or 'don't call it normal' may propose safe retract/assert operations.\n"
            "- Direct 'not allergic; side effect/nausea instead' may propose retracting the allergy and asserting the side effect, while keeping clinical advice out.\n"
            "- A direct correction like 'remove X allergy; stomach upset only' is explicit enough to retract the allergy and record side effect/intolerance when the old allergy fact is in context.\n"
            "- Denials are claim events, not negated facts. 'Omar denied signing' is denied(...), not not(signed(...)).\n"
            "- Counterfactuals and hypotheticals are not writes. Represent them as query/unsafe implication/self_check notes.\n"
            "- When pronouns or referents are ambiguous and only a generic speech/container fact such as told/said/claimed is safe, choose clarify rather than committing the speech wrapper.\n"
            "- Disjunctions like 'A or B caused it' do not prove either cause; record safe observations and quarantine cause assignment.\n"
            "- Do not copy context rules into candidate_operations unless the user is adding or changing the rule.\n"
            "- Do not invent required governance slots that are not in the predicate schema. Source document, authority, or reason fields are optional provenance unless the allowed predicate explicitly requires them.\n"
            "- Do not assert a fact about a quantified group atom such as submitted_form(residents) for 'all residents except Kai'. Use individual known members only when context enumerates them; otherwise mark the class-level write unsafe.\n"
            "- Preserve temporal scope: until, during, after, before, not yet, no longer, and from/to should not become timeless facts.\n"
            "- Preserve provenance: claimed, alleged, admitted, denied, observed, found, and reported are different relations."
        ),
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def build_messages(
    *,
    variant: str,
    scenario: dict[str, Any],
    include_schema_in_prompt: bool = True,
) -> list[dict[str, str]]:
    prompt = PROMPT_VARIANTS[variant]
    payload = {
        "task": "Analyze the utterance and emit semantic_ir_v1 JSON only.",
        "output_instruction": (
            "Return exactly one JSON object conforming to semantic_ir_v1. "
            "Do not include prose or wrapper keys. Keep arrays compact: include only essential entities, "
            "assertions, unsafe implications, and candidate operations, and do not repeat equivalent items."
        ),
        "domain": scenario["domain"],
        "utterance": scenario["utterance"],
        "context": scenario.get("context", []),
        "allowed_predicates": scenario.get("allowed_predicates", []),
        "authority_boundary": "The runtime validates and commits; you only propose semantic structure.",
        "variant_guidance": prompt["extra"],
    }
    if include_schema_in_prompt:
        payload["required_top_level_json_shape"] = SCHEMA_CONTRACT
        payload["output_instruction"] = (
            "Return exactly one JSON object using required_top_level_json_shape as the root shape. "
            "Do not copy the key name required_top_level_json_shape into your response."
        )
    return [
        {"role": "system", "content": str(prompt["system"])},
        {"role": "user", "content": "INPUT_JSON:\n" + _json_dumps(payload)},
    ]


def call_ollama(
    *,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    options: dict[str, Any],
    timeout: int,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "think": False,
        "messages": messages,
        "options": {
            "temperature": float(options.get("temperature", 0.0)),
            "top_p": float(options.get("top_p", 0.9)),
            "top_k": int(options.get("top_k", 20)),
            "num_ctx": int(options.get("num_ctx", 16384)),
        },
    }
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc)) from exc
    message = raw.get("message", {}) if isinstance(raw, dict) else {}
    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "raw": raw,
        "content": str(message.get("content", "")).strip(),
    }


def call_lmstudio(
    *,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    options: dict[str, Any],
    timeout: int,
    reasoning_effort: str,
    max_tokens: int,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": float(options.get("temperature", 0.0)),
        "top_p": float(options.get("top_p", 0.9)),
        "max_tokens": int(max_tokens),
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "semantic_ir_v1",
                "strict": True,
                "schema": SEMANTIC_IR_JSON_SCHEMA,
            },
        },
    }
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc)) from exc
    choices = raw.get("choices", []) if isinstance(raw, dict) else []
    message = choices[0].get("message", {}) if choices and isinstance(choices[0], dict) else {}
    content = str(message.get("content", "") if isinstance(message, dict) else "").strip()
    reasoning_content = str(message.get("reasoning_content", "") if isinstance(message, dict) else "").strip()
    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "raw": raw,
        "content": content or reasoning_content,
        "content_channel": "content" if content else ("reasoning_content" if reasoning_content else ""),
    }


def parse_json_payload(text: str) -> tuple[dict[str, Any] | None, str]:
    raw = str(text or "").strip()
    if not raw:
        return None, "empty"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.S)
        if not match:
            return None, "not_json"
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            return None, f"json_error:{exc}"
    if not isinstance(parsed, dict):
        return None, "json_not_object"
    return parsed, ""


def flatten_text(value: Any) -> str:
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, dict):
        return " ".join(flatten_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(flatten_text(v) for v in value)
    return str(value).lower()


def _decision_matches(actual: str, expected: str) -> bool:
    actual = actual.lower()
    expected = expected.lower()
    if actual == expected:
        return True
    if expected == "clarify" and actual in {"clarify", "quarantine"}:
        return True
    if expected == "reject" and actual in {"reject", "quarantine"}:
        return True
    if expected == "mixed" and actual in {"mixed", "clarify", "quarantine"}:
        return True
    return False


def score_record(parsed: dict[str, Any] | None, scenario: dict[str, Any]) -> dict[str, Any]:
    expect = scenario["expect"]
    if not parsed:
        return {
            "decision_ok": False,
            "schema_ok": False,
            "must_count": 0,
            "must_total": len(expect["must"]),
            "avoid_count": 0,
            "avoid_total": len(expect["avoid"]),
            "bad_commit_risk": "unknown",
            "rough_score": 0.0,
        }
    decision = str(parsed.get("decision", "")).lower()
    text = flatten_text(parsed)
    schema_keys = ["schema_version", "decision", "entities", "referents", "assertions", "unsafe_implications", "candidate_operations", "clarification_questions", "self_check"]
    schema_ok = all(key in parsed for key in schema_keys) and parsed.get("schema_version") == "semantic_ir_v1"
    must = [item.lower() for item in expect["must"]]
    avoid = [item.lower() for item in expect["avoid"]]
    noticed = [item for item in must if item in text]
    avoided = [item for item in avoid if item not in text]
    decision_ok = _decision_matches(decision, expect["decision"])
    bad_commit_risk = str((parsed.get("self_check") or {}).get("bad_commit_risk", "")).lower()
    return {
        "decision": decision,
        "expected_decision": expect["decision"],
        "decision_ok": decision_ok,
        "schema_ok": schema_ok,
        "must_count": len(noticed),
        "must_total": len(must),
        "noticed": noticed,
        "avoid_count": len(avoided),
        "avoid_total": len(avoid),
        "avoided": avoided,
        "bad_commit_risk": bad_commit_risk,
        "rough_score": (
            (1 if decision_ok else 0)
            + (1 if schema_ok else 0)
            + (len(noticed) / max(1, len(must)))
            + (len(avoided) / max(1, len(avoid)))
        ) / 4,
    }


def write_summary(records: list[dict[str, Any]], path: Path) -> None:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(record["variant"], []).append(record)
    lines = [
        "# Semantic IR Prompt Bakeoff",
        "",
        f"Generated: {_utc_now()}",
        "",
        "## Aggregate",
        "",
        "| Variant | Runs | JSON OK | Schema OK | Decision OK | Avg rough score | Avg latency ms |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for variant, rows in sorted(grouped.items()):
        json_ok = sum(1 for row in rows if row.get("parsed_ok"))
        schema_ok = sum(1 for row in rows if row.get("score", {}).get("schema_ok"))
        decision_ok = sum(1 for row in rows if row.get("score", {}).get("decision_ok"))
        avg_score = sum(float(row.get("score", {}).get("rough_score", 0.0)) for row in rows) / max(1, len(rows))
        avg_latency = sum(int(row.get("latency_ms", 0)) for row in rows) / max(1, len(rows))
        lines.append(f"| `{variant}` | {len(rows)} | {json_ok} | {schema_ok} | {decision_ok} | {avg_score:.2f} | {avg_latency:.0f} |")
    lines.extend(["", "## Low Rough Scores", ""])
    low = sorted(records, key=lambda row: float(row.get("score", {}).get("rough_score", 0.0)))[:24]
    for row in low:
        score = float(row.get("score", {}).get("rough_score", 0.0))
        lines.append(
            f"- `{row['variant']}` / `{row['scenario_id']}`: "
            f"score={score:.2f} parsed={row.get('parsed_ok')} "
            f"decision={row.get('score', {}).get('decision')} expected={row.get('score', {}).get('expected_decision')}"
        )
    lines.extend(["", "## Files", "", f"- JSONL: `{path.with_suffix('.jsonl').name}`"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["ollama", "lmstudio"], default="ollama")
    parser.add_argument("--model", default="")
    parser.add_argument("--variants", default="strict_contract_v1,negative_examples_v1,nbest_selfcheck_v1,domain_profile_v1,best_guarded_v2")
    parser.add_argument("--scenario-ids", default="")
    parser.add_argument("--scenario-group", choices=["all", "edge", "weak_edges"], default="all")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--num-ctx", type=int, default=16384)
    parser.add_argument("--reasoning-effort", default="none")
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--omit-schema-in-prompt", action="store_true")
    parser.add_argument("--include-schema-in-prompt", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    backend = str(args.backend or "ollama").strip().lower()
    model = str(args.model or "").strip()
    if not model:
        model = "qwen/qwen3.6-35b-a3b" if backend == "lmstudio" else "qwen3.6:35b"
    base_url = str(args.base_url or "").strip()
    if not base_url:
        base_url = "http://127.0.0.1:1234" if backend == "lmstudio" else "http://127.0.0.1:11434"
    variants = [item.strip() for item in args.variants.split(",") if item.strip()]
    scenario_ids = [item.strip() for item in str(args.scenario_ids or "").split(",") if item.strip()]
    if not scenario_ids:
        if args.scenario_group == "edge":
            scenario_ids = list(EDGE_SCENARIO_IDS)
        elif args.scenario_group == "weak_edges":
            scenario_ids = list(WEAK_EDGE_SCENARIO_IDS)
    by_id = {scenario["id"]: scenario for scenario in WILD_SCENARIOS}
    scenarios = [by_id[item] for item in scenario_ids] if scenario_ids else list(WILD_SCENARIOS)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jsonl_path = out_dir / f"semantic_ir_prompt_bakeoff_{run_slug}.jsonl"
    summary_path = jsonl_path.with_suffix(".md")
    records: list[dict[str, Any]] = []

    for variant in variants:
        if variant not in PROMPT_VARIANTS:
            raise SystemExit(f"Unknown variant: {variant}")
        for scenario in scenarios:
            options = dict(PROMPT_VARIANTS[variant])
            options["num_ctx"] = int(args.num_ctx)
            include_schema_in_prompt = bool(args.include_schema_in_prompt)
            if backend != "lmstudio":
                include_schema_in_prompt = not bool(args.omit_schema_in_prompt)
            record = {
                "ts": _utc_now(),
                "backend": backend,
                "model": model,
                "variant": variant,
                "scenario_id": scenario["id"],
                "domain": scenario["domain"],
                "options": {k: v for k, v in options.items() if k not in {"system", "extra"}},
                "prompt_schema_included": include_schema_in_prompt,
            }
            print(f"[{_utc_now()}] {backend} {model} {variant} {scenario['id']}", flush=True)
            try:
                messages = build_messages(
                    variant=variant,
                    scenario=scenario,
                    include_schema_in_prompt=include_schema_in_prompt,
                )
                if backend == "lmstudio":
                    response = call_lmstudio(
                        base_url=base_url,
                        model=model,
                        messages=messages,
                        options=options,
                        timeout=int(args.timeout),
                        reasoning_effort=str(args.reasoning_effort or ""),
                        max_tokens=int(args.max_tokens),
                    )
                else:
                    response = call_ollama(
                        base_url=base_url,
                        model=model,
                        messages=messages,
                        options=options,
                        timeout=int(args.timeout),
                    )
                parsed, parse_error = parse_json_payload(response["content"])
                record.update(
                    {
                        "latency_ms": response["latency_ms"],
                        "content": response["content"],
                        "content_channel": response.get("content_channel", "content"),
                        "parsed": parsed,
                        "parsed_ok": parsed is not None,
                        "parse_error": parse_error,
                        "score": score_record(parsed, scenario),
                    }
                )
            except Exception as exc:
                record.update(
                    {
                        "latency_ms": 0,
                        "content": "",
                        "parsed": None,
                        "parsed_ok": False,
                        "parse_error": str(exc),
                        "score": score_record(None, scenario),
                    }
                )
            records.append(record)
            with jsonl_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    write_summary(records, summary_path)
    print(f"Wrote {jsonl_path}")
    print(f"Wrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
