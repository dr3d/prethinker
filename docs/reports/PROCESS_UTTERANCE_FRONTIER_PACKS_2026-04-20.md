# Process Utterance Frontier Packs

- These packs are distilled from real forge failures and warnings.
- They are meant to be durable replay targets for the hardest current `process_utterance()` families.
- They intentionally keep `Freethinker` out of the loop for now so `v1` improvements remain honest.

## Packs

- correction pack: `12` cases
- temporal pack: `12` cases

## Correction Pack

- `correction_01_actually_no_notification_history_is_with_jax_not`: setup=`remember that notification history is with Priya` target=`actually no, notification history is with Jax not Priya` baseline=`fail/error`
- `correction_02_actually_no_archive_ledger_is_with_blake_not_jan`: setup=`remember that archive ledger is with Jan` target=`actually no, archive ledger is with Blake not Jan` baseline=`fail/error`
- `correction_03_actually_no_cart_is_with_fred_not_mara`: setup=`remember that cart is with Mara` target=`actually no, cart is with Fred not Mara` baseline=`fail/error`
- `correction_04_actually_no_cart_is_with_mara_not_scott`: setup=`remember that cart is with Scott` target=`actually no, cart is with Mara not Scott` baseline=`fail/error`
- `correction_05_actually_no_cart_is_with_theo_not_lena`: setup=`remember that cart is with Lena` target=`actually no, cart is with Theo not Lena` baseline=`fail/error`
- `correction_06_actually_no_cart_is_with_wilma_not_priya`: setup=`remember that cart is with Priya` target=`actually no, cart is with Wilma not Priya` baseline=`fail/error`
- `correction_07_actually_no_drone_kestrel_is_with_blake_not_sele`: setup=`remember that drone kestrel is with Selene` target=`actually no, drone kestrel is with Blake not Selene` baseline=`fail/error`
- `correction_08_actually_no_drone_kestrel_is_with_fred_not_selen`: setup=`remember that drone kestrel is with Selene` target=`actually no, drone kestrel is with Fred not Selene` baseline=`fail/error`
- `correction_09_actually_no_drone_kestrel_is_with_lena_not_noor`: setup=`remember that drone kestrel is with Noor` target=`actually no, drone kestrel is with Lena not Noor` baseline=`fail/error`
- `correction_10_actually_no_drone_kestrel_is_with_mara_not_selen`: setup=`remember that drone kestrel is with Selene` target=`actually no, drone kestrel is with Mara not Selene` baseline=`fail/error`
- `correction_11_actually_no_drone_kestrel_is_with_nora_not_wilma`: setup=`remember that drone kestrel is with Wilma` target=`actually no, drone kestrel is with Nora not Wilma` baseline=`fail/error`
- `correction_12_actually_no_launch_plan_is_with_noor_not_blake`: setup=`remember that launch plan is with Blake` target=`actually no, launch plan is with Noor not Blake` baseline=`fail/error`

## Temporal Pack

- `temporal_01_at_step_11_noor_was_in_galley_and_later_moved_to`: target=`at step 11 Noor was in Galley and later moved to Cedar House.` baseline=`fail/error` tags=`parse_error, validation_failure, logic_break`
- `temporal_02_at_step_11_noor_was_in_galley_and_later_moved_to`: target=`at step 11 Noor was in Galley and later moved to Salem.` baseline=`fail/error` tags=`parse_error, temporal_logic_failure, validation_failure`
- `temporal_03_at_step_6_noor_was_in_bay_3_and_later_moved_to_m`: target=`at step 6 Noor was in Bay 3 and later moved to Mudroom.` baseline=`fail/error` tags=`parse_error, validation_failure, logic_break`
- `temporal_04_at_step_11_noor_was_in_galley_and_later_moved_to`: target=`at step 11 Noor was in Galley and later moved to Pineglass Ridge.` baseline=`fail/error` tags=`parse_error, validation_failure, temporal_logic_break`
- `temporal_05_at_step_11_noor_was_in_harbor_city_and_later_mov`: target=`at step 11 Noor was in Harbor City and later moved to Market Hall.` baseline=`fail/error` tags=`parse_error, validation_failure, logic_break`
- `temporal_06_at_step_11_fred_was_in_salem_and_later_moved_to_`: target=`at step 11 Fred was in Salem and later moved to Harbor City.` baseline=`fail/error` tags=`parse_error, temporal_logic_failure, validation_failure`
- `temporal_07_at_9_am_friday_jax_was_in_salem_and_later_moved_`: target=`at 9 AM Friday Jax was in Salem and later moved to Morro Bay.` baseline=`warn/success` tags=`temporal_logic, over_clarification, brittle_parsing`
- `temporal_08_next_week_hope_was_in_pineglass_ridge_and_later_`: target=`next week Hope was in Pineglass Ridge and later moved to Market Hall.` baseline=`warn/success` tags=`temporal_ambiguity, implicit_sequence, over_simplification`
- `temporal_09_next_week_wilma_was_in_mudroom_and_later_moved_t`: target=`next week Wilma was in Mudroom and later moved to Market Hall.` baseline=`warn/success` tags=`temporal_mismatch, context_ignored`
- `temporal_10_at_step_11_theo_was_in_morro_bay_and_later_moved`: target=`at step 11 Theo was in Morro Bay and later moved to Market Hall.` baseline=`warn/success` tags=`temporal_conflict, over_clarification, logic_inconsistency`
- `temporal_11_at_step_11_jan_was_in_salem_and_later_moved_to_g`: target=`at step 11 Jan was in Salem and later moved to Galley.` baseline=`warn/success` tags=`temporal_ambiguity, brittle_parsing`
- `temporal_12_next_week_jan_was_in_galley_and_later_moved_to_m`: target=`next week Jan was in Galley and later moved to Mudroom.` baseline=`warn/success` tags=`temporal_ambiguity, over_clarification`
