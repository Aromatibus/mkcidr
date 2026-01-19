# ⧉国外からのサーバーアクセスを遮断するCIDRリストを自前で作成してみる

## ◇はじめに

※本編よりも並列ダウンロード処理の方が珍しいとのことでこの一行を加筆しました。（笑）
※プログレスバーによる進捗表示（[rir-samechk.py][]）も実装しているのは見ないそうです。

GITHUBで公開しています。
<!-- markdownlint-disable-next-line MD034 -->
https://github.com/Aromatibus/mkcidr

:::note alert
テストは行っていますが、十分な運用期間があるとは言えないため注意してください。
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

## ◇不正アクセスの多いこと多いこと

外部からのアクセスを解放して数時間経ってからだったと思います。
なんとなくアクセスログを見たところsshへの不正アクセスが大量に検知されていました。
たった数時間なのにあまりの多さに驚愕しました。
さらに調べてみるとアクセスは国外の決まった地域からであることがわかりました。
そこで不正アクセスを次の記事を参考にして遮断することにしました。

- 不正アクセスを遮断
  - [Server World][]様の記事から[Fail2Ban : 侵入防止システム][]
  - [5分で理解するfail2ban][]
- 国外からのアクセスを遮断
  - [Nginxで国外からのWEBアクセスを遮断][]
  - [【Cent OS 6.x】国単位でIPをブロックするスクリプト with ipset][]

## ◇そして盛大な寄り道へ

さて、アクセス制限はできました。が、しかし
[世界の国別 IPv4 アドレス割り当てリスト][]（ありがとうございます！）から
ダウンロードさせて頂くCIDRリストってなんぞ？となりました。
そして調べてみたところ

:::note question
これ自分で作れないかな？
:::
となりました（平常運転）

## ◇Pythonで実装

これを作っている時が一番楽しかったかもしれない！
<!-- markdownlint-disable-next-line MD034 -->
https://github.com/Aromatibus/mkcidr/blob/main/src/mkcidr.py

## ◇C#で実装

最近は[Google Gemini][]などAIを使ってプログラムを組むのも当たり前？になりました。
言語変換もできるかな？と試したところ思いの外良い結果がでました。
そこで更に改良したものを掲載します。

※実はこの記事のきっかけです。

- コマンドラインからコンパイルする場合は次のとおりにしてください
  （GITHUBに[D&Dでコンパイルするバッチファイル][]もあります。）

```BAT
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /r:System.Net.Http.dll mkcidr.cs
```
<!-- markdownlint-disable-next-line MD034 -->
https://github.com/Aromatibus/mkcidr/blob/main/src/cs_ver/mkCIDR.cs

## ◇おわりに

NURO光を使ってるんですがWebページの作成など色々と試す前に突然、MAP-Eへ変更により外部からのアクセスができなくなりました。
トンネルを使う方法やルーターの対応如何では公開も可能なようですが、NURO光では絶望的という意見が多いようです。
そもそもNURO光は確保しているIP4アドレスが少ないらしく今後、公開サーバーの運用はほぼ絶望的みたいですね。
乗り換えを考えていますが今後はMAP-Eが当たり前になってしまうんだろうか・・・

<https://github.com/Aromatibus/>

[rir-samechk.py]: https://github.com/Aromatibus/mkcidr/blob/main/src/rir-samechk.py
[D&Dでコンパイルするバッチファイル]: https://github.com/Aromatibus/mkcidr/blob/main/src/cs_ver/CSC_Http_CLI64_DragDropHere.bat
[Server World]: https://www.server-world.info/
[Fail2Ban : 侵入防止システム]: https://www.server-world.info/query?os=CentOS_Stream_9&p=fail2ban
[5分で理解するfail2ban]: https://qiita.com/Brutus/items/28f4dc2054ad7de54e73
[Nginxで国外からのWEBアクセスを遮断]: https://qiita.com/KensukeSakakibara/items/27d15975c754758321ad
[【Cent OS 6.x】国単位でIPをブロックするスクリプト with ipset]: https://qiita.com/R123/items/dc82461ad127c5ea0703
[世界の国別 IPv4 アドレス割り当てリスト]: http://nami.jp/ipv4bycc/
[Google Gemini]: https://gemini.google.com/
