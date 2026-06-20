from dataclasses import dataclass


@dataclass
class Grid:
    """Discretized 2-D grid. Origin (0, 0) is the NW corner; coordinates are (row, col)."""

    rows: int = 50
    cols: int = 50

    def in_bounds(self, row: int, col: int) -> bool:
        """Return True if (row, col) is within the grid boundaries."""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def clamp(self, row: int, col: int) -> tuple[int, int]:
        """Return (row, col) clamped to valid grid bounds."""
        return max(0, min(row, self.rows - 1)), max(0, min(col, self.cols - 1))
