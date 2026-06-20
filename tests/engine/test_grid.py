from engine.grid import Grid


def test_default_dimensions() -> None:
    g = Grid()
    assert g.rows == 50
    assert g.cols == 50


def test_custom_dimensions() -> None:
    g = Grid(rows=10, cols=20)
    assert g.rows == 10
    assert g.cols == 20


def test_in_bounds_nw_corner() -> None:
    g = Grid()
    assert g.in_bounds(0, 0) is True


def test_in_bounds_se_corner() -> None:
    g = Grid()
    assert g.in_bounds(49, 49) is True


def test_out_of_bounds_negative_row() -> None:
    g = Grid()
    assert g.in_bounds(-1, 0) is False


def test_out_of_bounds_negative_col() -> None:
    g = Grid()
    assert g.in_bounds(0, -1) is False


def test_out_of_bounds_row_equals_size() -> None:
    g = Grid()
    assert g.in_bounds(50, 0) is False


def test_out_of_bounds_col_equals_size() -> None:
    g = Grid()
    assert g.in_bounds(0, 50) is False


def test_clamp_within_bounds() -> None:
    g = Grid(rows=10, cols=10)
    assert g.clamp(5, 5) == (5, 5)


def test_clamp_negative_row() -> None:
    g = Grid(rows=10, cols=10)
    assert g.clamp(-3, 5) == (0, 5)


def test_clamp_negative_col() -> None:
    g = Grid(rows=10, cols=10)
    assert g.clamp(5, -2) == (5, 0)


def test_clamp_row_overflow() -> None:
    g = Grid(rows=10, cols=10)
    assert g.clamp(15, 5) == (9, 5)


def test_clamp_col_overflow() -> None:
    g = Grid(rows=10, cols=10)
    assert g.clamp(5, 15) == (5, 9)
