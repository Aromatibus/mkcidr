#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Extract data for the same IP address from the RIR list

# The library "concurrent.futures" is available in Python version 3.2 or later
# and has been tested with Python 3.10.
# https://docs.python.org/ja/3/library/concurrent.futures.html


import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from logging import INFO, Formatter, StreamHandler, getLogger
from urllib.parse import urlparse

import requests
import tqdm
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout
from urllib3.util import Retry


def init_logger() -> None:
    # https://qiita.com/tag1216/items/db5adcf1ddcb67cfefc8
    handler = StreamHandler()
    handler.setLevel(INFO)
    handler.setFormatter(Formatter("[%(asctime)s] [%(threadName)s] %(message)s"))
    logger = getLogger()
    logger.addHandler(handler)
    logger.setLevel(INFO)
    return


def allow_downloads(allow_time_min: int, URLs: list) -> bool:
    # Determine whether to continue based on the time(min)
    # the file was downloaded
    current_time = datetime.now().timestamp()
    for url in URLs:
        file_name = os.path.basename(urlparse(url).path)
        if not os.path.exists(file_name):
            return True
        download_time = os.path.getmtime(file_name)
        difference_time = (current_time - download_time) / 60
        if difference_time > allow_time_min:
            return True
    return False


def download(url) -> bool:
    rir_filename = os.path.basename(urlparse(url).path)
    rir_registry = rir_filename.split("-")[1]
    getLogger().info("download start : %s", rir_registry)
    try:
        retry = Retry(
            total=5,  # retry n times
            backoff_factor=2,  # wait 1, 2, 4, 8, 16 sec
            status_forcelist=[429, 500, 502, 503, 504],
        )  # retry when status code is ...
        session = requests.Session()
        session.mount("http://", HTTPAdapter(max_retries=retry))
        response = requests.get(url, timeout=(15.0, 15.0))
        session.close()
        response.raise_for_status()
    except ConnectionError as e:
        getLogger().error("  connection error : %s", rir_registry + " (" + str(e) + ")")
        return False
    except HTTPError as e:
        getLogger().error("  http error : %s", rir_registry + " (" + str(e) + ")")
        return False
    except Timeout as e:
        getLogger().error("  timeout error : %s", rir_registry + " (" + str(e) + ")")
        return False
    except RequestException as e:
        getLogger().error("  download error : %s", rir_registry + " (" + str(e) + ")")
        return False
    else:
        if response.status_code == 200:
            with open(rir_filename, "wb") as file:
                file.write(response.content)
        else:
            getLogger().error("  download error : %s", rir_registry)
            return False
    getLogger().info("download end   : %s", rir_registry)
    return True


def parallel_download(URLs: list) -> bool:
    getLogger().info("download task start")
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(download, url) for url in URLs]
        for future in as_completed(futures):
            if not future.result():
                return False
    for url in URLs:
        filename = os.path.basename(urlparse(url).path)
        if not os.path.exists(filename):
            getLogger().error("  download error : %s", filename + " (file not found)")
            return False
    getLogger().info("download task end")
    return True


def change_rir_format(line: str) -> str:
    params = line.split("|")
    params[0], params[1], params[2], params[3], params[4] = (
        params[3],
        params[4],
        params[0],
        params[1],
        params[2],
    )
    return "|".join(params[0:8])


def restore_rir_format(line: str) -> str:
    params = line.split("|")
    params[0], params[1], params[2], params[3], params[4] = (
        params[2],
        params[3],
        params[4],
        params[0],
        params[1],
    )
    return "|".join(params[0:8])


def rir_load_reformat_ipv4(RIR_URLs: list, EXCLUDED_COUNTRIES: list) -> list:
    getLogger().info("RIR Same Checker ipv4 : start")
    check_list = list()
    check_list_append = check_list.append
    getLogger().info("RIR Same Checker ipv4 : Load RIR")
    for rir_url in RIR_URLs:
        rir_filename = os.path.basename(urlparse(rir_url).path)
        rir_registry = rir_filename.split("-")[1]
        rir_path = os.path.abspath(os.path.join(os.getcwd(), rir_filename))
        with open(rir_path, "r") as file:
            for line in file:
                if line.startswith("#"):
                    continue
                params = line.split("|")
                if params[1] == "" or params[1] == rir_registry:
                    continue
                if params[1] in EXCLUDED_COUNTRIES:
                    continue
                if params[3] == "*":
                    continue
                if params[2] == "ipv4":
                    required_param = change_rir_format(line)
                    check_list_append(required_param)
    check_list.sort()
    return check_list


def rir_same_checker_ipv4(check_list: list) -> None:
    getLogger().info("RIR Same Checker ipv4 : Same Check Start")
    path_ipv4 = os.path.abspath(os.path.join(os.getcwd(), "ipv4"))
    if not os.path.exists(path_ipv4):
        os.makedirs(path_ipv4)
    same_list = list()
    same_list_append = same_list.append
    if str(check_list[0].split("|")[0]) == str(check_list[1].split("|")[0]):
        required_param = restore_rir_format(check_list[0])
        same_list.append(required_param)
    for line in tqdm.tqdm(check_list):
        if str(line.split("|")[0]) == str(
            check_list[check_list.index(line) - 1].split("|")[0]
        ):
            required_param = restore_rir_format(line)
            same_list_append(required_param)
            continue
        if line == check_list[-1]:
            continue
        if str(line.split("|")[0]) == str(
            check_list[check_list.index(line) + 1].split("|")[0]
        ):
            required_param = restore_rir_format(line)
            same_list_append(required_param)
            continue
    getLogger().info("RIR Same Checker ipv4 : Write File")
    with open(
        path_ipv4 + "/_Same_RIR.ipv4", "w", encoding="utf-8", newline="\n"
    ) as outfile:
        for line in same_list:
            outfile.write(line)
    getLogger().info("RIR Same Checker ipv4 : end")
    return


if __name__ == "__main__":
    # RIR: Regional Internet Registry
    # APNIC: Asia Pacific Network Information Centre
    APNIC = "http://ftp.apnic.net/pub/stats/apnic/delegated-apnic-extended-latest"
    # ARIN: American Registry for Internet Numbers
    ARIN = "http://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest"
    # RIPE: Reseaux IP Europeens Network Coordination Centre
    RIPENCC = "http://ftp.ripe.net/pub/stats/ripencc/delegated-ripencc-extended-latest"
    # LACNIC: The Latin American and Caribbean IP address Regional Registry
    LACNIC = "http://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-extended-latest"
    # AfriNIC: African Network Information Centre
    AfriNIC = "http://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-extended-latest"

    RIR_URLs = [APNIC, ARIN, RIPENCC, LACNIC, AfriNIC]
    EXCLUDED_COUNTRIES = ["ZZ"]

    DIR_IP_LISTS = "/var/ip-lists/"
    DIR_IP_LISTS = os.path.abspath(DIR_IP_LISTS)

    init_logger()

    print("Extract duplicate listings from RIR data")
    print("")

    if not os.path.exists(DIR_IP_LISTS):
        os.makedirs(DIR_IP_LISTS)

    if not os.access(DIR_IP_LISTS, os.W_OK):
        print("You do not have write permission to the /var/ directory.")
        print("")
        sys.exit(1)

    os.chdir(DIR_IP_LISTS)

    start = time.time()
    allow_time_min = 18 * 60  # 18 hours
    if allow_downloads(allow_time_min, RIR_URLs):
        if not parallel_download(RIR_URLs):
            print("The download was canceled because an error occurred.")
            sys.exit(1)
        print("download time : {:,.2f} sec".format(time.time() - start))
    else:
        print("The download was canceled because the specified time has not elapsed.")

    print("")
    start = time.time()
    rir_same_checker_ipv4(rir_load_reformat_ipv4(RIR_URLs, EXCLUDED_COUNTRIES))
    print("processing time : {:,.2f} sec".format(time.time() - start))

    sys.exit(0)
