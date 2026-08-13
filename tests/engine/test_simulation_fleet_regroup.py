import random

from engine.entities import BlueDrone, BlueMothership, RedVessel
from engine.grid import Grid
from engine.probability_map import ProbabilityMap
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
    positions: list[tuple[int, int]] | None = None,
    v_pos: tuple[int, int] = (19, 19),
    strategy_assignment: StrategyAssignment | None = None,
    range_cells: int = 3,
    drone_speed: int = 2,
) -> tuple[Simulation, list[BlueDrone], RedVessel]:
    g = Grid(rows=20, cols=20)
    m = BlueMothership(grid=g, row=0, col=0)
    positions = positions if positions is not None else [(5, 5), (5, 15)]
    drones = [BlueDrone(grid=g, row=p[0], col=p[1]) for p in positions]
    v = RedVessel(grid=g, row=v_pos[0], col=v_pos[1])
    sim = Simulation(
        grid=g,
        mothership=m,
        drones=drones,
        red_vessel=v,
        rng=random.Random(42),
        sonar=SonarModel(range_cells=range_cells),
        strategy_assignment=strategy_assignment,
        drone_speed=drone_speed,
    )
    return sim, drones, v


def _confirm(drone: BlueDrone) -> None:
    """Force a drone to CONFIRMING (default tracking_threshold=3: streak=2 -> CONFIRMING)."""
    drone.update_detection(True)
    drone.update_detection(True)


# ---------------------------------------------------------------------------
# No confirming drone: unchanged behavior
# ---------------------------------------------------------------------------


def test_move_drones_uses_assigned_strategies_when_no_drone_confirming() -> None:
    a = _FixedTargetStrategy(target=(1, 1))
    b = _FixedTargetStrategy(target=(18, 18))
    fake_rng = _FixedSequenceRandom(randoms=[1.0, 1.0], choices=[a, b])
    assignment = StrategyAssignment(
        strategies=[a, b], drone_count=2, switch_probability=0.0, rng=fake_rng
    )  # type: ignore[arg-type]
    sim, drones, _ = _make(positions=[(5, 5), (5, 15)], strategy_assignment=assignment)

    sim.move_drones()

    # _FixedTargetStrategy.next_target() always returns its raw target unconditionally
    # (no speed clamping — that's each real strategy's own job), so each drone jumps
    # straight to its assigned fixed target here, matching the established pattern in
    # tests/engine/test_simulation_strategy.py::test_move_drones_moves_drone_to_strategy_target.
    assert (drones[0].row, drones[0].col) == (1, 1)
    assert (drones[1].row, drones[1].col) == (18, 18)


# ---------------------------------------------------------------------------
# One confirming drone: others regroup
# ---------------------------------------------------------------------------


def test_move_drones_regroups_other_drones_toward_confirming_drone() -> None:
    a = _FixedTargetStrategy(target=(5, 5))  # anchor stays put via its own strategy
    b = _FixedTargetStrategy(target=(5, 19))  # b's own assigned target, should be ignored
    fake_rng = _FixedSequenceRandom(randoms=[1.0, 1.0], choices=[a, b])
    assignment = StrategyAssignment(
        strategies=[a, b], drone_count=2, switch_probability=0.0, rng=fake_rng
    )  # type: ignore[arg-type]
    sim, drones, _ = _make(positions=[(5, 5), (5, 15)], strategy_assignment=assignment)
    _confirm(drones[0])

    sim.move_drones()

    assert (drones[0].row, drones[0].col) == (5, 5)  # anchor: own strategy, unaffected
    assert (drones[1].row, drones[1].col) == (
        5,
        13,
    )  # regroups toward (5,5), not its own (5,19) target


# ---------------------------------------------------------------------------
# Minimum spacing
# ---------------------------------------------------------------------------


def test_move_drones_holds_position_when_regroup_would_violate_min_spacing() -> None:
    a = _FixedTargetStrategy(target=(5, 5))  # anchor stays put
    b = _FixedTargetStrategy(target=(5, 5))  # irrelevant, overridden by regroup
    fake_rng = _FixedSequenceRandom(randoms=[1.0, 1.0], choices=[a, b])
    assignment = StrategyAssignment(
        strategies=[a, b], drone_count=2, switch_probability=0.0, rng=fake_rng
    )  # type: ignore[arg-type]
    # drone 1 starts at Chebyshev distance 3 from the anchor == range_cells (min_spacing).
    # Its unconstrained regroup step (speed=2) would land it at distance 1, violating spacing.
    sim, drones, _ = _make(
        positions=[(5, 5), (5, 8)], strategy_assignment=assignment, range_cells=3, drone_speed=2
    )
    _confirm(drones[0])

    sim.move_drones()

    assert (drones[1].row, drones[1].col) == (5, 8)  # held in place, did not move


def test_move_drones_regroup_step_allowed_when_it_respects_min_spacing() -> None:
    a = _FixedTargetStrategy(target=(5, 5))
    b = _FixedTargetStrategy(target=(5, 5))
    fake_rng = _FixedSequenceRandom(randoms=[1.0, 1.0], choices=[a, b])
    assignment = StrategyAssignment(
        strategies=[a, b], drone_count=2, switch_probability=0.0, rng=fake_rng
    )  # type: ignore[arg-type]
    # drone 1 starts far enough (distance 10) that a speed=2 step still leaves it well
    # outside min_spacing=3 afterward (distance 8) -> allowed to move.
    sim, drones, _ = _make(
        positions=[(5, 5), (5, 15)], strategy_assignment=assignment, range_cells=3, drone_speed=2
    )
    _confirm(drones[0])

    sim.move_drones()

    assert (drones[1].row, drones[1].col) == (5, 13)


def test_move_drones_regroup_step_allowed_when_it_lands_exactly_at_min_spacing() -> None:
    a = _FixedTargetStrategy(target=(5, 5))
    b = _FixedTargetStrategy(target=(5, 5))
    fake_rng = _FixedSequenceRandom(randoms=[1.0, 1.0], choices=[a, b])
    assignment = StrategyAssignment(
        strategies=[a, b], drone_count=2, switch_probability=0.0, rng=fake_rng
    )  # type: ignore[arg-type]
    # drone 1 starts at distance 5 from the anchor; its speed=2 step lands it at distance
    # 3, exactly equal to min_spacing=3. Landing exactly at min_spacing is allowed (not a
    # violation) — only landing strictly closer than min_spacing holds the drone in place.
    sim, drones, _ = _make(
        positions=[(5, 5), (5, 10)], strategy_assignment=assignment, range_cells=3, drone_speed=2
    )
    _confirm(drones[0])

    sim.move_drones()

    assert (drones[1].row, drones[1].col) == (5, 8)


# ---------------------------------------------------------------------------
# Multi-confirmation tie-break
# ---------------------------------------------------------------------------


def test_move_drones_multiple_confirming_drones_others_converge_on_lowest_index() -> None:
    a = _FixedTargetStrategy(target=(5, 5))  # anchor (index 0): own strategy, unaffected
    b = _FixedTargetStrategy(target=(5, 15))  # also confirming, but not the anchor -> regroups too
    c = _FixedTargetStrategy(target=(19, 19))  # never confirming -> regroups toward index 0
    fake_rng = _FixedSequenceRandom(randoms=[1.0, 1.0, 1.0], choices=[a, b, c])
    assignment = StrategyAssignment(
        strategies=[a, b, c], drone_count=3, switch_probability=0.0, rng=fake_rng
    )  # type: ignore[arg-type]
    sim, drones, _ = _make(
        positions=[(5, 5), (5, 15), (5, 10)],
        strategy_assignment=assignment,
        range_cells=1,
        drone_speed=2,
    )
    _confirm(drones[0])
    _confirm(drones[1])

    sim.move_drones()

    assert (drones[0].row, drones[0].col) == (5, 5)  # anchor: own strategy, unaffected
    assert (drones[1].row, drones[1].col) == (5, 13)  # not the anchor -> regroups toward (5,5)
    assert (drones[2].row, drones[2].col) == (5, 8)  # regroups toward (5,5)


# ---------------------------------------------------------------------------
# Exit: regroup stops once the anchor drops below CONFIRMING
# ---------------------------------------------------------------------------


def test_move_drones_regroup_stops_once_anchor_no_longer_confirming() -> None:
    a = _FixedTargetStrategy(target=(5, 5))
    b = _FixedTargetStrategy(target=(5, 19))
    fake_rng = _FixedSequenceRandom(randoms=[1.0, 1.0, 1.0, 1.0], choices=[a, b])
    assignment = StrategyAssignment(
        strategies=[a, b], drone_count=2, switch_probability=0.0, rng=fake_rng
    )  # type: ignore[arg-type]
    sim, drones, _ = _make(positions=[(5, 5), (5, 15)], strategy_assignment=assignment)
    _confirm(drones[0])

    sim.move_drones()
    assert (drones[1].row, drones[1].col) == (5, 13)  # regrouped this turn

    drones[0].update_detection(False)  # streak resets to 0 -> SEARCHING
    sim.move_drones()

    # Back on the non-regroup path, _FixedTargetStrategy returns its raw target
    # unconditionally (no speed clamping) — drone 1 jumps straight to (5, 19),
    # not a speed-limited step toward it.
    assert (drones[1].row, drones[1].col) == (5, 19)


# ---------------------------------------------------------------------------
# Anchor's real destination is included in spacing checks
# ---------------------------------------------------------------------------


def test_move_drones_anchor_and_regrouping_drone_do_not_collide_when_anchor_moves() -> None:
    a = _FixedTargetStrategy(target=(5, 6))  # anchor moves onto drone 1's current cell
    b = _FixedTargetStrategy(target=(5, 5))  # irrelevant, overridden by regroup
    fake_rng = _FixedSequenceRandom(randoms=[1.0, 1.0], choices=[a, b])
    assignment = StrategyAssignment(
        strategies=[a, b], drone_count=2, switch_probability=0.0, rng=fake_rng
    )  # type: ignore[arg-type]
    sim, drones, _ = _make(
        positions=[(5, 5), (5, 6)], strategy_assignment=assignment, range_cells=3, drone_speed=2
    )
    _confirm(drones[0])

    sim.move_drones()

    assert (drones[0].row, drones[0].col) != (drones[1].row, drones[1].col)
    assert (drones[0].row, drones[0].col) == (5, 6)
    assert (drones[1].row, drones[1].col) == (5, 5)


def test_move_drones_holds_position_when_too_close_to_another_regrouping_drone() -> None:
    a = _FixedTargetStrategy(target=(5, 5))  # anchor stays put
    b = _FixedTargetStrategy(target=(5, 5))  # irrelevant, overridden by regroup
    c = _FixedTargetStrategy(target=(5, 5))  # irrelevant, overridden by regroup
    fake_rng = _FixedSequenceRandom(randoms=[1.0, 1.0, 1.0], choices=[a, b, c])
    assignment = StrategyAssignment(
        strategies=[a, b, c], drone_count=3, switch_probability=0.0, rng=fake_rng
    )  # type: ignore[arg-type]
    sim, drones, _ = _make(
        positions=[(5, 5), (5, 15), (5, 16)],
        strategy_assignment=assignment,
        range_cells=4,
        drone_speed=2,
    )
    _confirm(drones[0])

    sim.move_drones()

    assert (drones[0].row, drones[0].col) == (5, 5)  # anchor, unaffected
    assert (drones[1].row, drones[1].col) == (5, 13)  # far from anchor and from drone 2 -> moves
    assert (drones[2].row, drones[2].col) == (
        5,
        16,
    )  # held: too close to drone 1's newly-claimed (5,13)


def test_move_drones_regroup_converges_and_stabilizes_at_min_spacing_over_multiple_turns() -> None:
    a = _FixedTargetStrategy(target=(5, 5))  # anchor stays put every turn
    b = _FixedTargetStrategy(target=(5, 5))  # irrelevant, overridden by regroup
    fake_rng = _FixedSequenceRandom(randoms=[1.0, 1.0] * 6, choices=[a, b])
    assignment = StrategyAssignment(
        strategies=[a, b], drone_count=2, switch_probability=0.0, rng=fake_rng
    )  # type: ignore[arg-type]
    sim, drones, _ = _make(
        positions=[(5, 5), (5, 19)], strategy_assignment=assignment, range_cells=4, drone_speed=2
    )
    _confirm(drones[0])

    positions_over_time = []
    for _ in range(6):
        sim.move_drones()
        positions_over_time.append((drones[1].row, drones[1].col))

    assert positions_over_time == [
        (5, 17),
        (5, 15),
        (5, 13),
        (5, 11),
        (5, 9),
        (5, 9),  # stabilized: any further step would both close the gap and land under min_spacing
    ]
