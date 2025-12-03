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
