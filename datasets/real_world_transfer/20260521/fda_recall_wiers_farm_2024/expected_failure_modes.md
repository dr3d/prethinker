# Expected Failure Modes — fda_recall_wiers_farm_2024

The following are likely to be hard for any QA system reading this document, described generically:

- **Long compact identifiers.** Each retail-packaged product has a 12-digit UPC. Off-by-one digit errors, transposition, or partial truncation are easy mistakes.

- **Brand vs. company vs. seller confusion.** Wiers Farm is the company; Wiers Farm and Freshire Farms are the brand names; Walmart, Aldi, Kroger, Save-a-Lot, Shop N Save and others are sellers. A question about "the brand" can be answered with "the company" by mistake.

- **Two state agencies with similar acronyms.** MDARD (Michigan Department of Agriculture) reported the original positive finding; ODA (Ohio Department of Agriculture) cooperated in the investigation. Swapping the two is a plausible failure.

- **Multiple dates that all sit in mid-July 2024.** The original recall (July 12, 2024), the expansion announcement (July 22, 2024), and the FDA publish date (July 23, 2024) are easily confused, especially in compositional questions.

- **Per-state carve-outs inside the distribution table.** Many retailer rows include parentheticals such as "(cucumber only)" or "(cucumber, green bell pepper and pickling cucumber only)." A simple lookup that ignores parentheticals will overcount which products went to which retailer.

- **Implicit subjects in mid-paragraph sentences.** Sentences like "This expansion is in response to that investigation" and "Symptoms vary depending on the severity of the illness" inherit their subject from a prior sentence; resolving them out of order can drift.

- **Negative facts depend on prior context.** "There have been no illnesses or consumer complaints reported to date" needs to be retrieved as a negative-existence claim, not paraphrased into "few" or "some."

- **Two distinct product categories with separate listings.** Retail-packaged items list specific UPCs and sizes; bulk items list categories without UPCs. A question about UPCs that lands on a bulk item has no answer in the source.

- **Boilerplate vs. fact.** The general *Listeria monocytogenes* description is generic health-information boilerplate; readers may attribute boilerplate claims (about pregnant women, immunocompromised individuals, etc., or — in different versions of similar notices — those phrases) to this specific recall.

- **Headline-vs-body mismatch.** The headline mentions "cucumbers," but the expanded recall covers many other produce items; a heuristic that trusts the headline misses most of the distribution detail.

- **State abbreviation lists.** The retail-Walmart distribution list and the bulk-distribution state list overlap but do not match exactly; counting or comparing states across the two lists is a real composition task.
