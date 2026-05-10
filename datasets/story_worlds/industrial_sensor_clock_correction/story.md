# Meridian Polymer Plant — Line 4 Incident Packet

**Packet ID:** MPP-L4-INC-2026-0422
**Incident date:** 2026-04-22
**Compilation date:** 2026-04-26
**Compiled by:** S. Aurelio, Plant Engineering Lead
**Classification:** Internal review packet; not a regulatory submission

This packet supports plant engineering's review of the off-spec event of
2026-04-22 on Line 4. It reproduces sensor logs, the post-incident clock
drift audit, operator console notes, and maintenance records relevant to
event reconstruction.

## Section 1. Systems and Identifiers

The following systems are involved.

| System ID | Name                              | Time source          | Resolution |
| --------- | --------------------------------- | -------------------- | ---------- |
| SYS-A     | Process Control System (PCS)      | Internal RTC; NTP weekly | 1 second |
| SYS-B     | Quality Inspection Station (QIS)  | Internal RTC; NTP weekly | 1 second |
| SYS-C     | Maintenance Management System (MMS) | NTP continuous     | 1 second |
| SYS-D     | Operator Console (OC)             | Manual setting       | 1 minute  |

All system clocks are nominally UTC. Sensor and event identifiers used in
this packet are case-sensitive.

## Section 2. Clock Drift Audit (2026-04-25)

Following the incident, plant engineering conducted a clock drift audit
of the systems above against the plant reference clock REF-NTP-01.

| System | Last successful sync (UTC)     | Measured drift at audit | Drift direction          |
| ------ | ------------------------------ | ----------------------- | ------------------------ |
| SYS-A  | 2026-03-15 02:00:00            | +00:00:47               | Fast (PCS ahead of REF)  |
| SYS-B  | 2026-02-28 02:00:00            | -00:02:18               | Slow (QIS behind REF)    |
| SYS-C  | (continuous; no drift detected) | 00:00:00 (within ±1s)  | None                     |
| SYS-D  | (manual setting; not measurable) | Not measurable        | Indeterminate            |

**Interpretation rules adopted by this packet:**

- A SYS-A timestamp of `T` corresponds to wall-clock time `T - 00:00:47`.
- A SYS-B timestamp of `T` corresponds to wall-clock time `T + 00:02:18`.
- SYS-C timestamps are accepted as wall-clock.
- SYS-D timestamps are accepted at 1-minute resolution, no drift
  correction; their precision does not support sub-minute reasoning.
- These rules apply only to events recorded **after** the respective
  last successful sync. Events recorded before the last successful sync
  are not in scope for this packet.

The drift is treated as having accumulated linearly since the last
successful sync. For incidents close in time to the audit, the audit
drift is the best available estimate; a finer interpolation is not
performed.

SYS-B's NTP sync failure since 2026-02-28 is the subject of a separate
maintenance ticket (MMS-T-2026-0419-7); the cause is recorded in the
maintenance log but is not relevant to event reconstruction.

## Section 3. Raw Event Log (Selected)

The following events are reproduced as recorded by each system. Times
are as the originating system recorded them, before drift correction.

| Event ID | System | Recorded time (raw) | Description                                  |
| -------- | ------ | ------------------- | -------------------------------------------- |
| EV-01    | SYS-A  | 2026-04-22 14:02:13 | Extruder zone-3 setpoint changed (480 → 495 K) |
| EV-02    | SYS-A  | 2026-04-22 14:14:45 | Dryer feed rate increased to 18.4 kg/min     |
| EV-03    | SYS-A  | 2026-04-22 14:31:08 | Drying chamber humidity alarm (sensor HUM-D-04) |
| EV-04    | SYS-D  | 2026-04-22 14:33    | Operator note: "checked alarm, reset trip"   |
| EV-05    | SYS-A  | 2026-04-22 14:35:22 | Drying chamber humidity returned to range    |
| EV-06    | SYS-A  | 2026-04-22 14:48:01 | Extruder zone-3 setpoint reverted (495 → 480 K, manual) |
| EV-07    | SYS-D  | 2026-04-22 15:02    | Operator note: "starting visual inspection on output" |
| EV-08    | SYS-B  | 2026-04-22 15:09:33 | Batch B-2026-0422-3 flagged off-spec by QIS-OPT-12 |
| EV-09    | SYS-A  | 2026-04-22 15:14:50 | Line stop initiated (operator command)        |
| EV-10    | SYS-A  | 2026-04-22 15:14:55 | Line stop confirmed (E-stop chain)            |
| EV-11    | SYS-D  | 2026-04-22 15:15    | Operator note: "line stopped, calling supervisor" |
| EV-12    | SYS-B  | 2026-04-22 15:18:02 | Batch B-2026-0422-4 flagged off-spec by QIS-OPT-12 |
| EV-13    | SYS-C  | 2026-04-22 15:30:00 | Maintenance window opened for sensor diagnostics (MMS-T-2026-0422-1) |
| EV-14    | SYS-C  | 2026-04-23 09:00:00 | Maintenance window closed; line restart authorized |

## Section 4. Corrected Timeline

Applying the drift rules of Section 2 to the post-sync events of Section 3:

| Event ID | Wall-clock time (UTC, corrected)   | Note                                |
| -------- | ---------------------------------- | ----------------------------------- |
| EV-01    | 2026-04-22 14:01:26                | SYS-A −47s                          |
| EV-02    | 2026-04-22 14:13:58                | SYS-A −47s                          |
| EV-03    | 2026-04-22 14:30:21                | SYS-A −47s                          |
| EV-04    | 2026-04-22 14:33                   | SYS-D, no correction; 1-minute res. |
| EV-05    | 2026-04-22 14:34:35                | SYS-A −47s                          |
| EV-06    | 2026-04-22 14:47:14                | SYS-A −47s                          |
| EV-07    | 2026-04-22 15:02                   | SYS-D                                |
| EV-08    | 2026-04-22 15:11:51                | SYS-B +2m18s                         |
| EV-09    | 2026-04-22 15:14:03                | SYS-A −47s                          |
| EV-10    | 2026-04-22 15:14:08                | SYS-A −47s                          |
| EV-11    | 2026-04-22 15:15                   | SYS-D                                |
| EV-12    | 2026-04-22 15:20:20                | SYS-B +2m18s                         |
| EV-13    | 2026-04-22 15:30:00                | SYS-C                                |
| EV-14    | 2026-04-23 09:00:00                | SYS-C                                |

The raw-vs-corrected discrepancy materially changes one downstream
duration: the time between the first off-spec flag (EV-08) and line stop
initiation (EV-09).

- Raw computation: `15:14:50 (SYS-A) − 15:09:33 (SYS-B) = 00:05:17`.
- Corrected computation: `15:14:03 (wall) − 15:11:51 (wall) = 00:02:12`.

The corrected response interval is approximately 60% shorter than the
raw computation suggests. Plant engineering treats the corrected value
as authoritative for reconstruction purposes.

## Section 5. Maintenance / Offline Intervals

### 5.1 QIS-OPT-12 calibration (2026-04-15)

Quality inspection station camera QIS-OPT-12 was offline from
2026-04-15 06:00:00 UTC to 2026-04-15 14:00:00 UTC for routine
calibration (ticket MMS-T-2026-0414-3). The line continued to operate
during this window using only QIS-OPT-11 redundancy. This window is
relevant to the QIS sync failure investigation and is documented here
for context.

### 5.2 Line 4 stop-and-restart (2026-04-22 to 2026-04-23)

Line 4 was in line-stop state from the corrected wall-clock time of
EV-10 (2026-04-22 15:14:08) to the corrected wall-clock time of EV-14
(2026-04-23 09:00:00, line restart authorized). Total line-stop
duration: 17 hours 45 minutes 52 seconds. The line-stop interval is
treated as continuous; no partial restart occurred during the window.

### 5.3 Quality hold deadline rule

Plant procedure QHP-04 requires that off-spec material be held under
containment for 72 hours of *active production time* before disposition
review. *Active production time* excludes line-stop intervals and
offline maintenance windows. The 72-hour clock for batches
B-2026-0422-3 and B-2026-0422-4 began running at the corrected
wall-clock time of EV-08 (2026-04-22 15:11:51) and paused at the
corrected wall-clock time of EV-10 (2026-04-22 15:14:08). The clock
remained paused until line restart at EV-14 (2026-04-23 09:00:00). As
of compilation date, the clock has resumed.

## Section 6. Operator Notes (SYS-D, Reproduced)

The operator console at Line 4 was attended by R. Kim during the
incident window. Notes reproduced:

> 14:33 — checked alarm, reset trip
> 14:50 — extruder back to baseline, will continue monitoring
> 15:02 — starting visual inspection on output
> 15:08 — material is yellowing on bottom side. flagged for QIS.
> 15:15 — line stopped, calling supervisor
> 15:24 — supervisor on site
> 15:31 — handing off to maintenance team

R. Kim's note resolution is 1 minute; sub-minute timing should not be
inferred from these entries. R. Kim was not the originating reporter
of EV-08 or EV-12; those originated from QIS-OPT-12 automatic flagging.

## Section 7. Sensor Reliability Scope

The drying chamber humidity sensor HUM-D-04 (the source of EV-03) is a
capacitive RH sensor. Its certified reliability scope, per manufacturer
specification reproduced in the plant sensor register (not duplicated
here), is the measurement of relative humidity in the chamber. It is
not certified to identify the *cause* of an elevated reading.

Specifically, HUM-D-04 cannot establish whether the elevated humidity
at EV-03 was caused by:

- elevated feedstock moisture content,
- dryer malfunction (e.g., reduced air throughput),
- steam intrusion from an external pathway, or
- sensor self-fault.

The packet does not resolve the causation question. The cause of the
EV-03 alarm is recorded as **unresolved**, with the explicitly named
missing evidence being either (i) feedstock moisture analysis from the
dryer-inlet sample (sample LAB-2026-0422-S3, sent for analysis on
2026-04-22, results not yet returned as of 2026-04-26) or (ii) dryer
airflow logs from the dryer's local datalogger DRY-DL-04, which
plant maintenance reports as having lost data covering 14:25 to 14:38
on 2026-04-22 due to a buffer overflow on the local logger.

## Section 8. Inferences Available and Inferences Not Available

### 8.1 Available

- The corrected wall-clock interval between EV-08 and EV-09 is
  approximately 2 minutes 12 seconds.
- The line-stop duration between EV-10 and EV-14 is 17 hours 45
  minutes 52 seconds.
- Both SYS-A and SYS-B were running on stale sync at the time of the
  incident; SYS-A had been synced more recently than SYS-B.

### 8.2 Not available

- The cause of the EV-03 humidity alarm.
- The state of dryer airflow during 14:25 to 14:38 on 2026-04-22
  (logger data lost).
- The operator's actions between 14:50 and 15:02 (R. Kim's notes are
  silent for this interval; the absence of notes is not affirmative
  evidence of any specific action).
- Any sub-minute reasoning over SYS-D entries.

This packet does not assign root cause. Root cause assignment is the
function of a separate root-cause analysis (RCA), which is in
preparation but not part of this packet.

## Section 9. Sensor Register Excerpts

The plant sensor register, maintained by Plant Engineering, contains
the certified scope and reliability rating for each instrumented
sensor. The relevant excerpts are reproduced below; the full register
is referenced but not duplicated.

> **HUM-D-04** — Vendor: Sentec; Model: Sentec RH-220-Plus; Location:
> Dryer Chamber 4 mid-bed. Certified for measurement of relative
> humidity in the range 5–95 % RH at chamber temperatures up to 130 °C.
> Not certified for cause attribution. Last calibration 2026-01-12.
> Next calibration due 2026-07-12.
>
> **QIS-OPT-12** — Vendor: Vexcel; Model: V-OptiCheck 4; Location:
> Line 4 inspection bay. Certified for visual defect classification of
> pellet output (color uniformity, pellet shape) at line speeds up to
> 24 kg/min. Not certified for moisture content estimation. Last
> calibration 2026-04-15 (after the calibration window noted in 5.1).
>
> **QIS-OPT-11** — Vendor: Vexcel; Model: V-OptiCheck 4; Location:
> Line 4 inspection bay (redundant). Same scope as QIS-OPT-12. Last
> calibration 2026-03-10. Next calibration due 2026-09-10.
>
> **DRY-DL-04** — Vendor: Plant-built (PLC-attached datalogger);
> Location: Dryer Chamber 4 PLC cabinet. Records dryer airflow, inlet
> temperature, outlet temperature. 30-day rolling buffer. Known to
> drop entries on buffer overflow; no certified retention guarantee.
> Last firmware update 2025-09-04.

The "Not certified" lines are determinative for what may be inferred
from a sensor's data. EV-08 and EV-12 are within QIS-OPT-12's certified
scope (visual defect classification); EV-03 is within HUM-D-04's
certified scope (humidity measurement) but **not** within its
certified scope to attribute cause.

## Section 10. Investigation Timeline

| Date       | Step                                                                         |
| ---------- | ---------------------------------------------------------------------------- |
| 2026-04-22 | Incident on Line 4 (this packet's subject events)                            |
| 2026-04-22 | LAB-2026-0422-S3 sample sent for moisture analysis                           |
| 2026-04-23 | Line 4 maintenance window completed; line restart authorized at 09:00:00     |
| 2026-04-25 | Clock drift audit conducted against REF-NTP-01                               |
| 2026-04-25 | Buffer overflow on DRY-DL-04 confirmed by maintenance team; no recovery     |
| 2026-04-26 | This packet compiled                                                         |
| 2026-04-29 | Estimated return date for LAB-2026-0422-S3 (per lab confirmation)            |
| (TBD)      | Root cause analysis report                                                   |

## Section 11. Compilation Notes

This packet is for engineering review and is not the regulatory
incident report (which is filed under separate cover by Plant
Compliance, packet ID MPP-COMP-2026-0427). The two packets cover the
same incident but the regulatory report uses raw timestamps as
recorded by each system; the engineering packet (this document) uses
corrected wall-clock times. Discrepancies between the two are by
design and are not contradictions.

The following sources are referenced but not reproduced in full:
the plant sensor register; the maintenance ticket database; the
calibration records for QIS-OPT-12 and HUM-D-04; the dryer-inlet
sample chain-of-custody for LAB-2026-0422-S3; R. Kim's full operator
shift log (only the incident-window subset is reproduced).

End of packet.
