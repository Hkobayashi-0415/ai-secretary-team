@echo off
echo ================================================
echo    Cipher MCP Server - Aggregator Mode
echo ================================================
echo.
echo Starting Cipher in Aggregator Mode...
echo This will aggregate multiple MCP servers into one.
echo.

REM Set environment variables for Aggregator Mode
set MCP_SERVER_MODE=aggregator
set AGGREGATOR_CONFLICT_RESOLUTION=prefix
set AGGREGATOR_TIMEOUT=120000

REM Load GEMINI_API_KEY from .env file if not already set
if not defined GEMINI_API_KEY (
    for /f "tokens=1,2 delims==" %%a in ('findstr "GEMINI_API_KEY" cipher-source\.env') do (
        set GEMINI_API_KEY=%%b
    )
)

echo Configuration:
echo - Mode: Aggregator
echo - Conflict Resolution: prefix
echo - Timeout: 120 seconds
echo - Config File: cipher-source\memAgent\cipher.yml
echo - MCP_SERVER_MODE: %MCP_SERVER_MODE%
echo.
echo Starting server...
echo ------------------------------------------------

REM Change to cipher-source directory
cd /d cipher-source

REM Start Cipher in MCP mode with aggregator
node dist\src\app\index.cjs --mode mcp --agent memAgent\cipher.yml

echo.
echo ------------------------------------------------
echo Server stopped.
pause