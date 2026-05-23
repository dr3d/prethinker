# Expected Failure Modes — cpsc_recall_polaris_rzr200_2023

Generically, these features are likely to be hard for any QA system reading this document:

- **Cluster of small integers that are all "2".** The Incidents/Injuries paragraph names "32 reports", "two reports of crashes", "two reports of rollover/tip over", and "two injuries". A question that asks for one of the twos can easily return the 32, or vice-versa.

- **Two unit counts close together.** ~19,000 U.S. units vs. ~950 Canadian units. A retrieval system that grabs the first number it sees may answer with the wrong total.

- **U.S. vs. global scope.** The notice is a CPSC (U.S.) recall but is "In Conjunction With" Transport Canada. Questions about "how many were sold" require disambiguating "in the U.S." vs. "globally."

- **Date confusion between sale window and recall date.** Units were sold "May 2021 through September 2023"; the recall was announced December 14, 2023. A model may treat the sale-window end-date as the recall date.

- **Importer location vs. manufacturing location.** Importer is in Medina, Minnesota; vehicles were manufactured in China. Confusing the two is plausible.

- **Multiple phone numbers in the same notice.** Polaris consumer line (800-765-2747), CPSC hotline (800-638-2772), CPSC TTY (800-638-8270). All are 1-800 numbers and easy to swap.

- **A side-of-vehicle question with no answer.** The notice says the model name is printed "on the side of the chassis" without specifying left or right. A question that asks which side has only the indeterminate answer; a confident guess is a hallucination.

- **Branding marks distributed across surfaces.** "POLARIS" is stamped on the front grille; "POLARIS and RZR" are printed on the sides; the model name is also on the side of the chassis. A consolidated answer that says "POLARIS appears on the sides" loses precision.

- **Negative facts framed indirectly.** "Individual Commissioners may have statements related to this topic" tells the reader that statements are not in this document but may exist externally — a subtle indirect negation.

- **Price range vs. single price.** Vehicles sold "for between $6,300 and $7,500"; a single-number answer is wrong.

- **Boilerplate "About the CPSC" section.** The closing boilerplate talks about $1 trillion annually in product-related costs and the CPSC being established 50 years ago. These are not facts about *this recall*; treating them as such is an attribution error.

- **Hazard-vs-incident wording.** The Hazard field describes potential ("can lock up"); the Incidents field describes what has actually been reported. A question about whether anyone has actually been injured needs the latter, not the former.

- **Recall classification.** The notice labels itself a "Fast Track Recall." This is an internal CPSC processing classification, not a hazard class. Confusing it with "Class I/II/III" is plausible.

- **Remedy field is one word, supplemented by a paragraph.** "Remedy: Repair" appears in the summary fields; the full description requires the consumer to stop use, contact a dealer, and schedule a free replacement of the steering rack assembly. A question about "what is the remedy" can be partially correct (Repair) but miss the procedural specifics.
