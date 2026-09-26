"""Print the statistics quoted in main.tex that are derived from figure_data.json."""
import json, os
import numpy as np
from scipy import stats
d = json.load(open(os.path.join(os.path.dirname(__file__), "data", "figure_data.json")))
st = np.array(d["convergence"]["steps_k"])
print("== convergence (t90 = first time the 5-episode mean reaches 90% of the return improvement)")
for c, cur in d["convergence"]["curves"].items():
    t90s, fin, inc = [], [], []
    for y in cur:
        y = np.array(y); ys = np.convolve(y, np.ones(5) / 5, mode="valid"); ss = st[2:-2]
        r0 = ys[:3].mean(); rf = y[-5:].mean(); fin.append(rf)
        t90s.append(ss[np.argmax(ys >= r0 + 0.9 * (rf - r0))])
        i90 = np.searchsorted(st, 0.9 * st[-1]); inc.append((rf - y[i90 - 2:i90 + 3].mean()) / (rf - r0) * 100)
    fin = np.array(fin)
    print(f"{c}: t90 {np.mean(t90s):.1f}+-{np.std(t90s, ddof=1):.1f}k  final {fin.mean():.2f}+-{fin.std(ddof=1):.2f}  CV {100*fin.std(ddof=1)/abs(fin.mean()):.1f}%  share of total gain in last 10% of budget {np.mean(inc):.1f}%")
print("== string stability (Scenario 1, bounded pulse)")
ss = d["string_stability"]; cav = np.array(ss["is_cav"]) == 1
for c in ss["G2"]:
    g2 = np.array(ss["G2"][c]); gi = np.array(ss["Ginf"][c])
    mx2, mxi, gam = g2[:, cav].max(1), gi[:, cav].max(1), g2.prod(1)
    print(f"{c}: maxG2 {mx2.mean():.2f}+-{mx2.std(ddof=1):.2f}  maxGinf {mxi.mean():.2f}+-{mxi.std(ddof=1):.2f}  "
          f"pairs<=1 {(g2[:, cav] <= 1).sum()}/25  Gamma {gam.mean():.2f}+-{gam.std(ddof=1):.2f}  "
          f"argmax(Ginf) pos {np.bincount(gi[:, cav].argmax(1), minlength=5)}  HDV {g2[:, ~cav].mean(0).min():.2f}-{g2[:, ~cav].mean(0).max():.2f}")
a = d["attention"]
for k in ("full", "nofresh"):
    r = np.array(a["rho"][k]); print(f"rho {k}: {r.mean():.2f}+-{r.std(ddof=1):.2f} range {r.min():.2f}..{r.max():.2f}")
f, s = np.array(a["fresh"]), np.array(a["stale"])
print("fresh med %.2f IQR %.2f-%.2f | stale med %.2f IQR %.2f-%.2f" % (np.median(f), *np.percentile(f, [25, 75]), np.median(s), *np.percentile(s, [25, 75])))
print("Cliff delta %.2f" % ((f[:, None] > s[None, :]).mean() - (f[:, None] < s[None, :]).mean()))
te = np.array(a["event_t"]); ev = np.array(a["event"])
pre = ev[:, te < 0].mean(1); at3 = ev[:, np.argmin(abs(te - 3))]
print("event pre %.2f+-%.2f  at+3s %.2f+-%.2f" % (pre.mean(), pre.std(ddof=1), at3.mean(), at3.std(ddof=1)))
low = ev[:, (te > 8) & (te < 10)].mean(1); half = []
rec = []
for k in range(ev.shape[0]):
    thr = pre[k] - 0.5 * (pre[k] - low[k]); idx = np.where((te >= 0) & (ev[k] <= thr))[0]; half.append(te[idx[0]])
    idx2 = np.where((te >= 10) & (ev[k] >= 0.9 * pre[k]))[0]; rec.append(te[idx2[0]] - 10)
print("half-decrease %.1f+-%.1f s ; recovery to within 10%% %.1f+-%.1f s" % (np.mean(half), np.std(half, ddof=1), np.mean(rec), np.std(rec, ddof=1)))
print("== latency quantiles (ms)")
for c, v in d["latency"]["samples_ms"].items():
    print(c, "%.3f %.3f %.3f" % tuple(np.percentile(v, [50, 95, 99])))
print("== outage (from traces)")
t = np.array(d["outage"]["t"])
for c, tr in d["outage"]["trace"].items():
    tr = np.array(tr); pk = tr.max(1)
    print(c, "peak %.2f+-%.2f" % (pk.mean(), pk.std(ddof=1)), "table peak", np.mean(d["outage"]["peak"][c]).round(2), "rec", np.mean(d["outage"]["recovery"][c]).round(2))
