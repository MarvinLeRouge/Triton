from __future__ import annotations

import math
import random


class SonarModel:
    """Probabilistic sonar detection model: cone geometry + exponential decay law."""

    def __init__(
        self,
        range_cells: int = 8,
        half_angle_deg: float = 60.0,
        lambda_decay: float = 0.3,
        quiet_factor: float = 0.2,
        max_attention: float = 2.0,
        attention_rate: float = 0.25,
    ) -> None:
        self._range = range_cells
        self._cos_half = math.cos(math.radians(half_angle_deg))
        self._lambda = lambda_decay
        self._quiet_factor = quiet_factor
        self._max_attention = max_attention
        self._attention_rate = attention_rate

    def in_cone(
        self,
        drone: tuple[int, int],
        heading: tuple[int, int],
        target: tuple[int, int],
    ) -> bool:
        """True if target is within the sonar cone (range and angle)."""
        dr = target[0] - drone[0]
        dc = target[1] - drone[1]
        if dr == 0 and dc == 0:
            return True
        dist = math.hypot(dr, dc)
        if dist > self._range:
            return False
        h_norm = math.hypot(heading[0], heading[1])
        if h_norm == 0:
            return False
        cos_angle = (dr * heading[0] + dc * heading[1]) / (dist * h_norm)
        return cos_angle >= self._cos_half - 1e-9

    def pod(
        self,
        distance: float,
        vessel_moved: bool,
        detection_streak: int,
    ) -> float:
        """Probability of detection in [0, 1]."""
        noise = self._quiet_factor + (1.0 - self._quiet_factor) * (1.0 if vessel_moved else 0.0)
        attention = min(self._max_attention, 1.0 + self._attention_rate * detection_streak)
        return max(0.0, min(1.0, math.exp(-self._lambda * distance) * noise * attention))

    def try_detect(
        self,
        drone: tuple[int, int],
        heading: tuple[int, int],
        target: tuple[int, int],
        vessel_moved: bool,
        detection_streak: int,
        rng: random.Random,
    ) -> tuple[bool, float]:
        """Return (detected, pod_value). Rolls only if in cone."""
        if not self.in_cone(drone, heading, target):
            return False, 0.0
        dr = target[0] - drone[0]
        dc = target[1] - drone[1]
        if dr == 0 and dc == 0:
            return True, 1.0
        p = self.pod(math.hypot(dr, dc), vessel_moved, detection_streak)
        return rng.random() < p, p
