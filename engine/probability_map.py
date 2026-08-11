from __future__ import annotations

import math

import numpy as np
import numpy.typing as npt

from engine.grid import Grid
from engine.sonar_model import SonarModel


class ProbabilityMap:
    """1:1 probability-of-presence map over the grid.

    Temporal diffusion is added in a later Phase 3 branch.
    """

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
