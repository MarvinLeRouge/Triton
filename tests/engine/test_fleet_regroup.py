from engine.fleet_regroup import regroup_target
from engine.grid import Grid


def test_regroup_target_steps_toward_target_bounded_by_speed() -> None:
    g = Grid(rows=20, cols=20)
    result = regroup_target(position=(5, 5), target=(5, 15), speed=3, grid=g)
    assert result == (5, 8)


def test_regroup_target_reaches_target_exactly_when_within_speed() -> None:
    g = Grid(rows=20, cols=20)
    result = regroup_target(position=(5, 5), target=(5, 7), speed=3, grid=g)
    assert result == (5, 7)


def test_regroup_target_stays_put_when_already_at_target() -> None:
    g = Grid(rows=20, cols=20)
    result = regroup_target(position=(5, 5), target=(5, 5), speed=3, grid=g)
    assert result == (5, 5)


def test_regroup_target_moves_diagonally_toward_target() -> None:
    g = Grid(rows=20, cols=20)
    result = regroup_target(position=(0, 0), target=(10, 10), speed=2, grid=g)
    assert result == (2, 2)


def test_regroup_target_clamped_by_grid_bounds() -> None:
    g = Grid(rows=10, cols=10)
    result = regroup_target(position=(1, 1), target=(-5, -5), speed=5, grid=g)
    assert result == (0, 0)
