# Halverson Industrial Tower — Investigation Packet (Incident HIT-IR-2026-0419-A)

**Packet ID:** HIT-IR-2026-0419-A
**Subject:** After-hours access event, Server Room 4-South (4SR), 2026-04-19
**Incident date:** 2026-04-19 (Saturday)
**Compiled:** 2026-04-22 by T. Marquez, Corporate Security Manager
**Distribution:** Halverson Corporate Security; Halverson HR; Halverson Legal (advisory)
**Classification:** Internal investigation packet; not a finding of misconduct

This packet consolidates evidence collected through 2026-04-22 regarding
an after-hours badge-read pattern that culminated in a successful badge
read at the 4-South Server Room (4SR) door 4SR-D1 at 22:14 UTC on
2026-04-19. The packet enumerates evidence sources, documents source
reliability scope, and flags conflicts that the available evidence does
not resolve. Source identifiers (SRC-##) and evidence file names are
case-sensitive.

This packet does **not** make a finding of misconduct. Its purpose is to
collect and characterize the available evidence so that downstream HR
review and (if warranted) referral to law enforcement may proceed on a
clean evidentiary basis.

## Section 1. Source Evidence Catalog

| Source ID | Type                  | Identifier                       | Custodian            | Notes                                            |
| --------- | --------------------- | -------------------------------- | -------------------- | ------------------------------------------------ |
| SRC-01    | Badge access log      | BLE-2026-0419                    | Corporate Security   | Exported from Lenel system; NTP-synced.          |
| SRC-02    | CCTV (corridor)       | CAM-2026-0419-4S-12.dav          | Corporate Security   | From CAM-4S-12; **see Sec. 6 re: gap**.          |
| SRC-03    | CCTV (lobby)          | CAM-2026-0419-LOB-03.dav         | Corporate Security   | From CAM-LOB-03; clock drift, see Sec. 5.1.      |
| SRC-04    | Witness statement     | WS-2026-0420-TRENT               | HR (signed original) | R. Trent, security officer.                      |
| SRC-05    | Wi-Fi AP association  | PING-2026-0419                   | IT Networking        | Internal Cisco WLC log; per-AP timestamped.      |
| SRC-06    | Witness statement     | WS-2026-0420-ANDERS              | HR (signed original) | S. Anders, facilities tech.                      |

## Section 2. Subject

The badge associated with all 4SR entry attempts in the incident
window is **B-20471**, originally issued to **J. Holloway** (contractor,
Helix Engineering Services, contract HC-2025-117). The contract end
date was 2026-04-14. The badge was scheduled for deactivation in
ticket BD-2026-04-15-J. **The deactivation ticket was not closed as of
2026-04-19**; the badge remained active. Closure of BD-2026-04-15-J
is itself a separate process question being reviewed by Corporate
Security IT and is not part of this packet.

The packet notes that the badge being active does not establish that
J. Holloway physically used the badge during the incident window.
Badge B-20471 records the badge identifier; it does not record the
identity of the bearer. Photo verification is not collected at any
4SR reader.

## Section 3. Badge Access Log Excerpt (SRC-01)

The Lenel access control system is NTP-synced; the audit recorded a
clock skew of less than 1 second against reference NTP-A1 at the time
of the incident. Timestamps are UTC.

| Time (UTC)          | Badge   | Reader        | Result   |
| ------------------- | ------- | ------------- | -------- |
| 2026-04-19 22:02:14 | B-20471 | LOBBY-R1      | Granted  |
| 2026-04-19 22:09:45 | B-20471 | FLR4-EL2      | Granted  |
| 2026-04-19 22:14:08 | B-20471 | 4SR-D1        | Granted  |
| 2026-04-19 22:46:33 | B-20471 | FLR4-EL2      | Granted  |
| 2026-04-19 22:51:02 | B-20471 | LOBBY-R1      | Granted (egress) |

No other 4SR-D1 reads (granted or denied) appear in the badge log
between 18:00 on 2026-04-19 and 06:00 on 2026-04-20.

## Section 4. Wi-Fi AP Association Log Excerpt (SRC-05)

The Cisco wireless LAN controller (WLC) records device-to-AP
associations with per-AP timestamps. The WLC is NTP-synced (audit
skew <1s).

| Time (UTC)          | Device      | AP            | Coverage zone                          |
| ------------------- | ----------- | ------------- | -------------------------------------- |
| 2026-04-19 22:08:31 | DEV-12891   | AP-04-S2      | 4F South wing (corridor + 4SR vicinity) |
| 2026-04-19 22:50:14 | DEV-12891   | AP-LOB-1      | Lobby                                   |

DEV-12891 is the corporate-issued laptop assigned to J. Holloway
(asset tag HLV-LAP-12891, last MDM check-in 2026-04-15). The MDM
record shows the device was not collected on contract close; recovery
is in progress.

## Section 5. CCTV Excerpts

### 5.1 SRC-03 (CAM-LOB-03, lobby) — clock drift

CAM-LOB-03 captured a person entering the lobby on 2026-04-19. The
camera's recorded timestamp is **2026-04-19 21:47:26**. A
post-incident review of the camera's local clock found that
CAM-LOB-03's encoder NTP service had failed and the local clock was
**14m48s slow** against the building reference clock REF-NTP-B as of
2026-04-22.

Applying the drift correction yields a wall-clock time of approximately
**2026-04-19 22:02:14** (within 1 second of the SRC-01 badge read at
LOBBY-R1, B-20471). The drift correction memo is filed as
**CC-2026-04-22-LOB**.

The apparent conflict between SRC-01 (badge at 22:02) and SRC-03
(camera at 21:47) resolves under the drift correction; the two sources
are consistent post-correction. SRC-03's recorded image is reliable
for visual content but its **uncorrected** timestamp is not reliable;
the corrected timestamp is.

### 5.2 SRC-02 (CAM-4S-12, 4-South corridor) — recording gap

CAM-4S-12 (the camera covering the 4-South corridor outside 4SR-D1)
was offline for a scheduled firmware update from
**2026-04-19 22:00:00 to 22:45:00** per maintenance ticket
**FW-CAM-2026-04-19**. The firmware update window was scheduled three
weeks in advance and is documented in the camera maintenance log
(not reproduced; held by Corporate Security IT).

There is no CAM-4S-12 footage of the 4SR-D1 entry (22:14:08) or of
any movement in the corridor during the firmware window.

The absence of CAM-4S-12 footage **does not establish** that no
movement occurred during the window; the camera was offline by design.
The reverse — using the gap as evidence of no movement — is not
supported by this source.

## Section 6. Witness Statements

### 6.1 SRC-04: R. Trent (security officer), WS-2026-0420-TRENT

R. Trent was on patrol on the 4th floor at the time of the incident.
Statement reproduced from signed original (excerpt):

> "I was passing the south corridor on rounds at approximately 22:30.
> I observed a person at door 4SR-D1, partially turned away from me.
> The person was wearing a dark hoodie and light pants. The person
> was inside the door alcove and I could not see their face. I
> continued my rounds and did not engage. My next rounds pass at
> approximately 23:00 found the corridor empty."

R. Trent's time estimates are clock-based estimates using his issued
duty watch, which was synced manually against the building reference
clock at the start of his shift (18:00).

### 6.2 SRC-06: S. Anders (facilities tech), WS-2026-0420-ANDERS

S. Anders was attending to an HVAC issue on floor 4 in the adjacent
stairwell at the time of the incident. Statement reproduced from
signed original (excerpt):

> "I was in the south stairwell between approximately 22:15 and 22:35
> diagnosing an air handler trip. As I exited the stairwell at about
> 22:25 I saw a person leaving the 4SR area, walking toward the
> elevator. The person was wearing a blue work shirt and jeans. I did
> not get a clear look at the face. I assumed it was a regular
> after-hours staff member and did not stop them."

S. Anders's time estimates are based on his service phone clock,
which is NTP-synced via cellular and is not part of the building's
internal NTP fabric.

## Section 7. Source Reliability Scoping

The packet adopts the following reliability scoping for each source.
This scoping governs what may be inferred from each source.

| Source  | Reliable for                                                | Not reliable for                                            |
| ------- | ----------------------------------------------------------- | ----------------------------------------------------------- |
| SRC-01  | Time of badge read (NTP <1s); reader identity; badge identity | Identity of the bearer (no photo, no biometric)             |
| SRC-02  | Visual content during recorded windows                      | Coverage during the 22:00–22:45 firmware gap                |
| SRC-03  | Visual content; corrected timestamp post-CC-2026-04-22-LOB  | Uncorrected timestamp (was 14m48s slow)                     |
| SRC-04  | What R. Trent observed visually; his time estimate ±5 min   | Identity of the observed person (no clear face); sub-5-min timing |
| SRC-05  | Device-to-AP association (i.e., approximate location of device); time of association | Activity performed on the device (association ≠ activity); identity of device user |
| SRC-06  | What S. Anders observed visually; his time estimate ±5 min  | Identity of the observed person (no clear face); sub-5-min timing |

Specifically:

- SRC-01 is reliable for **time but not identity**. The badge log
  records that B-20471 was used; it does not record who held the badge
  at that moment.
- SRC-05 is reliable for **location but not activity**. AP association
  places DEV-12891 within the AP-04-S2 coverage zone at 22:08:31; it
  does not establish what was done on the device or who was operating
  the device.
- SRC-03's uncorrected timestamp is unreliable due to the NTP failure;
  the corrected timestamp is reliable per CC-2026-04-22-LOB.

## Section 8. Conflicts

### 8.1 Resolved conflict: lobby entry timestamp (SRC-03 vs SRC-01)

The apparent 15-minute discrepancy between SRC-03 (lobby CCTV at
21:47) and SRC-01 (badge read at 22:02) resolves under the drift
correction CC-2026-04-22-LOB. Post-correction, SRC-03 places the
person in the lobby at approximately 22:02:14, matching SRC-01 within
1 second. This conflict is **resolved**.

### 8.2 Unresolved conflict: clothing description (SRC-04 vs SRC-06)

R. Trent (SRC-04) reports observing a person at 4SR-D1 at
approximately 22:30 wearing **dark hoodie, light pants**. S. Anders
(SRC-06) reports observing a person leaving the 4SR area at
approximately 22:25 wearing **blue work shirt, jeans**.

The badge log (SRC-01) shows a single 4SR-D1 entry (22:14:08) and a
single FLR4-EL2 read (22:46:33) in the relevant window; CAM-4S-12 was
offline (Section 5.2).

The available evidence is consistent with at least three scenarios:

- (a) the same person was observed by both witnesses, and one or both
  clothing descriptions are mistaken;
- (b) two persons were present (one observed by each witness), and
  the badge log is incomplete because the second person did not use a
  badge at 4SR-D1 (e.g., entered behind the first, or via a tailgate);
- (c) one witness's time estimate is more inaccurate than ±5 minutes
  and the persons were observed at different times, possibly different
  individuals.

The packet **does not resolve** which scenario obtains. The conflict
between the clothing descriptions is preserved as **unresolved**, and
the available evidence is recorded as not sufficient to choose among
the scenarios.

## Section 9. Inferences Available and Inferences Not Available

### 9.1 Available

- Badge B-20471 was read at LOBBY-R1, FLR4-EL2, and 4SR-D1 in the
  sequence and at the times shown in SRC-01.
- Device DEV-12891 was associated with AP-04-S2 at 22:08:31.
- Camera CAM-LOB-03 captured a person entering the lobby at the
  drift-corrected time of approximately 22:02:14.

### 9.2 Not available

- The identity of the person who physically used badge B-20471 at
  any of the recorded reads. SRC-01 records the badge, not the
  bearer.
- The activity performed on DEV-12891 between 22:08:31 and 22:50:14.
  SRC-05 records the AP association, not the activity.
- The presence or absence of any person in the 4-South corridor
  between 22:00 and 22:45. CAM-4S-12 was offline (Section 5.2).
- A single coherent description of the person observed near 4SR.
  Witnesses SRC-04 and SRC-06 give incompatible clothing descriptions
  (Section 8.2); the conflict is unresolved.

The packet does not assign individual responsibility for the 4SR
entry. Assignment of responsibility is a function of HR review and,
if warranted, law-enforcement referral; this packet's role is to
characterize the evidence.

## Section 10. Procedural Notes

The badge B-20471 has been deactivated as of **2026-04-20 09:14 UTC**
(deactivation ticket BD-2026-04-20-EM, expedited). The deactivation
of B-20471 does not retroactively change the status of the
2026-04-19 reads in SRC-01.

DEV-12891 has been remotely wiped via MDM as of
**2026-04-21 11:00 UTC** (ticket MDM-WIPE-2026-04-21-A). The
disk image preserved before wipe is held by Corporate Security IT
under chain-of-custody record COC-2026-04-21-12891.

This packet supersedes the preliminary memo PRELIM-2026-04-20-A
issued by Corporate Security on the morning of 2026-04-20, which
contained the uncorrected SRC-03 timestamps and characterized the
SRC-04 vs SRC-06 conflict as a "minor discrepancy." Where this
packet conflicts with PRELIM-2026-04-20-A, this packet governs.

## Section 11. Sources Referenced But Not Reproduced

- Lenel access control system full export (only excerpt in Section 3).
- Cisco WLC AP association log full export (only excerpt in Section 4).
- CAM-LOB-03 video file (excerpt frames not embedded; file held by
  Corporate Security under chain of custody).
- CAM-4S-12 maintenance log (firmware update history).
- J. Holloway's contractor file (HR; contract HC-2025-117).
- DEV-12891 disk image (held by Corporate Security IT,
  COC-2026-04-21-12891).
- Building reference clock REF-NTP-B audit log.
- PRELIM-2026-04-20-A (superseded; retained for audit).

End of packet.
