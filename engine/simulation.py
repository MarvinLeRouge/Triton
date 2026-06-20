from __future__ import annotations

from enum import Enum, auto

from engine.entities import BlueDrone, BlueMothership, RedVessel
from engine.grid import Grid


class GameResult(Enum):
    IN_PROGRESS = auto()
    BLUE_WINS = auto()
    RED_WINS = auto()


class Simulation:
    """Turn-based simulation skeleton.

    Entities are moved externally between turns; advance() evaluates the
    resulting board state and updates win-condition counters.

    Win conditions
    --------------
    Blue wins when both streaks reach their thresholds simultaneously:
      - detection_streak  >= lock_turns       (drone tracks RedVessel)
      - engagement_streak >= engagement_turns  (RedVessel also in Mothership range)
    Red wins when max_turns is reached without Blue winning.

    Detection (Phase 1 placeholder)
    --------------------------------
    A drone detects the RedVessel when they share the same cell.
    Phase 2 will replace this with a sonar-cone probability model.

    Range metric
    ------------
    Mothership range uses Chebyshev distance: max(|Δrow|, |Δcol|).
    """

    def __init__(
        self,
        grid: Grid,
        mothership: BlueMothership,
        drones: list[BlueDrone],
        red_vessel: RedVessel,
        max_turns: int = 200,
        lock_turns: int = 3,
        mothership_range: int = 5,
        engagement_turns: int = 2,
    ) -> None:
        positions = (
            [(mothership.row, mothership.col)]
            + [(d.row, d.col) for d in drones]
            + [(red_vessel.row, red_vessel.col)]
        )
        if len(positions) != len(set(positions)):
            raise ValueError("Two or more entities share the same starting cell.")

        self._grid = grid
        self._mothership = mothership
        self._drones = list(drones)
        self._red_vessel = red_vessel
        self._max_turns = max_turns
        self._lock_turns = lock_turns
        self._mothership_range = mothership_range
        self._engagement_turns = engagement_turns

        self._turn: int = 0
        self._detection_streak: int = 0
        self._engagement_streak: int = 0
        self._result: GameResult = GameResult.IN_PROGRESS

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _detects_any(self) -> bool:
        return any(
            d.row == self._red_vessel.row and d.col == self._red_vessel.col for d in self._drones
        )

    def _in_mothership_range(self) -> bool:
        dr = abs(self._mothership.row - self._red_vessel.row)
        dc = abs(self._mothership.col - self._red_vessel.col)
        return max(dr, dc) <= self._mothership_range

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def advance(self) -> GameResult:
        """Evaluate the current board state and advance one turn.

        Must be called after all entity moves for the turn have been applied.
        Returns the current GameResult; repeated calls after game-over are no-ops.
        """
        if self._result is not GameResult.IN_PROGRESS:
            return self._result

        self._turn += 1

        detected = self._detects_any()
        in_range = self._in_mothership_range()

        if detected:
            self._detection_streak += 1
        else:
            self._detection_streak = 0

        if detected and in_range:
            self._engagement_streak += 1
        else:
            self._engagement_streak = 0

        if (
            self._detection_streak >= self._lock_turns
            and self._engagement_streak >= self._engagement_turns
        ):
            self._result = GameResult.BLUE_WINS
        elif self._turn >= self._max_turns:
            self._result = GameResult.RED_WINS

        return self._result

    @property
    def turn(self) -> int:
        return self._turn

    @property
    def result(self) -> GameResult:
        return self._result
