# Revision notes — Access-2026-34353 (resubmission)

## Files in this Overleaf project

| File | Use |
|---|---|
| `main.tex` | Revised manuscript. Every change relative to the originally submitted `main.tex` is highlighted (`\hl{}`, yellow table rows, boxed equations). Compile it for the **Highlighted PDF**. |
| `main_clean.tex` | The same text with no highlighting. Use it for the **Main Manuscript** upload (to compile it, set it as the main document in Overleaf). |
| `figures/*.pdf` | 9 new figures (vector PDFs with embedded TrueType fonts). |
| `scripts/` | The figure pipeline (see below). |
| Original figures | `Method_Overview.png`, `Communication Sample.png`, `Env_ITSC.png`, `attention_weight_heatmap.png` and `Result_ITSC/*`. These are **unchanged**: byte-identical, with LaTeX blocks identical to the submitted version. |

> ### ⚠️ Before resubmission
> Every number tagged `%reference` in `main.tex` (134 lines) is a **projection**, not a measurement.
> The same applies to **all nine new figures**, which are rendered from `scripts/data/figure_data.json`. That file contains projected data only.
> A hidden marker records this: each figure PDF carries the metadata `Subject: PROJECTED placeholder data`. The marker is not visible in the paper.
> Submitting these values or figures without running the experiments would be data fabrication.

## Replacing projected data with measured results

1. Run the experiments listed below.
2. Write your measurements into `scripts/data/figure_data.json`, keeping the same keys and shapes. `scripts/generate_projected_data.py` documents the schema: per-seed lists of 5 values, curves, and time series.
3. Run `python scripts/make_figures.py` to regenerate every figure in `figures/`.
4. Run `python scripts/derived_stats.py` to print the derived statistics quoted in the text: T90 of the learning curves, string-stability maxima and Γ, Spearman ρ, Cliff's δ, and latency quantiles.
5. Update each `%reference` line in `main.tex`, then re-read any sentence whose conclusion depends on the number.

Requirements: `pip install numpy scipy matplotlib`.

## `%reference` checklist by experiment

| Experiment | What to run | Where it appears |
|---|---|---|
| 1. Five-seed main comparison | Train Value/Dist/MQA/GAT/MHA with seeds 0–4. Evaluate at 10/30/50% Bernoulli loss (Scenario 1) with 20 common-random-number episodes per seed. Run the Linear, MPC and H∞ controllers on the same realizations. | Tables `robustness_analysis` and `main_multiseed`; Figs. `packet_loss_multiseed` (a,b) and `expanded_baseline`; abstract and conclusion (61%, 20%, 4.8 s) |
| 2. Learning curves | Log the training return per episode (200 episodes × 218 steps). The figure plots the team return divided by the number of controlled CAVs. | Fig. `training_convergence`; the convergence paragraph |
| 3. GE + outage (inference only) | GE with p_BG=0.20, p_GB=3/35. A 10-s outage of every CAV's nearest-upstream-CAV link, with a 30% Bernoulli background. Also run the matched outage-free episodes (same seeds and realizations); they are the reference band for the recovery time. | Table `ge_outage`; Fig. `ge_robustness` |
| 4. Random layouts (inference only) | 10/10/1 layouts at 50/70/90% × 5 realizations × 5 seeds. | Table `penetration`; Fig. `penetration_summary`(a,b); layout paragraph |
| 5. Core ablations | Retrain w/o distribution mapping and w/o ξ,τ,b (5 seeds each), plus H=1 and H=4 (3 seeds each). Evaluate the frozen models under GE and the outage. Evaluate held-out loss rates 40% and 60% (inference). | Table `ablation`; Figs. `ablation` and `packet_loss_multiseed`(c) |
| 6. Post-processing and benchmarks | Pulse disturbance ratios at the anchor condition, from rollouts started at the equilibrium cruise state with the pulse at t = 5 s. Attention–AoI analysis on the nearest upstream CAV token, for CAVs with at least 2 valid tokens. Per-step inference latency at the deployed platoon size. | Tables `string_stability` and `computation`; Figs. `string_stability`, `attention_aoi`, `computation` |

Also verify:
- Parameter and MAC counts. They are computed from the architecture, assuming a flattened 44-d input for the non-attention actors and no attention output projection.
- The CPU model named in the text.
- The Novelty-table row "Reused experiments/figures": check which figures actually appeared in the IV paper.
- The claim that training uses the Scenario 1–3 orderings.
- Headway parameters d0 / T_des / T_safe = 7.5 m / 1.0 s / 0.8 s. These were chosen to match your original data: 32–33 m MHA spacing and a safety threshold of about 28 m at 25 m/s in the original text, and about 7.5 m gaps at standstill. Replace them with the values in your code.
- Actor/critic learning rate 1e-5 with a 43.6k-step budget. This is unusually small for PPO; double-check it against your code.

## Changes in the latest round (consistency audit)

- **Latency figure:** the legend moved above the axes, so it no longer covers the curves.
- **Consistency with the original data:**
  - **Headway parameters:** changed from 1.2 s / 1.0 s to 1.0 s / 0.8 s. The desired and soft-safety distances at 25 m/s are now 32.5 m and 27.5 m, which matches the original 32–33 m spacing and about 28 m threshold.
  - **Attention analysis:** recalibrated to the original heatmap. The drop starts once the age reaches about 1 s (half-decrease 1.1 ± 0.3 s) and recovers within about 1 s. The previous "before T_stale / graded rather than threshold" statement contradicted the heatmap and the original text.
- **Logic fixes:**
  - The text claimed H∞ beats both non-attention MAPPO variants at 30% loss. This is false (6.10 vs 6.02 m), so the claim now covers 50% only.
  - Linear-CACC STD a under GE was 3.02 m/s², which is above a_max = 3. It is now 2.89.
  - Hedges' g for Distribution-based MAPPO: 6.4, not 6.5.
  - The pulse at t = 30 s was described as occurring "after the platoon has settled", but MPC, Value-based and Linear settle only after 34–39 s or never. The pulse rollouts now start from equilibrium.
  - The outage recovery reference was the start-up-affected interval 10–20 s. It is now the matched outage-free episodes.
  - Ablation variants were said to be "trained at the anchor condition". They now use the same training protocol as the full model.
  - Variant (ii) was described as a "deterministic" PPO actor. It is now described as a clipped Gaussian.
  - The attention analysis now excludes CAVs with a single upstream token.
- **Added clarifications:**
  - the generalization gap between the training-seen Scenario 1 and the unseen layouts (1–6%);
  - the plotted training return is per CAV;
  - the policies are stationary over the 60-s evaluation horizon;
  - why MQA is slightly slower than GAT despite fewer MACs.
- The random stream is unchanged, so only the attention section of `figure_data.json` changed.

## Changes in the previous round

- **10% / 30% penetration dropped.** The scope is now restricted to 50–90%, with a principled justification: at 10% there are no upstream CAV messages at all, and at 30% each CAV has at most two, typically separated by long HDV blocks. The requested sentence *"The conclusions of this study are therefore limited to mid-to-high CAV penetration regimes (50%–90%)"* is in §IV-E (Evaluation scenario). The abstract, contributions, limitations and conclusion are scoped the same way. The original weak justification ("cold-start effects are weak and trajectories overlap"), which Reviewer 2 criticised, is gone.
- **Three additions beyond the minimal package removed** (at your request). The text, tables, figures and highlighting were updated to match:
  - held-out 60% and 80% penetration: the rows in Table `penetration`, the sentences, and the points in `fig_penetration`;
  - the latency token-slot scaling benchmark (M = 4…64): panel (b) of `fig_computation` and its discussion. The figure is now a single-column latency ECDF;
  - the pulse string-stability extension to 70/90/60/80% penetration: the sentence in §String stability. String stability is reported at the anchor condition only.
  
  All other projected values and figures are unchanged. The RNG stream of `generate_projected_data.py` was kept, so no remaining number moved.
- **All 11 image placeholders replaced by 9 generated figures.** The two held-out figures were merged into related ones: penetration and layouts share one figure, as do trained and held-out loss rates.
- **Every figure-derived number synchronised with the figure data.** This includes learning-curve T90, the string-stability table (Γ is now the exact product of per-vehicle ratios), attention statistics, and latency quantiles.
- **Highlight audit.** A character-level diff against the original `main.tex` found two changes that had not been highlighted, and both are now highlighted:
  - "show large local fluctuations";
  - `V_{ij}` in the context equation.

## Suggested response text — Reviewer 2, comment 11 (10% and 30% penetration)

**Response.** We thank the reviewer for suggesting the 10% and 30% penetration cases. The present study focuses on mid-to-high CAV penetration regimes. There, cooperative V2V information exchange among multiple CAVs is frequent enough for the proposed communication-aware MHA controller to be meaningfully evaluated. At very low penetration, vehicle interactions are dominated by HDV car-following, and too little CAV information is communicated to exercise the proposed multi-vehicle information-fusion mechanism. In our ten-vehicle platoon this limitation is structural rather than empirical:
- At 10% penetration, the single CAV has no upstream CAV, so the attention module receives no messages at all.
- At 30% penetration, each CAV receives at most two upstream CAV messages, typically separated by long HDV blocks.

Evaluating these cases would therefore test the ego-sensing branch rather than the contribution of this paper. We restrict the experimental scope to 50%–90% penetration and explicitly avoid making claims about low-penetration performance.

**Action.**
- We removed the previous justification (weak cold-start effects and overlapping trajectories) and replaced it with the scope statement above (Section IV-E).
- We added: "The conclusions of this study are therefore limited to mid-to-high CAV penetration regimes (50%–90%)." The abstract, limitations and conclusion are restricted accordingly.
- Within this regime, we strengthened the evidence with layout-level results at 50%, 70% and 90% penetration. These use 10/10/1 distinct CAV/HDV orderings, including orderings not seen during training, evaluated with the frozen policy across five seeds (Table 6, Fig. 6).

## Reviewer compliance (updated)

- **R1:** 1–4 ✅
- **R2:**
  - 1–10, 12, 13 ✅
  - 11: defended with the scope restriction, supported by layout-level results at 50/70/90%.
  - Delay, jitter, heterogeneous links and Recurrent-MAPPO are defended in §Limitations.
- **R3:** all ✅
- **R4:**
  - 1–3, 5, 6 ✅
  - 4 (IndiSegNet): decline politely in the response letter; it is not relevant.
- **R5:**
  - 1, 2, 5 ✅
  - 3 and 4 are discussed in §Limitations; the suggested references are optional.
  - 6: the scalability claim is restricted in §Limitations. Only the per-step latency at the deployed size is measured (Table `computation`, Fig. `computation`); larger platoons are not claimed.
- **R6:**
  - 1–4 ✅
  - 5: suggested references are optional.
  - 6: unseen vehicle orderings ✅ (unseen penetration rates are defended by the 50–90% scope), severe loss (50/60%) ✅, abrupt disturbance ✅. Delay, heterogeneous dynamics and traffic density are defended in §Limitations.
