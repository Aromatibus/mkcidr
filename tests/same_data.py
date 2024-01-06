import os
import sys
from time import time
from urllib.parse import urlparse

import pandas as pd


def extracts_ipv46_lists(
    RIR_URLs: list, EXCLUDED_COUNTRIES: list
) -> tuple[list[str], list[str]]:
    rir_ipv4_list = list()
    rir_ipv6_list = list()
    rir_ipv4_list_append = rir_ipv4_list.append
    rir_ipv6_list_append = rir_ipv6_list.append
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
                required_param = "|".join(params[1:5]) + "\n"
                if params[2] == "ipv4":
                    rir_ipv4_list_append(required_param)
                if params[2] == "ipv6":
                    rir_ipv6_list_append(required_param)
    rir_ipv4_list.sort()
    rir_ipv6_list.sort()
    return rir_ipv4_list, rir_ipv6_list





if __name__ == "__main__":
    """
    RIR Format
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

    # RIR_URLs = [APNIC, ARIN, RIPENCC, LACNIC, AfriNIC]
    RIR_URLs = [AfriNIC]
    EXCLUDED_COUNTRIES = ["ZZ"]

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    rir_ipv4_list = list()
    rir_ipv4_list, _ = extracts_ipv46_lists(RIR_URLs, EXCLUDED_COUNTRIES)

    start = time()


    df = pd.DataFrame(rir_ipv4_list, columns=["registry", "cc", "type", "start", "value", "date", "status", "extensions"])

    # 重複した行を抽出する
    duplicate_rows = df[df.duplicated()]

    print(duplicate_rows)



    print("processing time : {:,.2f} sec".format(time() - start))
    print("")
    sys.exit(1)
