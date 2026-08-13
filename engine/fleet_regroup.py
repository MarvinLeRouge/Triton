from __future__ import annotations

from engine.grid import Grid


def regroup_target(
    position: tuple[int, int], target: tuple[int, int], speed: int, grid: Grid
) -> tuple[int, int]:
    """Return a drone's next cell while regrouping: a step of up to `speed` directly
    toward `target` (the confirming drone's position). Mirrors red_baseline_target's
    per-axis clamped-delta movement toward a fixed point."""
    row, col = position
    step_r = max(-speed, min(speed, target[0] - row))
    step_c = max(-speed, min(speed, target[1] - col))
    return grid.clamp(row + step_r, col + step_c)
