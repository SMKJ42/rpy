"""
    ## rpy.bench

    bench is a high level module designed to provide easy access to multiprocessing's Pool class

    ### Functions
    bench

    ### Internal functions
    _time_fn
    
    ### Classes
    TestResult
    TestResults
    PendingResult
    PendingResults

    ### Internal Classes
    _SupportsMap
    _SupportsGet
"""

import multiprocessing

from multiprocessing import pool
from typing import Callable, Protocol, TypeVar, Generic, Any, List, Self, Iterator
import timeit

T = TypeVar('T')
class _SupportsMap(Protocol):
    """Typing protocol for objects with a map method."""
    def map(self, func, iterable):
        """wrapper around the inner value's .map() function"""
        ...

class _SupportsGet(Protocol):
    """Helper class to wrap the future in an internal interface"""
    def get(self) -> T:
        """wrapper around the inner value's .get() function"""
        ...

class TestResult(Generic[T]):
    """
        ##
    """

    def __init__(self, name: str, time, res: T):
        self.name = name
        self.time = time
        self.inner = res

    def __str__(self):
        return f"TestResult({self.name}, {self.time}, {self.inner})"

    def __eq__(self, oth):
        return self.inner == oth.inner

    def __ne__(self, oth):
        return self.inner != oth.inner

    def __lt__(self, oth):
        return self.inner < oth.inner

    def __gt__(self, oth):
        return self.inner > oth.inner

    def __le__(self, oth):
        return self.inner <= oth.inner

    def __ge__(self, oth):
        return self.inner >= oth.inner

class TestResults(Generic[T]):
    """Holds the output value of the test, as well as the wall-clock time"""
    def __init__(self, vals: List[TestResult[T]]):
        self.inner = vals

    def sorted_by_time(self) -> 'TestResults[T]':
        """Returns a new list of sorted test results by time"""
        return TestResults(sorted(self.inner, key=lambda x: x.time))

    def sort(self):
        """In place sort of the test results by function name"""
        self.inner.sort()

    def __len__(self):
        return len(self.inner)

    def __iter__(self) -> Iterator[TestResult[T]]:
        return iter(self.inner)


class PendingResult(Generic[T]):
    """Holds a Pool future that is waiting to be polled with .wait()"""
    def __init__(self, name: str, fut: pool.AsyncResult):
        self.name = name
        self.fut = fut

    def __str__(self):
        return f"{self.name}: {self.fut}"

    def __eq__(self, oth):
        return self.name == oth.name

    def __ne__(self, oth):
        return self.name != oth.name

    def __lt__(self, oth):
        return self.name < oth.name

    def __gt__(self, oth):
        return self.name > oth.name

    def __le__(self, oth):
        return self.name <= oth.name

    def __ge__(self, oth):
        return self.name >= oth.name

    def wait(self) -> TestResult[T]:
        """Joins the future back into the branch"""
        time, res = self.fut.get()
        return TestResult[T](self.name, time, res)

class PendingResults(Generic[T]):
    """
        Pending Results is useful when you have a function does not take arguments,
        but is also not statically evaluated.

        Compilers are smart, and therefore statically evaluated functions such as
        ```
        def returnTrue():
            return True
        ```
        will be optimized into a static value and therefore be extremely fast.

        Such functions are not the use case of PendingResult. 
        Instead it is more usefull for something that has a side effect
        like a mutation or something that uses randomly generated values.

        Alternatively, you can construct this class with an empty 
        list and append the callbacks once the values are known.
        This will not have any significant value, but will save you 
        having to unroll the .wait() evaluation with a for loop.

        ## Example
        ```
        pend = PendingResults([])

        def sum_two_nums(a: int, b: int) -> int:
            return a + b
        
        for i in range(1_000_000):
            pend.append(sum_two_nums(i, i + 20))

        pend.wait()
        ```
    """
    def __init__(self, fns: list[PendingResult[T]]):
        self.inner = fns

    def __len__(self):
        return len(self.inner)

    def wait(self) -> TestResults[T]:
        """
        Waits for all the PendingResult(s) to resolve back to the main branch
        
        ## Returns
        A list of test results wrapped in a TestRestults class instance
        """
        results = [x.wait() for x in self.inner]
        return TestResults(results)

    def append(self, value: PendingResult[T]):
        """Functionally the same as a list.append()"""
        self.inner.append(value)

    def extend(self, value: List[PendingResult[T]]):
        """Functionally the same as a list.extend()"""
        self.inner.extend(value)

    def __iter__(self) -> Iterator[PendingResult[T]]:
        return iter(self.inner)

def _time_fn(test_fn: Callable[..., Any], iters, args, kwargs) -> tuple[float, Any]:
    result_holder = {"out": None}
    def capture_ret():
        result_holder["out"] = test_fn(*args, **kwargs)
    return timeit.timeit(capture_ret, number=iters), result_holder["out"]


def bench(p: pool.Pool, func: Callable[..., T], iters: int, *args, **kwargs) -> PendingResult:
    """
    Provides an easy to use function to perform bench testing and evaluate wall-clock time.
    Interpret results with a grain of salt.

    ## Example
    ```
    def is_true(boolean: bool) {
        return boolean
    }

    bench_tests = [is_true]

    if __name__ == '__main__':
        p = Pool()
        test_handles = PendingResults([])
        
        for test in tests:
            handle: bench.PendingResult = bench.bench(p, test, iters=10_000_000)
            test_handles.append(handle)

        test_results = test_handles.wait()

        for test in test_results:
            print(test)
    ```
    """
    result = p.apply_async(_time_fn, (func, iters, args, kwargs))
    return PendingResult(func.__name__, result)

