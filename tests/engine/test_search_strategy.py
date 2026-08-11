from engine.grid import Grid
from engine.probability_map import ProbabilityMap
from engine.search_strategy import FrontierCoverage, GreedyMaxProbability


def _pm(grid: Grid) -> ProbabilityMap:
    # spawn bands placed out of grid range so every cell falls back to a
    # uniform `floor` prior — a clean baseline for controlled test fixtures.
    return ProbabilityMap(grid, spawn_min_dist=100, spawn_max_dist=100)


# ---------------------------------------------------------------------------
# GreedyMaxProbability
# ---------------------------------------------------------------------------


def test_greedy_moves_toward_highest_probability_reachable_cell() -> None:
    grid = Grid(rows=10, cols=10)
    pm = _pm(grid)
    pm.values[5, 7] = 0.9  # within reach (speed=2 from (5,5))
    strategy = GreedyMaxProbability()
    target = strategy.next_target(position=(5, 5), speed=2, grid=grid, probability_map=pm)
    assert target == (5, 7)


def test_greedy_ignores_unreachable_peak() -> None:
    grid = Grid(rows=10, cols=10)
    pm = _pm(grid)
    pm.values[0, 0] = 0.9  # far outside reach
    pm.values[5, 6] = 0.5  # reachable, best available
    strategy = GreedyMaxProbability()
    target = strategy.next_target(position=(5, 5), speed=2, grid=grid, probability_map=pm)
    assert target == (5, 6)


def test_greedy_tie_break_prefers_closest_cell() -> None:
    grid = Grid(rows=10, cols=10)
    pm = _pm(grid)
    pm.values[3, 5] = 0.5  # distance 2
    pm.values[4, 5] = 0.5  # distance 1, tied on probability
    strategy = GreedyMaxProbability()
    target = strategy.next_target(position=(5, 5), speed=2, grid=grid, probability_map=pm)
    assert target == (4, 5)


def test_greedy_respects_grid_bounds() -> None:
    grid = Grid(rows=10, cols=10)
    pm = _pm(grid)
    strategy = GreedyMaxProbability()
    target = strategy.next_target(position=(0, 0), speed=2, grid=grid, probability_map=pm)
    assert grid.in_bounds(*target)


# ---------------------------------------------------------------------------
# FrontierCoverage
# ---------------------------------------------------------------------------


def test_frontier_prefers_nearest_above_mean_cell_over_farther_higher_peak() -> None:
    grid = Grid(rows=10, cols=10)
    pm = _pm(grid)
    mean = float(pm.values.mean())
    pm.values[5, 7] = mean + 0.5  # farther (distance 2), well above mean
    pm.values[5, 6] = mean + 0.01  # closer (distance 1), just above mean
    strategy = FrontierCoverage()
    target = strategy.next_target(position=(5, 5), speed=2, grid=grid, probability_map=pm)
    assert target == (5, 6)


def test_frontier_falls_back_to_max_reachable_when_none_above_mean() -> None:
    grid = Grid(rows=10, cols=10)
    pm = _pm(grid)
    pm.values[0, 0] = 50.0  # far outside reach, drags the grid mean well above any reachable cell
    pm.values[5, 6] = 0.02  # best among reachable, but still below the inflated mean
    pm.values[5, 7] = 0.015
    strategy = FrontierCoverage()
    target = strategy.next_target(position=(5, 5), speed=2, grid=grid, probability_map=pm)
    assert target == (5, 6)


def test_frontier_respects_grid_bounds() -> None:
    grid = Grid(rows=10, cols=10)
    pm = _pm(grid)
    strategy = FrontierCoverage()
    target = strategy.next_target(position=(0, 0), speed=2, grid=grid, probability_map=pm)
    assert grid.in_bounds(*target)
