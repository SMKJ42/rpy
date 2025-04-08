use pyo3::{
    exceptions::PyIndexError,
    prelude::*,
    types::{PyFunction, PyInt, PyList},
};

/// Formats the sum of two numbers as string.
#[pyfunction]
fn add_rust_native(a: usize, b: usize) -> usize {
    a + b
}

#[pyfunction]
fn add_py_bound<'a>(a: Bound<'a, PyInt>, b: Bound<'a, PyInt>) -> PyResult<Bound<'a, PyAny>> {
    return a.add(b);
}

#[pyfunction]
fn add_py_py<'a>(a: Py<PyInt>, b: Py<PyInt>) -> PyResult<Py<PyAny>> {
    return Python::with_gil(|py| a.bind(py).add(b.bind(py)).map(|i| i.unbind()));
}

#[pyfunction]
#[pyo3(signature = (f, list))]
fn reduce<'a>(
    f: Bound<'a, PyFunction>,
    list: Bound<'a, PyList>,
) -> Result<pyo3::Bound<'a, pyo3::PyAny>, PyErr> {
    let mut list = list.iter();

    let mut acc = match list.next() {
        Some(acc) => acc,
        None => {
            return Err(PyErr::new::<PyIndexError, _>(
                "Cannot reduce an array with zero lenght.",
            ))
        }
    };

    for item in list {
        acc = f.call1((acc, item))?;
    }

    return Ok(acc);
}

#[pyfunction]
fn reduce_add(list: Vec<f64>) -> f64 {
    list.into_iter()
        .reduce(|acc, curr| acc + curr)
        .unwrap_or(0.)
}

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name = "_rpy")]
fn rpy(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(add_rust_native, m)?)?;
    m.add_function(wrap_pyfunction!(add_py_bound, m)?)?;
    m.add_function(wrap_pyfunction!(add_py_py, m)?)?;
    m.add_function(wrap_pyfunction!(reduce, m)?)?;
    m.add_function(wrap_pyfunction!(reduce_add, m)?)?;
    Ok(())
}
