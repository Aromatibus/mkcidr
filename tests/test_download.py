#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# RIRのIPアドレスリストのダウンロードテスト
# 並列ダウンロードとシーケンシャルダウンロードの比較

# ライブラリ「concurrent.futures」はPythonバージョン3.2以降で利用可能であり、
# Python 3.10でテストされています。
# https://docs.python.org/ja/3/library/concurrent.futures.html

# プログレスバーの表示はライブラリ「tqdm」を利用しています。
# https://tqdm.github.io/


import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout
from tqdm import tqdm
from urllib3.util import Retry


def download(url: str, position: int = 0) -> bool:
    file_name = os.path.basename(urlparse(url).path)
    try:
        retry = Retry(
            total=5,  # retry n times
            backoff_factor=2,  # wait 1, 2, 4, 8, 16 sec
            status_forcelist=[429, 500, 502, 503, 504],
        )  # retry when status code is ...
        session = requests.Session()
        session.mount("http://", HTTPAdapter(max_retries=retry))
        response = requests.get(url, stream=True, timeout=(15.0, 15.0))
        session.close()
        response.raise_for_status()
    except ConnectionError as e:
        tqdm.write("Connection error : {}".format(file_name + " (" + str(e) + ")"))
        return False
    except HTTPError as e:
        tqdm.write("Http error : {}".format(file_name + " (" + str(e) + ")"))
        return False
    except Timeout as e:
        tqdm.write("Timeout error : {}".format(file_name + " (" + str(e) + ")"))
        return False
    except RequestException as e:
        tqdm.write("Download error : {}".format(file_name + " (" + str(e) + ")"))
        return False
    else:
        if response.status_code == 200:
            file_size = int(response.headers.get("content-length", 0))
            description = "({:0>2}) {}".format(position + 1, file_name).ljust(40)
            bar_format = (
                "{desc} : {percentage:3.0f}% ({remaining}) "
                + "|{bar:10}|"
                + " {n_fmt} ({rate_fmt}) / {total_fmt}"
            )
            with open(file_name, "wb") as file, tqdm(
                position=position,
                bar_format=bar_format,
                desc=description,
                total=file_size,
                ascii=True,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                dynamic_ncols=True,
                leave=False,
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    bar.update(len(data))
                    file.write(data)
        else:
            tqdm.write("Download error (HTTP) : {}".format(file_name))
            return False
    if not os.path.exists(file_name):
        tqdm.write("Download error (file not found) : {}".format(file_name))
        return False
    tqdm.write("Download end : {}".format(file_name))
    return True


def parallel_download(URLs: list, max_workers: int = 0) -> bool:
    if max_workers == 0:
        max_workers = len(URLs) if len(URLs) < 5 else 5
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download, url, URLs.index(url)) for url in URLs]
        for future in as_completed(futures):
            if not future.result():
                return False
    return True


def sync_download(URLs: list) -> bool:
    futures = [download(url) for url in URLs]
    if False in futures:
        return False
    return True


if __name__ == "__main__":
    # RIR（地域インターネットレジストリ） IP List
    # アジア太平洋地域:APNIC(Asia Pacific Network Information Centre)
    APNIC = "http://ftp.apnic.net/pub/stats/apnic/delegated-apnic-extended-latest"
    # 北米地域:ARIN(American Registry for Internet Numbers)
    ARIN = "http://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest"
    # 欧州地域:RIPE NCC(Reseaux IP Europeens Network Coordination Centre)
    RIPENCC = "http://ftp.ripe.net/pub/stats/ripencc/delegated-ripencc-extended-latest"
    # 中南米地域:LACNIC(The Latin American and Caribbean IP address Regional Registry)
    LACNIC = "http://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-extended-latest"
    # アフリカ地域:AfriNIC(African Network Information Centre)
    AfriNIC = "http://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-extended-latest"

    RIR_URLs = [APNIC, ARIN, RIPENCC, LACNIC, AfriNIC]
    # RIR_URLs = [APNIC, ARIN, LACNIC, AfriNIC]

    WORK_DIR = "./ip-lists/"
    if not os.path.exists(WORK_DIR):
        os.makedirs(WORK_DIR)
    os.chdir(WORK_DIR)

    start = time.time()
    print("Parallel Download      : Start")
    parallel_download(RIR_URLs)
    process_time = time.time() - start
    print("Parallel Download      : End")
    print("Parallel Download Time : {:,.2f} sec".format(process_time))
    print("")

    start = time.time()
    print("Sync Download          : Start")
    sync_download(RIR_URLs)
    process_time = time.time() - start
    print("Sync Download          : End")
    print("Sync Download Time     : {:,.2f} sec".format(process_time))

    print("")
    print("Download Complete")

    sys.exit(0)
