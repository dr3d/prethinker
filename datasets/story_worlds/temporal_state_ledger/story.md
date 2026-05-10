# Tessmore Regional Water Authority
## Emergency Operations Packet — April–May 2026
### Event: Service Zone 2 contamination, 2026-04-28 through 2026-05-04
### Compiled: 2026-05-05 by Operations Officer K. Alvarez

---

## 0. Compiler's Note

This packet documents the contamination event in Service Zone 2 detected on 2026-04-28 and the cascade of notices, sampling, and lift procedures that followed. It includes the operative rules, the timestamped event log, two state-interval summaries, one timestamp correction, and a comparison between an early projected lift and the actual lift. All times are local, in 24-hour notation. The packet is intended for the regulator and for the Authority's operations review.

---

## 1. Operative Rules (excerpt from the Operations Manual, §6)

The following rules govern the lifting of a Boil-Water Notice ("BWN") and the related notification deadlines. They are reproduced as relevant.

**Rule §6.1 — Clear-sample requirement.** A BWN may be lifted only after twenty-four (24) consecutive hours of clear samples from the originating Sample Station, with no detection of indicator organisms during that period.

**Rule §6.2 — Clock reset on positive sample.** If, during the 24-hour clear-sample period, any sample at the originating Sample Station tests positive, the clear-sample clock resets to zero. The 24-hour count begins again at the first clear sample following the positive.

**Rule §6.2a — Clock pause on sampler offline.** During any period in which the originating Sample Station's automated sampler is offline (whether for malfunction, scheduled maintenance, or operator action), the clear-sample clock pauses. The clock resumes when the sampler is restored to normal operation. A pause does not constitute a positive sample and does not trigger §6.2.

**Rule §6.3 — 48-hour lift-notification deadline.** Once the 24-hour clear-sample requirement under §6.1 has been met, the Authority shall issue a formal Lift Notice no later than forty-eight (48) hours from the moment the requirement is met. If the 48-hour deadline falls on a Saturday, Sunday, or recognized public holiday, the deadline shifts to close of business (17:00) on the next business day.

**Rule §6.4 — Restricted-Use Notice independence.** A Restricted-Use Notice ("RUN") issued for an adjacent zone may be lifted independently of the BWN, subject to its own 24-hour clear requirement. RUN deadlines under §6.3 are computed separately.

**Rule §6.5 — Timestamp correction.** A logged event timestamp may be corrected if a clock or device is found to have been miscalibrated, provided the underlying event is otherwise valid. The corrected timestamp replaces the original for all rule computations; the event itself is not invalidated.

---

## 2. Event Log — Service Zone 2 Contamination (chronological)

All times local. Where a row contains both an "as-logged" and a "corrected" timestamp, the corrected timestamp is operative for all rule computations under §6.5.

| Event ID | As-logged time | Corrected time | Description |
|---|---|---|---|
| E-01 | 2026-04-28 06:14 | — | Contamination detected at Sample Station S-3 (E. coli positive) |
| E-02 | 2026-04-28 08:00 | — | Boil-Water Notice **BWN-2026-04-28-A** issued for Service Zone 2 |
| E-03 | 2026-04-28 09:30 | — | Restricted-Use Notice **RUN-2026-04-28-B** issued for Service Zone 3 |
| E-04 | 2026-04-29 04:45 | 2026-04-29 03:45 | Sampler at S-3 fails (cause: power supply fault) |
| E-05 | 2026-04-29 14:20 | — | Sampler at S-3 restored; sampling resumes |
| E-06 | 2026-04-30 09:00 | — | Sample at S-3 tests positive (E. coli); §6.2 reset triggered |
| E-07 | 2026-04-30 15:00 | — | First clear sample at S-3 after positive; clear-sample clock starts |
| E-08 | 2026-05-01 09:00 | — | Routine sampler maintenance window opens; sampler offline; §6.2a pause begins |
| E-09 | 2026-05-01 11:00 | — | Maintenance complete; sampler resumes; §6.2a pause ends |
| E-10 | 2026-05-01 17:00 | — | 24-hour clear-sample requirement met (15:00 to 15:00 nominal, plus two hours of pause under §6.2a) |
| E-11 | 2026-05-01 17:30 | — | Operations Officer Alvarez logs §6.1 satisfied; §6.3 48-hour clock starts |
| E-12 | 2026-05-04 12:00 | — | Lift Notice **LFT-2026-05-04** issued for Service Zone 2 |
| E-13 | 2026-05-04 13:00 | — | Restricted-Use Notice for Service Zone 3 lifted (RUN-2026-04-28-B closed) |

Twelve entries above correspond to thirteen events; E-04 and E-05 are paired sampler-state changes.

### Note on E-04 (timestamp correction).

When the sampler at Station S-3 went offline on 2026-04-29, the as-logged timestamp on the local controller was 04:45. During post-event review on 2026-05-02, the Authority's metrology technician determined that the sampler controller's internal clock had drifted one hour ahead of the Authority's master clock. Under Rule §6.5, the corrected timestamp 2026-04-29 03:45 is operative for all rule computations. The underlying event — sampler offline — is not invalidated. The discrepancy of one hour does not affect any rule computation in this packet because no clear-sample countdown was active during the sampler offline period; however, the Authority records the correction for completeness.

---

## 3. State-Interval Summaries

The following intervals describe the duration over which each notice or operational state was active.

### 3.1 Boil-Water Notice in Service Zone 2

The BWN-2026-04-28-A notice was active from 2026-04-28 08:00 (issuance, E-02) until 2026-05-04 12:00 (lift, E-12). Total active duration: 6 days, 4 hours.

### 3.2 Restricted-Use Notice in Service Zone 3

The RUN-2026-04-28-B notice was active from 2026-04-28 09:30 (issuance, E-03) until 2026-05-04 13:00 (lift, E-13). Total active duration: 6 days, 3 hours, 30 minutes.

### 3.3 Sampler offline at Station S-3

The sampler at Station S-3 was offline twice during the event:

- First offline interval: 2026-04-29 03:45 (E-04 corrected) to 2026-04-29 14:20 (E-05). Duration: 10 hours, 35 minutes. Cause: power supply fault.
- Second offline interval: 2026-05-01 09:00 (E-08) to 2026-05-01 11:00 (E-09). Duration: 2 hours. Cause: routine sampler maintenance.

### 3.4 Clear-sample countdown active

The 24-hour clear-sample countdown under §6.1 was active in two segments separated by §6.2a pauses, but only one segment was needed because no positive samples occurred during the countdown:

- Active segment, part one: 2026-04-30 15:00 (E-07) to 2026-05-01 09:00 (E-08). Counted: 18 hours.
- Pause: 2026-05-01 09:00 to 2026-05-01 11:00. Counted: 0 hours (paused).
- Active segment, part two: 2026-05-01 11:00 (E-09) to 2026-05-01 17:00 (E-10). Counted: 6 hours.

Total counted: 24 hours. Requirement met at 2026-05-01 17:00.

---

## 4. Deadline Computation under §6.3

The 24-hour clear-sample requirement was met at **2026-05-01 17:00**, a Friday. The §6.3 48-hour deadline therefore falls at **2026-05-03 17:00**, a Sunday.

Under §6.3, when the deadline falls on a Saturday, Sunday, or recognized public holiday, the deadline shifts to **close of business (17:00) on the next business day**. The next business day after Sunday 2026-05-03 is Monday 2026-05-04. The adjusted deadline is therefore **2026-05-04 at 17:00**.

The Lift Notice LFT-2026-05-04 was issued at **2026-05-04 12:00**, which is five hours before the adjusted deadline. The Authority therefore satisfied §6.3 with the weekend shift applied.

If the weekend shift had not been applied, the Authority would have missed the original Sunday deadline by 19 hours.

---

## 5. Comparison: Earlier Projected Lift vs. Actual Lift

On **2026-04-29 16:00**, before the second positive sample at 2026-04-30 09:00, the Authority's operations desk circulated an internal projection memo (OPS-PROJ-04-29) stating that, if no further positive samples were detected, the BWN was expected to be lifted on the morning of **2026-05-02**. This projection was conditional and was made before the second positive sample (E-06).

The actual lift occurred on **2026-05-04 at 12:00**, two days and roughly four hours after the projection. The discrepancy is wholly accounted for by the §6.2 reset triggered by the 2026-04-30 09:00 positive sample, which had not yet occurred at the time of the projection.

The earlier projection should not be cited as an announcement, schedule, or commitment. It was an internal projection only and was superseded by events.

---

## 6. Notification Cross-Reference

| Notice | Issued | Lifted | Service Zone | Reference |
|---|---|---|---|---|
| BWN-2026-04-28-A | 2026-04-28 08:00 | 2026-05-04 12:00 | Zone 2 | E-02 / E-12 |
| RUN-2026-04-28-B | 2026-04-28 09:30 | 2026-05-04 13:00 | Zone 3 | E-03 / E-13 |
| LFT-2026-05-04 | 2026-05-04 12:00 | — | Zone 2 | E-12 |

The Lift Notice LFT-2026-05-04 has no lift time of its own; once issued, it is the closing instrument for the BWN. The RUN closure on 2026-05-04 13:00 is recorded under E-13 and is not a separate Lift Notice.

---

## 7. Open Items

The following items remained open at packet close (2026-05-05):

- The cause of the 2026-04-28 contamination has been preliminarily attributed to a main-line break upstream of Station S-3, but the engineering review report has not yet issued. Expected by 2026-05-19. The preliminary attribution is based on visual inspection of the upstream main and on the Authority's hydraulic model; final attribution awaits a written report from the engineering review team and may revise the cause.
- The Authority has not yet determined whether OPS-PROJ-04-29 should have been suppressed or was appropriate as an internal projection. A procedure review is scheduled for 2026-05-13. The review will examine whether internal projections of this kind should be circulated outside the operations desk and, if so, under what conditions and with what disclaimers. The review's findings have not been issued.
- The metrology technician's report on the S-3 sampler-controller clock drift is recorded in working notes but has not been formally filed. A formal filing is expected by 2026-05-12. The working notes confirm the one-hour drift found during the 2026-05-02 review and form the basis for the §6.5 timestamp correction applied to E-04.

These open items do not affect the operative facts in §§ 1–6. In particular, the §6.3 deadline computation in §4 stands regardless of the engineering review's final attribution of cause and regardless of the procedure review's findings.

---

## 8. Personnel

The following personnel are referenced in this packet:

- **K. Alvarez** — Operations Officer, compiler of this packet, signatory of the §6.1-met log entry at E-11.
- **D. Pham** — Metrology Technician, performed the 2026-05-02 review of the S-3 sampler-controller clock drift.
- **R. Iyer** — Field Sampling Lead, attended the routine maintenance window E-08 / E-09 on 2026-05-01.
- **M. Cortes** — Communications Officer, drafted BWN-2026-04-28-A, RUN-2026-04-28-B, and LFT-2026-05-04.

The compiler note at §0 is signed by K. Alvarez. No other personnel signed this packet.

---

## 9. State Snapshots — Selected Times

For convenience, the following table records the state at selected times.

| Time | BWN-Zone-2 state | RUN-Zone-3 state | Sampler S-3 state | Clear-sample clock |
|---|---|---|---|---|
| 2026-04-28 07:00 | Not yet issued | Not yet issued | Operational | Not running |
| 2026-04-28 09:00 | Active | Not yet issued | Operational | Not running |
| 2026-04-28 10:00 | Active | Active | Operational | Not running |
| 2026-04-29 04:30 | Active | Active | Offline (since 03:45 corrected) | Not running |
| 2026-04-29 15:00 | Active | Active | Operational (restored 14:20) | Not running |
| 2026-04-30 12:00 | Active | Active | Operational | Reset; not yet started |
| 2026-04-30 16:00 | Active | Active | Operational | Running (1 hr counted) |
| 2026-05-01 10:00 | Active | Active | Offline (maintenance) | Paused (18 hr counted) |
| 2026-05-01 12:00 | Active | Active | Operational | Running (19 hr counted) |
| 2026-05-01 17:00 | Active | Active | Operational | Met (24 hr counted) |
| 2026-05-04 12:00 | Just lifted | Active | Operational | n/a |
| 2026-05-04 13:00 | Lifted | Just lifted | Operational | n/a |
| 2026-05-04 14:00 | Lifted | Lifted | Operational | n/a |

End of packet.
