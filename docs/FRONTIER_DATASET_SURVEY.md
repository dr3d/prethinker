# Frontier Dataset Survey

Last updated: 2026-04-28

This note collects promising public or research-access sources for building
harder Prethinker frontier packs. The goal is not to hoard data. The goal is to
find source material that stresses governed semantic intake:

```text
source text -> semantic_ir_v1 proposal -> deterministic admission -> KB/query/trace
```

## Best Near-Term Targets

| Source | Access / License Caveat | Why It Helps |
| --- | --- | --- |
| [CUAD](https://www.atticusprojectai.org/cuad/) | CC BY 4.0 | Public contracts with clause spans. Strong for obligations, exceptions, termination, audit rights, and source-span fidelity. |
| [ContractNLI](https://arxiv.org/abs/2110.01799) | Public research dataset; verify repo terms before vendoring | Contract entailment, contradiction, and neutral examples. Good for exception semantics and not-mentioned rejection. |
| [MAUD](https://www.atticusprojectai.org/maud) | CC BY 4.0 | Merger agreements with expert labels. Useful for long-instrument intake and clause/question mapping. |
| [LegalBench-RAG](https://github.com/zeroentropy-ai/legalbenchrag) | MIT code; source datasets carry their own terms | Exact file and character-span retrieval tasks over legal datasets. Very aligned with provenance-gated admission. |
| [LegalBench](https://hazyresearch.stanford.edu/legalbench/) | Mixed per-task licenses | Useful legal task patterns: rule application, holdings, hearsay, interpretation, private right of action. |
| [MeetingBank](https://arxiv.org/abs/2305.17529) | Reported CC BY-NC-ND 4.0; verify distribution terms | City council meetings, minutes, agendas, and metadata. Good for public commitments, motions, votes, and deadlines. |
| [QMSum](https://github.com/Yale-LILY/QMSum) | MIT | Query-focused meeting summaries. Good for "what was decided about X?" with source support pressure. |
| [Vancouver archival council minutes](https://data.opendatasoft.com/explore/dataset/council-meeting-minutes-archival%40vancouver/?flg=en-us) | Open city data; OCR quality varies | Noisy public-record stressor for names, dates, motions, and malformed spans. |
| [ParlaMint](https://link.springer.com/article/10.1007/s10579-021-09574-0) | Open via CLARIN; licenses vary by corpus | Multilingual parliamentary proceedings with speakers and metadata. Useful for speaker/source attribution and multilingual policy turns. |
| [MedNLI](https://www.physionet.org/content/mednli/1.0.0/) | PhysioNet credentialed access | Clinical entailment/contradiction/neutral grounded in notes. Good for bounded medical-memory admission. |
| [RadNLI](https://www.physionet.org/content/radnli-report-inference/1.0.0/) | PhysioNet credentialed access | Radiology inference. Good for findings, absence, uncertainty, and temporal comparisons. |
| [PubMedQA](https://arxiv.org/abs/1909.06146) | Public biomedical QA | Yes/no/maybe source-backed biomedical answers. "Maybe" should stay insufficient evidence, not a hard KB fact. |
| [MedSafetyBench](https://github.com/AI4LIFE-GROUP/med-safety-bench) | MIT; research-only safety warning | Medical safety boundary tests for rejecting treatment/dose/procedural advice while preserving safe memory. |
| [TKGQA](https://www.mdpi.com/2306-5729/8/3/61) | CC BY 4.0 dataset on OSF | Temporal KG updates and QA. Strong candidate for truth-maintenance and dependency invalidation tests. |
| [FActScore](https://github.com/shmsw25/factscore) | Public repo; check data terms | Atomic factual decomposition with source support. Useful evaluation pattern for narrative-to-atom admission. |
| [QAGS](https://github.com/W4ngatang/qags) | Public repo; check dataset-derived licenses | Factual consistency via QA against source. Useful source-fidelity scoring pattern. |

## Test-Pack Concepts

1. **Council Commitment Admission Pack**  
   From MeetingBank, QMSum, or municipal minutes: motions, votes, assigned
   actions, deadlines, and responsible bodies. Admit only when speaker/body/date
   and source support are present.

2. **Contract Exception Pack**  
   From CUAD or ContractNLI: `must_notify`, `may_terminate`,
   `survives_termination`, exception clauses, survival clauses, and override
   ordering.

3. **Not-Mentioned Rejection Pack**  
   ContractNLI neutral cases should produce no durable facts, while still
   yielding traceable rejected or quarantined candidates.

4. **Legal Claim Status Pack**  
   CaseFacts/LegalBench-style claim verification: supported, refuted,
   overruled, quoted-only, and holding-only cases. Test claim/finding/holding
   separation and temporal legal truth maintenance.

5. **Medical Bounded Memory Pack**  
   MedNLI/RadNLI/PubMedQA examples where only directly entailed
   patient/document facts become candidates. Reject unsafe advice and keep
   `maybe` as insufficient evidence.

6. **Multilingual Municipal Pack**  
   ParlaMint or Portuguese municipal minutes: speaker attribution, vote
   outcomes, committee referrals, and policy commitments in non-English text.

7. **OCR/Noisy Minutes Pack**  
   Vancouver archival minutes with OCR artifacts: force conservative parsing,
   malformed-name quarantine, and date/source clarification.

8. **Truth-Maintenance Pack**  
   TKGQA-style before/after updates: acquisition, leadership, status, or policy
   facts that invalidate dependent conclusions when a later source supersedes
   earlier support.

9. **Source-Fidelity Narrative Pack**  
   FActScore/QAGS-inspired long summaries: every admitted atom must point to a
   minimal source span; unsupported narrative flourishes stay out of the KB.

## Suggested First Pull

Start with CUAD + MeetingBank/QMSum + PubMedQA because they cover the three
active axes without immediately requiring credentialed clinical access:

- contracts: obligations, exceptions, and rules;
- meetings: commitments, votes, and policy source provenance;
- biomedical public abstracts: bounded evidence and insufficient-evidence
  behavior.

Generated slices should live under ignored `datasets/*/generated/` until a tiny
fixture is curated for `docs/data/`.
