#!/usr/bin/env python3.10

# Extract data for the same IP address from the RIR list

import os
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
    p = line.rstrip().split("|")
    # 0:registry, 1:cc, 2:type, 3:start, 4:value -> 3, 4, 0, 1, 2
    new_params = [p[3], p[4], p[0], p[1], p[2], *p[5:8]]
    return "|".join(new_params)


def restore_rir_format(line: str) -> str:
    p = line.split("|")
    # 0:start, 1:value, 2:registry, 3:cc, 4:type -> 2, 3, 4, 0, 1
    new_params = [p[2], p[3], p[4], p[0], p[1], *p[5:8]]
    return "|".join(new_params)


def rir_load_reformat_ipv4(rir_urls: list[str], excluded_countries: list[str]) -> list[str]:
    getLogger().info("RIR Same Checker ipv4 : start")
    check_list: list[str] = []
    getLogger().info("RIR Same Checker ipv4 : Load RIR")
    MIN_RIR_PARAMS = 5

    for rir_url in rir_urls:
        rir_filename = Path(urlparse(rir_url).path).name
        rir_registry = rir_filename.split("-")[1]
        rir_path = Path.cwd().resolve() / rir_filename

        if not rir_path.exists():
            continue

        with rir_path.open() as file:
            for line in file:
                if line.startswith("#"):
                    continue
                params = line.split("|")
                if len(params) < MIN_RIR_PARAMS:
                    continue
                if params[1] == "" or params[1] == rir_registry:
                    continue
                if params[1] in excluded_countries:
                    continue
                if params[3] == "*":
                    continue
                if params[2] == "ipv4":
                    check_list.append(change_rir_format(line))

    check_list.sort()
    return check_list


def rir_same_checker_ipv4(check_list: list[str]) -> None:
    getLogger().info("RIR Same Checker ipv4 : Same Check Start")
    path_ipv4 = Path.cwd().resolve() / "ipv4"
    path_ipv4.mkdir(parents=True, exist_ok=True)

    MIN_ENTRIES_FOR_COMPARISON = 2
    same_list: list[str] = []
    n = len(check_list)
    if n < MIN_ENTRIES_FOR_COMPARISON:
        return

    # IPアドレス(index 0)が重複しているものを抽出 (O(N)で処理)
    is_same = [False] * n
    for i in range(n - 1):
        if check_list[i].split("|")[0] == check_list[i + 1].split("|")[0]:
            is_same[i] = True
            is_same[i + 1] = True

    same_list = [restore_rir_format(check_list[i]) for i in tqdm.tqdm(range(n)) if is_same[i]]

    getLogger().info("RIR Same Checker ipv4 : Write File")
    output_file = path_ipv4 / "_Same_RIR.ipv4"
    with output_file.open(mode="w", encoding="utf-8", newline="\n") as outfile:
        for line in same_list:
            outfile.write(line + "\n")

    getLogger().info("Number of the same address : %s", len(same_list))
    getLogger().info("RIR Same Checker ipv4 : end")


def main() -> None:
    # RIR URLs
    APNIC = "https://ftp.apnic.net/pub/stats/apnic/delegated-apnic-extended-latest"
    ARIN = "https://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest"
    RIPENCC = "https://ftp.ripe.net/pub/stats/ripencc/delegated-ripencc-extended-latest"
    LACNIC = "https://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-extended-latest"
    AFRINIC = "https://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-extended-latest"

    RIR_URLS = [APNIC, ARIN, RIPENCC, LACNIC, AFRINIC]
    EXCLUDED_COUNTRIES = ["ZZ"]
    PATH_IP_LISTS = Path(__file__).parent / "ip-lists"

    setup_logger()
    print("Extract duplicate listings from RIR data\n")

    if not PATH_IP_LISTS.exists():
        PATH_IP_LISTS.mkdir(parents=True)

    if not os.access(PATH_IP_LISTS, os.W_OK):
        print(f"You do not have write permission to the {PATH_IP_LISTS} directory.\n")
        return

    os.chdir(PATH_IP_LISTS)
    start_time = time.time()
    rir_same_checker_ipv4(rir_load_reformat_ipv4(RIR_URLS, EXCLUDED_COUNTRIES))
    print(f"processing time : {time.time() - start_time:,.2f} sec")


if __name__ == "__main__":
    main()
