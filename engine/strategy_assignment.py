from __future__ import annotations

import random

from engine.search_strategy import SearchStrategy


class StrategyAssignment:
    """Assigns and independently switches each drone's search strategy.

    Each drone rolls its own Bernoulli trial every turn (`advance()`) to
    switch to a randomly picked strategy from the pool, giving an irregular,
    per-drone-independent switching cadence rather than a fixed schedule.
    """

    def __init__(
        self,
        strategies: list[SearchStrategy],
        drone_count: int,
        switch_probability: float = 0.1,
        rng: random.Random | None = None,
    ) -> None:
        if not strategies:
            raise ValueError("strategies must be non-empty.")
        self._strategies = list(strategies)
        self._switch_probability = switch_probability
        self._rng = rng if rng is not None else random.Random()
        self._current = [self._rng.choice(self._strategies) for _ in range(drone_count)]

    def strategy_for(self, drone_idx: int) -> SearchStrategy:
        return self._current[drone_idx]

    def advance(self) -> None:
        """Roll each drone's independent switch chance for this turn."""
        for i in range(len(self._current)):
            if self._rng.random() < self._switch_probability:
                self._current[i] = self._rng.choice(self._strategies)
