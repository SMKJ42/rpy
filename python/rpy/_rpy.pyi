# from rpy import add_rust_native, add_py_bound, add_py_py, reduce, reduce_add

from typing import List, Any

def add_rust_native(a: int, b: int) -> int:
    ...

def add_py_bound(a: int, b: int) -> int:
    ...

def add_py_py(a: int, b: int) -> int:
    ...

def reduce(list: List[int], f: Any) -> int:
    ...

def reduce_add(list: List[int],) -> int:
    ...
