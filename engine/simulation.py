from __future__ import annotations

import random
from enum import StrEnum
from typing import Any

from engine.entities import BlueDrone, BlueMothership, RedVessel
from engine.grid import Grid
from engine.sonar_model import SonarModel


class GameResult(StrEnum):
    IN_PROGRESS = "in_progress"
    BLUE_WINS = "blue_wins"
    RED_WINS = "red_wins"


class Simulation:
    """Turn-based simulation rule engine.

    Entities are moved externally between turns; advance() evaluates the
    resulting board state and updates win-condition counters.

    Win conditions
    --------------
    Blue wins when both streaks reach their thresholds simultaneously:
      - detection_streak  >= lock_turns
      - engagement_streak >= engagement_turns  (RedVessel also in Mothership range)
    Red wins when max_turns is reached without Blue winning.

    Detection
    ---------
    SonarModel evaluates a probabilistic cone-shaped detection law each turn.
    Call notify_vessel_moved() before advance() to feed the speed signal.

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
        rng: random.Random | None = None,
        sonar: SonarModel | None = None,
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
        self._rng = rng if rng is not None else random.Random()
        self._sonar = sonar if sonar is not None else SonarModel()

        self._turn: int = 0
        self._detection_streak: int = 0
        self._engagement_streak: int = 0
        self._result: GameResult = GameResult.IN_PROGRESS
        self._vessel_moved: bool = False
        self._last_detection_events: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_detections(self) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for i, drone in enumerate(self._drones):
            detected, pod = self._sonar.try_detect(
                drone=(drone.row, drone.col),
                heading=drone.heading,
                target=(self._red_vessel.row, self._red_vessel.col),
                vessel_moved=self._vessel_moved,
                detection_streak=self._detection_streak,
                rng=self._rng,
            )
            if detected:
                events.append({"drone_idx": i, "pod": round(pod, 3)})
        return events

    def _in_mothership_range(self) -> bool:
        dr = abs(self._mothership.row - self._red_vessel.row)
        dc = abs(self._mothership.col - self._red_vessel.col)
        return max(dr, dc) <= self._mothership_range

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def notify_vessel_moved(self, moved: bool) -> None:
        """Signal whether RedVessel moved this turn, before calling advance()."""
        self._vessel_moved = moved

    def advance(self) -> GameResult:
        """Evaluate the current board state and advance one turn."""
        if self._result is not GameResult.IN_PROGRESS:
            return self._result

        self._turn += 1
        self._last_detection_events = self._compute_detections()
        detected = len(self._last_detection_events) > 0
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

    @property
    def grid(self) -> Grid:
        return self._grid

    @property
    def mothership(self) -> BlueMothership:
        return self._mothership

    @property
    def drones(self) -> list[BlueDrone]:
        return self._drones

    @property
    def vessel(self) -> RedVessel:
        return self._red_vessel

    def to_dict(self) -> dict[str, Any]:
        """Serialize the current game state to a JSON-compatible dict."""
        return {
            "turn": self._turn,
            "result": self._result.value,
            "mothership": {"row": self._mothership.row, "col": self._mothership.col},
            "drones": [
                {"row": d.row, "col": d.col, "heading": list(d.heading)} for d in self._drones
            ],
            "vessel": {"row": self._red_vessel.row, "col": self._red_vessel.col},
            "detection_events": self._last_detection_events,
        }
