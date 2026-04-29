# The Glitch in the Airlock - Comprehension Battery

## How To Use

1. Run ingest scenario: `kb_scenarios/story_glitch_in_the_airlock_roundtrip.json`
2. Run interrogation scenario: `kb_scenarios/story_glitch_in_the_airlock_interrogation.json`
3. Prefer the current Semantic IR/Lava cases that cover Glitch source-fidelity,
   identity, claim-vs-fact, and predicate-drift edges. The older golden-KB
   parser comparison lane has been retired from the working tree.

## Query Dialog (Fact Recall)

- `query is_a(jax, freelance_space_salvager).`
- `query has_habit(jax, borrows_oxygen_without_permission).`
- `query scouting_in(jax, nebula_sector).`
- `query too_radioactive(mega_cell, jax).`
- `query too_sluggish(eco_cell, jax).`
- `query just_right_for(nano_cell, jax).`
- `query too_heavy(titan_boots, jax).`
- `query too_floaty(hover_slippers, jax).`
- `query blew_fuse(sonic_zips).`
- `query charred(sonic_zips).`
- `query too_cold(cryo_chamber, jax).`
- `query too_squishy(memory_foam_cloud, jax).`
- `query slept_in(jax, bio_hammock).`
- `query returned_from(unit_alpha, morning_spacewalk).`
- `query returned_from(unit_beta, morning_spacewalk).`
- `query returned_from(widget, morning_spacewalk).`
- `query reported(unit_alpha, siphoned(high_grade_isotopes)).`
- `query reported(widget, fried(sonic_zips_motherboards)).`
- `query saw(widget, asleep_in(jax, bio_hammock)).`
- `query saw(jax, unit_alpha).`
- `query saw(jax, unit_beta).`
- `query saw(jax, widget).`
- `query activated(jax, jetpack).`
- `query performed(jax, zero_gravity_backflip_through_airlock).`
- `query vanished_into(jax, starfield).`
- `query hoped_for(widget, leave_review_on_galactic_map(jax)).`
- `query liked(jax, fuel_of(widget)).`

## Negative Control Queries

- `query too_radioactive(nano_cell, jax).`
- `query too_floaty(titan_boots, jax).`
- `query slept_in(jax, cryo_chamber).`
- `query charred(hover_slippers).`

These should return `no_results`.
