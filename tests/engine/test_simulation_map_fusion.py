import random

import numpy as np
import pytest

from engine.entities import BlueDrone, BlueMothership, RedVessel
from engine.grid import Grid
from engine.probability_map import ProbabilityMap
from engine.search_strategy import GreedyMaxProbability
from engine.simulation import Simulation
from engine.sonar_model import SonarModel
from engine.strategy_assignment import StrategyAssignment


def _make(
    d1_pos: tuple[int, int] = (5, 5),
    d2_pos: tuple[int, int] = (5, 20),
    v_pos: tuple[int, int] = (9, 9),
    sync_interval: int = 10,
    probability_maps: list[ProbabilityMap] | None = None,
    strategy_assignment: StrategyAssignment | None = None,
    lock_turns: int = 200,
    engagement_turns: int = 200,
) -> tuple[Simulation, BlueDrone, BlueDrone, RedVessel]:
    g = Grid(rows=10, cols=30)
    m = BlueMothership(grid=g, row=0, col=0)
    d1 = BlueDrone(grid=g, row=d1_pos[0], col=d1_pos[1])
    d2 = BlueDrone(grid=g, row=d2_pos[0], col=d2_pos[1])
    v = RedVessel(grid=g, row=v_pos[0], col=v_pos[1])
    sim = Simulation(
        grid=g,
        mothership=m,
        drones=[d1, d2],
        red_vessel=v,
        rng=random.Random(42),
        sonar=SonarModel(range_cells=0),
        sync_interval=sync_interval,
        lock_turns=lock_turns,
        engagement_turns=engagement_turns,
        probability_maps=probability_maps,
        strategy_assignment=strategy_assignment,
    )
    return sim, d1, d2, v


# ---------------------------------------------------------------------------
# Constructor validation
# ---------------------------------------------------------------------------


def test_sync_interval_zero_raises_value_error() -> None:
    with pytest.raises(ValueError, match="sync_interval"):
        _make(sync_interval=0)


def test_probability_maps_length_mismatch_raises_value_error() -> None:
    pm = ProbabilityMap(Grid(rows=10, cols=30), spawn_min_dist=100, spawn_max_dist=100)
    with pytest.raises(ValueError, match="probability_maps"):
        _make(probability_maps=[pm])  # 1 map, but _make() builds 2 drones


# ---------------------------------------------------------------------------
# Independent per-drone updates
# ---------------------------------------------------------------------------


def test_detecting_drones_map_changes_more_than_non_detecting_drones() -> None:
    # SonarModel.in_cone() always returns True for a drone's own cell regardless
    # of range, so ProbabilityMap.update() touches *every* drone's map every
    # turn (it zeroes out that drone's own cell when nothing was detected there)
    # — both maps change every turn. The meaningful check is that a drone with
    # a real detection changes far more than one with none.
    sim, d1, d2, v = _make(d1_pos=(5, 5), d2_pos=(5, 20), v_pos=(9, 9))
    before_d1 = sim.probability_maps[0].values.copy()
    before_d2 = sim.probability_maps[1].values.copy()

    v.move(5, 5)  # same cell as d1 → guaranteed detection (range_cells=0 special case)
    sim.advance()

    change_d1 = float(np.abs(sim.probability_maps[0].values - before_d1).sum())
    change_d2 = float(np.abs(sim.probability_maps[1].values - before_d2).sum())
    assert change_d1 > change_d2


# ---------------------------------------------------------------------------
# Divergence before sync, convergence after
# ---------------------------------------------------------------------------


def test_maps_diverge_before_sync_interval() -> None:
    sim, d1, d2, v = _make(d1_pos=(5, 5), d2_pos=(5, 20), v_pos=(9, 9), sync_interval=10)
    v.move(5, 5)

    for _ in range(5):  # < sync_interval, no sync happens
        sim.advance()

    assert not (sim.probability_maps[0].values == sim.probability_maps[1].values).all()


def test_maps_converge_exactly_after_sync_interval() -> None:
    sim, d1, d2, v = _make(d1_pos=(5, 5), d2_pos=(5, 20), v_pos=(9, 9), sync_interval=3)
    v.move(5, 5)

    for _ in range(3):
        sim.advance()

    assert (sim.probability_maps[0].values == sim.probability_maps[1].values).all()


def test_sync_combines_information_from_all_drones() -> None:
    # d1 detects the vessel repeatedly (co-located), d2 never does (far away).
    # Rather than hand-reconstructing advance()'s internal math (fragile —
    # would silently drift out of sync with the real implementation), this
    # checks the externally-observable contract: before sync the two maps
    # have genuinely diverged, and after sync the result is a real fusion
    # (not simply equal to either drone's own pre-sync view).
    sim, d1, d2, v = _make(d1_pos=(5, 5), d2_pos=(5, 20), v_pos=(9, 9), sync_interval=2)
    v.move(5, 5)  # same cell as d1 → guaranteed detection (range_cells=0 special case)

    sim.advance()  # turn 1: d1 detects (co-located), d2 doesn't — no sync yet
    d1_before_sync = sim.probability_maps[0].values.copy()
    d2_before_sync = sim.probability_maps[1].values.copy()
    assert not (d1_before_sync == d2_before_sync).all()  # confirms real divergence to fuse

    sim.advance()  # turn 2: sync triggers (2 % 2 == 0)

    assert (sim.probability_maps[0].values == sim.probability_maps[1].values).all()
    assert not (sim.probability_maps[0].values == d1_before_sync).all()
    assert not (sim.probability_maps[0].values == d2_before_sync).all()


def test_maps_converge_diverge_and_reconverge_across_multiple_sync_cycles() -> None:
    sim, d1, d2, v = _make(d1_pos=(5, 5), d2_pos=(5, 20), v_pos=(9, 9), sync_interval=3)
    v.move(5, 5)

    for _ in range(3):
        sim.advance()
    assert (sim.probability_maps[0].values == sim.probability_maps[1].values).all()
    assert abs(float(sim.probability_maps[0].values.sum()) - 1.0) < 1e-9

    for _ in range(2):
        sim.advance()
    assert not (sim.probability_maps[0].values == sim.probability_maps[1].values).all()

    sim.advance()  # turn 6: second sync
    assert (sim.probability_maps[0].values == sim.probability_maps[1].values).all()
    assert abs(float(sim.probability_maps[0].values.sum()) - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# Default / custom sync_interval
# ---------------------------------------------------------------------------


def test_default_sync_interval_is_10() -> None:
    sim, d1, d2, v = _make(d1_pos=(5, 5), d2_pos=(5, 20), v_pos=(9, 9))
    v.move(5, 5)

    for _ in range(9):
        sim.advance()
    diverged = (sim.probability_maps[0].values == sim.probability_maps[1].values).all()
    sim.advance()  # 10th turn
    converged = (sim.probability_maps[0].values == sim.probability_maps[1].values).all()

    assert not diverged
    assert converged


# ---------------------------------------------------------------------------
# move_drones() reads each drone's own map
# ---------------------------------------------------------------------------


def test_move_drones_reads_each_drones_own_map() -> None:
    pm1 = ProbabilityMap(Grid(rows=10, cols=30), spawn_min_dist=100, spawn_max_dist=100)
    pm2 = ProbabilityMap(Grid(rows=10, cols=30), spawn_min_dist=100, spawn_max_dist=100)
    pm1.values[5, 7] = 0.9  # peak reachable by d1 (speed=2 from (5,5))
    pm2.values[5, 22] = 0.9  # peak reachable by d2 (speed=2 from (5,20))
    assignment = StrategyAssignment(
        strategies=[GreedyMaxProbability()],
        drone_count=2,
        switch_probability=0.0,
        rng=random.Random(0),
    )
    sim, d1, d2, v = _make(
        d1_pos=(5, 5),
        d2_pos=(5, 20),
        probability_maps=[pm1, pm2],
        strategy_assignment=assignment,
    )

    sim.move_drones()

    assert (d1.row, d1.col) == (5, 7)
    assert (d2.row, d2.col) == (5, 22)


# ---------------------------------------------------------------------------
# to_dict() is a read-only projection
# ---------------------------------------------------------------------------


def test_to_dict_does_not_mutate_individual_maps() -> None:
    sim, d1, d2, v = _make(d1_pos=(5, 5), d2_pos=(5, 20), v_pos=(9, 9))
    v.move(5, 5)
    sim.advance()
    before_d1 = sim.probability_maps[0].values.copy()
    before_d2 = sim.probability_maps[1].values.copy()

    sim.to_dict()
    sim.to_dict()

    assert (sim.probability_maps[0].values == before_d1).all()
    assert (sim.probability_maps[1].values == before_d2).all()
