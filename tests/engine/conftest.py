from engine.search_strategy import SearchStrategy


class _FixedSequenceRandom:
    """Deterministic stand-in for random.Random: returns queued values in order."""

    def __init__(self, randoms: list[float], choices: list[SearchStrategy]) -> None:
        self._randoms = list(randoms)
        self._choices = list(choices)

    def random(self) -> float:
        return self._randoms.pop(0)

    def choice(self, seq: list[SearchStrategy]) -> SearchStrategy:
        return self._choices.pop(0)
