#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# ライブラリ「concurrent.futures」はPythonバージョン3.2以降で利用可能であり、
# Python 3.10でテストされています。
# https://docs.python.org/ja/3/library/concurrent.futures.html


import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from logging import INFO, Formatter, StreamHandler, getLogger


def init_logger() -> None:
    # https://qiita.com/tag1216/items/db5adcf1ddcb67cfefc8
    handler = StreamHandler()
    handler.setLevel(INFO)
    handler.setFormatter(Formatter("[%(asctime)s] [%(threadName)s] %(message)s"))
    logger = getLogger()
    logger.addHandler(handler)
    logger.setLevel(INFO)
    return


def fibonacci(n: int = 30) -> int:
    if n == 0 or n == 1:
        return n
    else:
        return fibonacci(n - 2) + fibonacci(n - 1)

def worker(n: int) -> int:
    getLogger().info("fibonacci start : pid(%s)", os.getpid())
    result = fibonacci(n)
    getLogger().info("fibonacci end   : result = %s", result)
    return result


def adjustment_parallel(VALUES: list) -> bool:
    MAX_THREADS = 5
    cores = os.cpu_count()
    cores = cores if cores is not None else 1
    if cores > MAX_THREADS:
        PoolExecutor = ProcessPoolExecutor(max_workers=None)
    else:
        PoolExecutor = ThreadPoolExecutor(max_workers=MAX_THREADS)
    with PoolExecutor as executor:
        futures = [executor.submit(fibonacci, n=petal) for petal in VALUES]
        for future in as_completed(futures):
            if not future.result():
                return False
    return True


def parallel_Process(VALUES: list) -> bool:
    #PoolExecutor = ProcessPoolExecutor(max_workers=None)
    PoolExecutor = ThreadPoolExecutor(max_workers=None)
    with PoolExecutor as executor:
        futures = [executor.submit(worker, n=n) for n in VALUES]
        for future in as_completed(futures):
            #print(future.result())
            if not future.result():
                return False
    return True


def sync(VALUES: list) -> bool:
    futures = [fibonacci(n) for n in VALUES]
    if False in futures:
        return False
    return True


if __name__ == "__main__":
    N = 30
    VALUES = [N] * 10
    print("VALUES : {}".format(VALUES))
    CORES = os.cpu_count()
    print("CPU Cores : {}".format(CORES))

    init_logger()
    getLogger().info("Parallel Process Test Start")

    getLogger().info("Parallel      : Start")
    start = time.time()
    parallel_Process(VALUES)
    process_time = time.time() - start
    getLogger().info("Parallel      : End")
    getLogger().info("Parallel Time : {:,.2f} sec".format(process_time))
    getLogger().info("")

    getLogger().info("Sync          : Start")
    start = time.time()
    sync(VALUES)
    process_time = time.time() - start
    getLogger().info("Sync          : End")
    getLogger().info("Sync Time     : {:,.2f} sec".format(process_time))

    getLogger().info("")
    getLogger().info("Parallel Process Test End")

    sys.exit(1)
