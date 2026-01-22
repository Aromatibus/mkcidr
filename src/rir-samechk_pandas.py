#!/usr/bin/env python3.10

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
    params = line.strip().split("|")
    # params[0:5] -> registry, cc, type, start, value
    # Reorder to: start, value, registry, cc, type
    new_params = [params[3], params[4], params[0], params[1], params[2]]
    new_params.extend(params[5:8])
    return "|".join(new_params)


def restore_rir_format(line: str) -> str:
    params = line.split("|")
    # Restore from: start, value, registry, cc, type
    # Back to: registry, cc, type, start, value
    restored = [params[2], params[3], params[4], params[0], params[1]]
    restored.extend(params[5:8])
    return "|".join(restored)


def rir_load_reformat_ipv4(rir_urls: list[str], excluded_countries: list[str]) -> list[str]:
    logger = getLogger()
    logger.info("RIR Same Checker ipv4 : start")
    check_list: list[str] = []
    excluded_set = set(excluded_countries)

    logger.info("RIR Same Checker ipv4 : Load RIR")
    for rir_url in rir_urls:
        rir_filename = Path(urlparse(rir_url).path).name
        rir_registry = rir_filename.split("-")[1]
        rir_path = Path.cwd() / rir_filename

        if not rir_path.exists():
            logger.warning("File not found: %s", rir_path)
            continue

        with rir_path.open(encoding="utf-8") as file:
            for line in file:
                if line.startswith("#") or not line.strip():
                    continue
                params = line.split("|")
                if len(params) < 7:
                    continue
                if params[1] in ("", rir_registry) or params[1] in excluded_set:
                    continue
                if params[3] == "*":
                    continue
                if params[2] == "ipv4":
                    check_list.append(change_rir_format(line))

    check_list.sort()
    return check_list


def rir_same_checker_ipv4(check_list: list[str]) -> None:
    logger = getLogger()
    logger.info("RIR Same Checker ipv4 : Same Check Start")
    path_ipv4 = Path.cwd() / "ipv4"
    path_ipv4.mkdir(parents=True, exist_ok=True)

    same_list: list[str] = []
    n = len(check_list)
    if n < 2:
        logger.info("No data to check.")
        return

    # Optimized duplicate check: compare with neighbors in O(n)
    for i in tqdm.tqdm(range(n)):
        current_ip = check_list[i].split("|")[0]
        is_same = False

        if i > 0 and current_ip == check_list[i - 1].split("|")[0]:
            is_same = True
        elif i < n - 1 and current_ip == check_list[i + 1].split("|")[0]:
            is_same = True

        if is_same:
            same_list.append(restore_rir_format(check_list[i]))

    logger.info("RIR Same Checker ipv4 : Write File")
    output_file = path_ipv4 / "_Same_RIR.ipv4"
    with output_file.open(mode="w", encoding="utf-8", newline="\n") as outfile:
        for line in same_list:
            outfile.write(f"{line}\n")

    logger.info("Number of the same address units : %d", len(same_list) // 2)
    logger.info("RIR Same Checker ipv4 : end")


def main() -> None:
    # RIR URLs
    RIR_URLS = [
        "https://ftp.apnic.net/pub/stats/apnic/delegated-apnic-extended-latest",
        "https://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest",
        "https://ftp.ripe.net/pub/stats/ripencc/delegated-ripencc-extended-latest",
        "https://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-extended-latest",
        "https://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-extended-latest",
    ]
    EXCLUDED_COUNTRIES = ["ZZ"]
    PATH_IP_LISTS = Path(__file__).parent / "ip-lists"

    setup_logger()
    print("Extract duplicate listings from RIR data\n")

    try:
        PATH_IP_LISTS.mkdir(parents=True, exist_ok=True)
        os.chdir(PATH_IP_LISTS)
    except OSError as e:
        print(f"Directory error: {e}")
        return

    start_time = time.time()
    data = rir_load_reformat_ipv4(RIR_URLS, EXCLUDED_COUNTRIES)
    if data:
        rir_same_checker_ipv4(data)

    print(f"processing time : {time.time() - start_time:,.2f} sec")


if __name__ == "__main__":
    main()
