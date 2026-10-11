# DDPG experiment results — Colab run

These results replace the earlier run and match Raina Shah’s uploaded executed notebook and output archive. The runtime and input hashes are recorded in `ddpg_run_manifest.json`.

## Completed work

- Eight tuning runs: four configurations × two seeds × 30,000 interactions; all eight saved checkpoints contain 28,500 updates.
- Five final runs: seeds 11, 22, 33, 44 and 55 × 100,000 interactions; all five saved checkpoints contain 98,500 updates.
- 32 tuning evaluation rows, 20 held-out test rows, 420 learning-curve rows, 180 robustness rows and 16 reward-sensitivity rows. All result rows report `ok`.
- Both farm replays are saved in the notebook. Its code cells have execution counts and no retained error outputs.

## Validation-only tuning

|   configuration_index | configuration                                     |   selection_score |   mean_irrigation_mm | valid   |
|----------------------:|:--------------------------------------------------|------------------:|---------------------:|:--------|
|                     2 | {'learning_rate': 0.0003, 'exploration_std': 0.1} |          -22.3231 |              641.438 | True    |
|                     3 | {'learning_rate': 0.0003, 'exploration_std': 0.2} |          -22.7861 |              648.546 | True    |
|                     1 | {'learning_rate': 0.0001, 'exploration_std': 0.2} |          -23.3383 |              654.669 | True    |
|                     0 | {'learning_rate': 0.0001, 'exploration_std': 0.1} |          -23.622  |              664.721 | True    |

The selected configuration is learning rate 0.0003 and exploration standard deviation 0.1. The uploaded final-training cell uses these same values.

## Held-out results

DDPG means are calculated across the five seed-level means; ± denotes sample SD across seeds.

| Policy | Discounted return | Irrigation (mm) | Days below target | Shortage (mm-days) | Drainage (mm) |
|---|---:|---:|---:|---:|---:|
| DDPG | -21.064 ± 0.316 | 601.87 ± 6.89 | 0.25 ± 0.18 | 0.58 ± 0.81 | 37.91 ± 3.77 |
| Threshold | -21.488 | 615.00 | 1.50 | 4.51 | 32.10 |

DDPG used 13.13 mm less irrigation on average and had fewer target violations, with 5.81 mm more drainage. Its return was 0.423 higher. These findings concern this simulator, not field superiority.

## Stability and sample efficiency

The mean learning curve and all five individual seeds met the declared operational stability rule. The mean curve first stayed above the threshold validation benchmark for three checkpoints starting at 5,000 interactions. Neither criterion proves mathematical convergence.

## Reward sensitivity

| scenario           |   discounted_return |   nominal_rescored_return |   irrigation_mm |   days_below_target |   shortage_mm_days |   drainage_mm |
|:-------------------|--------------------:|--------------------------:|----------------:|--------------------:|-------------------:|--------------:|
| shortage_weight_20 |             -23.549 |                   -35.747 |         669.758 |               0.125 |              0.016 |        45.113 |
| shortage_weight_5  |             -22.374 |                   -33.968 |         645.437 |               0.625 |              0.267 |        33.084 |

Increasing the shortage weight from 5 to 20 reduced dry days but increased irrigation and drainage. The higher weight did not eliminate all dry days. Separate sensitivity checkpoints were not supplied.

## Robustness

| scenario           |   discounted_return |
|:-------------------|--------------------:|
| kc_1.1             |             -24.182 |
| root_zone_0.6m     |             -23.710 |
| efficiency_0.75    |             -23.420 |
| planting_minus_14d |             -22.565 |
| capacity_0.8       |             -22.349 |
| planting_plus_14d  |             -20.356 |
| capacity_1.2       |             -20.120 |
| efficiency_0.95    |             -19.269 |
| kc_0.9             |             -18.283 |

These are one-at-a-time simulator perturbations, not geographic transfer tests. The study uses one virtual field, four test seasons and five seeds; the threshold controller was not separately optimised. Compare with TD3 and SAC only under the same shared experiment design.
