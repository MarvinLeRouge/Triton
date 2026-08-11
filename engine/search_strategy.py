from __future__ import annotations

from abc import ABC, abstractmethod

from engine.grid import Grid
from engine.probability_map import ProbabilityMap


def _reachable_cells(position: tuple[int, int], speed: int, grid: Grid) -> list[tuple[int, int]]:
    row, col = position
    cells: list[tuple[int, int]] = []
    for dr in range(-speed, speed + 1):
        for dc in range(-speed, speed + 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            if grid.in_bounds(r, c):
                cells.append((r, c))
    return cells


def _chebyshev(a: tuple[int, int], b: tuple[int, int]) -> int:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


class SearchStrategy(ABC):
    """Decides a BlueDrone's next target cell for one turn."""

    @abstractmethod
    def next_target(
        self,
        position: tuple[int, int],
        speed: int,
        grid: Grid,
        probability_map: ProbabilityMap,
    ) -> tuple[int, int]:
        """Return the (row, col) cell the drone should move to this turn."""
        ...


class GreedyMaxProbability(SearchStrategy):
    """Moves toward the reachable cell with the highest probability of presence.

    Ties broken by proximity to the current position (least movement), then
    by (row, col) for full determinism.
    """

    def next_target(
        self,
        position: tuple[int, int],
        speed: int,
        grid: Grid,
        probability_map: ProbabilityMap,
    ) -> tuple[int, int]:
        candidates = _reachable_cells(position, speed, grid)
        return max(
            candidates,
            key=lambda c: (
                probability_map.probability(*c),
                -_chebyshev(position, c),
                -c[0],
                -c[1],
            ),
        )


class FrontierCoverage(SearchStrategy):
    """Moves toward the nearest reachable cell above the map's mean probability.

    Favors thorough local coverage over jumping straight to the global peak.
    Falls back to the highest-probability reachable cell when none clears
    the mean.
    """

    def next_target(
        self,
        position: tuple[int, int],
        speed: int,
        grid: Grid,
        probability_map: ProbabilityMap,
    ) -> tuple[int, int]:
        candidates = _reachable_cells(position, speed, grid)
        mean = float(probability_map.values.mean())
        above_mean = [c for c in candidates if probability_map.probability(*c) > mean]
        if above_mean:
            return min(
                above_mean,
                key=lambda c: (_chebyshev(position, c), c[0], c[1]),
            )
        return max(
            candidates,
            key=lambda c: (probability_map.probability(*c), -c[0], -c[1]),
        )
