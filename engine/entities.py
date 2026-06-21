from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto

from engine.grid import Grid


class Faction(Enum):
    BLUE = auto()
    RED = auto()


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

    @property
    def faction(self) -> Faction:
        return Faction.BLUE


class RedVessel(Entity):
    """Red team's vessel — the search target."""

    @property
    def faction(self) -> Faction:
        return Faction.RED
