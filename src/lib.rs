use astroxide::regions::{PointLocation, SphericalPolygon};
use pyo3::prelude::*;

// A test function
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pyclass(name = "Region")]
struct Region {
    ra_verticies: Vec<f64>,
    dec_verticies: Vec<f64>,
    ra_interior_point: f64,
    dec_interior_point: f64,
}

#[pymethods]
impl Region {
    #[new]
    fn init(
        ra_verticies: Vec<f64>,
        dec_verticies: Vec<f64>,
        ra_interior_point: f64,
        dec_interior_point: f64,
    ) -> Self {
        Region {
            ra_verticies,
            dec_verticies,
            ra_interior_point,
            dec_interior_point,
        }
    }
}

#[pymodule]
fn regionx(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Add your functions here
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}
