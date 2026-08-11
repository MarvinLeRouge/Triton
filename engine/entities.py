from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, StrEnum, auto

from engine.grid import Grid


class Faction(Enum):
    BLUE = auto()
    RED = auto()


class DetectionState(StrEnum):
    SEARCHING = "searching"
    SIGNALING = "signaling"
    CONFIRMING = "confirming"
    TRACKING = "tracking"


def _state_for_streak(streak: int, tracking_threshold: int) -> DetectionState:
    if streak <= 0:
        return DetectionState.SEARCHING
    if streak >= tracking_threshold:
        return DetectionState.TRACKING
    if streak == tracking_threshold - 1:
        return DetectionState.CONFIRMING
    return DetectionState.SIGNALING


class Entity(ABC):
    """Base class for all game entities positioned on the grid."""

    def __init__(self, grid: Grid, row: int, col: int) -> None:
        if not grid.in_bounds(row, col):
            raise ValueError(f"Position ({row}, {col}) is out of bounds for {grid}.")
        self._grid = grid
        self._row = row
        self._col = col

    @property
    @abstractmethod
    def faction(self) -> Faction: ...

    @property
    def row(self) -> int:
        return self._row

    @property
    def col(self) -> int:
        return self._col

    def move(self, row: int, col: int) -> None:
        """Move the entity to (row, col); raises ValueError if out of bounds."""
        if not self._grid.in_bounds(row, col):
            raise ValueError(f"Position ({row}, {col}) is out of bounds for {self._grid}.")
        self._row = row
        self._col = col


class BlueMothership(Entity):
    """Blue team's stationary carrier — anchor of the search operation."""

    @property
    def faction(self) -> Faction:
        return Faction.BLUE


class BlueDrone(Entity):
    """Mobile sonar drone deployed by the BlueMothership."""

    def __init__(self, grid: Grid, row: int, col: int) -> None:
        super().__init__(grid, row, col)
        self._heading: tuple[int, int] = (0, 1)  # default: east, toward Red territory
        self._detection_streak: int = 0
        self._detection_state: DetectionState = DetectionState.SEARCHING

    @property
    def faction(self) -> Faction:
        return Faction.BLUE

    @property
    def heading(self) -> tuple[int, int]:
        return self._heading

    @property
    def detection_state(self) -> DetectionState:
        return self._detection_state

    def move(self, row: int, col: int) -> None:
        drow = row - self._row
        dcol = col - self._col
        if drow != 0 or dcol != 0:
            self._heading = (drow, dcol)
        super().move(row, col)

    def update_detection(self, detected: bool, tracking_threshold: int = 3) -> None:
        """Update this drone's own consecutive-detection streak and state.

        Note: all four states are only reachable when tracking_threshold >= 3.
        At tracking_threshold=2, SIGNALING becomes unreachable; at
        tracking_threshold<=1, both SIGNALING and CONFIRMING become unreachable.
        """
        self._detection_streak = self._detection_streak + 1 if detected else 0
        self._detection_state = _state_for_streak(self._detection_streak, tracking_threshold)


class RedVessel(Entity):
    """Red team's vessel — the search target."""

    @property
    def faction(self) -> Faction:
        return Faction.RED
