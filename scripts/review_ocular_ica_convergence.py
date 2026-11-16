"""Review why the exploratory ocular-ICA pilot fits stopped at the iteration cap.

Diagnosis-blind: reads only recording paths/IDs from the baseline QC (diagnosis column
dropped) and never touches classification. Writes only to outputs/ica_convergence_review;
the baseline archive and outputs/master_preprocessing are not modified.

Run from the project root:  .venv/bin/python scripts/review_ocular_ica_convergence.py
"""
from pathlib import Path
import json
import logging
import time

import numpy as np
import pandas as pd
import mne
from scipy.optimize import linear_sum_assignment

mne.set_log_level("WARNING")
root = Path.cwd()
out = root / "outputs/ica_convergence_review"
out.mkdir(exist_ok=True)
base = root / "outputs/baseline_2026-11-10_145427_EST/master_preprocessing"
names = json.loads((base / "preprocessing_settings.json").read_text())["shared_channels"]
rows = pd.read_csv(base / "recording_qc.csv").drop(columns="diagnosis")
PILOT = ["sub-1448", "sub-2009", "sub-2237A", "sub-2235A", "sub-2267A"]
FRONTAL = np.array([n.startswith(("FP", "AF")) for n in names])
EEGLAB_STOP = 1e-7  # runica default 'stop' for >32 channels, applied to the same weight-change quantity
LONG_ITER, SEEDS = 3000, [27, 1, 2]


def prepare(row):
    """Identical to scripts/evaluate_ocular_ica.py up to the ICA fit."""
    table = pd.read_csv(row.channels_path, sep="\t")
    raw = mne.io.read_raw_brainvision(row.header_path, preload=False, verbose=False)
    raw.rename_channels(dict(zip(raw.ch_names[:60], table.iloc[:60]["name"].str.upper())))
    raw.pick(names).reorder_channels(names)
    raw.crop(tmax=min(raw.times[-1], 300 - 1/raw.info["sfreq"])).load_data()
    raw.filter(.5, 40, method="iir", phase="zero",
               iir_params={"order": 4, "ftype": "butter", "output": "sos"}, verbose=False)
    raw.resample(200, method="fft", verbose=False)
    raw.crop(tmin=2, tmax=raw.times[-1] - 2)
    fit = raw.copy().filter(1, None, method="iir",
                            iir_params={"order": 4, "ftype": "butter", "output": "sos"}, verbose=False)
    return raw, fit


def run_ica(fit, max_iter, seed):
    ica = mne.preprocessing.ICA(n_components=20, method="infomax", fit_params={"extended": True, "verbose": True},
                                random_state=seed, max_iter=max_iter)
    grab = StepLog()
    logger = logging.getLogger("mne")
    logger.addHandler(grab)
    try:
        ica.fit(fit, decim=2, verbose=True)  # infomax logs raw step/lrate/wchange as record args
    finally:
        logger.removeHandler(grab)
    return ica, grab.steps, grab.restarts


class StepLog(logging.Handler):
    """Keep full-precision infomax step values (the formatted log rounds wchange to 1e-8)."""
    def __init__(self):
        super().__init__(logging.INFO)
        self.steps, self.restarts = [], 0

    def emit(self, record):
        if str(record.msg).startswith("step "):
            self.steps.append(tuple(float(x) for x in record.args[:3]))
        elif "re-starting" in record.getMessage():
            self.restarts += 1


def ocular_choice(ica, fit):
    """Codex's fixed rule: both FP1 and FP2 |r| >= 0.8 and frontal/other loading ratio >= 3."""
    _, scores = ica.find_bads_eog(fit, ch_name=["FP1", "FP2"], measure="correlation",
                                  threshold=.8, verbose=False)
    dual = np.abs(np.asarray(scores)).min(axis=0)
    load = np.abs(ica.get_components())
    ratio = load[FRONTAL].mean(axis=0) / np.maximum(load[~FRONTAL].mean(axis=0), 1e-15)
    eligible = np.flatnonzero((dual >= .8) & (ratio >= 3))
    return (int(eligible[np.argmax(dual[eligible])]) if len(eligible) else None), dual


def match(a, b):
    """Match components of two fits by |correlation| of their sensor patterns."""
    A, B = a.get_components(), b.get_components()
    r = np.abs(np.corrcoef(A.T, B.T)[:A.shape[1], A.shape[1]:])
    i, j = linear_sum_assignment(-r)
    return r, dict(zip(i, j)), r[i, j]


summary, stability, trajectories = [], [], []
for pid in PILOT:
    row = rows[rows.participant_id == pid].iloc[0]
    raw, fit = prepare(row)
    data = fit.get_data()[:, ::2]  # same samples ICA sees with decim=2
    sv = np.linalg.svd(data - data.mean(axis=1, keepdims=True), compute_uv=False)
    rank_info = mne.compute_rank(fit, rank="info", verbose=False)["eeg"]
    rank_est = mne.compute_rank(fit, rank=None, verbose=False)["eeg"]

    fits = {}
    for label, max_iter, seed in [("pilot_300", 300, 27)] + [(f"long_seed{s}", LONG_ITER, s) for s in SEEDS]:
        t = time.time()
        ica, steps, restarts = run_ica(fit, max_iter, seed)
        comp, dual = ocular_choice(ica, fit)
        fits[label] = (ica, comp)
        wchange = np.array([s[2] for s in steps])
        trajectories += [{"participant_id": pid, "fit": label, "step": int(s[0]),
                          "lrate": s[1], "wchange": s[2]} for s in steps]
        eeglab_step = next((int(s[0]) for s in steps if s[0] > 2 and s[2] < EEGLAB_STOP), None)
        summary.append({
            "participant_id": pid, "dataset": row.dataset, "fit": label, "seed": seed,
            "algorithm": "extended infomax (mne.preprocessing.infomax)",
            "filtering": "0.5-40 Hz Butterworth (4th order, zero-phase) -> 200 Hz -> extra 1 Hz high-pass for fit",
            "fit_reference": "recorded (TP9), not average-referenced",
            "duration_seconds": round(fit.times[-1] + 1/fit.info["sfreq"], 2),
            "fit_samples_after_decim2": data.shape[1], "channels": len(names),
            "n_components": ica.n_components_, "rank_info": int(rank_info),
            "rank_estimated": int(rank_est), "singular_value_ratio_min_max": float(sv[-1] / sv[0]),
            "pca_variance_explained_by_20": float(ica.pca_explained_variance_[:20].sum()
                                                  / ica.pca_explained_variance_.sum()),
            "samples_per_component_squared": round(data.shape[1] / 20**2, 1),
            "max_iter": max_iter, "n_iter": int(ica.n_iter_), "hit_cap": int(ica.n_iter_) >= max_iter,
            "restarts_after_blowup": restarts,
            "mne_stop_threshold": 1e-12, "final_wchange": float(wchange[-1]),
            "final_lrate": float(steps[-1][1]),
            "wchange_at_step_300": float(wchange[299]) if len(wchange) >= 300 else None,
            "first_step_below_eeglab_1e-7": eeglab_step,
            "ocular_component": comp,
            "ocular_dual_fp_correlation": float(dual[comp]) if comp is not None else None,
            "seconds": round(time.time() - t, 1)})
        print({k: summary[-1][k] for k in ["participant_id", "fit", "n_iter", "final_wchange",
                                           "first_step_below_eeglab_1e-7", "ocular_component"]}, flush=True)

    ref_ica, ref_comp = fits[f"long_seed{SEEDS[0]}"]
    for label, (ica, comp) in fits.items():
        if label == f"long_seed{SEEDS[0]}":
            continue
        r, pairs, matched = match(ref_ica, ica)
        stability.append({
            "participant_id": pid, "reference_fit": f"long_seed{SEEDS[0]}", "compared_fit": label,
            "median_matched_pattern_r": float(np.median(matched)),
            "min_matched_pattern_r": float(matched.min()),
            "components_matched_r_ge_0.95": int((matched >= .95).sum()),
            "reference_ocular_component": ref_comp, "compared_ocular_component": comp,
            "ocular_components_are_matched_pair": (ref_comp is not None and comp is not None
                                                   and pairs.get(ref_comp) == comp),
            "ocular_pattern_r": float(r[ref_comp, comp]) if ref_comp is not None and comp is not None else None})
    raw.close()

pd.DataFrame(summary).to_csv(out / "fit_summary.csv", index=False)
pd.DataFrame(stability).to_csv(out / "component_stability.csv", index=False)
pd.DataFrame(trajectories).to_csv(out / "weight_change_trajectories.csv", index=False)
print(pd.DataFrame(stability).to_string(index=False))
