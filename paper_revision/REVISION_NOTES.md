# Revision notes: Access-2026-34353

Files in this folder:

- `manuscript.tex`: the revised manuscript. Every change is marked with `\hl{}`, `\rowcolor{yellow}` or `\eqrevbox`, so it can be used to build the **Highlighted PDF**.
- `manuscript_clean.tex`: the same text with all highlighting removed, for the **Main Manuscript** upload.
- The git history keeps the pre-revision manuscript as its own commit, so `git diff HEAD~1 -- manuscript.tex` shows every edit.

> **Before you resubmit:** every value tagged `%reference` is a *projected* value. It was chosen to be internally consistent and plausible, but it is **not a measurement**. Replace each one with your actual experimental output, then re-read the sentence around it, because several discussion paragraphs draw conclusions from these numbers (for example, "not significant at 10%" or "GAT is the closest competitor"). If a real result differs, rewrite the conclusion to match it. Submitting any `%reference` value without measuring it would be data fabrication.
>
> Find them all with `grep -n "%reference" manuscript.tex` (124 lines).

---

## 1. Placeholder checklist, grouped by the 7-group minimal experiment package

| Group | What to run | Cost | Manuscript locations to overwrite |
|---|---|---|---|
| **1. Five-seed main results** | Retrain Value-MAPPO, Dist-MAPPO, MQA+Dist and MHA+Dist with seeds 0–4. Evaluate at 10/30/50% Bernoulli loss (50% CAV, Scenario 1) with 20 CRN episodes per seed. Run the model-based controllers (Linear, MPC, H∞) on the same 5×20 realizations. | Training | Table `robustness_analysis` (all 120 cells); Table `main_multiseed` (first-10-s speed, T90, Ts, min TTC, collisions, p_Holm, Hedges' g); the convergence paragraph after Fig. `training_convergence` (steps to 90% of final return, CV, Value-MAPPO slope); the packet-loss discussion (13.4, 15.46, 14.9, 17.8, 21.1, 1.24, 2.93, 14.12, 0.66, 2.03, ~42%, CI [3.77, 6.15]); the abstract and conclusion (61%, 20%, 4.8 s) |
| **2. GAT + loss-aware robust controller** | GAT-MAPPO (GATv2, 8 heads × 64, ≈154k params), 5 seeds. H∞ CACC per YANG2025103212, with the loss uncertainty bounded at 50%. | Training (GAT only) | GAT and H∞ columns in all tables; the GAT parameter count (154.0k) in Baselines; the H∞ design bound sentence |
| **3. GE (one matched PLR) + outage** | Inference only. GE with p_BG=0.20, p_GB=3/35 at the anchor. 10-s outage of each CAV's nearest-upstream-CAV link over t∈[20,30] s, with a 30% Bernoulli background. | Inference | Table `ge_outage`; the GE paragraph (realized loss 29.7%, link-episode std 4.6%/1.9%, burst 5.0); the discussion (p=0.015, g=1.8). *The 3.2% / 1.8×10⁻⁶ staleness probabilities are analytic, derived from the channel parameters, and stay valid.* |
| **4. 10/30% frozen-policy eval** | Inference only, with the frozen checkpoint. | Inference | Table `penetration` (10% and 30% rows), p=0.84, the "5/9" and "9/10" layout counts |
| **5. Random layouts (inference only)** | 9/10/10/10/1 layouts × 5 realizations × 5 seeds. | Inference | Table `penetration` (all rows); the layout paragraph (1.98–3.21 m, 5.12–7.34 m, 10/10, 8/10) |
| **6. Core ablation at the anchor** | New training: (ii) MHA without the distribution mapping (5 seeds); (iii) MHA without ξ,τ,b (5 seeds); H=1 and H=4 (3 seeds each). Then run each frozen model under GE and the outage. Unseen loss (40% and 60%) is inference only. | Training | Table `ablation`; the ablation paragraph (p=0.43, p=0.009, g=2.0); the unseen-loss paragraph (2.68, 3.98, 4.92, 10.12, 7.21, +29/30/26/7%) |
| **7. String stability + attention/AoI + latency** | Post-processing of frozen rollouts and a benchmark. | None | Table `string_stability`; the pulse paragraph (0.98–1.01 for the stop event); the stability discussion (HDV 1.06–1.14; 0.93/0.91/1.02 across penetration); the attention paragraph (ρ, medians/IQR, Cliff's δ, onset/recovery times, ρ without freshness); Table `computation` (latency, CPU model); the end-to-end time of 0.22 ms |

Other items to verify:

- **Parameter and MAC counts** (Table `computation`, 156.6k/151.2k/154.0k/9.4k/9.2k). These were *computed* from the architecture in Table `training_hyperparameters`, under three assumptions: the non-attention actors take the flattened ego + 8×5 padded tokens (44 inputs); there is no attention output projection; and LayerNorm is applied over the 512-d context. If your code differs, recount (for example, `sum(p.numel() for p in actor.parameters())`).
- **Novelty table**, row "Reused experiments/figures": confirm which figures actually appeared in the IV paper.
- **Training layouts**: the text now says the policy was trained on the Scenario 1–3 orderings. Confirm this.
- **Trajectory grids (speed/gap/braking figures)**: if these were produced by the preliminary model *without* the ξ/τ/b token features, regenerate them from seed 0 of the revised model. This is inference only. Otherwise the figures and the tables describe different networks.
- **Table `robustness_analysis` note**: this table is now five-seed mean±std. The single-run values from the preliminary protocol were removed, as Reviewer 2 item 9 asked.

---

## 2. Reviewer compliance audit

Legend: ✅ addressed in the manuscript · 🛡️ defended as a limitation (the manuscript explains why it was not done) · ✉️ response letter only

### Reviewer 1
| # | Comment | Status | Where |
|---|---|---|---|
| 1 | Training/implementation details | ✅ | Table `training_hyperparameters` (+ seeds, evaluation episodes), §Training details |
| 2 | MDP/POMDP and MHA's role | ✅ | Dec-POMDP/CTDE formulation; explicit statement that MHA does not restore the Markov property |
| 3 | Moderate "guaranteed"/"absolute collision avoidance" | ✅ | A grep finds no "absolute", and every "guarantee" is negated. Collisions are reported as 0/100 in Table `main_multiseed` |
| 4 | Staleness threshold, action-mapping factor, safety parameters | ✅ | T_stale = 1.0 s; the notation table now links mapping_factor = a_max = 3.0 m/s²; d0, T_des and T_safe are given |

### Reviewer 2
| # | Comment | Status | Where |
|---|---|---|---|
| 1 | Novelty vs. [17], dedicated table | ✅ | Table `iv_access_novelty`, with **new rows**: Architectural elements, Reused experiments/figures, Conclusions not obtainable from [17] |
| 2 | POMDP / belief-state claim | ✅ | Explicit Dec-POMDP; the claim is withdrawn |
| 3 | Separate state definitions | ✅ | S^t, c^t, o_i^t, m̂, m̃, ξ, τ, b, M_ij |
| 4 | Reward sign and coefficients | ✅ | Negative signs; w1=10, w2=20 |
| 5 | How MHA sees staleness | ✅ | The token z_ij includes ξ, τ, b; masking; T_stale |
| 6 | Multi-seed Fig. 6 analysis | ✅ | §Attention–freshness, now with quantitative results (ρ, medians, Cliff's δ, event-aligned timing) and a freshness-ablation cross-check |
| 7 | Proper string-stability metric | ✅ | L2/L∞ ratios, head-to-tail Γ, **new Table `string_stability`**, and a bounded-pulse protocol |
| 8 | Remove safety guarantees | ✅ | As for R1.3 |
| 9 | Multiple seeds: count, seeds, mean±std/CI, significance, curves; Table 2 single values | ✅ | 5 seeds {0–4}; **Table 2 converted to mean±std**; Welch + Holm + Hedges' g (the manuscript explains why Wilcoxon is invalid with n=5); convergence figure and numbers |
| 10 | Randomized configurations | ✅ | 9/10/10/10/1 layouts (90% has only one feasible layout, which is explained) |
| 11 | Report 10% and 30% | ✅ | Table `penetration`; at 10% the manuscript honestly reports no advantage |
| 12 | Realistic comm failures | ✅/🛡️ | GE, AoI and outage are done. Delay, jitter, heterogeneous links and distance-dependent delivery are defended in §Limitations, and claims are restricted |
| 12b | Robust controller; recurrent MAPPO; GAT | ✅/🛡️ | H∞ and GAT are added. Recurrent MAPPO is defended in §Limitations (the explicit AoI features supply its memory; adding it would confound the training pipeline) |
| 13 | Full ablation list | ✅ | Every item is covered, and Top-K is explained as not applicable (there is no Top-K module) |
| Q3 | Fixed compositions, 60-s horizon, single Krauss | ✅/🛡️ | Randomized layouts; the Krauss σ and 60-s horizon are acknowledged in §Limitations |
| Q4/5 | Ref [31] on 10% loss being "representative" | ✅ | The claim is removed: 10% is described as a "controlled baseline" with no citation. **Check that [31] is no longer cited for this** |

### Reviewer 3
| Comment | Status | Where |
|---|---|---|
| Bernoulli limitation | ✅ | Communication model + GE + analytic staleness comparison |
| Simplified scenario, generalizability | ✅ | §Scope and limitations |
| "across different range of CAV penetration rates" | ✅ | The phrase no longer exists |
| Dash punctuation | ✅ | `---` used |
| "The HDVs were modeled" | ✅ | Fixed |

### Reviewer 4
| # | Comment | Status | Where |
|---|---|---|---|
| 1 | How training ensures cold-start mitigation | ✅ | No auxiliary loss; the initial condition appears in every rollout; T90 and settling time are measured (and the gain is shown to be shared by all attention encoders) |
| 2 | Bursty losses | ✅ | GE + outage |
| 3 | Quantitative overhead vs. MAPPO | ✅ | **New Table `computation`** |
| 4 | IndiSegNet citation | ✉️ | It is not relevant (semantic segmentation), so decline politely. IEEE says authors are not obligated to cite suggested references |
| 5 | Reward weights: how chosen | ✅/🛡️ | Empirical design weights and their rationale; the full sweep is defended in §Limitations |
| 6 | MPC tuning; robust/adaptive MPC | ✅ | Tuning grid on a validation set; the robust comparator is H∞, and robust/adaptive MPC not being implemented is stated |

### Reviewer 5
| # | Comment | Status | Where |
|---|---|---|---|
| 1 | GAT comparison | ✅ | GAT-MAPPO, capacity-matched |
| 2 | i.i.d. Bernoulli is strong | ✅ | GE + outage |
| 3 | Security discussion (+ refs) | ✅/✉️ | §Limitations covers the threat model. The suggested game-theory PHY-security refs are optional; cite them only if you judge them relevant |
| 4 | Digital twin future work (+ refs) | ✅/✉️ | §Limitations and the conclusion; the refs are optional |
| 5 | Computational overhead and latency | ✅ | Table `computation` |
| 6 | Platoon-size scalability | 🛡️ | §Limitations restricts the scalability claim |

### Reviewer 6
| # | Comment | Status | Where |
|---|---|---|---|
| 1 | Novelty vs. attention MARL | ✅ | The SOTA paragraph, plus capacity-matched GAT/MQA comparisons |
| 2 | Packet-loss model justification | ✅ | Bernoulli is a controlled baseline; GE is correlated; distance dependence is excluded explicitly |
| 3 | Reproducibility | ✅ | Hyperparameters, seeds, convergence and cost |
| 4 | Baseline fairness | ✅ | Table `baseline_fairness` (+ a new Model-capacity row) |
| 5 | Consensus/formation refs | ✉️ | Optional; the topic is only tangential |
| 6 | Unseen penetration, severe loss, delay, heterogeneous dynamics, density, abrupt disturbance | ✅/🛡️ | Unseen penetration, 50–60% loss, braking and pulse are done. Delay, heterogeneity and density are defended in §Limitations |

**Residual risk:** Reviewer 2 and Reviewer 6 may still ask for delay/jitter and recurrent MAPPO. The manuscript now gives an explicit rationale for each. In the response letter, point to §Limitations and to the explicit-AoI argument instead of only saying "future work".
