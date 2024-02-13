#!/usr/bin/env python3

# Extract data for the same IP address from the RIR list

# The library "concurrent.futures" is available in Python version 3.2 or later
# and has been tested with Python 3.10.
# https://docs.python.org/ja/3/library/concurrent.futures.html


import os
import sys
import time
from logging import INFO, FileHandler, Formatter, StreamHandler, getLogger
from urllib.parse import urlparse

import tqdm


def setup_logger(log_file: str = "") -> None:
    handler = StreamHandler() if log_file == "" else FileHandler(log_file)
    handler.setFormatter(  # type: ignore
        Formatter(
            fmt="[%(asctime)s] %(threadName)s - %(message)s",
            datefmt="%Y/%m/%d-%H:%M:%S",
        ),
    )
    logger = getLogger()
    logger.setLevel(INFO)
    logger.addHandler(handler)  # type: ignore


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
    check_list = []
    check_list_append = check_list.append
    getLogger().info("RIR Same Checker ipv4 : Load RIR")
    for rir_url in RIR_URLs:
        rir_filename = os.path.basename(urlparse(rir_url).path)
        rir_registry = rir_filename.split("-")[1]
        rir_path = os.path.abspath(os.path.join(os.getcwd(), rir_filename))
        with open(rir_path) as file:
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
    same_list = []
    same_list_append = same_list.append
    if str(check_list[0].split("|")[0]) == str(check_list[1].split("|")[0]):
        required_param = restore_rir_format(check_list[0])
        same_list.append(required_param)
    for line in tqdm.tqdm(check_list):
        if str(line.split("|")[0]) == str(
            check_list[check_list.index(line) - 1].split("|")[0],
        ):
            required_param = restore_rir_format(line)
            same_list_append(required_param)
            continue
        if line == check_list[-1]:
            continue
        if str(line.split("|")[0]) == str(
            check_list[check_list.index(line) + 1].split("|")[0],
        ):
            required_param = restore_rir_format(line)
            same_list_append(required_param)
            continue
    getLogger().info("RIR Same Checker ipv4 : Write File")
    with open(
        path_ipv4 + "/_Same_RIR.ipv4",
        "w",
        encoding="utf-8",
        newline="\n",
    ) as outfile:
        for line in same_list:
            outfile.write(line)
    getLogger().info("Number of the same address : %s", int(len(same_list) / 2))
    getLogger().info("RIR Same Checker ipv4 : end")


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

    setup_logger()

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
    rir_same_checker_ipv4(rir_load_reformat_ipv4(RIR_URLs, EXCLUDED_COUNTRIES))
    print(f"processing time : {time.time() - start:,.2f} sec")

    sys.exit(0)
