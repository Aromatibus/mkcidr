import os
from urllib.parse import urlparse

import requests
from tqdm import tqdm

url = "http://ftp.ripe.net/pub/stats/ripencc/delegated-ripencc-extended-latest"
filename = os.path.basename(urlparse(url).path)

response = requests.get(url, stream=True)

# ファイルサイズを取得
file_size = int(response.headers.get('content-length', 0))

# tqdm を使用して進捗を表示
with open(filename, 'wb') as file, tqdm(
    desc=filename.ljust(35),
    total=file_size,
    unit='B',
    unit_scale=True,
    unit_divisor=1024,
) as bar:
    for data in response.iter_content(chunk_size=1024):
        bar.update(len(data))
        file.write(data)

print("ダウンロードが完了しました。")
