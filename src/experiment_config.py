"""Shared experiment settings and agent-specific configuration placeholders.

Environment settings in this module are fixed for the main comparison.  The
``SELECTED_AGENT_SETTINGS`` entries intentionally remain ``None`` until the
declared validation-only tuning procedure has been completed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


TRAIN_YEARS: Final[tuple[int, ...]] = tuple(range(2005, 2017))
VALIDATION_YEARS: Final[tuple[int, ...]] = tuple(range(2017, 2021))
TEST_YEARS: Final[tuple[int, ...]] = tuple(range(2021, 2025))

SEASON_SPLITS: Final[dict[str, tuple[int, ...]]] = {
    "train": TRAIN_YEARS,
    "validation": VALIDATION_YEARS,
    "test": TEST_YEARS,
    "all": TRAIN_YEARS + VALIDATION_YEARS + TEST_YEARS,
}


@dataclass(frozen=True)
class EnvironmentConfig:
    """Configuration of the daily Kyabram soil-water environment."""

    capacity_mm: float = 111.33333333333334
    initial_storage_fraction: float = 0.80
    max_irrigation_mm: float = 20.0
    irrigation_efficiency: float = 0.85
    season_length_days: int = 150
    planting_month: int = 11
    planting_day: int = 1
    planting_day_offset: int = 0
    kc_multiplier: float = 1.0
    irrigation_weight: float = 1.0
    shortage_weight: float = 10.0
    drainage_weight: float = 1.0
    rainfall_scale_mm: float = 20.0
    eto_scale_mm: float = 10.0
    history_days: int = 7

    def __post_init__(self) -> None:
        if self.capacity_mm <= 0:
            raise ValueError("capacity_mm must be positive")
        if not 0 < self.initial_storage_fraction <= 1:
            raise ValueError("initial_storage_fraction must be in (0, 1]")
        if self.max_irrigation_mm <= 0:
            raise ValueError("max_irrigation_mm must be positive")
        if not 0 < self.irrigation_efficiency <= 1:
            raise ValueError("irrigation_efficiency must be in (0, 1]")
        if self.season_length_days != 150:
            raise ValueError("The fixed main experiment uses 150 daily decisions")
        if self.history_days != 7:
            raise ValueError("The fixed observation uses seven completed days")
        if not 0 < self.kc_multiplier <= 1.1:
            raise ValueError("kc_multiplier must be in (0, 1.1]")
        if min(
            self.irrigation_weight,
            self.shortage_weight,
            self.drainage_weight,
        ) < 0:
            raise ValueError("Reward weights must be non-negative")
        if self.rainfall_scale_mm <= 0 or self.eto_scale_mm <= 0:
            raise ValueError("Weather scales must be positive")


@dataclass(frozen=True)
class TrainingConfig:
    """Settings shared by DDPG, TD3 and SAC."""

    gamma: float = 0.995
    tau: float = 0.005
    replay_capacity: int = 100_000
    batch_size: int = 128
    random_exploration_steps: int = 1_500
    final_training_steps: int = 100_000
    tuning_steps: int = 30_000
    evaluation_interval: int = 5_000
    hidden_sizes: tuple[int, int] = (128, 128)
    optimiser_betas: tuple[float, float] = (0.9, 0.999)
    optimiser_epsilon: float = 1e-8
    updates_per_step: int = 1
    final_seeds: tuple[int, ...] = (11, 22, 33, 44, 55)
    tuning_seeds: tuple[int, ...] = (101, 202)


ENV_CONFIG: Final = EnvironmentConfig()
TRAINING_CONFIG: Final = TrainingConfig()


# These grids are fixed before tuning.  Selection uses validation seasons only.
AGENT_TUNING_GRIDS: Final[dict[str, dict[str, tuple[float, ...]]]] = {
    "ddpg": {
        "learning_rate": (1e-4, 3e-4),
        "exploration_std": (0.1, 0.2),
    },
    "td3": {
        "learning_rate": (1e-4, 3e-4),
        "exploration_std": (0.1, 0.2),
    },
    "sac": {
        "learning_rate": (1e-4, 3e-4),
        "alpha": (0.1, 0.2),
    },
}


# Fill only after validation-only tuning.  Do not use test-season performance.
# Agent owners fill these placeholders only after running the agreed tuning
# grid.  Keeping the selected values here prevents private defaults from
# silently changing the comparison.
SELECTED_AGENT_SETTINGS: dict[str, dict[str, object | None]] = {
    "ddpg": {
        "learning_rate": None,
        "exploration_std": None,
    },
    "td3": {
        "learning_rate": None,
        "exploration_std": None,
        "policy_delay": 2,
        "target_smoothing_std": 0.2,
        "target_noise_clip": 0.5,
    },
    "sac": {
        "learning_rate": None,
        "alpha": None,
        # Decide and document these implementation details before SAC training.
        "log_std_bounds": None,
    },
}
