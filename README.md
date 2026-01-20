# ⧉国外からのサーバーアクセスを遮断するCIDRリストを自前で作成してみる（並列処理も有り）

## ◇はじめに

企業はもちろんですが個人でVPNや自宅サーバーのセキュリティーを高めるために国外から
のアクセスを制限を設ける事は非常に有用です。
私の場合、実際に不正アクセスの履歴を追うと特定の国からのアクセスだけで日本国内から
の不正アクセスはありませんでした。

不正アクセスを防止する方法としては

- 不正アクセスを遮断
  - [Fail2Ban : 侵入防止システム][]
  - [5分で理解するfail2ban][]
- 国外からのアクセスを遮断
  - [Nginxで国外からのWEBアクセスを遮断][]
  - [【Cent OS 6.x】国単位でIPをブロックするスクリプト with ipset][]

が有効且つ有名な方法です。

アクセス制限をするためにはipアドレスがどの国の物なのか記録したIPアドレスリストが
必要になります。
<!-- markdownlint-disable-next-line MD034 -->
http://nami.jp/ipv4bycc/

しかし「[世界の国別 IPv4 アドレス割り当てリスト][]」は注意書きにもあるとおり公開
停止してしまうことがありえます。
そこでサーバー内でリストを自作してしまうのが本プログラムとなります。

## ◇Pythonで実装

:::note info
高速化を狙って並列ダウンロートなど並列処理をしています。
また、別のプログラムではプログレスバーの進捗状況表示を実装しています。

- プログレスバーの進捗表示（[rir-samechk.py][]）
:::

今回の目的「[世界の国別 IPv4 アドレス割り当てリスト][]」からダウンロード
できる`cidr.txt`と同等なファイルは`\ip-lists\ipv4\_CIDR.ipv4`です。

それぞれ作成されるファイルについて説明いたします。
まず、プログラムファイルと同階層に`\ip-lists\`フォルダが作成されます。

直下にダウンロードした5つのファイルがあります。
ファイル名は`delegated-********-extended-latest`（"*"はRIRの管理団体名）

次にCIDRに変換されたファイルですが、ファルダは`IPv4`と`IPv6`に分かれます。
それぞれのフォルダ下にCIDRに変換されたアルファベット2桁の国名に分かれたファイルと
統合されたファイルがあります。

統合されたファイルは`_CIDR.ipv4`と`_CIDR.ipv6`です。

`_Same_RIR.ipv*`は管理する5つの団体同士でIPアドレスの譲渡の際に日によって
同じIPアドレスが複数存在することがあるため同じIPアドレスが見つかった場合に
`_Same_RIR.ipv*`にそのアドレスデータが保存されるようになっています。

およそ数日で解消されます。

<!-- markdownlint-disable-next-line MD034 -->
https://github.com/Aromatibus/mkcidr/blob/main/src/mkcidr.py

## ◇おわりに

最初にアップした記事は蛇足が多すぎたので大幅に加筆修正させていただきました。
最後までお読みいただきありがとうございました！
<!-- markdownlint-disable-next-line MD034 -->
https://github.com/Aromatibus/

[rir-samechk.py]: https://github.com/Aromatibus/mkcidr/blob/main/src/rir-samechk.py
[Fail2Ban : 侵入防止システム]: https://www.server-world.info/query?os=CentOS_Stream_9&p=fail2ban
[5分で理解するfail2ban]: https://qiita.com/Brutus/items/28f4dc2054ad7de54e73
[Nginxで国外からのWEBアクセスを遮断]: https://qiita.com/KensukeSakakibara/items/27d15975c754758321ad
[【Cent OS 6.x】国単位でIPをブロックするスクリプト with ipset]: https://qiita.com/R123/items/dc82461ad127c5ea0703
[世界の国別 IPv4 アドレス割り当てリスト]: http://nami.jp/ipv4bycc/
