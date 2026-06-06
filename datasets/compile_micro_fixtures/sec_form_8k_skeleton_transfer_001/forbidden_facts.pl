sec_filing(Filing, form_8_k, servicenow_inc_form_8_k_current_report_date_of_report_december_23_2025, v_2025_12_23, v_2025_12_23, SrcFiling).
sec_registrant(Filing, servicenow_inc, delaware_001_35580_20_2056195, SrcRegistrant).
sec_registrant_identifier(Filing, servicenow_inc, identifier_bundle, file_001_35580_ein_20_2056195_phone_408_501_8550_ticker_now, SrcIdentifiers).
sec_registrant_identifier(Filing, Registrant, cik, CikValue, SrcCik).
sec_filing_item(Filing, item_5_02, employment_agreement_amendment_with_william_r_mcdermott_and_executive_severance_policy_terms, substantive, SrcItem502).
sec_exhibit(Filing, exhibit_10_1, amendment_no_3_to_employment_agreement_between_the_registrant_and_william_r_mcdermott, filed, SrcExhibit101).
sec_exhibit(Filing, exhibit_104, cover_page_interactive_data_file_the_cover_page_xbrl_tags_are_embedded_within_the_inline_xbrl_document, not_stated, SrcExhibit104).
sec_signatory(Filing, servicenow_inc_by_s_russell_s_elmer_russell_s_elmer_general_counsel_date_december_23_2025, general_counsel, v_2025_12_23, SrcSignature).

% Source-only review `sec_t001_source_review_20260605` rejected these candidate
% variants. The exhibit table does not state filed/furnished treatment,
% service_now_inc/svc_now_inc are not faithful encodings of "ServiceNow, Inc.",
% and sec_material_event_ugly_003 is a fixture/source label, not a filing_id.
sec_exhibit(Filing, exhibit_10_1, agreement, filed, SrcExhibit101).
sec_exhibit(Filing, exhibit_10_2, other_exhibit, filed, SrcExhibit102).
sec_exhibit(Filing, exhibit_104, cover_page_ixbrl, filed, SrcExhibit104).
sec_registrant(Filing, service_now_inc, delaware, SrcRegistrant).
sec_registrant(Filing, svc_now_inc, delaware, SrcRegistrant).
sec_registrant_identifier(Filing, service_now_inc, commission_file_number, file_001_35580, SrcFileNumber).
sec_registrant_identifier(Filing, svc_now_inc, commission_file_number, file_001_35580, SrcFileNumber).
sec_exhibit(sec_material_event_ugly_003, exhibit_10_1, agreement, filed, SrcExhibit101).
sec_exhibit(sec_material_event_ugly_003, exhibit_10_2, other_exhibit, filed, SrcExhibit102).
sec_exhibit(sec_material_event_ugly_003, exhibit_104, cover_page_ixbrl, not_stated, SrcExhibit104).
