from __future__ import annotations

import numpy as np
import numpy.typing as npt

from engine.probability_map import ProbabilityMap


def fuse_maps(maps: list[ProbabilityMap]) -> npt.NDArray[np.float64]:
    """Combine multiple drones' independent maps into one consensus view: elementwise
    mean, renormalized to sum to 1. Pure - does not mutate the input maps."""
    stacked = np.stack([m.values for m in maps])
    fused = stacked.mean(axis=0)
    total = fused.sum()
    if total > 0:
        fused = fused / total
    return np.asarray(fused, dtype=np.float64)
