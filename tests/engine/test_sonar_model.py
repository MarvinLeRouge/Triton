import math
import random

from engine.sonar_model import SonarModel


def _sm(**kwargs: object) -> SonarModel:
    defaults: dict[str, object] = dict(
        range_cells=8,
        half_angle_deg=60.0,
        lambda_decay=0.3,
        quiet_factor=0.2,
        max_attention=2.0,
        attention_rate=0.25,
    )
    defaults.update(kwargs)
    return SonarModel(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# in_cone
# ---------------------------------------------------------------------------


def test_in_cone_same_cell_is_true() -> None:
    assert _sm().in_cone((5, 5), (0, 1), (5, 5)) is True


def test_in_cone_directly_in_heading_direction() -> None:
    # heading east (0,1), target 3 cells east → angle 0° < 60°
    assert _sm().in_cone((5, 5), (0, 1), (5, 8)) is True


def test_in_cone_within_half_angle() -> None:
    # heading east (0,1), target at 45° southeast → 45° < 60°
    assert _sm().in_cone((5, 5), (0, 1), (6, 6)) is True


def test_in_cone_outside_half_angle() -> None:
    # heading east (0,1), target directly north → 90° > 60°
    assert _sm().in_cone((5, 5), (0, 1), (4, 5)) is False


def test_in_cone_outside_range() -> None:
    assert _sm(range_cells=3).in_cone((5, 5), (0, 1), (5, 9)) is False


def test_in_cone_at_exact_range() -> None:
    assert _sm(range_cells=3).in_cone((5, 5), (0, 1), (5, 8)) is True


def test_in_cone_at_exact_half_angle() -> None:
    # half_angle=45°, target at 45° → on boundary → True
    sm = _sm(half_angle_deg=45.0)
    assert sm.in_cone((5, 5), (0, 1), (6, 6)) is True


def test_in_cone_behind_drone() -> None:
    # heading east (0,1), target 3 cells west → 180° > 60°
    assert _sm().in_cone((5, 5), (0, 1), (5, 2)) is False


# ---------------------------------------------------------------------------
# pod
# ---------------------------------------------------------------------------


def test_pod_moving_at_zero_distance() -> None:
    p = _sm(lambda_decay=0.3, quiet_factor=0.2).pod(0.0, vessel_moved=True, detection_streak=0)
    assert abs(p - 1.0) < 1e-9


def test_pod_stationary_at_zero_distance() -> None:
    p = _sm(lambda_decay=0.3, quiet_factor=0.2).pod(0.0, vessel_moved=False, detection_streak=0)
    assert abs(p - 0.2) < 1e-9


def test_pod_decays_with_distance() -> None:
    sm = _sm()
    assert sm.pod(1.0, vessel_moved=True, detection_streak=0) > sm.pod(
        4.0, vessel_moved=True, detection_streak=0
    )


def test_pod_moving_higher_than_stationary() -> None:
    sm = _sm()
    assert sm.pod(3.0, vessel_moved=True, detection_streak=0) > sm.pod(
        3.0, vessel_moved=False, detection_streak=0
    )


def test_pod_streak_increases_pod() -> None:
    sm = _sm()
    assert sm.pod(4.0, vessel_moved=True, detection_streak=4) > sm.pod(
        4.0, vessel_moved=True, detection_streak=0
    )


def test_pod_clamped_to_one() -> None:
    p = _sm(max_attention=2.0, attention_rate=0.25).pod(
        0.0, vessel_moved=True, detection_streak=100
    )
    assert p <= 1.0


def test_pod_exact_formula() -> None:
    sm = _sm(lambda_decay=0.3, quiet_factor=0.2, max_attention=2.0, attention_rate=0.25)
    expected = math.exp(-0.3 * 2.0)  # moving, streak=0, r=2 → noise=1.0, attn=1.0
    assert abs(sm.pod(2.0, vessel_moved=True, detection_streak=0) - expected) < 1e-9


# ---------------------------------------------------------------------------
# try_detect
# ---------------------------------------------------------------------------


def test_try_detect_outside_cone_returns_false_and_zero() -> None:
    detected, p = _sm().try_detect(
        (5, 5), (0, 1), (4, 5), vessel_moved=True, detection_streak=0, rng=random.Random(0)
    )
    assert detected is False
    assert p == 0.0


def test_try_detect_same_cell_always_detects() -> None:
    for seed in range(10):
        detected, p = _sm().try_detect(
            (5, 5), (0, 1), (5, 5), vessel_moved=False, detection_streak=0, rng=random.Random(seed)
        )
        assert detected is True
        assert p == 1.0


def test_try_detect_high_pod_usually_detects() -> None:
    sm = _sm(lambda_decay=0.01, quiet_factor=0.99)
    hits = sum(
        sm.try_detect(
            (5, 5), (0, 1), (5, 6), vessel_moved=True, detection_streak=0, rng=random.Random(i)
        )[0]
        for i in range(20)
    )
    assert hits > 15


def test_try_detect_range_zero_never_detects_distant() -> None:
    detected, _ = _sm(range_cells=0).try_detect(
        (5, 5), (0, 1), (5, 6), vessel_moved=True, detection_streak=0, rng=random.Random(0)
    )
    assert detected is False
