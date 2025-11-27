use astroxide::regions::{PointLocation, SphericalPolygon};
use pyo3::prelude::*;

// A test function
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pyclass] 
enum PointResult {
    Inside,
    Outside,
    Edge,
    Antipodal,
}

#[pyfunction]
fn is_inside_polygon(ra_verticies: Vec<f64>, dec_verticies, ra_int_point, dec_int_point, ra_point, dec_point)

#[pymodule]
fn regionx(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Add your functions here
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}
