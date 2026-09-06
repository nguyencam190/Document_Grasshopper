@echo off
REM ============================================================
REM  BAM DUP FILE NAY DE CAI PYTHON.
REM  Chay truoc cai_dat_mcp.bat. Neu may da co Python 3.10+
REM  thi no bao "khong can cai gi them" roi thoat.
REM ============================================================
cd /d "%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0cai_python.ps1"
set RC=%ERRORLEVEL%

if not "%RC%"=="0" goto :hong

echo.
echo Cai tiep hai MCP server luon? (bam Enter de cai, dong cua so de dung lai)
pause >nul
call "%~dp0cai_dat_mcp.bat"
exit /b 0

:hong
echo.
echo Cai Python KHONG THANH CONG (ma loi %RC%).
echo Chep nguyen doan chu o tren gui lai de xem vi sao.
echo.
echo Cach thu cong: vao python.org/downloads, tai ban 3.12 64-bit,
echo luc cai NHO TICK "Add python.exe to PATH".
echo.
pause
exit /b %RC%
