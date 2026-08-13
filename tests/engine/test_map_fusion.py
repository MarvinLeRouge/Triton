import numpy as np

from engine.grid import Grid
from engine.map_fusion import fuse_maps
from engine.probability_map import ProbabilityMap


def _pm(**kwargs: object) -> ProbabilityMap:
    defaults: dict[str, object] = dict(
        grid=Grid(rows=10, cols=10),
        spawn_min_dist=100,
        spawn_max_dist=100,  # bands out of range -> uniform floor prior
        floor=1e-6,
    )
    defaults.update(kwargs)
    return ProbabilityMap(**defaults)  # type: ignore[arg-type]


def test_fuse_maps_averages_elementwise() -> None:
    a = _pm()
    b = _pm()
    a.values[0, 0] = 0.5
    b.values[0, 0] = 0.1

    fused = fuse_maps([a, b])

    # elementwise mean before renormalization at this cell is (0.5 + 0.1) / 2 = 0.3;
    # after renormalization the ratio between this cell and any untouched cell is preserved
    untouched_before = (a.values[5, 5] + b.values[5, 5]) / 2
    assert fused[0, 0] / fused[5, 5] == (0.3 / untouched_before)


def test_fuse_maps_renormalizes_to_one() -> None:
    a = _pm()
    b = _pm()
    a.values[0, 0] = 0.5
    b.values[0, 0] = 0.1

    fused = fuse_maps([a, b])

    assert abs(float(fused.sum()) - 1.0) < 1e-9


def test_fuse_maps_single_map_is_equivalent_to_itself() -> None:
    a = _pm()
    fused = fuse_maps([a])
    assert np.allclose(fused, a.values)


def test_fuse_maps_does_not_mutate_inputs() -> None:
    a = _pm()
    b = _pm()
    before_a = a.values.copy()
    before_b = b.values.copy()

    fuse_maps([a, b])

    assert np.array_equal(a.values, before_a)
    assert np.array_equal(b.values, before_b)


def test_fuse_maps_nonnegative() -> None:
    a = _pm()
    b = _pm()
    fused = fuse_maps([a, b])
    assert bool((fused >= 0.0).all())
