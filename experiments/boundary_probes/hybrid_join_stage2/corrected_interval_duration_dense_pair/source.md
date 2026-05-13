# Corrected Interval Duration Dense Pair

## Record A

Record ID: CDD-1.
Subject: sample processing run SR-42.

The raw line log has four events:

- preparation started at 2026-08-02 06:40:00;
- preparation ended at 2026-08-02 07:04:00;
- sealed processing started at 2026-08-02 07:12:15;
- sealed processing ended at 2026-08-02 09:58:45.

The line clock was 4 minutes 15 seconds slow for the full record. Corrected
times add 4 minutes 15 seconds to each raw timestamp.

The corrected preparation start is 2026-08-02 06:44:15.
The corrected preparation end is 2026-08-02 07:08:15.
The corrected sealed-processing start is 2026-08-02 07:16:30.
The corrected sealed-processing end is 2026-08-02 10:03:00.

Elapsed-time questions must use corrected timestamps. Preparation and sealed
processing are separate intervals.

## Record B

Record ID: CDD-2.
Subject: evidence transfer window TW-8.

The raw transfer log has four events:

- packaging opened at 2026-09-11 22:15:20;
- packaging closed at 2026-09-11 22:36:50;
- external custody began at 2026-09-11 22:45:10;
- external custody ended at 2026-09-12 01:02:40.

The transfer scanner was 2 minutes 40 seconds fast for the full record.
Corrected times subtract 2 minutes 40 seconds from each raw timestamp.

The corrected packaging open time is 2026-09-11 22:12:40.
The corrected packaging close time is 2026-09-11 22:34:10.
The corrected external-custody start is 2026-09-11 22:42:30.
The corrected external-custody end is 2026-09-12 01:00:00.

Elapsed-time questions must use corrected timestamps. Packaging and external
custody are separate intervals.

