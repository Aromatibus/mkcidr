#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    FileHandler,
    Formatter,
    StreamHandler,
    getLogger,
)
from time import time
from typing import Union


def setup_logger(
    mode: int = INFO,
    log_file: str = "",
    debug: str = "",
    info: str = "",
    warning: str = "",
    error: str = "",
    critical: str = "",
    fmt: Union[str, None] = "[%(asctime)s] %(threadName)s - %(message)s",
    datefmt: Union[str, None] = "%Y/%m/%d-%H:%M:%S"
) -> None:
    """Setup logger
    mode 優先順位
    CRITICAL > ERROR > WARNING > INFO > DEBUG
    "INFO"にした場合、INFO以上のログが出力される。DEBUGは出力されない

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
    logger = getLogger(__name__)

    MODE_VAL = (CRITICAL, ERROR, WARNING, INFO, DEBUG)
    if mode not in MODE_VAL:
        logger.setLevel(INFO)
    else:
        logger.setLevel(mode)

    if log_file == "":
        if debug !="":
            debug = "debug.log"

        handler = StreamHandler()
    else:
        handler = FileHandler(log_file)

    if fmt is None:
        fmt = None
    if datefmt is None:
        datefmt = None

    handler.setFormatter(Formatter(fmt=fmt, datefmt=datefmt))

    logger.addHandler(handler)
    return


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    start = time()
    print("getLogger pattern 1.")
    setup_logger()
    getLogger().info("")
    getLogger().debug("This is DEBUG message.")
    getLogger().info("This is INFO message.")
    getLogger().warning("This is WARNING message.")
    getLogger().error("This is ERROR message.")
    getLogger().critical("This is CRITICAL message.")
    getLogger().info("")
    print("processing time : {:,.2f} sec".format(time() - start))

    print("")
    print("")
    start = time()
    print("getLogger pattern 2. DEBUG")
    setup_logger(mode=DEBUG, fmt=None, datefmt=None)
    getLogger().info("")
    getLogger().debug("This is DEBUG message.")
    getLogger().info("This is INFO message.")
    getLogger().warning("This is WARNING message.")
    getLogger().error("This is ERROR message.")
    getLogger().critical("This is CRITICAL message.")
    getLogger().info("")
    print("processing time : {:,.2f} sec".format(time() - start))
    sys.exit(1)
