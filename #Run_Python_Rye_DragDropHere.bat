@echo off

:: バッチファイルのShift-jis対策;
@chcp 65001>nul

title Python実行環境 %DATE% - %TIME%

for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set ESC=%%b)
set PROMPT=%ESC%[92m$P$G%ESC%[0m

cd /d %~dp0
call %~d0\Source\@Scripts\#DevEnvRye.bat
cmd /k



:: Python環境設定
set PYTHONPATH=%~dp0.venv
if not exist "%PYTHONPATH%" set PYTHONPATH=%~dp0..\.venv
if not exist "%PYTHONPATH%" set PYTHONPATH=%~dp0..\..\.venv
if exist "%PYTHONPATH%" set PATH=%PYTHONPATH%\Scripts;%PATH%

rem echo %ESC%[42;30m[%PYTHONPATH%]%ESC%[0m

:: venv環境へ移行
if exist "%PYTHONPATH%\Scripts\Activate.bat" call Activate.bat

:: 単独で起動された場合、コマンドプロンプトを表示
if "%1" == "" (cmd /k)

:: ラップタイム計測開始
call :LAPTime_Start

:: ドロップされたパスがドライブかファイルかフォルダか判別して実行
set TargetPathATTR=%~a1
set TargetPathATTR=%TargetPathATTR:~0,1%
if /i "%~n1" equ "" (
  echo "%1" is drive.
)
if /i "%TargetPathATTR%" equ "d" if /i "%~n1" neq "" (
  rem echo "%1" is folder.
  echo %ESC%[96mPython.exe -m %~n1%ESC%[0m
  echo ---------------------------------------------------------------------------------------
  Python -m %~n1
  echo ---------------------------------------------------------------------------------------
  echo.
)
if /i "%TargetPathATTR%" neq "d" (
  rem echo "%1" is file.
  echo %ESC%[96mPython.exe -m %~n1%ESC%[0m
  echo ---------------------------------------------------------------------------------------
  Python %1
  echo ---------------------------------------------------------------------------------------
  echo.
)

:: ラップタイム計測終了
call :LAPTime_Stop
call :LAPTime_Print

:: エラーチェック
if %ERRORLEVEL% neq 0 (
  echo ERRORLEVEL=%ERRORLEVEL%
  echo.
  cmd /k
)

:: 終了処理
echo.
choice /t 10 /d y /m "10秒後に自動的にウィンドウを閉じます。即時閉じる場合はＹ、プロンプトへはＮを押してください。"
if "%ERRORLEVEL%" equ "2" cmd /k
goto :eof


:: ◇経過時間の計測
:LAPTime_Start
  set T=%TIME: =0%
  set H=%T:~0,2%
  set M=%T:~3,2%
  set S=%T:~6,2%
  set L=%T:~9,2%

  rem --8進対策
  set /a H=1%H%-100
  set /a M=1%M%-100
  set /a S=1%S%-100
  exit /b

:LAPTime_Stop
  set T1=%TIME: =0%
  set H1=%T1:~0,2%
  set M1=%T1:~3,2%
  set S1=%T1:~6,2%
  set L1=%T1:~9,2%

  rem --8進対策
  set /a H1=1%H1%-100
  set /a M1=1%M1%-100
  set /a S1=1%S1%-100
 
  rem --終了時間の計算
  set /a H2=H1-H
  set /a M2=M1-M
  if %M2% LSS 0 set /a H2=H2-1
  if %M2% LSS 0 set /a M2=M2+60

  set /a S2=S1-S
  if %S2% LSS 0 set /a M2=M2-1
  if %S2% LSS 0 set /a S2=S2+60

  set /a L2=L1-L
  if %L2% LSS 0 set /a S2=S2-1
  if %L2% LSS 0 set /a L2=L2+100

  set /a DPS=%H2%*3600+%M2%*60+%S2%
  set DPS2=%DPS%.%L2%

  set HH=0%H2%
  set HH=%HH:~-2%
  set MM=0%M2%
  set MM=%MM:~-2%
  set SS=0%S2%
  set SS=%SS:~-2%

  set DPS_STAMP=%HH%:%MM%:%SS%
  set DPS_STAMP2=%DPS_STAMP%.%L2%

  exit /b

:LAPTime_Print
  echo %ESC%[43;30mStart：%T% / End：%T1% / Elapsed Time：%DPS_STAMP2% (%DPS2% Sec)%ESC%[0m
  exit /b


:: ドラッグアンドドロップされたファイルをひとつづつPythonに渡して実行
for %%i in (%*) do (
  call :LAPTime_Start
  call :Run_Python %%i
  call :LAPTime_Stop
  echo.
  call :LAPTime_Print
)
echo.

:Run_Python
  echo on
  Python.exe %1
  @echo off
  exit /b