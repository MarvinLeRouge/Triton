import random

import pytest

from engine.entities import BlueDrone, BlueMothership, RedVessel
from engine.grid import Grid
from engine.simulation import GameResult, Simulation
from engine.sonar_model import SonarModel


def _make(
    m_pos: tuple[int, int] = (0, 0),
    d_pos: tuple[int, int] = (1, 1),
    v_pos: tuple[int, int] = (9, 9),
    max_turns: int = 50,
    lock_turns: int = 2,
    mothership_range: int = 5,
    engagement_turns: int = 2,
) -> tuple[Simulation, BlueMothership, BlueDrone, RedVessel]:
    g = Grid(rows=10, cols=10)
    m = BlueMothership(grid=g, row=m_pos[0], col=m_pos[1])
    d = BlueDrone(grid=g, row=d_pos[0], col=d_pos[1])
    v = RedVessel(grid=g, row=v_pos[0], col=v_pos[1])
    sim = Simulation(
        grid=g,
        mothership=m,
        drones=[d],
        red_vessel=v,
        max_turns=max_turns,
        lock_turns=lock_turns,
        mothership_range=mothership_range,
        engagement_turns=engagement_turns,
        rng=random.Random(42),
        sonar=SonarModel(range_cells=0),  # same-cell only → mirrors Phase 1 behaviour
    )
    return sim, m, d, v


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


def test_initial_result_is_in_progress() -> None:
    sim, *_ = _make()
    assert sim.result is GameResult.IN_PROGRESS


def test_initial_turn_is_zero() -> None:
    sim, *_ = _make()
    assert sim.turn == 0


def test_overlapping_entities_raise() -> None:
    g = Grid(rows=10, cols=10)
    m = BlueMothership(grid=g, row=5, col=5)
    d = BlueDrone(grid=g, row=5, col=5)
    v = RedVessel(grid=g, row=9, col=9)
    with pytest.raises(ValueError):
        Simulation(grid=g, mothership=m, drones=[d], red_vessel=v)


# ---------------------------------------------------------------------------
# Tour et état de base
# ---------------------------------------------------------------------------


def test_advance_increments_turn() -> None:
    sim, *_ = _make()
    sim.advance()
    assert sim.turn == 1
    sim.advance()
    assert sim.turn == 2


def test_no_detection_stays_in_progress() -> None:
    sim, *_ = _make()
    for _ in range(5):
        result = sim.advance()
    assert result is GameResult.IN_PROGRESS


def test_timeout_gives_red_wins() -> None:
    sim, *_ = _make(max_turns=3)
    for _ in range(3):
        sim.advance()
    assert sim.result is GameResult.RED_WINS


# ---------------------------------------------------------------------------
# Condition de victoire Blue
# ---------------------------------------------------------------------------


def test_detection_without_mothership_range_stays_in_progress() -> None:
    # mothership (0,0), red (9,9) → Chebyshev distance = 9 > range=3
    sim, m, d, v = _make(m_pos=(0, 0), v_pos=(9, 9), mothership_range=3)
    d.move(9, 9)  # drone détecte red
    sim.advance()
    sim.advance()  # lock_turns=2 atteint, mais hors portée
    assert sim.result is GameResult.IN_PROGRESS


def test_in_range_without_detection_stays_in_progress() -> None:
    # red à portée du mothership, mais aucun drone ne le détecte
    sim, m, d, v = _make(m_pos=(0, 0), v_pos=(0, 4), mothership_range=5)
    # d reste en (1,1) → pas de détection
    sim.advance()
    sim.advance()
    assert sim.result is GameResult.IN_PROGRESS


def test_blue_wins_when_all_conditions_met() -> None:
    # mothership (0,0), red (0,4) → Chebyshev = 4 ≤ 5 → à portée
    sim, m, d, v = _make(
        m_pos=(0, 0), v_pos=(0, 4), mothership_range=5, lock_turns=2, engagement_turns=2
    )
    d.move(0, 4)  # même cellule que red → détection
    sim.advance()  # detection_streak=1, engagement_streak=1
    assert sim.advance() is GameResult.BLUE_WINS  # streaks=2 ≥ seuils


def test_blue_wins_require_lock_before_engagement() -> None:
    # lock_turns=3, engagement_turns=2 → Blue gagne au tour 3 seulement
    sim, m, d, v = _make(
        m_pos=(0, 0), v_pos=(0, 4), mothership_range=5, lock_turns=3, engagement_turns=2
    )
    d.move(0, 4)
    assert sim.advance() is GameResult.IN_PROGRESS  # streaks=1
    assert (
        sim.advance() is GameResult.IN_PROGRESS
    )  # detection=2, engagement=2 → engagement ok mais lock pas encore
    assert sim.advance() is GameResult.BLUE_WINS  # detection=3, engagement=3


# ---------------------------------------------------------------------------
# Réinitialisation des streaks
# ---------------------------------------------------------------------------


def test_detection_streak_resets_on_lost_contact() -> None:
    sim, m, d, v = _make(
        m_pos=(0, 0), v_pos=(0, 4), mothership_range=5, lock_turns=3, engagement_turns=3
    )
    d.move(0, 4)
    sim.advance()  # detection_streak=1
    d.move(1, 1)  # perte de contact
    sim.advance()  # detection_streak=0
    d.move(0, 4)  # recontact
    sim.advance()  # detection_streak=1
    sim.advance()  # detection_streak=2 → encore insuffisant (besoin 3)
    assert sim.result is GameResult.IN_PROGRESS


def test_engagement_streak_resets_when_out_of_range() -> None:
    # mothership_range=4 : (0,0)→(0,4) = Chebyshev 4 ≤ 4 → à portée
    #                       (0,9)→(0,4) = Chebyshev 5 > 4 → hors portée
    sim, m, d, v = _make(
        m_pos=(0, 0), v_pos=(0, 4), mothership_range=4, lock_turns=2, engagement_turns=2
    )
    d.move(0, 4)  # détection
    sim.advance()  # detection_streak=1, engagement_streak=1
    m.move(0, 9)  # mothership hors portée
    sim.advance()  # detection_streak=2 ≥ lock, mais engagement_streak=0 → reset
    assert sim.result is GameResult.IN_PROGRESS


# ---------------------------------------------------------------------------
# Gel du résultat après fin de partie
# ---------------------------------------------------------------------------


def test_turn_does_not_increment_after_blue_wins() -> None:
    sim, m, d, v = _make(m_pos=(0, 0), v_pos=(0, 4), mothership_range=5)
    d.move(0, 4)
    sim.advance()
    sim.advance()  # BLUE_WINS au tour 2
    sim.advance()  # ne doit pas avancer
    assert sim.turn == 2
    assert sim.result is GameResult.BLUE_WINS


def test_turn_does_not_increment_after_red_wins() -> None:
    sim, *_ = _make(max_turns=2)
    sim.advance()
    sim.advance()  # RED_WINS
    sim.advance()  # ne doit pas avancer
    assert sim.turn == 2
    assert sim.result is GameResult.RED_WINS


# ---------------------------------------------------------------------------
# detection_events
# ---------------------------------------------------------------------------


def test_detection_events_populated_when_drone_on_vessel() -> None:
    sim, m, d, v = _make(d_pos=(1, 1), v_pos=(5, 5))
    d.move(5, 5)  # same cell as vessel → certain detection (range_cells=0 degenerate case)
    sim.advance()
    state = sim.to_dict()
    assert len(state["detection_events"]) == 1
    assert state["detection_events"][0]["drone_idx"] == 0
    assert state["detection_events"][0]["pod"] == 1.0


def test_detection_events_empty_when_no_detection() -> None:
    sim, *_ = _make()  # drone at (1,1), vessel at (9,9) → no detection
    sim.advance()
    assert sim.to_dict()["detection_events"] == []


def test_to_dict_drones_include_heading() -> None:
    sim, m, d, v = _make()
    state = sim.to_dict()
    assert "heading" in state["drones"][0]
    assert state["drones"][0]["heading"] == [0, 1]  # default east
