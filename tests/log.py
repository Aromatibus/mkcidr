#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from logging import INFO, FileHandler, Formatter, StreamHandler, getLogger
from time import time
from typing import Union


def setup_logger(mode: Union[str, None] = None, log_file: str = "") -> None:
    if log_file == "":
        handler = StreamHandler()
    else:
        handler = FileHandler(log_file)
    fmt="[%(asctime)s] %(threadName)s - %(message)s"
    datefmt="%Y/%m/%d-%H:%M:%S"
    handler.setFormatter(Formatter(fmt=fmt, datefmt=datefmt))
    logger = getLogger()
    logger.setLevel(INFO)
    logger.addHandler(handler)
    return


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    start = time()
    print("This is Logger test print message.")

    logger = getLogger(__name__)
    logger.debug("This is DEBUG message.")
    logger.info("This is INFO message.")
    logger.warning("This is WARNING message.")
    logger.error("This is ERROR message.")
    logger.critical("This is CRITICAL message.")

    print("processing time : {:,.2f} sec".format(time() - start))
    sys.exit(1)

    setup_logger()

    getLogger().info("")
    getLogger().debug("This is DEBUG message.")
    getLogger().info("This is INFO message.")
    getLogger().warning("This is WARNING message.")
    getLogger().error("This is ERROR message.")
    getLogger().critical("This is CRITICAL message.")
    getLogger().info("")

    print("processing time : {:,.2f} sec".format(time() - start))
    sys.exit(1)
