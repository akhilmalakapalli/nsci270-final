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
