import random

from engine.entities import BlueDrone, BlueMothership, RedVessel
from engine.grid import Grid
from engine.simulation import GameResult, Simulation
from engine.sonar_model import SonarModel


def _make(
    m_pos: tuple[int, int] = (25, 4),
    d_pos: tuple[int, int] = (25, 5),
    v_pos: tuple[int, int] = (25, 40),
    vessel_speed: int = 1,
) -> tuple[Simulation, RedVessel]:
    g = Grid(rows=50, cols=50)
    m = BlueMothership(grid=g, row=m_pos[0], col=m_pos[1])
    d = BlueDrone(grid=g, row=d_pos[0], col=d_pos[1])
    v = RedVessel(grid=g, row=v_pos[0], col=v_pos[1])
    sim = Simulation(
        grid=g,
        mothership=m,
        drones=[d],
        red_vessel=v,
        rng=random.Random(42),
        sonar=SonarModel(range_cells=0),
        vessel_speed=vessel_speed,
    )
    return sim, v


# ---------------------------------------------------------------------------
# move_vessel()
# ---------------------------------------------------------------------------


def test_move_vessel_moves_toward_infiltration_zone() -> None:
    sim, v = _make(v_pos=(25, 40))
    sim.move_vessel()
    assert (v.row, v.col) == (25, 39)


def test_move_vessel_stays_once_inside_zone() -> None:
    sim, v = _make(v_pos=(25, 3))  # already inside the zone (cols 0-9, rows 22-27)
    sim.move_vessel()
    assert (v.row, v.col) == (25, 3)


def test_move_vessel_respects_vessel_speed() -> None:
    sim, v = _make(v_pos=(25, 40), vessel_speed=3)
    sim.move_vessel()
    assert (v.row, v.col) == (25, 37)


def test_move_vessel_no_op_after_game_ends() -> None:
    g = Grid(rows=50, cols=50)
    m = BlueMothership(grid=g, row=25, col=4)
    d = BlueDrone(grid=g, row=25, col=5)
    v = RedVessel(grid=g, row=25, col=40)
    sim = Simulation(
        grid=g,
        mothership=m,
        drones=[d],
        red_vessel=v,
        max_turns=1,
        rng=random.Random(42),
        sonar=SonarModel(range_cells=0),
    )
    sim.advance()
    assert sim.result is GameResult.RED_WINS

    before = (v.row, v.col)
    sim.move_vessel()

    assert (v.row, v.col) == before


# ---------------------------------------------------------------------------
# Infiltration win condition
# ---------------------------------------------------------------------------


def test_advance_declares_red_wins_when_vessel_enters_infiltration_zone() -> None:
    sim, v = _make(m_pos=(25, 4), v_pos=(25, 3))  # already inside the zone
    assert sim.advance() is GameResult.RED_WINS


def test_advance_stays_in_progress_when_vessel_outside_zone() -> None:
    sim, v = _make(m_pos=(25, 4), v_pos=(25, 40))
    assert sim.advance() is GameResult.IN_PROGRESS


def test_infiltration_zone_depends_on_mothership_row() -> None:
    # zone is rows [22,28) x cols [0,10) when mothership is at row 25
    sim, v = _make(m_pos=(25, 4), v_pos=(30, 3))  # inside col band, but row 30 is outside [22,28)
    assert sim.advance() is GameResult.IN_PROGRESS
