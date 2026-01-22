#!/usr/bin/env python3.10

"""Convert RIR IP address lists to CIDR format."""

# The library "concurrent.futures" is available in Python version 3.2 or later
# and has been tested with Python 3.10.
# https://docs.python.org/ja/3/library/concurrent.futures.html

import datetime
import ipaddress
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Regional Internet Registry (RIR) URLs
RIR_URLS: list[str] = [
    "https://ftp.apnic.net/pub/stats/apnic/delegated-apnic-extended-latest",
    "https://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest",
    "https://ftp.ripe.net/pub/stats/ripencc/delegated-ripencc-extended-latest",
    "https://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-extended-latest",
    "https://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-extended-latest",
]
# Excluded countries for IP address lists
EXCLUDED_COUNTRIES: set[str] = {"ZZ"}
# Allowed time in minutes before re-downloading files
ALLOW_TIME_MIN: int = 18 * 60
# Working directory for IP lists
WORKING_DIR: Path = Path("ip-lists")


def log(message: str) -> None:
    timestamp: str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y/%m/%d-%H:%M:%S")
    print(f"[{timestamp}] {message}")


def safe_urlretrieve(url: str, save_path: Path, timeout: int = 60) -> bool:
    try:
        if not url.startswith(("http://", "https://")):
            log("Security Error: Forbidden URL scheme")
            return False

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})  # noqa:S310

        opener = urllib.request.build_opener()
        with opener.open(req, timeout=timeout) as response, open(save_path, "wb") as f:
            f.write(response.read())
    except urllib.error.HTTPError as e:
        log(f"HTTP Error: {e.code} - {url}")
    except urllib.error.URLError as e:
        log(f"URL Error (Connection failed): {e.reason}")
    except TimeoutError:
        log(f"Timeout Error: {url}")
    except Exception as e:
        log(f"Unexpected Error: {e}")
    else:
        return True
    return False


def check_need_download() -> bool:
    for url in RIR_URLS:
        file_path: Path = WORKING_DIR / url.split("/")[-1]
        if not file_path.exists():
            return True

        mtime: datetime.datetime = datetime.datetime.fromtimestamp(
            file_path.stat().st_mtime, datetime.timezone.utc,
        )
        now: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
        if (now - mtime).total_seconds() / 60 > ALLOW_TIME_MIN:
            return True
    return False


def download_task(url: str) -> bool:
    file_name: str = url.split("/")[-1]
    reg: str = file_name.split("-")[1]
    save_path: Path = WORKING_DIR / file_name

    log(f"download start : {reg}")
    success: bool = safe_urlretrieve(url, save_path)
    if success:
        log(f"download end   : {reg}")
    return success


def parallel_download_files() -> bool:
    log("download task start (Parallel)")
    with ThreadPoolExecutor() as executor:
        results: list[bool] = list(executor.map(download_task, RIR_URLS))
    return all(results)


def _process_rir_line(line: str, reg: str, ipv4_data: dict, ipv6_data: dict) -> None:
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
    MIN_RIR_FIELDS: int = 5
    line = line.strip()
    if not line or line.startswith("#"):
        return

    p: list[str] = line.split("|")

    if (
        len(p) < MIN_RIR_FIELDS
        or not p[1] or p[1] == reg or p[1] in EXCLUDED_COUNTRIES or p[3] == "*"
    ):
        return

    cc: str = p[1]
    ip_type: str = p[2]
    start_ip: str = p[3]

    try:
        if ip_type == "ipv4":
            count: int = int(p[4])
            if cc not in ipv4_data:
                ipv4_data[cc] = []

            end_ip_int: int = int(ipaddress.IPv4Address(start_ip)) + count - 1
            networks = ipaddress.summarize_address_range(
                ipaddress.IPv4Address(start_ip),
                ipaddress.IPv4Address(end_ip_int),
            )
            ipv4_data[cc].extend(networks)

        elif ip_type == "ipv6":
            if cc not in ipv6_data:
                ipv6_data[cc] = []
            ipv6_data[cc].append(f"{start_ip}/{p[4]}")
    except Exception as e:
        log(f"Skipped invalid line: {line} ({e})")


def process_rir_data() -> None:
    log("RIR to CIDR start")
    ipv4_data: dict[str, list[ipaddress.IPv4Network]] = {}
    ipv6_data: dict[str, list[str]] = {}

    for url in RIR_URLS:
        file_name: str = url.split("/")[-1]
        file_path: Path = WORKING_DIR / file_name
        if not file_path.exists():
            continue

        reg: str = file_name.split("-")[1]

        with open(file_path, encoding="utf-8") as f:
            for line in f:
                _process_rir_line(line, reg, ipv4_data, ipv6_data)

    write_results("ipv4", ipv4_data)
    write_results("ipv6", ipv6_data)


def write_results(ip_type: str, data: dict) -> None:
    log(f"{ip_type} write start")
    folder: Path = WORKING_DIR / ip_type
    folder.mkdir(parents=True, exist_ok=True)
    master_path: Path = folder / f"_CIDR.{ip_type}"

    with open(master_path, "w", encoding="utf-8", newline="\n") as f_master:
        for cc in sorted(data.keys()):
            if ip_type == "ipv4":
                cidrs: list[str] = [str(n) for n in ipaddress.collapse_addresses(data[cc])]
            else:
                cidrs: list[str] = sorted(data[cc])

            cc_file_path: Path = folder / cc
            with open(cc_file_path, "w", encoding="utf-8", newline="\n") as f_cc:
                for c in cidrs:
                    f_cc.write(f"{c}\n")
                    f_master.write(f"{cc}\t{c}\n")


def main() -> None:
    log("RIR to CIDR IP lists start")
    try:
        WORKING_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        log(f"Fatal Error: {e}")
        return

    if check_need_download():
        if not parallel_download_files():
            log("Download failed. Aborting.")
            return
    else:
        log("Skip download: Files are up to date.")

    process_rir_data()
    log("end")


if __name__ == "__main__":
    main()
