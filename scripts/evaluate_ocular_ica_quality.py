"""Can the suspected ocular ICA component be removed responsibly? (pilot recordings)

Diagnosis-blind: recording paths/IDs only (diagnosis column dropped); no classification.
Writes only to outputs/ocular_ica_quality; never modifies source data or earlier outputs.

Run from the project root:
    .venv/bin/python scripts/evaluate_ocular_ica_quality.py              # 5 pilot recordings
    .venv/bin/python scripts/evaluate_ocular_ica_quality.py sub-2015 ... # other recordings

ICA configuration and component rule are unchanged from scripts/evaluate_ocular_ica.py:
extended infomax, 20 components, seed 27, fit on a 1 Hz high-passed copy with decim=2;
candidate = component with |r| >= 0.8 to both FP1 and FP2 and frontal/other loading ratio >= 3.

Blink-like events are detected independently of ICA from FP1/FP2 morphology:
mean(FP1, FP2), 1-10 Hz, positive peak >= max(50 uV, median + 6 robust SD), half-height
width 80-600 ms; blink-like if FP1/FP2 waveforms correlate > 0.8 within +/-250 ms and the
occipital (O1/O2/OZ) deflection is < 20% of the frontal peak.

Criteria fixed BEFORE looking at results. Removal is supported for a recording only if:
  C1 blink-like events exist, and >= 80% of them coincide with a component peak (|robust z| > 5);
  C2 >= 80% of component peaks (|robust z| > 5) fall within +/-250 ms of a blink-like event;
  C3 in blink epochs, frontal-pole (FP/AF) RMS falls by >= 50%;
  C4 in quiet epochs (no detected frontal peak, passing the existing screen), every band's
     power changes by <= 5% on posterior channels (P/PO/O) and alpha and beta by <= 5%
     averaged over all channels;
  C5 the same component is selected, with pattern r >= 0.95, when epochs with non-ocular
     disturbances (> 200 uV on any channel outside FP/AF/F) are excluded from the fit.
A recording with blink-like events but no selected component counts against the rule.
"""
from pathlib import Path
import json
import re
import sys

import numpy as np
import pandas as pd
import mne
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import welch, find_peaks

mne.set_log_level("ERROR")
root = Path.cwd()
out = root / "outputs/ocular_ica_quality"
out.mkdir(exist_ok=True)
current = root / "outputs/master_preprocessing"
names = json.loads((current / "preprocessing_settings.json").read_text())["shared_channels"]
rows = pd.read_csv(current / "recording_qc.csv", keep_default_na=False).drop(columns="diagnosis")
PILOT = ["sub-1448", "sub-2009", "sub-2237A", "sub-2235A", "sub-2267A"]
SF, EPOCH = 200, 800
BANDS = {"delta": (1, 4), "theta": (4, 8), "alpha": (8, 13), "beta": (13, 30)}
REGION = {"FP": "frontal_pole", "AF": "frontal_pole", "F": "frontal", "FC": "central", "C": "central",
          "CP": "central", "FT": "temporal", "T": "temporal", "TP": "temporal",
          "P": "posterior", "PO": "posterior", "O": "posterior"}
region = np.array([REGION[re.sub(r"(\d+|Z)$", "", n)] for n in names])
FRONTAL = np.isin(region, ["frontal_pole"])
ANTERIOR = np.isin(region, ["frontal_pole", "frontal"])
POSTERIOR = region == "posterior"
IIR = {"order": 4, "ftype": "butter", "output": "sos"}


def prepare(row):
    """Identical to the preprocessing notebook up to epoching (recorded reference)."""
    table = pd.read_csv(row.channels_path, sep="\t")
    raw = mne.io.read_raw_brainvision(row.header_path, preload=False, verbose=False)
    raw.rename_channels(dict(zip(raw.ch_names[:60], table.iloc[:60]["name"].str.upper())))
    raw.pick(names).reorder_channels(names)
    raw.crop(tmax=min(raw.times[-1], 300 - 1/raw.info["sfreq"])).load_data()
    raw.filter(.5, 40, method="iir", phase="zero", iir_params=IIR, verbose=False)
    raw.resample(SF, method="fft", verbose=False)
    raw.crop(tmin=2, tmax=raw.times[-1] - 2)
    return raw


def fit_ica(raw, bad_epochs=()):
    fit = raw.copy().filter(1, None, method="iir", iir_params=IIR, verbose=False)
    if len(bad_epochs):
        fit.set_annotations(mne.Annotations([4.0*k for k in bad_epochs], 4.0, "BAD_nonocular"))
    ica = mne.preprocessing.ICA(n_components=20, method="infomax", fit_params={"extended": True},
                                random_state=27, max_iter=300)
    ica.fit(fit, decim=2, reject_by_annotation=True, verbose=False)
    _, scores = ica.find_bads_eog(fit, ch_name=["FP1", "FP2"], measure="correlation",
                                  threshold=.8, verbose=False)
    dual = np.abs(np.asarray(scores)).min(axis=0)
    load = np.abs(ica.get_components())
    ratio = load[FRONTAL].mean(axis=0) / np.maximum(load[~FRONTAL].mean(axis=0), 1e-15)
    eligible = np.flatnonzero((dual >= .8) & (ratio >= 3))
    comp = int(eligible[np.argmax(dual[eligible])]) if len(eligible) else None
    return ica, comp, dual, ratio


def robust_z(x):
    mad = 1.4826 * np.median(np.abs(x - np.median(x)))
    return (x - np.median(x)) / mad


def blink_events(raw):
    d = mne.filter.filter_data(raw.get_data(picks=["FP1", "FP2", "O1", "O2", "OZ"]) * 1e6, SF, 1, 10,
                               method="iir", iir_params=IIR, verbose=False)
    v = d[:2].mean(axis=0)
    threshold = max(50.0, np.median(v) + 6 * 1.4826 * np.median(np.abs(v - np.median(v))))
    peaks, props = find_peaks(v, height=threshold, distance=int(.3*SF),
                              width=(int(.08*SF), int(.6*SF)), rel_height=.5)
    events = []
    for p, width in zip(peaks, props["widths"]):
        w = slice(max(p - 50, 0), p + 50)
        symmetry = float(np.corrcoef(d[0, w], d[1, w])[0, 1])
        posterior = float(abs(d[2:, p].mean()) / v[p])
        events.append({"sample": int(p), "seconds": p / SF, "fp_amplitude_uv": float(v[p]),
                       "width_ms": float(width / SF * 1000), "fp1_fp2_r": symmetry,
                       "occipital_ratio": posterior, "blink_like": symmetry > .8 and posterior < .2})
    return v, threshold, pd.DataFrame(events, columns=["sample", "seconds", "fp_amplitude_uv", "width_ms",
                                                       "fp1_fp2_r", "occipital_ratio", "blink_like"])


def epochs_of(raw):
    return mne.make_fixed_length_epochs(raw, duration=4, preload=True, verbose=False).get_data(copy=False)


def screen(x):
    """The existing fixed screen (49 channels): 200/1 uV before and after average reference."""
    def ok(y):
        ptp = np.ptp(y, axis=-1) * 1e6
        return ((ptp <= 200) & (ptp >= 1)).all(axis=1)
    return ok(x) & ok(x - x.mean(axis=1, keepdims=True))


def band_power(x):
    f, p = welch(x, fs=SF, window="hann", nperseg=400, noverlap=200, detrend="constant", axis=-1)
    p = p.mean(axis=0)
    df = f[1] - f[0]
    power = {b: p[:, (f >= lo) & ((f <= hi) if b == "beta" else (f < hi))].sum(axis=1) * df
             for b, (lo, hi) in BANDS.items()}
    total = p[:, (f >= 1) & (f <= 30)].sum(axis=1) * df
    return f, p, power, total


def evaluate(pid):
    row = rows[rows.participant_id == pid].iloc[0]
    raw = prepare(row)
    ica, comp, dual, ratio = fit_ica(raw)
    v, threshold, events = blink_events(raw)
    events.insert(0, "participant_id", pid)
    blinks = events.loc[events.blink_like, "sample"].to_numpy() if len(events) else np.array([], int)
    X0 = epochs_of(raw)
    n = len(X0)
    blink_epoch = np.zeros(n, bool)
    blink_epoch[np.minimum(blinks // EPOCH, n - 1)] = True
    any_peak = np.zeros(n, bool)
    if len(events):
        any_peak[np.minimum(events["sample"].to_numpy() // EPOCH, n - 1)] = True
    kept0 = screen(X0)
    quiet = kept0 & ~any_peak
    result = {"participant_id": pid, "dataset": row.dataset, "candidate_component": comp,
              "candidate_dual_fp_r": float(dual[comp]) if comp is not None else float(dual.max()),
              "candidate_frontal_ratio": float(ratio[comp]) if comp is not None else None,
              "blink_threshold_uv": threshold, "frontal_peaks": len(events),
              "blink_like_events": int(len(blinks)), "blink_epochs": int(blink_epoch.sum()),
              "quiet_epochs": int(quiet.sum()), "retained_epochs_before": int(kept0.sum())}
    channel_rows = []
    if comp is None:
        raw.close()
        return result, events, channel_rows

    # C1/C2: temporal alignment of the component with blink-like events.
    src = ica.get_sources(raw).get_data()[comp]
    src *= np.sign(np.corrcoef(src, v)[0, 1])
    z = robust_z(src)
    ic_peaks, _ = find_peaks(np.abs(z), height=5, distance=int(.3*SF))
    near = lambda a, b: np.array([np.any(np.abs(b - x) <= 50) for x in a], bool)
    result["blinks_with_component_peak"] = float(near(blinks, ic_peaks).mean()) if len(blinks) else np.nan
    result["component_peaks"] = len(ic_peaks)
    result["component_peaks_at_blinks"] = float(near(ic_peaks, blinks).mean()) if len(ic_peaks) else np.nan
    outside = np.ones(len(z), bool)
    for b in blinks:
        outside[max(b - 100, 0):b + 100] = False
    result["component_fp_r_outside_blinks"] = float(np.corrcoef(src[outside], v[outside])[0, 1])
    if quiet.any():  # spectral make-up of the component itself when no blink is present
        _, _, ic_power, ic_total = band_power(epochs_of(ica.get_sources(raw))[quiet][:, [comp]])
        for b in BANDS:
            result[f"component_quiet_relative_{b}"] = float(ic_power[b][0] / ic_total[0])

    # C3/C4: before/after removal, average reference as in the features.
    clean = ica.apply(raw.copy(), exclude=[comp], verbose=False)
    X1 = epochs_of(clean)
    kept1 = screen(X1)
    A0, A1 = X0 - X0.mean(axis=1, keepdims=True), X1 - X1.mean(axis=1, keepdims=True)
    result["retained_epochs_after"] = int(kept1.sum())
    for subset, mask in [("blink", blink_epoch), ("quiet", quiet)]:
        if not mask.any():
            continue
        rms = np.sqrt((A1[mask]**2).mean(axis=(0, 2)) / (A0[mask]**2).mean(axis=(0, 2)))
        _, _, p0, t0 = band_power(A0[mask])
        _, _, p1, t1 = band_power(A1[mask])
        for c, name in enumerate(names):
            channel_rows.append({"participant_id": pid, "subset": subset, "channel": name, "region": region[c],
                                 "rms_ratio": rms[c],
                                 **{f"{b}_power_change": p1[b][c] / p0[b][c] - 1 for b in BANDS}})
        result[f"{subset}_frontal_pole_rms_change"] = float(rms[FRONTAL].mean() - 1)
        result[f"{subset}_posterior_rms_change"] = float(rms[POSTERIOR].mean() - 1)
        result[f"{subset}_frontal_pole_beta_mean_change"] = float((p1["beta"][FRONTAL] / p0["beta"][FRONTAL] - 1).mean())
        for b in BANDS:
            result[f"{subset}_posterior_{b}_max_abs_change"] = float(np.abs(p1[b][POSTERIOR] / p0[b][POSTERIOR] - 1).max())
            result[f"{subset}_posterior_{b}_mean_change"] = float((p1[b][POSTERIOR] / p0[b][POSTERIOR] - 1).mean())
            result[f"{subset}_all_{b}_mean_change"] = float((p1[b] / p0[b] - 1).mean())
            result[f"{subset}_relative_{b}_change"] = float((p1[b] / t1).mean() - (p0[b] / t0).mean())

    # C5: refit without epochs that have non-ocular disturbances.
    disturbed = np.flatnonzero((np.ptp(X0[:, ~ANTERIOR], axis=-1) * 1e6 > 200).any(axis=1))
    result["nonocular_disturbed_epochs"] = len(disturbed)
    if len(disturbed):
        ica2, comp2, _, _ = fit_ica(raw, disturbed)
        r = np.abs(np.corrcoef(ica.get_components()[:, comp], ica2.get_components().T)[0, 1:])
        result["refit_component"] = comp2
        result["refit_pattern_r"] = float(r[comp2]) if comp2 is not None else float(r.max())
    else:
        result["refit_component"], result["refit_pattern_r"] = comp, 1.0

    plot(pid, row.dataset, raw, clean, ica, comp, src, z, v, blinks, quiet, A0, A1)
    raw.close()
    return result, events, channel_rows


def plot(pid, dataset, raw, clean, ica, comp, src, z, v, blinks, quiet, A0, A1):
    show = ["FP1", "FP2", "FZ", "CZ", "PZ", "OZ"]
    idx = [names.index(c) for c in show]
    d0 = raw.get_data() - raw.get_data().mean(axis=0)
    d1 = clean.get_data() - clean.get_data().mean(axis=0)
    fig, ax = plt.subplots(3, 2, figsize=(15, 12))
    windows = []
    if len(blinks):
        centre = blinks[np.argmax([np.sum(np.abs(blinks - b) < 5*SF) for b in blinks])]
        windows.append((ax[0, 0], max(centre - 5*SF, 0), 10, "Blink interval"))
    q = np.flatnonzero(quiet[:-1] & quiet[1:])
    if len(q):
        windows.append((ax[0, 1], q[0]*EPOCH, 8, "Quiet interval (no frontal peak, passes screen)"))
    elif quiet.any():
        windows.append((ax[0, 1], np.flatnonzero(quiet)[0]*EPOCH, 4, "Quiet epoch (no frontal peak, passes screen)"))
    for a, start, seconds, title in windows:
        s = slice(start, min(start + seconds*SF, d0.shape[1]))
        t = np.arange(s.stop - s.start) / SF + start / SF
        for k, c in enumerate(idx):
            off = -k * 150
            a.plot(t, d0[c, s]*1e6 + off, color="0.6", lw=.7, label="before" if k == 0 else None)
            a.plot(t, d1[c, s]*1e6 + off, color="tab:blue", lw=.7, label="after" if k == 0 else None)
        a.plot(t, z[s] / max(np.abs(z[s]).max(), 1) * 60 + 150, color="tab:red", lw=.8, label=f"IC{comp} (scaled)")
        a.set_yticks([150] + [-k*150 for k in range(len(show))], [f"IC{comp}"] + show)
        a.set(xlabel="Seconds", title=f"{title}; 150 µV spacing, average reference")
        a.legend(fontsize=7, loc="upper right")
    lag = np.arange(-int(.6*SF), int(.6*SF) + 1)
    good = blinks[(blinks + lag[0] >= 0) & (blinks + lag[-1] < len(v))]
    if len(good):
        ax[1, 0].plot(lag / SF, np.mean([v[b + lag] for b in good], axis=0), label="mean(FP1,FP2) 1–10 Hz, µV")
        ax[1, 0].plot(lag / SF, np.mean([z[b + lag] for b in good], axis=0) * 10, label=f"IC{comp} robust z ×10")
        ax[1, 0].legend(fontsize=7)
    ax[1, 0].set(xlabel="Seconds from blink-like peak", title=f"Blink-locked average (n={len(good)})")
    if quiet.any():
        f, p0, _, _ = band_power(A0[quiet])
        _, p1, _, _ = band_power(A1[quiet])
        use = (f >= 1) & (f <= 40)
        for c, color in zip(["FP1", "FZ", "CZ", "OZ"], ["C0", "C1", "C2", "C3"]):
            ax[1, 1].semilogy(f[use], p0[names.index(c), use]*1e12, color=color, lw=1.4, alpha=.45)
            ax[1, 1].semilogy(f[use], p1[names.index(c), use]*1e12, color=color, lw=.9, ls="--", label=c)
        ax[1, 1].set(xlabel="Hz", ylabel="µV²/Hz", title="Quiet epochs: solid faint = before, dashed = after")
        ax[1, 1].legend(fontsize=7)
        _, _, b0, _ = band_power(A0[quiet])
        _, _, b1, _ = band_power(A1[quiet])
        x = np.arange(len(names))
        for i, b in enumerate(BANDS):
            ax[2, 0].bar(x + (i - 1.5) * .2, (b1[b] / b0[b] - 1) * 100, width=.2, label=b)
        ax[2, 0].axhline(-5, color="k", ls=":", lw=.8)
        ax[2, 0].axhline(5, color="k", ls=":", lw=.8)
        ax[2, 0].set_xticks(x, names, rotation=90, fontsize=6)
        ax[2, 0].set(ylabel="% change", title="Quiet epochs: band power change per channel")
        ax[2, 0].legend(fontsize=7, ncol=4)
    pattern = ica.get_components()[:, comp]
    ax[2, 1].bar(range(len(names)), pattern * np.sign(pattern[names.index("FP1")]),
                 color=["tab:red" if f else "0.6" for f in FRONTAL])
    ax[2, 1].set_xticks(range(len(names)), names, rotation=90, fontsize=6)
    ax[2, 1].set(title=f"IC{comp} sensor pattern (no electrode coordinates available)")
    fig.suptitle(f"{dataset} / {pid}: candidate ocular component IC{comp} — before vs after removal")
    fig.tight_layout()
    fig.savefig(out / f"quality_{pid}.png", dpi=110)
    plt.close(fig)


def criteria(r):
    if r["blink_like_events"] == 0:
        return pd.Series({"C1": None, "C2": None, "C3": None, "C4": None, "C5": None,
                          "supported": pd.isna(r["candidate_component"])})
    if pd.isna(r["candidate_component"]):
        return pd.Series({"C1": False, "C2": None, "C3": None, "C4": None, "C5": None, "supported": False})
    c = {"C1": r["blinks_with_component_peak"] >= .8,
         "C2": r["component_peaks_at_blinks"] >= .8,
         "C3": r.get("blink_frontal_pole_rms_change", np.nan) <= -.5,
         "C4": (all(r.get(f"quiet_posterior_{b}_max_abs_change", np.inf) <= .05 for b in BANDS)
                and all(abs(r.get(f"quiet_all_{b}_mean_change", np.inf)) <= .05 for b in ["alpha", "beta"])),
         "C5": r["refit_component"] is not None and r["refit_pattern_r"] >= .95}
    return pd.Series({**c, "supported": all(bool(x) for x in c.values())})


if __name__ == "__main__":
    targets = sys.argv[1:] or PILOT
    tag = "pilot" if not sys.argv[1:] else "validation"
    results, events, channels = [], [], []
    for pid in targets:
        r, e, c = evaluate(pid)
        results.append(r)
        events.append(e)
        channels += c
        print(pid, "component", r["candidate_component"], "blink-like", r["blink_like_events"], flush=True)
    summary = pd.DataFrame(results)
    summary = pd.concat([summary, summary.apply(criteria, axis=1)], axis=1)
    summary.to_csv(out / f"{tag}_summary.csv", index=False)
    pd.concat(events, ignore_index=True).to_csv(out / f"{tag}_frontal_events.csv", index=False)
    pd.DataFrame(channels).to_csv(out / f"{tag}_channel_changes.csv", index=False)
    print(summary.T.to_string())
