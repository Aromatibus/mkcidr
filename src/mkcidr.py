#!/usr/bin/env python3.10

"""Convert RIR IP address lists to CIDR format."""

# The library "concurrent.futures" is available in Python version 3.2 or later
# and has been tested with Python 3.10.
# https://docs.python.org/ja/3/library/concurrent.futures.html

import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from logging import INFO, FileHandler, Formatter, StreamHandler, getLogger
from pathlib import Path
from urllib.parse import urlparse

import requests
from netaddr import IPAddress, IPRange, IPSet
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


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


def allow_downloads(allow_time_min: int, RIR_URLs: list[str]) -> bool:
    # Determine whether to continue based on the time(min)
    # the file was downloaded
    current_time = datetime.now(tz=timezone.utc).timestamp()
    for rir_url in RIR_URLs:
        rir_filename = Path(urlparse(rir_url).path).name
        if not Path(rir_filename).exists():
            return True
        download_time = Path(rir_filename).stat().st_mtime
        difference_time = (current_time - download_time) / 60
        if difference_time > allow_time_min:
            return True
    return False


def download(rir_url: str) -> bool:
    rir_filename = Path(urlparse(rir_url).path).name
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
        response = requests.get(rir_url, timeout=(15.0, 15.0))
        session.close()
        response.raise_for_status()
    except Exception as e:
        getLogger().error("  download error : %s", rir_registry + " (" + str(e) + ")")
        return False
    else:
        http_success = 200
        if response.status_code == http_success:
            with Path(rir_filename).open(mode="wb") as file:
                file.write(response.content)
        else:
            getLogger().error("  download error : %s", rir_registry)
            return False
    getLogger().info("download end   : %s", rir_registry)
    return True


def parallel_download(RIR_URLs: list[str]) -> bool:
    getLogger().info("download task start")
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(download, rir_url) for rir_url in RIR_URLs]
        for future in as_completed(futures):
            if not future.result():
                executor.shutdown(wait=False, cancel_futures=False)  # never stops
                return False
    for rir_url in RIR_URLs:
        rir_filename = Path(urlparse(rir_url).path).name
        if not Path(rir_filename).exists():
            getLogger().error("  download error : %s", rir_filename + " (file not found)")
            return False
    getLogger().info("download task end")
    return True


def rir2cidr(RIR_URLs: list[str], EXCLUDED_COUNTRIES: list[str]) -> None:
    """RIR Format.

        http://www.apnic.net/db/rir-stats-format.html
        Format     : registry|cc|type|start|value|date|status|extensions...]
        registry   : {afrinic, apnic, arin, iana, lacnic, ripencc}
        cc         : ISO 3166 2-letter code
        type       : {asn,ipv4,ipv6}
        start      : first address of the range
        value      : CIDR range
        status     : Type of allocation from the set
        extensions : Any extra data on a line is undefined
    ISO 3166 2-letter code
        https://www.iso.org/obp/ui/
        https://www.asahi-net.or.jp/~ax2s-kmtn/ref/iso3166-1.html
    """
    getLogger().info("RIR to CIDR start")
    rir_ipv4_list: list[str] = []
    rir_ipv6_list: list[str] = []
    rir_ipv4_list, rir_ipv6_list = extracts_ipv46_lists(RIR_URLs, EXCLUDED_COUNTRIES)
    getLogger().info("converted to CIDR start")
    cores = os.cpu_count()
    cores = cores if cores is not None else 1
    max_threads = 2
    PoolExecutor = ProcessPoolExecutor() if cores > max_threads else ThreadPoolExecutor()
    with PoolExecutor as executor:
        executor.submit(rir2cidr_ipv4, rir_ipv4_list)
        executor.submit(rir2cidr_ipv6, rir_ipv6_list)
    getLogger().info("converted to CIDR end")
    getLogger().info("RIR to CIDR end")


def extracts_ipv46_lists(
    RIR_URLs: list[str],
    EXCLUDED_COUNTRIES: list[str],
) -> tuple[list[str], list[str]]:
    getLogger().info("ipv4/ipv6 separate start")
    rir_ipv4_list: list[str] = []
    rir_ipv6_list: list[str] = []
    rir_ipv4_list_append = rir_ipv4_list.append
    rir_ipv6_list_append = rir_ipv6_list.append
    for rir_url in RIR_URLs:
        rir_filename = Path(urlparse(rir_url).path).name
        rir_registry = rir_filename.split("-")[1]
        rir_path = Path(Path.cwd()) / rir_filename
        with rir_path.open(mode="r") as file:
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
                required_param = "|".join(params[1:5]) + "\n"
                if params[2] == "ipv4":
                    rir_ipv4_list_append(required_param)
                if params[2] == "ipv6":
                    rir_ipv6_list_append(required_param)
    rir_ipv4_list.sort()
    rir_ipv6_list.sort()
    getLogger().info("ipv4/ipv6 separate end")
    return rir_ipv4_list, rir_ipv6_list


def rir2cidr_ipv4(rir_ipv4_list: list[str]) -> None:
    getLogger().info("ipv4 converted to CIDR start")
    getLogger().info("  ipv4 RIR to CIDR start")
    path_ipv4 = Path.cwd() / "ipv4"
    if not path_ipv4.exists():
        path_ipv4.mkdir()
    rir_cc = ""
    cidr_ipv4_list: list[str] = []
    cidr_ipv4_list_extend = cidr_ipv4_list.extend

    def write_cidr(path_ipv4: Path, rir_cc: str) -> None:
        ipv4_cidr_path = Path(path_ipv4) / rir_cc
        cidr_ipv4_list.sort()
        ipv4set = IPSet(cidr_ipv4_list)
        with ipv4_cidr_path.open(mode="w", encoding="utf-8", newline="\n") as file:
            for cidr in ipv4set.iter_cidrs():
                file.write(str(cidr) + "\n")

    for line in rir_ipv4_list:
        params = line.split("|")
        if rir_cc != params[0] and line != rir_ipv4_list[0]:
            write_cidr(path_ipv4, rir_cc)
            cidr_ipv4_list.clear()
        rir_cc = params[0]
        width = int(params[3])
        from_ip = IPAddress(params[2], version=4)
        to_ip = IPAddress(int(from_ip) + width - 1)
        cidr_ipv4_list_extend(str(cidr) for cidr in IPRange(params[2], to_ip).cidrs())
        if line == rir_ipv4_list[-1]:
            write_cidr(path_ipv4, rir_cc)
    getLogger().info("  ipv4 RIR to CIDR end")
    getLogger().info("  combine ipv4 country files start")
    concatenate_ipv4_country_files()
    getLogger().info("  combine ipv4 country files end")
    getLogger().info("ipv4 converted to CIDR end")


def concatenate_ipv4_country_files() -> None:
    path_ipv4 = Path.cwd() / "ipv4"
    file_list = list(Path(path_ipv4).glob("[A-Z][A-Z]"))
    file_list.sort()
    with Path(path_ipv4 / "_CIDR.ipv4").open(mode="w", encoding="utf-8", newline="\n") as outfile:
        for filename in file_list:
            country = Path(filename).stem
            with Path(filename).open(mode="r") as infile:
                for line in infile:
                    if line.strip() != "":
                        outfile.write(country + "\t" + line)


def rir2cidr_ipv6(rir_ipv6_list: list[str]) -> None:
    getLogger().info("ipv6 converted to CIDR start")
    getLogger().info("  ipv6 RIR to CIDR start")
    path_ipv6 = Path.cwd().resolve() / "ipv6"
    if not path_ipv6.exists():
        path_ipv6.mkdir()
    rir_cc = ""
    cidr_ipv6_list: list[str] = []
    cidr_ipv6_list_append = cidr_ipv6_list.append

    def write_cidr(path_ipv6: Path, rir_cc: str) -> None:
        ipv6_cidr_path = path_ipv6.resolve() / rir_cc
        cidr_ipv6_list.sort()
        ipv6set = IPSet(cidr_ipv6_list)
        with ipv6_cidr_path.open("w") as file:
            for cidr in ipv6set.iter_cidrs():
                file.write(str(cidr) + "\n")

    for line in rir_ipv6_list:
        params = line.split("|")
        if rir_cc != params[0] and line != rir_ipv6_list[0]:
            write_cidr(path_ipv6, rir_cc)
            cidr_ipv6_list.clear()
        rir_cc = params[0]
        cidr_ipv6_list_append(params[2] + "/" + params[3])
        if line == rir_ipv6_list[-1]:
            write_cidr(path_ipv6, rir_cc)
    getLogger().info("  ipv6 RIR to CIDR end")
    getLogger().info("  combine ipv6 country files start")
    concatenate_ipv6_country_files()
    getLogger().info("  combine ipv6 country files end")
    getLogger().info("ipv6 converted to CIDR end")


def concatenate_ipv6_country_files() -> None:
    path_ipv6 = Path.cwd().resolve() / "ipv6"
    file_list = list(Path(path_ipv6).glob("[A-Z][A-Z]"))
    file_list.sort()
    with Path(path_ipv6 / "_CIDR.ipv6").open("w", encoding="utf-8", newline="\n") as outfile:
        for filename in file_list:
            country = Path(filename).name.split(".")[0]
            with Path(filename).open("r") as infile:
                for line in infile:
                    if line.strip() != "":
                        outfile.write(country + "\t" + line)


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

    Path_IP_LISTS = Path("/var/ip-lists/").resolve()

    setup_logger()

    getLogger().info("RIR to CIDR IP lists start")
    getLogger().info("")

    if not os.access(Path_IP_LISTS.parents[0], os.W_OK):
        getLogger().info(f"You do not have write permission to the '{Path_IP_LISTS.parents[0]}' directory.")
        sys.exit(1)
    if not Path_IP_LISTS.exists():
        Path_IP_LISTS.mkdir(mode=0o664, parents=False, exist_ok=True)
    os.chdir(Path_IP_LISTS)
    getLogger().info(f"Destination Directories '{Path_IP_LISTS}'")
    getLogger().info("")

    start = time.time()
    HOUR = 60
    allow_time_min = 18 * HOUR
    if allow_downloads(allow_time_min, RIR_URLs):
        if not parallel_download(RIR_URLs):
            getLogger().info("The download was canceled because an error occurred.")
            sys.exit(1)
        getLogger().info(f"download time : {time.time() - start:,.2f} sec")
        start = time.time()
        rir2cidr(RIR_URLs, EXCLUDED_COUNTRIES)
        getLogger().info(f"processing time : {time.time() - start:,.2f} sec")
    else:
        getLogger().info(
            "The download was canceled because the specified time has not elapsed.",
        )
    getLogger().info("")

    sys.exit(0)
