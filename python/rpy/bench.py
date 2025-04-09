"""
    ## rpy.bench

    bench is a high level module designed to provide easy access to the pool function

    ### Functions

    ### Classes
"""

from typing import Callable, Protocol, TypeVar, Generic, Any, List, Self, Iterator
import timeit

T = TypeVar('T')

class SupportsMap(Protocol):
    """Typing protocol for objects with a map method."""
    def map(self, func, iterable):
        ...

class SupportsGet(Protocol):
    def get(self) -> T:
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
    def __init__(self, fns: List[Callable[..., T]]):
        self.inner = fns

    def sorted_by_time(self) -> Self:
        return TestResults(sorted(self.inner, key=lambda x: x.time))
    
    def sort(self):
        self.inner.sort()

    def __len__(self):
        return len(self.inner)

    def __iter__(self) -> Iterator[Self]:
        return self.inner.__iter__()


class PendingResult(Generic[T]):
    def __init__(self, name: str, fut: SupportsGet):
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
        time, res = self.fut.get()
        return TestResult[T](self.name, time, res)

class PendingResults(Generic[T]):
    """
        Pending Results is useful when you have a function does not take arguments, but is also not statically evaluated.

        Compilers are smart, and therefore statically evaluated functions such as
        ```
        def returnTrue():
            return True
        ```
        will be optimized into a static value and therefore be extremely fast.

        Such functions are not the use case of PendingResult. Instead it is more usefull for something that has a side effect
        like a mutation or something that uses randomly generated values.

        Alternatively, you can construct this class with an empty list and append the callbacks once the values are known.
        This will not have any significant value, but will save you having to unroll the .wait evaluation with a for loop.

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
        results = [x.wait() for x in self.inner]
        return TestResults(results)

    def append(self, value: T):
        self.inner.append(value)

    def extend(self, value: T):
        self.inner.extend(value)

    def __iter__(self) -> Iterator[Callable[..., T]]:
        return self.inner.__iter__()

def _time_fn(test_fn: Callable[..., Any], iters, args, kwargs) -> tuple[float, T]:
    result_holder = {"out": 0}
    def capture_ret():
        result_holder["out"] = test_fn(*args, **kwargs)
    return timeit.timeit(capture_ret, number=iters), result_holder["out"]


def bench(p: SupportsMap, func: Callable[..., Any], iters: int, *args, **kwargs) -> PendingResult:
    """
    Provides an easy to use function to 

    ```
    def is_true(boolean: bool) {
        return boolean
    }

    bench_tests = [is_true]

    if __name__ == '__main__':
        p = Pool()
        test_handles = []
        
        for test in tests:
            handle: bench.PendingResult = bench.bench(p, test, iters=10_000_000)
            test_handles.append(handle)

        test_results = map(lambda test: test.wait(), test_handles)

        for test in test_results:
            print(test)
    ```
    """
    result = p.apply_async(_time_fn, (func, iters, args, kwargs))
    return PendingResult(func.__name__, result)