import random

from engine.entities import BlueDrone, BlueMothership, DetectionState, RedVessel
from engine.grid import Grid
from engine.probability_map import ProbabilityMap
from engine.search_strategy import GreedyMaxProbability
from engine.simulation import Simulation
from engine.sonar_model import SonarModel
from engine.strategy_assignment import StrategyAssignment
from tests.engine.conftest import _FixedSequenceRandom


class _FixedTargetStrategy:
    """Deterministic stand-in for SearchStrategy: always returns a fixed target."""

    def __init__(self, target: tuple[int, int]) -> None:
        self._target = target

    def next_target(
        self,
        position: tuple[int, int],
        speed: int,
        grid: Grid,
        probability_map: ProbabilityMap,
    ) -> tuple[int, int]:
        return self._target


def _make(
    m_pos: tuple[int, int] = (0, 0),
    d_pos: tuple[int, int] = (5, 5),
    v_pos: tuple[int, int] = (9, 9),
    strategy_assignment: StrategyAssignment | None = None,
    probability_map: ProbabilityMap | None = None,
    drone_speed: int = 2,
) -> tuple[Simulation, BlueDrone, RedVessel]:
    g = Grid(rows=10, cols=10)
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
        strategy_assignment=strategy_assignment,
        probability_map=probability_map,
        drone_speed=drone_speed,
    )
    return sim, d, v


# ---------------------------------------------------------------------------
# move_drones()
# ---------------------------------------------------------------------------


def test_move_drones_moves_drone_to_strategy_target() -> None:
    fixed = _FixedTargetStrategy(target=(7, 7))
    assignment = StrategyAssignment(
        strategies=[fixed], drone_count=1, switch_probability=0.0, rng=random.Random(0)
    )  # type: ignore[arg-type]
    sim, d, _ = _make(d_pos=(5, 5), strategy_assignment=assignment)

    sim.move_drones()

    assert (d.row, d.col) == (7, 7)


def test_move_drones_advances_strategy_assignment_before_moving() -> None:
    a = _FixedTargetStrategy(target=(1, 1))
    b = _FixedTargetStrategy(target=(2, 2))
    fake_rng = _FixedSequenceRandom(randoms=[0.0], choices=[a, b])
    assignment = StrategyAssignment(
        strategies=[a, b], drone_count=1, switch_probability=1.0, rng=fake_rng
    )  # type: ignore[arg-type]
    assert assignment.strategy_for(0) is a
    sim, d, _ = _make(d_pos=(5, 5), strategy_assignment=assignment)

    sim.move_drones()

    assert assignment.strategy_for(0) is b
    assert (d.row, d.col) == (2, 2)


def test_move_drones_uses_probability_map_and_drone_speed() -> None:
    pm = ProbabilityMap(Grid(rows=10, cols=10), spawn_min_dist=100, spawn_max_dist=100)
    pm.values[5, 7] = 0.9  # peak within speed=2 reach of (5, 5)
    assignment = StrategyAssignment(
        strategies=[GreedyMaxProbability()],
        drone_count=1,
        switch_probability=0.0,
        rng=random.Random(0),
    )
    sim, d, _ = _make(
        d_pos=(5, 5), strategy_assignment=assignment, probability_map=pm, drone_speed=2
    )

    sim.move_drones()

    assert (d.row, d.col) == (5, 7)


def test_move_drones_respects_grid_bounds() -> None:
    sim, d, _ = _make(m_pos=(9, 0), d_pos=(0, 0))
    sim.move_drones()
    assert sim.grid.in_bounds(d.row, d.col)


def test_default_strategy_assignment_uses_simulation_rng_for_determinism() -> None:
    sim1, d1, _ = _make()
    sim2, d2, _ = _make()

    sim1.move_drones()
    sim2.move_drones()

    assert (d1.row, d1.col) == (d2.row, d2.col)


def test_move_drones_deconflicts_drones_targeting_the_same_cell() -> None:
    fixed = _FixedTargetStrategy(target=(3, 3))
    assignment = StrategyAssignment(
        strategies=[fixed], drone_count=2, switch_probability=0.0, rng=random.Random(0)
    )  # type: ignore[arg-type]
    g = Grid(rows=10, cols=10)
    m = BlueMothership(grid=g, row=0, col=0)
    d1 = BlueDrone(grid=g, row=1, col=1)
    d2 = BlueDrone(grid=g, row=2, col=2)
    v = RedVessel(grid=g, row=9, col=9)
    sim = Simulation(
        grid=g,
        mothership=m,
        drones=[d1, d2],
        red_vessel=v,
        rng=random.Random(42),
        sonar=SonarModel(range_cells=0),
        strategy_assignment=assignment,
    )

    sim.move_drones()

    assert (d1.row, d1.col) != (d2.row, d2.col)
    assert (d1.row, d1.col) == (3, 3)  # first drone claims the target
    assert (d2.row, d2.col) == (2, 2)  # second drone's target was claimed, stays in place


# ---------------------------------------------------------------------------
# Detection state integration
# ---------------------------------------------------------------------------


def test_advance_moves_drone_detection_state_to_signaling_on_first_contact() -> None:
    sim, d, v = _make(d_pos=(1, 1), v_pos=(9, 9))
    v.move(1, 1)  # same cell as drone → guaranteed detection (range_cells=0 special case)

    sim.advance()

    assert d.detection_state is DetectionState.SIGNALING


def test_advance_keeps_drone_detection_state_searching_without_contact() -> None:
    sim, d, v = _make(d_pos=(1, 1), v_pos=(9, 9))

    sim.advance()

    assert d.detection_state is DetectionState.SEARCHING


def test_advance_builds_up_drone_detection_state_over_consecutive_turns() -> None:
    sim, d, v = _make(d_pos=(1, 1), v_pos=(9, 9))
    v.move(1, 1)

    sim.advance()  # streak=1 → SIGNALING
    sim.advance()  # streak=2 → CONFIRMING
    sim.advance()  # streak=3 → TRACKING

    assert d.detection_state is DetectionState.TRACKING


def test_to_dict_includes_drone_detection_state() -> None:
    sim, d, v = _make(d_pos=(1, 1), v_pos=(9, 9))
    v.move(1, 1)
    sim.advance()

    state = sim.to_dict()

    assert state["drones"][0]["detection_state"] == "signaling"


def test_to_dict_includes_drone_strategy_name() -> None:
    assignment = StrategyAssignment(
        strategies=[GreedyMaxProbability()], drone_count=1, switch_probability=0.0
    )
    sim, d, v = _make(d_pos=(1, 1), v_pos=(9, 9), strategy_assignment=assignment)

    state = sim.to_dict()

    assert state["drones"][0]["strategy"] == "greedy_max_probability"


def test_global_win_condition_streak_unaffected_by_per_drone_detection_state() -> None:
    sim, d, v = _make(m_pos=(0, 0), d_pos=(0, 4), v_pos=(9, 9))
    v.move(0, 4)  # same cell as drone → guaranteed detection

    sim.advance()  # turn 1: detection_streak=1 (global), drone detection_state=SIGNALING
    sim.advance()  # turn 2: detection_streak=2 (global), drone detection_state=CONFIRMING

    assert d.detection_state is DetectionState.CONFIRMING
    assert sim.result.value == "in_progress"  # lock_turns default is 3, not reached yet
    sim.advance()  # turn 3: detection_streak=3 >= lock_turns=3; engagement also satisfied (mothership at (0,0), vessel at (0,4), Chebyshev=4 <= default mothership_range=5)
    assert d.detection_state is DetectionState.TRACKING
    assert sim.result.value == "blue_wins"
