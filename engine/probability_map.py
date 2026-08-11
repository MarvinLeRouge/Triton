from __future__ import annotations

import math

import numpy as np
import numpy.typing as npt

from engine.grid import Grid
from engine.sonar_model import SonarModel


class ProbabilityMap:
    """1:1 probability-of-presence map over the grid."""

    def __init__(
        self,
        grid: Grid,
        spawn_min_dist: int = 2,
        spawn_max_dist: int = 6,
        floor: float = 1e-6,
    ) -> None:
        self._grid = grid
        self._values = self._informed_prior(grid, spawn_min_dist, spawn_max_dist, floor)

    @property
    def values(self) -> npt.NDArray[np.float64]:
        return self._values

    def probability(self, row: int, col: int) -> float:
        """Return the probability mass at (row, col)."""
        return float(self._values[row, col])

    def update(
        self,
        sonar: SonarModel,
        drone: tuple[int, int],
        heading: tuple[int, int],
        detected: bool,
        vessel_moved: bool,
        detection_streak: int,
    ) -> None:
        """Bayesian update from one drone's sonar sweep outcome (detected / not detected).

        A positive detection can only originate from within the drone's cone,
        so cells outside it become impossible (likelihood 0) when detected is
        True. A negative sweep carries no information about cells outside the
        cone (likelihood 1). The drone's own cell is certain (pod=1.0),
        mirroring SonarModel.try_detect's generative process.
        """
        rows, cols = self._values.shape
        likelihood = np.full((rows, cols), 0.0 if detected else 1.0, dtype=np.float64)
        for row in range(rows):
            for col in range(cols):
                if not sonar.in_cone(drone, heading, (row, col)):
                    continue
                if (row, col) == drone:
                    pod = 1.0
                else:
                    dist = math.hypot(row - drone[0], col - drone[1])
                    pod = sonar.pod(dist, vessel_moved, detection_streak)
                likelihood[row, col] = pod if detected else (1.0 - pod)

        posterior = self._values * likelihood
        total = posterior.sum()
        if total > 0:
            self._values = posterior / total

    def diffuse(self, stay_weight: float = 0.6) -> None:
        """Spread probability mass to the 8 neighboring cells for one turn elapsed.

        Models RedVessel's possible movement since the last sonar sweep: each
        cell keeps `stay_weight` of its mass, the rest is split evenly across
        its in-bounds neighbors. Mass that would fall outside the grid is
        dropped and recovered by the final renormalization.
        """
        rows, cols = self._values.shape
        neighbor_weight = (1.0 - stay_weight) / 8.0
        padded = np.pad(self._values, 1, mode="constant", constant_values=0.0)

        diffused = stay_weight * self._values
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                diffused += neighbor_weight * padded[1 + dr : 1 + dr + rows, 1 + dc : 1 + dc + cols]

        total = diffused.sum()
        if total > 0:
            diffused /= total
        self._values = diffused

    @staticmethod
    def _informed_prior(
        grid: Grid, spawn_min_dist: int, spawn_max_dist: int, floor: float
    ) -> npt.NDArray[np.float64]:
        """Weight RedVessel's north/east/south spawn bands, `floor` everywhere else."""
        weights = np.full((grid.rows, grid.cols), floor, dtype=np.float64)
        rows = np.arange(grid.rows)[:, None]
        cols = np.arange(grid.cols)[None, :]

        north = (rows >= spawn_min_dist) & (rows <= spawn_max_dist)
        south = (rows >= grid.rows - 1 - spawn_max_dist) & (rows <= grid.rows - 1 - spawn_min_dist)
        east = (cols >= grid.cols - 1 - spawn_max_dist) & (cols <= grid.cols - 1 - spawn_min_dist)

        weights[north | south | east] += 1.0
        weights /= weights.sum()
        return weights
