#!/usr/bin/env python3.10
# -*- coding: utf-8 -*-

# RIRのIPアドレスリストのダウンロードテスト
# 並列ダウンロードとシーケンシャルダウンロードの比較

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import requests


def download(url: str) -> None:
    filename = os.path.basename(urlparse(url).path)
    response = requests.get(url)
    with open(filename, "wb") as file:
        file.write(response.content)
    return


def parallel_download(URLs: list) -> None:
    with ThreadPoolExecutor(max_workers=5) as executor:
        for url in URLs:
            executor.submit(download, url)
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

    RIR_URLs = [APNIC, ARIN, RIPENCC, LACNIC, AfriNIC]

    if not os.path.exists(WORK_DIR):
        os.makedirs(WORK_DIR)
    os.chdir(WORK_DIR)

    start = time.time()
    print("Parallel Download Start")
    parallel_download(RIR_URLs)
    process_time = time.time() - start
    print("Parallel Download Time : {:,.2f} sec".format(process_time))

    start = time.time()
    print("Sync Download Start")
    sync_download(RIR_URLs)
    process_time = time.time() - start
    print("Sync Download Time     : {:,.2f} sec".format(process_time))

    print("Download Complete")

    sys.exit(0)
