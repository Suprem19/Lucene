"""
PROJECTED placeholder data for the revision figures.

Every number produced here is a PROJECTION chosen to be internally consistent
with the %reference-tagged values in main.tex. None of it is a measurement.
Replace data/figure_data.json with measured results (same schema) and rerun
make_figures.py before submission.

Usage:  python scripts/generate_projected_data.py   -> scripts/data/figure_data.json
"""
import json
import math
import os

import numpy as np

RNG = np.random.default_rng(20260926)
N_SEEDS = 5
OUT = os.path.join(os.path.dirname(__file__), "data", "figure_data.json")


def exact(mean, std, n=N_SEEDS):
    """n values whose sample mean and sample std equal (mean, std) exactly."""
    z = RNG.standard_normal(n)
    z = (z - z.mean()) / z.std(ddof=1)
    return (mean + std * z).round(4).tolist()


CTRL = ["LIN", "MPC", "HINF", "VAL", "DIST", "GAT", "MQA", "MHA"]

# --------------------------------------------------------------------------
# 1) Bernoulli packet-loss robustness (Table robustness_analysis), 50% CAV
# --------------------------------------------------------------------------
LOSS_TABLE = {  # loss -> ctrl -> {metric: (mean, std)}
    10: {"LIN": {"rmse_d": (7.93, .39), "std_a": (2.36, .05)},
         "MPC": {"rmse_d": (6.61, .33), "std_a": (1.57, .04)},
         "HINF": {"rmse_d": (5.62, .30), "std_a": (0.81, .06)},
         "VAL": {"rmse_d": (5.37, .71), "std_a": (1.15, .11)},
         "DIST": {"rmse_d": (4.71, .55), "std_a": (0.44, .06)},
         "GAT": {"rmse_d": (2.39, .31), "std_a": (0.33, .04)},
         "MQA": {"rmse_d": (3.28, .42), "std_a": (0.37, .05)},
         "MHA": {"rmse_d": (1.96, .27), "std_a": (0.30, .04)}},
    30: {"LIN": {"rmse_d": (10.62, .48), "std_a": (2.78, .06)},
         "MPC": {"rmse_d": (8.95, .41), "std_a": (1.96, .05)},
         "HINF": {"rmse_d": (6.10, .35), "std_a": (0.92, .08)},
         "VAL": {"rmse_d": (6.95, .84), "std_a": (1.47, .13)},
         "DIST": {"rmse_d": (6.02, .66), "std_a": (0.78, .09)},
         "GAT": {"rmse_d": (2.91, .36), "std_a": (0.47, .06)},
         "MQA": {"rmse_d": (4.28, .52), "std_a": (0.58, .07)},
         "MHA": {"rmse_d": (2.34, .31), "std_a": (0.43, .05)}},
    50: {"LIN": {"rmse_d": (15.46, .62), "std_a": (2.93, .04)},
         "MPC": {"rmse_d": (12.71, .55), "std_a": (2.63, .05)},
         "HINF": {"rmse_d": (6.74, .40), "std_a": (1.03, .08)},
         "VAL": {"rmse_d": (9.38, 1.07), "std_a": (1.94, .17)},
         "DIST": {"rmse_d": (8.04, .97), "std_a": (1.14, .13)},
         "GAT": {"rmse_d": (3.79, .49), "std_a": (0.73, .08)},
         "MQA": {"rmse_d": (5.58, .66), "std_a": (0.88, .10)},
         "MHA": {"rmse_d": (3.08, .42), "std_a": (0.66, .08)}},
}
# Held-out loss rates (frozen policies, no retuning)
HELDOUT_LOSS = {
    40: {"HINF": (6.41, .37), "DIST": (6.97, .78), "GAT": (3.34, .42), "MHA": (2.68, .35)},
    60: {"HINF": (7.21, .44), "DIST": (10.12, 1.26), "GAT": (4.92, .66), "MHA": (3.98, .58)},
}

loss = {str(L): {c: {m: exact(*v) for m, v in d.items()} for c, d in tab.items()}
        for L, tab in LOSS_TABLE.items()}
for L, tab in HELDOUT_LOSS.items():
    loss[str(L)] = {c: {"rmse_d": exact(*v)} for c, v in tab.items()}

# --------------------------------------------------------------------------
# 2) Anchor-condition startup / safety (Table main_multiseed)
# --------------------------------------------------------------------------
ANCHOR = {
    "t90": {"LIN": (26.3, .9), "MPC": (23.1, .7), "HINF": (17.9, .5), "VAL": (21.3, 2.9),
            "DIST": (14.6, 1.5), "GAT": (10.7, .8), "MQA": (11.2, .9), "MHA": (9.8, .6)},
    "min_ttc": {"LIN": (3.4, .4), "MPC": (4.6, .3), "HINF": (7.9, .5), "VAL": (4.1, .7),
                "DIST": (5.2, .6), "GAT": (5.8, .5), "MQA": (5.6, .6), "MHA": (6.1, .5)},
}
anchor = {m: {c: exact(*v) for c, v in d.items()} for m, d in ANCHOR.items()}
anchor["rmse_d"] = {c: loss["30"][c]["rmse_d"] for c in CTRL}

# --------------------------------------------------------------------------
# 3) Training convergence (per-seed return curves)
# --------------------------------------------------------------------------
T_EP, STEPS_PER_EP = 200, 218
steps = np.arange(1, T_EP + 1) * STEPS_PER_EP / 1000.0  # k steps
CONV = {  # final return (x1e3), its std, time constant (k steps) and its spread
    "MHA": (-5.2, .21, 12.6, 1.2), "GAT": (-5.9, .27, 13.4, 1.4), "MQA": (-7.4, .39, 15.2, 1.8),
    "DIST": (-9.8, .64, 17.3, 2.2), "VAL": (-11.6, 1.13, 20.5, 2.9)}
conv = {"steps_k": steps.round(3).tolist(), "curves": {}}
for c, (rf, rs, tau, taus) in CONV.items():
    finals = exact(rf, rs)
    curves = []
    for rf_s in finals:
        r0 = -30.0 + RNG.normal(0, .6)
        tau_s = max(3.0, RNG.normal(tau, taus))
        k = 1.35  # slightly sigmoidal learning curve
        base = r0 + (rf_s - r0) * (1 - np.exp(-(steps / tau_s) ** k))
        # rescale so that the last-5-episode mean equals the seed's final return
        base = r0 + (base - r0) * (rf_s - r0) / (base[-5:].mean() - r0)
        noise = RNG.normal(0, 0.55, T_EP)
        noise = np.convolve(noise, np.ones(3) / 3, mode="same")
        curves.append((base + noise * np.linspace(1.0, 0.35, T_EP)).round(3).tolist())
    conv["curves"][c] = curves

# --------------------------------------------------------------------------
# 4) Penetration (layout-averaged) and layout-level values, 30% Bernoulli
# --------------------------------------------------------------------------
PEN = {  # penetration -> ctrl -> (mean, std) over seeds; 60 and 80 are held out
    50: {"HINF": (6.08, .13), "DIST": (6.09, .64), "GAT": (3.02, .38), "MHA": (2.47, .32)},
    60: {"HINF": (5.99, .13), "DIST": (5.93, .62), "GAT": (2.86, .37), "MHA": (2.35, .31)},
    70: {"HINF": (5.91, .12), "DIST": (5.62, .58), "GAT": (2.56, .33), "MHA": (2.08, .27)},
    80: {"HINF": (5.84, .12), "DIST": (5.47, .60), "GAT": (2.49, .34), "MHA": (2.03, .29)},
    90: {"HINF": (5.77, .11), "DIST": (5.18, .55), "GAT": (2.27, .30), "MHA": (1.83, .24)},
}
N_LAYOUT = {50: 10, 60: 10, 70: 10, 80: 9, 90: 1}
pen = {"seed": {str(p): {c: exact(*v) for c, v in d.items()} for p, d in PEN.items()},
       "layout": {}}
# layout effects: right-skewed (long HDV blocks upstream of a CAV are the hard cases)
E50_MHA = np.array([-0.49, -0.38, -0.27, -0.18, -0.10, -0.02, 0.07, 0.20, 0.43, 0.74])
E50_DIST = np.array([-0.97, -0.74, -0.52, -0.33, -0.18, -0.03, 0.14, 0.40, 0.98, 1.25])
for p, nl in N_LAYOUT.items():
    if nl == 1:
        eff = np.zeros(1)
        effd = np.zeros(1)
    elif p == 50:
        eff, effd = E50_MHA, E50_DIST
    else:
        g = RNG.gamma(2.0, 1.0, nl)
        g = np.sort((g - g.mean()) / g.std())
        eff = g * E50_MHA.std() * PEN[p]["MHA"][0] / PEN[50]["MHA"][0]
        effd = g * E50_DIST.std() * PEN[p]["DIST"][0] / PEN[50]["DIST"][0]
    # GAT shares the layout ordering with 1.2x the MHA layout effect
    pen["layout"][str(p)] = {
        "MHA": (PEN[p]["MHA"][0] + eff).round(3).tolist(),
        "GAT": (PEN[p]["GAT"][0] + 1.2 * eff).round(3).tolist(),
        "DIST": (PEN[p]["DIST"][0] + effd).round(3).tolist(),
    }

# --------------------------------------------------------------------------
# 5) GE vs Bernoulli (Table ge_outage) and outage time series
# --------------------------------------------------------------------------
GE = {"LIN": (13.35, .71), "MPC": (11.02, .58), "HINF": (6.64, .39), "VAL": (8.73, 1.12),
      "DIST": (7.41, .92), "GAT": (3.71, .47), "MQA": (5.12, .64), "MHA": (2.87, .38)}
ge = {"bern30": {c: loss["30"][c]["rmse_d"] for c in CTRL},
      "ge30": {c: exact(*v) for c, v in GE.items()}}

OUT_PEAK = {"HINF": (7.4, .5), "DIST": (11.8, 1.9), "GAT": (6.3, .9), "MHA": (4.6, .7)}
OUT_REC = {"HINF": (4.9, .4), "DIST": (7.2, 1.3), "GAT": (3.9, .7), "MHA": (2.9, .5)}
OUT_BASE = {"HINF": 1.55, "DIST": 2.30, "GAT": 1.05, "MHA": 0.85}  # pre-outage mean |e_d|
t = np.round(np.arange(10.0, 45.0 + 1e-9, 0.1), 2)
outage = {"t": t.tolist(), "trace": {}, "peak": {}, "recovery": {}}
for c in OUT_PEAK:
    peaks, recs = exact(*OUT_PEAK[c]), exact(*OUT_REC[c])
    outage["peak"][c], outage["recovery"][c] = peaks, recs
    traces = []
    for P, R in zip(peaks, recs):
        b = OUT_BASE[c] * (1 + RNG.normal(0, .06))
        band = b * 1.45
        tp = 30.0 + 0.6  # peak shortly after restoration (information arrives with delay)
        tau_d = (30.0 + R - tp) / math.log((P - b) / (band - b))
        rise = b + (P - b) * np.clip((t - 20.0) / (tp - 20.0), 0, 1) ** 1.6
        decay = b + (P - b) * np.exp(-(t - tp) / tau_d)
        y = np.where(t < 20.0, b, np.where(t <= tp, rise, decay))
        y = y + RNG.normal(0, 0.04 * b, t.size) * (t < 20.0)
        traces.append(np.round(y, 3).tolist())
    outage["trace"][c] = traces

# --------------------------------------------------------------------------
# 6) Attention - AoI analysis
# --------------------------------------------------------------------------
aoi_bins = np.round(np.arange(0.0, 3.01, 0.2), 2)
att = {"aoi_bins": aoi_bins.tolist(), "binned": {"full": [], "nofresh": []},
       "rho": {"full": [], "nofresh": []}}
from scipy.stats import spearmanr  # noqa: E402

for name, (a0, a_inf, lam, noise, n_tok) in {
        "full": (0.52, 0.14, 1.05, 0.078, 600),
        "nofresh": (0.44, 0.33, 0.9, 0.12, 600)}.items():
    for s in range(N_SEEDS):
        a0s = a0 + RNG.normal(0, .02)
        lams = lam * (1 + RNG.normal(0, .12))
        if name == "full" and s == 3:  # the weaker seed noted in the text
            a0s, a_inf_s = 0.46, 0.25
        else:
            a_inf_s = a_inf + RNG.normal(0, .015)
        curve = a_inf_s + (a0s - a_inf_s) * np.exp(-lams * aoi_bins)
        att["binned"][name].append(np.round(curve, 4).tolist())
        # token-level samples for the per-seed Spearman correlation
        tau_s = RNG.exponential(0.7, n_tok)
        tau_s = np.clip(tau_s, 0, 3.0)
        a_tok = a_inf_s + (a0s - a_inf_s) * np.exp(-lams * tau_s) + RNG.normal(0, noise, n_tok)
        att["rho"][name].append(round(float(spearmanr(tau_s, a_tok)[0]), 3))
# fresh vs stale distributions (nearest upstream CAV token)
fresh = np.clip(RNG.normal(0.47, 0.118, 4000), 0.02, 0.98)
stale = np.clip(RNG.gamma(3.6, 0.053, 1500), 0.01, 0.9)
att["fresh"] = np.round(fresh, 4).tolist()
att["stale"] = np.round(stale, 4).tolist()
# event-aligned attention on the interrupted link (onset at 0 s, restoration at 10 s)
te = np.round(np.arange(-3.0, 14.01, 0.1), 2)
att["event_t"] = te.tolist()
att["event"] = []
for s in range(N_SEEDS):
    pre = 0.51 + RNG.normal(0, .05) if s != 3 else 0.46
    low = 0.22 + RNG.normal(0, .05) if s != 3 else 0.31
    k_on = math.log(2) / (0.9 + RNG.normal(0, .15))       # half-decrease ~0.9 s
    k_off = -math.log(0.1) / (0.6 + RNG.normal(0, .12))    # within 10% after ~0.6 s
    y = np.where(te < 0, pre,
                 np.where(te < 10, low + (pre - low) * np.exp(-k_on * te),
                          pre - (pre - (low + (pre - low) * math.exp(-k_on * 10))) * np.exp(-k_off * (te - 10))))
    y = y + RNG.normal(0, 0.008, te.size)
    att["event"].append(np.round(y, 4).tolist())

# --------------------------------------------------------------------------
# 7) String stability: per-seed, per-position L2 / Linf ratios (Scenario 1)
# --------------------------------------------------------------------------
POS = ["veh0", "vehx1", "veh1", "vehx2", "vehx3", "vehx4", "veh2", "veh3", "veh4"]
IS_CAV = [1, 0, 1, 0, 0, 0, 1, 1, 1]
# mean L2 ratio for the five controlled CAVs (veh0, veh1, veh2, veh3, veh4)
G2_CAV = {"LIN": [0.96, 1.02, 1.41, 1.00, 0.95], "MPC": [0.92, 0.98, 1.18, 0.96, 0.92],
          "HINF": [0.87, 0.89, 0.96, 0.89, 0.88], "VAL": [0.93, 0.99, 1.26, 0.97, 0.93],
          "DIST": [0.90, 0.95, 1.09, 0.93, 0.91], "GAT": [0.87, 0.90, 1.00, 0.89, 0.88],
          "MQA": [0.87, 0.90, 1.03, 0.91, 0.89], "MHA": [0.86, 0.88, 0.95, 0.88, 0.87]}
GINF_FACTOR = {c: 1.08 for c in ["LIN", "MPC", "VAL", "DIST", "GAT", "MQA", "MHA"]}
GINF_FACTOR["HINF"] = 1.06
G2_HDV = [1.07, 1.09, 1.12, 1.10]
SEED_SD = {"LIN": .05, "MPC": .04, "HINF": .015, "VAL": .07, "DIST": .045,
           "GAT": .03, "MQA": .035, "MHA": .02}
ss = {"positions": POS, "is_cav": IS_CAV, "G2": {}, "Ginf": {}}
for c in CTRL:
    g2s, gis = [], []
    for s in range(N_SEEDS):
        cav = np.array(G2_CAV[c]) + RNG.normal(0, SEED_SD[c], 5)
        hdv = np.array(G2_HDV) + RNG.normal(0, .015, 4)
        g2 = np.empty(9)
        g2[np.array(IS_CAV) == 1] = cav
        g2[np.array(IS_CAV) == 0] = hdv
        ginf = g2 * (GINF_FACTOR[c] + RNG.normal(0, .012, 9))
        ginf[6] += 0.02  # peak deviation largest behind the three-HDV block
        g2s.append(np.round(g2, 3).tolist())
        gis.append(np.round(ginf, 3).tolist())
    ss["G2"][c], ss["Ginf"][c] = g2s, gis

# --------------------------------------------------------------------------
# 8) Ablations at the anchor condition
# --------------------------------------------------------------------------
ABL = {  # variant -> (n_seeds, {metric: (mean, std)})
    "full": (5, {"rmse_b": (2.34, .31), "std_a": (0.43, .05), "rmse_ge": (2.87, .38), "peak": (4.6, .7)}),
    "no_mha": (5, {"rmse_b": (6.02, .66), "std_a": (0.78, .09), "rmse_ge": (7.41, .92), "peak": (11.8, 1.9)}),
    "no_dist": (5, {"rmse_b": (3.47, .58), "std_a": (0.96, .14), "rmse_ge": (4.18, .71), "peak": (6.9, 1.3)}),
    "no_fresh": (5, {"rmse_b": (2.51, .34), "std_a": (0.45, .05), "rmse_ge": (3.94, .55), "peak": (8.3, 1.5)}),
    "h1": (3, {"rmse_b": (2.86, .41), "std_a": (0.47, .06), "rmse_ge": (3.42, .49), "peak": (5.7, 1.0)}),
    "h4": (3, {"rmse_b": (2.43, .30), "std_a": (0.44, .05), "rmse_ge": (2.96, .36), "peak": (4.8, .8)}),
    "mqa": (5, {"rmse_b": (4.28, .52), "std_a": (0.58, .07), "rmse_ge": (5.12, .64), "peak": (7.6, 1.2)}),
}
abl = {}
for v, (n, d) in ABL.items():
    abl[v] = {}
    for m, (mu, sd) in d.items():
        if v == "full" and m == "rmse_b":
            abl[v][m] = loss["30"]["MHA"]["rmse_d"]
        elif v == "full" and m == "std_a":
            abl[v][m] = loss["30"]["MHA"]["std_a"]
        elif v == "full" and m == "rmse_ge":
            abl[v][m] = ge["ge30"]["MHA"]
        elif v == "full" and m == "peak":
            abl[v][m] = outage["peak"]["MHA"]
        elif v == "no_mha" and m in ("rmse_b", "std_a"):
            abl[v][m] = loss["30"]["DIST"]["rmse_d" if m == "rmse_b" else "std_a"]
        elif v == "mqa" and m in ("rmse_b", "std_a"):
            abl[v][m] = loss["30"]["MQA"]["rmse_d" if m == "rmse_b" else "std_a"]
        else:
            abl[v][m] = exact(mu, sd, n)

# --------------------------------------------------------------------------
# 9) Computation: latency samples at M=8 and scaling with token slots
# --------------------------------------------------------------------------
LAT = {"VAL": (0.036, 0.041, 0.058), "DIST": (0.038, 0.044, 0.061), "GAT": (0.142, 0.163, 0.214),
       "MQA": (0.151, 0.172, 0.226), "MHA": (0.168, 0.191, 0.247)}
lat = {"samples_ms": {}, "scaling": {}}
for c, (med, p95, p99) in LAT.items():
    # smooth right-skewed quantile function: log x = log med + b z + c z^4 (z >= 0), b z (z < 0)
    z95, z99 = 1.6449, 2.3263
    A = np.array([[z95, z95 ** 4], [z99, z99 ** 4]])
    bb, cc = np.linalg.solve(A, np.log([p95 / med, p99 / med]))
    z = np.clip(RNG.standard_normal(10000), -3.5, 3.6)
    logx = np.log(med) + bb * z + np.where(z > 0, cc * z ** 4, 0.0)
    lat["samples_ms"][c] = np.round(np.exp(logx), 5).tolist()
M = [4, 8, 16, 32, 64]
SCAL = {"DIST": [0.037, 0.038, 0.040, 0.043, 0.050], "GAT": [0.133, 0.142, 0.161, 0.198, 0.276],
        "MQA": [0.144, 0.151, 0.165, 0.193, 0.251], "MHA": [0.155, 0.168, 0.194, 0.247, 0.352]}
lat["scaling"] = {"M": M, "median_ms": SCAL,
                  "p95_ms": {c: [round(x * 1.14, 4) for x in v] for c, v in SCAL.items()},
                  "macs_k_MHA": [round((148624 + 6144 * m) / 1000, 1) for m in M]}

# The 60%/80% penetration entries and the token-slot scaling benchmark are generated
# only so that the random stream (and hence every other projected value) stays
# unchanged; they are not part of the manuscript and are dropped here.
for p in ("60", "80"):
    pen["seed"].pop(p)
    pen["layout"].pop(p)
lat.pop("scaling")

data = {"_note": "PROJECTED placeholder data - replace with measured results before submission",
        "loss": loss, "anchor": anchor, "convergence": conv, "penetration": pen,
        "ge": ge, "outage": outage, "attention": att, "string_stability": ss,
        "ablation": abl, "latency": lat}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(data, f)
print("wrote", OUT)
