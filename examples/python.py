""" A testing area for my pyo3 functions"""

from multiprocessing import Pool
from functools import reduce

import rpy
from rpy import bench

import numpy as np
from typing import Any

ITERS = 10_000_000

def add_python(a, b):
    return a + b

def add(a, b):
    return a + b

def reduce_add_python(list: list[int]):
    return reduce(add, list)

def reduce_rust(list: list[int]) -> int:
    return rpy.reduce(add, list)

add_tests = [rpy.add_rust_native, rpy.add_py_bound, rpy.add_py_bound, add_python]
reduce_tests = [reduce_rust, reduce_add_python, np.add.reduce, rpy.reduce_add]

if __name__ == '__main__':
    p = Pool()
    add_test_handle: list[bench.PendingResult[int]] = []

    for (idx, test) in enumerate(add_tests):
        handle = bench.bench(p, test, ITERS, idx, idx + 1)
        add_test_handle.append(handle)

    reduce_test_handle: list[bench.PendingResult[int]] = []

    for (idx, test) in enumerate(reduce_tests):
        handle = bench.bench(p, test, 1, [i for i in range(ITERS)])
        reduce_test_handle.append(handle)

    add_test_results = map(lambda test: test.wait(), add_test_handle)
    reduce_test_results = map(lambda test: test.wait(), reduce_test_handle)

    for test in sorted(add_test_results):
        print(test)

    print("\n")
    
    for test in sorted(reduce_test_results):
        print(test)
