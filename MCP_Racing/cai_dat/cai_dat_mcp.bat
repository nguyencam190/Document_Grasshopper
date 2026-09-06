@echo off
REM Bam dup vao file nay de cai. Sua hai duong dan ben duoi cho dung may ban.
REM Bo bot mot dong neu chi muon cai mot server.

set MAYA_MCP=D:\MAYA_TOOLS\MayaMCP-main
set ARTSPEC=D:\Projects\MCP_Racing\artspec

cd /d "%~dp0"
python cai_dat_mcp.py --maya-mcp "%MAYA_MCP%" --artspec "%ARTSPEC%"

echo.
pause
