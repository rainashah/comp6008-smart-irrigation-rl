# Smart irrigation: project objectives and proposed approach

**Group-discussion version — Kyabram configuration, updated 6 October 2026.**

We aim to compare DDPG, TD3 and SAC for controlling a continuous irrigation amount in a representative simulated grain-maize field in Kyabram. The controller should reduce unnecessary water use while keeping soil water within a suitable range. The simulation will use historical Australian climate data and location-specific soil parameters.

For this draft we have selected Kyabram and fixed the initial environment and experiment settings in Section 8. The climate inputs are real historical data; soil water and irrigation outcomes are simulated. The reference point represents a virtual field, not a verified commercial paddock. We distinguish evidence-based relationships from our experimental assumptions. No RL agents have been trained for this draft.

## 1. Understand the RL concepts and explain why they apply

Irrigation is a sequential decision problem because water applied today changes the soil water available tomorrow. Applying too little water can increase later water stress. Applying too much can waste water through drainage or runoff. The controller therefore needs to consider the consequences of its actions over a growing season.

Our textbook explains that a policy describes how the agent chooses actions, while a value function estimates expected return under a policy [1, Sec. 3.5]. In our project, the actor selects an irrigation amount and the critic estimates the longer-term value of a decision. This matters because the lowest-water action today may leave the crop short of water later.

Using the textbook's return notation, our seasonal objective is based on:

$$
G_t=\sum_{k=0}^{T-t-1}\gamma^k R_{t+k+1},
$$

where $T$ is the end of the season and $\gamma$ controls the weight given to later rewards [1, Secs. 3.3–3.4]. We aim to maximise expected return, rather than just the reward for one day. SAC also includes an entropy term in its learning objective, as discussed below.

Exploration means trying irrigation amounts whose effects are uncertain; exploitation means using actions that currently look effective [1, Sec. 1.1]. We will explore inside the simulator and document how each agent does this. Random actions on a real farm are outside this project's scope.

This gives us a reason to investigate RL, but it does not establish that RL is necessary or better than a simple controller. We will include a soil-moisture-threshold irrigation rule as a practical benchmark. The project should show whether the additional learning and complexity provide a useful improvement.

## 2. Formulate the environment and examine the MDP assumptions

Our internal MDP includes available soil-water storage, the day within the season and the selected historical weather sequence. Actions are continuous irrigation depths from 0 to 20 mm/day. A daily water balance determines storage and reward after each action. Episodes last 150 days, and the common discount factor is 0.995. The season ending is terminal, with no bootstrap value. Stopping collection because a training budget has been reached is a collection cut-off, not a fabricated terminal transition. Section 8 specifies the observation, equations, reward and numerical settings.

At daily decision time $t$, the agent receives observation $O_t$, selects irrigation $I_t$, and the environment jointly produces reward $R_{t+1}$ and the next observation $O_{t+1}$. The interaction is therefore $O_t\rightarrow I_t\rightarrow\{R_{t+1},O_{t+1}\}$, repeated on the next day. In the textbook's generic notation, the same pattern is $S_t\rightarrow A_t\rightarrow\{R_{t+1},S_{t+1}\}$ [1, Sec. 3.1]. We use $I_t$ for the irrigation action because $A_t$ is already defined below as available soil-water storage.

Sutton and Barto explain that a Markov state must retain the information needed to determine the distribution of the next state and reward [1, Sec. 3.1, p. 49]. We distinguish that internal state from the agent's observation. The agent receives current storage, crop progress and seven days of past weather, but not the season identifier or future weather. This is a partially observable control problem; the history is an approximation to a sufficient state.

The soil-water balance is informed by FAO-56 [2], regional water-balance research [3], local maize research [9] and a peer-reviewed review of crop coefficients [10]. These sources support the modelling approach without validating our particular implementation. We model water above the lower extraction limit rather than inventing absolute moisture measurements. Waterlogging damage and crop yield are outside this baseline's scope.

The reward penalises irrigation, end-of-day shortage and drainage. It follows the textbook's distinction between specifying the desired outcome and prescribing the action sequence [1, Sec. 3.2]. Its numerical weights are our experimental preferences and will receive a separate sensitivity check.

## 3. Implement and tune three suitable agents

The continuous action space is the main reason for choosing DDPG, TD3 and SAC. Our textbook explains how parameterised policies can handle continuous actions without assigning a separate learned value to every possible action [1, Sec. 13.7]. Its actor–critic discussion also explains how a learned value estimate can guide policy updates [1, Sec. 13.5]. These ideas give us the foundation; the original papers below provide the specific algorithms we will implement. We can then compare different actor–critic approaches while keeping the irrigation task fixed.

| Agent | Scientific basis | Reason for including it |
|---|---|---|
| DDPG | Lillicrap et al. developed an actor–critic method for continuous control using a deterministic policy, experience replay and target networks [4]. | It provides a starting point for learning a continuous irrigation amount. Exploration requires a defined noise process. |
| TD3 | Fujimoto et al. address critic overestimation using twin critics, delayed policy updates and target-policy smoothing [5]. | It lets us investigate whether those changes improve stability and irrigation performance compared with DDPG. |
| SAC | Haarnoja et al. combine off-policy learning with a stochastic policy and a maximum-entropy objective [6]. | It provides a different approach to exploration and lets us test whether this helps across changing weather conditions. |

The original papers support their suitability for continuous control. They do not establish which agent will perform best in our irrigation environment. That is an empirical question for this project.

Each member will own one agent's implementation, pseudocode, tuning record and analysis. We will use the labs as a structural reference and explicitly link pseudocode steps to the implementation. Section 8 fixes the algorithm variants, including the original SAC formulation with a state-value network and a fixed entropy coefficient.

Each agent receives 100,000 interactions per final seed and the same four-configuration tuning allowance. Parameters will be selected using validation performance. We will record configurations and unsuccessful trials as well as successful ones, so the comparison does not depend on reporting only favourable runs.

## 4. Evaluate performance, stability and generalisation

Deep RL results can vary with random seeds, hyperparameters and implementation choices. Henderson et al. show why these factors matter when comparing algorithms [7]. We will therefore use multiple seeds and report the variation, rather than compare one successful run from each agent.

| Measure | What it will tell us |
|---|---|
| Evaluation return | How well the policy performs under the agreed reward. |
| Total irrigation, mm/season | How much water the controller applies over the same evaluation period. |
| Time below the target range | How often the simulated root zone is too dry. |
| Cumulative water deficit | How severe and persistent the shortage is, rather than just counting affected days. |
| Excess watering and drainage | Whether avoiding shortage comes at the cost of unnecessary water application. |
| Learning curves | How evaluation performance changes with training interactions. |
| Sample efficiency | How many interactions are needed to reach an agreed performance level, if reached. |
| Stability | Variation across seeds and deterioration or fluctuation during learning. |
| Held-out-season performance | Whether the learned policy works on weather sequences not used for training or tuning. |

We will compare complete seasons using shared initial conditions, action limits and evaluation rules. Chronological training, validation and test splits will keep seasons intact. Any fitted scaling will use training data only. The final test set will remain separate from tuning.

We will plot learning curves against environment interactions and use the operational stability criterion in Section 8. If an agent does not meet that criterion, we will report this rather than describe a noisy plateau as convergence. Training and evaluation will be separated, with the evaluation action-selection rule documented for each agent.

A useful result would reduce irrigation while maintaining comparable or better soil-water control than the threshold benchmark. These are simulation outcomes and plant-water-status proxies; they do not establish actual yield or crop health. Testing unseen years at one location also does not establish transfer to other soils, farms or climates.

## 5. Identify problems and explain their causes

Before long training runs, we will check simple cases: no rainfall or irrigation, irrigation without rainfall, heavy rainfall, a dry root zone and storage near capacity. We will check units, action bounds, water conservation and episode endings. True terminal states and externally imposed cut-offs need explicit handling in the learning targets. The textbook defines the value of a terminal state as zero [1, Sec. 3.5]. For our finite-season task, a genuine season ending therefore has no future-value contribution. A training cut-off before that ending must not automatically be treated as if the irrigation task itself has ended.

If an agent fails, we will examine the environment, reward, observations, exploration and numerical updates before attributing the result to the algorithm. The debugging record should identify what was observed, what was changed and whether the change addressed the problem. Failed runs are evidence to analyse, not results to hide.

The climate audit already shows why source quality needs attention. SILO uses interpolation to construct usable climate records [8]. We will preserve the source flags and distinguish measured inputs from estimates. Complete date coverage alone is not evidence that every daily value was observed.

## 6. Document the work and communicate the findings

The final notebook will explain the data, environment, agents, tuning and evaluation in a reproducible order. It will contain the results used in the report and presentation. The report will connect each major decision to its evidence and explain how the results support the conclusions.

For each important claim, we will separate:

- **Evidence:** what the cited study or our experiment actually shows.
- **Reasoning:** why that evidence supports the choice in this project.
- **Assumptions and limits:** what has not been measured, tested or established.

For example, TD3's design gives us a reason to test improved stability, but only our repeated runs can show whether that happens here. Similarly, a published soil-water model supports our modelling approach without proving our chosen field parameters are correct.

## 7. Plan and share the work fairly

Each member will implement and analyse one agent, contribute scientific references and take responsibility for a shared component. The proposed shared components are environment development, data/training infrastructure, and evaluation. We will review actual workload after the first working versions and redistribute tasks if needed.

Section 8 fixes observation order, action units and episode behaviour for parallel development. We will use one shared result schema for episode metrics and training checkpoints. We will integrate early and review one another's work. Everyone should be able to explain the environment and all three agents, not only their own section.

We will also share the substantial report work on improvements and future extensions. Each member will develop one improvement linked to a demonstrated limitation and one separate direction that expands the project. These proposals will need their own supporting literature and will be refined after the experiments. The references below support the present design; they do not by themselves complete that future-work requirement.

## 8. Kyabram configuration for the main experiment

These are our selected settings for the first implementation. We distinguish published evidence, values calculated from our downloaded data, and choices we have made to keep the experiment manageable. A citation supports the reasoning behind a choice; it does not make every numerical setting a scientifically established optimum.

### 8.1 Location and field representation

We will use **Kyabram, Victoria**, with SILO station **080091** and reference coordinate **36.3350° S, 145.0638° E** (WGS84). We will represent a **virtual agricultural field at this reference point**. This is the audited station coordinate and the centre of our soil extraction area, not a verified commercial maize paddock. We will not assign it a farm name or claim to reproduce an actual field trial.

The reason for choosing Kyabram is the combination of our usable climate record and relevant local irrigation research. Greenwood et al. measured three commercial silage-maize crops in northern Victoria and compared observed soil-water changes with a daily FAO-56 balance [9]. This supports investigating maize irrigation in the region. Their crops and measurements do not establish the properties of our virtual field, and their silage results do not validate our grain-maize calendar.

Our climate file covers 2005–2025. We will retain SILO's source flags, use rainfall and FAO-56 reference evapotranspiration as forcing, and keep temperature for descriptive analysis. Estimated or interpolated weather remains labelled as such [8]. We have already inspected all years for data integrity; the test restriction below concerns model selection and performance analysis, not pretending that the raw test dates have never been seen.

### 8.2 Crop calendar and rooting assumptions

We will model **grain maize**, planted on **1 November**, for **150 daily decisions**. The last simulated day is 30 March in a non-leap ending year and 29 March in a leap ending year. This fixed calendar makes seasons directly comparable. It is a project scenario, not a claim about the optimum planting date or a measured Kyabram cultivar.

| Stage | Days after planting, starting at 0 | Length | Single crop coefficient, $K_c$ |
|---|---|---:|---|
| Initial | 0–29 | 30 days | 0.30 |
| Development | 30–69 | 40 days | $0.30+0.90(t-29)/40$ |
| Mid-season | 70–119 | 50 days | 1.20 |
| Late season | 120–149 | 30 days | $1.20-0.85(t-119)/30$, ending at 0.35 |

FAO-56 provides the 30/40/50/30-day grain-maize example and these standard coefficient endpoints [2, Tables 11–12]. We transfer the seasonal pattern to southern-hemisphere summer as an explicit assumption. The peer-reviewed review by Pereira et al. supports the crop-coefficient method and reports broad agreement with the original FAO-56 coefficients, while emphasising the conditions needed for transfer [10]. Neither source establishes that this exact calendar is correct for Kyabram.

We choose a **fixed effective root-zone depth of 1.0 m**. This is the lower end of FAO-56's mature grain-maize range [2, Table 22] and matches the depth covered by our audited soil layers. Using that depth throughout the episode simplifies the storage model but overstates young plants' access to deeper water. This is a limitation of the baseline model, not a biological claim that seedlings already have one-metre roots. We will evaluate a 0.6 m reservoir as a separate structural sensitivity scenario. A growing-root model would need to track deeper water explicitly so that root growth cannot create water.

We use a single $K_c$ curve to keep the implementation small. The local maize paper reports a **basal** coefficient, $K_{cb}$, which excludes soil evaporation [9]. We will not substitute that value directly for our single $K_c$. Our model does not separately resolve evaporation after each wetting, cultivar development, yield, nutrient stress or waterlogging damage.

### 8.3 Soil storage and uncertainty

We will model **plant-available storage above the lower limit**, $A_t$, rather than absolute volumetric water content. Zero represents the assumed lower limit; $C$ represents available-water capacity up to the drained upper limit. This avoids inventing separate field-capacity and wilting-point measurements that our current audit does not contain.

The following values are the means of the six returned samples in each downloaded Kyabram subset. They are **service-generated area samples**, not six independent field measurements or a native-resolution paddock survey.

| Depth | Audited mean AWC, volume % | Layer thickness | Available storage |
|---|---:|---:|---:|
| 0–5 cm | 12.5000 | 50 mm | 6.2500 mm |
| 5–15 cm | 13.0000 | 100 mm | 13.0000 mm |
| 15–30 cm | 12.1667 | 150 mm | 18.2500 mm |
| 30–60 cm | 11.5000 | 300 mm | 34.5000 mm |
| 60–100 cm | 9.8333 | 400 mm | 39.3333 mm |
| **Total** | — | **1,000 mm** | **111.3333 mm** |

We calculate $C=\sum_j(AWC_j/100)\Delta z_j$, using unrounded values in code. Each episode starts at **$A_0=0.8C=89.0667$ mm**. The same initial storage is used for every agent and benchmark. Irrigation totals cover the simulated season only; they exclude any water needed to establish that common initial condition.

SLGA's hydraulic properties are modelled estimates derived through digital soil mapping and pedotransfer methods [11], with the AWC dataset providing the actual data provenance [12]. Our nominal profile is therefore a regional modelling input. It is not a locally calibrated soil profile.

We will evaluate frozen policies with **$0.8C$ and $1.2C$**, or **89.0667 and 133.6000 mm**, changing one assumption at a time. These are deliberately chosen sensitivity scenarios, **not a 95% confidence interval**. We do not infer statistical uncertainty from the six spatial samples. The 0.6 m root-zone scenario uses the first four layers, giving **72.0 mm**, rather than multiplying the one-metre capacity by 0.6. Field validation and formal map-uncertainty propagation remain outside our claims.

### 8.4 Observation and partial observability

The underlying simulator state contains $A_t$, day index $t$, selected season identifier, and the histories required to construct observations. Given that state and the action, the historical weather replay determines the next transition. This defines the internal MDP [1, Sec. 3.1].

The actor and critic both receive the same **18-element observation**, in this order:

1. $A_t/C$, $t/150$, current $K_c/1.2$, previous irrigation divided by 20.
2. Rainfall for the previous seven completed days, newest first, each divided by 20 mm.
3. Reference evapotranspiration for the same seven days, newest first, each divided by 10 mm.

**Observation properties.** We use a real-valued `float32` vector with shape **`(18,)`**, represented by a Gymnasium `Box`. It is a continuous numerical observation space, although the day index takes discrete daily values and the prescribed crop coefficient follows that index. There are no image inputs or categorical labels to encode.

| Zero-based indices | Feature | Declared range | Interpretation |
|---|---|---|---|
| 0 | $A_t/C$ | $[0,1]$ | Available storage as a fraction of the scenario capacity. |
| 1 | $t/150$ | $[0,1]$ | Decision observations use $t=0,\ldots,149$; the terminal observation uses $t=150$. |
| 2 | $K_{c,t}/1.2$ | $[0,1.1]$ | Nominal decision values lie in $[0.25,1]$. The common upper bound includes the predeclared +10% crop-coefficient scenario. Set this feature to zero at terminal time. |
| 3 | $I_{t-1}/20$ | $[0,1]$ | Previous applied irrigation; zero at reset. |
| 4–10 | $P_{t-1}/20,\ldots,P_{t-7}/20$ | $[0,\infty)$ each | Non-negative rainfall. Values above 1 represent more than 20 mm and remain visible. |
| 11–17 | $ET_{o,t-1}/10,\ldots,ET_{o,t-7}/10$ | $[0,\infty)$ each | Non-negative reference ET. Values above 1 represent more than 10 mm/day and remain visible. |

The declared space is:

```python
observation_space = gymnasium.spaces.Box(
    low=np.zeros(18, dtype=np.float32),
    high=np.array([1.0, 1.0, 1.1, 1.0] + [np.inf] * 14, dtype=np.float32),
    dtype=np.float32,
)
```

Infinite *space bounds* do not permit missing or infinite weather data in our implementation. All input weather and emitted observations must be finite; negative rainfall/ETo or non-finite values fail validation. Using open-ended weather bounds avoids setting limits from test-year maxima or clipping an unseen extreme. Gymnasium's checker warns about the infinite upper bounds; we retain them deliberately and separately check finiteness of actual outputs. Bounds and scaling are part of the interface, while partial observability is a separate modelling question [1, Sec. 3.1].

**Gymnasium interface.** The environment subclasses `gymnasium.Env`. `reset(seed=..., options=...)` returns `(observation, info)`; `step(action)` returns `(observation, reward, terminated, truncated, info)`. The exposed action space is `Box(-1, 1, shape=(1,), dtype=float32)`, mapped to 0–20 mm/day. Out-of-range or non-finite actions are rejected; exploration noise must be bounded by the agent before calling `step`.

`terminated=True` follows the 150th daily transition. The baseline environment does not impose an additional time limit, so `truncated=False`; a later external cut-off must be handled separately. Calling `step` after termination requires a reset first. The final observation retains storage, completed-day weather history and previous irrigation, with time equal to 1 and crop coefficient equal to zero. It is not used to bootstrap a terminal target. Diagnostic `info` contains water fluxes and reward components; neither actor nor critic receives it as an extra input.

These API details follow the [official Gymnasium environment documentation](https://gymnasium.farama.org/api/env/) and [space documentation](https://gymnasium.farama.org/api/spaces/fundamental/). These are implementation references, not peer-reviewed evidence for our scientific model.

The first episode observation uses the actual seven days before planting; previous irrigation is set to zero. Rain and evapotranspiration are divided by fixed scales without clipping, so extreme events remain distinguishable. No fitted normaliser is needed. Growth stage is represented by day index and $K_c$. We omit temperature from the policy because this baseline's phenology is fixed and its atmospheric demand already enters through ETo; this is a modelling choice, not evidence that temperature is generally irrelevant.

We hide the season/year identifier and future realised weather. Consequently, the agent faces a **partially observable problem**, and the seven-day history is an approximation, not proof of a Markov observation. We choose identical feed-forward history inputs for all three agents to keep their comparison manageable. Any claimed convergence is empirical; the fully observed MDP assumptions are not automatically satisfied at the observation level. A recurrent policy would be a separate extension.

### 8.5 Action, efficiency and daily transition

We choose a daily gross irrigation amount **$I_t\in[0,20]$ mm** and a nominal application efficiency **$\eta=0.85$**. The policy's bounded action $u\in[-1,1]$ maps to $I_t=10(u+1)$. Efficiency represents losses before water enters the modelled reservoir; drainage is accounted for separately.

These are **hypothetical sprinkler-system settings**, not measured pump capacity or efficiency at Kyabram. With this limit, at most 17 mm/day reaches storage. Our calculation using only the 2005–2016 training seasons gives a maximum potential crop ET of **11.64 mm/day** under the selected curve. The limit therefore allows both replacement and some replenishment without permitting an unlimited refill. We will evaluate efficiencies of **0.75 and 0.95** separately as sensitivity scenarios. A border-check system with large, infrequent applications would require a different action constraint.

The within-day order is fixed as follows. The agent acts before receiving that day's rainfall or ETo. Then the simulator performs:

$$
ET_{c,t}=K_{c,t}ET_{o,t},\qquad
p_t=\operatorname{clip}\{0.55+0.04(5-ET_{c,t}),\,0.1,\,0.8\},\qquad
A_{\min,t}=(1-p_t)C.
$$

$$
B_t=A_t+P_t+0.85I_t,\quad
D_t=\max(0,B_t-C),\quad
H_t=B_t-D_t,
$$

$$
K_{s,t}=\min(1,H_t/A_{\min,t}),\quad
ET_{a,t}=\min(H_t,K_{s,t}ET_{c,t}),\quad
A_{t+1}=H_t-ET_{a,t}.
$$

The depletion adjustment and stress relationship follow the FAO-56 framework [2, Ch. 8]. Applying all daily inputs before drainage and ET is our numerical approximation. It cannot resolve storm timing, infiltration limits or within-day root stress. We assume rainfall enters the bucket, set explicit surface runoff and capillary rise to zero, and route excess storage to immediate drainage. Thus $D_t$ is a **bucket overflow/drainage proxy**, not a validated drainage measurement. We do not claim to model persistent saturation or its health effects.

The identity $A_{t+1}=A_t+P_t+\eta I_t-D_t-ET_{a,t}$ must hold each day. We record all fluxes; clipping is not used to conceal balance errors. The model is adapted from water-balance principles, not a complete implementation of every FAO-56 process.

### 8.6 Reward and discount factor

Our target range is **$A_{\min,t}\leq A_{t+1}\leq C$**, with the lower bound varying with daily demand. At $ET_c=5$ mm/day, it is **50.1–111.33 mm**. This is plant-available storage, not a percentage soil-moisture sensor reading. End-of-day shortage is a conservative control metric; it is distinct from the day's modelled ET reduction.

We select:

$$
R_{t+1}=-\left[\frac{I_t}{20}
+10\max\left(0,\frac{A_{\min,t}-A_{t+1}}{A_{\min,t}}\right)
+\frac{D_t}{20}\right].
$$

The normalisation makes each term dimensionless. One maximum irrigation action costs 1 reward unit; a 10% shortfall below the lower threshold also costs 1; 20 mm drainage costs 1. This makes persistent shortage costly while retaining a reason to conserve water. Drainage remains penalised even when the final storage has returned below capacity. Rain-driven drainage can be unavoidable, so it must also be reported separately from irrigation.

The **weights 1, 10 and 1 are our stated preferences**, not crop-response coefficients inferred from a paper. The textbook supports expressing the intended outcome through reward [1, Sec. 3.2]; it does not justify these exact weights. This weighted reward permits trade-offs and does not guarantee zero stress.

We choose **$\gamma=0.995$** for all agents. A reward 149 days ahead retains about 47% of its immediate weight, compared with about 22% at 0.99. This gives later seasonal effects substantial influence while retaining discounted learning targets [1, Sec. 3.3]. It is not a published optimum. Evaluation reports both discounted and undiscounted environmental return, with physical water/stress metrics alongside them. SAC's entropy bonus is excluded from these shared evaluation returns.

For reward sensitivity, we will repeat short runs with shortage weights **5 and 20**, keeping the other weights fixed. Policies trained under different weights will be compared using water and stress outcomes and rescored under the nominal reward; their original returns are not directly comparable.

A training-only arithmetic check of this proposed balance and reward covered all 12 training seasons. Mean undiscounted returns were approximately **−745.22 for no irrigation, −250.59 for daily maximum irrigation and −39.59 for the threshold rule below**. This checks that obvious extremes are unattractive under these scenarios. It does not prove the reward cannot be exploited or show that any RL agent has learned successfully.

### 8.7 Splits, seeds and training budget

A season is labelled by its **planting year**, not its ending year. We use 20 complete 150-day seasons:

| Purpose | Planting years | Season count |
|---|---|---:|
| Training | 2005–2016 | 12 |
| Validation | 2017–2020 | 4 |
| Final test | 2021–2024 | 4 |

The last test season ends in March 2025. November 2025 is excluded because its season would extend beyond the downloaded record. Training samples complete seasons uniformly; days stay in their original order. All agents receive the same season schedule for a given seed, using a separate environment RNG from network and exploration RNGs. This controls exposure while allowing algorithms to differ in their learning.

Whole-season separation prevents adjacent days from the same episode entering different partitions. The final four seasons are used once the environment, reward, algorithm settings and evaluation plan are frozen. Test years are never used to select hyperparameters, checkpoints or favourable weather subsets.

| Setting | Selected value | Reasoning |
|---|---|---|
| Final training seeds | 11, 22, 33, 44, 55 | Five independent training runs per agent allow us to show variation within a student-project budget. Five is a compromise, not a guarantee of statistical power [7]. |
| Final interaction budget | 100,000 training transitions per run | About 667 season-equivalents of interaction, repeatedly drawn from only 12 unique seasons. Equal interaction budgets support sample-efficiency comparison; they do not imply equal compute. |
| Tuning allowance | Four configurations × seeds 101 and 202 × 30,000 transitions per agent | Equal search size and interaction allowance; selection uses validation only. |
| Evaluation interval | At step 0 and every 5,000 training transitions | Evaluate all four validation seasons from the shared initial storage; no learning or replay insertion during evaluation. |
| Checkpoint used for final test | Step 100,000 | Removes discretionary best-checkpoint selection. Save intermediate checkpoints for learning curves only. |
| Evaluation policy | DDPG/TD3: actor without exploration noise. SAC: tanh of the Gaussian mean | A fixed deployment rule gives repeatable nominal evaluation; this SAC action is not claimed to equal its distribution's exact mean after squashing. |
| Replay and minibatch | 100,000 transitions; minibatch 128 | Enough buffer for a full main run while keeping memory use modest. |
| Initial exploration | 1,500 uniformly random actions | Ten episodes before gradient updates; included in the total budget. |
| Networks | Two hidden layers of 128 ReLU units per actor/critic/value network | A compact starting capacity for 18 inputs and one action. Equal layer sizes do not give identical parameter counts. |
| Optimiser and target update | Adam; $\tau=0.005$ | Documented implementation choices held fixed except the learning-rate grid below. |
| Update budget | One critic/value update set per environment step after warm-up | TD3 still delays actor/target updates according to its algorithm. Record actual update counts and wall time. |

DDPG and TD3 tune learning rate **$10^{-4}$ or $3\times10^{-4}$**, crossed with Gaussian exploration standard deviation **0.1 or 0.2** in the $[-1,1]$ action space. We use independent Gaussian exploration for both as an explicit DDPG adaptation. TD3 uses delay **2**, target smoothing standard deviation **0.2** and noise clipping **±0.5**, before bounding the target action [5].

To keep the implementation tied to the peer-reviewed paper, SAC uses the **2018 formulation with a separate state-value network and fixed entropy coefficient**, rather than silently switching to a later variant [6]. Tune learning rate **$10^{-4}$ or $3\times10^{-4}$**, crossed with **$\alpha=0.1$ or $0.2$**. Use a tanh-squashed Gaussian, including the log-probability correction, with entropy defined in the normalised action coordinates. We use Adam's default betas $(0.9,0.999)$ and epsilon $10^{-8}$ for all agents.

Select the configuration with the highest mean **discounted environmental validation return** at 30,000 transitions across both tuning seeds and all four validation seasons. Break exact ties by lower validation irrigation, then the predeclared configuration order. A configuration with a numerically failed tuning run receives a selection score of negative infinity; the failed run remains in the record. If every configuration fails for an agent, fix and version the implementation before restarting the comparable experiment.

The main comparison and tuning require **2.22 million training transitions in total**. The two reward-sensitivity settings add **360,000** transitions: each agent uses its selected hyperparameters, seeds 101 and 202, and 30,000 transitions per setting. Total planned learning interactions are therefore **2.58 million**, excluding debugging and evaluation. Reward-sensitivity runs are exploratory and remain on training/validation seasons.

We will report each final seed's mean over the four test seasons, then the mean, sample standard deviation and all five seed results. Also show results separately by season. Days and seed–season combinations will not be presented as independent replicates. Four test seasons limit the strength of any generalisation claim [7].

For an operational learning-curve measure, call performance *stable* when the range across the last five validation checkpoints is at most $0.05\max(1,|\bar G|)$, where $\bar G$ is their mean. This is a declared plateau criterion, not a convergence theorem or proof of good performance. Report sample efficiency as the first checkpoint that matches or exceeds the threshold benchmark's mean validation return and continues to do so for the next two checkpoints; otherwise report “not reached”.

### 8.8 Benchmarks and robustness checks

The main benchmark uses only current storage: if $A_t<0.65C$, apply $I_t=\min[20,(0.90C-A_t)/0.85]$; otherwise apply zero. Its trigger and refill target are our fixed control settings, not a literature-derived optimum. It receives the same water limit, efficiency and initial condition as the RL agents. Also report zero-irrigation and maximum-irrigation policies as diagnostic bounds.

After freezing the main experiment, evaluate the final policies on the four test seasons under these one-at-a-time perturbations: capacity ×0.8 and ×1.2; effective rooting depth 0.6 m; efficiency 0.75 and 0.95; planting 14 days earlier and later; and the entire $K_c$ curve ×0.9 and ×1.1. All nine variants retain 150 days and the nominal action limit. Recompute the physical target range using the scenario capacity and crop demand. For capacity and root-depth changes, normalise observed storage by the scenario capacity and initialise at 80% of that capacity; the threshold benchmark uses the same known capacity. These therefore test transfer with a known storage calibration, not robustness to an unknown soil-sensor calibration error. For efficiency changes, the benchmark retains its nominal 0.85 refill calculation and RL observations contain no efficiency input. For crop-curve changes, the observation supplies the changed current coefficient. No policy retraining occurs. These tests assess sensitivity to selected assumptions, not robustness to every possible farm condition.

We will report irrigation, cumulative end-of-day shortage in mm-days, days below the target, actual/potential ET ratio, drainage and return. For shifted calendars, histories follow the shifted dates. These periods still fit within the downloaded record and remain separate from the training years. A policy that saves water by increasing stress must be described as a trade-off, not an unqualified improvement.

### 8.9 Environment timestep cost and computational feasibility

**Question: How much time does the environment take to process one timestep?**

We measured a small `gymnasium.Env` prototype implementing the nominal equations, action checks, 18-element observations and diagnostic flux outputs described above. It used the actual downloaded Kyabram training seasons. This is a planning benchmark of the environment, not a trained-agent result or a completed project notebook.

| Benchmark detail | Recorded value |
|---|---|
| Date | 4 October 2026 |
| Host | Shared Linux x86-64 host, CPU reported as AMD EPYC 9V74; single-process Python loop, no GPU |
| Versions | Python 3.12.14; NumPy 2.3.5; Gymnasium 1.3.0 |
| Data loading | Climate JSON loaded and training-season arrays assembled once, outside the timed loop |
| Pre-timing checks | Gymnasium `check_env` plus 10,000 validation/warm-up transitions |
| Timed workload | Five repetitions, each with 100,000 transitions; resets included whenever a season ended |
| Actions | Uniform random actions generated before timing; no actor-network inference |
| Timing method | `time.perf_counter()` around each full loop; elapsed time divided by 100,000 |
| Five elapsed times | 1.052154, 1.051865, 1.054582, 1.076037, 1.070947 seconds |
| Median amortised time | **10.55 microseconds per transition**, including reset and loop overhead |
| Range of repetition means | **10.52–10.76 microseconds per transition**; this is not a per-step latency percentile |
| Median throughput | Approximately **94,824 transitions/second** |

The validation checked that outputs were finite and inside their declared space, rainfall history advanced without revealing future values, the terminal flag occurred on day 150, rewards were finite/non-positive, and water-balance residuals stayed below $10^{-10}$ mm. The only recorded Gymnasium warning concerned the intentionally infinite weather-space bounds. These checks establish basic implementation consistency, not agronomic validation.

At the measured rate, **2.58 million learning interactions correspond to approximately 27.2 seconds of environment execution alone**. This extrapolation excludes file loading, neural-network inference, replay sampling, gradient updates, evaluation, checkpoints, plotting and logging. It is not an estimate that the complete experiment will finish in 27 seconds, and it does not predict performance on a MacBook or a Colab instance.

The calculation per step uses a fixed number of arithmetic operations and a fixed 14-value weather history. It needs no external API calls or optimisation solver during training. This supports computational feasibility of the environment. Neural-network updates are likely to account for much more time; their cost has not yet been measured.

**End-to-end runtime measurement.** Once each agent is integrated, run a 10,000-interaction pilot on the chosen training hardware. Measure warm-up/collection time, post-warm-up update time, and one four-season evaluation separately. Record device and software versions. Estimate each agent's planned total from its number of runs, warm-up steps and update steps, then add evaluation/checkpoint time and a 30% scheduling contingency. Use actual measurements for each algorithm rather than treating their update costs as equal. These pilot results must replace an assumed wall-clock training estimate before launching the final runs.

The final 100,000-step runs have 21 validation checkpoints each, including step zero. Tuning and reward-sensitivity runs have seven each. Together with final testing and the nine environmental variants, this gives **430,200 additional RL-policy evaluation transitions**, assuming every planned run finishes. Diagnostic benchmark policies and debugging are extra. Evaluation uses forward passes but no gradient updates. This distinction prevents us from equating the learning-transition budget with the complete compute budget.

### 8.10 Implementation feasibility, dependencies and timeline

**Question: Can we implement the environment in a reasonable time without obscure data or special algorithms?**

Yes, for the deliberately simplified model specified here. Climate and soil inputs have already been downloaded and screened. The transition is an explicit daily calculation, and the planning prototype already demonstrates that the observation, action and step interfaces can run. We do not need a crop-growth package, paid weather service, numerical PDE solver or live farm hardware. This conclusion applies to a comparative simulation study, not to a field-ready irrigation controller.

The implementation is feasible within the project timeline because the main data sources are already available, the environment uses a small fixed-size observation and one continuous action, and each transition requires only a short sequence of arithmetic operations. The measured prototype also passed the Gymnasium interface and consistency checks described in Section 8.9. The remaining work is integration, validation and documentation rather than development of an obscure simulator or collection of new field data.

| Planned date | Milestone | Completion evidence |
|---|---|---|
| 5 October | Freeze data loading, calendar, configuration and season partitions | All 20 seasons and seven-day histories available; disjoint season lists; saved input hashes and configuration. |
| 5–6 October | Implement the shared environment and scenario options | Working `reset()` and `step()` methods, fixed space definitions, seeded season selection and scenario parameters. |
| 6–7 October | Validate physics and information timing | Hand-calculated dry, wet and action-boundary cases; mass balance; reproducible resets; no future-weather inputs; correct terminal handling. |
| 7 October | Benchmark and check agent integration | Environment timing reproduced on the selected hardware; all three agent loops accept the same interface. |
| 7–8 October | Document and independently review the environment | Notebook equations match the code; configuration, assumptions and metrics are explained; another member completes a review. |
| 11 October | Complete integrated agent implementations and runtime pilots | DDPG, TD3 and SAC run through the shared environment; pseudocode is mapped to code; end-to-end runtime is recorded. |
| 15 October | Complete tuning runs | All agents receive the declared tuning allowance; validation results and failed trials are retained. |
| 18 October | Complete final experiments | Five-seed main runs, held-out tests and planned robustness evaluations are saved. |
| 19–22 October | Complete analysis, reproducibility checks and presentation | Final figures and tables reproduce from saved results; recorded presentation is ready before the deadline. |
| 29 October | Complete report review | Group review finished before the 30 October report deadline. |

One member owns environment integration, while the other two work in parallel on agent components and the data/evaluation utilities using the frozen interface. All three still own an agent. We redistribute shared tasks if environment development takes substantially more time, so that the integration owner does not also carry all validation and documentation work.

**Dependencies and execution.** Use Python, NumPy and Gymnasium for the environment; PyTorch for our agent implementations; pandas and Matplotlib for analysis and figures. The benchmark versions above are verified for the prototype. The full notebook's dependency versions will be recorded after integration on the selected runtime. Load weather into memory before training and save checkpoints/results to persistent storage. The final submission is one organised notebook; existing library trainers are not a substitute for our own agent implementations.

The timeline leaves limited recovery time before the **23 October** code and presentation deadline and the **30 October** report deadline. It shows that the environment is manageable, but it does not guarantee that every agent will train successfully.

**Scope and contingency.** Keep the single-reservoir model, fixed phenology and historical weather replay for the main comparison. If runtime pilots exceed the available compute window, first remove avoidable per-step I/O and excessive logging. Any necessary budget revision must be documented and applied fairly to all three agents before final testing. We will not inspect test performance and then give a preferred agent more tuning time. A training failure requires technical investigation; limited resources alone are not our scientific explanation for failure.

## References

[1] R. S. Sutton and A. G. Barto, *Reinforcement Learning: An Introduction*, 2nd ed. Cambridge, MA, USA: MIT Press, 2018. [Publisher](https://mitpress.mit.edu/9780262039246/reinforcement-learning/). Course copy: *RLbook2020(1).pdf*, with copyright dates 2018 and 2020. Section and page references above refer to this supplied copy; page numbers are the printed book pages.

[2] R. G. Allen, L. S. Pereira, D. Raes, and M. Smith, *Crop Evapotranspiration: Guidelines for Computing Crop Water Requirements*, FAO Irrigation and Drainage Paper 56. Rome, Italy: FAO, 1998. [Crop coefficients](https://www.fao.org/4/x0490e/x0490e0b.htm); [soil-water stress and balance](https://www.fao.org/4/x0490e/x0490e0e.htm).

[3] K. L. Greenwood, A. R. Lawson, and K. B. Kelly, “The water balance of irrigated forages in northern Victoria, Australia,” *Agricultural Water Management*, vol. 96, no. 5, pp. 847–858, 2009. doi: [10.1016/j.agwat.2008.11.005](https://doi.org/10.1016/j.agwat.2008.11.005).

[4] T. P. Lillicrap et al., “Continuous control with deep reinforcement learning,” in *Proc. International Conference on Learning Representations (ICLR)*, 2016. [Author manuscript](https://arxiv.org/abs/1509.02971).

[5] S. Fujimoto, H. van Hoof, and D. Meger, “Addressing function approximation error in actor-critic methods,” in *Proc. 35th International Conference on Machine Learning*, vol. 80, 2018, pp. 1587–1596. [Proceedings](https://proceedings.mlr.press/v80/fujimoto18a.html).

[6] T. Haarnoja, A. Zhou, P. Abbeel, and S. Levine, “Soft actor-critic: Off-policy maximum entropy deep reinforcement learning with a stochastic actor,” in *Proc. 35th International Conference on Machine Learning*, vol. 80, 2018, pp. 1861–1870. [Proceedings](https://proceedings.mlr.press/v80/haarnoja18b.html).

[7] P. Henderson, R. Islam, P. Bachman, J. Pineau, D. Precup, and D. Meger, “Deep reinforcement learning that matters,” in *Proc. AAAI Conference on Artificial Intelligence*, vol. 32, no. 1, 2018, doi: [10.1609/aaai.v32i1.11694](https://doi.org/10.1609/aaai.v32i1.11694). [Proceedings](https://ojs.aaai.org/index.php/AAAI/article/view/11694).

[8] S. J. Jeffrey, J. O. Carter, K. B. Moodie, and A. R. Beswick, “Using spatial interpolation to construct a comprehensive archive of Australian climate data,” *Environmental Modelling & Software*, vol. 16, no. 4, pp. 309–330, 2001, doi: [10.1016/S1364-8152(01)00008-1](https://doi.org/10.1016/S1364-8152%2801%2900008-1). [Publisher](https://www.sciencedirect.com/science/article/pii/S1364815201000081).

[9] K. L. Greenwood, G. N. Mundy, and K. B. Kelly, “On-farm measurement of the water use and productivity of maize,” *Australian Journal of Experimental Agriculture*, vol. 48, no. 3, pp. 274–284, 2008, doi: [10.1071/EA06094](https://doi.org/10.1071/EA06094).

[10] L. S. Pereira, P. Paredes, D. J. Hunsaker, R. López-Urrea, and Z. Mohammadi Shad, “Standard single and basal crop coefficients for field crops. Updates and advances to the FAO56 crop water requirements method,” *Agricultural Water Management*, vol. 243, Art. no. 106466, 2021, doi: [10.1016/j.agwat.2020.106466](https://doi.org/10.1016/j.agwat.2020.106466).

[11] B. P. Malone et al., “Update and expansion of the soil and landscape grid of Australia,” *Geoderma*, vol. 455, Art. no. 117226, 2025, doi: [10.1016/j.geoderma.2025.117226](https://doi.org/10.1016/j.geoderma.2025.117226).

[12] R. Searle, P. D. S. N. Somarathna, and B. Malone, *Soil and Landscape Grid National Soil Attribute Maps – Available Volumetric Water Capacity (Percent) (3 arc second resolution) Version 2*, CSIRO, 2022, dataset, doi: [10.25919/4jwj-na34](https://doi.org/10.25919/4jwj-na34). The DOI currently points to the CSIRO collection revision v4. “Version 2” names the soil product; collection revision and product version are different. The audit's saved WCS URLs and file hashes identify our actual downloads.

## Reference verification record

**Checked 4 October 2026.** The checks covered (1) publication identity and publication type, (2) DOI registration/title match where a DOI was identified, and (3) whether the source actually supports the claim made here. DOI metadata was checked against Crossref for journal/conference items and DataCite for the dataset, with publisher or conference records checked separately. A DOI alone is not evidence of peer review.

| Ref. | Publication / review status | DOI outcome | What it supports and what it does not |
|---|---|---|---|
| [1] | Authoritative MIT Press textbook; supplied course copy checked. Not classified here as a peer-reviewed research article. | No DOI verified for this edition; cite ISBN **9780262039246** and the publisher. | MDP, policy, return, reward and actor–critic foundations; not exact crop settings or neural-agent convergence in this observation space. |
| [2] | Authoritative FAO technical manual; not a peer-reviewed journal article. | No DOI verified; retain official FAO chapter links. | Source equations and tables; local parameter transfer remains an assumption. |
| [3] | Peer-reviewed research article, *Agricultural Water Management*. | **10.1016/j.agwat.2008.11.005**: Crossref title/author/year match and DOI redirect checked. | Regional forage water-balance evidence; not field-specific validation. |
| [4] | Peer-reviewed ICLR 2016 conference paper; checked against the official accepted-paper record and author manuscript. | No conference-publication DOI identified. | Original DDPG method. Its arXiv record is an access copy, not independent proof of peer review. |
| [5] | Peer-reviewed ICML 2018 conference paper, PMLR 80. | Official proceedings metadata lists no DOI. | Original TD3 mechanisms; no guarantee of superiority for irrigation. |
| [6] | Peer-reviewed ICML 2018 conference paper, PMLR 80. | Official proceedings metadata lists no DOI. | Original SAC formulation; not authority for silently using later automatic-temperature variants. |
| [7] | Peer-reviewed AAAI 2018 technical-track paper. | **10.1609/aaai.v32i1.11694**: Crossref and AAAI record match; DOI redirect checked. | Reproducibility and variability; does not prescribe exactly five seeds or our budget. |
| [8] | Peer-reviewed research article, *Environmental Modelling & Software*. | **10.1016/S1364-8152(01)00008-1**: Crossref and publisher match; DOI redirect checked. | SILO interpolation methodology; not a validation of every downloaded value. |
| [9] | Peer-reviewed research article, *Australian Journal of Experimental Agriculture*. The publisher now hosts it within its Animal Production Science archive. | **10.1071/EA06094**: Crossref and CSIRO/ConnectSci title, authors, year and pages match. Direct resolver access was blocked in one check; the publisher's DOI lookup and abstract were accessible. | Regional silage-maize measurements and FAO-56 comparison; not our grain calendar, exact coordinate or single-coefficient value. |
| [10] | Peer-reviewed review article, *Agricultural Water Management*; the authors' university record explicitly classifies it as peer-reviewed. | **10.1016/j.agwat.2020.106466**: Crossref and author/publisher metadata match; DOI redirect checked. | Crop-coefficient method and transfer conditions; 2020 in the DOI does not change the 2021 volume citation. |
| [11] | Peer-reviewed research article, *Geoderma*; published version and received/revised/accepted history checked. | **10.1016/j.geoderma.2025.117226**: Crossref, publisher metadata and published PDF match; DOI redirect checked. | Digital soil mapping methods and limitations; not a measured Kyabram soil profile. |
| [12] | Research dataset; not a peer-reviewed article. | **10.25919/4jwj-na34**: DataCite title/creator/type match and DOI redirect checked. | Data provenance only; dataset DOI must not be counted as a peer-reviewed paper. |

There are **six peer-reviewed publications with verified registered DOIs** in this list: [3], [7]–[11]. The three original algorithm papers are also peer-reviewed, but no conference DOI was identified in the checked records. We retain the textbook, FAO manual and soil dataset because they serve distinct purposes, and label their status rather than claiming every reference is a peer-reviewed DOI-bearing article. We have not substituted arXiv DOIs or invented DOIs to fill gaps.

Verification links: [ICLR 2016 accepted papers](https://iclr.cc/archive/www/2016.html); [PMLR review expectations](https://proceedings.mlr.press/faq.html); [AAAI peer-review statement](https://ojs.aaai.org/index.php/AAAI/about); [CSIRO publishing policies](https://connectsci.au/an/pages/publishing-policies); [CSIRO maize article and publication history](https://connectsci.au/an/article-lookup/doi/10.1071/ea06094); [Pereira et al. author-institution record](https://researchportal.ulisboa.pt/en/publications/standard-single-and-basal-crop-coefficients-for-field-crops-updat/); [Malone et al. published version](https://researchonline.jcu.edu.au/94095/1/94095.pdf); [SLGA DataCite record](https://api.datacite.org/dois/10.25919/4jwj-na34). These links verify provenance and status; they are not additional scientific evidence for our numerical choices.

## Appendix: reproducible planning benchmark

<details>
<summary>Environment prototype and timing script used for Section 8.9</summary>

This code is retained to make the planning measurement inspectable. It implements the nominal training-season environment only; it is not the final notebook, scenario suite or an RL-agent implementation. Save the code as `kyabram_runtime_check.py` and run it against the audited JSON:

```bash
python kyabram_runtime_check.py /path/to/kyabram_080091_daily.json
```

```python
"""Planning prototype: benchmark environment execution, not RL training."""
import json, sys, platform, time, warnings
from datetime import date, timedelta
from pathlib import Path
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from gymnasium.utils.env_checker import check_env

class KyabramPrototype(gym.Env):
    metadata = {'render_modes': []}

    def __init__(self, climate_path):
        super().__init__()
        rows = {r['date']: r for r in json.loads(Path(climate_path).read_text())}
        self.weather = []
        for year in range(2005, 2017):
            start = date(year, 11, 1) - timedelta(days=7)
            block = [[rows[(start + timedelta(days=i)).isoformat()][k]
                      for k in ('rain_mm', 'eto_mm')] for i in range(157)]
            self.weather.append(np.asarray(block, dtype=np.float64))
        self.weather = np.stack(self.weather)
        assert np.isfinite(self.weather).all() and (self.weather >= 0).all()
        self.capacity = 111.33333333333334
        self.action_space = spaces.Box(-1.0, 1.0, shape=(1,), dtype=np.float32)
        self.observation_space = spaces.Box(
            low=np.zeros(18, dtype=np.float32),
            high=np.array([1, 1, 1.1, 1] + [np.inf] * 14, dtype=np.float32),
            dtype=np.float32)
        self.day = 150

    @staticmethod
    def kc(t):
        if t >= 150: return 0.0  # terminal observation only
        if t < 30: return 0.3
        if t < 70: return 0.3 + 0.9 * (t - 29) / 40
        if t < 120: return 1.2
        return 1.2 - 0.85 * (t - 119) / 30

    def observation(self):
        history = self.weather[self.season, self.day:self.day + 7][::-1]
        return np.concatenate((
            [self.storage / self.capacity, self.day / 150,
             self.kc(self.day) / 1.2, self.previous_irrigation / 20],
            history[:, 0] / 20, history[:, 1] / 10)).astype(np.float32)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.season = int(self.np_random.integers(12))
        self.day = 0
        self.storage = 0.8 * self.capacity
        self.previous_irrigation = 0.0
        return self.observation(), {}

    def step(self, action):
        if self.day >= 150: raise RuntimeError('Reset after termination')
        action = np.asarray(action, dtype=np.float32)
        if not self.action_space.contains(action):
            raise ValueError('Expected one finite action in [-1, 1]')
        irrigation = 10.0 * (float(action[0]) + 1.0)
        rain, eto = self.weather[self.season, self.day + 7]
        demand = self.kc(self.day) * float(eto)
        depletion_fraction = min(0.8, max(0.1, 0.55 + 0.04 * (5 - demand)))
        lower = (1 - depletion_fraction) * self.capacity
        prior = self.storage
        incoming = prior + float(rain) + 0.85 * irrigation
        drainage = max(0.0, incoming - self.capacity)
        wet_storage = incoming - drainage
        actual_et = min(wet_storage, min(1.0, wet_storage / lower) * demand)
        self.storage = wet_storage - actual_et
        shortage = max(0.0, lower - self.storage)
        reward = -(irrigation / 20 + 10 * shortage / lower + drainage / 20)
        self.previous_irrigation = irrigation
        self.day += 1
        info = dict(irrigation_mm=irrigation, drainage_mm=drainage,
                    actual_et_mm=actual_et, potential_et_mm=demand,
                    shortage_mm=shortage,
                    balance_residual_mm=self.storage -
                    (prior + float(rain) + 0.85 * irrigation - drainage - actual_et))
        return self.observation(), float(reward), self.day == 150, False, info

def main(path):
    env = KyabramPrototype(path)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        check_env(env, skip_render_check=True)
    env.reset(seed=11)
    rng = np.random.default_rng(2026)
    actions = rng.uniform(-1, 1, size=(100_000, 1)).astype(np.float32)
    # Untimed validation: every output, history timing, boundaries, water balance.
    for action in actions[:10_000]:
        old_day, season = env.day, env.season
        obs, reward, terminal, truncated, info = env.step(action)
        assert env.observation_space.contains(obs) and np.isfinite(obs).all()
        assert np.isfinite(reward) and reward <= 0
        assert abs(info['balance_residual_mm']) < 1e-10
        assert terminal == (old_day == 149) and not truncated
        assert np.isclose(obs[4] * 20, env.weather[season, old_day + 7, 0])
        if terminal: env.reset()
    durations = []
    for repeat in range(5):
        env.reset(seed=11 + repeat)
        start = time.perf_counter()
        for action in actions:
            _, _, terminal, truncated, _ = env.step(action)
            if terminal or truncated: env.reset()
        durations.append(time.perf_counter() - start)
    cpu = next((line.split(':', 1)[1].strip() for line in
                Path('/proc/cpuinfo').read_text().splitlines()
                if line.startswith('model name')), 'unknown')
    result = dict(python=platform.python_version(), numpy=np.__version__,
                  gymnasium=gym.__version__, platform=platform.platform(), cpu=cpu,
                  measured_on='2026-10-04', warmup_validation_steps=10_000,
                  timed_steps_per_repeat=100_000, repeats=5,
                  seconds=durations, median_us_per_step=float(np.median(durations))*10,
                  check_env_passed=True, validation_passed=True,
                  checker_warnings=[str(w.message) for w in caught])
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main(sys.argv[1])
```

</details>
