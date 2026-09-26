"""
Render the revision figures from scripts/data/figure_data.json into figures/*.pdf.

The JSON currently holds PROJECTED placeholder data (see generate_projected_data.py).
Replace it with measured results using the same schema and rerun:
    python scripts/make_figures.py
"""
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import NullFormatter  # noqa: E402
from scipy import stats  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)
D = json.load(open(os.path.join(HERE, "data", "figure_data.json")))

# ---------------------------------------------------------------- style ----
INK, INK2, AXIS, GRID = "#1a1a19", "#52514e", "#8a8984", "#e6e5e1"
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Liberation Serif", "Times New Roman", "Nimbus Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "text.color": INK, "axes.labelcolor": INK, "axes.edgecolor": AXIS,
    "xtick.color": INK2, "ytick.color": INK2,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "grid.linestyle": "-",
    "axes.axisbelow": True, "legend.frameon": False,
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})
W2, W1 = 7.0, 3.45  # double / single column width (in)
T975 = 2.776       # t_{0.975,4}

NAME = {"LIN": "Linear-CACC", "MPC": "MPC-CACC", "HINF": r"$H_\infty$ CACC", "VAL": "Value-based MAPPO",
        "DIST": "Distribution-based MAPPO", "GAT": "GAT-MAPPO", "MQA": "MQA+Distribution",
        "MHA": "MHA+Distribution"}
SHORT = {"LIN": "Linear", "MPC": "MPC", "HINF": r"$H_\infty$", "VAL": "Value", "DIST": "Distribution",
         "GAT": "GAT", "MQA": "MQA", "MHA": "MHA (ours)"}
# fixed identity colours: the four hues pass the all-pairs CVD check; the rest are
# neutral greys separated by marker and line style (secondary encoding)
COL = {"MHA": "#2a78d6", "GAT": "#eb6834", "MQA": "#1baf7a", "DIST": "#4a3aa7",
       "VAL": "#8a8984", "HINF": "#262624", "MPC": "#5c5b57", "LIN": "#b3b2ac"}
MK = {"MHA": "o", "GAT": "D", "MQA": "^", "DIST": "s", "VAL": "v", "HINF": "P", "MPC": "X", "LIN": "<"}
LS = {"MHA": "-", "GAT": "-", "MQA": "-", "DIST": "-", "VAL": (0, (4, 2)), "HINF": "-",
      "MPC": (0, (1, 1.4)), "LIN": (0, (4, 1.5, 1, 1.5))}
ORDER = ["LIN", "MPC", "HINF", "VAL", "DIST", "MQA", "GAT", "MHA"]
META = {"Subject": "PROJECTED placeholder data - replace with measured results before submission",
        "Keywords": "projected-placeholder"}


def ci(x):
    """mean and half-width of the two-sided 95% t-interval (n = number of seeds)."""
    x = np.asarray(x, float)
    return x.mean(), stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))


def panel(ax, label):
    ax.text(-0.02, 1.04, label, transform=ax.transAxes, fontsize=8, fontweight="bold",
            ha="right", va="bottom")


def lw(c):
    return 1.6 if c == "MHA" else 1.0


def save(fig, name):
    fig.savefig(os.path.join(FIG, name + ".pdf"), metadata=META)
    fig.savefig(os.path.join(FIG, name + ".png"), dpi=200)
    plt.close(fig)


def handles(keys, marker=True):
    return [Line2D([], [], color=COL[k], lw=lw(k), ls=LS[k], marker=MK[k] if marker else None,
                   ms=4, mfc=COL[k], mec="white", mew=0.5, label=NAME[k]) for k in keys]


# ----------------------------------------------------- F1 convergence ------
def fig_convergence():
    st = np.array(D["convergence"]["steps_k"])
    fig, ax = plt.subplots(figsize=(W1, 2.3))
    for c in ["VAL", "DIST", "MQA", "GAT", "MHA"]:
        cur = np.array(D["convergence"]["curves"][c])
        sm = np.array([np.convolve(y, np.ones(5) / 5, mode="valid") for y in cur])
        x = st[2:-2]
        m, h = sm.mean(0), T975 * sm.std(0, ddof=1) / np.sqrt(sm.shape[0])
        ax.fill_between(x, m - h, m + h, color=COL[c], alpha=0.16, lw=0)
        ax.plot(x, m, color=COL[c], lw=lw(c), ls=LS[c], label=NAME[c], zorder=3 if c == "MHA" else 2)
    ax.set_xlabel(r"Environment steps ($\times10^3$)")
    ax.set_ylabel(r"Episode return per CAV ($\times10^3$)")
    ax.set_xlim(0, st[-1])
    ax.legend(handles=handles(["MHA", "GAT", "MQA", "DIST", "VAL"], marker=False), loc="lower right",
              handlelength=2.2)
    save(fig, "fig_training_convergence")


# ------------------------------------------- F2 expanded baseline (seeds) --
def fig_expanded():
    A = D["anchor"]
    metrics = [("rmse_d", "Spacing RMSE (m), lower is better"), ("t90", r"$T_{90}$ (s), lower is better"),
               ("min_ttc", "Minimum TTC (s), higher is better")]
    fig, axes = plt.subplots(1, 3, figsize=(W2, 2.35), sharey=True)
    rng = np.random.default_rng(1)
    for j, (ax, (m, title)) in enumerate(zip(axes, metrics)):
        for i, c in enumerate(ORDER):
            v = np.array(A[m][c]); mu, h = ci(v)
            model = c in ("LIN", "MPC", "HINF")
            ax.scatter(v, i + rng.uniform(-0.16, 0.16, v.size), s=9, color=COL[c], alpha=0.55, lw=0,
                       zorder=2)
            ax.plot([mu - h, mu + h], [i, i], color=COL[c], lw=1.6 if c == "MHA" else 1.1,
                    solid_capstyle="round", zorder=3)
            ax.scatter([mu], [i], s=22 if c == "MHA" else 16, marker=MK[c],
                       facecolor="white" if model else COL[c], edgecolor=COL[c], lw=0.9, zorder=4)
        ax.axhline(2.5, color=AXIS, lw=0.5)
        ax.set_title(title, loc="left")
        ax.grid(axis="y", visible=False)
        panel(ax, "(%s)" % "abc"[j])
    axes[0].set_yticks(range(len(ORDER)))
    axes[0].set_yticklabels([NAME[c] for c in ORDER])
    axes[0].set_ylim(-0.6, len(ORDER) - 0.4)
    x0 = axes[0].get_xlim()[0]
    axes[0].text(x0 + 0.1, 2.38, "model-based", ha="left", va="top", fontsize=6.5, color=INK2)
    axes[0].text(x0 + 0.1, 2.62, "learning-based", ha="left", va="bottom", fontsize=6.5, color=INK2)
    save(fig, "fig_expanded_baseline")


# ---------------------------------------------------- F3 penetration -------
def fig_penetration():
    P = D["penetration"]
    pens = [50, 70, 90]
    held = set()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(W2, 2.4), gridspec_kw={"width_ratios": [1, 1.1]})
    for p in held:
        ax.axvspan(p - 3.5, p + 3.5, color="#f1f0ec", lw=0, zorder=0)
        ax.text(p, 7.1, "held-out", ha="center", va="bottom", fontsize=6.5, color=INK2)
    for c in ["HINF", "DIST", "GAT", "MHA"]:
        mus = np.array([ci(P["seed"][str(p)][c])[0] for p in pens])
        hs = np.array([ci(P["seed"][str(p)][c])[1] for p in pens])
        ax.plot(pens, mus, color=COL[c], lw=lw(c), ls=LS[c], zorder=2)
        for p, mu, h in zip(pens, mus, hs):
            ax.errorbar(p, mu, yerr=h, color=COL[c], lw=0.9, capsize=0, zorder=3)
            ax.scatter(p, mu, marker=MK[c], s=22 if c == "MHA" else 16, zorder=4,
                       facecolor="white" if p in held else COL[c], edgecolor=COL[c], lw=0.9)
        ax.text(92.0, mus[-1], SHORT[c], va="center", fontsize=7, color=INK)
    ax.set_xticks(pens)
    ax.set_xticklabels([f"{p}%" for p in pens])
    ax.set_xlim(44, 99)
    ax.set_ylim(0, 7.6)
    ax.set_xlabel("CAV penetration")
    ax.set_ylabel("Spacing RMSE (m)")
    panel(ax, "(a)")
    rng = np.random.default_rng(3)
    off = {"DIST": -0.26, "GAT": 0.0, "MHA": 0.26}
    for k, p in enumerate(pens):
        for c, o in off.items():
            v = np.array(P["layout"][str(p)][c])
            x = k + o
            if v.size > 1:
                bp = bx.boxplot(v, positions=[x], widths=0.2, showfliers=False, patch_artist=True,
                                medianprops=dict(color=COL[c], lw=1.1),
                                boxprops=dict(facecolor="white", edgecolor=COL[c], lw=0.7),
                                whiskerprops=dict(color=COL[c], lw=0.7), capprops=dict(color=COL[c], lw=0.7))
            bx.scatter(x + rng.uniform(-0.06, 0.06, v.size), v, s=6, color=COL[c], alpha=0.75, lw=0, zorder=3)
        if p in held:
            bx.axvspan(k - 0.45, k + 0.45, color="#f1f0ec", lw=0, zorder=0)
    bx.set_xticks(range(len(pens)))
    nlay = [len(P["layout"][str(p)]["MHA"]) for p in pens]
    bx.set_xticklabels([f"{p}%\n({n} layout{'s' if n > 1 else ''})" for p, n in zip(pens, nlay)])
    bx.set_xlim(-0.55, len(pens) - 0.45)
    bx.set_ylabel("Layout-level spacing RMSE (m)")
    bx.legend(handles=[Line2D([], [], color=COL[c], marker="s", ls="", ms=4, label=NAME[c])
                       for c in ["DIST", "GAT", "MHA"]], loc="upper right", ncol=1, handletextpad=0.2)
    bx.set_ylim(0, 9.2)
    panel(bx, "(b)")
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig_penetration")


# --------------------------------------------------- F4 packet loss --------
def fig_packet_loss():
    L = D["loss"]
    fig, axes = plt.subplots(1, 3, figsize=(W2, 2.45))
    trained = [10, 30, 50]
    for ax, m, ylab, lab in [(axes[0], "rmse_d", "Spacing RMSE (m)", "(a)"),
                             (axes[1], "std_a", r"Acceleration STD (m/s$^2$)", "(b)")]:
        for c in ORDER:
            mus = [ci(L[str(l)][c][m])[0] for l in trained]
            hs = [ci(L[str(l)][c][m])[1] for l in trained]
            ax.errorbar(trained, mus, yerr=hs, color=COL[c], lw=lw(c), ls=LS[c], marker=MK[c], ms=3.6,
                        mfc=COL[c], mec="white", mew=0.4, capsize=0, elinewidth=0.8,
                        zorder=4 if c == "MHA" else 3)
        ax.set_xticks(trained)
        ax.set_xticklabels([f"{l}%" for l in trained])
        ax.set_xlabel("Bernoulli packet-loss rate")
        ax.set_ylabel(ylab)
        panel(ax, lab)
    ax = axes[2]
    allr = [10, 30, 40, 50, 60]
    ax.axvspan(9, 51, color="#f1f0ec", lw=0, zorder=0)
    ax.text(30, 11.2, "training range", ha="center", fontsize=6.5, color=INK2)
    for c in ["HINF", "DIST", "GAT", "MHA"]:
        mus = np.array([ci(L[str(l)][c]["rmse_d"])[0] for l in allr])
        hs = np.array([ci(L[str(l)][c]["rmse_d"])[1] for l in allr])
        ax.plot(allr, mus, color=COL[c], lw=lw(c), ls=LS[c], zorder=2)
        for l, mu, h in zip(allr, mus, hs):
            ax.errorbar(l, mu, yerr=h, color=COL[c], lw=0.8, capsize=0, zorder=3)
            ax.scatter(l, mu, marker=MK[c], s=18, zorder=4, lw=0.8, edgecolor=COL[c],
                       facecolor="white" if l in (40, 60) else COL[c])
        ax.text(61.8, mus[-1], SHORT[c], va="center", fontsize=7)
    ax.set_xticks(allr)
    ax.set_xticklabels([f"{l}%" for l in allr])
    ax.set_xlim(6, 68)
    ax.set_ylim(0, 12)
    ax.set_xlabel("Packet-loss rate (open: held-out)")
    ax.set_ylabel("Spacing RMSE (m)")
    panel(ax, "(c)")
    fig.legend(handles=handles(list(reversed(ORDER))), loc="upper center", ncol=8, bbox_to_anchor=(0.5, 1.07),
               handlelength=1.8, columnspacing=0.9, handletextpad=0.4)
    fig.tight_layout(w_pad=1.2)
    save(fig, "fig_packet_loss")


# ---------------------------------------------------- F5 GE / outage -------
def fig_ge():
    G = D["ge"]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(W2, 2.45), gridspec_kw={"width_ratios": [1, 1.2]})
    for i, c in enumerate(ORDER):
        b, g = np.mean(G["bern30"][c]), np.mean(G["ge30"][c])
        ax.plot([b, g], [i, i], color=COL[c], lw=1.1, zorder=2)
        ax.scatter(b, i, s=18, marker=MK[c], facecolor="white", edgecolor=COL[c], lw=0.9, zorder=3)
        ax.scatter(g, i, s=18, marker=MK[c], facecolor=COL[c], edgecolor=COL[c], lw=0.9, zorder=3)
        ax.text(17.9, i, f"+{100 * (g / b - 1):.1f}%", va="center", ha="right", fontsize=6.8, color=INK2)
    ax.set_yticks(range(len(ORDER)))
    ax.set_yticklabels([NAME[c] for c in ORDER])
    ax.set_xlim(0, 18)
    ax.set_xticks([0, 2.5, 5, 7.5, 10, 12.5, 15])
    ax.set_ylim(-0.6, len(ORDER) - 0.4)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Spacing RMSE (m) at 30% average loss")
    ax.legend(handles=[Line2D([], [], color=INK2, marker="o", mfc="white", ls="", ms=4, label="Bernoulli"),
                       Line2D([], [], color=INK2, marker="o", ls="", ms=4, label="Gilbert\u2013Elliott")],
              loc="upper center", bbox_to_anchor=(0.62, 1.0))
    panel(ax, "(a)")
    O = D["outage"]
    t = np.array(O["t"])
    bx.axvspan(20, 30, color="#f1f0ec", lw=0, zorder=0)
    bx.text(25, 0.25, "10-s outage", ha="center", fontsize=6.8, color=INK2)
    for c in ["DIST", "HINF", "GAT", "MHA"]:
        tr = np.array(O["trace"][c])
        m, h = tr.mean(0), T975 * tr.std(0, ddof=1) / np.sqrt(tr.shape[0])
        bx.fill_between(t, m - h, m + h, color=COL[c], alpha=0.16, lw=0)
        bx.plot(t, m, color=COL[c], lw=lw(c), ls=LS[c], label=NAME[c])
    bx.set_xlim(12, 45)
    bx.set_ylim(0, 14)
    bx.set_xlabel("Time (s)")
    bx.set_ylabel("Max. absolute spacing error (m)")
    bx.legend(loc="upper left")
    panel(bx, "(b)")
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig_ge_outage")


# ---------------------------------------------------- F6 attention ---------
def fig_attention():
    A = D["attention"]
    fig, axes = plt.subplots(1, 3, figsize=(W2, 2.3), gridspec_kw={"width_ratios": [1.15, 0.8, 1.2]})
    ax = axes[0]
    x = np.array(A["aoi_bins"])
    full, nof = np.array(A["binned"]["full"]), np.array(A["binned"]["nofresh"])
    for y in full:
        ax.plot(x, y, color=COL["MHA"], lw=0.6, alpha=0.45)
    ax.plot(x, full.mean(0), color=COL["MHA"], lw=1.6, label="with freshness inputs")
    ax.plot(x, nof.mean(0), color=COL["VAL"], lw=1.2, ls=(0, (4, 2)), label=r"w/o $\xi,\tau,b$")
    ax.axvline(1.0, color=INK2, lw=0.6, ls=(0, (2, 2)))
    ax.text(1.05, 0.76, r"$T_{\rm stale}$", fontsize=7, color=INK2)
    r = np.array(A["rho"]["full"]); r2 = np.array(A["rho"]["nofresh"])
    ax.text(2.95, 0.77, rf"$\rho={r.mean():.2f}\pm{r.std(ddof=1):.2f}$", ha="right", fontsize=7, color=COL["MHA"])
    ax.text(2.95, 0.69, rf"$\rho={r2.mean():.2f}\pm{r2.std(ddof=1):.2f}$", ha="right", fontsize=7, color=INK2)
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 0.82)
    ax.set_xlabel("Message age of information (s)")
    ax.set_ylabel("Attention on nearest upstream CAV")
    ax.legend(loc="lower left")
    panel(ax, "(a)")
    bx = axes[1]
    fr, stl = np.array(A["fresh"]), np.array(A["stale"])
    vp = bx.violinplot([fr, stl], positions=[0, 1], widths=0.7, showextrema=False)
    for body, col in zip(vp["bodies"], [COL["MHA"], COL["VAL"]]):
        body.set_facecolor(col); body.set_alpha(0.25); body.set_edgecolor(col); body.set_linewidth(0.6)
    for k, v in enumerate([fr, stl]):
        q1, med, q3 = np.percentile(v, [25, 50, 75])
        bx.plot([k, k], [q1, q3], color=INK, lw=2.2, solid_capstyle="butt")
        bx.scatter([k], [med], s=14, color="white", edgecolor=INK, lw=0.8, zorder=3)
        bx.text(k + 0.4, med, f"{med:.2f}", va="center", fontsize=6.8, color=INK2)
    bx.set_xticks([0, 1])
    bx.set_xticklabels([r"fresh ($\tau\leq1$ s)", r"stale ($\tau>1$ s)"])
    bx.set_ylim(0, 1.0)
    bx.set_ylabel("Attention on nearest upstream CAV")
    bx.grid(axis="x", visible=False)
    panel(bx, "(b)")
    cx = axes[2]
    te = np.array(A["event_t"]); ev = np.array(A["event"])
    cx.axvspan(0, 10, color="#f1f0ec", lw=0, zorder=0)
    main = np.delete(ev, 3, axis=0)
    m, h = ev.mean(0), T975 * ev.std(0, ddof=1) / np.sqrt(ev.shape[0])
    cx.fill_between(te, m - h, m + h, color=COL["MHA"], alpha=0.18, lw=0)
    cx.plot(te, m, color=COL["MHA"], lw=1.6, label="mean of 5 seeds")
    cx.plot(te, ev[3], color=COL["MHA"], lw=0.8, ls=(0, (3, 1.5)), label="weakest seed")
    cx.text(5, 0.78, "link outage", ha="center", fontsize=6.8, color=INK2)
    cx.set_xlim(te[0], te[-1])
    cx.set_ylim(0, 0.84)
    cx.set_xlabel("Time from outage onset (s)")
    cx.set_ylabel("Attention on interrupted link")
    cx.legend(loc="center", bbox_to_anchor=(0.5, 0.55))
    panel(cx, "(c)")
    del main
    fig.tight_layout(w_pad=1.2)
    save(fig, "fig_attention_aoi")


# ------------------------------------------------ F7 string stability ------
def fig_string():
    S = D["string_stability"]
    pos, cav = S["positions"], np.array(S["is_cav"]) == 1
    keys = ["LIN", "MPC", "HINF", "DIST", "GAT", "MHA"]
    fig, axes = plt.subplots(1, 2, figsize=(W2, 2.35), sharey=True)
    for ax, g, lab, ttl in [(axes[0], "G2", "(a)", r"$G_i^{(2)}$"), (axes[1], "Ginf", "(b)", r"$G_i^{(\infty)}$")]:
        for k in np.where(~cav)[0]:
            ax.axvspan(k - 0.5, k + 0.5, color="#f1f0ec", lw=0, zorder=0)
        ax.axhline(1.0, color=INK, lw=0.8, zorder=1)
        for j, c in enumerate(keys):
            arr = np.array(S[g][c])
            mu, h = arr.mean(0), T975 * arr.std(0, ddof=1) / np.sqrt(arr.shape[0])
            xs = np.arange(9) + (j - 2.5) * 0.07
            ax.plot(xs, mu, color=COL[c], lw=lw(c), ls=LS[c], zorder=3 if c == "MHA" else 2)
            ax.errorbar(xs, mu, yerr=h, fmt="none", ecolor=COL[c], elinewidth=0.7, zorder=2)
            ax.scatter(xs[cav], mu[cav], marker=MK[c], s=16 if c == "MHA" else 12, color=COL[c],
                       edgecolor="white", lw=0.4, zorder=4)
        ax.set_xticks(range(9))
        ax.set_xticklabels([r"$\mathtt{%s}$" % p for p in pos], rotation=40, ha="right")
        ax.set_xlim(-0.5, 8.5)
        ax.set_ylabel(ttl + " (ratio to predecessor)")
        ax.text(3.5 + 0.5, 1.53, "HDV block", ha="center", fontsize=6.8, color=INK2)
        panel(ax, lab)
    axes[0].set_ylim(0.78, 1.62)
    fig.legend(handles=handles(list(reversed(keys))), loc="upper center", ncol=6, bbox_to_anchor=(0.5, 1.07),
               columnspacing=1.0, handlelength=1.8)
    fig.tight_layout(w_pad=1.2)
    save(fig, "fig_string_stability")


# ---------------------------------------------------- F8 ablations ---------
def fig_ablation():
    A = D["ablation"]
    fig, axes = plt.subplots(1, 3, figsize=(W2, 2.35), gridspec_kw={"width_ratios": [1.05, 1, 1]})
    ax = axes[0]
    conds = [("rmse_b", "Bernoulli\nRMSE"), ("rmse_ge", "GE\nRMSE"), ("peak", "Outage\npeak")]
    rng = np.random.default_rng(5)
    for k, (m, lbl) in enumerate(conds):
        ref = np.mean(A["full"][m])
        for v, o, col, fc in [("full", -0.17, COL["MHA"], COL["MHA"]), ("no_fresh", 0.17, COL["VAL"], "white")]:
            vals = np.array(A[v][m]) / ref
            mu, h = ci(vals)
            ax.scatter(k + o + rng.uniform(-0.05, 0.05, vals.size), vals, s=7, color=col, alpha=0.6, lw=0)
            ax.errorbar(k + o, mu, yerr=h, color=col, lw=1.1, capsize=0, zorder=3)
            ax.scatter(k + o, mu, s=20, marker="o", facecolor=fc, edgecolor=col, lw=1.0, zorder=4)
        ax.text(k + 0.33, np.mean(A["no_fresh"][m]) / ref, f"+{100 * (np.mean(A['no_fresh'][m]) / ref - 1):.0f}%",
                ha="left", va="center", fontsize=6.8, color=INK2)
    ax.axhline(1.0, color=AXIS, lw=0.5)
    ax.set_xticks(range(3))
    ax.set_xticklabels([c[1] for c in conds])
    ax.set_ylabel("Relative to full model")
    ax.set_ylim(0.6, 2.9)
    ax.set_xlim(-0.5, 2.85)
    ax.grid(axis="x", visible=False)
    ax.legend(handles=[Line2D([], [], color=COL["MHA"], marker="o", ls="", ms=4, label="full model"),
                       Line2D([], [], color=COL["VAL"], marker="o", mfc="white", ls="", ms=4,
                              label=r"w/o freshness ($\xi,\tau,b$)")], loc="upper left")
    panel(ax, "(a)")
    variants = [("no_mha", "w/o MHA", COL["DIST"]), ("mqa", "MQA (matched)", COL["MQA"]),
                ("no_dist", "w/o distribution map.", COL["VAL"]), ("no_fresh", "w/o freshness", COL["VAL"]),
                ("h1", r"$H=1$", COL["MHA"]), ("h4", r"$H=4$", COL["MHA"]), ("full", r"Full ($H=8$)", COL["MHA"])]
    for ax, m, xl, lab in [(axes[1], "rmse_b", "Spacing RMSE (m)", "(b)"),
                           (axes[2], "std_a", r"Acceleration STD (m/s$^2$)", "(c)")]:
        for i, (v, name, col) in enumerate(variants):
            vals = np.array(A[v][m]); mu, h = ci(vals)
            hollow = v in ("h1", "h4")
            ax.scatter(vals, i + rng.uniform(-0.13, 0.13, vals.size), s=7, color=col, alpha=0.55, lw=0)
            ax.plot([mu - h, mu + h], [i, i], color=col, lw=1.1)
            ax.scatter(mu, i, s=20, facecolor="white" if hollow else col, edgecolor=col, lw=1.0, zorder=4)
        ax.set_yticks(range(len(variants)))
        ax.set_yticklabels([n for _, n, _ in variants] if m == "rmse_b" else [])
        ax.set_ylim(-0.6, len(variants) - 0.4)
        ax.grid(axis="y", visible=False)
        ax.set_xlabel(xl)
        panel(ax, lab)
    axes[1].text(0.98, 0.97, "hollow: 3 seeds", transform=axes[1].transAxes, ha="right", va="top",
                 fontsize=6.5, color=INK2)
    fig.tight_layout(w_pad=1.0)
    save(fig, "fig_ablation")


# --------------------------------------------------- F9 computation --------
def fig_computation():
    Lt = D["latency"]
    fig, ax = plt.subplots(figsize=(W1, 2.55))
    for c in ["VAL", "DIST", "GAT", "MQA", "MHA"]:
        v = np.sort(np.array(Lt["samples_ms"][c]))
        y = np.arange(1, v.size + 1) / v.size
        ax.plot(v, y, color=COL[c], lw=lw(c), ls=LS[c], label=NAME[c])
        p99 = np.percentile(v, 99)
        ax.scatter([p99], [0.99], s=12, marker=MK[c], color=COL[c], edgecolor="white", lw=0.4, zorder=3)
    ax.set_xscale("log")
    ax.set_xlim(0.028, 0.5)
    ax.set_xticks([0.03, 0.05, 0.1, 0.2, 0.4])
    ax.set_xticklabels(["0.03", "0.05", "0.1", "0.2", "0.4"])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel(r"Actor latency per decision (ms, batch 1, $M=8$)")
    ax.set_ylabel("Empirical CDF")
    ax.set_ylim(0, 1.02)
    # legend above the axes so that no curve is covered
    ax.legend(handles=handles(["MHA", "MQA", "GAT", "DIST", "VAL"]), loc="lower left",
              bbox_to_anchor=(-0.02, 1.01), ncol=2, handlelength=2.0, columnspacing=1.0,
              handletextpad=0.4, borderaxespad=0.0)
    save(fig, "fig_computation")


if __name__ == "__main__":
    fig_convergence()
    fig_expanded()
    fig_penetration()
    fig_packet_loss()
    fig_ge()
    fig_attention()
    fig_string()
    fig_ablation()
    fig_computation()
    print("figures written to", FIG)
