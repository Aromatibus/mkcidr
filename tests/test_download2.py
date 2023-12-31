#!/usr/bin/env python3.10
# -*- coding: utf-8 -*-

# RIRのIPアドレスリストのダウンロードテスト
# 並列ダウンロードとシーケンシャルダウンロードの比較

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests
from tqdm import tqdm  # https://tqdm.github.io/


def download(url: str, position: int = 0) -> None:
    filename = os.path.basename(urlparse(url).path)
    response = requests.get(url, stream=True)
    file_size = int(response.headers.get("content-length", 0))
    description = "({:0>2}) {}".format(position+1, filename).ljust(40)
    bar_format="{desc} : {percentage:3.0f}% ({remaining}) |{bar:30}| {n_fmt} / {total_fmt} ({rate_fmt})"
    with open(filename, "wb") as file, tqdm(
        bar_format=bar_format,
        position=position,
        desc=description,
        total=file_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        dynamic_ncols=True,
        leave =False,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            bar.update(len(data))
            file.write(data)
    return


def parallel_download(URLs: list, max_workers: int=0) -> None:
    if max_workers == 0:
        max_workers=len(URLs) if len(URLs) < 5 else 5
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download, url, URLs.index(url)) for url in URLs]
        for future in as_completed(futures):
            if not future.result():
                return
    #print("\n" * (max_workers+2))
    return


def sync_download(URLs: list) -> None:
    for url in URLs:
        download(url)
    return


if __name__ == "__main__":
    WORK_DIR = "./ip-list/"

    # RIR（地域インターネットレジストリ） IP List
    # fmt: off
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
    # fmt: on

    #RIR_URLs = [APNIC, ARIN, RIPENCC, LACNIC, AfriNIC]
    RIR_URLs = [APNIC, ARIN, LACNIC, AfriNIC]

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
