# Dataset check and preprocessing report

Feature tables are technically validated under the documented export conventions.
They are not proof of an independently verified external test cohort.

Shared scalp channels: 49.
Shared participant IDs: none.
All ten transferred participants placed correctly: True.
Identical binary files: 0 recordings.

## resting-task-1 (ds003944 v1.0.1)
Participants inventoried: 82; feature rows: 74; excluded: 8.
Original diagnostic counts: {'Psychosis': 50, 'Control': 32}.
Retained diagnostic counts: {'Psychosis': 45, 'Control': 29}.
Sampling rates (Hz): [1000.0, 3000.0003000000297].
Raw duration range (s): 300.00–397.00.
Exclusion reasons: {'fewer than 60 usable seconds after fixed artifact rejection': 8}.

## resting-task-2 (ds003947 v1.0.1)
Participants inventoried: 61; feature rows: 33; excluded: 28.
Original diagnostic counts: {'Psychosis': 31, 'Control': 30}.
Retained diagnostic counts: {'Psychosis': 19, 'Control': 14}.
Sampling rates (Hz): [1000.0, 3000.0003000000297].
Raw duration range (s): 300.00–368.50.
Exclusion reasons: {'fewer than 60 usable seconds after fixed artifact rejection': 28}.

## Remaining limitations
- Person-level independence cannot be established from IDs and the READMEs alone.
- Channel order and scale follow BIDS/EEGLAB conventions, without original acquisition cross-check.
- Hardware filtering, complete processing history, and original artifact annotations unavailable.

The Task 1 transferred participants remain eligible; acquisition origin alone is not an exclusion.
No ICA, interpolation, classifier, learned scaling, or diagnosis-based tuning was performed.

## Readiness checklist
- [x] Source data inspected without modification.
- [x] Participant inventory and transferred-participant placement checked.
- [x] Fixed processing, artifact rules, and feature definitions recorded.
- [x] Output integrity and exact agreement with QC checked.
- [x] Both datasets have accepted participant feature rows.
- [ ] Independent person-level cohort membership confirmed beyond dataset IDs.
- [ ] Original acquisition channel order/calibration and full processing history independently verified.
