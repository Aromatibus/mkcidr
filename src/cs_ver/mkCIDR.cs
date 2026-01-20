using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;

namespace RirToCidrConverter
{
    class Program
    {
        // --- 定数の宣言 ---
        private const string APNIC = "http://ftp.apnic.net/pub/stats/apnic/delegated-apnic-extended-latest";
        private const string ARIN = "http://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest";
        private const string RIPENCC = "http://ftp.ripe.net/pub/stats/ripencc/delegated-ripencc-extended-latest";
        private const string LACNIC = "http://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-extended-latest";
        private const string AFRINIC = "http://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-extended-latest";
        private static readonly string[] RIR_URLS = { APNIC, ARIN, RIPENCC, LACNIC, AFRINIC };
        private static readonly string[] EXCLUDED_COUNTRIES = { "ZZ" };
        private const int ALLOW_TIME_MIN = 18 * 60;
        private const string WORKING_DIR = "ip-lists";

        static void Main(string[] args)
        {
            ServicePointManager.SecurityProtocol = (SecurityProtocolType)3072; // TLS 1.2
            Log("RIR to CIDR IP lists start");

            string basePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, WORKING_DIR);
            try
            {
                if (!Directory.Exists(basePath)) Directory.CreateDirectory(basePath);
                Directory.SetCurrentDirectory(basePath);
            }
            catch (Exception ex)
            {
                Log(string.Format("Error: {0}", ex.Message));
                return;
            }

            if (CheckNeedDownload())
            {
                DateTime downloadStartTime = DateTime.Now;
                if (!ParallelDownloadFiles()) return;
                Log(string.Format("download time : {0:F2} sec", (DateTime.Now - downloadStartTime).TotalSeconds));
            }

            DateTime processStartTime = DateTime.Now;
            ProcessRirData();
            Log(string.Format("processing time : {0:F2} sec", (DateTime.Now - processStartTime).TotalSeconds));
            Log("end");
        }

        static bool CheckNeedDownload()
        {
            foreach (string url in RIR_URLS)
            {
                string fileName = Path.GetFileName(new Uri(url).LocalPath);
                if (!File.Exists(fileName)) return true;
                if ((DateTime.UtcNow - File.GetLastWriteTimeUtc(fileName)).TotalMinutes > ALLOW_TIME_MIN) return true;
            }
            return false;
        }

        static bool ParallelDownloadFiles()
        {
            Log("download task start (Parallel)");
            bool allSuccess = true;
            Parallel.ForEach(RIR_URLS, (url, state) =>
            {
                string fileName = Path.GetFileName(new Uri(url).LocalPath);
                string reg = fileName.Split('-')[1];
                try {
                    Log(string.Format("download start : {0}", reg));
                    using (WebClient c = new WebClient()) { c.DownloadFile(url, fileName); }
                    Log(string.Format("download end   : {0}", reg));
                }
                catch (Exception ex) {
                    Log(string.Format("download error : {0} ({1})", reg, ex.Message));
                    allSuccess = false;
                    state.Stop();
                }
            });
            return allSuccess;
        }

        static void ProcessRirData()
        {
            Log("RIR to CIDR start (Strong Merge Mode)");
            var ipv4Data = new Dictionary<string, List<IpRange>>();
            var ipv6Data = new Dictionary<string, List<string>>();

            foreach (string url in RIR_URLS)
            {
                string fileName = Path.GetFileName(new Uri(url).LocalPath);
                if (!File.Exists(fileName)) continue;
                string reg = fileName.Split('-')[1];

                foreach (string line in File.ReadAllLines(fileName))
                {
                    if (string.IsNullOrEmpty(line) || line.StartsWith("#")) continue;
                    string[] p = line.Split('|');
                    if (p.Length < 5 || string.IsNullOrEmpty(p[1]) || p[1] == reg || EXCLUDED_COUNTRIES.Contains(p[1]) || p[3] == "*") continue;

                    if (p[2] == "ipv4")
                    {
                        if (!ipv4Data.ContainsKey(p[1])) ipv4Data[p[1]] = new List<IpRange>();
                        ipv4Data[p[1]].Add(new IpRange(p[3], uint.Parse(p[4])));
                    }
                    else if (p[2] == "ipv6")
                    {
                        if (!ipv6Data.ContainsKey(p[1])) ipv6Data[p[1]] = new List<string>();
                        ipv6Data[p[1]].Add(string.Format("{0}/{1}", p[3], p[4]));
                    }
                }
            }

            WriteFiles("ipv4", ipv4Data, true);
            WriteFiles("ipv6", ipv6Data, false);
        }

        static void WriteFiles(string type, object data, bool isIpv4)
        {
            Log(string.Format("{0} converted to CIDR start", type));
            if (!Directory.Exists(type)) Directory.CreateDirectory(type);
            string masterPath = Path.Combine(type, string.Format("_CIDR.{0}", type));

            using (StreamWriter master = new StreamWriter(masterPath, false, new UTF8Encoding(false)))
            {
                if (isIpv4) {
                    var dict = (Dictionary<string, List<IpRange>>)data;
                    foreach (var cc in dict.Keys.OrderBy(k => k)) {
                        var cidrs = StrongMergeIpv4(dict[cc]);
                        using (StreamWriter sw = new StreamWriter(Path.Combine(type, cc), false, new UTF8Encoding(false))) {
                            foreach (var c in cidrs) { sw.WriteLine(c); master.WriteLine(string.Format("{0}\t{1}", cc, c)); }
                        }
                    }
                } else {
                    var dict = (Dictionary<string, List<string>>)data;
                    foreach (var cc in dict.Keys.OrderBy(k => k)) {
                        var cidrs = dict[cc].OrderBy(s => s).ToList();
                        using (StreamWriter sw = new StreamWriter(Path.Combine(type, cc), false, new UTF8Encoding(false))) {
                            foreach (var c in cidrs) { sw.WriteLine(c); master.WriteLine(string.Format("{0}\t{1}", cc, c)); }
                        }
                    }
                }
            }
            Log(string.Format("{0} converted to CIDR end", type));
        }

        static List<string> StrongMergeIpv4(List<IpRange> ranges)
        {
            if (ranges.Count == 0) return new List<string>();

            // 1. 個々の範囲を最小単位のCIDRに分解
            var allCidrs = new List<CidrBlock>();
            foreach (var range in ranges)
            {
                allCidrs.AddRange(GetCidrBlocksFromRange(range.Start, range.End));
            }

            // 2. 再帰的に集約 (隣り合う同サイズのブロックを1つ上のサイズにまとめる)
            bool changed;
            do {
                changed = false;
                var sorted = allCidrs.OrderBy(c => c.Network).ThenBy(c => c.Mask).ToList();
                var nextLevel = new List<CidrBlock>();

                for (int i = 0; i < sorted.Count; i++)
                {
                    if (i < sorted.Count - 1 && sorted[i].Mask == sorted[i + 1].Mask)
                    {
                        uint size = (uint)1 << (32 - sorted[i].Mask);
                        // 隣り合っており、かつマージ後のネットワークアドレスが妥当か確認
                        if (sorted[i].Network + size == sorted[i + 1].Network && (sorted[i].Network % (size * 2) == 0))
                        {
                            nextLevel.Add(new CidrBlock(sorted[i].Network, (byte)(sorted[i].Mask - 1)));
                            i++; // 次の要素も消費
                            changed = true;
                            continue;
                        }
                    }
                    nextLevel.Add(sorted[i]);
                }
                allCidrs = nextLevel;
            } while (changed);

            return allCidrs.Select(c => string.Format("{0}/{1}", UintToIp(c.Network), c.Mask)).ToList();
        }

        static List<CidrBlock> GetCidrBlocksFromRange(uint start, uint end)
        {
            var res = new List<CidrBlock>();
            while (end >= start)
            {
                byte maxMask = 32;
                while (maxMask > 0)
                {
                    uint mask = (uint)0xffffffff << (32 - (maxMask - 1));
                    if ((start & mask) != start) break;
                    maxMask--;
                }
                double maxDiff = Math.Floor(Math.Log((double)end - start + 1) / Math.Log(2));
                byte finalMask = Math.Max(maxMask, (byte)(32 - (byte)maxDiff));
                res.Add(new CidrBlock(start, finalMask));
                uint blockSize = (uint)1 << (32 - finalMask);
                if (0xffffffff - start < blockSize) break;
                start += blockSize;
                if (start > end) break;
            }
            return res;
        }

        static string UintToIp(uint ip) { return string.Format("{0}.{1}.{2}.{3}", (ip >> 24) & 0xFF, (ip >> 16) & 0xFF, (ip >> 8) & 0xFF, ip & 0xFF); }
        static uint IpToUint(string ip) {
            string[] parts = ip.Split('.');
            return (uint.Parse(parts[0]) << 24) | (uint.Parse(parts[1]) << 16) | (uint.Parse(parts[2]) << 8) | uint.Parse(parts[3]);
        }
        static void Log(string m) { lock (typeof(Program)) { Console.WriteLine(string.Format("[{0:yyyy/MM/dd-HH:mm:ss}] {1}", DateTime.Now, m)); } }

        struct IpRange {
            public uint Start, End;
            public IpRange(string s, uint c) { Start = IpToUint(s); End = Start + c - 1; }
        }

        struct CidrBlock {
            public uint Network; public byte Mask;
            public CidrBlock(uint n, byte m) { Network = n; Mask = m; }
        }
    }
}
