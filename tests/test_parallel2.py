import multiprocessing
import os
import time
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


def fibonacci_recursive(n: int = 10, position: int = 0) -> int:
    if n == 0 or n == 1:
        return n
    else:
        return fibonacci_recursive(n - 2) + fibonacci_recursive(n - 1)


def worker():
    print("Process ID: {} is starting.".format(os.getpid()))
    # getLogger().info("Process ID: {} is starting.".format(os.getpid()))
    fibonacci_recursive(30)
    print("Process ID: {} is finishing.".format(os.getpid()))
    # getLogger().info("Process ID: {} is finishing.".format(os.getpid()))


if __name__ == "__main__":
    start_time = time.time()
    num_processes = multiprocessing.cpu_count()

    init_logger()
    getLogger().info("Start")

    processes = []
    for _ in range(num_processes):
        process = multiprocessing.Process(target=worker)
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    end_time = time.time()
    elapsed_time = end_time - start_time
    getLogger().info(f"Total elapsed time: {elapsed_time} seconds.")
