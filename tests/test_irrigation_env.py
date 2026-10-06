"""Consistency tests for the shared Kyabram irrigation environment."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from gymnasium.utils.env_checker import check_env

from src import EnvironmentConfig, KyabramIrrigationEnv


ROOT = Path(__file__).resolve().parents[1]


def climate_path() -> Path:
    """Find the audit archive in either a clone or this working directory."""

    candidates = (
        ROOT / "data" / "Irrigation_Data_Audit.zip",
        ROOT / "Irrigation_Data_Audit.zip",
        ROOT / "irrigation_audit" / "kyabram_080091_daily.json",
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Kyabram audit data is not available for the tests")


@pytest.fixture()
def env() -> KyabramIrrigationEnv:
    return KyabramIrrigationEnv(climate_path(), split="train")


def test_gymnasium_api(env: KyabramIrrigationEnv) -> None:
    # Infinite weather upper bounds deliberately produce one checker warning.
    with pytest.warns(UserWarning, match="infinity"):
        check_env(env, skip_render_check=True)


def test_reset_is_reproducible_and_observation_is_valid(
    env: KyabramIrrigationEnv,
) -> None:
    first_observation, first_info = env.reset(seed=11)
    second_observation, second_info = env.reset(seed=11)

    np.testing.assert_array_equal(first_observation, second_observation)
    assert first_info["season_year"] == second_info["season_year"]
    assert first_observation.shape == (18,)
    assert first_observation.dtype == np.float32
    assert env.observation_space.contains(first_observation)
    np.testing.assert_allclose(first_observation[:4], [0.8, 0.0, 0.25, 0.0])


@pytest.mark.parametrize(
    ("split", "year"),
    (("train", 2005), ("validation", 2017), ("test", 2021)),
)
def test_each_split_accepts_only_its_own_seasons(split: str, year: int) -> None:
    split_env = KyabramIrrigationEnv(climate_path(), split=split)
    _, info = split_env.reset(options={"season_year": year})
    assert info["season_year"] == year

    wrong_year = 2021 if split != "test" else 2005
    with pytest.raises(ValueError, match="is not in"):
        split_env.reset(options={"season_year": wrong_year})


def test_action_mapping_and_weather_history_timing(env: KyabramIrrigationEnv) -> None:
    initial, _ = env.reset(options={"season_year": 2005})
    next_observation, _, _, _, info = env.step(np.array([-1.0], dtype=np.float32))

    assert info["irrigation_mm"] == pytest.approx(0.0)
    assert next_observation[4] * 20.0 == pytest.approx(info["rain_mm"])
    assert next_observation[11] * 10.0 == pytest.approx(info["eto_mm"])
    np.testing.assert_allclose(next_observation[5:11], initial[4:10])
    np.testing.assert_allclose(next_observation[12:18], initial[11:17])

    env.reset(options={"season_year": 2005})
    _, _, _, _, info = env.step(np.array([1.0], dtype=np.float32))
    assert info["irrigation_mm"] == pytest.approx(20.0)


@pytest.mark.parametrize(
    "action",
    (
        np.array([-1.01], dtype=np.float32),
        np.array([1.01], dtype=np.float32),
        np.array([np.nan], dtype=np.float32),
        np.array([0.0, 0.0], dtype=np.float32),
    ),
)
def test_invalid_actions_are_rejected(
    env: KyabramIrrigationEnv,
    action: np.ndarray,
) -> None:
    env.reset(options={"season_year": 2005})
    with pytest.raises(ValueError):
        env.step(action)


def test_one_transition_matches_the_declared_equations(
    env: KyabramIrrigationEnv,
) -> None:
    env.reset(options={"season_year": 2005})
    action = np.array([0.25], dtype=np.float32)
    _, reward, _, _, info = env.step(action)

    irrigation = 10.0 * (float(action[0]) + 1.0)
    crop_demand = info["kc"] * info["eto_mm"]
    depletion = np.clip(0.55 + 0.04 * (5.0 - crop_demand), 0.1, 0.8)
    minimum = (1.0 - depletion) * env.config.capacity_mm
    incoming = (
        info["storage_before_mm"]
        + info["rain_mm"]
        + env.config.irrigation_efficiency * irrigation
    )
    drainage = max(0.0, incoming - env.config.capacity_mm)
    wet_storage = incoming - drainage
    stress = min(1.0, wet_storage / minimum)
    actual_et = min(wet_storage, stress * crop_demand)
    storage_after = wet_storage - actual_et
    shortage = max(0.0, minimum - storage_after)
    expected_reward = -(
        irrigation / 20.0 + 10.0 * shortage / minimum + drainage / 20.0
    )

    assert info["storage_after_mm"] == pytest.approx(storage_after)
    assert info["balance_residual_mm"] == pytest.approx(0.0, abs=1e-12)
    assert reward == pytest.approx(expected_reward)


def test_complete_episode_terminates_on_day_150(env: KyabramIrrigationEnv) -> None:
    env.reset(options={"season_year": 2005})
    max_residual = 0.0

    for step in range(150):
        observation, reward, terminated, truncated, info = env.step(
            np.array([0.0], dtype=np.float32)
        )
        assert env.observation_space.contains(observation)
        assert np.isfinite(reward) and reward <= 0.0
        assert not truncated
        assert terminated is (step == 149)
        max_residual = max(max_residual, abs(info["balance_residual_mm"]))

    assert observation[1] == pytest.approx(1.0)
    assert observation[2] == pytest.approx(0.0)
    assert max_residual < 1e-10
    with pytest.raises(RuntimeError, match="Episode has ended"):
        env.step(np.array([0.0], dtype=np.float32))


def test_scenario_configuration_changes_capacity() -> None:
    scenario = EnvironmentConfig(capacity_mm=72.0)
    scenario_env = KyabramIrrigationEnv(
        climate_path(),
        split="test",
        config=scenario,
    )
    observation, info = scenario_env.reset(options={"season_year": 2021})

    assert info["capacity_mm"] == pytest.approx(72.0)
    assert scenario_env.storage_mm == pytest.approx(57.6)
    assert observation[0] == pytest.approx(0.8)
