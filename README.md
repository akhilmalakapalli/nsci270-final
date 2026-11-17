# NSCI 270 EEG project

Start with [00_master_data_check_and_preprocessing.ipynb](00_master_data_check_and_preprocessing.ipynb). It checks participant inventories, dataset compatibility and recording quality, then applies one fixed preprocessing procedure and saves participant-level relative delta, theta, alpha and beta power. Later research-question notebooks should use its separate feature tables.

## Run

Use Python 3.14 and the project's `.venv` kernel in VS Code, or create an environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Open the notebook at the project root and run all cells in order. The data are approximately 20 GB; processing reads one recording at a time. The source datasets are never rewritten.

- `data/resting-task-1`: OpenNeuro ds003944 v1.0.1, intended training data.
- `data/resting-task-2`: OpenNeuro ds003947 v1.0.1, intended held-out test data.
- `outputs/master_preprocessing`: separate feature CSVs, participant and recording QC, epoch rejection logs, settings, representative plots, and a dataset-check report.

Read `outputs/master_preprocessing/dataset_check_report.md` before later analyses. A recording may have one isolated, persistently bad channel omitted (not interpolated) under a fixed rule; see `HANDOFF.md` Section 2. The original-run outputs are archived in `outputs/baseline_2026-11-10_145427_EST/` and revision 2 in `outputs/revision2_2026-11-10_151143_EST/`. The exclusion and ocular-ICA investigations are in `outputs/exclusion_investigation/`, `outputs/ica_convergence_review/`, `outputs/ocular_ica_quality/` and `scripts/`. Ocular ICA is not applied (see `HANDOFF.md` Section 4). Channel ordering and units follow the documented BIDS/EEGLAB export conventions; the original acquisition records and full processing history are unavailable. The READMEs describe independently collected samples, but do not establish person-level non-overlap. Ten acquisition-2 participants are intentionally in Task 1 and remain eligible.

The `.eeg` recordings use Git LFS. After cloning, install Git LFS and run `git lfs install` and `git lfs pull` to materialize them. A GitHub source ZIP alone may contain pointers instead of recordings.

## Experiment 1 (Question 1): cross-dataset classification

Open [01_band_power_cross_dataset_classification.ipynb](01_band_power_cross_dataset_classification.ipynb) with the `.venv` kernel (`pip install -r requirements.txt` includes scikit-learn) and run all cells. It chooses logistic-regression settings (C and class weighting) by 5-fold cross-validation within Dataset 1 (Task 1), saves that choice, and then tests the locked model once on Dataset 2 (Task 2). It reads only the frozen preprocessing in `outputs/frozen_preprocessing_2026-11-16_124625_EST/` and, for the sensitivity check, the 107-participant baseline. Both are verified against their SHA-256 manifests first.

Results are written to `outputs/experiment_1_revised/`: CV scores, selected settings, test predictions and metrics, ROC and confusion-matrix figures, settings with input hashes, and `results_summary.md`. This is a revised exploratory analysis, because Dataset 2 results were seen in the original version. The original notebook and outputs are archived unchanged in `outputs/archive_experiment_1_original_2026-11-16_125350_EST/`. See `HANDOFF.md` Sections 5–6.

## Experiment 2 (Question 2): within- versus cross-dataset performance

Open [02_within_vs_cross_dataset_performance.ipynb](02_within_vs_cross_dataset_performance.ipynb) with the `.venv` kernel and run all cells. It estimates internal performance on Dataset 1 with repeated nested cross-validation: 5 outer folds × 5 repeats (seeds 101–505), with inner 5-fold selection over the same grid as Experiment 1. It then compares that with the Dataset 2 result reused from `outputs/experiment_1_revised/`, which is verified but not refitted. Outputs are in `outputs/experiment_2/`: outer-fold predictions, fold and repeat metrics with the settings chosen per fold, inner candidate scores, summary metrics and the descriptive generalization gap, a comparison figure, settings with input hashes, and `results_summary.md`. See `HANDOFF.md` Section 7.
