#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from logging import INFO, FileHandler, Formatter, StreamHandler, getLogger
from time import time
from typing import Union


def setup_logger(
    log_file: str = "",
    debug: str = "",
    info: str = "",
    warning: str = "",
    error: str = "",
    critical: str = "",
    fmt: Union[str, None] = None,
    datefmt: Union[str, None] = None
) -> None:
    """Setup logger
    %(asctime)s		    # 生成時間。YYYY-MM-DD HH:MM:SS,UUU 形式。datefmtでフォーマット変更可能
    %(created)f		    # 生成時間。time.time()が返却する形式
    %(msecs)d		    # 生成時間のミリ秒部
    %(relativeCreated)d	# logginモジュールが読み込まれてからの経過時間(ミリ秒)
    %(levelname)s		# レベル名(DEBUG, INFO, WARNING, ERROR, CRITICAL)
    %(levelno)s		    # レベル番号。DEBUGは10, INFOは20
    %(module)s		    # モジュール名
    %(pathname)s		# パス名
    %(filename)s		# ファイル名
    %(funcName)s		# 関数名
    %(lineno)d		    # 行番号
    %(message)s		    # ログメッセージ
    %(name)s		    # ロガー名
    %(process)d		    # プロセスID
    %(processName)s		# プロセス名
    %(thread)d		    # スレッドID
    %(threadName)s		# スレッド名
    """

    if log_file == "":
        if debug !="":
            debug = "debug.log"

        handler = StreamHandler()
    else:
        handler = FileHandler(log_file)

    if fmt is None:
        fmt = "[%(asctime)s] %(threadName)s - %(message)s"
    else:
        fmt = "[%(asctime)s] %(threadName)s - " + fmt
    if datefmt is None:
        datefmt = "%Y/%m/%d-%H:%M:%S"

    handler.setFormatter(Formatter(fmt=fmt, datefmt=datefmt))
    logger = getLogger()
    logger.setLevel(INFO)
    logger.addHandler(handler)
    return


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    start = time()
    print("This is logger test print message.")
    logger = getLogger(__name__)
    logger.debug("This is DEBUG message.")
    logger.info("This is INFO message.")
    logger.warning("This is WARNING message.")
    logger.error("This is ERROR message.")
    logger.critical("This is CRITICAL message.")
    print("processing time : {:,.2f} sec".format(time() - start))
    print("")

    start = time()
    print("This is getLogger test print message.")
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
