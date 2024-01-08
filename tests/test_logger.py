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

if __name__ == "__main__":

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


    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    start = time()

    print("This is logger test print message.")
    print("")

    logger = getLogger(__name__)
    logger.setLevel(DEBUG)
    # 優先順位 : CRITICAL > ERROR > WARNING > INFO > DEBUG
    # INFOにした場合、INFO以上のログが出力される。DEBUGは出力されない

    #fmt = "[%(asctime)s] %(threadName)s - %(message)s"
    fmt = "[%(asctime)s.%(msecs)d][(%(process)d)%(processName)s][(%(thread)d)%(threadName)s] [%(module)s][%(funcName)s] (%(lineno)03d) : %(message)s"
    datefmt = "%Y/%m/%d-%H:%M:%S"

    handler = StreamHandler()
    handler.setFormatter(Formatter(fmt=fmt))
    handler.setFormatter(Formatter(fmt=fmt, datefmt=datefmt))
    logger.addHandler(handler)


    logger.debug("DEBUG message.")
    logger.info("INFO message.")
    logger.warning("WARNING message.")
    logger.error("ERROR message.")
    logger.critical("CRITICAL message.")

    print("")
    print("processing time : {:,.2f} sec".format(time() - start))
    sys.exit(1)
