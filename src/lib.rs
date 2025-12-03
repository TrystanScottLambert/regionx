use astroxide::regions::{PointLocation, SphericalAnulus, SphericalAperture, SphericalPolygon};
use pyo3::prelude::*;

#[pyclass]
#[derive(Debug, Clone, Copy, PartialEq, Eq)] // Add these derives
pub enum PointResult {
    Inside,
    Outside,
}

#[pymethods]
impl PointResult {
    fn __eq__(&self, other: &Self) -> bool {
        matches!(
            (self, other),
            (PointResult::Inside, PointResult::Inside)
                | (PointResult::Outside, PointResult::Outside)
        )
    }

    fn __hash__(&self) -> u64 {
        *self as u64
    }
}

fn convert_loc(location: PointLocation) -> PointResult {
    match location {
        PointLocation::Inside => PointResult::Inside,
        PointLocation::Outside => PointResult::Outside,
    }
}

#[pyclass]
pub struct Polygon {
    polygon: SphericalPolygon,
}

#[pymethods]
impl Polygon {
    #[new]
    pub fn new(ra_verticies: Vec<f64>, dec_verticies: Vec<f64>) -> Self {
        let polygon = SphericalPolygon::new(ra_verticies, dec_verticies);
        Polygon { polygon }
    }

    pub fn is_inside(&self, ra_point: f64, dec_point: f64) -> PointResult {
        convert_loc(self.polygon.locate_point(ra_point, dec_point))
    }

    pub fn check_points(&self, ra_points: Vec<f64>, dec_points: Vec<f64>) -> Vec<PointResult> {
        let results = self.polygon.locate_points(&ra_points, &dec_points);
        results.iter().map(|&result| convert_loc(result)).collect()
    }
}

#[pyclass]
pub struct Aperture {
    aperture: SphericalAperture,
}

#[pymethods]
impl Aperture {
    #[new]
    pub fn new(ra_center: f64, dec_center: f64, radius_deg: f64) -> Self {
        let sph_app = SphericalAperture::new(ra_center, dec_center, radius_deg);
        Aperture { aperture: sph_app }
    }

    pub fn is_inside(&self, ra_point: f64, dec_point: f64) -> PointResult {
        convert_loc(self.aperture.locate_point(ra_point, dec_point))
    }

    pub fn check_points(&self, ra_points: Vec<f64>, dec_points: Vec<f64>) -> Vec<PointResult> {
        let results = self.aperture.locate_points(&ra_points, &dec_points);
        results.iter().map(|&result| convert_loc(result)).collect()
    }
}

#[pyclass]
pub struct Anulus {
    anulus: SphericalAnulus,
}

#[pymethods]
impl Anulus {
    #[new]
    pub fn new(ra_center: f64, dec_center: f64, inner_radius: f64, outer_radius: f64) -> Self {
        let sph_app = SphericalAnulus::new(ra_center, dec_center, inner_radius, outer_radius);
        Anulus { anulus: sph_app }
    }

    pub fn is_inside(&self, ra_point: f64, dec_point: f64) -> PointResult {
        convert_loc(self.anulus.locate_point(ra_point, dec_point))
    }

    pub fn check_points(&self, ra_points: Vec<f64>, dec_points: Vec<f64>) -> Vec<PointResult> {
        let results = self.anulus.locate_points(&ra_points, &dec_points);
        results.iter().map(|&result| convert_loc(result)).collect()
    }
}

#[pymodule]
fn regionx(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Add your functions here
    m.add_class::<PointResult>()?;
    m.add_class::<Polygon>()?;
    m.add_class::<Anulus>()?;
    m.add_class::<Aperture>()?;
    Ok(())
}
