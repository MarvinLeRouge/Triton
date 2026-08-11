from __future__ import annotations

from dataclasses import dataclass

from engine.grid import Grid

ROW_BAND_HALF = 3
COL_DEPTH = 10


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
