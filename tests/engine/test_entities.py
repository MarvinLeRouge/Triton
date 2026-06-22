import pytest

from engine.entities import BlueDrone, BlueMothership, Entity, Faction, RedVessel
from engine.grid import Grid

# ---------------------------------------------------------------------------
# Faction
# ---------------------------------------------------------------------------


def test_faction_values() -> None:
    assert Faction.BLUE is not Faction.RED


# ---------------------------------------------------------------------------
# BlueMothership
# ---------------------------------------------------------------------------


def test_mothership_faction() -> None:
    g = Grid()
    m = BlueMothership(grid=g, row=10, col=10)
    assert m.faction is Faction.BLUE


def test_mothership_position() -> None:
    g = Grid()
    m = BlueMothership(grid=g, row=5, col=7)
    assert m.row == 5
    assert m.col == 7


def test_mothership_is_entity() -> None:
    g = Grid()
    assert isinstance(BlueMothership(grid=g, row=0, col=0), Entity)


def test_mothership_out_of_bounds_raises() -> None:
    g = Grid(rows=10, cols=10)
    with pytest.raises(ValueError):
        BlueMothership(grid=g, row=10, col=0)


# ---------------------------------------------------------------------------
# BlueDrone
# ---------------------------------------------------------------------------


def test_drone_faction() -> None:
    g = Grid()
    d = BlueDrone(grid=g, row=3, col=4)
    assert d.faction is Faction.BLUE


def test_drone_is_entity() -> None:
    g = Grid()
    assert isinstance(BlueDrone(grid=g, row=0, col=0), Entity)


def test_drone_out_of_bounds_raises() -> None:
    g = Grid(rows=10, cols=10)
    with pytest.raises(ValueError):
        BlueDrone(grid=g, row=0, col=10)


def test_drone_move_valid() -> None:
    g = Grid()
    d = BlueDrone(grid=g, row=5, col=5)
    d.move(6, 6)
    assert d.row == 6
    assert d.col == 6


def test_drone_move_out_of_bounds_raises() -> None:
    g = Grid(rows=10, cols=10)
    d = BlueDrone(grid=g, row=5, col=5)
    with pytest.raises(ValueError):
        d.move(10, 5)


# ---------------------------------------------------------------------------
# RedVessel
# ---------------------------------------------------------------------------


def test_red_vessel_faction() -> None:
    g = Grid()
    v = RedVessel(grid=g, row=20, col=30)
    assert v.faction is Faction.RED


def test_red_vessel_is_entity() -> None:
    g = Grid()
    assert isinstance(RedVessel(grid=g, row=0, col=0), Entity)


def test_red_vessel_out_of_bounds_raises() -> None:
    g = Grid(rows=10, cols=10)
    with pytest.raises(ValueError):
        RedVessel(grid=g, row=-1, col=0)


def test_red_vessel_move_valid() -> None:
    g = Grid()
    v = RedVessel(grid=g, row=10, col=10)
    v.move(11, 9)
    assert v.row == 11
    assert v.col == 9


def test_red_vessel_move_out_of_bounds_raises() -> None:
    g = Grid(rows=10, cols=10)
    v = RedVessel(grid=g, row=5, col=5)
    with pytest.raises(ValueError):
        v.move(5, -1)


# ---------------------------------------------------------------------------
# BlueDrone — heading
# ---------------------------------------------------------------------------


def test_drone_default_heading_is_east() -> None:
    g = Grid()
    d = BlueDrone(grid=g, row=5, col=5)
    assert d.heading == (0, 1)


def test_drone_heading_updates_on_move_south() -> None:
    g = Grid()
    d = BlueDrone(grid=g, row=5, col=5)
    d.move(6, 5)
    assert d.heading == (1, 0)


def test_drone_heading_updates_on_move_northeast() -> None:
    g = Grid()
    d = BlueDrone(grid=g, row=5, col=5)
    d.move(4, 6)
    assert d.heading == (-1, 1)


def test_drone_heading_preserved_when_stationary() -> None:
    g = Grid()
    d = BlueDrone(grid=g, row=5, col=5)
    d.move(6, 5)  # heading now (1, 0)
    d.move(6, 5)  # no movement → heading unchanged
    assert d.heading == (1, 0)


def test_drone_heading_updates_on_diagonal_move() -> None:
    g = Grid()
    d = BlueDrone(grid=g, row=5, col=5)
    d.move(6, 6)
    assert d.heading == (1, 1)
