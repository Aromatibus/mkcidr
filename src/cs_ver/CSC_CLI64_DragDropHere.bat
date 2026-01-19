@echo off

:: 遅延展開 バグの原因になる場合があるので注意;
setlocal enabledelayedexpansion

:: エスケープシーケンスを登録;
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set ESC=%%b)

:: UTF-8などで保存されたバッチファイルのShiftJis対策;
:: chcp 65001 > nul

:: 実行時のフォルダに移動;
pushd "%~dp0"

:: コマンドプロンプトを変更;
set prompt=%ESC%[104m$P$G%ESC%[0m

:: C# のコンパイラ
:: 32bit
:: set CSC=C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe
:: 64bit
set CSC=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe

:: 引数１が空でなければ、拡張子を".cs"に仮定変更してCSCに渡す;
if "%1" == "" (goto :EndProcess)
@echo on
%CSC% %~n1.cs /platform:x64
@echo.
@if %ERRORLEVEL% neq 0 (cmd /k)
@echo off
echo %~n1|clip

:: 終了処理（エクスプローラーから起動されていたらプロンプト表示）;
:EndProcess
echo %CMDCMDLINE% | find /i "%~f0" > nul
if %ERRORLEVEL% neq 0 (goto :eof)
echo.
choice /t 3 /c qa /d q /m "3秒待機します。即閉じる場合はQ、コマンドラインへはAを押してください。"
echo.
if "%ERRORLEVEL%" equ "2" (cmd /k)
