use astroxide::regions::{PointLocation, SphericalAnulus, SphericalAperture, SphericalPolygon};
use pyo3::prelude::*;

#[pyclass]
pub enum PointResult {
    Inside,
    Outside,
    Edge,
}

#[pyclass]
pub struct Polygon {
    polygon: SphericalPolygon,
}

#[pymethods]
impl Polygon {
    #[new]
    pub fn new(ra_verticies: Vec<f64>, dec_verticies: Vec<f64>) -> Self {
        let polygon = SphericalPolygon::new(ra_verticies, dec_verticies).unwrap();
        Polygon { polygon }
    }
    pub fn is_inside(&self, ra_point: f64, dec_point: f64) -> PointResult {
        match self.polygon.locate_point(ra_point, dec_point) {
            PointLocation::Inside => PointResult::Inside,
            PointLocation::Outside => PointResult::Outside,
            PointLocation::OnBoundary => PointResult::Edge,
        }
    }

    pub fn locate_all(&self, ra_points: Vec<f64>, dec_points: Vec<f64>) -> Vec<PointResult> {
        let results = self.polygon.locate_points(ra_points.clone(), dec_points);
        let mut locations = Vec::with_capacity(ra_points.len());
        for result in results {
            match result {
                PointLocation::Inside => locations.push(PointResult::Inside),
                PointLocation::Outside => locations.push(PointResult::Outside),
                PointLocation::OnBoundary => locations.push(PointResult::Edge),
            }
        }
        locations
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
        match self.aperture.locate_point(ra_point, dec_point) {
            PointLocation::OnBoundary => PointResult::Edge,
            PointLocation::Inside => PointResult::Inside,
            PointLocation::Outside => PointResult::Outside,
        }
    }

    pub fn locate_all(&self, ra_points: Vec<f64>, dec_points: Vec<f64>) -> Vec<PointResult> {
        let results = self.aperture.locate_points(&ra_points, &dec_points);
        let mut locations: Vec<PointResult> = Vec::new();
        for result in results {
            match result {
                PointLocation::OnBoundary => locations.push(PointResult::Edge),
                PointLocation::Inside => locations.push(PointResult::Inside),
                PointLocation::Outside => locations.push(PointResult::Outside),
            }
        }
        locations
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
        match self.anulus.locate_point(ra_point, dec_point) {
            PointLocation::OnBoundary => PointResult::Edge,
            PointLocation::Inside => PointResult::Inside,
            PointLocation::Outside => PointResult::Outside,
        }
    }

    pub fn locate_all(&self, ra_points: Vec<f64>, dec_points: Vec<f64>) -> Vec<PointResult> {
        let results = self.anulus.locate_points(&ra_points, &dec_points);
        let mut locations: Vec<PointResult> = Vec::new();
        for result in results {
            match result {
                PointLocation::OnBoundary => locations.push(PointResult::Edge),
                PointLocation::Inside => locations.push(PointResult::Inside),
                PointLocation::Outside => locations.push(PointResult::Outside),
            }
        }
        locations
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
