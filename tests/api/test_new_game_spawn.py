from api.main import _spawn_red_vessel
from engine.grid import Grid


class _FixedSequenceRandom:
    """Deterministic stand-in for random.Random: returns queued values in order."""

    def __init__(self, values: list[object]) -> None:
        self._values = list(values)

    def choice(self, seq: object) -> object:
        return self._values.pop(0)

    def randint(self, a: int, b: int) -> int:
        value = self._values.pop(0)
        assert isinstance(value, int)
        return value


def test_spawn_red_vessel_avoids_occupied_cell() -> None:
    grid = Grid(rows=20, cols=20)
    # border="north", dist=2 -> first attempt col=5 collides with occupied
    # cell (2, 5); the retry must land on col=7 instead.
    rng = _FixedSequenceRandom(["north", 2, 5, 7])
    occupied = {(2, 5)}

    vessel = _spawn_red_vessel(grid, rng, occupied)  # type: ignore[arg-type]

    assert (vessel.row, vessel.col) == (2, 7)
    assert (vessel.row, vessel.col) not in occupied


def test_spawn_red_vessel_returns_immediately_when_first_attempt_is_free() -> None:
    grid = Grid(rows=20, cols=20)
    rng = _FixedSequenceRandom(["east", 3, 10])
    occupied: set[tuple[int, int]] = set()

    vessel = _spawn_red_vessel(grid, rng, occupied)  # type: ignore[arg-type]

    assert (vessel.row, vessel.col) == (10, grid.cols - 1 - 3)
