# はじめに

日々、趣味のプログラムを書いたりして楽しんでいます。
Pythonに興味を持ちPythonのあまりのすばらしさに感動しています。
その流れからWebアプリを作ってみたいと思い、いきおいでVPSを借りてみました。
Linux自体はじめてだったため一から勉強しながら進めています。
その過程で学んだことをまとめていきたいと思います。

## ◇複数行のコメントについて

コメント記述は通常"[rem][]"ですが、そのほかに"::"が利用できます。
この:（コロン）を二つ重ねたものはラベルの記載方法を利用したもので公式のものではないテクニックとなるようですが、複数行に渡ってコメントをする方法が公式にあることはあまり知られていません。
方法は公式のマイクロソフトドキュメント「[rem][]」に記載されていますので抜粋します。

<details><summary>複数行のコメントのサンプル</summary>

```bat:Sample.bat
Rem/||(
    The REM statement evaluates to success,
    so these lines will never be executed.
    Keep in mind that you will need to escape closing parentheses
    within multi-line comment blocks like shown in this example. ^)
  )
```

</details>

### ・コメント行のバグについて

"Rem/||()"を使ったコメントは公式にしては色々と問題を起こします。
私自身それほど利用する機会はないため検証できていません。仕様と割り切るしかなさそうです。
"::"のコメントについても問題を起こすケースがありますが、こちらは行末に";"を付けることで回避できます。

:::note info
※2022/07/14
「[DOSバッチファイルの複数行のコメント][]」にバグ？について記載を見つけました。
「FORおよびIFコマンドは、解析されるため、閉じ括弧と無効な構文には注意する必要があります。」
とのことです。
:::

# ◇管理者権限の付与（空白名対応版）

powershellを利用したテクニックは有名なのですが、引数の引き渡しに言及したものは見たことがありませんでした。
どうもファイル名、フォルダ名に空白を含むと誤動作をすることが原因だったようです。
私も指摘を受け空白が含まれているファイル名、フォルダ名に対応するものに作り直しました。
バグが残っている可能性はありますが掲載いたします。

:::note info
【 ポイント解説 】
以前からあるバージョンはバッチファイルを直接起動し自身はそのまま終了する方法で管理者権限を得ています。
新しいバージョンはコマンドプロンプトを管理者権限で新しく起動する方法で管理者権限を得ています。
エクスプローラーからのバッチファイルをダブルクリックや別のファイルをドラックアンドドロップして起動した場合は違いを感じることはほとんどありません。
しかし、コマンドプロンプトから起動した場合は新しくコマンドプロンプトを起動しているため「古いウィンドウをどうするか」という問題がでてしまいます。
以下のサンプルでは「[◇Windowsのバッチファイルで実行方法を判別する][]」の利用してエクスプローラーから起動した場合のみ古いウィンドウを閉じるようにしています。

```
echo %cmdcmdline%|find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 (exit)
goto :eof
```

この三行を書き換えることで管理者権限へ移行時の処理を変更できます。
以下に変更候補の例を紹介します。
|記述|結果|
|:-|:-|
|goto :eof|バッチファイルを終了させます。|
|exit|コマンドプロンプトを閉じます。|
|Timeout /t 3 /nobreak|指定秒待機後、処理を続行します。上記と組み合わせて使用します。|

あくまで一例ですが、参考になれば幸いです。
:::

<details><summary>管理者権限付与（引数、空白対応版）</summary>

```bat
:: 遅延展開宣言 バグの原因になる場合があります;
setlocal enabledelayedexpansion


:: 管理者権限がない場合は管理者権限で実行し直す;
openfiles>NUL 2>&1
if %ERRORLEVEL% equ 0 (goto :Admin)
set ARGV=&&for %%a in (%*) do (set ARGV=!ARGV! \"%%a\")
powershell.exe -Command Start-Process %comspec% -ArgumentList "'/c, \"%~f0\", %ARGV%'" -Verb Runas
echo %cmdcmdline%|find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 (exit)
goto :eof
:Admin
```

</details>

:::note info
サンプル中、引数を処理する部分にさらに手を加えた物を使用しています。
ここだけ抜粋して他へ応用できます。
:::

<details><summary>管理者権限付与の動作テストサンプル</summary>

```bat:ElevateAdmin.bat
@echo off


:: 遅延展開宣言 バグの原因になる場合があります;
setlocal enabledelayedexpansion


:: 管理者権限がない場合は管理者権限で実行し直す;
openfiles>NUL 2>&1
if %ERRORLEVEL% equ 0 (goto :Admin)
set ARGV=&&for %%a in (%*) do (set ARGV=!ARGV! \"%%a\")
powershell.exe -Command Start-Process %comspec% -ArgumentList "'/c, \"%~f0\", %ARGV%'" -Verb Runas
echo %cmdcmdline%|find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 (exit)
goto :eof
:Admin


set ARGV=&&set ARGC=0
for %%a in (%*) do (set /a ARGC+=1&&set ARGV!ARGC!=%%a&&set ARGV=!ARGV! \"%%a\")

echo.
echo 0=%%0[%0]
echo %%*=[%*]
echo.
echo ARGC=[%ARGC%]
echo ARGV=[%ARGV%]
echo.
echo 1=%%1[%1], ARGV1[%ARGV1%]
echo 2=%%2[%2], ARGV2[%ARGV2%]
echo 3=%%3[%3], ARGV3[%ARGV3%]
echo 4=%%4[%4], ARGV4[%ARGV4%]
echo 5=%%5[%5], ARGV5[%ARGV5%]
echo.


:: 終了処理（エクスプローラーから起動されていた場合はPauseする）;
:EndProcess
echo %cmdcmdline%|find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 (pause)
goto :eof
```

</details>

色々なバージョンがありますが参考に掲載します。

<details><summary>管理者権限付与（旧版）</summary>

```bat
:: 管理者権限で実行されていない場合、自分を管理者権限で実行し直す;
openfiles > NUL 2>&1
if %errorlevel% neq 0 (
powershell start-process %~0 -verb runas
goto :eof
)
```

</details>

# ◇エスケープシーケンスによる画面制御

これは有名ですが紹介します。
必ず"setlocal"を先に宣言します。
カラーコードなど制御文の説明に見やすいものが見当たらなかったため英文ですがマイクロソフトの「[コンソール仮想端末シーケンス][]」とサンプルのバッチを掲載します。

### ・画面制御とカラー文字のサンプル

<details><summary>画面制御とカラー文字のサンプル</summary>

```bat:Esc.bat
@echo off


:: 遅延展開 バグの原因になる場合があるので注意;
setlocal enabledelayedexpansion


:: %ESC%でエスケープシーケンスを利用できるようにする;
for /f "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set ESC=%%b)


echo.
echo 画面制御
echo 文字列  説明  備考
echo %%ESC%%[0J  カーソル位置から画面右下まで消去
echo %%ESC%%[1J  画面左上からカーソル位置まで消去
echo %%ESC%%[2J  画面クリア
echo %%ESC%%[0K  カーソル位置から右側消去  同一行
echo %%ESC%%[1K  カーソル位置から左側消去  同一行
echo %%ESC%%[2K  カーソルのある１行の消去
echo %%ESC%%[nA  カーソルをn行上へ移動
echo %%ESC%%[nB  カーソルをn行下へ移動
echo %%ESC%%[nC  カーソルをn桁右へ移動  右端で停止
echo %%ESC%%[nD  カーソルをn桁左へ移動  左端で停止
echo %%ESC%%[r;cH  カーソルをr行、n桁目へ移動  もしくは%%ESC%%[r;nf
echo ------------------------------------
echo.
echo.


echo.
echo これはテストです。この行が書き変わります。
pause

echo %ESC%[2A%ESC%[2K
echo %ESC%[1A%ESC%[2K
echo %ESC%[2A
echo 書き換えられたでしょうか
pause


echo.
echo %ESC%[41;97mエスケープシーケンスによるカラー出力テスト%ESC%[0m
echo.
echo https://docs.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences
echo.
echo %%ESC%%[101;93m%ESC%[101;93m STYLES %ESC%[0m
echo %%ESC%%[0m %ESC%[0mReset%ESC%[0m
echo %%ESC%%[1m %ESC%[1mBold%ESC%[0m
echo %%ESC%%[4m %ESC%[4mUnderline%ESC%[0m
echo %%ESC%%[7m %ESC%[7mInverse%ESC%[0m
echo.
echo %%ESC%%[42;93m%ESC%[42;93m NORMAL FOREGROUND COLORS %ESC%[0m
echo %%ESC%%[30m %ESC%[30mBlack%ESC%[0m (black)
echo %%ESC%%[31m %ESC%[31mRed%ESC%[0m
echo %%ESC%%[32m %ESC%[32mGreen%ESC%[0m
echo %%ESC%%[33m %ESC%[33mYellow%ESC%[0m
echo %%ESC%%[34m %ESC%[34mBlue%ESC%[0m
echo %%ESC%%[35m %ESC%[35mMagenta%ESC%[0m
echo %%ESC%%[36m %ESC%[36mCyan%ESC%[0m
echo %%ESC%%[37m %ESC%[37mWhite%ESC%[0m
echo.
echo %%ESC%%[43;30m%ESC%[43;30m NORMAL BACKGROUND COLORS %ESC%[0m
echo %%ESC%%[40m %ESC%[40mBlack%ESC%[0m
echo %%ESC%%[41m %ESC%[41mRed%ESC%[0m
echo %%ESC%%[42m %ESC%[42mGreen%ESC%[0m
echo %%ESC%%[43m %ESC%[43mYellow%ESC%[0m
echo %%ESC%%[44m %ESC%[44mBlue%ESC%[0m
echo %%ESC%%[45m %ESC%[45mMagenta%ESC%[0m
echo %%ESC%%[46m %ESC%[46mCyan%ESC%[0m
echo %%ESC%%[47m %ESC%[47mWhite%ESC%[0m (white)
echo.
echo %%ESC%%[47;30m%ESC%[47;30m STRONG FOREGROUND COLORS %ESC%[0m
echo %%ESC%%[90m %ESC%[90mWhite%ESC%[0m
echo %%ESC%%[91m %ESC%[91mRed%ESC%[0m
echo %%ESC%%[92m %ESC%[92mGreen%ESC%[0m
echo %%ESC%%[93m %ESC%[93mYellow%ESC%[0m
echo %%ESC%%[94m %ESC%[94mBlue%ESC%[0m
echo %%ESC%%[95m %ESC%[95mMagenta%ESC%[0m
echo %%ESC%%[96m %ESC%[96mCyan%ESC%[0m
echo %%ESC%%[97m %ESC%[97mWhite%ESC%[0m
echo.
echo %%ESC%%[41;97m%ESC%[41;97m STRONG BACKGROUND COLORS %ESC%[0m
echo %%ESC%%[100m %ESC%[100mBlack%ESC%[0m
echo %%ESC%%[101m %ESC%[101mRed%ESC%[0m
echo %%ESC%%[102m %ESC%[102mGreen%ESC%[0m
echo %%ESC%%[103m %ESC%[103mYellow%ESC%[0m
echo %%ESC%%[104m %ESC%[104mBlue%ESC%[0m
echo %%ESC%%[105m %ESC%[105mMagenta%ESC%[0m
echo %%ESC%%[106m %ESC%[106mCyan%ESC%[0m
echo %%ESC%%[107m %ESC%[107mWhite%ESC%[0m
echo.
echo %%ESC%%[101;93m%ESC%[101;93m COMBINATIONS %ESC%[0m
echo %%ESC%%[31m                     %ESC%[31mred foreground color%ESC%[0m
echo %%ESC%%[7m                      %ESC%[7minverse foreground ^<-^> background%ESC%[0m
echo %%ESC%%[7;31m                   %ESC%[7;31minverse red foreground color%ESC%[0m
echo %%ESC%%[7m and nested %%ESC%%[31m %ESC%[7mbefore %ESC%[31mnested%ESC%[0m
echo %%ESC%%[31m and nested %%ESC%%[7m %ESC%[31mbefore %ESC%[7mnested%ESC%[0m
echo.


:: 終了処理（エクスプローラーから起動されていた場合はPauseする）;
:EndProcess
echo %cmdcmdline% | find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 (cmd /k)
goto :eof
```

</details>

### ・可視光線のシミュレート

これは見たことないですね。
一応、オリジナルです。
最後は白になるようにしていますがこんな感じのを表示します。
![Visible light](https://upload.wikimedia.org/wikipedia/commons/c/cc/Spectrum.svg)

<details><summary>R.B.G. カラーグラデーションのサンプル</summary>

```bat:RGB.bat
@echo off


:: 遅延展開 バグの原因になる場合があるので注意;
setlocal enabledelayedexpansion


:: %ESC%でエスケープシーケンスを利用できるようにする;
for /f "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set ESC=%%b)

set MinValue=0
set MaxValue=255
set ChgValue=0
set Shape=■

echo.
echo R.G.B. Pattern

set R=%MinValue%
set G=%MinValue%
set B=%MinValue%
set RGBBox=

set RGBBox=%ESC%[38;2;%R%;%G%;%B%m%Shape%
set R=%MaxValue%
set RGBBox=%RGBBOX%%ESC%[38;2;%R%;%G%;%B%m%Shape%
set G=%MaxValue%
set RGBBox=%RGBBOX%%ESC%[38;2;%R%;%G%;%B%m%Shape%
set R=%MinValue%
set RGBBox=%RGBBOX%%ESC%[38;2;%R%;%G%;%B%m%Shape%
set B=%MaxValue%
set RGBBox=%RGBBOX%%ESC%[38;2;%R%;%G%;%B%m%Shape%
set G=%MinValue%
set RGBBox=%RGBBOX%%ESC%[38;2;%R%;%G%;%B%m%Shape%
set R=%MaxValue%
set RGBBox=%RGBBOX%%ESC%[38;2;%R%;%G%;%B%m%Shape%
set G=%MaxValue%
set RGBBox=%RGBBOX%%ESC%[38;2;%R%;%G%;%B%m%Shape%
echo %RGBBOX%%ESC%[0m
echo.


echo Mono Color Pattern / R.G.B. Gradations
set ChgValue=8
set RGBBox=
for /l %%m in (%MinValue%, %ChgValue%, %MaxValue%) do (
  set RGBBox=!RGBBox!%ESC%[38;2;%%m;%%m;%%mm%Shape%
)
echo %RGBBOX%%ESC%[0m
echo.


echo Spectrum Pattern / R.G.B. Gradations
set R=%MinValue%
set G=%MinValue%
set B=%MinValue%
set ChgValue=32
set RGBBox=

:: Blue Min to Max;
for /l %%b in (%MinValue%, %ChgValue%, %MaxValue%) do (
  set RGBBox=!RGBBox!%ESC%[38;2;%R%;%G%;%%bm%Shape%
)
set B=%MaxValue%

:: Green Min to Max;
for /l %%g in (%MinValue%, %ChgValue%, %MaxValue%) do (
  set RGBBox=!RGBBox!%ESC%[38;2;%R%;%%g;%B%m%Shape%
)
set G=%MaxValue%

:: Blue Max to Min;
for /l %%b in (%MaxValue%, -%ChgValue%, %MinValue%) do (
  set RGBBox=!RGBBox!%ESC%[38;2;%R%;%G%;%%bm%Shape%
)
set B=%MinValue%

:: Red Min to Max;
for /l %%r in (%MinValue%, %ChgValue%, %MaxValue%) do (
  set RGBBox=!RGBBox!%ESC%[38;2;%%r;%G%;%B%m%Shape%
)
set R=%MaxValue%

:: Green Max to Min;
for /l %%g in (%MaxValue%, -%ChgValue%, %MinValue%) do (
  set RGBBox=!RGBBox!%ESC%[38;2;%R%;%%g;%B%m%Shape%
)
set G=%MinValue%

:: Blue Min to Max;
for /l %%b in (%MinValue%, %ChgValue%, %MaxValue%) do (
  set RGBBox=!RGBBox!%ESC%[38;2;%R%;%G%;%%bm%Shape%
)
set B=%MaxValue%

:: Green Min to Max;
for /l %%g in (%MinValue%, %ChgValue%, %MaxValue%) do (
  set RGBBox=!RGBBox!%ESC%[38;2;%R%;%%g;%B%m%Shape%
)
set G=%MaxValue%

set RGBBox=%RGBBox%%ESC%[38;2;%R%;%G%;%B%m%Shape%

echo %RGBBOX%%ESC%[0m
echo.


:: 終了処理（エクスプローラーから起動されていた場合はPauseする）;
:EndProcess
echo %cmdcmdline%|find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 (cmd /k)
goto :eof
```

</details>

# ◇入力された値が数値か確認する

サンプルのみ掲載します。

<details><summary>入力された値が数値か確認するサンプル</summary>

```bat:NumCheck.bat
@echo off


:: 遅延展開宣言 バグの原因になる場合があります;
setlocal enabledelayedexpansion


:: 入力されたものが指定された範囲の数値かチェックする;
:InputNumeric
set NumMin=10
set NumMax=100
echo 数値を%NumMin%～%NumMax%の範囲で入力してください。
set /p Num=">"
:: 数値チェック;
call :IsInteger %%Num%%
if %ERRORLEVEL% neq 0 (
  echo 数値以外が含まれています。
  goto :InputNumeric
)
:: 指定サイズチェック; ifを重ねて AND を判定をしています。;
if %Num% geq %NumMin% if %Num% leq %NumMax% goto :InputNumericEnd
echo 入力する数値が指定可能な範囲外です。
echo.
goto :InputNumeric
:InputNumericEnd
echo.
echo 入力された数値は [%Num%] でした。


:: 終了処理（エクスプローラーから起動されていた場合はPauseする）;
:EndProcess
echo %cmdcmdline% | find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 Pause
goto :end


:: 変数が数値かチェック;
:IsInteger
set X=%1
if "%X%" equ "" exit /b -1
if defined X set X=%X:0=%
if defined X set X=%X:1=%
if defined X set X=%X:2=%
if defined X set X=%X:3=%
if defined X set X=%X:4=%
if defined X set X=%X:5=%
if defined X set X=%X:6=%
if defined X set X=%X:7=%
if defined X set X=%X:8=%
if defined X set X=%X:9=%
if not defined X exit /b 0
exit /b -1
```

</details>

# ◇空きドライブを検索

サンプルのみ掲載します。

<details><summary>空きドライブ検索のサンプル</summary>

```bat:UnUsedDrive.bat
@echo off


:: 遅延展開宣言 バグの原因になる場合があります;
setlocal enabledelayedexpansion


:: 空きドライブを検索;
set DRIVE=ABCDEFGHIJKLMNOPQRSTUVWXYZ
for /l %%i in (0,1,25) do (
  set DL=!DRIVE:~%%i,1!
  if not exist !DL!: (set UNUSEDRIVE=!UNUSEDRIVE!!DL!)
)
echo 使われていないドライブは [%UNUSEDRIVE%] です。
echo.


:: 終了処理（エクスプローラーから起動されていた場合はPauseする）;
:EndProcess
echo %cmdcmdline%|find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 Pause
goto :end
```

</details>

# ◇日時を好みのフォーマットで作成

バッチファイルの中で日付や曜日、時刻を表示したい時がありますが自由なフォーマットにするのは案外難しいです。
次の方法なら見た目にもシンプルで自由度が高いのでお勧めです。
フォーマットの書式は

|内容|変数|
|:-|:-:|
|西暦|%%1|
|月|%%2|
|日|%%3|
|曜日|%%4|
|時|%%5|
|分|%%6|
|秒|%%7|
|ミリ秒|%%8|

上記を参考に
|表記|記述式|
|:-|:-|
|YYYY/MM/DD(Week) HH:MM:SS.MS|%%1/%%2/%%3(%%4) %%5:%%6:%%7.%%8|
|MM/DD HH:MM|%%2/%%3 %%5:%%6|

のように区切り文字を自由に指定して必要ないものは省けます。
次にサンプルを掲載します。

<details><summary>日時を好みのフォーマットで作成のサンプル</summary>

```bat:YMDHMS.bat
@echo off


:: 遅延展開宣言 バグの原因になる場合があります;
setlocal enabledelayedexpansion


:: 日時を好みのフォーマットで作成;
set WeekChar="Sun,Mon,Tue,Wed,Thu,Fri,Sat"
powershell.exe "exit (Get-Date).DayOfWeek"
set /a WEEKDAY=%ERRORLEVEL% + 1
for /f "tokens=%WEEKDAY% delims=," %%w in (%WeekChar%) do set WEEK=%%w
for /f "tokens=1-8 delims=/:. " %%1 in ("%date% %WEEK% %time: =0%") do set YMDHMS=%%1/%%2/%%3/(%%4) %%5:%%6:%%7.%%8
echo 今の日時は%YMDHMS%です。


:: 終了処理（エクスプローラーから起動されていた場合はPauseする）;
:EndProcess
echo %cmdcmdline%|find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 Pause
goto :end
```

</details>

<details><summary>Powershellを使いたくない場合はツェラーの公式が使えます。</summary>

```bat:Powershell.DayOfWeek
powershell.exe "exit (Get-Date).DayOfWeek"
```

の代わりに

```bat:Zeller's congruence
set /a YY=%DATE:~0,4%
set /a MM=%DATE:~5,2%
set /a DD=%DATE:~8,2%
if %MM% leq 2 (set /a YY=%YY% - 1 && set /a MM=%MM% + 12)
set /a WEEKDAY=((%YY% + %YY% / 4 - %YY% / 100 + %YY% / 400 + (13 * %MM% + 8) / 5 + %DD%) %% 7) + 1
```

に変更します。
</details>

# ◇Beepや音楽を鳴らす

様々な方法がありますのでまとめて紹介します。
PowerShellを使うと好きな音楽を奏でることもできます。
guitarrapc_tech様の「[PowerShellでビープ音の「ドレミの歌」を奏でてみよう][]」がイイ感じです。

<details><summary>Beepや音楽を鳴らすのサンプル</summary>

```bat:BeepMusic.bat
@echo off


:: 遅延展開宣言 バグの原因になる場合があります;
setlocal enabledelayedexpansion


:: Beepや音楽を鳴らす;
echo.
echo 方法 1
echo 制御文字をそのまま出力する
pause
echo 

echo.
echo 方法 2
echo 制御文字を作成する
pause
for /f "delims=0" %%a in ('cmd.exe /u /c echo 〇') do @echo %%a

echo.
echo 方法 3
echo 制御文字を作成し環境変数に登録して鳴らす
pause
for /f "delims=0" %%a in ('cmd.exe /u /c echo 〇') do set BEL=%%a
echo %BEL%

echo.
echo 方法 4
echo Windows標準のビープを鳴らす
pause
rundll32 user32.dll,MessageBeep

echo.
echo 方法 5
echo Powershellを使って自由な音階で鳴らす
pause
PowerShell ^&{Start-Sleep -milliseconds 100;[Console]::Beep(524,500);[Console]::Beep(660,500);[Console]::Beep(784,500);[Console]::Beep(1046,900);}


:: 終了処理（エクスプローラーから起動されていた場合はPauseする）;
:EndProcess
echo %cmdcmdline%|find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 Pause
goto :end
```

</details>

<details><summary>再生できる音階（周波数）をテストするサンプル</summary>

```bat:ScaleFreqTest.bat
@echo off


:: 遅延展開 バグの原因になる場合があるので注意;
setlocal enabledelayedexpansion


:: BPMを元に４分音符（単位ミリ秒）を計算;
set BPM=120
set /a QuarterNote=60 * 1000 / %BPM%
set REST=Start-Sleep -milliseconds
:: 音階の国際表記と周波数（小数点以下を活かすため1000倍にしておく）;
set Cn0=16352
set Cs0=17324
set Dn0=18354
set Ds0=19446
set En0=20602
set Fn0=21827
set Fs0=23125
set Gn0=24500
set Gs0=25957
set An0=27500
set As0=29135
set Bn0=30868
:: 音階毎に周波数を設定;
for /l %%i in (0, 1, 9) do (
  set /a RATE=1
  for /l %%x in (1, 1, %%i) do (set /a RATE=!RATE!*2)
  set /a Cn%%i=%Cn0% * !RATE! / 1000
  set /a Cs%%i=%Cs0% * !RATE! / 1000
  set /a Dn%%i=%Dn0% * !RATE! / 1000
  set /a Ds%%i=%Ds0% * !RATE! / 1000
  set /a En%%i=%En0% * !RATE! / 1000
  set /a Fn%%i=%Fn0% * !RATE! / 1000
  set /a Fs%%i=%Fs0% * !RATE! / 1000
  set /a Gn%%i=%Gn0% * !RATE! / 1000
  set /a Gs%%i=%Gs0% * !RATE! / 1000
  set /a An%%i=%An0% * !RATE! / 1000
  set /a As%%i=%As0% * !RATE! / 1000
  set /a Bn%%i=%Bn0% * !RATE! / 1000
)


echo.
echo BPM=%BPM%
echo QuarterNote=%QuarterNote%ms
echo.
echo ♪再生テスト（ドミソド）
echo.
PowerShell ^&{^
  (%REST% %QuarterNote%);^
  Write-Output "Cn5=%Cn5%Hz";[Console]::Beep(%Cn5%, %QuarterNote%);^
  Write-Output "En5=%En5%Hz";[Console]::Beep(%En5%, %QuarterNote%);^
  Write-Output "Gn5=%Gn5%Hz";[Console]::Beep(%Gn5%, %QuarterNote%);^
  Write-Output "Cn6=%Cn6%Hz";[Console]::Beep(%Cn6%, %QuarterNote%*2)^
}

pause

echo.
echo ♪周波数の再生範囲テストします。
echo.
echo プログラム上で指定できる数値の範囲は整数値37～32767となっています。
echo ここではDs1(38Hz)からBn9(15804Hz)まで再生します。
echo.
echo 88鍵のピアノは一番低い音がAn0(27.5Hz)、一番高い音はCn8(4186Hz)とされてます。
echo 実際、音楽でメインの旋律にそこまで低音、高音が使われることはほとんどありません。
echo.
echo 環境によって再生できる周波数は違うと思われます。
echo 私の環境では低音はDS1(38Hz)から再生されていますがブツブツとノイズ音の方が大きく
echo 高音はGn9(12544Hz)から音が聞こえなくなりました。
echo.

pause
echo.

PowerShell ^&{^
  (%REST% %QuarterNote%);^
  Write-Output "Ds1=%Ds1%Hz";[Console]::Beep(%Ds1%, %QuarterNote%);^
  Write-Output "En1=%En1%Hz";[Console]::Beep(%En1%, %QuarterNote%);^
  Write-Output "Fn1=%Fn1%Hz";[Console]::Beep(%Fn1%, %QuarterNote%);^
  Write-Output "Fs1=%Fs1%Hz";[Console]::Beep(%Fs1%, %QuarterNote%);^
  Write-Output "Gn1=%Gn1%Hz";[Console]::Beep(%Gn1%, %QuarterNote%);^
  Write-Output "Gs1=%Gs1%Hz";[Console]::Beep(%Gs1%, %QuarterNote%);^
  Write-Output "An1=%An1%Hz";[Console]::Beep(%An1%, %QuarterNote%);^
  Write-Output "As1=%As1%Hz";[Console]::Beep(%As1%, %QuarterNote%);^
  Write-Output "Bn1=%Bn1%Hz";[Console]::Beep(%Bn1%, %QuarterNote%);^
  Write-Output "Cn2=%Cn2%Hz";[Console]::Beep(%Cn2%, %QuarterNote%);^
  Write-Output "Cs2=%Cs2%Hz";[Console]::Beep(%Cs2%, %QuarterNote%);^
  Write-Output "Dn2=%Dn2%Hz";[Console]::Beep(%Dn2%, %QuarterNote%);^
  Write-Output "Ds2=%Ds2%Hz";[Console]::Beep(%Ds2%, %QuarterNote%);^
  Write-Output "En2=%En2%Hz";[Console]::Beep(%En2%, %QuarterNote%);^
  Write-Output "Fn2=%Fn2%Hz";[Console]::Beep(%Fn2%, %QuarterNote%);^
  Write-Output "Fs2=%Fs2%Hz";[Console]::Beep(%Fs2%, %QuarterNote%);^
  Write-Output "Gn2=%Gn2%Hz";[Console]::Beep(%Gn2%, %QuarterNote%);^
  Write-Output "Gs2=%Gs2%Hz";[Console]::Beep(%Gs2%, %QuarterNote%);^
  Write-Output "An2=%An2%Hz";[Console]::Beep(%An2%, %QuarterNote%);^
  Write-Output "As2=%As2%Hz";[Console]::Beep(%As2%, %QuarterNote%);^
  Write-Output "Bn2=%Bn2%Hz";[Console]::Beep(%Bn2%, %QuarterNote%);^
  Write-Output "Cn3=%Cn3%Hz";[Console]::Beep(%Cn3%, %QuarterNote%);^
  Write-Output "Cs3=%Cs3%Hz";[Console]::Beep(%Cs3%, %QuarterNote%);^
  Write-Output "Dn3=%Dn3%Hz";[Console]::Beep(%Dn3%, %QuarterNote%);^
  Write-Output "Ds3=%Ds3%Hz";[Console]::Beep(%Ds3%, %QuarterNote%);^
  Write-Output "En3=%En3%Hz";[Console]::Beep(%En3%, %QuarterNote%);^
  Write-Output "Fn3=%Fn3%Hz";[Console]::Beep(%Fn3%, %QuarterNote%);^
  Write-Output "Fs3=%Fs3%Hz";[Console]::Beep(%Fs3%, %QuarterNote%);^
  Write-Output "Gn3=%Gn3%Hz";[Console]::Beep(%Gn3%, %QuarterNote%);^
  Write-Output "Gs3=%Gs3%Hz";[Console]::Beep(%Gs3%, %QuarterNote%);^
  Write-Output "An3=%An3%Hz";[Console]::Beep(%An3%, %QuarterNote%);^
  Write-Output "As3=%As3%Hz";[Console]::Beep(%As3%, %QuarterNote%);^
  Write-Output "Bn3=%Bn3%Hz";[Console]::Beep(%Bn3%, %QuarterNote%);^
  Write-Output "Cn4=%Cn4%Hz";[Console]::Beep(%Cn4%, %QuarterNote%);^
  Write-Output "Cs4=%Cs4%Hz";[Console]::Beep(%Cs4%, %QuarterNote%);^
  Write-Output "Dn4=%Dn4%Hz";[Console]::Beep(%Dn4%, %QuarterNote%);^
  Write-Output "Ds4=%Ds4%Hz";[Console]::Beep(%Ds4%, %QuarterNote%);^
  Write-Output "En4=%En4%Hz";[Console]::Beep(%En4%, %QuarterNote%);^
  Write-Output "Fn4=%Fn4%Hz";[Console]::Beep(%Fn4%, %QuarterNote%);^
  Write-Output "Fs4=%Fs4%Hz";[Console]::Beep(%Fs4%, %QuarterNote%);^
  Write-Output "Gn4=%Gn4%Hz";[Console]::Beep(%Gn4%, %QuarterNote%);^
  Write-Output "Gs4=%Gs4%Hz";[Console]::Beep(%Gs4%, %QuarterNote%);^
  Write-Output "An4=%An4%Hz";[Console]::Beep(%An4%, %QuarterNote%);^
  Write-Output "As4=%As4%Hz";[Console]::Beep(%As4%, %QuarterNote%);^
  Write-Output "Bn4=%Bn4%Hz";[Console]::Beep(%Bn4%, %QuarterNote%);^
  Write-Output "Cn5=%Cn5%Hz";[Console]::Beep(%Cn5%, %QuarterNote%);^
  Write-Output "Cs5=%Cs5%Hz";[Console]::Beep(%Cs5%, %QuarterNote%);^
  Write-Output "Dn5=%Dn5%Hz";[Console]::Beep(%Dn5%, %QuarterNote%);^
  Write-Output "Ds5=%Ds5%Hz";[Console]::Beep(%Ds5%, %QuarterNote%);^
  Write-Output "En5=%En5%Hz";[Console]::Beep(%En5%, %QuarterNote%);^
  Write-Output "Fn5=%Fn5%Hz";[Console]::Beep(%Fn5%, %QuarterNote%);^
  Write-Output "Fs5=%Fs5%Hz";[Console]::Beep(%Fs5%, %QuarterNote%);^
  Write-Output "Gn5=%Gn5%Hz";[Console]::Beep(%Gn5%, %QuarterNote%);^
  Write-Output "Gs5=%Gs5%Hz";[Console]::Beep(%Gs5%, %QuarterNote%);^
  Write-Output "An5=%An5%Hz";[Console]::Beep(%An5%, %QuarterNote%);^
  Write-Output "As5=%As5%Hz";[Console]::Beep(%As5%, %QuarterNote%);^
  Write-Output "Bn5=%Bn5%Hz";[Console]::Beep(%Bn5%, %QuarterNote%);^
  Write-Output "Cn6=%Cn6%Hz";[Console]::Beep(%Cn6%, %QuarterNote%);^
  Write-Output "Cs6=%Cs6%Hz";[Console]::Beep(%Cs6%, %QuarterNote%);^
  Write-Output "Dn6=%Dn6%Hz";[Console]::Beep(%Dn6%, %QuarterNote%);^
  Write-Output "Ds6=%Ds6%Hz";[Console]::Beep(%Ds6%, %QuarterNote%);^
  Write-Output "En6=%En6%Hz";[Console]::Beep(%En6%, %QuarterNote%);^
  Write-Output "Fn6=%Fn6%Hz";[Console]::Beep(%Fn6%, %QuarterNote%);^
  Write-Output "Fs6=%Fs6%Hz";[Console]::Beep(%Fs6%, %QuarterNote%);^
  Write-Output "Gn6=%Gn6%Hz";[Console]::Beep(%Gn6%, %QuarterNote%);^
  Write-Output "Gs6=%Gs6%Hz";[Console]::Beep(%Gs6%, %QuarterNote%);^
  Write-Output "An6=%An6%Hz";[Console]::Beep(%An6%, %QuarterNote%);^
  Write-Output "As6=%As6%Hz";[Console]::Beep(%As6%, %QuarterNote%);^
  Write-Output "Bn6=%Bn6%Hz";[Console]::Beep(%Bn6%, %QuarterNote%);^
  Write-Output "Cn7=%Cn7%Hz";[Console]::Beep(%Cn7%, %QuarterNote%);^
  Write-Output "Cs7=%Cs7%Hz";[Console]::Beep(%Cs7%, %QuarterNote%);^
  Write-Output "Dn7=%Dn7%Hz";[Console]::Beep(%Dn7%, %QuarterNote%);^
  Write-Output "Ds7=%Ds7%Hz";[Console]::Beep(%Ds7%, %QuarterNote%);^
  Write-Output "En7=%En7%Hz";[Console]::Beep(%En7%, %QuarterNote%);^
  Write-Output "Fn7=%Fn7%Hz";[Console]::Beep(%Fn7%, %QuarterNote%);^
  Write-Output "Fs7=%Fs7%Hz";[Console]::Beep(%Fs7%, %QuarterNote%);^
  Write-Output "Gn7=%Gn7%Hz";[Console]::Beep(%Gn7%, %QuarterNote%);^
  Write-Output "Gs7=%Gs7%Hz";[Console]::Beep(%Gs7%, %QuarterNote%);^
  Write-Output "An7=%An7%Hz";[Console]::Beep(%An7%, %QuarterNote%);^
  Write-Output "As7=%As7%Hz";[Console]::Beep(%As7%, %QuarterNote%);^
  Write-Output "Bn7=%Bn7%Hz";[Console]::Beep(%Bn7%, %QuarterNote%);^
  Write-Output "Cn8=%Cn8%Hz";[Console]::Beep(%Cn8%, %QuarterNote%);^
  Write-Output "Cs8=%Cs8%Hz";[Console]::Beep(%Cs8%, %QuarterNote%);^
  Write-Output "Dn8=%Dn8%Hz";[Console]::Beep(%Dn8%, %QuarterNote%);^
  Write-Output "Ds8=%Ds8%Hz";[Console]::Beep(%Ds8%, %QuarterNote%);^
  Write-Output "En8=%En8%Hz";[Console]::Beep(%En8%, %QuarterNote%);^
  Write-Output "Fn8=%Fn8%Hz";[Console]::Beep(%Fn8%, %QuarterNote%);^
  Write-Output "Fs8=%Fs8%Hz";[Console]::Beep(%Fs8%, %QuarterNote%);^
  Write-Output "Gn8=%Gn8%Hz";[Console]::Beep(%Gn8%, %QuarterNote%);^
  Write-Output "Gs8=%Gs8%Hz";[Console]::Beep(%Gs8%, %QuarterNote%);^
  Write-Output "An8=%An8%Hz";[Console]::Beep(%An8%, %QuarterNote%);^
  Write-Output "As8=%As8%Hz";[Console]::Beep(%As8%, %QuarterNote%);^
  Write-Output "Bn8=%Bn8%Hz";[Console]::Beep(%Bn8%, %QuarterNote%);^
  Write-Output "Cn9=%Cn9%Hz";[Console]::Beep(%Cn9%, %QuarterNote%);^
  Write-Output "Cs9=%Cs9%Hz";[Console]::Beep(%Cs9%, %QuarterNote%);^
  Write-Output "Dn9=%Dn9%Hz";[Console]::Beep(%Dn9%, %QuarterNote%);^
  Write-Output "Ds9=%Ds9%Hz";[Console]::Beep(%Ds9%, %QuarterNote%);^
  Write-Output "En9=%En9%Hz";[Console]::Beep(%En9%, %QuarterNote%);^
  Write-Output "Fn9=%Fn9%Hz";[Console]::Beep(%Fn9%, %QuarterNote%);^
  Write-Output "Fs9=%Fs9%Hz";[Console]::Beep(%Fs9%, %QuarterNote%);^
  Write-Output "Gn9=%Gn9%Hz";[Console]::Beep(%Gn9%, %QuarterNote%);^
  Write-Output "Gs9=%Gs9%Hz";[Console]::Beep(%Gs9%, %QuarterNote%);^
  Write-Output "An9=%An9%Hz";[Console]::Beep(%An9%, %QuarterNote%);^
  Write-Output "As9=%As9%Hz";[Console]::Beep(%As9%, %QuarterNote%);^
  Write-Output "Bn9=%Bn9%Hz";[Console]::Beep(%Bn9%, %QuarterNote%);^
}

echo.
echo 再生を終了しました。
echo.


:: 終了処理（エクスプローラーから起動されていた場合はPauseする）;
:EndProcess
echo %cmdcmdline%|find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 (pause)
goto :eof
```

</details>

# ◇実行方法を判別する

エクスプローラーまたはコマンドからの起動を判別できると色々と応用が利きます。
私はほぼすべてのバッチの最後にサンプルの内容を入れてます。

<details><summary>実行がエクスプローラーからかコマンドか判別するサンプル</summary>

```bat:DiscExplorerBoot.bat
:: 終了処理（エクスプローラーから起動されていた場合はPauseする）;
:EndProcess
echo %cmdcmdline%|find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 (Pause)
```

</details>

# ◇メッセージウインドウを表示

バッチの中でなにか入力待機をさせる場合、「はい／いいえ」など単純なものはウインドウを表示してマウスのみで完結させたい場合があります。
ＰｏｗｅｒＳｈｅｌｌで実現できます。

<details><summary>メッセージウィンドウで入力待機させる</summary>

```
powershell -Command "Add-Type -AssemblyName System.Windows.Forms;$result = [System.Windows.Forms.MessageBox]::Show(\"メッセージ文1`nメッセージ文2`nメッセージ文3\", 'タイトル', 'YesNoCancel', 'Asterisk');exit $result;"
echo 戻り値は %ERRORLEVEL% です
pause
```

</details>

メッセージ文 は、\” で括ると、「`n」で改行できます。
表示するボタン は、次の値を指定します。
どのボタンが押されたかは、実行サンプルのようにすると、バッチの %ERRORLEVEL% で取得できます。
指定する値で表示されるボタンと値の関係は、次のようになります。
（）内が %ERRORLEVEL% の値です。

〇表示するボタン
|コマンド|ボタン(ERRORLEVELの値)|
|:-|:-|
|AbortRetryIgnore| 中止（3） 再試行（4） 無視（5） |
|OK| OK（1） |
|OKCancel| OK（1） キャンセル（2） |
|RetryCancel| 再試行（4） キャンセル（2） |
|YesNo| はい（6） いいえ（7） |
|YesNoCancel| はい（6） いいえ（7） キャンセル（2） |

〇表示するアイコン
|表記|コマンド|
|:-|:-|
|青い〇内に「！」|Asterisk、Information|
|赤い〇内に「×」|Error、Hand、Stop|
|黄色い△内に「！」|Exclamation、Warning|
|青い〇内に「？」|Question|
|なし|None|

# ◇トーストを使って通知する

![Toast.gif](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/588934/5a80e27e-ff14-5b64-f3f4-dea4b3ed7504.gif)

トーストを利用するとバッチを終了し閉じたあとでも通知に記録を残すことができます。
ＰｏｗｅｒＳｈｅｌｌで実現できます。

<details><summary>トーストによる通知を行うサンプル</summary>

```
@echo off


set ToastMsg=\"バッチファイルからトースト通知します。`n行数も増やせます`n1`n2`n3`n4\"
PowerShell.exe ^&{$m=%ToastMsg%;$a='%comspec%';$t=[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType,Windows.UI.Notifications,ContentType=WindowsRuntime]::ToastText01);$t.GetElementsByTagName('text').Item(0).InnerText=$m;[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($a).Show($t);}


echo Message Strings.
echo.
echo %ToastMsg%
echo.


:: 終了処理（エクスプローラーから起動されていた場合はPauseする）;
:EndProcess
echo %cmdcmdline%|find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 (pause)
goto :eof
```

</details>

Powershellをバッチに埋め込もうとしないで使う場合はもっと色々なことができるのですが、バッチ一行でシンプルにするためメッセージのみです。
※サンプルではメッセージ文を編集しやすくするため、２行に分けています。

メッセージ文 は、```「\”」``` で括ります。```「`n」```で改行ができます。

# ◇仮想ディスクを作成、最適化する

仮想ディスクはサーバーの運用に限らず様々な場面で管理がしやすく有効です。
私の場合は自宅と会社の環境作りやＵＳＢで持ち歩ける環境作りに利用しています。
また、ＢｉｔＬｏｃｋｅｒによるパスワード制限を使えるのでセキュリティー面も安心です。

※ＢｉｔＬｏｃｋｅｒでパスワード制限を利用するにはＷｉｎｄｏｗｓＰｒｏ版の管理者権限が必要です。
参考 : [【初心者向け】Windows10でUSBメモリを暗号化する【テレワーク】][]

私が実際に利用している仮想ディスクを作成、最適化するバッチファイルを紹介いたします。

### ・仮想ディスクを作成する

<details><summary>仮想ディスクを作成するサンプル</summary>

```bat:MakeVirtualDisk.bat
@echo off


:: 遅延展開宣言 バグの原因になる場合があります;
setlocal enabledelayedexpansion


:: 管理者権限がない場合は管理者権限で実行し直す;
openfiles>NUL 2>&1
if %ERRORLEVEL% equ 0 (goto :Admin)
set ARGV=&&for %%a in (%*) do (set ARGV=!ARGV! \"%%a\")
powershell.exe -Command Start-Process %comspec% -ArgumentList "'/c, \"%~f0\", %ARGV%'" -Verb Runas
echo %cmdcmdline%|find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 (exit)
goto :eof
:Admin


:: タイトル宣言;
title VHDX仮想ディスクを作成
echo.


:: カレントディレクトリを実行ファイルと同じに変更;
if "%~dp0" neq "%CD%" pushd "%~dp0"


:: %ESC%でエスケープシーケンスを利用;
for /f "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set ESC=%%b)


:: 仮想ディスクのボリュームラベル（ファイル名）を指定;
:InputFilename
echo 仮想ディスクのファイル名を入力してください。
set /p VDLabel=">"
if "%VDLabel%" equ "" goto :InputFilename


:: VHDファイルのパスを作成;
set VDFILE=%VDLabel%.vhdx
set VDFILE=%~dp0%VDFILE%


:: 同名のファイルを確認;
if exist "%VDFILE%" (
  echo "%ESC%[92m%VDFILE%%ESC%[0m"は既に存在するファイルです。
  goto :InputFilename
)
echo.


:: 仮想ディスクのサイズをMBで指定 (1GB=1024MB);仕様では最小３ＭＢのようですがエラーになるため４ＭＢ以上にしています。;
:InputFileSize
set NumMin=4
set NumMax=67108864
echo 仮想ディスクの最大サイズをＭＢ単位で指定してください。(1GB=1024MB)
echo 指定できる範囲は %NumMin%～%NumMax% です。
set /p VDSIZE=">"
:: 数値チェック;
call :IsInteger %%VDSIZE%%
if %ERRORLEVEL% neq 0 (
  echo 数値以外が含まれています。
  goto :InputFileSize
)
:: 指定サイズチェック; ifを重ねて AND を判定をしています。;
if %VDSIZE% geq %NumMin% if %VDSIZE% leq %NumMax% goto :InputFileSizeEnd
echo 数値を%NumMin%～%NumMax%の範囲で入力してください。
echo.
goto :InputFileSize
:InputFileSizeEnd
echo.

:: 仮想ディスクのドライブレターの指定と空きドライブを検索;
set DRIVE=ABCDEFGHIJKLMNOPQRSTUVWXYZ
for /l %%i in (0,1,25) do (
  set DL=!DRIVE:~%%i,1!
  if not exist !DL!: (set UNUSEDRIVE=!UNUSEDRIVE!!DL!)
)
echo 仮想ディスクに設定するドライブレターをＡからＺの中から指定してください。
:INPUT_VDRIVELETTER
echo 利用できるドライブは %ESC%[92m%UNUSEDRIVE%%ESC%[0m です。
set /p VDRIVELETTER=">"
if "%VDRIVELETTER%" equ "" goto :INPUT_VDRIVELETTER
if exist %VDRIVELETTER%: goto :INPUT_VDRIVELETTER
echo.


:: 仮想ディスクのファイルタイプを指定;
Rem/||(
  expandable ・・・　サイズを可変にして最小サイズでファイルを作成
                 通常はこちらを推薦
                 最小サイズで作成されるためメンテナンス性に優れ、ファイルの最適化やあとで固定サイズに変更が可能
  fixed　     ・・・　サイズを固定して最大サイズでファイルを作成
                 最初からディスク領域を確保するため断片化を防げパフォーマンスはこちらが上とされているがＳＳＤなどではほぼ無意味
                 容量が決まっている場合や、空き容量の少ないＵＳＢメモリなどに保存する場合はこちらも有効
)
set VDMODE=expandable
echo 仮想ディスクのファイルタイプを指定してください。 
echo デフォルトは「%ESC%[92m%VDMODE%%ESC%[0m」です。変更しない場合はそのままエンターを押してください。 
echo サイズを可変にする場合「%ESC%[92mexpandable%ESC%[0m」と入力してください。 
echo サイズを固定にする場合「%ESC%[92mfixed%ESC%[0m」と入力してください。 
:INPUT_VDTYPE
set /p VDTYPE=">"
if /i "%VDTYPE%" equ "expandable" (
  set VDMODE=expandable
  goto :INPUT_VDTYPE_OK
)
if /i "%VDTYPE%" equ "fixed"  (
  set VDMODE=fixed
  goto :INPUT_VDTYPE_OK
)
if "%VDTYPE%" neq "" goto :INPUT_VDTYPE
:INPUT_VDTYPE_OK
echo.


:: 仮想ディスクのファイル情報表示;
echo %ESC%[92m
echo Virtual Drive File Name = "%VDFILE%"
echo                    Size = %VDSIZE% MB
echo             Driveletter = %VDRIVELETTER%:\
echo                    Mode = %VDMODE%
echo %ESC%[0m

pause

:: Diskpart.exeのスクリプトファイル名を日付・時刻から作成;
for /f "tokens=1-8 delims=/:. " %%1 in ("%date% %time: =0%") do set TEMPFILE=%%1%%2%%3%%5%%6%%7.$$$
set TEMPFILE=%~dp0TEMP%TEMPFILE%

pause


:: Diskpart.exeのスクリプトファイルを作成;
(
echo create vdisk file="%VDFILE%" maximum=%VDSIZE% type=%VDMODE%
echo select vdisk file="%VDFILE%"
echo attach vdisk
echo clean
echo create partition primary
echo format fs=ntfs label="%VDLabel%" quick
echo assign letter=%VDRIVELETTER%
echo detach vdisk
) > %TEMPFILE%

pause


:: 仮想ファイルの作成;
diskpart /s %TEMPFILE%
echo.
echo Dsikpart Result         = %ERRORLEVEL%
if %ERRORLEVEL% neq 0 goto :Error_DISKPART

pause


:: スクリプトファイルを削除;
del %TEMPFILE%


:: 正常終了;
echo.
echo Finished.
echo.
:: 正常終了の音楽を鳴らす;
PowerShell ^&{Start-Sleep -milliseconds 100;[Console]::Beep(524,500);[Console]::Beep(660,500);[Console]::Beep(784,500);[Console]::Beep(1046,900);}
goto :EndProcess


:: Diskpartでエラー発生;
:Error_DISKPART
echo.
echo %ESC%[41;97mAn error occurred in the creation of the virtual file.%ESC%[0m
echo.
:: Windows標準のBEEPを鳴らす;
rundll32 user32.dll,MessageBeep
goto :EndProcess


:: 終了処理（エクスプローラーから起動されていた場合はPauseする）;
:EndProcess
echo %cmdcmdline%|find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 Pause


:: 変数が数値かチェック;
:IsInteger
set X=%1
if "%X%" equ "" exit /b -1
if defined X set X=%X:0=%
if defined X set X=%X:1=%
if defined X set X=%X:2=%
if defined X set X=%X:3=%
if defined X set X=%X:4=%
if defined X set X=%X:5=%
if defined X set X=%X:6=%
if defined X set X=%X:7=%
if defined X set X=%X:8=%
if defined X set X=%X:9=%
if not defined X exit /b 0
exit /b -1
```

</details>

### ・仮想ディスクを最適化する

最適化するバッチファイルですが、[SDELETE][].exeを利用しています。
標準ではない外部コマンドなのですが、バッチでEXEファイルを生成しています。
作成するためにJScriptを利用します。

:::note info
バッチファイルへのJScriptの埋め込み
バッチファイルへのJScriptの埋め込みについては次のページが参考になります。
[Windowsでshebangもどき、またはバッチにスクリプトを埋め込む方法]
:::

:::note info
データの完全消去について
実はJScriptを利用しバッチのみでデータ消去するバッチファイルも作成していたのですが、空き領域の計算が不正確のまま途中から放置しています。
[SDELETE][].exeの生成と同じくBase64文字列をバイナリデータに変換することで実現できるわけですが、ご興味のある方は「[携帯環境作成支援スクリプトMECSS][]」からコメント「// 指定したドライブの空き領域にバイナリ・ゼロのファイルを作成した後に削除」を検索してみてください。

データの完全消去については次のページが参考になります。
- [HDDやSSDなどのデータを完全消去する方法と消去方式の規格]
- [データの完全消去(wikipedia)][]
:::

:::note info
拡張子について
私はJScriptを利用したバッチファイルは区別するために拡張子を「.cmd」にしています。
「.bat」はMS-DOS時代から使われている標準の拡張子
「.cmd」はWindows NT系から使われる拡張子
らしいのですが、違いもちゃんとあるようです。

|拡張子|違い|
|:-|:-|
|.bat|エラーが発生した時だけ、ERRORLEVELが変化する|
|.cmd|コマンド成功時も、ERRORLEVELが変化する|

次のページが参考になります。

- [Ｗｉｎｄｏｗｓの拡張子「.cmd」ファイルと「.bat」ファイルの違い][]
- [Difference between CMD and BAT][]
- [Windows batch files: .bat vs .cmd?][]
:::

:::note info
ファイル名の先頭を「@」にすると
同じような方法はほかにもありますが、ファイル名の先頭を「@」にするとコマンドラインから起動できないようにできます。
ちょっとしたことですが誤動作を防ぐひとつの方法です。
:::

:::note alert
使用には仮想ディスクファイルをドラックアンドドロップします。
実際に使用しており実用レベルですが、ドライブレターの割り当て有無など考慮していない部分があります。ご利用いただける場合は事前にバックアップを取るなど十分注意してください。
:::

<details><summary>仮想ディスクを最適化する</summary>

```bat:@OptimizeVirtualDiskFile_Make_SDelete_Ver_DragDropHere.cmd
@if(0)==(0) rem /* Start of Batch
@echo off


:: 遅延展開 バグの原因になる場合があるので注意;
setlocal enabledelayedexpansion


:: エクスプローラーから起動された場合、タイトル宣言;
echo %cmdcmdline% | find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 title 仮想ディスクファイルの最適化

:: 管理者権限がない場合は管理者権限で実行し直す;
openfiles>NUL 2>&1
if %ERRORLEVEL% equ 0 (goto :Admin)
set ARGV=&&set ARGC=0
for %%a in (%*) do (set /a ARGC+=1&&set ARGV!ARGC!=%%a&&set ARGV=!ARGV! \"%%a\")
powershell.exe -Command Start-Process %comspec% -ArgumentList "'/c, \"%~f0\", %ARGV%'" -Verb Runas
echo %cmdcmdline%|find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 (exit)
goto :eof
:Admin


:: 実行時のフォルダに移動;
pushd "%~dp0"

:: エスケープシーケンスを利用;
for /f "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set ESC=%%b)


:: 仮想ディスクファイル名を設定（コマンドライン、ドラッグアンドドロップ両対応できるようにファイル名を完全修飾パス名で指定）;
set VDISKFILE=%~f1
echo Target File=%ESC%[92m%VDISKFILE%%ESC%[0m
echo.


:: ファイルの存在チェック;
if not exist %VDISKFILE% (
  echo %ESC%[41;97mFile not found.%ESC%[0m
  echo.
  goto :EndProcess
)


:: sdelete.exeの存在チェック;
if not exist "sdelete.exe" (
  echo %ESC%[41;97m^"sdelete.exe^" not found.%ESC%[0m
  echo %ESC%[41;97m^Make "sdelete.exe^".%ESC%[0m
  echo.
  call cscript.exe //nologo //E:JScript "%~f0"
  call certutil -f -decode "sdelete.b64" "sdelete.exe"
)


:: 仮想ファイルをマウント;
echo.
echo %ESC%[44mMount the virtual disk.%ESC%[0m
PowerShell.exe ^"Mount-DiskImage -ImagePath ^"%VDISKFILE%^";Start-Sleep -milliseconds 2000^"


:: ドライブレターを取得してバッチに返す;返ってくるのはShift-JISコードのためアルファベットに変換;
PowerShell.exe ^"$drive = (Get-DiskImage -ImagePath ^"%VDISKFILE%^"^|Get-Disk^|Get-Partition^|Get-Volume).DriveLetter;exit $drive^"
set /a POS=%ERRORLEVEL%-65
set Alphabet=ABCDEFGHIJKLMNOPQRSTUVWXYZ
set VIRTUAL_DRIVE=!Alphabet:~%POS%,1!:


:: 仮想ドライブを最適化と空きスペースを詰める;
echo.
echo %ESC%[44mOptimizes fragmented files.%ESC%[0m
defrag.exe %VIRTUAL_DRIVE%
echo.
echo %ESC%[44mFree space on the virtual disk is summarized.%ESC%[0m
defrag.exe -x %VIRTUAL_DRIVE%


:: 仮想ドライブの空き領域をZeroFill(SDelete);
echo.
echo %ESC%[44mZero-filling the virtual disk.%ESC%[0m
sdelete.exe -z %VIRTUAL_DRIVE%


:: 仮想ファイルをアンマウント;
PowerShell.exe ^"Dismount-DiskImage -ImagePath ^"%VDISKFILE%^";Start-Sleep -milliseconds 2000^"


:: Diskpart.exeのスクリプトファイル名を日付・時刻から作成;
for /f "tokens=1-8 delims=/:. " %%1 in ("%date% %time: =0%") do set TEMPFILE=%%1%%2%%3%%5%%6%%7.$$$
set TEMPFILE=%~dp0TEMP%TEMPFILE%


:: Diskpart.exeのスクリプトファイルを作成;
(
echo select vdisk file="%VDISKFILE%"
echo compact vdisk
) > %TEMPFILE%


:: Diskpart 仮想ファイルの最適化;
echo.
echo %ESC%[44mOptimizing virtual disk.%ESC%[0m
diskpart /s %TEMPFILE%
echo.
echo Dsikpart Result         = %ERRORLEVEL%
if %ERRORLEVEL% neq 0 goto :Error_DISKPART


:: 後処理、関連ファイルを削除;
del %TEMPFILE%
del "sdelete.b64"
del "sdelete.exe"


:: 正常終了;
echo.
echo %ESC%[92mFinished.%ESC%[0m
echo.
PowerShell ^&{Start-Sleep -milliseconds 100;[Console]::Beep(524,500);[Console]::Beep(660,500);[Console]::Beep(784,500);[Console]::Beep(1046,900);}
goto :EndProcess


:: Diskpartでエラー発生;
:Error_DISKPART
echo.
echo An error occurred in the creation of the virtual file.
echo.
rundll32 user32.dll,MessageBeep
goto :EndProcess


:: 終了処理（エクスプローラーから起動されていた場合はPauseする）;
:EndProcess
popd
echo %cmdcmdline% | find /i "%~f0">NUL
if %ERRORLEVEL% equ 0 Pause
goto :eof


rem End of Batch */
GAP
@end
/*** Start of JScript <JavaScript ECMAScript3?> ***/
function main() {
  CreateSdeleteFile("SDelete.b64");
}

// "SDelete.exe"を作成
function CreateSdeleteFile(SdeleteFileName) {
  var SdeleteB64 = function() {/*
-----BEGIN CERTIFICATE-----
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
GMLDdW4hOhemDWKhTgLUAE6qR9zOVApcDyhTCC5z7d19HihzCBYvVkQVL5izv8dA
F2UrMAC3qkN4+hB2VlQ2V2BNKoF+EIqgaS5758ZO5DdkYfw+D0a2bvbccxFObhMA
X3IVBje7528TdignSjZcIsAafmKGPAgGW7vXBk0sSuYGbB51Z/ZwLRKKwE+ITm/C
eN2B68hjX/55Z3IR0t0ScLdSDn7eu4ez2X6nhj+OdUoP9wCwlk5iubBzz12mbxOu
Jb++/2mPF0FNBlBNTS9kZC95j2T+M/f8ACwgTSARKCxISDptbTrQeeC141M3ZoYa
3IwTVB4RV+BwDOWDLnUPYjvgPbZfqm9ua+9ZO81/H49z3dZu2yOfQie3cl22tq0j
zx/fSqzzFq4nSnNWMXjonZb3pv665bsNmh95T3UPbGFJvPY/DmenOtSXccKeJifp
2IO05Pu/dbGt3RZTz3Ij52ye2Axf71fnEdm2PYPvX/fYDB0cG6+TbEewg18fbx/Y
gsEWL0NHJ3FOvra2TQ9QTbTd3jO6ZAp5/2QDu7HbsXpNAyAjSlMnXrp3SAI6umYi
R+qEp6+CXud53l/Rr+QG6Ozwz7N5nvT4/LAACBA8z/M8GCQwOETnPc/zSExQVF5Y
nud5nlxgZGhscE6e53l0fIiQmPM8z/MGoKiwvMTN8zzP0Nzg5PCxed5bpAQxFhAG
GCDneZ7nKDA4QEie53meWGh4jKCweZ7necTM1Nzk82ye5+z0/LIEDM/zPM8UHCQ0
SFSe53lnX7JgBmx4iJx5nud5rMDU3OTqUM/m+LMgNGpOSw1Ab0ckswNYJYdMKCBc
yUErJBADhBAIluSBgQEBQKYdWH+CAQMCV2mELXeXKF0FAyQI5xL2tjv2vzAfFAIr
GxOhDWLfAwEBX9oKggXT7yOqQhMWADW5VTWtCwJLLkAGARDTAuSSggIL/6jqGAWA
gYKDhIX/////hoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKX/////pqeo
qaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMX/////xsfIycrLzM3Oz9DR0tPU
1dbX2Nna29zd3t/g4eLj5OWw/v//5ufo6err7O3u7/Dx8vP09fb3+Pn6+/yEqgAc
WNEKYEQBkdEIVUEA/03AqGL/0YAhxRY//y8fGQP/8H/4/7aFLC/vfw4QROf9DGsB
JzAEvRAGHBCjGJ8oNGqOLVIXOusI7nr7Q+44dmc1AGuTSwBSL1RZn8AJBl9htWtc
iwsnVkFYCUsjjAEywEctwJYA+D9y37/eG5sYX2cjg0ZkyO0aSxJoD2ne0X5j32Uf
LRpvAK52+/9rDwBHc9sIIUWHA08EBroQh2F3ILBgtd+rIUPqIuMAu2IYBb+vLc9D
w2qrYS33R4fXUJbaL7fvlGDbam+jL8aC3QVPgkdia2qfGy9qQ4K22kFfPxp6F4Fr
AAMj1UZwpfNm41eQQzuA42dABn2gCyCLS9lqB0ZvZ7ZK3AgZYC9z+rQFxR0TNls/
UGKpKEs/tZRCD4p4k1PomxrtZ0eznjJQVw9nY3+D0d6aW78/f9q3CzqKww9pT2At
QbAPR1UPFqMP3zeLV7syWr97c25qa2hPOx5laydgp/dgLQ9r90JHF7MRtBovc5t6
0i4Da8vrOpdh62J6n2hNU0HHbme1m6kPYwNhR7aC3mAmh/4/VjtXrd9sNyzYe/h3
b8N7R6ktOVpG3iBPCBwdW/vjpkHCiq8HY6MvYMBvPxrH1moPTz+jcFixD+d2T7qr
YcUh2z8X4DzvAbeCdWEb8gCrH5N4PyjmBlaHcmd28BYs/8MnR2AX4K0bBwA/gwWb
tn95RwfxKC1YdTfTvasdUmpvb091g3VFrbbLPwcSNrix+p+nZZa2TG9HQwCD6cM2
swCvNOGQt58Oc2HnC6Q7IY4Wqz3QpQhHN2MySNcW4CP/12emMNpQlyCHwk1IO7tX
ry3fBwJpszstw2GetQJrV/96IIxkNggbJy10Gsg03y26BTrwcGsPf4MdHKw3Q7Nn
wECukC0tBobk6PcmddXSIZUvJ2mLxg2MNgA/l1jYEimTX0BFueSSzwcXVHicyuw2
UkG0EkwAQi/E5bPWkUPYWrsX4CSz50hJ6ENTR/iVbjvtvhwvvkRfL2hUbsFpI5DX
vqwfF14qI5XQQehMvwgZqYxUQyBCRGWkMlJJXEp8lZHKSFqUU8BUVF4qI/RHwAxV
VoyXjCQ8RpJCF5HKSGVcQ3xMfVEjlaBTvIpBpPJSmRfcQ8EETL2CSGUoU3/BYO/a
bW0uL3wqT6oXz1nlkpC0Tl/YUEJSmXUvwgSjUxcoQkhlpDJITGRPI5WRyohDsETo
jFReKkbDCEUwMlIZqUdUSHjKSGWkTZhOuCojlZFJ3EH8WqmMVF7EIFI8VaQyUhlk
WYRWOA2zbqgTRhfIh8TUZKTSrY8X3FXk1m7n2/fE7FUX/F5C910za/TFDC9OFxha
shpdu/YXJEc0F1ArRNbjrc0XYHJL98V040wXr127ZIyUv6gXvFBr8HkQNxfUt0sX
KO6CNuRyQc/GJvcfL7l2xhgvNExUDk9cO8kEr9TGcBeQ9GHYFffcFxc3Q+3/by2H
Tw8MDBoMBxA2BAwILQQDChB/VxTwEAgdCNoBd9IgAsiRI2cPKAMwBDgFHDly5EgG
UAdYCGAJkSNHjmgKcAt4DDly5MiADYgOkA+YECNHjhygEagSsBO4cuTIkRTAFcgW
0BhHjhw52BngGugb8BzkyJcj+B3TAB4IHzccOXIQIBghICK/I5EjZ2cfKCQPMCU4
Jjly5MhAJ0gpUCpYKyNHjhxgLGgtcC94cuTIkTaAN4g4kDlHjhw5mD6gP6hAsEHk
yJEjuEPARMhGjhw5ctBH2EngSuhLyJcjR/BO+E/UAFAcOXLkCFYQVxhaIGWRl0eO
KH8wAQQ0Anbky9lAAx9MBL00BVgGD3w5cnZkBx9wCHwJszQLZ0fOjogMD5QNoA6/
rA/syJEjuBDEERASD3Lk7OwoEy/QFA/cFegWR458OfQY1QAZDBoYG+TIkSMkHDAd
PB6OHDlySB9UIGAhbCLIkSNHeCOEJJAlHDly5JwmqCe0KcAqkSNHjswr2CzkLTly
5Mv8L9YIMhQ0IDUjR44cLDY4N0Q4UHLkyJE5XDpoO3Q+R44cOYA/jECYQaRD5MiR
I7BEyEXURr4cOXLgR+xJ+ErXBEvIkSNHEEwcTihPHDly5DRQQFJMVlhXkSNHjmRa
dGWEa3l55MiUbKSBsAEIvAQ5O/vU/gcfyAkP1AovR44c4AzsEPgT2ARy5MiRFBAW
HBooHUeOHDlALEw7ZD5wQ+TlkSN8a5QBDKQEjhw5crAHvAnICtQMyJcjR+Aa7DvZ
BGscOfLyEAEQIAQsBzgJkSNHjkQKUAxcGjny8shoO3QBFIQEkAcjR44cnAmoCrQM
wPLyyJEazDvkARj0CUeOHPnaAAoMDBgaJDvkyMsjPAEcTAlYCl4eOXJkGnA7iAEg
mAnlkSNHpAqwO7wBJB45cuTMCdgK5DvwASjlkSNX2wAJDAoYASy8PHLkJAkwCjwB
MEgJkZdHjlQKYAE0bAk88vLIeAqEATiQCpwBPCMvj7yoCrQBQMAKzPny5csKRNgK
SOQKTPAKUIdGrnz8BHzcCBoYIhu79a3nJ2XGBuAHNyPDrJPvLnM/ZGSvbFroTW4P
bk9+pU2+nUdfaA51Jt/yqH4Ar2ob9ag33gcXtN1OZh9wcF9yL92jtotXaM87D3Fm
Ay0ndpoPcgAGmlx1lqXJ7W3nX89lqMkF7zoPT2bU+qTsLu+PYbccNHkwdQ9ttrvd
bhOvYX9vb2lPcz/5rtJ2aw8vd691O2lyO3T/cLovtttBLx+Gf26vRtpuGx8/bS/O
J71vGM9rP3lT8hGnSAfTFmE7KvHj1y8tHkc3+/FIjC1/Hj9ad3H5Otwv8EsXZUXl
tuPdNy1yUh8WRgBJHe11y3IvaF8qTDe+bsfHLeJVPy9TF3Ta0nZcVC9eThZivMvl
XU8ucFBwX215j0+HTkZSFnXYcfkuVddyUmfa0nY030tvjkEudt25PF1FHnRUF3Ie
dDsuUo/vS09kk4dDXURHhlXtuHyXZVmnbEnHy9fepb5FbNfqVhd0Wz7cjlTfpod2
QtvRYEdO709N9xcM1UmvWmueF3VbDo5WXx9OTT7UdpeDNlp4khdH29G2HhdvF3ei
y4sXj0V3b0+HB5evwTdOv3RUxwQu3YplLy9zWdHlq3THa1oXeUfXkTz4bha/dZdV
bXcUo/53YibvGfa0PR8XJy90wdOkLRZlP2clx65dbBdyd3OBDi7fbV9NY2c6tmlD
po+3l2PTDh3Tpy0bt6ALvm6LVh9xy0Jww4Fx+0PXbdMFv/SnB2EnUa+CB1xgH9cP
dZtuGGW/WK+rRelt2jZnX2cvMGmx5GZuZ1CVaTFMY1DvB6+Di2Nuz0PHl7wVk6dO
Zd/WTrQgtFWXX/8OtAW7y88aR+8YQOsaSJeW2LDgLecWVef3FazgLudDMoc/Bmjt
YIf3F7405Nn3TABZX71tu833TN9ux/dCVLDguK73SJ9CDyFP29AKasvHRABaTKYd
oPbHSUEG3Fbvx0NvP0LFdtHvc8dHWnAQzN9Tp01fuH3HJt9Fr1AvZkdDo2CIbW+v
YY/ukmG4VB4nWkRKBTcq1pcHlke67VgbYk2XSheXVjdtRfdLZ3NzZ1k2btcwFSdC
X09nbnLD1UgTx0Kyd/tYC0dKf0dyGYqhMg9BYXZFV3BC91cXQ0ddwXc7Sy9uv0g/
TOzgKo5HQR9VNy/WcO3aQl9QL1HPbZ96uWsXxxdra71LPxc2jykOVolSn7NPyyvN
pAAXQseAZ88y6uNAcWc/40zYD1ja5MiRI2SxcKB8j44cOXKIz5TVoNKsqciRI0e4
ucTE0NxeOnLk3EPozPS/5+TsbOTkAMgpHwybLyRr2ZQ6cighPGO3AR9T6sjZSEQP
VH1gt+cC2ZEjZx94RUgEhEcPR87m1JCHBwUfnEhYBsiRsyOoog+0kcBJs7l05Myz
2KvHQX/kc+rIkYtgB/RKlwjIkSN/D+UAowzNGKwcOXLkJMkwkjy6SMWRI0eOVLRg
1mzQcnbkyHhLhMCQ099wCY4cOTuc0Q+o3bTXwMrIkSNHzLXYweTUHPly5PCk/K3m
CN8Uk5EjR44g4Cy7OM45cuTIROFQ21zeaNnkbGIddMYHIx+AZY4cOXJwKoxsUCaY
aDlyNrP3Cj+kTJAuZ0eOHLBzgAu8lA/IpeTIkSPUruBN7LbuqTl1+LxnPvfnBIg2
tc5GNx8Qf8cMP44cOXIcTpgvKHToGJEjZ0c0ry9AWpANR85m1kxPlygfWGogH5zN
rSNkYXcOH3BQI2dHjqAPfJUviFGozmbWkRCUUvctH6ByyJEjR6gxrHjwOpxgAuC4
ghcR7xg/NrXOjsSJD9RTRzIfjhw5cuB5SCXsZ0AkjdxbR/hmJ+gEjitsap2dHxBt
DxyDNz0fI2dT6yiGdzsfNISg5MjZkTBAnQ9Md1h1djYDcGRVdxIfcJYPmwE4cnxU
iJenE68Ajhw5lI3QNqB+I0fOZtcUH6xW0BW45MiRs1cPxJjQjOCf8jcFcPCoNxYf
6QBYTQAcOeAXDFkXPM6OnJ0fGIUPJKcwdm88nCmAI0fwGUhbJ8iRs7MiH1RkD2C+
cMMcOXLkgLCQuKDLsMe+nM0BJxofwFzcGOOAI2dHzMIP5L38ptnZyD2H6hSZGx8s
mi8DcOTIOF24M0R6hzYFcDZAH1CKJzgfjhw5cmCA6DlsgQgcEwFnR3heD4RuRx3A
kSNnH5BfyDWcfETA2URXIB+oYpd25MjZHh+0YMA0wJ4vnB05cth7WCfwaQ/8b5Ej
R77rCAMY4iiQOXLkyDShQLJMqlhGxtAGHWRwDxIFY28VFwplF0JoS2G7YxdkShdz
xp4GNhcOF3zIx6ribxdrAHdsAGLC2iGXeW3vsEtmD4MvcXMXE1wibXeLZ3krMTsn
egtjN6RU4mIvbP+g+9J7b2KnDwou70nY/x8uc2E+9aXFd1cbg07Cl1fih7ZLQ2ju
bwoJ29uMaxd/FxS291I3FwsXNw26tuYXdb9tChZet1gnx3IXg7G37XcX8noXSrvk
kGsXYmdp9yw55NmPagBtbim1rQRKF1N9pIh4FzeH7GIlrhd3P0MXdsMFMWJ/X2wX
LLm2ti9fZB8ybSiaF3NnAHR2sN0haPoXkngXJ22fwrsXornkkmsXZXJ5JbNnDcMv
dZPLg9t2d3Q3ZXWpA7FQr7LQ26XbNwq/C+1iGy1HChdfFzu2G3JoChcnylbpbhdt
SlfvfVcKX0eXZRdsY7O1Q5cv72EXjXqLdQo/C//dSj2F4u8KYJXeYm8LB+MAuO1P
FwrXWhAb9Zdwtxql6b2NPwZ6F8fve9kuvxsfT3IXqbdTl3lnbwsd7ZLbnwunX95C
vU8PC/+raMnl8i5ubnK3Ut+WLxdHed8L6QJYrQ9TfLddfNdnFwpHbs1jTJdzH9vX
WKh3rYcLN1V621n6Fwt/2tHaplMf+x/rrdbRc/8L0iXvVv8K7nNzbQu2hfsXTxdW
6+3WCkcLh22LdCYKr2NcyO2tH2s/amqQ2diFbvsfc7Do/Thxz2wXL6sC2yp/Lwe3
2oF4L/pfLwredrRfdvMX96QDJ+93Fmt501zSljSOdBZlaMAKcO4LFv8Vq3UPdwqn
H7t8H4BfdUd1cCIWkiO4F2Z1L20AVrCHR4nbAqAKbrfvemRgVwtrMx90RXzHDm4X
aP96bcjbQjsXfmd2d5X1NgBvz96hl/9y5AtUEGMtXsdrBUDq/299MfzQnCyfDEJh
9bmrv6Rcw5H+//LxKWMdtf00BcTSh2aS+RU7bH/v/v+fgNmQZZQsQmLXAUUimhcm
J0+fkQKVB8HfSP//iVYkHKf6xWdtyHPcba3rcvHBzmQnol/W//9jyhik7yV70c1w
799rHz7qnV/h7////+Ru/sPNagy8ZjIfOS4DAkVaJfjScVZKwsPaB9CP9////y6o
CEOyqnwaIY5AzorzC87EhCcL63zDlCWtSRLp////fxrd2lSfzL9hWdyrq1zHDEQF
9WcWvNFSr7f7KY2PYJT///+/KschDIq7F6SOr1apn0cGNrJLXeBf3IAKqv7wQP//
V//ZjqjQgBprI0RkOEwylsdXg9VCSuRhIqnZPTf4//8QPL1y8+WRdBVZwA2mHexs
2SoQ0+b7hR5b/////2FPbmkqexgc4lAEKzTdL+4nUGOZccmmFulKjiguCBdv//93
+G5JGm4Z20AyJkCtBFByHvnV0ZQpu81bZpbW////Ljui2336ZaxT3neboiCwU/m/
xqsllEtN4wT///9NOMP79NAiUlAoD7fz8hNXExRC3H1dOdaZGVn/8P//+Bw4kgDW
FLOGuXelemH+txJqYQt6ER2NZ8P/////ViAflDqLNgmbCGlwvb5ldiDrxCabnehn
FW4JFZ0r8jKMb/D/cRNRSL7OouVFUn8agbt4lPcC//+vsEiMAF3wsHXG26kUudni
33IPZUxLKB////93FuD2bcKRQ1HPyZUnVavi1ifmqJymsT1X/////0rQ7PTwiCN/
xW0KWG8Ev0PDXS34SAgR7hxZoPoo8PTNSv3//z+lLhmgcda8h0RpfQFu+RCdVhp5
daQK/////+GyuTx1iIKTFj/Nazq0id6HnghGRU1oDKbb/ZGTJN8Tx////+xoMCdE
tJnuQYG2w8oCWPFRaNmiJXZ9jXFOgv13/f9k++aDWvIPrVeUEbWACrUpIM/Sxdd9
bf///7/aHE23zd5wndo9QRa3TsrQcZgT5NeQOkBP4j+r+W93twv2+E0m5q8KyxAx
kAnSWNrLJmH/////VoeDHGrB9Id1duhELM9HoEGeBQjJPga6oOjIz+dVwPr///8F
UkQB77B+ICRzJXLRgfm45K4FFQdAYjt6T13/////pM4zQeJPbW0PIfIzVuVWE8El
l9frKITrltN3O0keri3/v+D/H0cgOK2W0c76itsqTobAaFWhXWmyiTwSJHH/PwCM
RapBHCdKF25XrmLsqon/////Iu/d+6K25O/hF/K9ZjOAiLQ3Piy4v5HerBkIZPTU
Tmr+/1f8/zUOalZnLttAyjsqeGibMmvZxa/1vGlkJv///51n9F+A+6/RVe2oIEqb
+FeXqwr+rgF7pixKaf////+Vvx4pHMTHqtLV2HbHNtEMVdqTkJ3HmqjLSyUYdvAN
Cf////+IqPd0EB86/BFI5a2OY1kQ58uX6GnXJj5y5LSGqpBbIv////85M5x1B3pL
kelHLXf5bprnQAsWxPiSDBDwX/IRbMMlQuP///+L+cmdkQtzr3z/BYUtQ7BpdSst
LIRXphDvH9D///+/OnrH5WK46GqI2BDlmM3IxVWJEFW2WdDUvvtYMYK4A/////8Z
RUwDOclNGawAxR/iwEx5oYDJO9Etsen4Im1emok4ezMb///YGXnOcnbGeJ+55XlO
A5TkV6EZ1v//6dRcbG995Jvn2Tv5oW9id1E0////v2pZK95Y3jzPWP9GIhV8V6hZ
decmU2d3F2O35utfCv39////42k56DM1oAWoh7kx9kMPHyHbQ1rYlvUbq6IZP2gE
////SvZk/n2+LwTJS7Dt9eHaTqGPc9sJ5JzuT2f/////DZ8Vqda1tfYOljhzkcJJ
68yXK1+VPzgP9rORIBQ3eNHy////30LRwd4iPhVX36+KX+X1d4vK56NbUi8DPU/n
Qr/p/78Q3fRSCUVd4UK0ri40s6NvoyRueii093f/////wUvQyNJn4Piormc7ya2z
VshsC52dlQDBSFs9ir5K9Db+////2VJN6NtxxSEc+QmBRUpq2KrXfEzhCJylm3UA
iDzkF////wVVktQQ8QS+cmQYDME2h/ureBQpr1H8Of////+X6yUVMCtMCw4DoTs8
/ii6/Ih3WEOeuKTkPXPC8kZ8mP//v+hidI9iGduutqMushRQqo2rOepCNJaXqd/f
AUDpU//+0/PSgAJ5oJ4B////G5DxrdzHLK09ODdNxnPQZ23qBqibUfjyA8Si4f//
//9SoDojENepc4VEutkSzwMYh3CbOtxS6FKy5U77Fwcvpv//X/RNvuHXDE/tYox7
7LnOIUBm1ACDFaHmdePM8lcVOOkpL4TvineS9dNx/////z12oOkvFH1mTPQzLvG4
844NDxNplExzqA8mYEATATwK/////4hxzCEtpTfvydqKtDG7QkFM+dZsBYvIuAEF
4nztl1LEH////2HDYqrY2ofe6jO4YWjwlL2azBNq1cGNLWH6////EBPoNnrGnikW
9Ao/SfPPpqV3oyO+pIJboswvchCK/0JTPp2+uBPCqE4yTAi/4v//M568uv6sdjIh
TC4yzRM+tJH+cAxcu4WXFEL8/////RrMRvjdOObShwdpF9ECGv7xtT6uq7nDb+4I
HL4Cf9f/UxmqwkCB2Xf4LD3X4e4v59UJY1Fy/////90ZqK9GWirWztwCKv7dRs6N
JBMnrdIjtxm7BMQrzAa3/78A/8rrsUfcSwmdxNzFjlHmMYBWw46oWC80/n/T/0Ie
BIsU5b/+E/yuD3ljZ/021WZ2UOG5YgaVovEVJrBnGq7A/////+EF0DtzEts/Lp+j
4p2yYeLcYyq8BCaUm9VwYZYl48K5/////3ULFCEsHR9gahO4ojvSiXN98WDf18rG
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
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIA
EAAAACAAAIAYAAAAYAAAgAAAAAAAAAAAAAAAAAAAAQABAAAAOAAAgAAAAAAAAAAA
AAAAAAAAAQAJBAAAUAAAAKTABQAkAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA
AQAAAHgAAIAAAAAAAAAAAAAAAAAAAAEACQQAAJAAAADMwwUAfQEAAAAAAAAAAAAA
oFAFACQDNAAAAFYAUwBfAFYARQBSAFMASQBPAE4AXwBJAE4ARgBPAAAAAAC9BO/+
AAABAAQAAgAAAAAABAACAAAAAAA/AAAAAAAAAAQABAABAAAAAAAAAAAAAAAAAAAA
ggIAAAEAUwB0AHIAaQBuAGcARgBpAGwAZQBJAG4AZgBvAAAAXgIAAAEAMAA0ADAA
OQAwADQAYgAwAAAAaAAkAAEAQwBvAG0AcABhAG4AeQBOAGEAbQBlAAAAAABTAHkA
cwBpAG4AdABlAHIAbgBhAGwAcwAgAC0AIAB3AHcAdwAuAHMAeQBzAGkAbgB0AGUA
cgBuAGEAbABzAC4AYwBvAG0AAABOABMAAQBGAGkAbABlAEQAZQBzAGMAcgBpAHAA
dABpAG8AbgAAAAAAUwBlAGMAdQByAGUAIABmAGkAbABlACAAZABlAGwAZQB0AGUA
AAAAACoABQABAEYAaQBsAGUAVgBlAHIAcwBpAG8AbgAAAAAAMgAuADAANAAAAAAA
MAAIAAEASQBuAHQAZQByAG4AYQBsAE4AYQBtAGUAAABTAEQAZQBsAGUAdABlAAAA
dgApAAEATABlAGcAYQBsAEMAbwBwAHkAcgBpAGcAaAB0AAAAQwBvAHAAeQByAGkA
ZwBoAHQAIAAoAEMAKQAgADEAOQA5ADkALQAyADAAMQA5ACAATQBhAHIAawAgAFIA
dQBzAHMAaQBuAG8AdgBpAGMAaAAAAAAAQAAMAAEATwByAGkAZwBpAG4AYQBsAEYA
aQBsAGUAbgBhAG0AZQAAAHMAZABlAGwAZQB0AGUALgBlAHgAZQAAAEoAFQABAFAA
cgBvAGQAdQBjAHQATgBhAG0AZQAAAAAAUwB5AHMAaQBuAHQAZQByAG4AYQBsAHMA
IABTAGQAZQBsAGUAdABlAAAAAAAuAAUAAQBQAHIAbwBkAHUAYwB0AFYAZQByAHMA
aQBvAG4AAAAyAC4AMAA0AAAAAABEAAAAAQBWAGEAcgBGAGkAbABlAEkAbgBmAG8A
AAAAACQABAAAAFQAcgBhAG4AcwBsAGEAdABpAG8AbgAAAAAACQSwBMhTBQA8P3ht
bCB2ZXJzaW9uPScxLjAnIGVuY29kaW5nPSdVVEYtOCcgc3RhbmRhbG9uZT0neWVz
Jz8+DQo8YXNzZW1ibHkgeG1sbnM9J3VybjpzY2hlbWFzLW1pY3Jvc29mdC1jb206
YXNtLnYxJyBtYW5pZmVzdFZlcnNpb249JzEuMCc+DQogIDx0cnVzdEluZm8geG1s
bnM9InVybjpzY2hlbWFzLW1pY3Jvc29mdC1jb206YXNtLnYzIj4NCiAgICA8c2Vj
dXJpdHk+DQogICAgICA8cmVxdWVzdGVkUHJpdmlsZWdlcz4NCiAgICAgICAgPHJl
cXVlc3RlZEV4ZWN1dGlvbkxldmVsIGxldmVsPSdhc0ludm9rZXInIHVpQWNjZXNz
PSdmYWxzZScgLz4NCiAgICAgIDwvcmVxdWVzdGVkUHJpdmlsZWdlcz4NCiAgICA8
L3NlY3VyaXR5Pg0KICA8L3RydXN0SW5mbz4NCjwvYXNzZW1ibHk+DQoAAAAAAAAA
AAAAAAAAAAAUxgUA2MUFAAAAAAAAAAAAAAAAACHGBQDgxQUAAAAAAAAAAAAAAAAA
LsYFAOjFBQAAAAAAAAAAAAAAAAA4xgUA8MUFAAAAAAAAAAAAAAAAAEXGBQAExgUA
AAAAAAAAAAAAAAAAUMYFAAzGBQAAAAAAAAAAAAAAAAAAAAAAAAAAAFzGBQAAAAAA
asYFAAAAAAB2xgUAAAAAAJzGBQB+xgUAjMYFAKrGBQAAAAAAusYFAAAAAADGxgUA
AAAAAEFEVkFQSTMyLmRsbABDT01ETEczMi5kbGwAR0RJMzIuZGxsAEtFUk5FTDMy
LkRMTABVU0VSMzIuZGxsAFZFUlNJT04uZGxsAAAAUmVnT3BlbktleVcAAABQcmlu
dERsZ1cAAABFbmREb2MAAEV4aXRQcm9jZXNzAAAAR2V0UHJvY0FkZHJlc3MAAExv
YWRMaWJyYXJ5QQAAVmlydHVhbFByb3RlY3QAAFNldEN1cnNvcgAAAFZlclF1ZXJ5
VmFsdWVXAAAAsAUAEAAAANI76D3sPfQ9ALAFABAAAADSO+g97D30PQAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAIAjAAAAAgIAMIIjbwYJKoZIhvcNAQcCoIIjYDCCI1wC
AQExDzANBglghkgBZQMEAgEFADBcBgorBgEEAYI3AgEEoE4wTDAXBgorBgEEAYI3
AgEPMAkDAQCgBKICgAAwMTANBglghkgBZQMEAgEFAAQgyRxcn3KjnhLhwumMb9nl
xSvUaCeejQYv5EZusELxQDyggg2BMIIF/zCCA+egAwIBAgITMwAAAYdyF3IVWUDH
CQAAAAABhzANBgkqhkiG9w0BAQsFADB+MQswCQYDVQQGEwJVUzETMBEGA1UECBMK
V2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0
IENvcnBvcmF0aW9uMSgwJgYDVQQDEx9NaWNyb3NvZnQgQ29kZSBTaWduaW5nIFBD
QSAyMDExMB4XDTIwMDMwNDE4Mzk0N1oXDTIxMDMwMzE4Mzk0N1owdDELMAkGA1UE
BhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQxHjAc
BgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEeMBwGA1UEAxMVTWljcm9zb2Z0
IENvcnBvcmF0aW9uMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzrfJ
C3Oz90+zCiIaLmB3sDBZp6vAMruxToWQkGm1cAadlUuFsgdkHuE0AU/Ggc5wDQxD
4xyjXT0/F8+XDWpYulx3n0vIv1l7RdL0rD/DRL+pgR7gNqdX8NsAfxdHR7Cdxn2e
XNLDyY5JbImKj8OfcSeeJDPdSDoIjtjlM4zQJYz4m4wlnx+1M0NUzx3OHcHopbPB
hCK2wUW+yFsIjmy9do1k+GIe9TUILyfRZ+vlIQ/cdrpN3S4/OL8LdTbhUIrSicSF
dH1bETUd2m0FTi6qQ7oG69EszS+qPMczhy+Tl4hhsIOnpIlwNf9l12O8lRXN/bZX
nQ7WY0ozW3sdc88ElwIDAQABo4IBfjCCAXowHwYDVR0lBBgwFgYKKwYBBAGCN0wI
AQYIKwYBBQUHAwMwHQYDVR0OBBYEFIaL+GcjvemsZCXTI6c7ts1VziXLMFAGA1Ud
EQRJMEekRTBDMSkwJwYDVQQLEyBNaWNyb3NvZnQgT3BlcmF0aW9ucyBQdWVydG8g
UmljbzEWMBQGA1UEBRMNMjMwMDEyKzQ1ODM4NTAfBgNVHSMEGDAWgBRIbmTlUAXT
gqoXNzcitW2oynUClTBUBgNVHR8ETTBLMEmgR6BFhkNodHRwOi8vd3d3Lm1pY3Jv
c29mdC5jb20vcGtpb3BzL2NybC9NaWNDb2RTaWdQQ0EyMDExXzIwMTEtMDctMDgu
Y3JsMGEGCCsGAQUFBwEBBFUwUzBRBggrBgEFBQcwAoZFaHR0cDovL3d3dy5taWNy
b3NvZnQuY29tL3BraW9wcy9jZXJ0cy9NaWNDb2RTaWdQQ0EyMDExXzIwMTEtMDct
MDguY3J0MAwGA1UdEwEB/wQCMAAwDQYJKoZIhvcNAQELBQADggIBAIsZskuhOr6a
1g/ShTSAfRuc8jLiI2QDrlCdRCv1ZYOhW92R1441MAEyiHF2xbhQulq+Cja1OA2P
7AVapmm+QAv43t26VKY7caRMqlKrT3N9MBIP6zvb5ipqiqCz09+7L3NjVQZhjZfv
OajuH1f8OwseydAW6pNfSnETXY7eniqE50zxwR5VR0CB2aTMWnGxTgJCa6gFZGGX
c+4pDV08VfhkW9+rQuAcjDcRNgxe7xXb2omT9AlWeQcidoAIVzHSvfrrMc1ZPdd6
inXtTgLlnb/q53apACJvH1JUZ6+LGkgoO3CG1MAgn9desFCexLiQ4NLx3soZwnh5
wW8h90WZBxItqH5n4JxSEiWQ3TAHlWRlTodtCaedFwc6qJKT83mes3Nf4MiCzcol
YBPkT5I51ELIXdX9TzIJ97Z7Ngs+2yYlVGqhDt5/akRYMuSbi2nulMHhnwHjqN3Y
C2cYpCs2LN4QzGhLSavCD+9XF+0F3upZzJl1Px3X89qfPe2XfpFPr2byiN3MC37l
UICtkWds/inNyt3UT89q18nCuVwrkWZrxmm/1m62Ygu8CUGqYAaHZbTCORjHRawY
PSHhe/6z+BKlUF3irXr05WV46bjYYY7kftgzLf3Vrn416YlvdW6N2h+hGozgC15q
MYJbQqdSu4a0uoJrL4/eHC0X+dEEOFPEMIIHejCCBWKgAwIBAgIKYQ6Q0gAAAAAA
AzANBgkqhkiG9w0BAQsFADCBiDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hp
bmd0b24xEDAOBgNVBAcTB1JlZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jw
b3JhdGlvbjEyMDAGA1UEAxMpTWljcm9zb2Z0IFJvb3QgQ2VydGlmaWNhdGUgQXV0
aG9yaXR5IDIwMTEwHhcNMTEwNzA4MjA1OTA5WhcNMjYwNzA4MjEwOTA5WjB+MQsw
CQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9u
ZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSgwJgYDVQQDEx9NaWNy
b3NvZnQgQ29kZSBTaWduaW5nIFBDQSAyMDExMIICIjANBgkqhkiG9w0BAQEFAAOC
Ag8AMIICCgKCAgEAq/D6chAcLq3YbqqCEE00uvK2WCGfQhsqa+laUKq4BjgaBEm6
f8MMHt03a8YS2AvwOMKZBrDIOdUBFDFC04kNeWSHfpRgJGyvnkmc6Whe0t+bU7IK
LMOv2akrrnoJr9eWWcpgGgXpZnboMlImEi/nqwhQz7NEt13YxC4Ddato88tt8zpc
oRb0RrrgOGSsbmQ1eKagYw8t00CT+OPeBw3VXHmlSSnnDb6gE3e+lD3v++MrWhAf
TVYoonpy4BI6t0le2O3tQ5GD2Xuye4Yb2T6xjF3oiU+EGvKhL1nkkDstrjNYxbc+
/jLTswM9sbKvkjh+0p2ALPVOVpEhNSXDOW5kf1O6nA+tGSOEy/S6A4aN91/w0FK/
jJSHvMAhdCVfGCi2zCcoOCWYOUo2z3yxkq4cI6epZuxhH2rhKEmdX4jiJV3TIUs+
UsS1Vz8kA/DRelsv1SPjcF0PUUZ3s/gA4bysAoJf28AVs70b1FVL5zmhD+kjSbwY
uER8ReTBw3J64HLnJN+/RpnF78IcV9uDjexNSTCnq47f7Fufr/zdsGbiwZeBe+3W
7UvnSSmnEyimp31ngOaKYnhfsi+E11ecXL93KCjx7W3DKI8sj0A3T8HhhUSJxAlM
xdSlQy90lfdu+HggWCwTXWCVmj5PM4TasIgX3p5O9JawvEagbJjS4NaIjAsCAwEA
AaOCAe0wggHpMBAGCSsGAQQBgjcVAQQDAgEAMB0GA1UdDgQWBBRIbmTlUAXTgqoX
NzcitW2oynUClTAZBgkrBgEEAYI3FAIEDB4KAFMAdQBiAEMAQTALBgNVHQ8EBAMC
AYYwDwYDVR0TAQH/BAUwAwEB/zAfBgNVHSMEGDAWgBRyLToCMZBDuRQFTuHqp8cx
0SOJNDBaBgNVHR8EUzBRME+gTaBLhklodHRwOi8vY3JsLm1pY3Jvc29mdC5jb20v
cGtpL2NybC9wcm9kdWN0cy9NaWNSb29DZXJBdXQyMDExXzIwMTFfMDNfMjIuY3Js
MF4GCCsGAQUFBwEBBFIwUDBOBggrBgEFBQcwAoZCaHR0cDovL3d3dy5taWNyb3Nv
ZnQuY29tL3BraS9jZXJ0cy9NaWNSb29DZXJBdXQyMDExXzIwMTFfMDNfMjIuY3J0
MIGfBgNVHSAEgZcwgZQwgZEGCSsGAQQBgjcuAzCBgzA/BggrBgEFBQcCARYzaHR0
cDovL3d3dy5taWNyb3NvZnQuY29tL3BraW9wcy9kb2NzL3ByaW1hcnljcHMuaHRt
MEAGCCsGAQUFBwICMDQeMiAdAEwAZQBnAGEAbABfAHAAbwBsAGkAYwB5AF8AcwB0
AGEAdABlAG0AZQBuAHQALiAdMA0GCSqGSIb3DQEBCwUAA4ICAQBn8oalmOBUeRou
09h0ZyKbC5YR4WOSmUKWfdJ5DJDBZV8uLD74w3LRbYP+vj/oCso7v0epo/Np22O/
IjWll11lhJB9i0ZQVdgMknzSGksc8zxCi1LQsP1r4z4HLimb5j0bpdS1HXeUOeLp
ZMlEPXh6I/MTfaaQdION9MsmAkYqwooQu6SpBQyb7Wj6aC6VoCo/KmtYSWMfCWlu
WpiW5IP0wI/zRive/DvQvTXvbiWu5a8n7dDd8w6vmSiXmE0OPQvyCInWH8MyGOLw
xS3OW560STkKxgrCxq2u5bLZ2xWIUUVYODJxJxp/sfQn+N4sOiBpmLJZiWhub6e3
dMNABQamASooPoI/E01mC8CzTfXhj38cbxV9Rad25UAqZaPDXVJihsMdYzaXht/a
8/jyFqGaJ+HNpZfQ7l1jQeNbB5yHPgZ3BtEGsXUfFL5hYbXw3MYbBL7fQccOKO7e
ZS/sl/ahXJbYANahRr1Z85elCUtIEJmAH9AAKcWxm6U/RXceNcbSoqKfenoi+kiV
H6v7RyOA9Z74v2u3S5fi63V4GuzqN5l5GEv/1rMjaHXmr/r8i+sLgOppO6/8MO0E
TI7f33VtY5E90Z1WTk+/gFcioXgRMiF670EKsT/7qMykXcGhiJtXcVZOSEXAQsmb
dlsKgEhr/Xmfwb1tbWrJUnMTDXpQzTGCFWEwghVdAgEBMIGVMH4xCzAJBgNVBAYT
AlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYD
VQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xKDAmBgNVBAMTH01pY3Jvc29mdCBD
b2RlIFNpZ25pbmcgUENBIDIwMTECEzMAAAGHchdyFVlAxwkAAAAAAYcwDQYJYIZI
AWUDBAIBBQCggagwGQYJKoZIhvcNAQkDMQwGCisGAQQBgjcCAQQwHAYKKwYBBAGC
NwIBCzEOMAwGCisGAQQBgjcCARUwLwYJKoZIhvcNAQkEMSIEIJDxoAAy2cy26XPC
xOIhWGNqOZJ7BYA8qsEcCHv2+iQkMDwGCisGAQQBgjcCAQwxLjAsoAqACABTAGQA
ZQBsoR6AHGh0dHBzOi8vd3d3LnN5c2ludGVybmFscy5jb20wDQYJKoZIhvcNAQEB
BQAEggEAETbul9vUfPgIp+DiU2f++pVr3m+ggQxS3sUAyNJByOAElwaL7IlI0Hu+
QBasgP3mPZdob6PYEF+hGkdHytC18S6Okudave9MUCdqhOIVMXDxH4A46BG6v9Pl
F1GB0H7W4smCEpZAm9ku1PhYYV26HyCmKqT6j/MpQeBINGxcQxl7xwZJwy8P2elH
mAib0XpMhS/fuhFd2DnFd2h8stPZthk0JhR/SAUrz0rx13Idz7K5zEkw5128bhGj
FtPDjDrNEv3z15z5HvdaZsTeYwKtdFiERBBO/tSEbxKQcNnQIIaUrahwI3LDaafG
p7SXe7MA46OUE4CnZUQnB/0Xn3AWTKGCEvEwghLtBgorBgEEAYI3AwMBMYIS3TCC
EtkGCSqGSIb3DQEHAqCCEsowghLGAgEDMQ8wDQYJYIZIAWUDBAIBBQAwggFVBgsq
hkiG9w0BCRABBKCCAUQEggFAMIIBPAIBAQYKKwYBBAGEWQoDATAxMA0GCWCGSAFl
AwQCAQUABCCUZLmlSLXNVR86tpjfWoPIWbzHlpr34/jQtoZjlPB8CgIGX7vNGmk6
GBMyMDIwMTEyNDIzMzYxOC4yNDlaMASAAgH0oIHUpIHRMIHOMQswCQYDVQQGEwJV
UzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UE
ChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSkwJwYDVQQLEyBNaWNyb3NvZnQgT3Bl
cmF0aW9ucyBQdWVydG8gUmljbzEmMCQGA1UECxMdVGhhbGVzIFRTUyBFU046MEE1
Ni1FMzI5LTRENEQxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNlcnZp
Y2Wggg5EMIIE9TCCA92gAwIBAgITMwAAAScvbqPvkagZqAAAAAABJzANBgkqhkiG
9w0BAQsFADB8MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYw
JAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQQ0EgMjAxMDAeFw0xOTEyMTkw
MTE0NTlaFw0yMTAzMTcwMTE0NTlaMIHOMQswCQYDVQQGEwJVUzETMBEGA1UECBMK
V2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0
IENvcnBvcmF0aW9uMSkwJwYDVQQLEyBNaWNyb3NvZnQgT3BlcmF0aW9ucyBQdWVy
dG8gUmljbzEmMCQGA1UECxMdVGhhbGVzIFRTUyBFU046MEE1Ni1FMzI5LTRENEQx
JTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNlcnZpY2UwggEiMA0GCSqG
SIb3DQEBAQUAA4IBDwAwggEKAoIBAQD4Ad5xEZ5On0uNL71ng9xwoDPRKeMUyEIj
5yVxPRPh5GVbU7D3pqDsoXzQMhfeRP61L1zlU1HCRS+129eo0yj1zjbAlmPAwosU
gyIonesWt9E4hFlXCGUcIg5XMdvQ+Ouzk2r+awNRuk8ABGOa0I4VBy6zqCYHyX2p
GauiB43frJSNP6pcrO0CBmpBZNjgepof5Z/50vBuJDUSug6OIMQ7ZwUhSzX4bEmZ
UUjAycBb62dhQpGqHsXe6ypVDTgAEnGONdSBKkHiNT8H0Zt2lm0vCLwHyTwtgIdi
67T/LCp+X2mlPHqXsY3u72X3GYn/3G8YFCkrSc6m3b0wTXPd5/2fAgMBAAGjggEb
MIIBFzAdBgNVHQ4EFgQU5fSWVYBfOTEkW2JTiV24WNNtlfIwHwYDVR0jBBgwFoAU
1WM6XIoxkPNDe3xGG8UzaFqFbVUwVgYDVR0fBE8wTTBLoEmgR4ZFaHR0cDovL2Ny
bC5taWNyb3NvZnQuY29tL3BraS9jcmwvcHJvZHVjdHMvTWljVGltU3RhUENBXzIw
MTAtMDctMDEuY3JsMFoGCCsGAQUFBwEBBE4wTDBKBggrBgEFBQcwAoY+aHR0cDov
L3d3dy5taWNyb3NvZnQuY29tL3BraS9jZXJ0cy9NaWNUaW1TdGFQQ0FfMjAxMC0w
Ny0wMS5jcnQwDAYDVR0TAQH/BAIwADATBgNVHSUEDDAKBggrBgEFBQcDCDANBgkq
hkiG9w0BAQsFAAOCAQEACsqNfNFVxwalZ42cEMuzZc126Nvluanx8UewDVeUQZEZ
HRmppMFHAzS/g6RzmxTyR2tKE3mChNGW5dTL730vEbRhnYRmBgiX/gT3f4AQrOPn
ZGXY7zszcrlbgzxpakOX+x0u4rkP3Ashh3B2CdJ11XsBdi5PiZa1spB6U5S8D15g
qTUfoIniLT4v1DBdkWExsKI1vsiFcDcjGJ4xRlMRF+fw7SY0WZoOzwRzKxDTdg4D
usAXpaeKbch9iithLFk/vIxQrqCr/niW8tEA+eSzeX/Eq1D0ZyvOn4e2lTnwoJUK
H6OQAWSBogyK4OCbFeJOqdKAUiBTgHKkQIYh/tbKQjCCBnEwggRZoAMCAQICCmEJ
gSoAAAAAAAIwDQYJKoZIhvcNAQELBQAwgYgxCzAJBgNVBAYTAlVTMRMwEQYDVQQI
EwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3Nv
ZnQgQ29ycG9yYXRpb24xMjAwBgNVBAMTKU1pY3Jvc29mdCBSb290IENlcnRpZmlj
YXRlIEF1dGhvcml0eSAyMDEwMB4XDTEwMDcwMTIxMzY1NVoXDTI1MDcwMTIxNDY1
NVowfDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcT
B1JlZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UE
AxMdTWljcm9zb2Z0IFRpbWUtU3RhbXAgUENBIDIwMTAwggEiMA0GCSqGSIb3DQEB
AQUAA4IBDwAwggEKAoIBAQCpHQ28dxGKOiDs/BOX9fp/aZRrdFQQ1aUKAIKF++18
aEssX8XD5WHCdrc+Zitb8BVTJwQxH0EbGpUdzgkTjnxhMFmxMEQP8WCIhFRDDNdN
uDgIs0Ldk6zWczBXJoKjRQ3Q6vVHgc2/JGAyWGBG8lhHhjKEHnRhZ5FfgVSxz5NM
ksHEpl3RYRNuKMYa+YaAu99h/EbBJx0kZxJyGiGKr0tkiVBisV39dx898Fd1rL2K
Qk1AUdEPnAY+Z3/1ZsADlkR+79BL/W7lmsqxqPJ6Kgox8NpOBpG2iAg16HgcsOmZ
zTznL0S6p/TcZL2kAcEgCZN4zfy8wMlEXV4WnAEFTyJNAgMBAAGjggHmMIIB4jAQ
BgkrBgEEAYI3FQEEAwIBADAdBgNVHQ4EFgQU1WM6XIoxkPNDe3xGG8UzaFqFbVUw
GQYJKwYBBAGCNxQCBAweCgBTAHUAYgBDAEEwCwYDVR0PBAQDAgGGMA8GA1UdEwEB
/wQFMAMBAf8wHwYDVR0jBBgwFoAU1fZWy4/oolxiaNE9lJBb186aGMQwVgYDVR0f
BE8wTTBLoEmgR4ZFaHR0cDovL2NybC5taWNyb3NvZnQuY29tL3BraS9jcmwvcHJv
ZHVjdHMvTWljUm9vQ2VyQXV0XzIwMTAtMDYtMjMuY3JsMFoGCCsGAQUFBwEBBE4w
TDBKBggrBgEFBQcwAoY+aHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3BraS9jZXJ0
cy9NaWNSb29DZXJBdXRfMjAxMC0wNi0yMy5jcnQwgaAGA1UdIAEB/wSBlTCBkjCB
jwYJKwYBBAGCNy4DMIGBMD0GCCsGAQUFBwIBFjFodHRwOi8vd3d3Lm1pY3Jvc29m
dC5jb20vUEtJL2RvY3MvQ1BTL2RlZmF1bHQuaHRtMEAGCCsGAQUFBwICMDQeMiAd
AEwAZQBnAGEAbABfAFAAbwBsAGkAYwB5AF8AUwB0AGEAdABlAG0AZQBuAHQALiAd
MA0GCSqGSIb3DQEBCwUAA4ICAQAH5ohRDeLG4Jg/gXEDPZ2joSFvs+umzPUxvs8F
4qn++ldtGTCzwsVmyWrf9efweL3HqJ4l4/m87WtUVwgrUYJEEvu5U4zM9GASinbM
QEBBm9xcF/9c+V4XNZgkVkt070IQyK+/f8Z/8jd9Wj8c8pl5SpFSAK84Dxf1L3mB
ZdmptWvkx872ynoAb0swRCQiPM/tA6WWj1kpvLb9BOFwnzJKJ/1Vry/+tuWOM7ti
X5rbV0Dp8c6ZZpCM/2pif93FSguRJuI57BlKcWOdeyFtw5yjojz6f32WapB4pm3S
4Zz5Hfw42JT0xqUKloakvZ4argRCg7i1gJsiOCC1JeVk7Pf0v35jWSUPei45V3ai
caoGig+JFrphpxHLmtgOR5qAxdDNp9DvfYPw4TtxCd9ddJgiCGHasFAeb73x4QDf
5zEHpJM692VHeOj4qEir995yfmFrb3epgcunCaw5u+zGy9iCtHLNHfS4hQEegPsb
iSpUObJb2sgNVZl6h3M7COaYLeqN4DMuEin1wC9UJyH3yKxO2ii4sanblrKnQqLJ
zxlBTeCG+SqaoxFmMNO7dDJL32N79ZmKLxvHIa9Zta7cRDyXUHHXodLFVeNp3lfB
0d4wwP3M5k37Db9dT+mdHhk4L7zPWAUu7w2gUDXa7wknHNWzfjUeCLraNtvTX4/e
dIhJEqGCAtIwggI7AgEBMIH8oYHUpIHRMIHOMQswCQYDVQQGEwJVUzETMBEGA1UE
CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
b2Z0IENvcnBvcmF0aW9uMSkwJwYDVQQLEyBNaWNyb3NvZnQgT3BlcmF0aW9ucyBQ
dWVydG8gUmljbzEmMCQGA1UECxMdVGhhbGVzIFRTUyBFU046MEE1Ni1FMzI5LTRE
NEQxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNlcnZpY2WiIwoBATAH
BgUrDgMCGgMVALOVuE5sgxzETO4s+poBqI6r1x8zoIGDMIGApH4wfDELMAkGA1UE
BhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQxHjAc
BgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UEAxMdTWljcm9zb2Z0
IFRpbWUtU3RhbXAgUENBIDIwMTAwDQYJKoZIhvcNAQEFBQACBQDjZ50DMCIYDzIw
MjAxMTI0MTg1MzU1WhgPMjAyMDExMjUxODUzNTVaMHcwPQYKKwYBBAGEWQoEATEv
MC0wCgIFAONnnQMCAQAwCgIBAAICIIMCAf8wBwIBAAICEdswCgIFAONo7oMCAQAw
NgYKKwYBBAGEWQoEAjEoMCYwDAYKKwYBBAGEWQoDAqAKMAgCAQACAwehIKEKMAgC
AQACAwGGoDANBgkqhkiG9w0BAQUFAAOBgQBijU1764wc+YWxQIHxMy18/3PyCK8F
oBo72xUeibU/x+bluxI5cWkm/UfRfGA0vpNHUcBHIBeOQ17Wqir5Ls45tMbnbPTq
JsLDbWsXg340+y1VQ9zp3vzK6Nl708GZY3j8j7Bqhe8TNFLKCw4NB3Ipz2ruUbJ/
ypd5c9LjTqgdBDGCAw0wggMJAgEBMIGTMHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQI
EwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3Nv
ZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBD
QSAyMDEwAhMzAAABJy9uo++RqBmoAAAAAAEnMA0GCWCGSAFlAwQCAQUAoIIBSjAa
BgkqhkiG9w0BCQMxDQYLKoZIhvcNAQkQAQQwLwYJKoZIhvcNAQkEMSIEIDIBurqE
MSBjvhBpHbhsIWdvnS2a/BKvtgQWNUZT+i+LMIH6BgsqhkiG9w0BCRACLzGB6jCB
5zCB5DCBvQQgG5LoSxKGHWoW/wVMlbMztlQ4upAdzEmqH//vLu0jPiIwgZgwgYCk
fjB8MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMH
UmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQD
Ex1NaWNyb3NvZnQgVGltZS1TdGFtcCBQQ0EgMjAxMAITMwAAAScvbqPvkagZqAAA
AAABJzAiBCAAPzK98dfPLiCuuqXKDI4QMkF2ZTU4OgfOlR5pWDiYZjANBgkqhkiG
9w0BAQsFAASCAQDT7NtDxlqUltU7SBpO0CCFInWMVrkjo8Mh0q+rNzhIWd98gxeI
3gTk5pqUwVRxfN/qlBVNEz+UtEgbS7oWveiiGb7eiVrQPEJJoWEAuWWaMIjcBQ3a
GJsf22QHV+Ls7AsEBZG1cexRRz82MP1WgBVaAKX1fFw8eGy3pEA2TA0AlxbOEu6/
BxmmmLR9ykN/BBvuz5EY5wroqw4nRrT4rjsMEKG3GHDHEUDcrGxJ2DtJiCCjKB0J
agsZBhVqdiBdf4owY5GObkqAtn1BAWvs9RQE/+Nce8q65DxPxBH47vXaaLuUmWxi
+nJTHQY8PTQvp2syT9s+MGj4TO9n7/Yhm6F7AAAAAAA=
-----END CERTIFICATE-----
*/}.toString().split("\r\n").slice(1,-1).join("\r\n");
  var ws = new ActiveXObject("WScript.Shell");
  var sfo = new ActiveXObject("Scripting.FileSystemObject");
  var MODE = {
    READING: 1,
    WRITING: 2,
    APPENDING: 8,
    CREATE: true,
    NOT_CREATE: false,
    WAIT: true,
    NOT_WAIT: false
  }
  var WINSTYLE = {
    HIDDEN: 0,
    NORMAL: 1,
    MINIMUM: 2,
    MAXIMUM: 3,
    INACTIVE_NORMAL: 4,
    LAST_TIME: 5,
    INACTIVE_MINIMUM: 7
  }
  var otf = sfo.OpenTextFile(SdeleteFileName, MODE.WRITING, MODE.CREATE);
  otf.Write(SdeleteB64);
  otf.Close();
  // ws.Run(SdeleteFileName, WINSTYLE.MAXIMUM, MODE.NOT_WAIT);
}

WScript.Quit(main());
```

</details>

# おわりに

他のバッチファイルもお見せできるレベルに修正できたら掲載したいです。
お粗末様でした。

https://github.com/Aromatibus/

[携帯環境作成支援スクリプトMECSS]: https://github.com/Aromatibus/MECCS

[rem]: https://docs.microsoft.com/ja-jp/windows-server/administration/windows-commands/rem
[DOSバッチファイルの複数行のコメント]: https://www.web-dev-qa-db-ja.com/ja/batch-file/dos%E3%83%90%E3%83%83%E3%83%81%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%81%AE%E8%A4%87%E6%95%B0%E8%A1%8C%E3%81%AE%E3%82%B3%E3%83%A1%E3%83%B3%E3%83%88/941134090/

[コンソール仮想端末シーケンス]: https://docs.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences

[PowerShellでビープ音の「ドレミの歌」を奏でてみよう]: https://tech.guitarrapc.com/entry/2013/02/05/000226

[【初心者向け】Windows10でUSBメモリを暗号化する【テレワーク】]: https://qiita.com/ronkabu/items/bdee0480475befa77186
[SDELETE]: https://docs.microsoft.com/en-us/sysinternals/downloads/sdelete
[Ｗｉｎｄｏｗｓの拡張子「.cmd」ファイルと「.bat」ファイルの違い]: https://urashita.com/archives/13383
[Difference between CMD and BAT]: https://copyprogramming.com/howto/difference-between-cmd-and-bat
[Windows batch files: .bat vs .cmd?]: https://stackoverflow-com.translate.goog/questions/148968/windows-batch-files-bat-vs-cmd?_x_tr_sl=en&_x_tr_tl=ja&_x_tr_hl=ja&_x_tr_pto=sc
[Windowsでshebangもどき、またはバッチにスクリプトを埋め込む方法]: https://qiita.com/snipsnipsnip/items/50e4ca88e3ce3f8cffda
[HDDやSSDなどのデータを完全消去する方法と消去方式の規格]: https://onoredekaiketsu.com/how-to-completely-erase-data-such-as-hdd-and-ssd/
[データの完全消去(wikipedia)]: https://ja.wikipedia.org/wiki/%E3%83%87%E3%83%BC%E3%82%BF%E3%81%AE%E5%AE%8C%E5%85%A8%E6%B6%88%E5%8E%BB
