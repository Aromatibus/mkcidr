# ⧉国外からのサーバーアクセスを遮断するCIDRリストを自前で作成してみる（並列処理も有り）

## ◇はじめに

※本編より並列ダウンロード処理の方が珍しいとのことで並列処理のタグを加筆しました。
※プログレスバーによる進捗表示（[rir-samechk.py][]）も実装しているのは見ないそうです。
※AIでPythonからC#に変換したバージョンはCIDRの処理に誤りがあるためQiitaでの公開停止しました。

GitHubで公開しています。
<!-- markdownlint-disable-next-line MD034 -->
https://github.com/Aromatibus/mkcidr

:::note alert
テストは行っていますが無保証です。
十分な運用期間があるとは言えないため注意してください。
:::

:::note warn
※注　前置きが長いので興味の無い方は読み飛ばし推薦です。
:::

今からおよそ2年前に自宅サーバーを立ち上げようとしました。
準備を進めていたところでNURO光に突然MAP-Eが導入されました。
調べた結果、無料では公開サーバーは不可能だと結論に至りました。
そして計画は断念そのまま放置していました。

とは言え、色々と楽しかったのですが（笑）

※準備中、[Server World][]様には大変お世話になりました。ありがとうございます！！
<!-- markdownlint-disable-next-line MD034 -->
https://www.server-world.info/

## ◇不正アクセスの多いこと多いこと

外部からのアクセスを解放して数時間経ってからだったと思います。
なんとなくアクセスログを見たところsshへの不正アクセスが大量に検知されていました。
たった数時間なのにあまりの多さに驚愕しました。
さらに調べてみるとアクセスは国外の決まった地域からであることがわかりました。
そこで不正アクセスを次の記事を参考にして遮断することにしました。

- 不正アクセスを遮断
  - [Fail2Ban : 侵入防止システム][]
  - [5分で理解するfail2ban][]
- 国外からのアクセスを遮断
  - [Nginxで国外からのWEBアクセスを遮断][]
  - [【Cent OS 6.x】国単位でIPをブロックするスクリプト with ipset][]

## ◇そして盛大な寄り道へ

さて、アクセス制限はできました。が、しかし
「[世界の国別 IPv4 アドレス割り当てリスト][]」（ありがとうございます！）から
ダウンロードさせて頂くCIDRリストってなんぞ？となりました。

<!-- markdownlint-disable-next-line MD034 -->
http://nami.jp/ipv4bycc/

そして調べてみたところ

:::note question
これ自分で作れないかな？
:::
となりました。

また、「[Office Nami][]」様が善意で公開されている「[世界の国別 IPv4 アドレス割り当てリスト][]」は自身の注意書きにあるとおり公開停止されてしまうこともあります。
そのような事があっても自前で準備できれば安心です。

## ◇Pythonで実装

今回の目的「[世界の国別 IPv4 アドレス割り当てリスト][]」からダウンロードできる`cidr.txt`と同等なファイルは`\ip-lists\ipv4\_CIDR.ipv4`です。

それぞれ作成されるファイルについて説明いたします。
まず、プログラムファイルと同階層に`\ip-lists\`フォルダが作成されます。

直下にダウンロードした5つのファイルがあります。
ファイル名は`delegated-********-extended-latest`（"*"にはRIRを管理する5つの団体名）です。

次にCIDRに変換されたファイルですが、ファルダは`IPv4`と`IPv6`に分かれます。
それぞれのフォルダ下にCIDRに変換されたアルファベット2桁の国名に分かれたファイルと統合されたファイルがあります。
統合されたファイルは`_CIDR.ipv4`と`_CIDR.ipv6`です。

残る`_Same_RIR.ipv*`ですがこれは管理する5つの団体同士でIPアドレスの譲渡が行われており日によって同じIPアドレスが別の団体のファイルに存在することがあるからです。
同じIPアドレスが見つかった場合は`_Same_RIR.ipv*`にそのアドレスデータが保存されるようになっています。およそ数日で解消されます。

<!-- markdownlint-disable-next-line MD034 -->
https://github.com/Aromatibus/mkcidr/blob/main/src/mkcidr.py

## ◇おわりに

NURO光を使ってるんですがWebページの作成など色々と試す前に突然、MAP-Eへ変更により外部からのアクセスができなくなりました。
トンネルを使う方法やルーターの対応如何では公開も可能なようですが、NURO光では絶望的という意見が多いようです。
そもそもNURO光は確保しているIP4アドレスが少ないらしく今後、公開サーバーの運用はほぼ絶望的みたいですね。
乗り換えを考えていますが今後はMAP-Eが当たり前になってしまうんだろうか・・・

<!-- markdownlint-disable-next-line MD034 -->
https://github.com/Aromatibus/

[rir-samechk.py]: https://github.com/Aromatibus/mkcidr/blob/main/src/rir-samechk.py
[D&Dでコンパイルするバッチファイル]: https://github.com/Aromatibus/mkcidr/blob/main/src/cs_ver/CSC_Http_CLI64_DragDropHere.bat
[Server World]: https://www.server-world.info/
[Fail2Ban : 侵入防止システム]: https://www.server-world.info/query?os=CentOS_Stream_9&p=fail2ban
[5分で理解するfail2ban]: https://qiita.com/Brutus/items/28f4dc2054ad7de54e73
[Nginxで国外からのWEBアクセスを遮断]: https://qiita.com/KensukeSakakibara/items/27d15975c754758321ad
[【Cent OS 6.x】国単位でIPをブロックするスクリプト with ipset]: https://qiita.com/R123/items/dc82461ad127c5ea0703

[Office Nami]: http://nami.jp/
[世界の国別 IPv4 アドレス割り当てリスト]: http://nami.jp/ipv4bycc/
[Google Gemini]: https://gemini.google.com/
