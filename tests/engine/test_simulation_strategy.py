import random

from engine.entities import BlueDrone, BlueMothership, RedVessel
from engine.grid import Grid
from engine.probability_map import ProbabilityMap
from engine.search_strategy import GreedyMaxProbability, SearchStrategy
from engine.simulation import Simulation
from engine.sonar_model import SonarModel
from engine.strategy_assignment import StrategyAssignment


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


class _FixedSequenceRandom:
    """Deterministic stand-in for random.Random: returns queued values in order."""

    def __init__(self, randoms: list[float], choices: list[SearchStrategy]) -> None:
        self._randoms = list(randoms)
        self._choices = list(choices)

    def random(self) -> float:
        return self._randoms.pop(0)

    def choice(self, seq: list[SearchStrategy]) -> SearchStrategy:
        return self._choices.pop(0)


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
