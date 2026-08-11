from engine.grid import Grid
from engine.probability_map import ProbabilityMap
from engine.sonar_model import SonarModel


def _pm(**kwargs: object) -> ProbabilityMap:
    defaults: dict[str, object] = dict(
        grid=Grid(rows=20, cols=20),
        spawn_min_dist=2,
        spawn_max_dist=6,
        floor=1e-6,
    )
    defaults.update(kwargs)
    return ProbabilityMap(**defaults)  # type: ignore[arg-type]


def _uniform_pm(**kwargs: object) -> ProbabilityMap:
    # spawn bands placed out of grid range so every cell falls back to `floor`.
    defaults: dict[str, object] = dict(
        grid=Grid(rows=10, cols=10),
        spawn_min_dist=100,
        spawn_max_dist=100,
        floor=1e-6,
    )
    defaults.update(kwargs)
    return ProbabilityMap(**defaults)  # type: ignore[arg-type]


def _sm(**kwargs: object) -> SonarModel:
    defaults: dict[str, object] = dict(
        range_cells=8,
        half_angle_deg=60.0,
        lambda_decay=0.3,
        quiet_factor=0.2,
        max_attention=2.0,
        attention_rate=0.25,
    )
    defaults.update(kwargs)
    return SonarModel(**defaults)  # type: ignore[arg-type]


def test_diffuse_preserves_sum_to_one() -> None:
    pm = _pm()
    pm.diffuse()
    assert abs(float(pm.values.sum()) - 1.0) < 1e-9


def test_diffuse_preserves_shape() -> None:
    grid = Grid(rows=20, cols=15)
    pm = _pm(grid=grid)
    pm.diffuse()
    assert pm.values.shape == (grid.rows, grid.cols)


def test_diffuse_nonnegative() -> None:
    pm = _pm()
    pm.diffuse()
    assert bool((pm.values >= 0.0).all())


def test_diffuse_spreads_spike_to_neighbors() -> None:
    pm = _pm()
    # a zero-range sonar can only ever "see" the drone's own cell, so a
    # detection collapses the whole map onto a single spike there.
    pm.update(
        sonar=_sm(range_cells=0),
        drone=(10, 10),
        heading=(0, 1),
        detected=True,
        vessel_moved=True,
        detection_streak=0,
    )
    assert pm.probability(10, 10) == 1.0

    pm.diffuse()

    assert pm.probability(10, 10) < 1.0
    assert pm.probability(9, 10) > 0.0


def test_diffuse_interior_cell_ends_up_above_corner_cell_from_uniform_prior() -> None:
    # Boundary cells have fewer neighbors to receive mass from, so starting
    # from a flat prior, an interior cell should end up strictly ahead of a
    # corner cell once diffusion (and the following renormalization) runs.
    pm = _uniform_pm()
    assert pm.probability(0, 0) == pm.probability(5, 5)  # sanity: flat prior

    pm.diffuse()

    assert pm.probability(5, 5) > pm.probability(0, 0)
