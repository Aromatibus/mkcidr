# ⧉国外からのサーバーアクセスを遮断するCIDRリストを自前で作成してみる（並列処理も有り）

## ◇はじめに

企業はもちろんですが個人でVPNや自宅サーバーのセキュリティーを高めるために国外からのアクセスを制限を設ける事は非常に有用です。

私の場合、実際に不正アクセスの履歴を追うと特定の国からのアクセスだけで日本国内からの不正アクセスはありませんでした。

不正アクセスを防止する方法としては

- 不正アクセスを遮断
  - [Fail2Ban : 侵入防止システム][]
  - [5分で理解するfail2ban][]
- 国外からのアクセスを遮断
  - [Nginxで国外からのWEBアクセスを遮断][]
  - [【Cent OS 6.x】国単位でIPをブロックするスクリプト with ipset][]

が有効且つ有名な方法です。

アクセス制限をするためにはipアドレスがどの国の物なのか記録したIPアドレスリストが必要になります。

<!-- markdownlint-disable-next-line MD034 -->
http://nami.jp/ipv4bycc/

しかし「[世界の国別 IPv4 アドレス割り当てリスト][]」は注意書きにもあるとおり公開を停止してしまうことがありえます。

そこでサーバー内でリストを自作してしまうのが本プログラムとなります。

## ◇Pythonで実装

<!-- markdownlint-disable-next-line MD034 -->
https://github.com/Aromatibus/mkcidr

### ・RIR to CIDR

<!-- markdownlint-disable-next-line MD034 -->
https://github.com/Aromatibus/mkcidr/blob/main/src/mkcidr.py

※Qiitaの埋め込み表示制限により200行までしか表示されません。
　全体はリンク先を直接見てください。

:::note info
RIRからCIDRへ変換するプログラムです。
IPv4、IPv6の両方を変換、リストを作成します。
高速化を狙って並列ダウンロートなど並列処理をしています。
:::

:::note question
2026/01/21
なるべくシンプルになるよう全体を見直しました。
サイズは3分2ほどになり処理も早くなった気がします。
loggerなど使わなくなった関数もあるのでオリジナルも残してあります。
:::

それぞれ作成されるファイルについて説明いたします。

今回の目的である「[世界の国別 IPv4 アドレス割り当てリスト][]」からダウンロードできる`cidr.txt`と同等のファイルは`\ip-lists\ipv4\_CIDR.ipv4`です。

プログラムファイルと同階層に`\ip-lists\`フォルダが作成されます。

直下にダウンロードした5つのファイルがあります。
ファイル名は`delegated-********-extended-latest`（"*"はRIRの管理団体名）

次にCIDRに変換されたファイルですが、ファルダは`IPv4`と`IPv6`に分かれます。
それぞれのフォルダ下にCIDRへ変換されたアルファベット2桁の国名に分かれたファイルと統合されたファイルがあります。

統合されたファイルは`_CIDR.ipv4`と`_CIDR.ipv6`です。

### ・IPv4 Same Checker

<!-- markdownlint-disable-next-line MD034 -->
https://github.com/Aromatibus/mkcidr/blob/main/src/rir-samechk.py

:::note info
IPv4のみですが重複アドレスをチェックするプログラムです。
プログレスバーによる進捗表示を実装しています。
:::

IPアドレスは管理する5つの団体同士で譲渡されることがあります。
その際に日によって同じIPアドレスが同時に別の国に存在することがあります。
（数日で解消されます）
それをチェックします。
検出結果は`_Same_RIR.ipv4`に保存されます。

## ◇おわりに

最初にアップした記事は蛇足が多すぎたので大幅に加筆修正させていただきました。
最後までお読みいただきありがとうございました！

<!-- markdownlint-disable-next-line MD034 -->
https://github.com/Aromatibus/

[Fail2Ban : 侵入防止システム]: https://www.server-world.info/query?os=CentOS_Stream_9&p=fail2ban
[5分で理解するfail2ban]: https://qiita.com/Brutus/items/28f4dc2054ad7de54e73
[Nginxで国外からのWEBアクセスを遮断]: https://qiita.com/KensukeSakakibara/items/27d15975c754758321ad
[【Cent OS 6.x】国単位でIPをブロックするスクリプト with ipset]: https://qiita.com/R123/items/dc82461ad127c5ea0703
[世界の国別 IPv4 アドレス割り当てリスト]: http://nami.jp/ipv4bycc/
