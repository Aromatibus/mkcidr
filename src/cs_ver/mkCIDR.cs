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

        // 2026-01-19 未完

        //  --- 設定定数 ---
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
