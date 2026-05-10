# Internal Investigation Packet — IIR-2026-0084

## Subject: Unauthorized After-Hours Access Allegation, Pemberton Building, 2026-04-17

**Compiled by:** J. Voskresenskaya, Office of the Facilities Inspector  
**Compilation date:** 2026-05-06  
**Distribution:** Facilities Director; HR Compliance; Building Security Manager; Subject (T. Aldridge) via counsel

---

## 1. Background

This packet documents a contested factual record concerning alleged unauthorized after-hours access to the Pemberton Building, 4th floor, on the night of Friday 2026-04-17 into Saturday 2026-04-18. The allegation, raised by the building Security Manager (S. Khoury) on 2026-04-21, is that employee T. Aldridge (badge ID BDG-44217, Research Division) accessed restricted Lab 4-C between approximately 22:00 on 2026-04-17 and 02:00 on 2026-04-18, outside Aldridge's authorized after-hours window (which terminates at 21:00 on weekdays) and without the supervising-presence requirement (a Lab 4-C policy in force since 2025-09-01).

T. Aldridge denies entering Lab 4-C on that date and asserts having departed the building at approximately 19:30 on 2026-04-17.

The following evidence is in the record. The Inspector takes no position in this packet; the packet exists to make the conflicts explicit for the Facilities Director's adjudication.

---

## 2. Evidence sources

### 2.1 Source A — Badge access logs (BAS export, system PEM-BAS-7)

The Pemberton Building Access System (PEM-BAS-7) recorded the following events on Aldridge's badge BDG-44217 between 2026-04-17 18:00 and 2026-04-18 04:00:

| Event | Timestamp (PEM-BAS-7) | Reader | Description |
|---|---|---|---|
| BAS-001 | 2026-04-17 18:43:11 | LOBBY-MAIN | Egress, lobby turnstile |
| BAS-002 | 2026-04-17 22:07:34 | LOBBY-MAIN | Ingress, lobby turnstile |
| BAS-003 | 2026-04-17 22:09:02 | ELEV-W-4 | 4th-floor west elevator authorization |
| BAS-004 | 2026-04-17 22:11:48 | DOOR-4-C | Lab 4-C ingress |
| BAS-005 | 2026-04-18 01:54:22 | DOOR-4-C | Lab 4-C egress |
| BAS-006 | 2026-04-18 01:57:10 | ELEV-W-4 | 4th-floor west elevator authorization (descending) |
| BAS-007 | 2026-04-18 02:01:33 | LOBBY-MAIN | Egress, lobby turnstile |

PEM-BAS-7 is the building's primary credential system and is, in normal operation, considered authoritative for ingress/egress events. However, the system's clock-sync history is relevant: see §3.2.

### 2.2 Source B — CCTV footage (camera CAM-LOBBY-N)

CAM-LOBBY-N covers the main lobby turnstile, with timestamping driven by an independent NTP source (the building's facilities NTP server, distinct from PEM-BAS-7's clock). Footage retention is 30 days; the relevant segment was preserved by Security on 2026-04-22 (file reference CAM-LOBBY-N_20260417-1800_20260418-0400.mp4, SHA-256 hash logged).

Footage shows:

- **CAM-001 (timestamp 2026-04-17 19:31:08):** an individual matching Aldridge's general description (height, jacket, satchel) exits through the main turnstile.
- **CAM-002 (timestamp 2026-04-17 22:54:29):** an individual enters through the main turnstile carrying a similar satchel. The individual's face is partially obscured by a cap and a high collar; facial features are not clearly resolvable. Build and gait are broadly consistent with Aldridge but not distinctive.
- **CAM-003 (timestamp 2026-04-18 02:48:47):** an individual exits through the main turnstile with the satchel. Face again obscured.

No other ingress/egress events on Aldridge's badge appear on CAM-LOBBY-N during this window.

CAM-LOBBY-N is reliable for *that an entry/exit occurred at the lobby turnstile* and for its own timestamp. It is not reliable for *positive identification of the individual* given the obscured face. The Security Office notes this limitation in its 2026-04-22 cover memo.

### 2.3 Source C — Witness statement, R. Okafor (custodial supervisor)

R. Okafor was on duty in the Pemberton Building between 21:00 on 2026-04-17 and 05:00 on 2026-04-18, working a routine custodial round. Okafor provided a signed statement on 2026-04-23 (statement ID WIT-OKA-001).

Relevant content of WIT-OKA-001:

> "I was on the 4th floor between approximately 23:00 and 23:40 on Friday night, doing the corridor and restroom round. I did not see Aldridge or anyone else on the 4th floor during that period. The corridor lights outside Lab 4-C were on the standard motion-activated cycle and I did not observe them activate independent of my own movement. I cannot speak to what happened on the floor before 23:00 or after 23:40."

Okafor's reliability:
- **Reliable for:** absence of corridor activity on 4th floor 23:00–23:40.
- **Not reliable for:** what occurred inside Lab 4-C (Okafor did not enter); what occurred 22:11–23:00 or 23:40–01:54 (outside Okafor's 4th-floor presence).

### 2.4 Source D — Memo from Lab 4-C Principal Investigator, Dr. M. Hsiao

Dr. Hsiao authored a memo dated 2026-04-22 (memo ID LAB4C-MEM-2026-04-22) at Security's request. Relevant content:

> "I was informed on the morning of 2026-04-18 that the Lab 4-C autoclave cycle scheduled to terminate at 22:00 on 2026-04-17 had not been properly logged out. The unit was found in an idle-but-powered state at 09:15 on 2026-04-18. The autoclave's internal log shows the cycle completed at 21:58 and was not manually closed. Closing the cycle requires a credentialed user inside the lab. I do not have personal knowledge of who, if anyone, was in the lab between 22:00 on 2026-04-17 and 09:15 on 2026-04-18."

Hsiao's memo establishes that the autoclave was in a state requiring manual closure but does not establish who, if anyone, was present.

### 2.5 Source E — Email thread between Aldridge and Aldridge's supervisor (P. Renner)

Two emails are relevant, retrieved from the corporate mail server on 2026-04-25.

- **EMAIL-001:** From Aldridge to Renner, sent 2026-04-17 19:24:52: "Heading out, I'll pick up the 4-C samples Monday morning. Have a good weekend." (Send timestamp from corporate mail server; server clock is independently NTP-synced and is considered reliable.)
- **EMAIL-002:** From Renner to Aldridge, sent 2026-04-21 10:14:30: "Security is asking about Friday night, 4-C. Were you there?" Aldridge replied at 10:21:08: "No. I left around 7:30 and went straight home. I did not go back."

EMAIL-001 is reliable as evidence that *Aldridge sent a message at 19:24:52 stating an intent to leave*. It does not, by itself, establish that Aldridge actually left or did not return.

### 2.6 Source F — Aldridge's personal phone location data (subpoenaed via internal HR process, returned 2026-05-01)

Aldridge consented to release of cell-site location data for 2026-04-17 18:00 to 2026-04-18 04:00. The carrier returned data with the following caveats: cell-site granularity is approximately 400m in the relevant area; pings are recorded only when the device transacts with a tower (not continuous).

Returned pings:

| Ping | Timestamp (carrier UTC, converted to local) | Sector |
|---|---|---|
| LOC-001 | 2026-04-17 19:33 | Sector covering Pemberton Building and three surrounding blocks |
| LOC-002 | 2026-04-17 19:51 | Sector covering Aldridge's residential neighborhood (≈4.2 km from Pemberton) |
| LOC-003 | 2026-04-17 20:47 | Aldridge's residential neighborhood sector |
| LOC-004 | 2026-04-17 23:12 | Aldridge's residential neighborhood sector |
| LOC-005 | 2026-04-18 07:08 | Aldridge's residential neighborhood sector |

No pings place the device near Pemberton between 19:51 on 2026-04-17 and 07:08 on 2026-04-18. Carrier note: a powered-down device or a device in airplane mode would generate no pings; the data does not affirmatively establish that the device was in the residential sector continuously, only that it transacted with that sector's towers at the listed times.

---

## 3. Identified conflicts

### 3.1 Lobby ingress timestamp disagreement (BAS vs. CCTV)

PEM-BAS-7 records the post-22:00 lobby ingress at 22:07:34 (BAS-002). CAM-LOBBY-N records the corresponding lobby ingress at 22:54:29 (CAM-002). The discrepancy is 47 minutes 5 seconds.

**Status: timeline-resolvable.** The Building Engineering Office confirmed on 2026-04-28 that PEM-BAS-7's clock had drifted from NTP. PEM-BAS-7's last successful NTP sync was 2026-03-19. Engineering's audit on 2026-04-28 measured a +47-minute-12-second drift on PEM-BAS-7 against the building NTP source. Applying this correction, BAS-002 corresponds to a true wall-clock time of 22:54:46, within 17 seconds of CAM-002's 22:54:29. The two sources are therefore in agreement on the ingress event time when clock drift is corrected. The same +47:12 correction applied to BAS-007 (raw 02:01:33) yields a corrected wall-clock 02:48:45, within 2 seconds of CAM-003's 02:48:47.

The BAS clock drift is documented in maintenance ticket BAS-MAINT-2026-04-28-003.

### 3.2 BAS internal-event timestamps for Lab 4-C

The Lab 4-C ingress/egress events (BAS-004 at 22:11:48 and BAS-005 at 01:54:22) and the elevator events (BAS-003 at 22:09:02 and BAS-006 at 01:57:10) are subject to the same +47:12 BAS clock drift. Corrected:

- BAS-003 corrected: 22:56:14
- BAS-004 corrected: 22:59:00
- BAS-005 corrected: 02:41:34
- BAS-006 corrected: 02:44:22

**Status: timeline-resolvable for ordering only.** The internal events have no independent corroborating timestamp source (CAM-LOBBY-N covers the lobby, not the 4th floor; there is no CCTV inside Lab 4-C or in the 4th-floor corridor). The corrected timestamps are internally consistent and consistent with the lobby events, but the +47:12 correction is the only available correction; whether the 4th-floor events represent Aldridge's actual activity is a separate question (see §3.3 and §3.4).

### 3.3 Identity of the lobby individual

CAM-LOBBY-N's CAM-002 and CAM-003 are not facially resolvable. The badge BDG-44217 was used at the turnstile, but a badge presentation does not establish who held the badge. Aldridge has not reported the badge as lost or stolen.

**Status: genuinely unresolved.** The available evidence is:

- Badge BDG-44217 was used (BAS-002 and BAS-007).
- An individual of broadly consistent build entered and exited (CAM-002, CAM-003).
- Aldridge denies being there (EMAIL-002, signed statement of 2026-04-25).
- Aldridge's phone was in the residential sector at 23:12 (LOC-004) but the carrier caveat means continuous residential presence is not affirmatively established.
- No witness places Aldridge at the building or in Lab 4-C.
- No witness contradicts Aldridge's denial.

The packet does not resolve whether the individual was Aldridge, someone using Aldridge's badge with or without Aldridge's knowledge, or some other arrangement.

### 3.4 Activity inside Lab 4-C

BAS-004 and BAS-005 establish that *the badge BDG-44217 caused the Lab 4-C door to authorize ingress and egress*, on the corrected timeline 22:59 and 02:41. The autoclave was found unclosed (LAB4C-MEM-2026-04-22). Closure of the autoclave requires a credentialed user inside the lab.

**Status: genuinely unresolved.** The evidence does not establish:

- Whether the individual who entered Lab 4-C did or did not interact with the autoclave;
- Whether the autoclave's unclosed state is causally connected to the after-hours entry or independent (the cycle terminated at 21:58, before any of the disputed events);
- What was done inside Lab 4-C during the ≈3 hours 42 minutes of corrected presence.

No internal lab logs (other than the autoclave's own cycle log) recorded user activity for that interval.

### 3.5 The 19:30 vs 19:31 departure

Aldridge's statement is "around 7:30." CAM-001 shows departure at 19:31:08. EMAIL-001 was sent at 19:24:52. BAS-001 (egress) raw is 18:43:11; corrected for +47:12 drift, this is 19:30:23.

**Status: timeline-resolvable.** All three sources (BAS corrected, CAM-LOBBY-N, the email and Aldridge's own statement) place Aldridge's evening departure within a 45-second window around 19:30–19:31. There is no conflict on the evening departure.

### 3.6 Custodial round and 4th-floor activity

Okafor reports being on the 4th floor 23:00–23:40 and observing no corridor activity. The corrected BAS timeline places the Lab 4-C ingress at 22:59 and egress at 02:41. Therefore, on the corrected timeline, the individual entered Lab 4-C ≈1 minute before Okafor's reported floor presence began and remained inside until ≈3 hours after Okafor left the floor.

**Status: not in conflict.** Okafor's testimony is fully consistent with the corrected BAS timeline: a person inside a closed lab would not generate corridor activity, and Okafor explicitly disclaims knowledge of in-lab activity. Okafor's testimony does, however, weakly corroborate that no *additional* person was traversing the 4th-floor corridor during the 23:00–23:40 window.

---

## 4. Summary table of source reliability

| Source | Reliable for | Not reliable for |
|---|---|---|
| A (BAS) | Badge events and their ordering, after +47:12 clock correction | Identity of badge holder; absolute timestamps without correction |
| B (CCTV) | Lobby entry/exit occurred and its NTP-synced timestamp | Identity of obscured individual |
| C (Okafor) | 4th-floor corridor inactivity 23:00–23:40 | Activity inside Lab 4-C; activity outside that 40-minute window |
| D (Hsiao memo) | Autoclave cycle terminated 21:58 unclosed; closure requires in-lab credentialed user | Identity of any in-lab visitor; whether visitor interacted with autoclave |
| E (emails) | The sending of the messages at the stated server timestamps | Whether Aldridge actually departed and remained departed |
| F (phone location) | Phone transacted with stated sectors at stated times | Continuous device location; device-holder identity |

---

## 5. Items remaining open at packet close

1. Identity of the individual who entered the lobby at 22:54 and Lab 4-C at 22:59 on the corrected timeline (§3.3).
2. Activity inside Lab 4-C between 22:59 and 02:41 (§3.4).
3. Whether the autoclave's unclosed state is causally related to the in-lab presence or coincidental (§3.4).

The Facilities Director will adjudicate on the basis of this packet at a hearing scheduled for 2026-05-19.
