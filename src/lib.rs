use pyo3::{
    prelude::*,
    types::{PyFunction, PyInt, PyList},
};

#[pyfunction]
fn add_py_bound<'a>(a: Bound<'a, PyInt>, b: Bound<'a, PyInt>) -> PyResult<Bound<'a, PyAny>> {
    return a.add(b);
}

#[pyfunction]
#[pyo3(signature = (nums, f))]
fn reduce<'a>(
    nums: Bound<'a, PyList>,
    f: Bound<'a, PyFunction>,
) -> PyResult<Option<Bound<'a, PyAny>>> {
    let mut list = nums.iter();

    let mut acc = match list.next() {
        Some(acc) => acc,
        None => return Ok(None),
    };

    for item in list {
        acc = f.call1((acc, item))?;
    }

    return Ok(Some(acc));
}

#[pyfunction]
fn reduce_add(nums: Vec<f64>) -> f64 {
    nums.into_iter()
        .reduce(|acc, curr| acc + curr)
        .unwrap_or(0.)
}

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name = "_rpy")]
fn rpy(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(add_py_bound, m)?)?;
    m.add_function(wrap_pyfunction!(reduce, m)?)?;
    m.add_function(wrap_pyfunction!(reduce_add, m)?)?;
    Ok(())
}
