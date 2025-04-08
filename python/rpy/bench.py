from typing import Any, Callable, Protocol, TypeVar, Generic
import timeit
import multiprocessing
from multiprocessing import pool, Pool

T = TypeVar('T')

class SupportsMap(Protocol):
    """Typing protocol for objects with a map method."""
    def map(self, func, iterable):
        ...

class SupportsGet(Protocol):
    def get(self) -> T:
        ...

class TestResult(Generic[T]):
    def __init__(self, name: str, inner: T):
        self.name = name
        self.inner = inner

    def __str__(self):
        return f"{self.name}: {self.inner}"

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
        res = self.res.get()
        return TestResult[T](self.name, res)

def _time_fn(this_test, iters, args):
    return timeit.timeit(lambda: this_test(*args), number=iters)

def bench(p: SupportsMap, func: Callable[[int, int], int], iters: int, *args, **kwargs) -> PendingResult:
    result = p.apply_async(_time_fn, (func, iters, args))
    return PendingResult(func.__name__, result)