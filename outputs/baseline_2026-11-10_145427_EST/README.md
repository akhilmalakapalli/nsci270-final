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

Read `outputs/master_preprocessing/dataset_check_report.md` before later analyses. Channel ordering and units follow the documented BIDS/EEGLAB export conventions; the original acquisition records and full processing history are unavailable. The READMEs describe independently collected samples, but do not establish person-level non-overlap. Ten acquisition-2 participants are intentionally in Task 1 and remain eligible.

The `.eeg` recordings use Git LFS. After cloning, install Git LFS and run `git lfs install` and `git lfs pull` to materialize them. A GitHub source ZIP alone may contain pointers instead of recordings.
