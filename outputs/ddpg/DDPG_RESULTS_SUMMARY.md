# DDPG experiment results

This file summarises Raina Shah's completed DDPG experiments using configuration fingerprint `7fc3978e1036c4192871625454e78e071d739b3e01762ebbe99108120866f282`.

## Completed experiment budget

- Tuning: four configurations × two seeds × 30,000 interactions = 240,000 interactions.
- Final training: five seeds × 100,000 interactions = 500,000 interactions.
- Reward sensitivity: two shortage weights × two seeds × 30,000 interactions = 120,000 interactions.
- Final-policy robustness: five seeds × nine one-at-a-time scenarios × four held-out seasons.
- Failed trials: zero.

Every 30,000-step run completed 28,500 gradient updates after the fixed 1,500-step random-exploration period. Every 100,000-step run completed 98,500 updates.

## Validation-only tuning

| Rank | Learning rate | Exploration SD | Mean validation discounted return | Mean irrigation (mm) |
|---:|---:|---:|---:|---:|
| 1 | 0.0003 | 0.1 | -22.205 | 640.26 |
| 2 | 0.0003 | 0.2 | -22.869 | 638.28 |
| 3 | 0.0001 | 0.1 | -23.152 | 658.21 |
| 4 | 0.0001 | 0.2 | -24.086 | 651.20 |

The first configuration was selected before the 2021–2024 test results were examined.

## Held-out test results

The DDPG values are means across the five seed-level means, with sample SD across seeds where shown. The threshold controller is deterministic and is averaged across the four test seasons.

| Policy | Discounted return | Irrigation (mm) | Days below target | Shortage (mm-days) | Drainage (mm) |
|---|---:|---:|---:|---:|---:|
| DDPG | -21.041 ± 0.435 | 600.95 ± 9.76 | 0.30 ± 0.41 | 0.49 ± 0.91 | 38.01 ± 4.90 |
| Threshold controller | -21.488 | 615.00 | 1.50 | 4.51 | 32.10 |

DDPG's mean return was 0.447 higher (less negative), with 14.05 mm less irrigation and fewer target-range violations. It also produced 5.91 mm more drainage. This supports a small improvement under the declared simulator and reward, not field superiority.

## Learning behaviour

- The across-seed mean curve met the predeclared stability rule over its final five checkpoints.
- Four of five individual seeds met the rule; seed 11 narrowly missed it.
- The mean curve first stayed above the threshold-controller validation return for three consecutive checkpoints beginning at 5,000 interactions.
- This is an operational benchmark-crossing measure, not proof of mathematical convergence.

## Reward sensitivity

| Shortage weight | Discounted return | Nominally rescored return | Irrigation (mm) | Days below target | Shortage (mm-days) | Drainage (mm) |
|---:|---:|---:|---:|---:|---:|---:|
| 5 | -22.321 | -33.832 | 640.42 | 0.50 | 0.96 | 33.40 |
| 20 | -24.311 | -36.953 | 686.51 | 0.00 | 0.00 | 52.56 |

The higher shortage weight removed dry days in these validation runs but increased irrigation and drainage. This confirms that physical behaviour depends on the reward weights.

## Robustness highlights

The most difficult one-at-a-time scenarios by mean discounted return were `kc_1.1` (-23.789), `root_zone_0.6m` (-23.737) and `efficiency_0.75` (-23.317). The easier scenarios were `kc_0.9` (-18.446) and `efficiency_0.95` (-19.241). These tests vary selected simulator assumptions and do not establish geographic transfer.

## Limitations

The experiment uses one simulated Kyabram field, historical weather, four test seasons and five seeds. The threshold controller was not separately optimised. The policy may exploit simulator-specific relationships, and no measured crop yield or field deployment was evaluated. Final conclusions about relative algorithm performance require TD3 and SAC to use the same data, fingerprint, budgets and evaluation rules.

