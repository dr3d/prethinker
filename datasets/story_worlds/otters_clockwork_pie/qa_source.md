Below is a **100-question test battery** for the Tilly/Otter story KB. I'm treating this as a **GIC benchmark**: each row gives the question, the expected answer, and a likely mistake your ingestion/compiler/reasoner may make.

Use these to test whether the system handles **entities, ownership, event order, causality, permission, inference, negation, final state, and moral abstraction**.

---

# 1-10: Core entity and setting recognition

|  # | Question                                                  | Expected answer                                                                | Likely mistake / why                                                                 |
| -: | --------------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ |
|  1 | Who lives in the willow-root house                       | The Little Slip of an Otter, the Middle-sized Otter, and the Great Long Otter. | May answer "three bears" because of Goldilocks contamination from the prompt source. |
|  2 | What species are the household members                   | They are otters.                                                               | May classify them generically as animals but miss `otter/1`.                         |
|  3 | Where is the house located                               | Beneath the roots of a willow tree, in a wood, beside a bright running river.  | May choose only one location and drop containment/adjacency relations.               |
|  4 | Who is the outsider who enters the house                 | Tilly Tumbletop.                                                               | May call her Goldilocks due to similarity with source tale.                          |
|  5 | Who sent Tilly on an errand                              | Her aunt.                                                                      | May infer "mother" from Goldilocks structure.                                        |
|  6 | What was Tilly supposed to fetch                         | Blue thread and pepper.                                                        | May omit one item or turn them into food items for the otters.                       |
|  7 | What kind of day was it for the Little Slip of an Otter  | His half-birthday.                                                             | May call it a birthday, losing the whimsical "half-birthday" detail.                 |
|  8 | What did the otters bake                                 | A clockwork pie.                                                               | May encode merely as `pie` and lose the clockwork/magical property.                  |
|  9 | What ingredients or components were in the clockwork pie | Apples, moon-sugar, and six little brass wheels.                               | May treat brass wheels as metaphorical rather than literal objects.                  |
| 10 | Why did the otters leave the house                       | To gather mint while the clockwork pie cooled / stopped ticking too fiercely.  | May say they went for a walk, copying the Goldilocks structure.                      |

---

# 11-20: Objects, sizes, and ownership

|  # | Question                                                        | Expected answer                                                                | Likely mistake / why                                                              |
| -: | --------------------------------------------------------------- | ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- |
| 11 | Which otter owns the little mug                                | The Little Slip of an Otter.                                                   | May infer all mugs are shared household property only.                            |
| 12 | Which otter owns the middle-sized boots                        | The Middle-sized Otter.                                                        | May confuse middle-sized object ownership with Tilly after she uses them.         |
| 13 | Which otter owns the great boat                                | The Great Long Otter.                                                          | May map "great" to quality instead of size.                                       |
| 14 | What objects come in little, middle, and great versions        | Mugs, boots, boats, and knives/slices in the later scene.                      | May only list the first three recurring household objects.                        |
| 15 | What was the little boat designed for                          | It was made for otters, not queens / not a human child pretending to be queen. | May miss the "designed_for" inference and say "rowing."                           |
| 16 | Whose half-birthday wheels were swallowed                      | The Little Slip of an Otter's half-birthday wheels.                            | May say the wheels belonged to Tilly because they ended up inside her.            |
| 17 | What object did the otters use to remove the wheels from Tilly | The pie-key.                                                                   | May invent a doctor, magnet, spoon, or medicine.                                  |
| 18 | Where were the boats                                           | In the rain-barrel.                                                            | May put them in the river because otters and boats suggest river use.             |
| 19 | What was inside the middle boat                                | Rules, including Rule Number Seven.                                            | May treat the rule as narrator commentary rather than an object/text in the boat. |
| 20 | Which object had holes danced into it                          | The little boots.                                                              | May say the little boat was damaged, mixing the boot and boat consequences.       |

---

# 21-30: Tilly's errand and distractions

|  # | Question                                                  | Expected answer                                                                              | Likely mistake / why                                                                   |
| -: | --------------------------------------------------------- | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| 21 | What did Tilly do instead of running her errand properly | She poked sticks into puddles, counted beetles, and followed a goose-shaped cloud.           | May summarize as "she played" and lose individual facts.                               |
| 22 | Did Tilly remember the blue thread clearly               | No. She forgot the blue thread.                                                              | May assume she remembered because she later has it when going home.                    |
| 23 | Did Tilly entirely forget the pepper                     | No. She had only a hazy notion of pepper.                                                    | May collapse "hazy notion" into total forgetting.                                      |
| 24 | Did Tilly arrive at the house because she was invited    | No. She found it while wandering/distracted.                                                 | May infer invitation because the otters are hospitable.                                |
| 25 | How did Tilly inspect the house before entering          | She looked in the round window, peeped through the chimney-hole, and tapped the door softly. | May skip the chimney-hole as too odd or improbable.                                    |
| 26 | Did anyone answer Tilly's tap                            | No. Nobody answered.                                                                         | May infer silence means nobody was home, which is true, but should preserve the event. |
| 27 | Why was Tilly's tap described as sneaky                  | She tapped softly so she could claim she had knocked without truly making a proper attempt.  | May miss the intent behind the action.                                                 |
| 28 | Was Tilly described as properly polished                 | No. She was "not polished," only "rubbed about at the edges."                                | May interpret literally as physically dirty rather than morally/socially unpolished.   |
| 29 | What should a polite child have done                     | Wait outside and say something like, "Good morning, Otters, I believe I am lost."            | May treat this hypothetical as an event that actually happened.                        |
| 30 | Did Tilly enter through force                            | No. She lifted the latch and entered without permission.                                     | May incorrectly encode burglary/forced entry.                                          |

---

# 31-40: Pie-testing sequence

|  # | Question                                                | Expected answer                                                              | Likely mistake / why                                                  |
| -: | ------------------------------------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 31 | What did Tilly see on the windowsill                   | The clockwork pie.                                                           | May say porridge due to Goldilocks template contamination.            |
| 32 | What did Tilly say about the ticking pie               | "A pie that ticks! That must be a pie in a hurry."                           | May paraphrase correctly but fail to attach it as direct speech.      |
| 33 | Which knife did Tilly use first                        | The Great Long Otter's great knife.                                          | May omit tools and only encode eating.                                |
| 34 | What was wrong with the great slice                    | It ticked too quickly and chased her fork around the plate.                  | May encode "too hot" from Goldilocks.                                 |
| 35 | What was wrong with the middle slice                   | It ticked too slowly, making her wait for the raisins.                       | May encode "too cold" from Goldilocks.                                |
| 36 | What was right about the little slice                  | It ticked in a merry, comfortable rhythm.                                    | May just say "it tasted good," missing the rhythm comparison.         |
| 37 | Which slice did Tilly eat all up                       | The little pie slice.                                                        | May say she ate the whole clockwork pie.                              |
| 38 | What did Tilly swallow by eating the little slice      | Six brass wheels.                                                            | May fail to propagate components of the slice into swallowed objects. |
| 39 | What immediate bodily effect did the pie have on Tilly | Her stomach buzzed and later tick-tocked.                                    | May encode only the later ticking and miss the buzzing.               |
| 40 | Why is eating the brass wheels important               | It causes the ticking-stomach problem and later requires the pie-key remedy. | May treat it as comic decoration without causal importance.           |

---

# 41-50: Boots sequence

|  # | Question                                     | Expected answer                                                        | Likely mistake / why                                                    |
| -: | -------------------------------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 41 | What did Tilly try after eating the pie     | The three pairs of boots.                                              | May jump directly to boats because both involve movement.               |
| 42 | What happened with the great boots          | Each boot walked in a different direction and took her legs with them. | May reduce to "too big," losing magical behavior.                       |
| 43 | How did Tilly judge the great boots         | They were too wandering.                                               | May normalize to "too large," which is not the story's stated judgment. |
| 44 | What happened with the middle boots         | They refused to move unless she stated her errand clearly.             | May miss that boots enforce a rule-like condition.                      |
| 45 | Why couldn't Tilly satisfy the middle boots | She could not state her errand clearly.                                | May say the boots did not fit, copying the physical-size pattern.       |
| 46 | How did Tilly judge the middle boots        | They were too particular.                                              | May say "too stiff" only, missing the rule/obedience aspect.            |
| 47 | How did Tilly judge the little boots        | Just mischievous enough.                                               | May map it to simply "just right," losing the special variation.        |
| 48 | What did the little boots do                | They began to dance.                                                   | May say Tilly chose to dance, losing boot agency.                       |
| 49 | Where did the dancing take Tilly            | Around the table, over the mat, under the stool, and into the pantry.  | May collapse the path into "into the pantry."                           |
| 50 | What did Tilly knock down in the pantry     | A jar of sugared minnows.                                              | May treat "sugared minnows" as fish in water, not sweets/food.          |

---

# 51-60: Boat sequence

|  # | Question                                      | Expected answer                                                                                     | Likely mistake / why                                                                      |
| -: | --------------------------------------------- | --------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 51 | What did Tilly decide to do after dancing    | Row in one of the boats.                                                                            | May infer she wanted to escape rather than play.                                          |
| 52 | Where did she climb into the great boat      | In the rain-barrel.                                                                                 | May put the great boat on the river.                                                      |
| 53 | What was wrong with the great boat           | It rocked grandly and splashed water into both her ears; it was too billowy.                        | May encode "too big" instead of "too billowy."                                            |
| 54 | What was wrong with the middle boat          | It had too many rules and was too bossy.                                                            | May treat the rules as spoken by the otters, not written/painted inside the boat.         |
| 55 | What was Rule Number Seven                   | "No rowing until all previous rules have been obeyed."                                              | May generate a plausible but nonexistent rule.                                            |
| 56 | Which boat did Tilly accept                  | The little boat.                                                                                    | May say little boat was objectively right, ignoring that it later fails under her weight. |
| 57 | What did Tilly pretend to be while rowing    | Queen of a lake.                                                                                    | May omit because it seems whimsical, but it matters for the "not made for queens" line.   |
| 58 | Why was the little boat unsuitable for Tilly | It was made for otters, and Tilly was heavier than an otter, especially after eating clockwork pie. | May say simply "because she was too heavy," losing the after-eating causal detail.        |
| 59 | What happened to the rain-barrel plug        | It popped out.                                                                                      | May miss plug entirely because it is a small event.                                       |
| 60 | What happened after the plug popped out      | Water rushed across the floor.                                                                      | May say the boat sank in the river instead of flooding the house floor.                   |

---

# 61-70: Return of the otters and discovery

|  # | Question                                                       | Expected answer                                                                                          | Likely mistake / why                                                          |
| -: | -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 61 | When did the otters return                                    | After gathering mint, after Tilly had eaten, danced, rowed, flooded the floor, and ended up in a puddle. | May place their return too early, before the boat sequence.                   |
| 62 | Who opened the door when the otters returned                  | The Great Long Otter.                                                                                    | May assign the action to the household collectively.                          |
| 63 | What did the Great Long Otter do after opening the door       | He sniffed.                                                                                              | May omit sensory evidence.                                                    |
| 64 | What did the otters first notice about the pie                | The great and middle slices had been cut, and the little slice had been eaten all up.                    | May say all the pie was gone.                                                 |
| 65 | Which otter complains that the little slice was eaten         | The Little Slip of an Otter.                                                                             | May assign all "someone has been..." lines to the Great Long Otter.           |
| 66 | What did the Great Long Otter infer about his boots           | Somebody had been walking in them.                                                                       | May say he saw Tilly wearing them, which is not the discovery sequence.       |
| 67 | What did the Middle-sized Otter infer about her boots         | Somebody had been arguing with them.                                                                     | May flatten to "someone wore them," losing comedy/inference.                  |
| 68 | What did the Little Slip of an Otter discover about his boots | Somebody had danced holes in them.                                                                       | May say they were merely dirty.                                               |
| 69 | What did the Little Slip of an Otter discover about his boat  | Somebody had sunk it all the way to the bottom.                                                          | May say it was broken but not sunk.                                           |
| 70 | What sound revealed Tilly's hiding place                      | Tilly sneezed from inside the pantry.                                                                    | May say her ticking stomach revealed her, which happened after she was found. |

---

# 71-80: Evidence on Tilly and diagnosis

|  # | Question                                                       | Expected answer                                                                                    | Likely mistake / why                                                        |
| -: | -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| 71 | Where was Tilly found                                         | In the pantry.                                                                                     | May say in the bed, copying Goldilocks.                                     |
| 72 | What condition was Tilly in when found                        | Dripping wet, with crumbs in her hair, sugared minnows in her pockets, and a tick-tocking stomach. | May list only one clue.                                                     |
| 73 | What was stuck to Tilly's sleeve earlier                      | A sugared minnow.                                                                                  | May confuse sleeve clue with pocket clue.                                   |
| 74 | Why did the Great Long Otter say the stomach sound was bad    | He said it was not a healthy sound for a child.                                                    | May answer medically instead of preserving his quoted judgment.             |
| 75 | What did the Middle-sized Otter say about the stomach ticking | "Nor a lawful one."                                                                                | May miss the legal/normative joke.                                          |
| 76 | What did the Little Slip of an Otter identify inside Tilly    | His half-birthday wheels.                                                                          | May say "the otters' wheels" and miss ownership/special occasion.           |
| 77 | Did Tilly deny responsibility at the end                      | No. She apologized and explained what happened.                                                    | May overgeneralize from earlier "That was not my fault."                    |
| 78 | What was Tilly's explanation                                  | She was sent for blue thread and pepper, and found a ticking pie instead.                          | May treat this as an excuse rather than an explanation attached to apology. |
| 79 | What did the Great Long Otter say about trouble               | "That is how trouble often begins."                                                                | May turn this into the final moral, though the final moral is different.    |
| 80 | Did the otters immediately punish Tilly harshly               | No. They gave her a towel, a sharp look, fixed the wheel problem, and made her repair the damage.  | May impose a harsher fairy-tale punishment from genre expectations.         |

---

# 81-90: Remedy, restitution, and final state

|  # | Question                                                 | Expected answer                                                                     | Likely mistake / why                                                     |
| -: | -------------------------------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| 81 | What did the Middle-sized Otter give Tilly              | A towel.                                                                            | May assign the towel to the Great Long Otter as leader.                  |
| 82 | What did the Little Slip of an Otter give Tilly         | A sharp look.                                                                       | May encode as a physical object rather than an expression/judgment.      |
| 83 | Where did the otters put Tilly to fix the wheel problem | On a stool.                                                                         | May say "in bed" due to Goldilocks contamination.                        |
| 84 | How did the otters remove the brass wheels              | They wound Tilly gently with the pie-key until the wheels clicked out of her mouth. | May invent vomiting, surgery, magic spell, or magnet.                    |
| 85 | How many brass wheels came out                          | Six.                                                                                | May answer "one" because the story describes them coming out one by one. |
| 86 | In what condition were the recovered wheels             | Quite clean and none the worse, except one had a tooth-mark.                        | May say they were damaged or digested.                                   |
| 87 | What did Tilly help mop                                 | The floor.                                                                          | May say the whole house, overgeneralizing.                               |
| 88 | What did Tilly help mend                                | The little boat.                                                                    | May say the little boots, mixing repair targets.                         |
| 89 | What did Tilly help polish                              | The boots.                                                                          | May say only the little boots, but the story says boots generally.       |
| 90 | What did the otters give Tilly after restitution        | A fresh slice of ordinary pie without machinery in it.                              | May say another clockwork pie slice, missing the "ordinary" contrast.    |

---

# 91-100: Higher-order reasoning, negation, moral, and traps

|   # | Question                                                                          | Expected answer                                                                                                                                                                                                                          | Likely mistake / why                                                                                                        |
| --: | --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
|  91 | Did Tilly leave with the errand items                                            | Yes. She left with blue thread and pepper.                                                                                                                                                                                               | May say no because she had forgotten them earlier.                                                                          |
|  92 | What extra item did Tilly leave with                                             | A sprig of mint.                                                                                                                                                                                                                         | May miss because it is a minor final-state object.                                                                          |
|  93 | What promise did Tilly make                                                      | Never again to enter a willow-root house without being asked.                                                                                                                                                                            | May generalize to "never enter any house," which is morally close but not exact.                                            |
|  94 | What sound remained in Tilly's memory                                            | Tick-tock.                                                                                                                                                                                                                               | May say her stomach literally continued ticking.                                                                            |
|  95 | What does the remembered tick-tock symbolize                                     | A warning/conscience: mind your manners before the pie does it for you.                                                                                                                                                                  | May treat the sound as an ongoing physical condition rather than moral memory.                                              |
|  96 | Was Tilly's final condition the same as her pantry condition                     | No. By the end she is no longer physically ticking, has apologized, helped repair damage, and leaves with a promise.                                                                                                                     | May fail to update final state after the remedy.                                                                            |
|  97 | Who is mostly responsible for the pantry mess                                    | Tilly, even though she says it was not her fault.                                                                                                                                                                                        | May believe the character's denial instead of narrator implication.                                                         |
|  98 | Was the little boat "just right" in every sense                                  | No. Tilly judged it right for rowing, but it was not actually suitable for her weight.                                                                                                                                                   | May treat subjective "just right" as objective safety.                                                                      |
|  99 | What is the main moral of the story                                              | Mind your manners before the pie does it for you.                                                                                                                                                                                        | May give generic "don't steal" or "don't go into strangers' houses," which is partly right but not the story's exact moral. |
| 100 | What makes this story structurally similar to Goldilocks but logically different | It has three householders, three sizes of objects, repeated testing, an intruding child, owner return, discovery, and moral consequence; but the entities, objects, actions, magical mechanics, causality, and resolution are different. | May overfit the original tale and import porridge, chairs, beds, bears, mother, sleeping, or running away.                  |

---

# Bonus: the nastiest failure modes to watch for

These are the mistakes I would especially expect from an English-to-Prolog GIC.

## 1. Template contamination

Because the story intentionally resembles **Goldilocks**, the model may hallucinate:

```prolog
bear(great_big_bear).
food(porridge).
object(chair).
object(bed).
event(_, goldilocks, sleep_in, little_bed, bedroom).
```

This is the big one. A strong GIC should **respect the current story over the source pattern**.

## 2. Losing whimsical literals

The model may treat absurd details as style rather than facts:

```text
clockwork pie
moon-sugar
six brass wheels
pie-key
rules painted inside the boat
stomach tick-tocking
```

For this test, those are not decorative. They are **causal facts**.

## 3. Collapsing all "just right" cases

A weak extraction may encode:

```prolog
just_right(little_pie_slice).
just_right(little_boots).
just_right(little_boat).
```

But the story actually has different judgment dimensions:

```prolog
ticking_speed
mischief_level
rowing_fit
```

The GIC should preserve **attribute-specific judgments**.

## 4. Confusing subjective judgment with objective truth

Tilly judges the little boat "just right," but it later sinks. That means:

```prolog
judged(tilly, little_boat, rowing_fit, just_right).
```

does **not** imply:

```prolog
safe_for(tilly, little_boat).
```

That is an excellent reasoning trap.

## 5. Missing final-state updates

During the story:

```prolog
stomach_condition(tilly, ticking).
sunk(little_boat).
flooded(floor).
```

By the end:

```prolog
wheels_recovered.
little_boat_mended.
floor_mopped.
tilly_no_longer_ticking.
```

A good reasoner must distinguish **ever happened** from **currently true at the end**.

## 6. Believing character speech as narrator truth

Tilly says:

```text
That was not my fault.
```

But the narrator says:

```text
though it mostly was.
```

The KB should preserve both:

```prolog
said(tilly, denial).
mostly_responsible_for(tilly, jar_incident).
```

This tests attribution and contradiction handling.

## 7. Under-modeling ownership

The story depends on whose object was used or damaged:

```prolog
owned_by(little_boat, little_slip_otter).
used_without_permission(tilly, little_boat).
damaged(little_boat).
```

A shallow parse may simply say "Tilly used a boat," losing the moral/norm layer.

## 8. Missing implicit norm violations

The story does not always say "this was wrong" directly. The GIC should infer:

```prolog
entered_without_permission.
ate_without_permission.
used_property_without_permission.
caused_damage.
owed_restitution.
```

But it should not over-punish or invent crimes beyond the text.

## 9. Failing event ordering

Many questions require sequence:

```text
Did Tilly apologize before or after the wheels were removed
Did the otters return before or after the boat sank
Did Tilly get ordinary pie before or after helping clean
```

The GIC needs event IDs or temporal indices.

## 10. Not separating objects from events

For example:

```text
little_pie_slice
```

is an object/food.

```text
Tilly eating the little pie slice
```

is an event.

```text
the little pie slice being gone
```

is a resulting state.

A good KB needs all three layers.
