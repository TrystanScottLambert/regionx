import pytest
from regionx import Polygon, Aperture, Anulus, PointResult


def test_polygon_ra_edge():
    """
    Tests that a polygon will work across the 0, 360 line.
    """
    ra_points = [359, 359, 1, 1]
    dec_points = [80, 82, 82, 80]
    poly = Polygon(ra_points, dec_points)
    assert poly.is_inside(0.0, 81) == PointResult.Inside
    assert poly.is_inside(300, 80) == PointResult.Outside
    assert poly.is_inside(359, 81) == PointResult.Outside  # line is out

    eval_points_ra = [0, 300, 359]
    eval_points_dec = [81, 80, 81]
    results = poly.check_points(eval_points_ra, eval_points_dec)
    answers = [PointResult.Inside, PointResult.Outside, PointResult.Outside]
    for r, a in zip(results, answers):
        assert r == a


def test_aperture_ra_edge():
    """
    Tests that an aperture works across the 0/360 line.
    """
    app = Aperture(0, 0, 1)  # floating points are a mother
    assert app.is_inside(0, 0) == PointResult.Inside
    assert app.is_inside(0.1, 0.1) == PointResult.Inside
    assert app.is_inside(359.2, 0) == PointResult.Inside
    assert app.is_inside(0, 1) == PointResult.Inside
    assert app.is_inside(358, 0) == PointResult.Outside
    assert app.is_inside(0, 2) == PointResult.Outside

    eval_ra = [0.0, 0.1, 359.2, 0, 358, 0]
    eval_dec = [0.0, 0.1, 0, 1, 0, 2]
    results = app.check_points(eval_ra, eval_dec)
    answers = [
        PointResult.Inside,
        PointResult.Inside,
        PointResult.Inside,
        PointResult.Inside,
        PointResult.Outside,
        PointResult.Outside,
    ]
    for r, a in zip(results, answers):
        print(r)
        assert r == a


def test_anulus_ra_edge():
    """
    Tests that an aperture works across the 0/360 line.
    """
    app = Anulus(0, 0, 1, 2)  # floating points are a mother
    eval_ra = [0.0, 0.1, 358.5, 0, 358, 0]
    eval_dec = [0.0, 0.1, 0, 1, 0, 2]
    results = app.check_points(eval_ra, eval_dec)
    answers = [
        PointResult.Outside,
        PointResult.Outside,
        PointResult.Inside,
        PointResult.Inside,
        PointResult.Inside,
        PointResult.Inside,
    ]
    for r, a in zip(results, answers):
        print(r)
        assert r == a

    for ra, dec, ans in zip(eval_ra, eval_dec, answers):
        assert app.is_inside(ra, dec) == ans


def test_aperture_at_pole():
    """
    Checking that the aperture works at the pole.
    """
    app = Aperture(0, -90, 2)
    eval_ra = [0, 90, 180, 270, 0, 90, 180, 270]
    eval_dec = [-89, -88.5, -89.9, -88.1, -87.9, -87.0, -87.8, 0.0]
    answers = [
        PointResult.Inside,
        PointResult.Inside,
        PointResult.Inside,
        PointResult.Inside,
        PointResult.Outside,
        PointResult.Outside,
        PointResult.Outside,
        PointResult.Outside,
    ]
    results = app.check_points(eval_ra, eval_dec)
    for r, a in zip(results, answers):
        print(r)
        assert r == a
    for ra, dec, ans in zip(eval_ra, eval_dec, answers):
        assert app.is_inside(ra, dec) == ans
