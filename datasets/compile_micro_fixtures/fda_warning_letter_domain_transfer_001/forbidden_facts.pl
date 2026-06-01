% Forbidden facts for fda_warning_letter_domain_transfer_001.
% Each pattern represents an obvious cheat that must NOT appear in a compile.

% paragraph/prose-shaped violation category instead of a governed atom
fda_violation(V, L, violation_2, 'failed to prevent microbiological contamination of sterile products', Src).

% full rule text packed into the citation slot instead of a compact citation token
fda_violation_citation(V, 'twenty one CFR 211.113(b) control of microbiological contamination text', cgmps_requirement, Src).

% full response instruction collapsed into one atom
fda_response_requirement(L, written_response, fifteen_working_days, fda, 'notify the office in writing of all steps taken within fifteen working days', Src).

% source excerpt / summary smuggled in as a detail value
fda_violation_detail(V, affected_product, 'summary of the warning letter findings', violation_scope, Src).

% inferred contact / party not present in the source
fda_correspondence_party(L, Contact, contact, jane_roe, Src).

% inferred repeat-observation context not stated by the source
fda_conclusion_scope(L, repeat_observation_context, prevent_recurrence, Src).

% fabricated prior warning letter (none is source-stated)
fda_prior_warning_letter(W, L, v_2024_01_01, prior_letter, Src).

% fabricated regulatory meeting / teleconference (none is source-stated)
fda_regulatory_meeting(M, L, v_2025_07_01, Src).

% MARCS/WL number must not be treated as a facility identifier such as FEI
fda_facility_identity(Facility, apothecary_pharma_llc, Location, 717972, Src).
