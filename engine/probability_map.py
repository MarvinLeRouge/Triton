from __future__ import annotations

import numpy as np
import numpy.typing as npt

from engine.grid import Grid


class ProbabilityMap:
    """1:1 probability-of-presence map over the grid.

    Bayesian updates and temporal diffusion are added in later Phase 3
    branches; this class currently exposes only the informed prior.
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
