import time
from concurrent.futures import ThreadPoolExecutor


def task_function(index):
    print(f"Task {index} started")
    time.sleep(5)
    print(f"Task {index} completed")


if __name__ == "__main__":
    # ThreadPoolExecutor のインスタンスを作成
    with ThreadPoolExecutor(max_workers=3) as executor:
        # タスクをサブミット
        futures = [executor.submit(task_function, i) for i in range(5)]
        # シャットダウン
        # この時点で未完了のタスクはキャンセルされ、進行中のタスクも即座に中断される
        executor.shutdown(wait=False, cancel_futures=False)  # never stops
