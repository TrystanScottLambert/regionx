use astroxide::regions::{PointLocation, SphericalAnulus, SphericalAperture, SphericalPolygon};
use pyo3::prelude::*;

#[pyclass]
pub enum PointResult {
    Inside,
    Outside,
    Edge,
}

#[pyfunction]
pub fn is_inside_polygon(
    ra_verticies: Vec<f64>,
    dec_verticies: Vec<f64>,
    ra_point: f64,
    dec_point: f64,
) -> PointResult {
    let poly = SphericalPolygon::new(ra_verticies, dec_verticies).unwrap();
    let result = poly.locate_point(ra_point, dec_point);
    match result {
        PointLocation::Inside => PointResult::Inside,
        PointLocation::Outside => PointResult::Outside,
        PointLocation::OnBoundary => PointResult::Edge,
    }
}

#[pyfunction]
pub fn is_inside_aperture(
    ra_center: f64,
    dec_center: f64,
    radius_deg: f64,
    ra_point: f64,
    dec_point: f64,
) -> PointResult {
    let app = SphericalAperture::new(ra_center, dec_center, radius_deg);
    let result = app.locate_point(ra_point, dec_point);
    match result {
        PointLocation::Inside => PointResult::Inside,
        PointLocation::Outside => PointResult::Outside,
        PointLocation::OnBoundary => PointResult::Edge,
    }
}

#[pyfunction]
pub fn is_inside_annulus(
    ra_center: f64,
    dec_center: f64,
    inner_radius_deg: f64,
    outer_radius_deg: f64,
    ra_point: f64,
    dec_point: f64,
) -> PointResult {
    let ann = SphericalAnulus::new(ra_center, dec_center, inner_radius_deg, outer_radius_deg);
    let result = ann.locate_point(ra_point, dec_point);
    match result {
        PointLocation::Inside => PointResult::Inside,
        PointLocation::Outside => PointResult::Outside,
        PointLocation::OnBoundary => PointResult::Edge,
    }
}

#[pymodule]
fn regionx(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Add your functions here
    m.add_function(wrap_pyfunction!(is_inside_polygon, m)?)?;
    m.add_function(wrap_pyfunction!(is_inside_annulus, m)?)?;
    m.add_function(wrap_pyfunction!(is_inside_aperture, m)?)?;
    m.add_class::<PointResult>()?;
    Ok(())
}
