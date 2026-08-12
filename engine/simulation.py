from __future__ import annotations

import random
from enum import StrEnum
from typing import Any

from engine.entities import BlueDrone, BlueMothership, RedVessel
from engine.grid import Grid
from engine.probability_map import ProbabilityMap
from engine.red_behavior import (
    RED_DETECTION_RANGE,
    blue_units_within_range,
    infiltration_zone_for,
    red_baseline_target,
    red_evasion_target,
)
from engine.search_strategy import FrontierCoverage, GreedyMaxProbability
from engine.sonar_model import SonarModel
from engine.strategy_assignment import StrategyAssignment


class GameResult(StrEnum):
    IN_PROGRESS = "in_progress"
    BLUE_WINS = "blue_wins"
    RED_WINS = "red_wins"


class Simulation:
    """Turn-based simulation rule engine.

    Entities are moved externally between turns; advance() evaluates the
    resulting board state and updates win-condition counters. Drones move
    via move_drones() (per their assigned SearchStrategy); RedVessel moves
    via move_vessel() — baseline: steps toward the infiltration zone, or
    evasion: flees the nearest drone that detected it last turn, if any.
    Both are called before advance().

    Win conditions
    --------------
    Blue wins when both streaks reach their thresholds simultaneously:
      - detection_streak  >= lock_turns
      - engagement_streak >= engagement_turns  (RedVessel also in Mothership range)
    Red wins by infiltration (RedVessel reaches the zone behind Mothership's
    spawn) or when max_turns is reached without Blue winning.

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
        probability_map: ProbabilityMap | None = None,
        strategy_assignment: StrategyAssignment | None = None,
        drone_speed: int = 2,
        vessel_speed: int = 1,
        red_detection_range: int = RED_DETECTION_RANGE,
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
        self._probability_map = (
            probability_map if probability_map is not None else ProbabilityMap(grid)
        )
        self._drone_speed = drone_speed
        self._strategy_assignment = (
            strategy_assignment
            if strategy_assignment is not None
            else StrategyAssignment(
                strategies=[GreedyMaxProbability(), FrontierCoverage()],
                drone_count=len(drones),
                rng=self._rng,
            )
        )
        self._vessel_speed = vessel_speed
        self._red_detection_range = red_detection_range
        self._infiltration_zone = infiltration_zone_for(mothership.row, grid)

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
            self._probability_map.update(
                sonar=self._sonar,
                drone=(drone.row, drone.col),
                heading=drone.heading,
                detected=detected,
                vessel_moved=self._vessel_moved,
                detection_streak=self._detection_streak,
            )
            drone.update_detection(detected, self._lock_turns)
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

    def move_drones(self) -> None:
        """Move each drone according to its currently assigned search strategy.

        Called externally before advance(), matching notify_vessel_moved()'s
        pattern: Simulation evaluates state but never moves entities on its
        own initiative.

        Drones claim distinct cells within the same turn: if a drone's computed
        target is already claimed by an earlier drone this turn, it stays in
        place instead of stacking on top of it.
        """
        if self._result is not GameResult.IN_PROGRESS:
            return

        self._strategy_assignment.advance()
        claimed: set[tuple[int, int]] = set()
        for i, drone in enumerate(self._drones):
            strategy = self._strategy_assignment.strategy_for(i)
            target = strategy.next_target(
                position=(drone.row, drone.col),
                speed=self._drone_speed,
                grid=self._grid,
                probability_map=self._probability_map,
            )
            if target in claimed:
                target = (drone.row, drone.col)
            claimed.add(target)
            drone.move(*target)

    def move_vessel(self) -> None:
        """Move RedVessel one step: flees the nearest threat if it was detected by a
        drone last turn, or if it senses a drone within its own detection range,
        otherwise heads toward the infiltration zone (baseline behavior).

        Called externally before advance(), matching move_drones()'s pattern. Reacts to
        the most recently computed detections (advance() hasn't run yet this turn).
        Its own sensing only covers drones, not BlueMothership — the mothership sits
        at the fixed objective Red is deliberately heading toward, not a reactive threat.
        """
        if self._result is not GameResult.IN_PROGRESS:
            return

        position = (self._red_vessel.row, self._red_vessel.col)
        detected = [
            (self._drones[e["drone_idx"]].row, self._drones[e["drone_idx"]].col)
            for e in self._last_detection_events
        ]
        drone_positions = [(d.row, d.col) for d in self._drones]
        aware = blue_units_within_range(position, drone_positions, self._red_detection_range)
        threats = list(dict.fromkeys(detected + aware))

        if threats:
            target = red_evasion_target(
                position=position, threats=threats, speed=self._vessel_speed, grid=self._grid
            )
        else:
            target = red_baseline_target(
                position=position,
                zone=self._infiltration_zone,
                speed=self._vessel_speed,
                grid=self._grid,
            )
        self._red_vessel.move(*target)

    def advance(self) -> GameResult:
        """Evaluate the current board state and advance one turn."""
        if self._result is not GameResult.IN_PROGRESS:
            return self._result

        self._turn += 1
        self._last_detection_events = self._compute_detections()
        self._probability_map.diffuse()
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
        elif self._infiltration_zone.contains(self._red_vessel.row, self._red_vessel.col):
            self._result = GameResult.RED_WINS
        elif self._turn >= self._max_turns:
            self._result = GameResult.RED_WINS

        self._vessel_moved = False
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

    @property
    def probability_map(self) -> ProbabilityMap:
        return self._probability_map

    def to_dict(self) -> dict[str, Any]:
        """Serialize the current game state to a JSON-compatible dict."""
        return {
            "turn": self._turn,
            "result": self._result.value,
            "mothership": {"row": self._mothership.row, "col": self._mothership.col},
            "drones": [
                {
                    "row": d.row,
                    "col": d.col,
                    "heading": list(d.heading),
                    "detection_state": d.detection_state.value,
                    "strategy": self._strategy_assignment.strategy_for(i).name,
                }
                for i, d in enumerate(self._drones)
            ],
            "vessel": {"row": self._red_vessel.row, "col": self._red_vessel.col},
            "detection_events": self._last_detection_events,
            "probability_map": self._probability_map.values.round(4).tolist(),
        }
