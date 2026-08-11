from engine.grid import Grid
from engine.red_behavior import (
    InfiltrationZone,
    infiltration_zone_for,
    red_baseline_target,
    red_evasion_target,
)

# ---------------------------------------------------------------------------
# infiltration_zone_for
# ---------------------------------------------------------------------------


def test_zone_spans_10_cols_from_west_edge() -> None:
    grid = Grid(rows=50, cols=50)
    zone = infiltration_zone_for(mothership_row=25, grid=grid)
    assert zone.col_min == 0
    assert zone.col_max == 10


def test_zone_is_6_rows_tall_centered_on_mothership_row() -> None:
    grid = Grid(rows=50, cols=50)
    zone = infiltration_zone_for(mothership_row=25, grid=grid)
    assert zone.row_min == 22
    assert zone.row_max == 28


def test_zone_clamped_to_grid_bounds_near_top_edge() -> None:
    grid = Grid(rows=50, cols=50)
    zone = infiltration_zone_for(mothership_row=1, grid=grid)
    assert zone.row_min == 0
    assert zone.row_max == 4


# ---------------------------------------------------------------------------
# InfiltrationZone.contains
# ---------------------------------------------------------------------------


def _zone() -> InfiltrationZone:
    return InfiltrationZone(row_min=5, row_max=11, col_min=0, col_max=10)


def test_contains_inside_zone() -> None:
    assert _zone().contains(7, 3) is True


def test_contains_row_below_min() -> None:
    assert _zone().contains(4, 3) is False


def test_contains_row_at_max_is_excluded() -> None:
    assert _zone().contains(11, 3) is False


def test_contains_col_at_max_is_excluded() -> None:
    assert _zone().contains(7, 10) is False


def test_contains_col_min_is_included() -> None:
    assert _zone().contains(7, 0) is True


# ---------------------------------------------------------------------------
# red_baseline_target
# ---------------------------------------------------------------------------


def test_moves_west_when_row_already_aligned() -> None:
    grid = Grid(rows=50, cols=50)
    zone = _zone()
    target = red_baseline_target(position=(7, 20), zone=zone, speed=1, grid=grid)
    assert target == (7, 19)


def test_moves_diagonally_when_row_misaligned() -> None:
    grid = Grid(rows=50, cols=50)
    zone = _zone()
    target = red_baseline_target(position=(20, 20), zone=zone, speed=1, grid=grid)
    assert target == (19, 19)


def test_does_not_overshoot_when_closer_than_speed() -> None:
    grid = Grid(rows=50, cols=50)
    zone = _zone()  # col_max=10, so col 9 is the nearest cell still inside the zone
    target = red_baseline_target(position=(7, 12), zone=zone, speed=3, grid=grid)
    assert target == (7, 9)


def test_stays_in_place_once_inside_zone() -> None:
    grid = Grid(rows=50, cols=50)
    zone = _zone()
    target = red_baseline_target(position=(7, 3), zone=zone, speed=1, grid=grid)
    assert target == (7, 3)


def test_respects_speed_greater_than_one() -> None:
    grid = Grid(rows=50, cols=50)
    zone = _zone()
    target = red_baseline_target(position=(7, 20), zone=zone, speed=3, grid=grid)
    assert target == (7, 17)


def test_respects_grid_bounds() -> None:
    grid = Grid(rows=10, cols=10)
    zone = InfiltrationZone(row_min=0, row_max=6, col_min=0, col_max=10)
    target = red_baseline_target(position=(0, 0), zone=zone, speed=1, grid=grid)
    assert grid.in_bounds(*target)


# ---------------------------------------------------------------------------
# red_evasion_target
# ---------------------------------------------------------------------------


def test_flees_west_when_threat_is_east() -> None:
    grid = Grid(rows=50, cols=50)
    target = red_evasion_target(position=(20, 20), threats=[(20, 25)], speed=1, grid=grid)
    assert target == (20, 19)


def test_flees_diagonally_when_threat_is_diagonal() -> None:
    grid = Grid(rows=50, cols=50)
    target = red_evasion_target(position=(20, 20), threats=[(23, 23)], speed=1, grid=grid)
    assert target == (19, 19)


def test_flees_from_nearest_threat_among_several() -> None:
    grid = Grid(rows=50, cols=50)
    target = red_evasion_target(position=(20, 20), threats=[(20, 30), (20, 22)], speed=1, grid=grid)
    assert target == (20, 19)  # flees the closer threat at (20, 22), east → moves west


def test_respects_speed() -> None:
    grid = Grid(rows=50, cols=50)
    target = red_evasion_target(position=(20, 20), threats=[(20, 25)], speed=3, grid=grid)
    assert target == (20, 17)


def test_evasion_respects_grid_bounds() -> None:
    grid = Grid(rows=10, cols=10)
    target = red_evasion_target(position=(0, 0), threats=[(1, 1)], speed=1, grid=grid)
    assert grid.in_bounds(*target)
