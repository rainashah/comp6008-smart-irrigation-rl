# Fixed experiment settings

**Group-discussion configuration — updated 6 October 2026.**

This document is the shared implementation specification for the Kyabram smart-irrigation experiment. All three agents must use the same environment, data partitions, interaction budget and evaluation procedure. Scientific justification and references are provided in [`PROJECT_OBJECTIVES.md`](PROJECT_OBJECTIVES.md).

Any change to a setting below must be agreed by the group and recorded before final testing. The final test seasons must not be used to select settings, hyperparameters or checkpoints.

## 1. Study definition

| Setting | Fixed value |
|---|---|
| Problem | Continuous daily irrigation control in a simulated grain-maize field |
| Location | Kyabram, Victoria, Australia |
| SILO station | `080091` |
| Reference coordinate | 36.3350° S, 145.0638° E, WGS84 |
| Field interpretation | Virtual field at the reference point; not a verified commercial paddock |
| Climate record | 1 January 2005 to 31 December 2025 |
| Main algorithms | DDPG, TD3 and SAC |
| Practical benchmark | Fixed soil-water-threshold controller |
| Diagnostic policies | Zero irrigation and maximum irrigation |
| Time step | One day |
| Episode | One 150-day maize season |

## 2. Crop calendar

| Setting | Fixed value |
|---|---|
| Crop | Grain maize |
| Planting date | 1 November |
| Decisions per episode | 150 |
| Effective root-zone depth | 1.0 m |

### Crop-coefficient schedule

| Stage | Days after planting | Length | Single crop coefficient, $K_c$ |
|---|---:|---:|---|
| Initial | 0–29 | 30 days | 0.30 |
| Development | 30–69 | 40 days | $0.30+0.90(t-29)/40$ |
| Mid-season | 70–119 | 50 days | 1.20 |
| Late season | 120–149 | 30 days | $1.20-0.85(t-119)/30$, ending at 0.35 |

The terminal observation at $t=150$ uses a crop coefficient of zero and is not used for bootstrapping.

## 3. Soil-water reservoir

The simulator models plant-available water above an assumed lower extraction limit. It does not model absolute volumetric soil moisture.

| Depth | Mean available water capacity | Layer thickness | Available storage |
|---|---:|---:|---:|
| 0–5 cm | 12.5000% | 50 mm | 6.2500 mm |
| 5–15 cm | 13.0000% | 100 mm | 13.0000 mm |
| 15–30 cm | 12.1667% | 150 mm | 18.2500 mm |
| 30–60 cm | 11.5000% | 300 mm | 34.5000 mm |
| 60–100 cm | 9.8333% | 400 mm | 39.3333 mm |
| **Total** | — | **1,000 mm** | **111.3333 mm** |

| Setting | Fixed value |
|---|---:|
| Nominal capacity, $C$ | 111.3333 mm |
| Initial storage, $A_0$ | $0.8C=89.0667$ mm |

Use unrounded layer values in calculations. The same initial storage is used for all agents and benchmarks.

## 4. Agent observation

The actor and critic receive the same 18-element `float32` observation. The year identifier, season identifier, future rainfall and future evapotranspiration are hidden.

| Indices | Feature | Scaling | Declared range |
|---|---|---|---|
| 0 | Current available storage | $A_t/C$ | $[0,1]$ |
| 1 | Day within season | $t/150$ | $[0,1]$ |
| 2 | Current crop coefficient | $K_{c,t}/1.2$ | $[0,1.1]$ |
| 3 | Previous irrigation | $I_{t-1}/20$ | $[0,1]$ |
| 4–10 | Previous seven completed days of rainfall, newest first | Each value divided by 20 mm | $[0,\infty)$ each |
| 11–17 | Previous seven completed days of reference ETo, newest first | Each value divided by 10 mm | $[0,\infty)$ each |

```python
observation_space = gymnasium.spaces.Box(
    low=np.zeros(18, dtype=np.float32),
    high=np.array([1.0, 1.0, 1.1, 1.0] + [np.inf] * 14, dtype=np.float32),
    dtype=np.float32,
)
```

Requirements:

- all emitted observations must be finite;
- rainfall and ETo must be finite and non-negative;
- weather inputs are scaled but not clipped;
- the first observation uses the actual seven days before planting;
- previous irrigation is zero at reset; and
- `info` diagnostics are not provided to the actor or critic.

This is a partially observable problem. The seven-day history is an approximation to a sufficient state and does not prove that the observation is Markov.

## 5. Action and Gymnasium interface

| Setting | Fixed value |
|---|---|
| Policy action space | `Box(-1, 1, shape=(1,), dtype=float32)` |
| Physical irrigation | $I_t=10(u_t+1)$ mm |
| Physical action range | 0–20 mm/day |
| Nominal application efficiency | $\eta=0.85$ |

Out-of-range and non-finite actions are rejected. Each agent must bound its exploration action before calling `step()`.

The environment API is:

```python
observation, info = env.reset(seed=..., options=...)
next_observation, reward, terminated, truncated, info = env.step(action)
```

`terminated=True` follows the 150th daily transition. The baseline environment has no additional time limit, so `truncated=False`. An external training cut-off is not a terminal transition and must not remove bootstrapping from an otherwise non-terminal target.

## 6. Daily transition

The agent chooses irrigation before receiving that day's rainfall or ETo. The fixed within-day calculation is:

$$
ET_{c,t}=K_{c,t}ET_{o,t}
$$

$$
p_t=\operatorname{clip}\{0.55+0.04(5-ET_{c,t}),0.1,0.8\}
$$

$$
A_{\min,t}=(1-p_t)C
$$

$$
B_t=A_t+P_t+0.85I_t
$$

$$
D_t=\max(0,B_t-C),\qquad H_t=B_t-D_t
$$

$$
K_{s,t}=\min(1,H_t/A_{\min,t})
$$

$$
ET_{a,t}=\min(H_t,K_{s,t}ET_{c,t})
$$

$$
A_{t+1}=H_t-ET_{a,t}
$$

The following daily mass-balance identity must hold within numerical tolerance:

$$
A_{t+1}=A_t+P_t+\eta I_t-D_t-ET_{a,t}.
$$

Fixed simplifying assumptions:

- rainfall enters the reservoir directly;
- surface runoff is zero;
- capillary rise is zero;
- storage above capacity becomes immediate drainage;
- storm timing and infiltration limits are not resolved; and
- waterlogging damage and crop yield are outside the baseline model.

## 7. Reward and objective

The acceptable end-of-day range is:

$$
A_{\min,t}\leq A_{t+1}\leq C.
$$

The shared environmental reward is:

$$
R_{t+1}=-\left[
\frac{I_t}{20}
+10\max\left(0,\frac{A_{\min,t}-A_{t+1}}{A_{\min,t}}\right)
+\frac{D_t}{20}
\right].
$$

| Component | Weight and normalisation |
|---|---|
| Irrigation use | $I_t/20$ |
| Soil-water shortage | $10\max(0,(A_{\min,t}-A_{t+1})/A_{\min,t})$ |
| Drainage | $D_t/20$ |
| Discount factor | $\gamma=0.995$ |

SAC's entropy bonus is excluded from the shared environmental return used to compare agents.

## 8. Season partitions

A season is labelled by its planting year.

| Purpose | Planting years | Seasons |
|---|---|---:|
| Training | 2005–2016 | 12 |
| Validation | 2017–2020 | 4 |
| Final test | 2021–2024 | 4 |

The last test season ends in March 2025. November 2025 is excluded because the downloaded climate record does not contain its complete 150-day season.

Rules:

- complete seasons remain intact;
- training samples seasons uniformly;
- all agents use the same season schedule for a given seed;
- environment, network and exploration random-number generators remain separate; and
- test seasons are not used for tuning, checkpoint selection or reward changes.

## 9. Shared training settings

| Setting | Fixed value |
|---|---|
| Final seeds | 11, 22, 33, 44 and 55 |
| Final budget | 100,000 environment interactions per seed and agent |
| Tuning allowance | Four configurations × seeds 101 and 202 × 30,000 interactions per agent |
| Evaluation schedule | Step 0 and every 5,000 training interactions |
| Final checkpoint | Step 100,000 |
| Replay capacity | 100,000 transitions |
| Minibatch size | 128 |
| Initial random exploration | 1,500 actions, included in the interaction budget |
| Network size | Two hidden layers of 128 ReLU units for each actor, critic and value network |
| Optimiser | Adam, betas $(0.9,0.999)$, epsilon $10^{-8}$ |
| Soft-update coefficient | $\tau=0.005$ |
| Update rate | One critic/value update set per environment step after warm-up |

No agent receives additional training interactions because it appears promising. Failed and numerically invalid runs remain in the experiment record.

## 10. Algorithm-specific settings and tuning grids

### DDPG

| Setting | Values |
|---|---|
| Learning rate | $10^{-4}$ or $3\times10^{-4}$ |
| Gaussian exploration standard deviation | 0.1 or 0.2 in the normalised action space |
| Evaluation action | Actor output without exploration noise |

The four tuning configurations are the two learning rates crossed with the two exploration standard deviations.

### TD3

| Setting | Values |
|---|---|
| Learning rate | $10^{-4}$ or $3\times10^{-4}$ |
| Gaussian exploration standard deviation | 0.1 or 0.2 |
| Policy delay | 2 |
| Target smoothing standard deviation | 0.2 |
| Target-noise clipping | ±0.5 |
| Evaluation action | Actor output without exploration noise |

The four tuning configurations are the two learning rates crossed with the two exploration standard deviations. Target noise is applied before the target action is bounded.

### SAC

Use the 2018 SAC formulation with a separate state-value network and fixed entropy coefficient.

| Setting | Values |
|---|---|
| Learning rate | $10^{-4}$ or $3\times10^{-4}$ |
| Fixed entropy coefficient, $\alpha$ | 0.1 or 0.2 |
| Policy | Tanh-squashed Gaussian with log-probability correction |
| Entropy coordinates | Normalised action space |
| Evaluation action | Tanh of the Gaussian mean |

The four tuning configurations are the two learning rates crossed with the two values of $\alpha$.

## 11. Hyperparameter selection

Select each agent's configuration using the highest mean discounted environmental validation return at 30,000 interactions, averaged across both tuning seeds and all four validation seasons.

Tie-breaking order:

1. higher mean validation return;
2. lower mean validation irrigation for an exact return tie; and
3. predeclared configuration order for a remaining exact tie.

A configuration with a numerically failed tuning run receives a selection score of negative infinity. If every configuration fails for one agent, repair and version the implementation before restarting that agent's comparable experiment.

## 12. Benchmarks

The main threshold benchmark uses current storage only:

$$
I_t=
\begin{cases}
\min\left[20,\dfrac{0.90C-A_t}{0.85}\right], & A_t<0.65C,\\
0, & A_t\geq0.65C.
\end{cases}
$$

It uses the same action limit, nominal efficiency, initial storage and seasons as the RL agents. Also evaluate zero-irrigation and maximum-irrigation policies as diagnostic bounds.

## 13. Evaluation measures

For every agent, seed, season and benchmark, record:

- discounted environmental return;
- undiscounted environmental return;
- total irrigation in mm/season;
- days below the target range;
- cumulative end-of-day shortage in mm-days;
- actual-to-potential ET ratio;
- excess watering and drainage;
- training interactions and learning curve;
- wall-clock training and evaluation time; and
- numerical failures or incomplete runs.

Report each final seed's mean across the four test seasons, the mean and sample standard deviation across five seeds, every seed-level result, and results separated by season. Days and seed–season combinations are not treated as independent experimental replicates.

## 14. Learning-curve rules

Call performance operationally stable when the range across the last five validation checkpoints is at most:

$$
0.05\max(1,|\bar G|),
$$

where $\bar G$ is the mean return across those checkpoints. This is a declared plateau criterion, not a convergence proof.

Sample efficiency is the first evaluation checkpoint that matches or exceeds the threshold benchmark's mean validation return and remains at or above it for the following two checkpoints. Otherwise report **not reached**.

## 15. Predeclared sensitivity and robustness scenarios

The nominal settings above remain the main experiment. After the main configuration is frozen, evaluate the trained policies without retraining under the following one-at-a-time changes:

| Scenario group | Values |
|---|---|
| Soil capacity | $0.8C$ and $1.2C$ |
| Effective root-zone depth | 0.6 m, using the first four layers and capacity 72.0 mm |
| Irrigation efficiency | 0.75 and 0.95 |
| Planting date | 14 days earlier and 14 days later |
| Entire crop-coefficient curve | $0.9K_c$ and $1.1K_c$ |

All nine variants keep the 150-day episode and nominal action limit. Change only one assumption at a time. For altered capacity or root depth, initialise at 80% of the scenario capacity and normalise storage by that capacity.

The threshold benchmark receives the scenario capacity. Under efficiency changes, it retains its nominal 0.85 refill calculation, and the RL observation does not reveal efficiency. Under crop-coefficient changes, the observation contains the changed current coefficient.

## 16. Reward sensitivity

Repeat short exploratory runs with shortage weights 5 and 20 while keeping the irrigation and drainage weights fixed at 1. Each agent uses its selected hyperparameters, seeds 101 and 202, and 30,000 interactions per reward setting.

Policies trained under different reward weights must be compared using the physical water and shortage measures and may be rescored under the nominal reward. Their original training returns are not directly comparable.

## 17. Required implementation checks

Before agent training, verify:

- Gymnasium's environment checker passes apart from the documented warning about infinite weather upper bounds;
- reset behaviour is reproducible for a fixed seed;
- observations and rewards are finite;
- actions outside the declared space are rejected;
- no future weather appears in the observation;
- rainfall and ETo histories advance by exactly one day;
- the mass-balance residual remains below $10^{-10}$ mm in the reference test;
- the 150th transition returns `terminated=True`;
- `step()` after termination requires reset;
- genuine termination removes bootstrapping;
- an external collection cut-off does not masquerade as termination; and
- dry, wet, heavy-rain and action-boundary cases match hand calculations.

## 18. Planned interaction totals

| Experiment component | Learning interactions |
|---|---:|
| Tuning | 720,000 |
| Five-seed final training | 1,500,000 |
| Reward sensitivity | 360,000 |
| **Total planned learning interactions** | **2,580,000** |

Evaluation transitions, benchmarks, debugging and environment validation are additional and must not be counted as learning interactions.
