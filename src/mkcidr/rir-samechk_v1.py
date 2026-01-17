#!/usr/bin/env python3.10

# Extract data for the same IP address from the RIR list

import os
import sys
import time
from logging import INFO, FileHandler, Formatter, StreamHandler, getLogger
from pathlib import Path
from urllib.parse import urlparse

import tqdm


def setup_logger(log_file: str = "") -> None:
    handler = StreamHandler() if log_file == "" else FileHandler(log_file)
    handler.setFormatter(
        Formatter(
            fmt="[%(asctime)s] %(threadName)s - %(message)s",
            datefmt="%Y/%m/%d-%H:%M:%S",
        ),
    )
    logger = getLogger()
    logger.setLevel(INFO)
    logger.addHandler(handler)


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


def rir_load_reformat_ipv4(RIR_URLs: list[str], EXCLUDED_COUNTRIES: list[str]) -> list[str]:
    getLogger().info("RIR Same Checker ipv4 : start")
    check_list: list[str] = []
    check_list_append = check_list.append
    getLogger().info("RIR Same Checker ipv4 : Load RIR")
    for rir_url in RIR_URLs:
        rir_filename = Path(urlparse(rir_url).path).name
        rir_registry = rir_filename.split("-")[1]
        rir_path = Path.cwd().resolve() / rir_filename
        with Path(rir_path).open() as file:
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


def rir_same_checker_ipv4(check_list: list[str]) -> None:
    getLogger().info("RIR Same Checker ipv4 : Same Check Start")
    path_ipv4 = Path.cwd().resolve() / "ipv4"
    path_ipv4.mkdir(parents=True, exist_ok=True)
    same_list: list[str] = []
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
    with Path(path_ipv4 / "_Same_RIR.ipv4").open(
        mode="w",
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
    DIR_IP_LISTS = Path(DIR_IP_LISTS).resolve()

    setup_logger()

    print("Extract duplicate listings from RIR data\n")

    if not DIR_IP_LISTS.exists():
        DIR_IP_LISTS.mkdir(parents=True)

    if not os.access(DIR_IP_LISTS, os.W_OK):
        print("You do not have write permission to the /var/ directory.\n")
        sys.exit(1)

    os.chdir(DIR_IP_LISTS)

    start = time.time()
    rir_same_checker_ipv4(rir_load_reformat_ipv4(RIR_URLs, EXCLUDED_COUNTRIES))
    print(f"processing time : {time.time() - start:,.2f} sec")

    sys.exit(0)
