# Shared irrigation environment

**Group implementation handoff — 6 October 2026.**

The shared Gymnasium environment is implemented in [`src/irrigation_env.py`](../src/irrigation_env.py). It follows the observation, action, transition, reward, split and terminal rules in [`FIXED_EXPERIMENT_SETTINGS.md`](FIXED_EXPERIMENT_SETTINGS.md). All three agents should import this class rather than create separate environment copies.

## Quick start

From the repository root:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

Create a training environment:

```python
import numpy as np

from src import KyabramIrrigationEnv

env = KyabramIrrigationEnv(split="train")
observation, info = env.reset(seed=11)

action = np.array([0.0], dtype=np.float32)  # maps to 10 mm irrigation
next_observation, reward, terminated, truncated, info = env.step(action)
```

The default loader reads `data/Irrigation_Data_Audit.zip` and uses the Kyabram SILO record inside it. A JSON path, archive path or directory can instead be passed as `climate_path`.

## Interface that must remain shared

| Item | Shared value |
|---|---|
| Observation | 18 `float32` values in the fixed documented order |
| Policy action | One `float32` value in $[-1,1]$ |
| Physical action | 0–20 mm/day, using $I_t=10(u_t+1)$ |
| Episode | 150 daily transitions |
| Training seasons | 2005–2016 |
| Validation seasons | 2017–2020 |
| Test seasons | 2021–2024 |
| Terminal handling | `terminated=True` after day 150; `truncated=False` |

Use `reset(options={"season_year": 2005})` when a specific season is needed for evaluation or debugging. A requested year must belong to the environment's selected split.

## Agent-specific placeholders

Shared training settings, tuning grids and the unfilled selections are in [`src/experiment_config.py`](../src/experiment_config.py). Each algorithm owner should implement their agent in a separate file, for example:

- `src/agents/ddpg.py`
- `src/agents/td3.py`
- `src/agents/sac.py`

The entries below deliberately remain `None` until validation-only tuning is finished:

| Agent | Placeholders to fill |
|---|---|
| DDPG | selected learning rate and exploration standard deviation |
| TD3 | selected learning rate and exploration standard deviation |
| SAC | selected learning rate, fixed entropy coefficient and documented log-standard-deviation bounds |

Do not fill these from test-season results. The selected values should be written once to `SELECTED_AGENT_SETTINGS`, with the validation result recorded in the experiment output.

Agent code may define private variables needed by its equations, but it must not change the environment, split, network size, replay capacity, batch size, discount factor, soft-update coefficient or interaction budgets.

## Parallel workflow

1. One member owns DDPG, one owns TD3 and one owns SAC.
2. Everyone imports the same environment and configuration module.
3. Use a shared transition record: `(observation, action, reward, next_observation, terminated)`.
4. Run the environment tests before merging agent changes.
5. Integrate each agent with a short smoke run before starting the declared tuning grid.
6. Save learning curves and episode metrics with agent, configuration, seed, split, season and interaction count.

## Current validation coverage

The automated tests check:

- the Gymnasium API;
- seeded reset reproducibility and chronological split enforcement;
- the normalised-to-physical action mapping;
- weather-history timing without future-weather leakage;
- rejection of invalid actions;
- one transition against an independent calculation of the equations;
- water-balance residuals, finite rewards and observations; and
- termination exactly after the 150th transition.

The expected Gymnasium warning about infinite weather-space upper bounds is retained deliberately because valid weather values are required to be finite but are not clipped using test-set maxima.
