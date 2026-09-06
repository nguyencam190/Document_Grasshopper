@echo off
REM ============================================================
REM  Bam dup vao file nay de cai. Chi can sua MOT dong: MAYA_MCP.
REM ============================================================

REM --- Sua cho dung may ban. Day la thu muc CHUA src\maya_mcp_server.py ---
set MAYA_MCP=D:\MAYA_TOOLS\MayaMCP-main

cd /d "%~dp0"

REM --- Tu tim artspec: canh file .bat, hoac o thu muc cha ---
set ARTSPEC=
if exist "%~dp0artspec\artspec\server.py"    set ARTSPEC=%~dp0artspec
if exist "%~dp0..\artspec\artspec\server.py" set ARTSPEC=%~dp0..\artspec

set ARGS=
if exist "%MAYA_MCP%\src\maya_mcp_server.py"     set ARGS=%ARGS% --maya-mcp "%MAYA_MCP%"
if not exist "%MAYA_MCP%\src\maya_mcp_server.py" echo [!] Khong thay MayaMCP o "%MAYA_MCP%" - bo qua. Sua dong set MAYA_MCP o tren.
if defined ARTSPEC     set ARGS=%ARGS% --artspec "%ARTSPEC%"
if not defined ARTSPEC echo [!] Khong thay artspec canh file nay - bo qua.

if not defined ARGS goto :khong_co_gi

python cai_dat_mcp.py %ARGS% %*

echo.
pause

goto :xong

:khong_co_gi
echo.
echo KHONG CO GI DE CAI. Kiem lai duong dan MAYA_MCP o dau file nay.
echo.
pause
exit /b 1

:xong
