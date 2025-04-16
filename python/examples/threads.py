"""Benchmarking io ops"""

from typing import Tuple, List
from multiprocessing import Pool
import time

def add() -> List[int]:
    arr = []
    for i in range(1_000_000):
        if i == 500_000:
            print("HALFWAY")
        arr.append(i + 1)
    return arr

def timeout():
    time.sleep(1.5)

def elapsed(start: int):
    return time.perf_counter_ns() - start

def print_sleep(s: Tuple[int, float],):
    time.sleep(s[0])
    return print(f"time for {s[0]}: {time.perf_counter_ns() - s[1]}")


if __name__ == '__main__':
    with Pool(processes=2) as p:
        t = time.perf_counter_ns()
        # .apply_async dispatches a thread that immediately starts work...
        p1 = p.apply_async(time.sleep, [1.5])
        print(f"time to queue: {elapsed(t)}")
        p2 = p.apply(time.sleep, [1])
        if not p1.ready():
            print("async still pending...")
        print(f"time to sync complete: {elapsed(t)}")
        p1.get()
        if p1.ready():
            print("async resolved...")
        print(f"time for async complete: {elapsed(t)}")
        l = [lambda x: x for _ in range(4)]
    ## we can also start a new pool
    with Pool(processes=3) as p:
        t = time.perf_counter_ns()
        # or we can even start a pool inside another pool... Probably not the best idea though.
        with Pool(processes=4) as p:
            # Notice that .map utilized the .apply_async() function and that the
            # final '1' value does not reslove with the others,
            # as the worker threads are all used and waiting to resolve.
            p.map(print_sleep, [(1,t), (1, t), (2,t), (3,t), (4,t), (1, t)], 4)
                                            #  assume queues are instant and that poll fn's on timeout are instant

                                            # 0 sec |-W------W-------W------W------Q------Q-|

                                            # 1 sec |-R------R-------W------W------W------W-|

                                            # 2 sec |-R------R-------R------W------W------R-|

                                            # 3 sec |-R------R-------R------R------W------R-|

                                            # 4 sec |-R------R-------R------R------W------R-|

                                            # 5 sec |-R------R-------R------R------R------R-|

    print("DONE")

