""" A testing area for my pyo3 functions"""

from multiprocessing import Pool
from functools import reduce
from typing import List

import numpy as np

from .. import rpy 
from ..rpy import bench

ITERS = 1_000_000

def add_python(a, b):
    return a + b

def add(a, b):
    return a + b

def reduce_add_python(nums: List[int]):
    return reduce(add, nums)

def reduce_rust(nums: List[int]) -> int:
    return rpy.reduce(f=add, nums=nums)

def numpy_reduce(nums: List[int]):
    np.add.reduce(array=nums)

add_tests = [rpy.add_py_bound, add_python]
reduce_tests = [reduce_rust, reduce_add_python, numpy_reduce, rpy.reduce_add]

if __name__ == '__main__':
    p = Pool()
    add_test_handle = bench.PendingResults([])

    for (idx, test) in enumerate(add_tests):
        handle = bench.bench(p, test, ITERS, idx, idx + 1)
        add_test_handle.append(handle)

    reduce_test_handle = bench.PendingResults([])

    for (idx, test) in enumerate(reduce_tests):
        handle = bench.bench(p, test, 1, [i for i in range(ITERS)])
        reduce_test_handle.append(handle)

    add_results = add_test_handle.wait()
    reduce_results = reduce_test_handle.wait()

    for test in list(add_results.sorted_by_time()):
        print(test)

    print("\n")

    for test in list(reduce_results.sorted_by_time()):
        print(test)
