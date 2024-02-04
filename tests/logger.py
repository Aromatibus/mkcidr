import os
import sys
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING, FileHandler, Formatter, StreamHandler, getLogger
from pathlib import Path
from time import time


def set_logger(level: int | str = INFO, path: str = "") -> None:
    """Setup logger.

    https://docs.python.org/3/library/logging.html

    優先順位
    CRITICAL > ERROR > WARNING > INFO > DEBUG
    "INFO"にした場合、INFO以上のログが出力される。DEBUGは出力されない
    %(asctime)s		    # 生成時間。YYYY-MM-DD HH:MM:SS,UUU 形式。datefmtでフォーマット変更可能
    %(created)f		    # 生成時間。time()が返却する形式
    %(msecs)d		    # 生成時間のミリ秒部
    %(relativeCreated)d	# logginモジュールが読み込まれてからの経過時間(ミリ秒)
    %(levelname)s		# レベル名(DEBUG, INFO, WARNING, ERROR, CRITICAL)
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
    LEVELS = {"debug": DEBUG, "info": INFO, "warning": WARNING, "error": ERROR, "critical": CRITICAL}
    if isinstance(level, str):
        level = LEVELS.get(level.lower(), INFO)
    if isinstance(level, int):
        keys = [key for key, value in LEVELS.items() if value == int(level)]
        level = LEVELS.get(keys[0], INFO)
    logger = getLogger()
    logger.setLevel(level)
    handler = StreamHandler() if path == "" else FileHandler(path)
    handler.setFormatter(  # type: ignore
        Formatter(
            fmt="[%(asctime)s] [%(threadName)s] %(message)s",
            datefmt="%Y/%m/%d-%H:%M:%S",
        ),
    )
    # https://github.com/python/mypy/issues/12690
    logger.addHandler(handler)  # type: ignore
    return


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)

    start = time()
    print("getLogger pattern 1.")
    set_logger()
    getLogger().info("")
    getLogger().debug("This is DEBUG message.")
    getLogger().info("This is INFO message.")
    getLogger().warning("This is WARNING message.")
    getLogger().error("This is ERROR message.")
    getLogger().critical("This is CRITICAL message.")
    getLogger().info("")
    print(f"processing time : {time() - start:,.2f} sec")

    print("")
    print("")
    start = time()
    print("getLogger pattern 2. DEBUG")
    set_logger(level=DEBUG)
    getLogger().info("")
    getLogger().debug("This is DEBUG message.")
    getLogger().info("This is INFO message.")
    getLogger().warning("This is WARNING message.")
    getLogger().error("This is ERROR message.")
    getLogger().critical("This is CRITICAL message.")
    getLogger().info("")
    print(f"processing time : {time() - start:,.2f} sec")
    sys.exit(1)
