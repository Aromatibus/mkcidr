@echo off

cd /d %~dp0

title Python Make venv %DATE% - %TIME% 

for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set ESC=%%b)
set PROMPT=%ESC%[42;93m$P$G%ESC%[0m

:: PATHを通しておく
call R:\Source\@Scripts\#DevEnv.bat

:: Poetryで仮想環境初期化
call python -m poetry init
:: Poetryで仮想環境を現在のプロジェクトのみに設定
call python -m poetry config --local virtualenvs.in-project true
:: 開発用ライブラリをインストール
call python -m poetry add --group dev ruff mypy

:: Poetry環境へ移行
call python -m poetry shell
