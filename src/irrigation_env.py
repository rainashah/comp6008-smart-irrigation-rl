"""Gymnasium environment for the Kyabram smart-irrigation experiment.

The agent acts before observing the current day's realised rainfall and ETo.
Each action advances the daily soil-water balance by exactly one day and emits
the reward and next 18-element observation.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .experiment_config import ENV_CONFIG, SEASON_SPLITS, EnvironmentConfig


DEFAULT_ARCHIVE = Path(__file__).resolve().parents[1] / "data" / "Irrigation_Data_Audit.zip"
KYABRAM_ARCHIVE_MEMBER = "irrigation_audit/kyabram_080091_daily.json"


class KyabramIrrigationEnv(gym.Env[np.ndarray, np.ndarray]):
    """Daily single-reservoir irrigation environment.

    Parameters
    ----------
    climate_path:
        Path to ``kyabram_080091_daily.json``, the audit ZIP containing that
        file, or a directory containing the JSON.  If omitted, the environment
        looks for ``data/Irrigation_Data_Audit.zip`` in the repository root.
    split:
        One of ``train``, ``validation``, ``test`` or ``all``.  A reset samples
        complete seasons uniformly from the selected split.
    config:
        Shared environment configuration.  Scenario changes should be supplied
        through a new immutable ``EnvironmentConfig`` instance.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        climate_path: str | Path | None = None,
        *,
        split: str = "train",
        config: EnvironmentConfig = ENV_CONFIG,
    ) -> None:
        super().__init__()

        if split not in SEASON_SPLITS:
            raise ValueError(
                f"Unknown split {split!r}; expected one of {tuple(SEASON_SPLITS)}"
            )

        self.config = config
        self.split = split
        self.allowed_years = SEASON_SPLITS[split]
        self._records = self._load_records(climate_path)
        self._weather, self._dates = self._build_seasons(self._records)

        self.action_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(1,),
            dtype=np.float32,
        )
        self.observation_space = spaces.Box(
            low=np.zeros(18, dtype=np.float32),
            high=np.array(
                [1.0, 1.0, 1.1, 1.0] + [np.inf] * 14,
                dtype=np.float32,
            ),
            dtype=np.float32,
        )

        self.season_year: int | None = None
        self.day = self.config.season_length_days
        self.storage_mm = 0.0
        self.previous_irrigation_mm = 0.0
        self._terminated = True

    @staticmethod
    def _read_json_bytes(path: Path) -> bytes:
        if path.is_dir():
            path = path / "kyabram_080091_daily.json"
        if not path.exists():
            raise FileNotFoundError(
                f"Climate data not found at {path}. Pass the Kyabram JSON or "
                "the data/Irrigation_Data_Audit.zip path."
            )
        if path.suffix.lower() == ".zip":
            with ZipFile(path) as archive:
                try:
                    return archive.read(KYABRAM_ARCHIVE_MEMBER)
                except KeyError as exc:
                    raise ValueError(
                        f"{path} does not contain {KYABRAM_ARCHIVE_MEMBER}"
                    ) from exc
        return path.read_bytes()

    def _load_records(self, climate_path: str | Path | None) -> dict[date, tuple[float, float]]:
        path = DEFAULT_ARCHIVE if climate_path is None else Path(climate_path)
        try:
            payload = json.loads(self._read_json_bytes(path))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid climate JSON in {path}") from exc

        if not isinstance(payload, list):
            raise ValueError("Expected the climate JSON root to be a list")

        records: dict[date, tuple[float, float]] = {}
        for index, row in enumerate(payload):
            try:
                row_date = date.fromisoformat(row["date"])
                rain = float(row["rain_mm"])
                eto = float(row["eto_mm"])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Malformed climate row at index {index}") from exc
            if row_date in records:
                raise ValueError(f"Duplicate climate date: {row_date.isoformat()}")
            if not np.isfinite(rain) or not np.isfinite(eto):
                raise ValueError(f"Non-finite climate input on {row_date.isoformat()}")
            if rain < 0 or eto < 0:
                raise ValueError(f"Negative climate input on {row_date.isoformat()}")
            records[row_date] = (rain, eto)

        return records

    def _build_seasons(
        self,
        records: dict[date, tuple[float, float]],
    ) -> tuple[dict[int, np.ndarray], dict[int, tuple[date, ...]]]:
        weather: dict[int, np.ndarray] = {}
        dates: dict[int, tuple[date, ...]] = {}
        block_days = self.config.history_days + self.config.season_length_days

        for year in SEASON_SPLITS["all"]:
            planting = date(
                year,
                self.config.planting_month,
                self.config.planting_day,
            ) + timedelta(days=self.config.planting_day_offset)
            block_start = planting - timedelta(days=self.config.history_days)
            block_dates = tuple(
                block_start + timedelta(days=offset) for offset in range(block_days)
            )
            missing = [day for day in block_dates if day not in records]
            if missing:
                raise ValueError(
                    f"Season {year} is incomplete; first missing date is "
                    f"{missing[0].isoformat()}"
                )
            values = np.asarray([records[day] for day in block_dates], dtype=np.float64)
            if values.shape != (block_days, 2) or not np.isfinite(values).all():
                raise ValueError(f"Invalid assembled weather block for season {year}")
            weather[year] = values
            dates[year] = block_dates

        return weather, dates

    def _kc(self, day: int) -> float:
        if day >= self.config.season_length_days:
            return 0.0
        if day < 30:
            base = 0.30
        elif day < 70:
            base = 0.30 + 0.90 * (day - 29) / 40
        elif day < 120:
            base = 1.20
        else:
            base = 1.20 - 0.85 * (day - 119) / 30
        return self.config.kc_multiplier * base

    def _observation(self) -> np.ndarray:
        if self.season_year is None:
            raise RuntimeError("Call reset() before requesting an observation")

        history_start = self.day
        history_end = history_start + self.config.history_days
        history = self._weather[self.season_year][history_start:history_end][::-1]
        if history.shape != (self.config.history_days, 2):
            raise RuntimeError("Weather history window has an unexpected shape")

        observation = np.concatenate(
            (
                np.asarray(
                    [
                        self.storage_mm / self.config.capacity_mm,
                        self.day / self.config.season_length_days,
                        self._kc(self.day) / 1.2,
                        self.previous_irrigation_mm / self.config.max_irrigation_mm,
                    ],
                    dtype=np.float64,
                ),
                history[:, 0] / self.config.rainfall_scale_mm,
                history[:, 1] / self.config.eto_scale_mm,
            )
        ).astype(np.float32)

        if observation.shape != (18,) or not np.isfinite(observation).all():
            raise RuntimeError("Environment produced an invalid observation")
        if not self.observation_space.contains(observation):
            raise RuntimeError("Environment produced an observation outside its space")
        return observation

    def _current_decision_date(self) -> date | None:
        if self.season_year is None or self.day >= self.config.season_length_days:
            return None
        return self._dates[self.season_year][self.config.history_days + self.day]

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        super().reset(seed=seed)
        options = {} if options is None else dict(options)
        unknown_options = set(options) - {"season_year"}
        if unknown_options:
            raise ValueError(f"Unknown reset options: {sorted(unknown_options)}")

        requested_year = options.get("season_year")
        if requested_year is None:
            year_index = int(self.np_random.integers(len(self.allowed_years)))
            self.season_year = self.allowed_years[year_index]
        else:
            requested_year = int(requested_year)
            if requested_year not in self.allowed_years:
                raise ValueError(
                    f"Season {requested_year} is not in the {self.split!r} split"
                )
            self.season_year = requested_year

        self.day = 0
        self.storage_mm = (
            self.config.initial_storage_fraction * self.config.capacity_mm
        )
        self.previous_irrigation_mm = 0.0
        self._terminated = False

        info = {
            "split": self.split,
            "season_year": self.season_year,
            "day": self.day,
            "decision_date": self._current_decision_date().isoformat(),
            "capacity_mm": self.config.capacity_mm,
        }
        return self._observation(), info

    def step(
        self,
        action: np.ndarray,
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        if self._terminated or self.season_year is None:
            raise RuntimeError("Episode has ended; call reset() before step()")

        action_array = np.asarray(action, dtype=np.float32)
        if action_array.size != 1:
            raise ValueError("Expected exactly one normalised irrigation action")
        action_array = action_array.reshape(1)
        if not self.action_space.contains(action_array):
            raise ValueError("Action must be finite and within [-1, 1]")

        normalised_action = float(action_array[0])
        irrigation_mm = 0.5 * self.config.max_irrigation_mm * (
            normalised_action + 1.0
        )

        decision_date = self._current_decision_date()
        weather_index = self.config.history_days + self.day
        rain_mm, eto_mm = self._weather[self.season_year][weather_index]
        kc = self._kc(self.day)
        potential_et_mm = kc * float(eto_mm)
        depletion_fraction = float(
            np.clip(0.55 + 0.04 * (5.0 - potential_et_mm), 0.1, 0.8)
        )
        minimum_storage_mm = (1.0 - depletion_fraction) * self.config.capacity_mm

        storage_before_mm = self.storage_mm
        incoming_storage_mm = (
            storage_before_mm
            + float(rain_mm)
            + self.config.irrigation_efficiency * irrigation_mm
        )
        drainage_mm = max(0.0, incoming_storage_mm - self.config.capacity_mm)
        wet_storage_mm = incoming_storage_mm - drainage_mm
        stress_coefficient = min(1.0, wet_storage_mm / minimum_storage_mm)
        actual_et_mm = min(
            wet_storage_mm,
            stress_coefficient * potential_et_mm,
        )
        storage_after_mm = wet_storage_mm - actual_et_mm
        shortage_mm = max(0.0, minimum_storage_mm - storage_after_mm)

        irrigation_penalty = (
            self.config.irrigation_weight
            * irrigation_mm
            / self.config.max_irrigation_mm
        )
        shortage_penalty = (
            self.config.shortage_weight * shortage_mm / minimum_storage_mm
        )
        drainage_penalty = (
            self.config.drainage_weight
            * drainage_mm
            / self.config.max_irrigation_mm
        )
        reward = -(irrigation_penalty + shortage_penalty + drainage_penalty)

        self.storage_mm = storage_after_mm
        self.previous_irrigation_mm = irrigation_mm
        self.day += 1
        self._terminated = self.day == self.config.season_length_days

        balance_residual_mm = storage_after_mm - (
            storage_before_mm
            + float(rain_mm)
            + self.config.irrigation_efficiency * irrigation_mm
            - drainage_mm
            - actual_et_mm
        )
        info = {
            "split": self.split,
            "season_year": self.season_year,
            "completed_day": self.day,
            "decision_date": decision_date.isoformat() if decision_date else None,
            "normalised_action": normalised_action,
            "irrigation_mm": irrigation_mm,
            "rain_mm": float(rain_mm),
            "eto_mm": float(eto_mm),
            "kc": kc,
            "potential_et_mm": potential_et_mm,
            "actual_et_mm": actual_et_mm,
            "stress_coefficient": stress_coefficient,
            "depletion_fraction": depletion_fraction,
            "minimum_storage_mm": minimum_storage_mm,
            "storage_before_mm": storage_before_mm,
            "storage_after_mm": storage_after_mm,
            "shortage_mm": shortage_mm,
            "drainage_mm": drainage_mm,
            "irrigation_penalty": irrigation_penalty,
            "shortage_penalty": shortage_penalty,
            "drainage_penalty": drainage_penalty,
            "balance_residual_mm": balance_residual_mm,
        }

        return self._observation(), float(reward), self._terminated, False, info

