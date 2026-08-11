import random

from engine.entities import BlueDrone, BlueMothership, RedVessel
from engine.grid import Grid
from engine.probability_map import ProbabilityMap
from engine.simulation import Simulation
from engine.sonar_model import SonarModel


def _make(
    m_pos: tuple[int, int] = (0, 0),
    d_pos: tuple[int, int] = (1, 1),
    v_pos: tuple[int, int] = (9, 9),
    probability_map: ProbabilityMap | None = None,
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
        probability_map=probability_map,
    )
    return sim, d, v


def test_simulation_exposes_probability_map_matching_grid_shape() -> None:
    sim, *_ = _make()
    assert sim.probability_map.values.shape == (10, 10)


def test_advance_keeps_probability_map_normalized() -> None:
    sim, *_ = _make()
    sim.advance()
    assert abs(float(sim.probability_map.values.sum()) - 1.0) < 1e-9


def test_advance_changes_probability_map_from_initial_prior() -> None:
    sim, *_ = _make()
    before = sim.probability_map.values.copy()
    sim.advance()
    after = sim.probability_map.values
    assert not (before == after).all()


def test_detection_concentrates_probability_on_detected_cell() -> None:
    sim, d, v = _make(d_pos=(1, 1), v_pos=(5, 5))
    d.move(5, 5)  # same cell as vessel → certain detection
    sim.advance()
    assert sim.probability_map.probability(5, 5) > 0.5


def test_to_dict_includes_probability_map_with_correct_shape() -> None:
    sim, *_ = _make()
    state = sim.to_dict()
    assert "probability_map" in state
    assert len(state["probability_map"]) == 10
    assert len(state["probability_map"][0]) == 10


def test_probability_map_can_be_injected() -> None:
    custom = ProbabilityMap(Grid(rows=10, cols=10), floor=1e-3)
    sim, *_ = _make(probability_map=custom)
    assert sim.probability_map is custom
