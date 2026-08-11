import pytest

from engine.search_strategy import FrontierCoverage, GreedyMaxProbability
from engine.strategy_assignment import StrategyAssignment
from tests.engine.conftest import _FixedSequenceRandom


def test_initial_assignment_picks_from_pool() -> None:
    greedy = GreedyMaxProbability()
    frontier = FrontierCoverage()
    rng = _FixedSequenceRandom(randoms=[], choices=[greedy, frontier])
    assignment = StrategyAssignment(strategies=[greedy, frontier], drone_count=2, rng=rng)  # type: ignore[arg-type]
    assert assignment.strategy_for(0) is greedy
    assert assignment.strategy_for(1) is frontier


def test_advance_switches_drone_when_roll_is_below_probability() -> None:
    greedy = GreedyMaxProbability()
    frontier = FrontierCoverage()
    rng = _FixedSequenceRandom(randoms=[0.05, 0.99], choices=[greedy, greedy, frontier])
    assignment = StrategyAssignment(
        strategies=[greedy, frontier], drone_count=2, switch_probability=0.1, rng=rng
    )  # type: ignore[arg-type]

    assignment.advance()

    assert assignment.strategy_for(0) is frontier  # rolled 0.05 < 0.1 → switched
    assert assignment.strategy_for(1) is greedy  # rolled 0.99 >= 0.1 → unchanged


def test_advance_with_zero_probability_never_switches() -> None:
    greedy = GreedyMaxProbability()
    rng = _FixedSequenceRandom(randoms=[0.0], choices=[greedy])
    assignment = StrategyAssignment(
        strategies=[greedy], drone_count=1, switch_probability=0.0, rng=rng
    )  # type: ignore[arg-type]

    assignment.advance()

    assert assignment.strategy_for(0) is greedy


def test_advance_with_full_probability_always_switches() -> None:
    greedy = GreedyMaxProbability()
    frontier = FrontierCoverage()
    rng = _FixedSequenceRandom(randoms=[0.999], choices=[greedy, frontier])
    assignment = StrategyAssignment(
        strategies=[greedy, frontier], drone_count=1, switch_probability=1.0, rng=rng
    )  # type: ignore[arg-type]

    assignment.advance()

    assert assignment.strategy_for(0) is frontier


def test_drones_switch_independently() -> None:
    greedy = GreedyMaxProbability()
    frontier = FrontierCoverage()
    # drone 0 rolls below threshold (switches), drone 1 rolls above (stays)
    rng = _FixedSequenceRandom(randoms=[0.01, 0.5], choices=[greedy, greedy, frontier])
    assignment = StrategyAssignment(
        strategies=[greedy, frontier], drone_count=2, switch_probability=0.2, rng=rng
    )  # type: ignore[arg-type]

    assignment.advance()

    assert assignment.strategy_for(0) is frontier
    assert assignment.strategy_for(1) is greedy


def test_empty_strategies_raises() -> None:
    with pytest.raises(ValueError):
        StrategyAssignment(strategies=[], drone_count=1)
