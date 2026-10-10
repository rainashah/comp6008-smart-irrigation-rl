# Smart Irrigation with Reinforcement Learning

COMP6008 group project comparing **DDPG, TD3 and SAC** for continuous irrigation control in a simulated maize field at **Kyabram, Victoria**.

The controller selects a daily irrigation depth from **0–20 mm**. A soil-water-balance simulator combines that action with historical rainfall and reference evapotranspiration to update soil-water storage. The objective is to maintain suitable water availability while reducing irrigation use and unnecessary drainage.

## Current status

- Kyabram selected after auditing the available SILO and CSIRO data.
- Historical climate and soil inputs downloaded and screened.
- Shared Gymnasium environment implemented in the group notebook.
- Environment validated for observation shape, action bounds, weather timing, water balance and 150-day termination.
- DDPG implementation, validation-only tuning, five-seed final testing, reward sensitivity and robustness experiments are complete.
- TD3 and SAC implementation and matching experiments remain to be completed by their assigned members.

The climate inputs are real historical observations or SILO interpolations. Soil water, irrigation decisions and crop response are simulated. The reference coordinate represents a virtual field, not a verified commercial paddock.

## Repository structure

```text
.
├── README.md
├── data/
│   └── Irrigation_Data_Audit.zip
├── docs/
│   ├── DATA_AUDIT.md
│   ├── FIXED_EXPERIMENT_SETTINGS.md
│   ├── PRACTICAL_CODE_REUSE.md
│   └── PROJECT_OBJECTIVES.md
├── notebooks/
│   ├── 00_shared_template.ipynb
│   └── 01_ddpg.ipynb
└── outputs/
    ├── ddpg/
    │   └── DDPG_RESULTS_SUMMARY.md
    ├── td3/
    └── sac/
```

## Start here

Open [`notebooks/00_shared_template.ipynb`](notebooks/00_shared_template.ipynb) in Google Colab or Jupyter.

Raina's completed executed DDPG notebook is [`notebooks/01_ddpg.ipynb`](notebooks/01_ddpg.ipynb). Its concise results and limitations are in [`outputs/ddpg/DDPG_RESULTS_SUMMARY.md`](outputs/ddpg/DDPG_RESULTS_SUMMARY.md).

The notebook contains:

- the complete Kyabram Gymnasium environment;
- fixed shared settings and chronological season splits;
- environment validation and benchmark policies;
- shared replay-buffer and neural-network utilities;
- separate work areas for DDPG, TD3 and SAC; and
- templates for tuning, evaluation and results.

If Colab does not make the repository data available automatically, upload [`data/Irrigation_Data_Audit.zip`](data/Irrigation_Data_Audit.zip) using the Colab Files panel before running the data-loading cell.

## Visual farm replay

Both notebooks include a farm animation following the RGB-frame capture and evaluation patterns in Practicals 1 and 9. Open in Colab or a trusted Jupyter notebook and run the visual replay cells for play/pause and frame controls; GitHub's static preview does not run the animation player. Saved compact video previews are embedded in the notebooks.

The template shows the threshold controller. The DDPG notebook also shows final seed 11 on validation season 2017. To regenerate that DDPG replay, place `ddpg_seed11.pt` in `outputs/ddpg/final/` (or upload it to `/content/` in Colab). Crop artwork is illustrative; displayed water, irrigation and reward come from the simulator.

## Parallel group workflow

| Member | Agent | Output directory |
|---|---|---|
| Raina Shah | DDPG | `outputs/ddpg/` |
| Arnav Dangmali | TD3 | `outputs/td3/` |
| Malaika Noor | SAC | `outputs/sac/` |

Each agent keeps its results, checkpoints and visualisations in its own subfolder. Use the notebook helper `agent_output_dir("ddpg")`, `agent_output_dir("td3")` or `agent_output_dir("sac")`; it resolves the same repository output directory when launched from the repository root or `notebooks/`. Keep tuning, final and reward-sensitivity results in corresponding subfolders within the agent directory.


Create the following copies from the shared template:

```text
notebooks/01_ddpg.ipynb
notebooks/02_td3.ipynb
notebooks/03_sac.ipynb
```

Each member should implement only their assigned agent section. The environment, observations, reward, data splits, shared network size, training budgets and evaluation rules must remain identical across agents. Proposed shared-setting changes should be agreed and recorded before final testing.

After the three agents pass short integration runs, merge them into one final comparison notebook for tuning, five-seed experiments, held-out testing and robustness evaluation.

## Current DDPG result

Validation-only tuning selected a learning rate of `0.0003` and exploration standard deviation of `0.1`. Across five final seeds and the held-out 2021–2024 seasons, DDPG achieved a mean discounted return of **-21.041 ± 0.435**, compared with **-21.488** for the fixed threshold controller. DDPG used 14.05 mm less irrigation on average and reduced dry-day violations, but produced 5.91 mm more drainage. This is a result for the declared simulator, not evidence of field superiority.

## Experiment summary

| Component | Shared design |
|---|---|
| Location | Kyabram, Victoria; SILO station `080091` |
| Crop and episode | Grain maize; 150 daily decisions from 1 November |
| Observation | 18 values: soil-water storage, crop progress, previous irrigation and seven days of rainfall/ETo history |
| Action | One continuous normalised action mapped to 0–20 mm irrigation per day |
| Reward | Penalties for irrigation use, soil-water shortage and drainage |
| Training seasons | 2005–2016 |
| Validation seasons | 2017–2020 |
| Test seasons | 2021–2024 |
| Algorithms | DDPG, TD3 and SAC |
| Main benchmark | Fixed soil-water-threshold controller |

## Project documents

- [`DATA_AUDIT.md`](docs/DATA_AUDIT.md) — climate and soil audit, including the Kyabram–Kununurra comparison.
- [`PROJECT_OBJECTIVES.md`](docs/PROJECT_OBJECTIVES.md) — assignment responses, MDP definition, scientific reasoning and references.
- [`FIXED_EXPERIMENT_SETTINGS.md`](docs/FIXED_EXPERIMENT_SETTINGS.md) — authoritative shared implementation, tuning and evaluation rules.
- [`PRACTICAL_CODE_REUSE.md`](docs/PRACTICAL_CODE_REUSE.md) — practical material that can be adapted and the limits of that reuse.

## Reproducibility rule

The test seasons must not be used to select hyperparameters, checkpoints, reward weights or other design settings. Record unsuccessful and numerically failed runs as well as successful results.
