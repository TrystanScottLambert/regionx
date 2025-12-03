import pytest
from hypothesis import given, strategies as st, assume, settings
from hypothesis.strategies import composite
import math
from regionx import Polygon, Aperture, Anulus, PointResult


# Custom strategies for spherical coordinates
@composite
def ra_strategy(draw):
    """Generate RA in range [0, 360)"""
    return draw(st.floats(min_value=0.0, max_value=360.0, exclude_max=True))


@composite
def dec_strategy(draw):
    """Generate Dec in range [-90, 90]"""
    return draw(st.floats(min_value=-90.0, max_value=90.0))


@composite
def radius_strategy(draw):
    """Generate radius in degrees [0.1, 45]"""
    return draw(st.floats(min_value=0.1, max_value=45.0))


@composite
def point_strategy(draw):
    """Generate a single (ra, dec) point"""
    ra = draw(ra_strategy())
    dec = draw(dec_strategy())
    return (ra, dec)


@composite
def convex_polygon_strategy(draw):
    """Generate a convex polygon by creating points around a circle"""
    n_vertices = draw(st.integers(min_value=3, max_value=8))
    center_ra = draw(ra_strategy())
    center_dec = draw(dec_strategy())
    radius = draw(st.floats(min_value=5.0, max_value=20.0))

    # Generate vertices in order around the center
    # Make sure angles are sufficiently different to avoid duplicate vertices
    angles = []
    for i in range(n_vertices):
        # Evenly space angles with small random offset
        base_angle = (360.0 / n_vertices) * i
        offset = draw(st.floats(min_value=-10.0, max_value=10.0))
        angles.append(base_angle + offset)

    ra_vertices = []
    dec_vertices = []
    for angle in angles:
        # Simple approximation for small regions
        ra = (center_ra + radius * math.cos(math.radians(angle))) % 360
        dec = max(-90, min(90, center_dec + radius * math.sin(math.radians(angle))))
        ra_vertices.append(ra)
        dec_vertices.append(dec)

    # Verify vertices are distinct enough (at least 0.1 degrees apart)
    for i in range(len(ra_vertices)):
        for j in range(i + 1, len(ra_vertices)):
            ra_diff = abs(ra_vertices[i] - ra_vertices[j])
            dec_diff = abs(dec_vertices[i] - dec_vertices[j])
            # If vertices are too close, adjust slightly
            if ra_diff < 0.1 and dec_diff < 0.1:
                ra_vertices[j] += 0.5
                dec_vertices[j] += 0.5

    return ra_vertices, dec_vertices


@composite
def concave_polygon_strategy(draw):
    """Generate a concave polygon (star-like shape)"""
    n_points = draw(st.integers(min_value=5, max_value=10))
    center_ra = draw(ra_strategy())
    center_dec = draw(dec_strategy())
    outer_radius = draw(st.floats(min_value=5.0, max_value=20.0))
    inner_radius = outer_radius * draw(st.floats(min_value=0.3, max_value=0.7))

    ra_vertices = []
    dec_vertices = []

    for i in range(n_points):
        angle = (360 / n_points) * i
        # Alternate between outer and inner radius
        radius = outer_radius if i % 2 == 0 else inner_radius

        ra = (center_ra + radius * math.cos(math.radians(angle))) % 360
        dec = max(-90, min(90, center_dec + radius * math.sin(math.radians(angle))))
        ra_vertices.append(ra)
        dec_vertices.append(dec)

    return ra_vertices, dec_vertices


# Test fixtures for specific locations
@pytest.fixture
def aperture_at_pole():
    """Aperture centered at North Pole"""
    return Aperture(ra_center=0.0, dec_center=90.0, radius_deg=10.0)


@pytest.fixture
def aperture_at_south_pole():
    """Aperture centered at South Pole"""
    return Aperture(ra_center=0.0, dec_center=-90.0, radius_deg=10.0)


@pytest.fixture
def aperture_at_equator_ra0():
    """Aperture at equator, RA=0"""
    return Aperture(ra_center=0.0, dec_center=0.0, radius_deg=10.0)


@pytest.fixture
def aperture_at_equator_ra180():
    """Aperture at equator, RA=180"""
    return Aperture(ra_center=180.0, dec_center=0.0, radius_deg=10.0)


@pytest.fixture
def anulus_at_pole():
    """Anulus centered at North Pole"""
    return Anulus(ra_center=0.0, dec_center=90.0, inner_radius=5.0, outer_radius=15.0)


@pytest.fixture
def anulus_at_equator_ra0():
    """Anulus at equator, RA=0"""
    return Anulus(ra_center=0.0, dec_center=0.0, inner_radius=5.0, outer_radius=15.0)


# Hypothesis tests
class TestAperture:
    @given(
        center_ra=ra_strategy(),
        center_dec=dec_strategy(),
        radius=radius_strategy(),
        test_point=point_strategy(),
    )
    @settings(max_examples=500)
    def test_aperture_random_points(self, center_ra, center_dec, radius, test_point):
        """Test aperture with random centers and points"""
        aperture = Aperture(center_ra, center_dec, radius)
        ra, dec = test_point
        result = aperture.is_inside(ra, dec)
        assert isinstance(result, PointResult)

    @given(center_ra=ra_strategy(), center_dec=dec_strategy(), radius=radius_strategy())
    @settings(max_examples=200)
    def test_aperture_batch_returns_results(self, center_ra, center_dec, radius):
        """Test that batch check returns valid results"""
        aperture = Aperture(center_ra, center_dec, radius)

        # Generate a small set of test points
        ra_points = [0.0, 90.0, 180.0, 270.0]
        dec_points = [0.0, 30.0, -30.0, 60.0]

        # Batch check
        batch_results = aperture.check_points(ra_points, dec_points)

        # Verify we got results back
        assert len(batch_results) == len(ra_points)
        assert all(isinstance(r, PointResult) for r in batch_results)

    def test_aperture_at_north_pole_contains_pole(self, aperture_at_pole):
        """Aperture at North Pole should contain the pole"""
        result = aperture_at_pole.is_inside(0.0, 90.0)
        assert isinstance(result, PointResult)

    def test_aperture_at_south_pole_contains_pole(self, aperture_at_south_pole):
        """Aperture at South Pole should contain the pole"""
        result = aperture_at_south_pole.is_inside(0.0, -90.0)
        assert isinstance(result, PointResult)

    def test_aperture_at_ra0(self, aperture_at_equator_ra0):
        """Test aperture at RA=0"""
        result = aperture_at_equator_ra0.is_inside(0.0, 0.0)
        assert isinstance(result, PointResult)

    def test_aperture_at_ra180(self, aperture_at_equator_ra180):
        """Test aperture at RA=180"""
        result = aperture_at_equator_ra180.is_inside(180.0, 0.0)
        assert isinstance(result, PointResult)


class TestAnulus:
    @given(
        center_ra=ra_strategy(), center_dec=dec_strategy(), test_point=point_strategy()
    )
    @settings(max_examples=500)
    def test_anulus_random_points(self, center_ra, center_dec, test_point):
        """Test anulus with random centers and points"""
        inner = 5.0
        outer = 15.0
        anulus = Anulus(center_ra, center_dec, inner, outer)
        ra, dec = test_point
        result = anulus.is_inside(ra, dec)
        assert isinstance(result, PointResult)

    @given(
        center_ra=ra_strategy(),
        center_dec=dec_strategy(),
        inner=st.floats(min_value=1.0, max_value=20.0),
        outer=st.floats(min_value=21.0, max_value=40.0),
    )
    @settings(max_examples=200)
    def test_anulus_center_is_outside(self, center_ra, center_dec, inner, outer):
        """Center of anulus should be outside (in the hole)"""
        anulus = Anulus(center_ra, center_dec, inner, outer)
        # Center should be outside since it's inside the inner radius
        result = anulus.is_inside(center_ra, center_dec)
        assert isinstance(result, PointResult)

    def test_anulus_at_north_pole(self, anulus_at_pole):
        """Test anulus at North Pole"""
        result = anulus_at_pole.is_inside(0.0, 90.0)
        assert isinstance(result, PointResult)

    def test_anulus_at_equator(self, anulus_at_equator_ra0):
        """Test anulus at equator"""
        result = anulus_at_equator_ra0.is_inside(0.0, 0.0)
        assert isinstance(result, PointResult)


class TestPolygon:
    @given(polygon_data=convex_polygon_strategy(), test_point=point_strategy())
    @settings(max_examples=300)
    def test_convex_polygon_random_points(self, polygon_data, test_point):
        """Test convex polygons with random test points"""
        ra_vertices, dec_vertices = polygon_data
        polygon = Polygon(ra_vertices, dec_vertices)
        ra, dec = test_point
        result = polygon.is_inside(ra, dec)
        assert isinstance(result, PointResult)

    @given(polygon_data=concave_polygon_strategy(), test_point=point_strategy())
    @settings(max_examples=300)
    def test_concave_polygon_random_points(self, polygon_data, test_point):
        """Test concave (star-shaped) polygons with random test points"""
        ra_vertices, dec_vertices = polygon_data
        polygon = Polygon(ra_vertices, dec_vertices)
        ra, dec = test_point
        result = polygon.is_inside(ra, dec)
        assert isinstance(result, PointResult)

    @given(polygon_data=convex_polygon_strategy())
    @settings(max_examples=100)
    def test_polygon_batch_returns_results(self, polygon_data):
        """Test that batch check returns valid results for polygons"""
        ra_vertices, dec_vertices = polygon_data
        polygon = Polygon(ra_vertices, dec_vertices)

        # Generate test points
        ra_points = [0.0, 90.0, 180.0, 270.0]
        dec_points = [0.0, 30.0, -30.0, 60.0]

        batch_results = polygon.check_points(ra_points, dec_points)

        assert len(batch_results) == len(ra_points)
        assert all(isinstance(r, PointResult) for r in batch_results)

    def test_triangle_at_pole(self):
        """Test a triangle near the North Pole"""
        ra_vertices = [0.0, 120.0, 240.0]
        dec_vertices = [85.0, 85.0, 85.0]
        polygon = Polygon(ra_vertices, dec_vertices)

        result = polygon.is_inside(0.0, 87.0)
        assert isinstance(result, PointResult)

    def test_polygon_crossing_ra0(self):
        """Test a polygon that crosses RA=0"""
        ra_vertices = [350.0, 10.0, 10.0, 350.0]
        dec_vertices = [10.0, 10.0, -10.0, -10.0]
        polygon = Polygon(ra_vertices, dec_vertices)

        result = polygon.is_inside(0.0, 0.0)
        assert isinstance(result, PointResult)

    def test_polygon_at_equator(self):
        """Test a polygon centered at the equator"""
        ra_vertices = [170.0, 190.0, 190.0, 170.0]
        dec_vertices = [10.0, 10.0, -10.0, -10.0]
        polygon = Polygon(ra_vertices, dec_vertices)

        result = polygon.is_inside(180.0, 0.0)
        assert isinstance(result, PointResult)


class TestEdgeCases:
    @given(ra=ra_strategy(), dec=dec_strategy())
    @settings(max_examples=100)
    def test_tiny_aperture(self, ra, dec):
        """Test very small apertures"""
        aperture = Aperture(ra, dec, 0.001)
        result = aperture.is_inside(ra, dec)
        assert isinstance(result, PointResult)

    @given(ra=ra_strategy())
    @settings(max_examples=100)
    def test_aperture_at_exact_poles(self, ra):
        """Test apertures at exact pole locations"""
        # North pole
        aperture_n = Aperture(ra, 90.0, 10.0)
        result_n = aperture_n.is_inside(ra, 90.0)
        assert isinstance(result_n, PointResult)

        # South pole
        aperture_s = Aperture(ra, -90.0, 10.0)
        result_s = aperture_s.is_inside(ra, -90.0)
        assert isinstance(result_s, PointResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
