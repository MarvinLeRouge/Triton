import numpy as np

from engine.grid import Grid
from engine.probability_map import ProbabilityMap


def _pm(**kwargs: object) -> ProbabilityMap:
    defaults: dict[str, object] = dict(
        grid=Grid(rows=20, cols=20),
        spawn_min_dist=2,
        spawn_max_dist=6,
        floor=1e-6,
    )
    defaults.update(kwargs)
    return ProbabilityMap(**defaults)  # type: ignore[arg-type]


def test_values_shape_matches_grid() -> None:
    grid = Grid(rows=20, cols=15)
    pm = _pm(grid=grid)
    assert pm.values.shape == (grid.rows, grid.cols)


def test_values_sum_to_one() -> None:
    pm = _pm()
    assert abs(float(pm.values.sum()) - 1.0) < 1e-9


def test_values_nonnegative() -> None:
    pm = _pm()
    assert bool((pm.values >= 0.0).all())


def test_no_cell_has_zero_probability() -> None:
    # A floor keeps every cell reachable by future Bayesian updates.
    pm = _pm()
    assert bool((pm.values > 0.0).all())


def test_probability_returns_value_at_cell() -> None:
    pm = _pm()
    assert pm.probability(0, 0) == float(pm.values[0, 0])


def test_north_spawn_band_has_higher_probability_than_west_zone() -> None:
    # North band: rows [spawn_min_dist, spawn_max_dist], any column.
    pm = _pm()
    band_cell = pm.probability(4, 10)
    west_zone_cell = pm.probability(10, 4)  # Blue mothership territory, outside all bands
    assert band_cell > west_zone_cell


def test_south_spawn_band_has_higher_probability_than_west_zone() -> None:
    grid = Grid(rows=20, cols=20)
    pm = _pm(grid=grid)
    band_cell = pm.probability(grid.rows - 1 - 4, 10)
    west_zone_cell = pm.probability(10, 4)
    assert band_cell > west_zone_cell


def test_east_spawn_band_has_higher_probability_than_west_zone() -> None:
    grid = Grid(rows=20, cols=20)
    pm = _pm(grid=grid)
    band_cell = pm.probability(10, grid.cols - 1 - 4)
    west_zone_cell = pm.probability(10, 4)
    assert band_cell > west_zone_cell


def test_band_cells_have_uniform_probability() -> None:
    pm = _pm()
    assert pm.probability(3, 5) == pm.probability(6, 15)


def test_replace_values_updates_the_map() -> None:
    pm = _pm()
    new_values = pm.values.copy()
    new_values[0, 0] = 0.9
    pm.replace_values(new_values)
    assert pm.probability(0, 0) == 0.9


def test_replace_values_reflected_in_values_property() -> None:
    pm = _pm()
    new_values = pm.values.copy()
    new_values[3, 4] = 0.5
    pm.replace_values(new_values)
    assert pm.values[3, 4] == 0.5


def test_replace_values_does_not_alias_the_input_array() -> None:
    pm = _pm()
    shared = np.zeros((pm.values.shape[0], pm.values.shape[1]))
    pm.replace_values(shared)
    shared[0, 0] = 42.0
    assert pm.values[0, 0] != 42.0
