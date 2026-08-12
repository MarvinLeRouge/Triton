from __future__ import annotations

from dataclasses import dataclass

from engine.grid import Grid

ROW_BAND_HALF = 3
COL_DEPTH = 10
RED_DETECTION_RANGE = 10


@dataclass(frozen=True)
class InfiltrationZone:
    """Rectangular zone behind BlueMothership's spawn: reaching it wins the game for Red."""

    row_min: int
    row_max: int
    col_min: int
    col_max: int

    def contains(self, row: int, col: int) -> bool:
        return self.row_min <= row < self.row_max and self.col_min <= col < self.col_max


def infiltration_zone_for(mothership_row: int, grid: Grid) -> InfiltrationZone:
    """Build the infiltration zone from BlueMothership's spawn row: a fixed-depth band
    hugging the west edge, ROW_BAND_HALF rows above/below the mothership's row."""
    row_min = max(0, mothership_row - ROW_BAND_HALF)
    row_max = min(grid.rows, mothership_row + ROW_BAND_HALF)
    col_max = min(grid.cols, COL_DEPTH)
    return InfiltrationZone(row_min=row_min, row_max=row_max, col_min=0, col_max=col_max)


def red_baseline_target(
    position: tuple[int, int], zone: InfiltrationZone, speed: int, grid: Grid
) -> tuple[int, int]:
    """Return RedVessel's next cell: a step of up to `speed` toward the nearest cell in `zone`."""
    row, col = position
    target_row = min(max(row, zone.row_min), zone.row_max - 1)
    target_col = min(max(col, zone.col_min), zone.col_max - 1)
    step_r = max(-speed, min(speed, target_row - row))
    step_c = max(-speed, min(speed, target_col - col))
    return grid.clamp(row + step_r, col + step_c)


def _chebyshev(a: tuple[int, int], b: tuple[int, int]) -> int:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _sign(x: int) -> int:
    return (x > 0) - (x < 0)


def blue_units_within_range(
    position: tuple[int, int],
    blue_positions: list[tuple[int, int]],
    detection_range: int,
) -> list[tuple[int, int]]:
    """Return the Blue unit positions within RedVessel's own omnidirectional sensing
    range (Chebyshev distance) — independent of whether Blue's sonar detected Red."""
    return [p for p in blue_positions if _chebyshev(position, p) <= detection_range]


def red_evasion_target(
    position: tuple[int, int], threats: list[tuple[int, int]], speed: int, grid: Grid
) -> tuple[int, int]:
    """Return RedVessel's next cell: a step of up to `speed` directly away from the
    nearest threat (drone that detected it this turn), ignoring the infiltration zone."""
    row, col = position
    nearest = min(threats, key=lambda t: _chebyshev(position, t))
    step_r = _sign(row - nearest[0]) * speed
    step_c = _sign(col - nearest[1]) * speed
    return grid.clamp(row + step_r, col + step_c)
