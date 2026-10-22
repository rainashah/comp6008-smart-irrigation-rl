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
- The **[executed consolidated review notebook](notebooks/COMP6008_Group12_Consolidated_Review.ipynb)** brings the three agents, shared environment, saved-result comparisons and replay verification into one notebook. Its recorded Colab run shows both held-out and replay checks passing; it does not retrain by default.
- A project-specific [`requirements.txt`](requirements.txt) with six direct, version-pinned Python dependencies is now included.

The original `00_shared_template.ipynb` remains a **shared environment/scaffold** and still contains agent implementation placeholders. It is **not** a substitute for the completed agent notebooks.

## Where to find the work

| Location | Contents |
|---|---|
| **[`notebooks/COMP6008_Group12_Consolidated_Review.ipynb`](notebooks/COMP6008_Group12_Consolidated_Review.ipynb)** | **Primary review notebook**: consolidated implementations, saved-results comparison, verification checks and 2017 replay; includes recorded Colab outputs |
| [`requirements.txt`](requirements.txt) | Six direct Python dependencies, selected dynamically from project notebook imports and installed versions |
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

## Run the consolidated notebook (recommended)

The **[consolidated review notebook](notebooks/COMP6008_Group12_Consolidated_Review.ipynb)** is the single entry point for reviewing the shared environment, DDPG, TD3 and SAC implementations, saved held-out comparisons and the 2017 replay. It has recorded execution outputs on `main`: **all 60 test seed–season records agree with the saved results, and all four replay controllers match the stored 2017 replay**. These are saved-output verification checks, **not** a fresh retraining run.

### Run in Google Colab

1. Open [**the consolidated notebook in Colab**](https://colab.research.google.com/github/rainashah/comp6008-smart-irrigation-rl/blob/main/notebooks/COMP6008_Group12_Consolidated_Review.ipynb).
2. Start a **fresh Python runtime**. The notebook's first code cell clones this repository to `/content/comp6008-smart-irrigation-rl`, changes directory to `notebooks/` and installs its initial Python packages. **Do not clone it a second time into the same path.** If that directory already exists, restart the runtime before running the bootstrap cell.
3. Run the notebook's cells in order (`Runtime → Run all`). The standard configuration reads existing experiment files and **does not retrain** the models.
4. Confirm that the comparison audit lists all three agents and that the notebook prints:

   - `PASS: All 60 held-out seed-season records agree with the saved group results.`
   - `PASS: All four 2017 replay controllers reproduce the saved results.`

5. The comparison section writes fresh analysis figures and tables to `outputs/comparison/` in the **runtime checkout**. The replay verification writes separate files to `outputs/consolidated_replay/`. These files are **not automatically committed to GitHub**.

**Default safety switches:** `RUN_DDPG_DEVELOPMENT`, `RUN_DDPG_TUNING`, `RUN_FINAL_DDPG`, `RUN_TD3_DEVELOPMENT`, `RUN_TD3_TUNING`, `RUN_FINAL_TD3`, `RUN_TD3_REWARD_SENSITIVITY`, and `RUN_SAC_EXPERIMENTS` are `False`. `RUN_REPLAY_CHECK` is `True` and `GENERATE_NEW_MP4` is `False`. Keep the training switches off when verifying the saved results; enabling them can regenerate model or result files.

The final dependency-management cell in the notebook can regenerate `requirements.txt` from the current Colab runtime. It writes only to the runtime's repository checkout unless someone commits it.

### Dependencies and local setup

The repository now includes [`requirements.txt`](requirements.txt) with the six directly imported Python dependencies as recorded in the successful Colab environment:

```text
gymnasium==1.4.0
ipython==7.34.0
matplotlib==3.10.0
numpy==2.1.3
pandas==2.2.3
torch==2.11.0
```

On a compatible local Python installation, install them using:

```bash
python -m pip install -r requirements.txt
```

A local Jupyter interface (for example, JupyterLab) must also be installed to open `.ipynb` notebooks. **FFmpeg is a separate system-level requirement only for generating a new MP4**; the original replay video is already stored in `outputs/replay/`.

**How `requirements.txt` was prepared:** an unfiltered Colab `pip freeze` listed 646 environment-wide packages. Instead, project notebook imports were scanned dynamically and their installed versions selected from that `pip freeze` output, excluding unrelated Colab packages and replacing the platform-specific PyTorch wheel URL with a standard package version. This is a **direct-dependency snapshot**, not a full environment lockfile, and a fresh local installation with these exact pins has not been independently validated.

### Standalone comparison notebook

The original [`04_algorithm_comparison.ipynb`](notebooks/04_algorithm_comparison.ipynb) is retained. To use it separately, clone/download the full repository, set the working directory to the repository root or `notebooks/`, and execute the notebook in order. It reads the saved CSV outputs rather than retraining and generates cross-agent tables, learning curves, generalisation plots, robustness and uncertainty analyses under `outputs/comparison/`.

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
