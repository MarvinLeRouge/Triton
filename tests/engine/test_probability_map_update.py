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


def test_update_result_sums_to_one() -> None:
    pm = _pm()
    pm.update(
        sonar=_sm(),
        drone=(10, 10),
        heading=(0, 1),
        detected=False,
        vessel_moved=True,
        detection_streak=0,
    )
    assert abs(float(pm.values.sum()) - 1.0) < 1e-9


def test_update_preserves_shape() -> None:
    grid = Grid(rows=20, cols=15)
    pm = _pm(grid=grid)
    pm.update(
        sonar=_sm(),
        drone=(10, 5),
        heading=(0, 1),
        detected=False,
        vessel_moved=True,
        detection_streak=0,
    )
    assert pm.values.shape == (grid.rows, grid.cols)


def test_update_nonnegative() -> None:
    pm = _pm()
    pm.update(
        sonar=_sm(),
        drone=(10, 10),
        heading=(0, 1),
        detected=True,
        vessel_moved=True,
        detection_streak=0,
    )
    assert bool((pm.values >= 0.0).all())


def test_update_not_detected_lowers_swept_high_pod_cell_relative_to_prior() -> None:
    pm = _pm()
    before = pm.probability(10, 12)  # directly ahead of drone heading east, in cone
    before_far = pm.probability(0, 0)  # unaffected reference cell, outside cone
    pm.update(
        sonar=_sm(),
        drone=(10, 10),
        heading=(0, 1),
        detected=False,
        vessel_moved=True,
        detection_streak=0,
    )
    after = pm.probability(10, 12)
    after_far = pm.probability(0, 0)
    assert (after / after_far) < (before / before_far)


def test_update_detected_zeroes_cells_outside_cone() -> None:
    # A positive detection can only originate from within this drone's cone —
    # a cell this sweep couldn't have seen becomes impossible.
    pm = _pm()
    pm.update(
        sonar=_sm(),
        drone=(10, 10),
        heading=(0, 1),
        detected=True,
        vessel_moved=True,
        detection_streak=0,
    )
    assert pm.probability(0, 0) == 0.0


def test_update_detected_favors_closer_cell_within_cone() -> None:
    # drone/cells chosen to stay outside every spawn band (rows 2-6, 13-17,
    # cols 13-17 on this 20x20 grid), so the prior is flat and only the
    # distance-based POD drives the comparison.
    pm = _pm()
    pm.update(
        sonar=_sm(),
        drone=(10, 5),
        heading=(0, 1),
        detected=True,
        vessel_moved=True,
        detection_streak=0,
    )
    close_cell = pm.probability(10, 6)  # distance 1, in cone
    far_cell = pm.probability(10, 12)  # distance 7, still in cone (range 8)
    assert close_cell > far_cell


def test_update_cells_outside_cone_keep_same_relative_ratio() -> None:
    pm = _pm()
    before_a = pm.probability(0, 0)
    before_b = pm.probability(19, 0)
    pm.update(
        sonar=_sm(),
        drone=(10, 10),
        heading=(0, 1),
        detected=False,
        vessel_moved=True,
        detection_streak=0,
    )
    after_a = pm.probability(0, 0)
    after_b = pm.probability(19, 0)
    assert abs((after_a / after_b) - (before_a / before_b)) < 1e-9


def test_update_same_cell_as_drone_not_detected_zeroes_it_out() -> None:
    pm = _pm()
    pm.update(
        sonar=_sm(),
        drone=(10, 10),
        heading=(0, 1),
        detected=False,
        vessel_moved=True,
        detection_streak=0,
    )
    assert pm.probability(10, 10) == 0.0
