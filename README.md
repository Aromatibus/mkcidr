## ◇はじめに

GITHUBで公開しています。
[Aromatibus/mkcidr]

:::note alert
テストは行っていますが、十分な運用期間があるとは言えないため注意してください。
:::

:::note warn
※注　前置きが長いので興味の無い方は読み飛ばし推薦です。
:::

今からおよそ1年前に自宅サーバーを立ち上げようとしました。
準備を進めていたところでNURO光に突然MAP-Eが導入されました。
調べた結果、無料では公開サーバーは不可能だと結論に至りました。
そして計画は断念そのまま放置していました。。。

とは言え、色々と楽しかったのですが（笑）

※準備中、[Server World][]様には大変お世話になりました。ありがとうございます！！

## ◇不正アクセスの多いこと多いこと

外部からのアクセスを解放して数時間後だったと思います。
なんとなくアクセスログを見たところsshへの不正アクセスが大量に検知されていました。
たった数時間なのにあまりの多さに驚愕しました。
さらに調べてみるとアクセスは国外のまとまった地域からであることがわかりました。
そこで不正アクセスを次の記事を参考に遮断することにしました。

- 不正アクセスを遮断
  - [Server World][]様の記事から[Fail2Ban : 侵入防止システム][]
  - [5分で理解するfail2ban][]
- 国外からのアクセスを遮断
  - [Nginxで国外からのWEBアクセスを遮断][]
  - [【Cent OS 6.x】国単位でIPをブロックするスクリプト with ipset][]

## ◇そして盛大な寄り道へ

さて、アクセス制限はできました。が、
[世界の国別 IPv4 アドレス割り当てリスト][]からダウンロードさせて頂くCIDRリストってなんぞ？からの

:::note question
これ自分で作れないかな？
:::
となりました（平常運転）

## ◇Pythonで実装

これを作っている時が一番楽しかったかもしれない！

<!-- markdownlint-disable MD033 -->
<details><summary>mkcidr.py</summary>
<!-- markdownlint-enable MD033 -->

```Python:mkcidr.py
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
    handler.setFormatter(
        Formatter(
            fmt="[%(asctime)s] %(threadName)s - %(message)s",
            datefmt="%Y/%m/%d-%H:%M:%S",
        ),
    )
    logger = getLogger()
    logger.setLevel(INFO)
    logger.addHandler(handler)


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
        getLogger().exception("  download error : %s", rir_registry + " (" + str(e) + ")")  # noqa: TRY401
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

    Path_IP_LISTS = Path(__file__).parent / "ip-lists"

    setup_logger()

    getLogger().info("RIR to CIDR IP lists start")
    getLogger().info("")

    if not os.access(Path_IP_LISTS.parents[0], os.W_OK):
        getLogger().info("Directory '%s' No write permissions.", Path_IP_LISTS.parents[0])

        sys.exit(1)
    if not Path_IP_LISTS.exists():
        Path_IP_LISTS.mkdir(mode=0o775, parents=False, exist_ok=True)
    os.chdir(Path_IP_LISTS)
    getLogger().info("Destination Directories '%s'", Path_IP_LISTS)
    getLogger().info("")

    start = time.time()
    HOUR = 60
    allow_time_min = 18 * HOUR
    if allow_downloads(allow_time_min, RIR_URLs):
        if not parallel_download(RIR_URLs):
            getLogger().info("The download was canceled because an error occurred.")
            sys.exit(1)
        getLogger().info("download time : %.2f sec", time.time() - start)
        start = time.time()
        rir2cidr(RIR_URLs, EXCLUDED_COUNTRIES)
        getLogger().info("processing time : %.2f sec", time.time() - start)
    else:
        getLogger().info(
            "The download was canceled because the specified time has not elapsed.",
        )
    getLogger().info("end")

    sys.exit(0)
```

<!-- markdownlint-disable MD033 -->
</details>
<!-- markdownlint-enable MD033 -->

## ◇C#で実装

最近は[Google Gemini][]などAIを使ってプログラムを組むのも当たり前？になりました。
言語変換もできるかな？と試したところ思いの外良い結果がでました。
そこで更に改良したものを掲載します。

※実はこの記事のきっかけです。

◯コマンドラインからコンパイルする場合は次のとおりにしてください

[Aromatibus/mkcidr][]に[バッチファイル][]もあります。

```BAT
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /r:System.Net.Http.dll mkcidr.cs
```

<!-- markdownlint-disable MD033 -->
<details><summary>mkcidr.cs</summary>
<!-- markdownlint-enable MD033 -->

```C#:mkcidr.cs
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;

namespace RirToCidrConverter
{
    class Program
    {
        // Python版をAIでC#に変換しエラー処理追加、修正、最適化

        // --- 設定定数 ---
        private static readonly int allowTimeMin = 18 * 60; // 再ダウンロード許可時間 (分)
        private static readonly int MaxRetryCount = 3;      // 再ダウンロード試行回数
        private static readonly int RetryWaitSeconds = 10;  // ダウンロード失敗時の待機時間（秒）
        private static readonly string[] ExcludedCountries = { "ZZ" };
        private static readonly string[] RirUrls = {
            "http://ftp.apnic.net/pub/stats/apnic/delegated-apnic-extended-latest",
            "http://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest",
            "http://ftp.ripe.net/pub/stats/ripencc/delegated-ripencc-extended-latest",
            "http://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-extended-latest",
            "http://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-extended-latest"
        };

        static void Main(string[] args)
        {
            // TLS 1.2 を有効化 (RIPE NCCなどのHTTPS/TLS接続エラー対策)
            ServicePointManager.SecurityProtocol = (SecurityProtocolType)3072
                                                    | SecurityProtocolType.Tls
                                                    | SecurityProtocolType.Ssl3;

            Console.WriteLine("RIR to CIDR Converter\n");

            try
            {
                RunAsync().Wait();
            }
            catch (Exception ex)
            {
                Exception baseEx = ex.GetBaseException();
                Log(string.Format("Critical Error: {0}", baseEx.Message));
            }

            Console.WriteLine("\nProcessing completed. Press any key to exit.");
            Console.ReadKey();
        }

        static async Task RunAsync()
        {
            string baseDir = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "ip-lists");
            try
            {
                if (!Directory.Exists(baseDir)) Directory.CreateDirectory(baseDir);
                Directory.SetCurrentDirectory(baseDir);
            }
            catch (Exception ex)
            {
                Log(string.Format("Directory access failed: {0}", ex.Message));
                return;
            }

            Log("RIR to CIDR IP lists start");

            if (NeedDownload(allowTimeMin))
            {
                bool downloadSuccess = await ParallelDownload();
                if (!downloadSuccess)
                {
                    Log("Error: Specified number of retries failed. Terminating process.");
                    return;
                }
                ConvertRirToCidr();
            }
            else
            {
                Log(string.Format("Skip download (within {0:F1} hours).", Math.Ceiling(allowTimeMin / 60.0 * 10) / 10));
            }

            Log("All processing completed.");
        }

        // --- ログ出力 ---
        private static void Log(string message)
        {
            string timestamp = DateTime.Now.ToString("yyyy/MM/dd-HH:mm:ss");
            Console.WriteLine(string.Format("[{0}] {1}", timestamp, message));
        }

        // --- ダウンロード判定 ---
        private static bool NeedDownload(int allowTimeMin)
        {
            foreach (var url in RirUrls)
            {
                try
                {
                    string fileName = Path.GetFileName(new Uri(url).LocalPath);
                    if (!File.Exists(fileName)) return true;
                    var diff = DateTime.UtcNow - File.GetLastWriteTimeUtc(fileName);
                    if (diff.TotalMinutes > allowTimeMin) return true;
                }
                catch
                {
                    return true;
                }
            }
            return false;
        }

        // --- 並列ダウンロード (User-Agent追加版) ---
        private static async Task<bool> ParallelDownload()
        {
            Log("Download task start");

            var handler = new HttpClientHandler()
            {
                AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate
            };

            using (var client = new HttpClient(handler))
            {
                client.Timeout = TimeSpan.FromSeconds(30);
                // RIPE NCC等のブロック対策としてUser-Agentを設定
                client.DefaultRequestHeaders.Add("User-Agent", "Mozilla/5.0 (compatible; RirCidrConverter/1.0)");
                client.DefaultRequestHeaders.Add("Accept", "*/*");

                var tasks = RirUrls.Select(async url =>
                {
                    string fileName = Path.GetFileName(new Uri(url).LocalPath);
                    string registry = fileName.Contains("-") ? fileName.Split('-')[1] : "unknown";

                    bool success = false;
                    for (int i = 0; i <= MaxRetryCount; i++)
                    {
                        try
                        {
                            if (i > 0) Log(string.Format("Retry ({0}/{1}) : {2}", i, MaxRetryCount, registry));
                            else Log(string.Format("download start : {0}", registry));

                            var response = await client.GetAsync(url, HttpCompletionOption.ResponseHeadersRead);
                            if (response.IsSuccessStatusCode)
                            {
                                using (var fs = new FileStream(fileName, FileMode.Create, FileAccess.Write, FileShare.None))
                                {
                                    await response.Content.CopyToAsync(fs);
                                }
                                Log(string.Format("download end   : {0}", registry));
                                success = true;
                                break;
                            }
                            else
                            {
                                Log(string.Format("download error : {0} (Status: {1} {2})",
                                    registry, (int)response.StatusCode, response.ReasonPhrase));
                            }
                        }
                        catch (Exception ex)
                        {
                            Log(string.Format("download error : {0} ({1})", registry, ex.Message));
                        }

                        if (!success && i < MaxRetryCount)
                        {
                            Log(string.Format("Waiting {0} seconds before next attempt...", RetryWaitSeconds));
                            await Task.Delay(RetryWaitSeconds * 1000);
                        }
                    }
                    return success;
                });

                var results = await Task.WhenAll(tasks);
                return results.All(r => r);
            }
        }

        // --- RIRデータをCIDRに変換 ---
        private static void ConvertRirToCidr()
        {
            Log("RIR to CIDR conversion start");
            var ipv4Data = new List<string>();
            var ipv6Data = new List<string>();

            foreach (var url in RirUrls)
            {
                string fileName = Path.GetFileName(new Uri(url).LocalPath);
                if (!File.Exists(fileName)) continue;

                string registry = fileName.Contains("-") ? fileName.Split('-')[1] : "";

                foreach (var line in File.ReadAllLines(fileName))
                {
                    if (line.StartsWith("#") || string.IsNullOrWhiteSpace(line)) continue;
                    var p = line.Split('|');
                    if (p.Length < 5) continue;
                    if (p[1] == "" || p[1] == registry || ExcludedCountries.Contains(p[1]) || p[3] == "*") continue;

                    string formatted = string.Join("|", p[1], p[2], p[3], p[4]);
                    if (p[2] == "ipv4") ipv4Data.Add(formatted);
                    else if (p[2] == "ipv6") ipv6Data.Add(formatted);
                }
            }

            Parallel.Invoke(
                () => ProcessIpv4(ipv4Data.OrderBy(s => s).ToList()),
                () => ProcessIpv6(ipv6Data.OrderBy(s => s).ToList())
            );
        }

        private static void ProcessIpv4(List<string> sortedData)
        {
            string dir = "ipv4";
            if (!Directory.Exists(dir)) Directory.CreateDirectory(dir);
            var groups = sortedData.Select(s => s.Split('|')).GroupBy(p => p[0]);

            foreach (var g in groups)
            {
                var cidrs = new List<string>();
                foreach (var p in g)
                {
                    uint? startIp = ToUint(p[2]);
                    uint count;
                    if (startIp.HasValue && uint.TryParse(p[3], out count))
                    {
                        cidrs.AddRange(RangeToCidr(startIp.Value, count));
                    }
                }
                if (cidrs.Count > 0)
                    File.WriteAllLines(Path.Combine(dir, g.Key), cidrs.Distinct());
            }
            ConcatenateFiles(dir, "_CIDR.ipv4");
        }

        private static void ProcessIpv6(List<string> sortedData)
        {
            string dir = "ipv6";
            if (!Directory.Exists(dir)) Directory.CreateDirectory(dir);
            var groups = sortedData.Select(s => s.Split('|')).GroupBy(p => p[0]);

            foreach (var g in groups)
            {
                var cidrs = new List<string>();
                foreach (var p in g)
                {
                    if (IsValidIpv6(p[2]))
                    {
                        cidrs.Add(string.Format("{0}/{1}", p[2], p[3]));
                    }
                }
                if (cidrs.Count > 0)
                    File.WriteAllLines(Path.Combine(dir, g.Key), cidrs.OrderBy(s => s));
            }
            ConcatenateFiles(dir, "_CIDR.ipv6");
        }

        private static void ConcatenateFiles(string dir, string outputName)
        {
            try
            {
                var files = Directory.GetFiles(dir, "??").OrderBy(f => f);
                using (var sw = new StreamWriter(Path.Combine(dir, outputName)))
                {
                    foreach (var f in files)
                    {
                        string country = Path.GetFileName(f);
                        foreach (var line in File.ReadAllLines(f))
                        {
                            if (!string.IsNullOrWhiteSpace(line))
                                sw.WriteLine(string.Format("{0}\t{1}", country, line.Trim()));
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Log(string.Format("File concatenation error: {0}", ex.Message));
            }
        }

        private static List<string> RangeToCidr(uint start, uint count)
        {
            var result = new List<string>();
            if (count == 0) return result;
            uint end = start + count - 1;
            while (start <= end)
            {
                byte maxMask = 32;
                while (maxMask > 0)
                {
                    uint mask = (uint)0xffffffff << (32 - (maxMask - 1));
                    if ((start & mask) != start || (start | ~mask) > end) break;
                    maxMask--;
                }
                result.Add(string.Format("{0}/{1}", ToIpString(start), maxMask));
                uint blockSize = (uint)1 << (32 - maxMask);
                if (uint.MaxValue - blockSize < start) break;
                start += blockSize;
            }
            return result;
        }

        private static uint? ToUint(string ipAddress)
        {
            if (string.IsNullOrWhiteSpace(ipAddress)) return null;
            IPAddress address;
            if (IPAddress.TryParse(ipAddress.Trim(), out address))
            {
                if (address.AddressFamily != System.Net.Sockets.AddressFamily.InterNetwork)
                    return null;
                byte[] bytes = address.GetAddressBytes();
                if (BitConverter.IsLittleEndian) Array.Reverse(bytes);
                return BitConverter.ToUInt32(bytes, 0);
            }
            return null;
        }

        private static string ToIpString(uint ip)
        {
            byte[] bytes = BitConverter.GetBytes(ip);
            if (BitConverter.IsLittleEndian) Array.Reverse(bytes);
            return new IPAddress(bytes).ToString();
        }

        private static bool IsValidIpv6(string ipAddress)
        {
            if (string.IsNullOrWhiteSpace(ipAddress)) return false;
            IPAddress address;
            return IPAddress.TryParse(ipAddress.Trim(), out address) &&
                address.AddressFamily == System.Net.Sockets.AddressFamily.InterNetworkV6;
        }
    }
}
```

<!-- markdownlint-disable MD033 -->
</details>
<!-- markdownlint-enable MD033 -->

## ◇おわりに

NURO光を使ってるんですがWebページの作成など色々と試す前に突然、MAP-Eへ変更により外部からのアクセスができなくなりました。
トンネルを使う方法やルーターの対応如何では公開も可能なようですが、NURO光では絶望的という意見が多いようです。
そもそもNURO光は確保しているIP4アドレスが少ないらしく今後、公開サーバーの運用はほぼ絶望的みたいですね。
乗り換えを考えていますが今後はMAP-Eが当たり前になってしまうんだろうか・・・

<https://github.com/Aromatibus/>

[Aromatibus/mkcidr]: https://github.com/Aromatibus/mkcidr
[バッチファイル]: https://github.com/Aromatibus/mkcidr/blob/main/src/cs_ver/CSC_Http_CLI64_DragDropHere.bat
[Server World]: https://www.server-world.info/
[Fail2Ban : 侵入防止システム]: https://www.server-world.info/query?os=CentOS_Stream_9&p=fail2ban
[5分で理解するfail2ban]: https://qiita.com/Brutus/items/28f4dc2054ad7de54e73
[Nginxで国外からのWEBアクセスを遮断]: https://qiita.com/KensukeSakakibara/items/27d15975c754758321ad
[【Cent OS 6.x】国単位でIPをブロックするスクリプト with ipset]: https://qiita.com/R123/items/dc82461ad127c5ea0703
[世界の国別 IPv4 アドレス割り当てリスト]: http://nami.jp/ipv4bycc/
[Google Gemini]: https://gemini.google.com/
