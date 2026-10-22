# Smart Irrigation with Reinforcement Learning

**COMP6008 · Group 12** — Raina Shah (DDPG), Arnav Dangmali (TD3), Malaika Noor (SAC)

This project compares **Deep Deterministic Policy Gradient (DDPG)**, **Twin Delayed DDPG (TD3)** and **Soft Actor-Critic (SAC)** for continuous daily irrigation control in a *simulated* grain-maize field at Kyabram, Victoria, Australia (SILO station `080091`).

An agent chooses **0–20 mm of irrigation per day**. A shared Gymnasium soil-water-balance environment updates available root-zone water using historical rainfall, irrigation, evapotranspiration and drainage. All three agents are evaluated using the same environment, training budgets and held-out seasons.

**Scope:** Historical climate inputs are real records or SILO-derived estimates; the field, soil-water dynamics, irrigation actions and crop response are simulated. This study does **not** measure actual crop yield, demonstrate real-farm deployment or establish superiority on other farms.

## Project status

- Implementations and saved experiments are available for **all three agents: DDPG, TD3 and SAC**.
- Validation-based hyperparameter tuning, five-seed final training/evaluation, reward-sensitivity and nine-scenario robustness experiments have been conducted.
- `04_algorithm_comparison.ipynb` analyses the saved results across agents, including learning curves, stability, held-out performance, robustness and uncertainty.
- `05_farm_replay.ipynb` uses **saved final seed-11 checkpoints** for a synchronised 2017 validation-season replay; it does not retrain the models.
- The comparison and replay outputs, model checkpoints and source data archive are stored in this repository.

The original `00_shared_template.ipynb` remains a **shared environment/scaffold** and still contains agent implementation placeholders. It is **not** a substitute for the completed agent notebooks.

## Where to find the work

| Location | Contents |
|---|---|
| [`notebooks/00_shared_template.ipynb`](notebooks/00_shared_template.ipynb) | Shared environment, assumptions, benchmark and reusable utilities; agent placeholders remain |
| [`notebooks/01_ddpg.ipynb`](notebooks/01_ddpg.ipynb) | Raina's DDPG implementation, training, evaluation and diagnostics |
| [`notebooks/02_td3.ipynb`](notebooks/02_td3.ipynb) | Arnav's TD3 implementation, training, evaluation and findings |
| [`notebooks/03_sac.ipynb`](notebooks/03_sac.ipynb) | Malaika's SAC implementation, training, evaluation and findings |
| [`notebooks/04_algorithm_comparison.ipynb`](notebooks/04_algorithm_comparison.ipynb) | Cross-algorithm analysis of saved experiment outputs; **no retraining required** |
| [`notebooks/05_farm_replay.ipynb`](notebooks/05_farm_replay.ipynb) | Four-controller validation-season replay using saved checkpoints |
| [`data/Irrigation_Data_Audit.zip`](data/Irrigation_Data_Audit.zip) | Bundled climate and soil data, provenance and audit scripts |
| [`outputs/ddpg/`](outputs/ddpg/), [`outputs/td3/`](outputs/td3/), [`outputs/sac/`](outputs/sac/) | Agent checkpoints, tuning records, final results and sensitivity/robustness outputs |
| [`outputs/replay/`](outputs/replay/) | Replay MP4, preview image, daily simulation data and 2017 summary |
| [`outputs/learning_curves_comparison.png`](outputs/learning_curves_comparison.png) and [`outputs/robustness_comparison.png`](outputs/robustness_comparison.png) | Additional group comparison graphics |
| [`docs/`](docs/) | Scientific rationale, fixed settings, data audit and practical-code reuse notes |

The three agent notebooks contain saved execution outputs and are comparatively large. Open one at a time if GitHub's preview struggles to render them.

## Environment and experimental design

| Setting | Value |
|---|---|
| Virtual field | Kyabram, Victoria; SILO station 080091 |
| Crop and episode | Grain maize; 150 daily decisions beginning 1 November |
| Observation | 18 values: storage, season day, crop coefficient, previous irrigation, seven days of rainfall and reference ETo history |
| Action | Normalised continuous action in [−1, 1], mapped to 0–20 mm/day |
| Dynamics | Daily water balance with rain, effective irrigation (nominal efficiency 0.85), drainage and crop evapotranspiration |
| Reward | Negative penalties for irrigation use, soil-water shortage and drainage |
| Training / validation / test planting years | 2005–2016 / 2017–2020 / 2021–2024 |
| Final training | 100,000 environment steps per seed per agent |
| Final training seeds | 11, 22, 33, 44, 55 |
| Tuning | Four configurations × two tuning seeds (101 and 202) × 30,000 steps per agent |
| Main reference policy | Fixed soil-water-threshold controller |

For precise equations, observation ordering, reward scaling and evaluation rules, see [`FIXED_EXPERIMENT_SETTINGS.md`](docs/FIXED_EXPERIMENT_SETTINGS.md). The agent selects irrigation *before* the current day's rainfall and ETo are revealed.

## Reproduce the saved comparisons

The fastest path to inspect the group's final results is to **reuse the checked-in CSV files** rather than rerun all training.

1. Clone or download the whole repository, retaining the `notebooks/` and `outputs/` folders.
2. Set the working directory to the repository root (or `notebooks/`).
3. Open [`notebooks/04_algorithm_comparison.ipynb`](notebooks/04_algorithm_comparison.ipynb) in Jupyter or Google Colab and run its cells in order.
4. Review the input/fairness audit and regenerated tables and graphs in `outputs/comparison/`.

The comparison notebook checks available inputs, fixed final seeds, test years and training budgets. It writes comparison tables, figures and findings to `outputs/comparison/` **when executed**; that generated directory is not necessarily included in the current Git checkout.

### Local setup

The project notebooks use Python, PyTorch, Gymnasium, NumPy, pandas and Matplotlib. The original shared notebook installs these package ranges:

```bash
python -m pip install "gymnasium>=1.0,<2" "numpy>=1.22" "torch>=2.0" "pandas>=2.0" "matplotlib>=3.7" jupyterlab ipykernel nbconvert
```

The recorded GitHub Actions farm-replay build runs on Python 3.11. **Dependency versions for all training notebooks are not pinned in a `requirements.txt` file in this repository at present**; the command above is a starting setup, not a verified lockfile for every original training run.

For Colab, clone the repository into the runtime first (opening only a GitHub notebook does not automatically provide `data/`, `outputs/` or the other notebooks):

```python
!git clone https://github.com/rainashah/comp6008-smart-irrigation-rl.git
%cd /content/comp6008-smart-irrigation-rl
```

Then run the selected notebook with this repository accessible in the runtime. The shared notebook also has an installation cell. Full training is substantially more expensive than loading the saved comparisons.

### Data source and availability

The required experiment input is already included at [`data/Irrigation_Data_Audit.zip`](data/Irrigation_Data_Audit.zip). The simulator reads `irrigation_audit/kyabram_080091_daily.json` **from inside that ZIP**; you do not need to download new climate data to run the supplied saved analyses or the shared environment.

- Climate: Queensland Government **SILO Patched Point** historical daily rainfall and derived reference evapotranspiration.
- Soil: **TERN/CSIRO Soil and Landscape Grid** available-water-capacity data used to define the simplified virtual root-zone reservoir.
- Audit instructions, licensing/source details and optional refresh instructions: [`docs/DATA_AUDIT.md`](docs/DATA_AUDIT.md).
- Refreshing SILO climate data is optional and requires an authorised `SILO_EMAIL` for the provided downloader. A refreshed dataset may differ from the fixed experiment input.

The data ZIP also contains climate/soil audit scripts. The soil audit uses Pillow; it is not needed to analyse the already-saved RL results.

## Re-run an agent or regenerate the video

To inspect an individual implementation, open its notebook: [DDPG](notebooks/01_ddpg.ipynb), [TD3](notebooks/02_td3.ipynb) or [SAC](notebooks/03_sac.ipynb). Each includes the environment and agent-specific development, tuning, final evaluation and analysis. **Follow its own cell order and instructions.** Running training may be time-consuming and may regenerate output files; preserve the checked-in checkpoints and results if you want to compare an independent rerun.

To reproduce the presentation replay **without retraining**, execute [`notebooks/05_farm_replay.ipynb`](notebooks/05_farm_replay.ipynb) from a repository checkout with the saved seed-11 checkpoints present. Creating an MP4 requires an available `ffmpeg` executable (installed in the [farm replay GitHub Actions workflow](.github/workflows/farm-replay.yml)). Its output files include:

- [`farm_replay_2017.mp4`](outputs/replay/farm_replay_2017.mp4) — 37.5-second four-panel replay of DDPG, TD3, SAC and the threshold controller.
- [`farm_replay_2017_preview.png`](outputs/replay/farm_replay_2017_preview.png) — static preview.
- [`farm_replay_2017_daily.csv`](outputs/replay/farm_replay_2017_daily.csv) and [`farm_replay_2017_summary.csv`](outputs/replay/farm_replay_2017_summary.csv) — simulator outputs.

**Important:** 2017 is a **validation** year. The replay is an illustrative comparison under identical simulated conditions, **not** an additional held-out test. Formal performance comparisons use the 2021–2024 test seasons.

## Saved held-out results

Final results averaged over **five training seeds × four held-out planting years (2021–2024)**. Return is discounted environmental reward (higher/less negative is better); irrigation is mean total irrigation per 150-day season.

| Agent | Mean discounted return | SD across seed-level means | Mean irrigation (mm/season) |
|---|---:|---:|---:|
| TD3 | −20.426 | 0.295 | 588.01 |
| DDPG | −21.064 | 0.316 | 601.87 |
| SAC | −22.847 | 0.359 | 621.81 |

TD3 had the highest average reward and lowest irrigation of the three agents under the declared simulator and evaluation. Interpret water savings alongside soil-water shortage and drainage, not in isolation. These results are **not** measured farm yields or evidence of cross-location transfer.

The values originate from the stored final test and summary CSVs. For full per-season, per-seed and robustness comparisons, run `04_algorithm_comparison.ipynb`.

## Supporting documentation

- [`docs/FIXED_EXPERIMENT_SETTINGS.md`](docs/FIXED_EXPERIMENT_SETTINGS.md) — shared design, equations, hyperparameter selection and experiment protocol.
- [`docs/DATA_AUDIT.md`](docs/DATA_AUDIT.md) — source-data screening and provenance; some historical planning statements predate the fixed Kyabram experiment.
- [`docs/PROJECT_OBJECTIVES.md`](docs/PROJECT_OBJECTIVES.md) — rationale, scientific sources and project requirements.
- [`docs/PRACTICAL_CODE_REUSE.md`](docs/PRACTICAL_CODE_REUSE.md) — practical-code starting points and adaptation boundaries.

## Reproducibility and interpretation

Hyperparameters and selected checkpoints were chosen from **validation**, not final test years. Final test summaries, robustness perturbations and reward-sensitivity runs address different questions and should not be conflated. A five-seed study in one simplified virtual field cannot establish universal algorithm superiority.

**Code-submission note:** This repository currently keeps the completed agent implementations in separate notebooks, and `00_shared_template.ipynb` contains placeholders. If the assessment requires one consolidated notebook, a `requirements.txt` file or individual declaration forms, those are **separate submission checks** and should not be assumed complete merely because this README is current.
