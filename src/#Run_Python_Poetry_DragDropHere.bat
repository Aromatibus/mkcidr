@echo off

:: バッチファイルのShift-jis対策;
@chcp 65001>nul

cd /d %~dp0
call %~d0\Source\@Scripts\#DevEnv.bat

for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set ESC=%%b)
set PROMPT=%ESC%[92m$P$G%ESC%[0m

title Poetry Python実行環境 %DATE% - %TIME%
echo %ESC%[92m[Poetry Python実行環境 %DATE% - %TIME%]%ESC%[0m

:: 単独で起動された場合、Poetry Shellを表示
if "%1" == "" (python -m poetry shell)

:: 実行
@echo on
call python -m poetry run python %~nx1
@echo off

:: エラーチェック
if %ERRORLEVEL% neq 0 (
  echo ERRORLEVEL=%ERRORLEVEL%
  echo.
  python -m poetry shell
)

:: 終了処理
:: バッチファイルのShift-jis対策;
@chcp 65001>nul
echo.
choice /t 10 /d y /m "10秒後に自動的にウィンドウを閉じます。即時閉じる場合はＹ、プロンプトへはＮを押してください。"
if "%ERRORLEVEL%" equ "2" python -m poetry shell

goto :eof



:: Python環境設定
set PYTHONPATH=%~dp0.venv
if not exist "%PYTHONPATH%" set PYTHONPATH=%~dp0..\.venv
if not exist "%PYTHONPATH%" set PYTHONPATH=%~dp0..\..\.venv
if exist "%PYTHONPATH%" set PATH=%PYTHONPATH%\Scripts;%PATH%

:: venv環境へ移行
if exist "%PYTHONPATH%\Scripts\Activate.bat" call Activate.bat
