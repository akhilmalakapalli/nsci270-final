# Section 1 — Work completed as of November 10, 2026, 2:42:12 PM EST

Timestamp: **2026-11-10 14:42:12 America/New_York (UTC−05:00)** / **2026-11-10 19:42:12 UTC**. This is the status-check timestamp for this handoff, not the start or end time of every earlier operation.

This document is the continuing project handoff. Preserve this section as a historical snapshot. Append **Section 2**, **Section 3**, and so on with a new timestamp for later work. Describe what changed, why, which checks were actually run, output/count changes, Git status, and remaining limitations. If correcting an earlier statement, identify the correction explicitly instead of silently rewriting the history.

## 1.1 Project scope and current outcome

Workspace: `/Users/akhil/Documents/nsci270-final`.

Two pieces of work have been performed:

1. Repaired the GitHub sync problem and uploaded all original EEG recordings using Git LFS.
2. Created and executed `00_master_data_check_and_preprocessing.ipynb` as the shared data-checking, QC, preprocessing, and feature-extraction foundation for later NSCI 270 research notebooks.

The executed notebook produced **107 participant feature rows: 74 from Task 1 and 33 from Task 2**. It inspected **143 recordings**, with one recording per participant, and excluded **36 participants** because they had fewer than 60 seconds remaining after the fixed artifact rejection procedure. Excluded participants remain in the QC tables and their source recordings remain in `data`.

The outputs are technically validated **under documented BIDS/EEGLAB export conventions**. This is not independent confirmation of the original electrode mapping/calibration, complete acquisition history, or person-level separation between the intended training and test cohorts.

No classifiers, learned transformations, feature selection, model tuning, performance evaluation, or research-question analyses have been implemented.

## 1.2 Git sync investigation and repair

### Initial problem

- The original branch was `main`, one local commit ahead of `origin/main`.
- The remote was and remains `https://github.com/akhilmalakapalli/nsci270-final.git`.
- The pending local commit was `a42132e` (`first set`), following `c387059` (`Initial commit`).
- The `data` directory contained 625 files, including 143 `.eeg` recordings. All were already tracked; the problem was not missing `git add` operations.
- The recordings occupied approximately 20.07 GB in decimal units (about 19 GiB). Fifty-five files exceeded 100 MiB, preventing an ordinary GitHub push of the original commit.
- Git LFS was not installed. The nested dataset `.gitattributes` files contained DataLad/git-annex metadata, not Git LFS tracking rules.
- A prior IDE Git push was still packing/transferring in the background. That attempt was stopped before the corrected push proceeded.

### Repair performed

- Installed Git LFS through Homebrew (`git-lfs 3.8.1`) and initialized its hooks/configuration for this repository with `git lfs install --local`.
- Migrated `*.eeg` in the unpublished `main` history to LFS, excluding the already-published `origin/main` history:

```sh
git lfs migrate import --include='*.eeg'   --include-ref=refs/heads/main   --exclude-ref=refs/remotes/origin/main
```

- Migration added the LFS tracking rule in the root `.gitattributes` and changed the unpublished commit ID to `bada33e2e58f5ea4e1de581a1c1f757840a0fc14` (`first set`).
- After migration, files in the working tree initially contained LFS pointers. Ran `git lfs checkout` to restore all full binary recordings locally.
- Verified the local size and SHA-256 content of all 143 recordings against their LFS pointers. All passed.
- Ran `git push origin main`. The approximately 20 GB first upload took an extended period at roughly 4.4 MB/s overall; the final tool result reported 143/143 LFS objects uploaded and a successful `main` update. No force push was used.
- Confirmed that GitHub's LFS endpoint accepted all 143 objects (20.07 GB) without object errors and that local `main` matched `origin/main`.

### Backup clarification and current Git state

A `backup/pre-lfs-sync` branch was created during the original repair. **It is not present in the current workspace snapshot**, and `git cat-file -t a42132e` currently cannot resolve the original pre-migration object. Do not rely on that earlier backup branch being available. The handoff does not establish why it is absent now.

At this section's status check, local `main` and the local `origin/main` reference both point to `bada33e2e58f5ea4e1de581a1c1f757840a0fc14`. The EEG/data push is complete. **The later notebook implementation, outputs, README edits, requirements, ignore rules, and this handoff have not been committed or pushed.** The status check showed:

```text
 M README.md
?? .gitignore
?? 00_master_data_check_and_preprocessing.ipynb
?? outputs/
?? requirements.txt
```

`HANDOFF.md` is being added by this documentation task. No data-file changes were reported by `git diff --name-only -- data` after notebook execution.

## 1.3 Materials inspected and dataset mapping

Before implementation, inspected the project README, dataset READMEs, dataset descriptions/DOIs, participant TSVs and label definitions, channel tables, BrainVision headers, recording JSON sidecars, and release notes. Searched for workspace instructions and existing Python/notebook work; no applicable `AGENTS.md` or existing analysis code was found. The initial project README contained only the project title. The source dataset folders were not renamed or moved.

| Local folder | OpenNeuro dataset | Version | Intended later role | Participants | Control | Psychosis |
| --- | --- | --- | --- | --- | --- | --- |
| data/resting-task-1 | ds003944 | 1.0.1 | Training | 82 | 32 | 50 |
| data/resting-task-2 | ds003947 | 1.0.1 | Held-out test; independence limitation below | 61 | 30 | 31 |

The dataset-description DOIs match the requested accessions and version 1.0.1. Participant metadata defines `Control` as healthy and `Psychosis` as first episode psychosis. Output tables preserve the source label `Psychosis`; it should not be silently relabeled as a narrower diagnosis.

Inventory checks found no duplicate participant rows, multiple recordings per participant, missing required recording components, unmaterialized LFS/annex content, or unknown diagnosis labels in this run. The inventory links IDs, dataset/accession, diagnosis, acquisition, task, source paths, and recording identifiers.

## 1.4 Acquisition membership, transferred participants, and independence

Both dataset READMEs describe two independently collected samples. They also explicitly say that ten acquisition-2 participants were placed in Task 1 because they used the Task 1 montage, and excluded from Task 2.

The notebook verified all ten IDs against both READMEs, participant rosters, and recording files. All ten are in Task 1 and absent from Task 2. They were assigned acquisition 2 while keeping dataset membership `resting-task-1`. Other Task 1 participants were assigned acquisition 1 according to the README description; Task 2 participants were assigned acquisition 2. Acquisition was not inferred from an ID suffix alone.

**All ten transferred participants passed QC and are included in the Task 1 features.** They were not excluded merely because they originated in acquisition 2.

| Transferred participant | Dataset | Acquisition | Retained epochs | Usable seconds | Outcome |
| --- | --- | --- | --- | --- | --- |
| sub-2140A | resting-task-1 | 2 | 28 | 112 | Included |
| sub-2170A | resting-task-1 | 2 | 35 | 140 | Included |
| sub-2174A | resting-task-1 | 2 | 35 | 140 | Included |
| sub-2176A | resting-task-1 | 2 | 44 | 176 | Included |
| sub-2177A | resting-task-1 | 2 | 41 | 164 | Included |
| sub-2184A | resting-task-1 | 2 | 73 | 292 | Included |
| sub-2193A | resting-task-1 | 2 | 53 | 212 | Included |
| sub-2214A | resting-task-1 | 2 | 51 | 204 | Included |
| sub-2217A | resting-task-1 | 2 | 73 | 292 | Included |
| sub-2221A | resting-task-1 | 2 | 56 | 224 | Included |

There are no exact participant-ID overlaps between datasets and no identical EEG binary hashes among the 143 recordings. Neither finding proves that different IDs correspond to different people. No crosswalk or author confirmation of person-level non-overlap was available. Because Task 1 also contains acquisition-2 participants, a simple “acquisition 1 versus acquisition 2” interpretation is incorrect. Describe Task 2 as an intended held-out dataset with unresolved person-level independence until stronger evidence is available.

**ID detail:** `sub-2221` and `sub-2221A` are different literal IDs in these files. `sub-2221` was excluded by QC; transferred participant `sub-2221A` was included. The notebook does not remove suffixes or assume the two are the same person.

## 1.5 Recording compatibility and export interpretation

| Property | Task 1 | Task 2 |
| --- | --- | --- |
| Condition | Eyes-open rest, fixation on a centered plus sign | Same documented instructions |
| Equipment description | Elekta Neuromag Vectorview | Elekta Neuromag Vectorview with Easycap cap |
| Header channels | 64 | 64 |
| Scalp table rows | First 60, EEG, microV | First 60, EEG, microV; different montage |
| Recorded reference | TP9 | TP9 |
| Sampling rates | 81 recordings at 1000 Hz; 1 at approximately 3000 Hz | 7 recordings at 1000 Hz; 54 at approximately 3000 Hz |
| Exact high sampling rate | Approximately 3000.00030000003 Hz | Approximately 3000.00030000003 Hz |
| Raw duration range | 300–397 seconds | 300–368.49996315 seconds |
| Power-line frequency | 60 Hz | 60 Hz |
| SoftwareFilters | n/a | n/a |
| Hardware-filter history | Not documented | Not documented |
| Available marker references / annotations | 0 / 0 | 0 / 0 |
| Channel status columns | Not provided | Not provided |

### Issue found and decision made

Headers use generic labels such as `EEG001`; channel tables use anatomical labels. Header calibration fields are blank. Auxiliary-channel ordering/types disagree between the header labels and the channel table, and there are no marker files/references. I asked whether original documentation or a corrected export was available. The user replied: **“no i don't know. fix as you see fit.”**

The initial concern about a possible reader blocker was resolved by inspecting the EEGLAB exporter and testing MNE: the standard MNE 1.13.2 BrainVision reader successfully read the files without modifying headers or supplying custom overrides. The EEGLAB exporter intentionally writes blank calibration fields and omits the marker reference when its event structure is empty. This explains the format, but does not prove how each source recording was originally calibrated or annotated.

Implementation decisions:

- Use the ordered first 60 rows of each recording's `channels.tsv` as scalp labels; normalize case to uppercase (`FP1`/`Fp1`, `Oz`/`OZ`, etc.).
- Use the channel-table microvolt units and MNE's default microvolt interpretation for this export. MNE represents data internally in volts; thresholds are converted accordingly.
- Validate channel count, layout, file size, sampling rate, and duration against the supplied metadata.
- Exclude the trailing auxiliary channels and mastoid/reference labels from features. No attempt was made to guess or repair the auxiliary-channel correspondence.
- Use the same 49 shared scalp channels for all participants. Do not rename generic channel indices directly across datasets without their own channel tables: the montages differ.
- Preserve all original source headers, sidecars, channel tables, and EEG binaries. No synthetic marker files were created.

The conventional mapping and scale are explicit assumptions, not independently verified acquisition facts. A shared multiplicative scale cancels in relative band power, but amplitude-based rejection still depends on correct calibration; channel-specific scale or ordering errors would also affect the features.

Relevant primary documentation consulted:

- [EEGLAB BrainVision exporter](https://github.com/sccn/bva-io/blob/master/pop_writebva.m): export layout, blank calibration fields, and marker-reference behavior.
- [MNE BrainVision reader](https://mne.tools/stable/generated/mne.io.read_raw_brainvision.html): reading and unit convention.
- [BIDS EEG channel tables](https://bids-specification.readthedocs.io/en/v1.7.0/04-modality-specific-files/03-electroencephalography.html): channel ordering convention.

### Shared channels

```text
AF3, AF4, AF7, C1, C2, C3, C4, C5, C6, CP1, CP2, CP3, CP4, CZ, F1, F2, F3, F4, F5, F6, F7, F8, FC1, FC2, FC5, FC6, FP1, FP2, FT7, FT8, FZ, O1, O2, OZ, P3, P4, P5, P6, P7, P8, PO3, PO4, PO7, PO8, PZ, T7, T8, TP7, TP8
```

## 1.6 Notebook organization and raw-data QC

Created the actual Jupyter notebook at [00_master_data_check_and_preprocessing.ipynb](00_master_data_check_and_preprocessing.ipynb). It has 15 cells: seven Markdown section introductions and eight code cells, including a separate plotting cell. Its seven sections follow the requested structure:

1. Purpose and setup.
2. Data completeness and participant inventory.
3. Independence and compatibility.
4. Raw-data quality checks.
5. Consistent preprocessing.
6. Feature extraction.
7. Validation and saved outputs.

Paths resolve from the working directory upward to the project root containing both dataset folders. The notebook runs top to bottom without variables from a previous interactive session. Small functions handle repeated file/header checks, recording loading, and preprocessing. There are no custom classes or general configuration frameworks.

Raw checks actually performed:

- Required files and materialization checks, including LFS pointers and annex links/pointers.
- BrainVision channel/sample dimensions and binary byte count; channel-major float32 layout.
- Header/JSON sampling rate and duration agreement, task consistency, and channel-table row count/units.
- MNE reading of all 143 recordings.
- Every sample of the **49 selected shared scalp channels** checked for nonfinite values and whole-recording constant signals. These numeric checks are not a claim that all auxiliary or discarded channels were assessed.
- SHA-256 hashes of all recording binaries to detect identical content under different paths/IDs.
- Available bad-channel status and annotations inspected; none were supplied in this export.

Results: all 143 recordings readable; no completeness errors, reader warnings, nonfinite shared-channel samples, constant shared channels, or duplicate binary hashes. Absence of annotation files/status columns is recorded as unavailable information, not evidence that the original signals are artifact-free.

Two representative figures were created: the first readable recording in sorted order for each dataset (`sub-1448` and `sub-2235A`). Each shows five seconds of FP1/CZ/OZ and a shared-channel Welch spectrum calculated from up to 20 seconds. Both figures were visually inspected. They show raw signals and line noise; they are not post-cleaning validation plots. Selection did not depend on diagnosis.

## 1.7 Fixed preprocessing procedure

Settings were chosen as simple project rules before inspecting diagnosis-related feature patterns. The same settings were applied to both datasets; Task 2 outcomes were not used to relax thresholds.

1. Load only the shared scalp channels using the recording-specific ordered channel table.
2. Use at most the first 300 seconds, so longer exports do not contribute extra recording time.
3. Apply a 0.5–40 Hz, fourth-order Butterworth filter using second-order sections and forward/backward zero-phase filtering. This is a broad analysis filter with margins around the 1–30 Hz feature range. `SoftwareFilters: n/a` is not proof of no earlier filtering; unknown acquisition filtering cannot be undone.
4. Resample with MNE's anti-aliased FFT method to 200 Hz. No separate 60 Hz notch was added because the analysis low-pass and feature range already exclude that frequency.
5. Trim two seconds at each end after filtering/resampling.
6. Make nonoverlapping four-second epochs. In this run each recording produced 74 candidate epochs, representing 296 seconds after trimming.
7. Before re-referencing, reject an epoch if any shared channel has peak-to-peak amplitude greater than 200 µV or less than 1 µV. Reject annotated bad intervals if available.
8. Average-reference surviving epochs over the same shared channels, then repeat the same rejection checks. The first check prevents a shared artifact from being hidden by reference subtraction.
9. Require at least 15 retained epochs, equivalent to 60 usable seconds, to include the participant's features. Do not automatically relax the rule when fewer epochs survive.

There is no ICA, bad-channel interpolation, adaptive participant-specific channel subset, or diagnosis-dependent artifact rule. A recording with a bad shared channel would be excluded rather than changing the reference/channel set. This is intentionally conservative and can discard substantial data; the thresholds are project choices, not validated clinical cutoffs.

Other explicit eligibility rules cover missing/unreadable data, unknown labels, duplicate roster rows, duplicate binary files, multiple recordings without an aggregation decision, and inconsistent dataset documentation. None of those rules caused the 36 exclusions in the present run.

## 1.8 Participant outcomes and attrition

| Dataset | Diagnosis | Inventoried | Included | Excluded |
| --- | --- | --- | --- | --- |
| resting-task-1 | Control | 32 | 29 | 3 |
| resting-task-1 | Psychosis | 50 | 45 | 5 |
| resting-task-2 | Control | 30 | 14 | 16 |
| resting-task-2 | Psychosis | 31 | 19 | 12 |
| Both | All | 143 | 107 | 36 |

Task 1 exclusion rate: **8/82 = 9.8%**. Task 2 exclusion rate: **28/61 = 45.9%**. This large difference is a material limitation for later generalization claims. The work so far does not establish whether it is caused by acquisition differences, noise, the conservative rejection procedure, calibration assumptions, or some combination. Do not describe the retained participants as necessarily representative of the entire source cohorts. No thresholds were changed in response to this difference.

Retained-participant usable duration:

| Dataset | Minimum seconds | Median seconds | Maximum seconds | Retained epochs contributing to features |
| --- | --- | --- | --- | --- |
| resting-task-1 | 68 | 234 | 296 | 4032 |
| resting-task-2 | 96 | 212 | 296 | 1738 |

Across all participants, including those later excluded for insufficient duration, Task 1 retained 4,083 of 6,068 candidate epochs; Task 2 retained 1,861 of 4,514. The feature tables use only 4,032 Task 1 and 1,738 Task 2 epochs, respectively, because a few surviving epochs from an excluded participant are not included. Eleven excluded participants had no retained epochs.

### Every excluded participant and the recorded reason

**The inclusion-level reason for every row below is “fewer than 60 usable seconds after fixed artifact rejection.”** Every participant had 74 candidate epochs. The rejected count is 74 minus the retained count. Source recordings were not deleted.

The final column summarizes the five most frequently named channels in rejected-epoch logs, with the number of rejected epochs mentioning each channel. A single epoch may name multiple channels, so these counts must not be added to infer the number of rejected epochs. They are log descriptions, not diagnoses of faulty electrodes.

**Logging limitation:** the current MNE drop logs list channel names, but do not separately identify high-amplitude versus flatness rejection or the before-reference versus after-reference stage. Those finer causes cannot be recovered confidently from the saved channel-name strings alone. Do not invent them.

### resting-task-1 exclusions

| Participant | Diagnosis | Kept epochs | Rejected epochs | Usable seconds | Most frequently logged rejection channels |
| --- | --- | --- | --- | --- | --- |
| sub-2009 | Control | 12 | 62 | 48 | FP1: 62; FP2: 44; AF7: 26; AF3: 12; AF4: 9 |
| sub-2015 | Psychosis | 0 | 74 | 0 | FP1: 74; FP2: 4; AF3: 1; AF4: 1; AF7: 1 |
| sub-2020 | Psychosis | 6 | 68 | 24 | FP2: 67; FP1: 50; AF4: 18; O1: 12; PO7: 9 |
| sub-2034 | Psychosis | 6 | 68 | 24 | FP2: 62; AF7: 60; FP1: 53; AF4: 24; F6: 7 |
| sub-2124 | Control | 7 | 67 | 28 | FP2: 66; FP1: 50; AF4: 14; AF3: 8; AF7: 8 |
| sub-2178 | Psychosis | 9 | 65 | 36 | FP1: 65; FP2: 63; AF7: 30; AF3: 4; F8: 2 |
| sub-2218 | Psychosis | 1 | 73 | 4 | FP2: 71; AF3: 63; AF4: 54; AF7: 53; F1: 7 |
| sub-2221 | Control | 10 | 64 | 40 | F1: 55; FP2: 23; FP1: 14; F8: 4; F6: 3 |

### resting-task-2 exclusions

| Participant | Diagnosis | Kept epochs | Rejected epochs | Usable seconds | Most frequently logged rejection channels |
| --- | --- | --- | --- | --- | --- |
| sub-2235A | Control | 8 | 66 | 32 | AF7: 66; FP1: 66; FP2: 66; AF3: 44; AF4: 38 |
| sub-2240A | Control | 8 | 66 | 32 | FP1: 66; AF7: 65; FP2: 65; AF3: 30; AF4: 27 |
| sub-2252A | Psychosis | 2 | 72 | 8 | FP1: 72; AF7: 66; FP2: 48; AF3: 25; AF4: 15 |
| sub-2267A | Control | 0 | 74 | 0 | FP1: 74; AF7: 73; FP2: 73; AF3: 72; AF4: 70 |
| sub-2269A | Control | 0 | 74 | 0 | FP1: 74; FP2: 74; AF7: 73; AF4: 33; AF3: 30 |
| sub-2276A | Psychosis | 0 | 74 | 0 | P4: 74; AF7: 2; F5: 2; F7: 2; FC5: 2 |
| sub-2279A | Psychosis | 0 | 74 | 0 | P4: 74; FP2: 38; FP1: 34; AF7: 22; AF3: 16 |
| sub-2290A | Control | 0 | 74 | 0 | CP4: 74; AF7: 72; AF4: 70; AF3: 69; F2: 65 |
| sub-2320A | Control | 0 | 74 | 0 | FP1: 74; FP2: 74; AF7: 64; AF4: 36; AF3: 25 |
| sub-2355A | Control | 6 | 68 | 24 | FP1: 68; FP2: 65; AF7: 59; AF3: 34; AF4: 17 |
| sub-2356A | Control | 0 | 74 | 0 | FP1: 74; FP2: 74; AF7: 73; AF4: 65; AF3: 64 |
| sub-2367A | Psychosis | 13 | 61 | 52 | FP1: 61; FP2: 60; AF7: 59; AF3: 23; AF4: 22 |
| sub-2403A | Psychosis | 3 | 71 | 12 | FP1: 67; FP2: 62; AF7: 51; AF3: 27; AF4: 23 |
| sub-2419A | Psychosis | 0 | 74 | 0 | AF7: 74; FP1: 74; FP2: 74; AF3: 70; AF4: 51 |
| sub-2426A | Control | 0 | 74 | 0 | F3: 74; FP1: 74; FP2: 74; AF7: 67; AF4: 22 |
| sub-2430A | Control | 8 | 66 | 32 | FP1: 64; FP2: 63; AF7: 60; AF3: 51; AF4: 48 |
| sub-2431A | Psychosis | 0 | 74 | 0 | F3: 74; FP1: 17; FP2: 15; AF7: 6; AF3: 4 |
| sub-2442A | Control | 4 | 70 | 16 | FP1: 70; FP2: 70; AF7: 43; AF4: 27; AF3: 19 |
| sub-2476A | Psychosis | 10 | 64 | 40 | FP1: 64; FP2: 50; AF7: 16; AF3: 7; F7: 6 |
| sub-2479A | Control | 12 | 62 | 48 | FP1: 62; FP2: 53; AF7: 24; PZ: 1 |
| sub-2494A | Control | 3 | 71 | 12 | AF7: 71; FP1: 71; FP2: 71; AF3: 54; AF4: 38 |
| sub-2498A | Psychosis | 7 | 67 | 28 | FP1: 67; AF7: 9; AF3: 5; AF4: 3; F7: 1 |
| sub-2503A | Psychosis | 12 | 62 | 48 | FP2: 62; FP1: 60; CP1: 5; AF7: 3; F8: 2 |
| sub-2505A | Psychosis | 3 | 71 | 12 | AF7: 69; C5: 21; FP2: 16; P7: 15; FP1: 14 |
| sub-2514A | Psychosis | 4 | 70 | 16 | FP1: 70; FP2: 60; AF7: 29; C2: 6; AF3: 5 |
| sub-2518A | Control | 11 | 63 | 44 | FP1: 58; FP2: 55; AF7: 34; AF3: 22; AF4: 12 |
| sub-2538A | Control | 7 | 67 | 28 | FP1: 65; FP2: 63; AF7: 40; AF3: 38; AF4: 30 |
| sub-2574A | Control | 2 | 72 | 8 | FP1: 72; FP2: 70; AF7: 50; AF4: 12; AF3: 7 |

### Included participant roster

The CSV feature tables and `participant_qc.csv` are authoritative for machine use. These lists make the Section 1 snapshot self-contained; all listed IDs have one feature row.

**resting-task-1 — 74 included:**

`sub-1448`, `sub-1824`, `sub-1971`, `sub-1983`, `sub-1989`, `sub-1990`, `sub-1998`, `sub-1999`, `sub-2000`, `sub-2002`, `sub-2017`, `sub-2018`, `sub-2025`, `sub-2028`, `sub-2038`, `sub-2041`, `sub-2044`, `sub-2054`, `sub-2067`, `sub-2070`, `sub-2071`, `sub-2072`, `sub-2073`, `sub-2081`, `sub-2082`, `sub-2086`, `sub-2089`, `sub-2092`, `sub-2093`, `sub-2095`, `sub-2096`, `sub-2105`, `sub-2109`, `sub-2110`, `sub-2117`, `sub-2122`, `sub-2125`, `sub-2128`, `sub-2129`, `sub-2131`, `sub-2133`, `sub-2134`, `sub-2135`, `sub-2136`, `sub-2137`, `sub-2138`, `sub-2140A`, `sub-2141`, `sub-2142`, `sub-2143`, `sub-2149`, `sub-2170A`, `sub-2171`, `sub-2174`, `sub-2174A`, `sub-2176`, `sub-2176A`, `sub-2177`, `sub-2177A`, `sub-2179`, `sub-2184A`, `sub-2187`, `sub-2193`, `sub-2193A`, `sub-2195`, `sub-2196`, `sub-2197`, `sub-2199`, `sub-2213`, `sub-2214A`, `sub-2217A`, `sub-2221A`, `sub-2222`, `sub-2223`.

**resting-task-2 — 33 included:**

`sub-2237A`, `sub-2238A`, `sub-2245A`, `sub-2246A`, `sub-2249A`, `sub-2259A`, `sub-2262A`, `sub-2266A`, `sub-2268A`, `sub-2318A`, `sub-2336A`, `sub-2342A`, `sub-2350A`, `sub-2351A`, `sub-2372A`, `sub-2379A`, `sub-2384A`, `sub-2387A`, `sub-2389A`, `sub-2392A`, `sub-2397A`, `sub-2406A`, `sub-2418A`, `sub-2448A`, `sub-2456A`, `sub-2477A`, `sub-2480A`, `sub-2496A`, `sub-2512A`, `sub-2526A`, `sub-2530A`, `sub-2578A`, `sub-2581A`.

## 1.9 Feature definition and validation

Features: `relative_delta`, `relative_theta`, `relative_alpha`, and `relative_beta`.

- Welch PSD for each accepted four-second epoch and channel.
- Two-second Hann windows, 50% overlap, constant detrending, mean Welch averaging, density scaling.
- At 200 Hz, each window contains 400 samples and gives 0.5 Hz frequency-bin spacing.
- First average PSDs equally across accepted epochs within each channel.
- Integrate by summing PSD bins times bin width.
- Divide each channel's band power by that channel's total power from 1 through 30 Hz.
- Average the resulting relative power equally across the 49 shared channels. This is **mean of channel-wise ratios**, not ratio of channel-averaged powers.
- One output row per included participant. Participants are not weighted by their number of accepted epochs in later tabular data simply because more epochs survived.

| Band | Frequency bins |
| --- | --- |
| Delta | 1 ≤ f < 4 Hz |
| Theta | 4 ≤ f < 8 Hz |
| Alpha | 8 ≤ f < 13 Hz |
| Beta | 13 ≤ f ≤ 30 Hz |
| Denominator | 1 ≤ f ≤ 30 Hz |

The bands partition the denominator without overlapping boundary bins. All four features should sum to one up to numerical rounding.

Checks actually passed:

- Executed every notebook code cell in a fresh kernel: execution counts 1 through 8, no cell errors.
- Notebook JSON/schema validation with `nbformat`.
- Unique participant keys in QC and features, with no shared feature-table IDs across datasets.
- Same four feature columns, finite values, values between zero and one, and sums equal to one within `1e-10` tolerance.
- Positive finite PSD total power for every included channel/recording.
- Exact agreement between feature participant IDs and included participant-QC rows, and between feature source recording IDs and included recording-QC rows.
- At least 60 usable seconds and exactly 49 identical retained channels for all included participants.
- Exclusion reasons present for every excluded participant.
- Epoch-log retained counts agree with recording-QC counts.
- Re-read the saved CSVs and independently checked included-ID agreement for each dataset.
- `git diff --check` passed; no source-data changes were reported.

### Synthetic checks of the processing function

Ran separate temporary checks using the actual notebook preprocessing function:

1. A synthetic 100-second, 1,000 Hz recording with three channels, a known 10 Hz signal, low noise, and a large injected artifact. Processing retained 22 of 24 epochs (88 seconds), rejected artifact-contaminated epochs, and preserved a PSD peak at 10 Hz within 0.5 Hz.
2. A synthetic all-zero recording. It retained zero epochs, produced no spectrum/features, and returned the explicit insufficient-usable-duration reason.

These checks were run from temporary scripts/commands, not installed as a persistent repository test suite. They test processing behavior; they do not prove biological validity of the real-data channel mapping or thresholds. The real-data run emitted “all epochs were dropped” warnings for some recordings; those outcomes are represented in QC, not hidden or treated as successful feature extraction.

## 1.10 Files created or updated

| Path | Purpose |
| --- | --- |
| 00_master_data_check_and_preprocessing.ipynb | Executed, self-contained foundation notebook with results and two representative plots. |
| README.md | Expanded from the title-only README to setup, usage, dataset paths, LFS retrieval, output locations, and limitations. |
| requirements.txt | Exact versions of the eight direct notebook/execution dependencies. |
| .gitignore | Ignores .venv/, .ipynb_checkpoints/, __pycache__/, and .DS_Store. Existing tracked .DS_Store files were not removed. |
| .gitattributes | Root EEG LFS tracking rule created during migration; already in pushed data commit. |
| .venv/ | Local Python environment; ignored and not committed. |
| HANDOFF.md | This timestamped work history; append future numbered sections. |

All saved derived outputs are in [outputs/master_preprocessing](outputs/master_preprocessing). Source data are separate and unchanged. Running the notebook again overwrites the named derived outputs; archive results before a scientifically meaningful procedure change if a historical comparison is needed.

| Output file | Contents |
| --- | --- |
| resting-task-1_features.csv | 74 included participant rows, four relative-power features, diagnosis/acquisition, source recording ID, SHA-256, usable duration, retained epochs/channel count, export-interpretation flag. |
| resting-task-2_features.csv | Same schema, 33 included participant rows. |
| participant_inventory.csv | 143 participants with dataset/accession, label, acquisition, roster-row count and recording count. |
| participant_qc.csv | 143 participants, inclusion status, explicit exclusion reasons, usable duration, epoch counts, channel lists/counts, and recording IDs. |
| recording_qc.csv | 143 recordings, all source paths, metadata comparisons, materialization/readability checks, content hashes, raw QC, processing outcome and inclusion status. |
| epoch_qc.csv | 10,582 candidate epochs with recording ID, epoch index, onset, kept flag, and rejection channels/annotations. Onsets start at two seconds after the initial crop. |
| transferred_participant_check.csv | Ten transferred participants and roster/file/documentation placement checks. |
| dataset_compatibility.csv | Recording counts, sampling-rate sets, duration ranges, references, and documented filter summaries. |
| preprocessing_settings.json | Fixed settings, channel list, dataset mapping, package/Python versions, feature definition and unresolved assumptions. |
| dataset_check_report.md | Short generated dataset counts/QC/results report and readiness checklist. |
| resting-task-1_representative_raw.png | Raw signal and PSD figure for sub-1448. |
| resting-task-2_representative_raw.png | Raw signal and PSD figure for sub-2235A. |

## 1.11 Environment and how to resume

The execution environment used Python **3.14.7**. Git LFS was installed with Homebrew; notebook dependencies were installed in the project-local `.venv`, not with a global pip install.

Pinned direct dependencies:

```text
numpy==2.5.4
pandas==3.1.1
scipy==1.18.1
matplotlib==3.11.2
mne==1.13.2
nbformat==5.11.1
nbclient==0.11.0
ipykernel==7.4.0
```

For a new checkout:

```sh
git lfs install
git lfs pull
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Use Python 3.14 for the recorded environment. In VS Code, open the notebook at the project root, select the `.venv` Python kernel, and run all cells in order. A GitHub source ZIP may contain pointers instead of the actual EEG recordings; confirm LFS materialization. The first dataset download is approximately 20 GB.

Execution in this work used `nbclient` in a fresh kernel with the project root as the working directory and wrote the executed outputs back to the notebook. The temporary build/execution/synthetic-check scripts are not required for normal use: the notebook itself contains the implementation.

## 1.12 Remaining limitations and next steps

1. **Person-level cohort independence is unresolved.** The documentation and exact-ID/hash checks support distinct files and describe separate collection samples, but cannot exclude the same person appearing under different IDs. Obtain a trustworthy subject crosswalk or author confirmation before calling this a definitively independent external test cohort.
2. **Channel mapping and calibration are conventional interpretations.** The user authorized proceeding without original records. Current processing follows BIDS ordering and the EEGLAB/MNE microvolt convention; it does not establish original electrode identity or calibration independently.
3. **Prior processing is not fully known.** `SoftwareFilters: n/a`, absent hardware-filter details, and EEGLAB-export headers are not a full processing history. No claim has been made that these are untouched acquisition files.
4. **No original artifact annotations or bad-channel labels are available.** Automated checks catch selected obvious problems, not every blink, muscle artifact, movement, or other physiological confound. A few representative plots are not manual review of all participants.
5. **Task 2 attrition is high.** Twenty-eight of 61 participants are excluded, versus eight of 82 in Task 1. Interpret later results for the retained population carefully. Do not adjust exclusions based on Task 2 diagnosis-feature patterns or predictive performance. Any technically justified revision should be documented before rerunning and applied consistently to both datasets.
6. **Detailed epoch-cause attribution is limited.** Logs preserve offending channel names and rejected epochs, but not separate flat/high-amplitude causes or rejection stage. If that detail is needed, improve logging in a future section rather than retroactively assigning causes.
7. **Later analyses remain separate.** Any learned scaling, imputation, feature selection, or model fitting belongs in later notebooks, fitted on Dataset 1 only. This foundation does not estimate model performance or answer the project research questions.
8. **Implementation work is still local.** Review and commit/push the notebook, supporting files, outputs, and handoff when requested. The earlier EEG-data upload is already complete; avoid confusing that success with publication of the later notebook work.

When continuing, read the notebook, `preprocessing_settings.json`, `participant_qc.csv`, and `dataset_check_report.md` first. If the pipeline changes, rerun end to end, repeat relevant validation, record the exact before/after participant counts and exclusion changes, and append a newly timestamped section here. Preserve the distinction between findings verified in files, documented export conventions, and unresolved scientific questions.

# Section 2 — Exclusion investigation and isolated bad-channel revision, as of November 10, 2026, 3:12:16 PM EST

Timestamp: **2026-11-10 15:12:16 America/New_York (UTC−05:00)** / **2026-11-10 20:12:16 UTC**.

This section covers the investigation of the excessive Task 2 exclusions reported in Section 1.8, and the resulting preprocessing revision. Two agents did the work. A first agent (Codex) archived the baseline, ran the diagnosis-blind investigation and chose the revision, then stopped before implementing it. A second agent (Claude Code) checked the state Codex left, confirmed that the revision had **not** been applied, implemented exactly the revision Codex specified, reran the notebook and validated it.

## 2.1 Corrections to Section 1

- **Backup branch (Section 1.2).** Section 1 says `backup/pre-lfs-sync` was absent and that "the handoff does not establish why." The reason: the LFS migration had already rewritten that branch to `bada33e`, the same commit as `main`, so it was no longer a backup. The user then explicitly authorized deleting it and permanently removing the unreachable pre-migration commit `a42132e` (branch delete, reflog expiry, `git gc --prune=now`). Before deletion, every file in `a42132e` was checked against `bada33e`: 484 non-EEG files are byte-identical, all 143 `.eeg` blobs match their LFS SHA-256/size, and the only addition is `.gitattributes`. All recordings remain in `data/`, the local LFS store and GitHub.
- **Logging limitation (Section 1.12, item 6).** This is now resolved: rejections are logged by rule (high/flat) and stage (before/after reference), with offending channels.

## 2.2 Baseline preservation

The Section 1 notebook, README, requirements, handoff and all `outputs/master_preprocessing` files were copied to `outputs/baseline_2026-11-10_145427_EST/`, with a SHA-256 manifest (`sha256_manifest.json`). That folder is the reference for every before/after comparison below and must not be overwritten.

**Interrupted-run note:** a notebook execution at about 15:02 EST re-ran the *unchanged* Section 1 notebook. Its outputs were byte-identical to the baseline, and only cell timestamps and kernel IDs differed. It was not the revision.

## 2.3 Diagnosis-blind investigation (`outputs/exclusion_investigation`, `scripts/`)

Scripts: `scripts/diagnose_baseline_exclusions.py` and `scripts/evaluate_ocular_ica.py`. Both read the baseline QC with the diagnosis column dropped and are run from the project root with `.venv/bin/python`. Codex's isolated-channel evaluation was a temporary script; its output is `isolated_channel_evaluation.csv`.

- **Reproduction.** A NumPy re-implementation of the fixed screen reproduced the baseline retained-epoch count for all 143 recordings (asserted in the script).
- **Stage and rule (baseline, 49 channels).**

| Dataset | Candidate epochs | High-amplitude failures before reference | Flat failures before reference | Failures after reference (high/flat) | Kept |
| --- | --- | --- | --- | --- | --- |
| resting-task-1 | 6068 | 1971 | 10 | 3 / 2 | 4083 |
| resting-task-2 | 4514 | 2650 | 0 | 3 / 0 | 1861 |

  Nearly all loss is high-amplitude rejection before referencing. Flatness and the post-reference check are negligible.
- **Channels.** Losses are dominated by FP1/FP2/AF7/AF3/AF4, more so in Task 2 (see `rejection_channel_summary.csv`). The inspected examples show widespread, cross-correlated frontal transients consistent with eye artifacts (for example sub-2235A and sub-2267A). A few recordings instead show one channel failing in essentially every epoch (`diagnostic_*.png`).
- **Units and mapping.** `reader_unit_checks.csv`: MNE's values equal a direct little-endian float32 channel-major decode × 1e-6 (maximum error 0.0 V) for all recordings, and all scalp rows are `microV`. This confirms consistent reading of the export convention. It is **not** independent verification of the original calibration. No electrode-coordinate files exist in either dataset, and MNE reports no montage.
- **Isolated-channel candidates.** A channel was a candidate if it failed high in ≥90% of epochs with a median peak-to-peak ≥5× the median channel. Eight channel/recording pairs met that. Four had a maximum absolute correlation with any other channel below 0.4 (sub-2015 FP1, sub-2426A F3, sub-2431A F3, sub-2505A AF7). The other four (sub-2276A P4, sub-2279A P4, sub-2290A CP4, sub-2356A FP1) correlate at 0.79–0.996 with other channels. They are therefore not isolated, and the rule leaves them alone.
- **Ocular ICA pilot (not adopted).** Extended-infomax ICA with 20 components was run on five recordings, with one component selected by fixed FP1/FP2-correlation and frontal-loading rules. It reduced frontal transients in several examples (for example sub-2009: 12 → 74 epochs; sub-2235A: 8 → 72), but **every fit reached the 300-iteration cap without converging**, and the auxiliary EOG channel mapping is unresolved. It was kept as exploratory evidence only.

## 2.4 Revision implemented (notebook revision 2)

Same thresholds, filter, epoching, 60-second minimum and bands as Section 1. Changes:

1. **Isolated bad-channel omission.** This uses one rule for both datasets and is applied before screening, to the candidate epochs before referencing. A channel is omitted if it (a) fails >200 µV in ≥90% of epochs, (b) has a median peak-to-peak ≥5× the across-channel median, and (c) has a maximum absolute correlation <0.4 with every other channel over the continuous preprocessed (filtered, resampled, trimmed) recording. At most one channel is omitted. If two or more qualify, none is omitted (no recording hit this case). The omitted channel is excluded from the average reference, the epoch screen and the channel-averaged features, leaving 48 channels. **No interpolation**, because no electrode coordinates are supplied. Rationale: these channels show non-physiological rectangular/step signals that are uncorrelated with neighbours (see the `cleaning_*.png` plots), so a single bad electrode should not discard the whole recording. The rule thresholds were set from diagnosis-blind channel statistics, not from feature or label patterns.
2. **Staged rejection logging.** `epoch_qc.csv` now has `rejection_stage`, `pre_reference_high_channels`, `pre_reference_flat_channels`, `post_reference_high_channels`, `post_reference_flat_channels` and `annotation`, and keeps `rejection_channels_or_annotation` for the rejecting stage. `recording_qc.csv` gains per-stage/per-rule counts, `isolated_bad_channel_candidates`, `omitted_channel` and the `baseline_49ch_*` comparison columns. The feature CSVs gain `omitted_channel`.
3. **Epoch screening is now done in NumPy** (peak-to-peak > 200 µV or < 1 µV per channel, then average reference over the retained channels, then the same screen again) instead of MNE `drop_bad`. This is behaviour-preserving: it reproduces the archived Section 1 retained counts exactly.
4. **New outputs:** `rejection_stage_summary.csv`, `rejection_channel_summary.csv`, and four `cleaning_<dataset>_<participant>.png` plots. The notebook grew from 15 to 17 cells (a cause-summary cell and a cleaning-plot cell after the preprocessing cell). The Markdown in Sections 3–6 and the settings JSON (`isolated_bad_channel_rule`, `reference`, `revision`, and the new unresolved item about eye artifacts) were updated to match.

## 2.5 Results

| Dataset | Diagnosis | Inventoried | Included, Section 1 | Included, revision 2 |
| --- | --- | --- | --- | --- |
| resting-task-1 | Control | 32 | 29 | 29 |
| resting-task-1 | Psychosis | 50 | 45 | 46 |
| resting-task-2 | Control | 30 | 14 | 14 |
| resting-task-2 | Psychosis | 31 | 19 | 21 |
| Both | All | 143 | 107 | **110** |

Recovered participants: sub-2015 (Task 1, FP1 omitted, 0 → 280 s), sub-2431A (Task 2, F3 omitted, 0 → 228 s) and sub-2505A (Task 2, AF7 omitted, 12 → 148 s). sub-2426A had F3 omitted but remains excluded (0 s) because FP1/FP2/AF7 also fail. No participant lost inclusion. All three recovered participants carry the `Psychosis` label. This was not used in, and was not known when setting, the rule; it is reported only for transparency.

Revised epoch totals: Task 1 has 1901 high / 10 flat failures before reference, 3 / 2 after, and 4153 kept. Task 2 has 2559 / 0 before, 3 / 0 after, and 1952 kept. Usable seconds among included participants (minimum / median / maximum): Task 1 68 / 236 / 296; Task 2 96 / 212 / 296. Exclusion rates: Task 1 **7/82 = 8.5%** (was 9.8%) and Task 2 **26/61 = 42.6%** (was 45.9%).

Still excluded (all for fewer than 60 usable seconds):
- **Task 1:** sub-2009, sub-2020, sub-2034, sub-2124, sub-2178, sub-2218, sub-2221.
- **Task 2:** sub-2235A, sub-2240A, sub-2252A, sub-2267A, sub-2269A, sub-2276A, sub-2279A, sub-2290A, sub-2320A, sub-2355A, sub-2356A, sub-2367A, sub-2403A, sub-2419A, sub-2426A, sub-2430A, sub-2442A, sub-2476A, sub-2479A, sub-2494A, sub-2498A, sub-2503A, sub-2514A, sub-2518A, sub-2538A, sub-2574A.

**Unresolved cause:** the remaining Task 2 attrition is mostly widespread frontal high-amplitude transients consistent with eye artifacts. This revision does not address them, by design. The minimum duration was not lowered, thresholds were not raised, and frontal channels were not removed.

## 2.6 Checks actually run

- Notebook executed top to bottom in a fresh `.venv` kernel with `nbclient` from the project root: code cells ran in order (execution counts 1–10), with no errors, in 103 s. All in-notebook assertions passed. New assertions cover: at most one omitted channel; retained channels equal the shared set minus the omitted one; `n_retained_channels` is 49 or 48 to match; and before-reference rejections in `epoch_qc` match the recording counts.
- Compared against `outputs/baseline_2026-11-10_145427_EST/`:
  - The recomputed `baseline_49ch_retained_epochs` and `baseline_49ch_included` equal the archived `retained_epochs`/`included` for all 143 recordings.
  - Recordings without an omitted channel have identical retained counts.
  - The four relative-power features of all 107 previously included participants are **bit-for-bit identical** (maximum absolute difference 0.0).
- The four cleaning plots were visually inspected.
- No source-data changes: `git diff --stat -- data` is empty.

## 2.7 Git status and remaining limitations

Nothing from Sections 1–2 beyond the EEG data commit `bada33e` has been committed or pushed. Untracked or modified: `README.md`, `.gitignore`, the notebook, `HANDOFF.md`, `outputs/` (including the baseline archive and the investigation outputs), `requirements.txt` and `scripts/`.

Section 1.12 still applies, except item 6 (resolved above) and item 5. For item 5, Task 2 attrition remains high (42.6% versus 8.5%), and the dominant cause is now identified as frontal transients rather than unknown. Possible next steps, none taken:
- A converging, documented ocular-artifact method, applied identically to both datasets and validated diagnosis-blind.
- A resolution of the auxiliary EOG channel mapping.

# Section 3 — Review of the ocular-ICA "convergence failures", as of November 10, 2026, 10:49:19 PM EST

Timestamp: **2026-11-10 22:49:18 America/New_York (UTC−05:00)** / **2026-11-11 03:49:19 UTC**.

Scope: this section explains why the five exploratory ICA fits from Section 2.3 reported reaching the iteration limit. It tests one correction, without using diagnosis labels or classification. No components were removed, the notebook was not modified or rerun, and neither preprocessing version was changed: `outputs/baseline_2026-11-10_145427_EST/` (Section 1) and `outputs/master_preprocessing/` (revision 2) are untouched.

## 3.1 Correction to Section 2

Section 2.3 (and the notebook's Section 5 text and `preprocessing_settings.json` "unresolved" entry from revision 2) say that every ICA fit "reached the 300-iteration cap without converging." **That is incorrect.** All five fits met MNE's convergence criterion. The notebook and settings wording were left as-is so revision 2's outputs stay unchanged. Correct it the next time the notebook is deliberately revised.

## 3.2 Configuration reviewed (as in `scripts/evaluate_ocular_ica.py`)

| Item | Value |
| --- | --- |
| Algorithm | Extended infomax, `mne.preprocessing.infomax` (MNE 1.13.2), random_state 27 |
| Filtering | 0.5–40 Hz 4th-order Butterworth, zero-phase; FFT resample to 200 Hz; 2 s edge trim; additional 1 Hz 4th-order Butterworth high-pass on the fitting copy |
| Reference during fit | Recorded reference (TP9 is not among the 49 channels); not average-referenced |
| Data | 49 shared channels; 296 s per recording; fit with `decim=2` → 29,600 samples (100 Hz effective) |
| Components | 20 (PCA to 20 before ICA); 20 components retain 98.2–99.9% of PCA variance |
| Estimated rank | 49 (both `rank="info"` and the estimated rank); smallest/largest singular value ratio 0.0017–0.014; no rank deficiency |
| Samples per component² | 74 (well above the common ≈20–30 heuristic) |
| Iteration limit | `max_iter=300` (MNE's `"auto"` default for infomax would be 500) |
| Warnings | MNE issues **no** convergence warning for infomax. The only signal Codex used was `n_iter_ == 300`. sub-1448 and sub-2235A had 6 and 11 automatic restarts with a lowered learning rate after early weight blow-up; MNE does this routinely and it is not an error. |

## 3.3 Cause: an MNE reporting quirk, not a fitting failure

In `mne/preprocessing/infomax_.py`, when the weight-change stopping rule is met (`change < w_change`, default 1e-12), the loop runs `step = max_iter` and returns that as `n_iter`. **A fit that converges therefore reports `n_iter_` equal to the limit.** Evidence (`scripts/review_ocular_ica_convergence.py` → `outputs/ica_convergence_review/`):

- Step values were captured at full precision from the log record arguments (the formatted log rounds below 1e-8). Every fit stopped after 120–134 real steps, with a final weight change of 4.8e-13 to 1.0e-12, below the 1e-12 criterion.
- All fits also passed EEGLAB `runica`'s default stop value for more than 32 channels (1e-7, on the same weight-change quantity) by steps 63–72.
- Rerunning with `max_iter=3000` gave **identical** unmixing results for seed 27: matched component pattern r = 1.000 for all 20 components, the same stopping step, and the same ~2 s runtime. Raising the limit, the obvious "correction," changes nothing because the limit was never binding.
- Caveat: as is standard for infomax, the criterion is reached partly through learning-rate annealing (about 1e-3 down to about 4e-9). Meeting it shows the weights stopped changing, not that a global optimum was found. Seed stability is therefore the more relevant check.

## 3.4 Seed stability, without diagnosis labels (`component_stability.csv`)

Fits with seeds 27, 1 and 2 (3,000-step limit) were compared by matching component sensor patterns (Hungarian assignment on absolute correlation):

- **Ocular component under the fixed selection rule:** where a component was selected (4 of 5 recordings), all three seeds chose the matched component, with pattern r ≥ 0.99996 and FP1/FP2 correlation varying by under 0.002. In sub-2237A, no component met the rule under any seed.
- **Whole decomposition:** median matched r was 0.96–0.9996. sub-2009, sub-2235A and sub-2237A had all 20 components at r ≥ 0.95. sub-1448 (16–18/20) and sub-2267A (12–14/20) had some unstable non-ocular components. sub-2267A is a heavily artifact-contaminated recording (0 retained epochs under both preprocessing versions).

## 3.5 Conclusion and what is still unsupported

No configuration or implementation error explains the "failures." The fits converged and the identified ocular component is reproducible across seeds. No correction to the ICA configuration is justified. The only fix is interpretive: judge convergence by the final weight change, not `n_iter_`.

This removes convergence as a reason to reject ICA, but **does not yet justify applying it**. Still open before any component removal or full-pipeline rerun:
1. Component identification relies on correlation with the scalp channels FP1/FP2 plus a frontal-loading ratio. There are no EOG channels (the auxiliary mapping is unresolved) and no electrode coordinates for topographic review.
2. Cleaning quality has not been quantified: how much non-ocular frontal and other signal is removed, and the effect on spectra and band power across all channels.
3. The fits include large non-ocular artifacts (for example sub-2267A); whether to exclude such segments before fitting has not been evaluated.

Checks run: the review script completed for all 5 recordings × 4 fits with no errors, and `git diff --stat -- data` is empty. Nothing has been committed. New untracked files: `scripts/review_ocular_ica_convergence.py` and `outputs/ica_convergence_review/` (`fit_summary.csv`, `component_stability.csv`, `weight_change_trajectories.csv`).

# Section 4 — Ocular-component removal quality evaluation and text correction, as of November 16, 2026, 12:38:45 PM EST

Timestamp: **2026-11-16 12:38:45 America/New_York (UTC−05:00)** / **2026-11-16 17:38:45 UTC**.

**Decision: ocular-component removal is not supported by the pilot and is not applied.** The 110-participant revision 2 preprocessing is retained unchanged. Because the pilot failed, the procedure was not validated on additional recordings, as the task instructed.

## 4.1 Convergence-text correction (no numerical change)

- Notebook Section 5 Markdown: replaced "not adopted because its fits did not converge" with the correct account. The fits converged (Section 3); the component tracked blinks; removal failed the quality criteria below; and EOG channels and electrode positions are missing.
- `preprocessing_settings.json` (and, through the same notebook list, `dataset_check_report.md`): the last "unresolved" item now gives the same reason. Strictly, the earlier JSON wording ("evaluated but not adopted") did not claim non-convergence; it was clarified for consistency.
- Before re-execution, revision 2 was archived to `outputs/revision2_2026-11-10_151143_EST/` (the notebook, all `master_preprocessing` files, and `sha256_manifest.txt`). The notebook was then re-executed with `nbclient` in a fresh kernel: 103 s, no errors, all assertions passed. **All 16 CSV/PNG outputs are byte-identical to the archive.** Only the one sentence in `preprocessing_settings.json` and `dataset_check_report.md` differs. Counts remain 75 (Task 1) and 35 (Task 2).

## 4.2 Method (`scripts/evaluate_ocular_ica_quality.py` → `outputs/ocular_ica_quality/`)

Diagnosis-blind: diagnosis is dropped on load and no classification is done. It covers the same five pilot recordings, with the same ICA configuration and component rule as `scripts/evaluate_ocular_ica.py`. Preprocessing up to epoching is identical to the notebook. Before/after comparisons use average reference, as the features do.

- **Blink detection independent of ICA:** mean(FP1, FP2) at 1–10 Hz; a positive peak ≥ max(50 µV, median + 6 robust SD) with half-height width 80–600 ms. It counts as blink-like when FP1 and FP2 correlate > 0.8 within ±250 ms and the O1/O2/OZ deflection is < 20% of the frontal peak.
- **Subsets:** blink epochs contain a blink-like event. Quiet epochs contain no detected frontal peak and pass the existing fixed screen.
- **Criteria, written into the script docstring before the first run.** Removal is supported only if all five hold:
  - C1: ≥ 80% of blinks coincide with a component peak (|robust z| > 5).
  - C2: ≥ 80% of component peaks fall at blinks.
  - C3: blink-epoch FP/AF RMS falls by ≥ 50%.
  - C4: in quiet epochs, posterior (P/PO/O) power changes by ≤ 5% in every band, and all-channel mean alpha and beta change by ≤ 5%.
  - C5: the same component is selected (pattern r ≥ 0.95) when epochs with > 200 µV on any channel outside FP/AF/F are excluded from the fit.
  These thresholds are project choices, not published standards.
- **Two metrics added after the first run, to explain the mechanism (not decision criteria):** the component's own band composition in quiet epochs, and signed posterior changes. A summary-logic bug (NaN versus None for sub-2237A) and an empty quiet-plot panel were fixed. No criterion was changed.

## 4.3 Evidence

| | sub-1448 | sub-2009 | sub-2237A | sub-2235A | sub-2267A |
| --- | --- | --- | --- | --- | --- |
| Dataset | Task 1 | Task 1 | Task 2 | Task 2 | Task 2 |
| Candidate component | IC1 | IC0 | none | IC0 | IC0 |
| Blink-like events | 51 | 139 | 0 | 112 | 43 |
| Blinks with component peak (C1) | 100% | 99% | – | 99% | 100% |
| Component peaks at blinks (C2) | 71% | 95% | – | 96% | 27% |
| Component–FP correlation outside blinks | 0.59 | 0.04 | – | 0.12 | 0.73 |
| Blink-epoch FP/AF RMS change (C3) | −46% | −71% | – | −74% | −46% |
| Quiet epochs | 31 | 5 | 73 | 8 | 0 |
| Quiet FP/AF RMS change | −20% | −15% | – | −28% | – |
| Quiet posterior delta, maximum absolute change | 11% | 10% | – | 34% | – |
| Quiet posterior alpha / beta, mean change | +0.2% / +1.7% | +10.6% / +12.6% | – | +9.5% / +8.7% | – |
| Component beta share during quiet epochs | 11% | 52% | – | 6% | – |
| Non-ocular disturbed epochs; refit pattern r (C5) | 2; 0.99998 | 0; 1.0 | – | 2; 0.99998 | 18; 0.99991 |
| Retained epochs before → after (not a criterion) | 72 → 72 | 12 → 74 | 74 | 8 → 72 | 0 → 19 |
| All criteria met | No (C2, C3, C4) | No (C4) | n/a: no blinks, correctly nothing selected | No (C4) | No (C2, C3; C4 not evaluable) |

Interpretation:
- **Blink alignment is strong** (C1), not just frontal correlation. Detected events have blink morphology: median width 111–170 ms, FP1/FP2 r ≈ 0.99–1.00, occipital ratio 0.04–0.08. The blink-locked component average reproduces the FP waveform (`quality_*.png`). In sub-2237A the only frontal peak had an occipital ratio of 0.85 (not blink-like), and no component was selected, which is consistent.
- **Removal does not leave blink-free data intact** (C4 fails wherever it can be evaluated):
  - In sub-1448, FP1 loses 58% of its quiet-epoch beta and up to 76% of its delta, and posterior delta drops by up to 11%. Blinks contribute little beta, so non-blink activity is being removed. Whether it is slow eye movement or neural signal cannot be determined without EOG.
  - In sub-2009 and sub-2235A, quiet-epoch posterior alpha/beta *increase* by about 9–13% on average, and AF3 beta by up to about 55%. The sub-2009 component is 52% beta in quiet epochs. The component therefore carries non-ocular high-frequency (frontal-electrode or muscle-like) activity, and subtracting it injects that activity into other channels.
  - In sub-2267A, blink-epoch FP/AF beta increased 146% after removal, and large frontal transients remain.
- **Non-ocular disturbances barely changed the fit** (C5 passes; pattern r ≥ 0.9999). However, the pilot had only 0–18 disturbed epochs per recording, so this is weak evidence for heavily disturbed recordings.
- Retention gains (for example 8 → 72 epochs) were **not** used as evidence. They partly reflect the non-blink content removed above.

## 4.4 Limitations and possible next steps (not taken)

- There are no confirmed EOG channels (the auxiliary mapping is unresolved) and no measured electrode positions, so component identity cannot be confirmed topographically. The blink detector uses FP1/FP2, the same channels as the selection rule. It adds morphological and temporal evidence but is not independent of the frontal channels.
- Quiet-epoch estimates rest on only 5–8 epochs in the two artifact-heavy recordings (though before/after are compared on the same epochs). The 5% limits are project choices.
- No claim is made that any cleaning would preserve all neural activity.
- A plausible contributor is that 20 components for rank-49 data group blinks together with frontal high-frequency activity. Testing other component counts or artifact-handling methods would need new, pre-specified criteria, applied identically to both datasets and judged on cleaning quality, not retention.

## 4.5 Files and Git status

- **New:** `scripts/evaluate_ocular_ica_quality.py`; `outputs/ocular_ica_quality/` (`pilot_summary.csv`, `pilot_channel_changes.csv`, `pilot_frontal_events.csv`, `quality_<participant>.png` for the 4 recordings with a candidate component); and `outputs/revision2_2026-11-10_151143_EST/`.
- **Modified:** the notebook (one Markdown sentence and one settings string; re-executed); `outputs/master_preprocessing/preprocessing_settings.json` and `dataset_check_report.md` (one sentence each); `README.md` (archive pointers).
- `git diff --stat -- data` is empty.
- Nothing is committed; the same untracked set as Section 2.7 plus the files above.
