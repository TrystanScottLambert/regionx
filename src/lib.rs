use astroxide::regions::{PointLocation, SphericalPolygon};
use pyo3::prelude::*;

// A test function
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pyclass]
pub enum PointResult {
    Inside,
    Outside,
    Edge,
    Antipodal,
}

#[pyfunction]
pub fn is_inside_polygon(
    ra_verticies: Vec<f64>,
    dec_verticies: Vec<f64>,
    ra_int_point: f64,
    dec_int_point: f64,
    ra_point: f64,
    dec_point: f64,
) -> PointResult {
    let poly =
        SphericalPolygon::new(ra_verticies, dec_verticies, ra_int_point, dec_int_point).unwrap();
    let result = poly.locate_point(ra_point, dec_point);
    match result {
        PointLocation::Inside => PointResult::Inside,
        PointLocation::Outside => PointResult::Outside,
        PointLocation::OnBoundary => PointResult::Edge,
        PointLocation::Antipodal => PointResult::Antipodal,
    }
}

#[pymodule]
fn regionx(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Add your functions here
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(is_inside_polygon, m)?)?;
    m.add_class::<PointResult>()?;
    Ok(())
}
